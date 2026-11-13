# YottaFlex AI — Data Dictionary

## 1. Overview

YottaFlex AI uses a SQLite relational database to represent industrial water infrastructure, monitor telemetry, detect anomalies, and record simulation and event history.

The database contains 13 tables:

1. Facility
2. Pump
3. Tank
4. Valve
5. NetworkNode
6. Pipe
7. Sensor
8. Telemetry
9. OperatingMode
10. Alarm
11. SimulationRun
12. EventHistory
13. GroundTruth

## 2. Table Definitions

### 2.1 Facility

Stores information about each water infrastructure facility.

| Column | Type | Constraint | Description |
|---|---|---|---|
| facility_id | TEXT | Primary Key | Unique facility identifier |
| facility_name | TEXT | NOT NULL | Facility name |
| location | TEXT | NOT NULL | Facility location |

Relationship:
- One Facility can have multiple Pumps, Tanks, Valves, Sensors, Pipes, and other operational records.

### 2.2 Pump

Stores pump equipment and its rated capacity.

| Column | Type | Constraint | Description |
|---|---|---|---|
| pump_id | TEXT | Primary Key | Unique pump identifier |
| facility_id | TEXT | Foreign Key | Associated facility |
| pump_name | TEXT | NOT NULL | Pump name |
| capacity_lpm | REAL | NOT NULL | Rated capacity in litres per minute |
| status | TEXT | NOT NULL | Current pump status |

Relationship:
- Each Pump belongs to one Facility.
- A Facility can contain multiple Pumps.

### 2.3 Tank

Stores water tank capacity and current water level.

| Column | Type | Constraint | Description |
|---|---|---|---|
| tank_id | TEXT | Primary Key | Unique tank identifier |
| facility_id | TEXT | Foreign Key | Associated facility |
| tank_name | TEXT | NOT NULL | Tank name |
| capacity_liters | REAL | CHECK > 0 | Maximum tank capacity |
| current_level_liters | REAL | CHECK constraints | Current water volume |
| status | TEXT | NOT NULL | Current tank status |

Validation:
- Capacity must be greater than zero.
- Current level cannot be negative.
- Current level cannot exceed tank capacity.

### 2.4 Valve

Stores valve information and opening conditions.

| Column | Type | Constraint | Description |
|---|---|---|---|
| valve_id | TEXT | Primary Key | Unique valve identifier |
| facility_id | TEXT | Foreign Key | Associated facility |
| valve_name | TEXT | NOT NULL | Valve name |
| state | TEXT | CHECK | OPEN, CLOSED, PARTIALLY_OPEN |
| opening_percentage | REAL | 0–100 | Valve opening percentage |

### 2.5 NetworkNode

Represents equipment nodes in the water network topology.

| Column | Type | Constraint | Description |
|---|---|---|---|
| node_id | TEXT | Primary Key | Unique network node |
| facility_id | TEXT | Foreign Key | Associated facility |
| equipment_type | TEXT | CHECK | PUMP, TANK, or VALVE |
| equipment_id | TEXT | UNIQUE with facility and type | Referenced equipment identifier |

Note:
- Equipment references are stored using equipment_type and equipment_id.
- The equipment_id reference is validated at application level because it is polymorphic.

### 2.6 Pipe

Stores physical connections between network nodes.

| Column | Type | Constraint | Description |
|---|---|---|---|
| pipe_id | TEXT | Primary Key | Unique pipe identifier |
| facility_id | TEXT | Foreign Key | Associated facility |
| pipe_name | TEXT | NOT NULL | Pipe name |
| source_node_id | TEXT | Foreign Key | Starting network node |
| target_node_id | TEXT | Foreign Key | Ending network node |
| diameter_mm | REAL | CHECK > 0 | Pipe diameter in millimetres |
| max_flow_lpm | REAL | CHECK > 0 | Maximum flow capacity |
| status | TEXT | NOT NULL | Current pipe status |

