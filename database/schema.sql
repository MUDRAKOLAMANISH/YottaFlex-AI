CREATE TABLE IF NOT EXISTS Facility (
    facility_id TEXT PRIMARY KEY,
    facility_name TEXT NOT NULL,
    location TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS Pump (
    pump_id TEXT PRIMARY KEY,
    facility_id TEXT NOT NULL,
    pump_name TEXT NOT NULL,
    capacity_lpm REAL NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (facility_id)
        REFERENCES Facility(facility_id)
);
CREATE TABLE IF NOT EXISTS Tank (
    tank_id TEXT PRIMARY KEY,
    facility_id TEXT NOT NULL,
    tank_name TEXT NOT NULL,
    capacity_liters REAL NOT NULL,
    current_level_liters REAL NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (facility_id)
        REFERENCES Facility(facility_id),
    CHECK (capacity_liters > 0),
    CHECK (current_level_liters >= 0),
    CHECK (current_level_liters <= capacity_liters)
);
CREATE TABLE IF NOT EXISTS Valve (
    valve_id TEXT PRIMARY KEY,
    facility_id TEXT NOT NULL,
    valve_name TEXT NOT NULL,
    state TEXT NOT NULL,
    opening_percentage REAL NOT NULL,
    FOREIGN KEY (facility_id)
        REFERENCES Facility(facility_id),
    CHECK (state IN ('OPEN', 'CLOSED', 'PARTIALLY_OPEN')),
    CHECK (opening_percentage >= 0 AND opening_percentage <= 100)
);
CREATE TABLE IF NOT EXISTS NetworkNode (
    node_id TEXT PRIMARY KEY,
    facility_id TEXT NOT NULL,
    equipment_type TEXT NOT NULL,
    equipment_id TEXT NOT NULL,
    FOREIGN KEY (facility_id)
        REFERENCES Facility(facility_id),
    CHECK (equipment_type IN ('PUMP', 'TANK', 'VALVE')),
    UNIQUE (facility_id, equipment_type, equipment_id)
);
CREATE TABLE IF NOT EXISTS Pipe (
    pipe_id TEXT PRIMARY KEY,
    facility_id TEXT NOT NULL,
    pipe_name TEXT NOT NULL,
    source_node_id TEXT NOT NULL,
    target_node_id TEXT NOT NULL,
    diameter_mm REAL NOT NULL,
    max_flow_lpm REAL NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (facility_id)
        REFERENCES Facility(facility_id),
    FOREIGN KEY (source_node_id)
        REFERENCES NetworkNode(node_id),
    FOREIGN KEY (target_node_id)
        REFERENCES NetworkNode(node_id),
    CHECK (source_node_id != target_node_id),
    CHECK (diameter_mm > 0),
    CHECK (max_flow_lpm > 0)
);
CREATE TABLE IF NOT EXISTS Sensor (
    sensor_id TEXT PRIMARY KEY,
    facility_id TEXT NOT NULL,
    sensor_name TEXT NOT NULL,
    sensor_type TEXT NOT NULL,
    equipment_type TEXT NOT NULL,
    equipment_id TEXT NOT NULL,
    unit TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (facility_id)
        REFERENCES Facility(facility_id),
    CHECK (sensor_type IN ('FLOW', 'PRESSURE', 'LEVEL')),
    CHECK (equipment_type IN ('PUMP', 'TANK', 'VALVE', 'PIPE'))
);
CREATE TABLE IF NOT EXISTS Telemetry (
    telemetry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    reading_value REAL NOT NULL,
    quality_status TEXT NOT NULL DEFAULT 'GOOD',
    FOREIGN KEY (sensor_id)
        REFERENCES Sensor(sensor_id),
    CHECK (quality_status IN ('GOOD', 'SUSPECT', 'BAD'))
);
CREATE TABLE IF NOT EXISTS OperatingMode (
    mode_id TEXT PRIMARY KEY,
    facility_id TEXT NOT NULL,
    mode_name TEXT NOT NULL,
    description TEXT,
    pump_speed_percentage REAL NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    FOREIGN KEY (facility_id)
        REFERENCES Facility(facility_id),
    CHECK (pump_speed_percentage >= 0
           AND pump_speed_percentage <= 100),
    CHECK (status IN ('ACTIVE', 'INACTIVE'))
);
CREATE TABLE IF NOT EXISTS Alarm (
    alarm_id TEXT PRIMARY KEY,
    facility_id TEXT NOT NULL,
    equipment_type TEXT,
    equipment_id TEXT,
    alarm_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    description TEXT NOT NULL,
    detected_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'OPEN',
    FOREIGN KEY (facility_id)
        REFERENCES Facility(facility_id),
    CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    CHECK (status IN ('OPEN', 'ACKNOWLEDGED', 'RESOLVED'))
);
CREATE TABLE IF NOT EXISTS SimulationRun (
    simulation_id TEXT PRIMARY KEY,
    facility_id TEXT NOT NULL,
    simulation_name TEXT NOT NULL,
    scenario_type TEXT NOT NULL,
    input_configuration TEXT NOT NULL,
    result_summary TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING',
    started_at TEXT NOT NULL,
    completed_at TEXT,
    FOREIGN KEY (facility_id)
        REFERENCES Facility(facility_id),
    CHECK (status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED'))
);
CREATE TABLE IF NOT EXISTS EventHistory (
    event_id TEXT PRIMARY KEY,
    facility_id TEXT NOT NULL,
    simulation_id TEXT,
    equipment_type TEXT NOT NULL,
    equipment_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    previous_state TEXT,
    new_state TEXT,
    event_description TEXT,
    event_timestamp TEXT NOT NULL,
    FOREIGN KEY (facility_id)
        REFERENCES Facility(facility_id),
    FOREIGN KEY (simulation_id)
        REFERENCES SimulationRun(simulation_id)
);
CREATE TABLE IF NOT EXISTS GroundTruth (
    ground_truth_id TEXT PRIMARY KEY,
    facility_id TEXT NOT NULL,
    simulation_id TEXT,
    equipment_type TEXT NOT NULL,
    equipment_id TEXT NOT NULL,
    issue_type TEXT NOT NULL,
    is_anomaly INTEGER NOT NULL,
    rule_description TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    FOREIGN KEY (facility_id)
        REFERENCES Facility(facility_id),
    FOREIGN KEY (simulation_id)
        REFERENCES SimulationRun(simulation_id),
    CHECK (is_anomaly IN (0, 1)),
    CHECK (issue_type IN (
        'NORMAL',
        'LEAK',
        'BLOCKAGE',
        'PUMP_DEGRADATION',
        'SENSOR_FAULT'
    ))
);
-- Performance indexes

CREATE INDEX IF NOT EXISTS idx_pump_facility
ON Pump(facility_id);

CREATE INDEX IF NOT EXISTS idx_tank_facility
ON Tank(facility_id);

CREATE INDEX IF NOT EXISTS idx_valve_facility
ON Valve(facility_id);

CREATE INDEX IF NOT EXISTS idx_pipe_facility
ON Pipe(facility_id);

CREATE INDEX IF NOT EXISTS idx_sensor_facility
ON Sensor(facility_id);

CREATE INDEX IF NOT EXISTS idx_telemetry_sensor_time
ON Telemetry(sensor_id, recorded_at);

CREATE INDEX IF NOT EXISTS idx_alarm_facility
ON Alarm(facility_id);

CREATE INDEX IF NOT EXISTS idx_simulation_facility
ON SimulationRun(facility_id);

CREATE INDEX IF NOT EXISTS idx_event_facility_time
ON EventHistory(facility_id, event_timestamp);

CREATE INDEX IF NOT EXISTS idx_groundtruth_simulation
ON GroundTruth(simulation_id);