Validation:
- Source and target nodes must be different.
- Both nodes must exist in NetworkNode.
- Pipe diameter and maximum flow must be positive.

### 2.7 Sensor

Stores sensor configuration and equipment associations.

| Column | Type | Constraint | Description |
|---|---|---|---|
| sensor_id | TEXT | Primary Key | Unique sensor identifier |
| facility_id | TEXT | Foreign Key | Associated facility |
| sensor_name | TEXT | NOT NULL | Sensor name |
| sensor_type | TEXT | CHECK | FLOW, PRESSURE, or LEVEL |
| equipment_type | TEXT | CHECK | PUMP, TANK, VALVE, or PIPE |
| equipment_id | TEXT | NOT NULL | Associated equipment identifier |
| unit | TEXT | NOT NULL | Measurement unit |
| status | TEXT | NOT NULL | Sensor status |

Note:
- Equipment associations use a polymorphic equipment identifier.
- The equipment reference is checked by application-level validation.

### 2.8 Telemetry

Stores time-series readings collected from sensors.

| Column | Type | Constraint | Description |
|---|---|---|---|
| telemetry_id | INTEGER | Primary Key, AUTOINCREMENT | Unique telemetry record |
| sensor_id | TEXT | Foreign Key | Source sensor |
| recorded_at | TEXT | NOT NULL | Reading timestamp |
| reading_value | REAL | NOT NULL | Measured value |
| quality_status | TEXT | CHECK | GOOD, SUSPECT, or BAD |

### 2.9 OperatingMode

Stores facility operating configurations.

| Column | Type | Constraint | Description |
|---|---|---|---|
| mode_id | TEXT | Primary Key | Unique operating mode |
| facility_id | TEXT | Foreign Key | Associated facility |
| mode_name | TEXT | NOT NULL | Operating mode name |
| description | TEXT | Optional | Mode description |
| pump_speed_percentage | REAL | 0–100 | Pump speed setting |
| created_at | TEXT | NOT NULL | Creation timestamp |
| status | TEXT | ACTIVE or INACTIVE | Operating mode status |

### 2.10 Alarm

Stores detected anomalies and operational alarms.

| Column | Type | Constraint | Description |
|---|---|---|---|
| alarm_id | TEXT | Primary Key | Unique alarm identifier |
| facility_id | TEXT | Foreign Key | Associated facility |
| equipment_type | TEXT | Optional | Equipment category |
| equipment_id | TEXT | Optional | Equipment identifier |
| alarm_type | TEXT | NOT NULL | Detected issue type |
| severity | TEXT | CHECK | LOW, MEDIUM, HIGH, CRITICAL |
| description | TEXT | NOT NULL | Alarm details |
| detected_at | TEXT | NOT NULL | Detection timestamp |
| status | TEXT | OPEN by default | OPEN, ACKNOWLEDGED, RESOLVED |

### 2.11 SimulationRun

Stores simulation execution details and results.

| Column | Type | Constraint | Description |
|---|---|---|---|
| simulation_id | TEXT | Primary Key | Unique simulation identifier |
| facility_id | TEXT | Foreign Key | Associated facility |
| simulation_name | TEXT | NOT NULL | Simulation name |
| scenario_type | TEXT | NOT NULL | Scenario category |
| input_configuration | TEXT | NOT NULL | Simulation input configuration |
| result_summary | TEXT | Optional | Simulation result summary |
| status | TEXT | CHECK | PENDING, RUNNING, COMPLETED, FAILED |
| started_at | TEXT | NOT NULL | Start timestamp |
| completed_at | TEXT | Optional | Completion timestamp |

### 2.12 EventHistory

Maintains a record of equipment and operational events.

| Column | Type | Constraint | Description |
|---|---|---|---|
| event_id | TEXT | Primary Key | Unique event identifier |
| facility_id | TEXT | Foreign Key | Associated facility |
| simulation_id | TEXT | Optional Foreign Key | Related simulation |
| equipment_type | TEXT | NOT NULL | Equipment category |
| equipment_id | TEXT | NOT NULL | Equipment identifier |
| event_type | TEXT | NOT NULL | Event category |
| previous_state | TEXT | Optional | Previous equipment state |
| new_state | TEXT | Optional | Updated equipment state |
| event_description | TEXT | Optional | Event details |
| event_timestamp | TEXT | NOT NULL | Event timestamp |

### 2.13 GroundTruth

Stores expected anomaly labels for evaluation.

| Column | Type | Constraint | Description |
|---|---|---|---|
| ground_truth_id | TEXT | Primary Key | Unique ground truth identifier |
| facility_id | TEXT | Foreign Key | Associated facility |
| simulation_id | TEXT | Optional Foreign Key | Related simulation |
| equipment_type | TEXT | NOT NULL | Equipment category |
| equipment_id | TEXT | NOT NULL | Equipment identifier |
| issue_type | TEXT | CHECK | NORMAL, LEAK, BLOCKAGE, PUMP_DEGRADATION, SENSOR_FAULT |
| is_anomaly | INTEGER | 0 or 1 | Expected anomaly indicator |
| rule_description | TEXT | NOT NULL | Rule used to assign the label |
| recorded_at | TEXT | NOT NULL | Label timestamp |

## 3. Relationships and Cardinality

| Parent Table | Child Table | Relationship |
|---|---|---|
| Facility | Pump | One-to-Many |
| Facility | Tank | One-to-Many |
| Facility | Valve | One-to-Many |
| Facility | NetworkNode | One-to-Many |
| Facility | Pipe | One-to-Many |
| Facility | Sensor | One-to-Many |
| Facility | OperatingMode | One-to-Many |
| Facility | Alarm | One-to-Many |
| Facility | SimulationRun | One-to-Many |
| Facility | EventHistory | One-to-Many |
| Facility | GroundTruth | One-to-Many |
| NetworkNode | Pipe | One-to-Many as source |
| NetworkNode | Pipe | One-to-Many as target |
| Sensor | Telemetry | One-to-Many |
| SimulationRun | EventHistory | One-to-Many, optional |
| SimulationRun | GroundTruth | One-to-Many, optional |

## 4. Data Integrity and Validation

The database uses:

- Primary keys to uniquely identify records.
- Foreign keys to maintain relational integrity.
- NOT NULL constraints for mandatory fields.
- CHECK constraints for valid equipment states and measurement ranges.
- UNIQUE constraints for network equipment associations.
- Indexes to improve query performance.
- Application-level validation for polymorphic equipment references.

## 5. Indexes

The following indexes support common queries:

| Index | Table | Purpose |
|---|---|---|
| idx_pump_facility | Pump | Facility-based pump lookup |
| idx_tank_facility | Tank | Facility-based tank lookup |
| idx_valve_facility | Valve | Facility-based valve lookup |
| idx_pipe_facility | Pipe | Facility-based pipe lookup |
| idx_sensor_facility | Sensor | Facility-based sensor lookup |
| idx_telemetry_sensor_time | Telemetry | Sensor and timestamp lookup |
| idx_alarm_facility | Alarm | Facility-based alarm lookup |
| idx_simulation_facility | SimulationRun | Facility-based simulation lookup |
| idx_event_facility_time | EventHistory | Facility and event-time lookup |
| idx_groundtruth_simulation | GroundTruth | Simulation-based label lookup |

## 6. Design Notes and Limitations

- The database uses SQLite for lightweight local storage.
- Telemetry is stored as time-series records linked to sensors.
- Network topology is represented using NetworkNode and Pipe.
- GroundTruth provides expected labels for anomaly evaluation.
- Equipment references in Sensor, NetworkNode, Alarm, EventHistory, and GroundTruth use equipment_type and equipment_id rather than direct foreign keys to every equipment table.
- Some cross-table and lifecycle validations are handled by application logic rather than database constraints.
- The current schema does not contain a separate pump-curve table.
- This database uses synthetic data and is intended as a demonstration system, not a validated hydraulic engineering model.