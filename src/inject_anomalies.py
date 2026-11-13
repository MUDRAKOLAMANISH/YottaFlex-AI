
import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "yottaflex.db"

SCENARIOS = [
    {
        "simulation_id": "SIM-2026-000001",
        "ground_truth_id": "GT-001",
        "alarm_id": "ALM-001",
        "sensor_id": "SNS-PIPE-001",
        "equipment_type": "PIPE",
        "equipment_id": "PIPE-001",
        "issue_type": "LEAK",
        "value": 1.2,
        "quality": "GOOD",
        "severity": "HIGH",
        "rule": "Pipe pressure below 1.5 BAR for 30 latest readings."
    },
    {
        "simulation_id": "SIM-2026-000002",
        "ground_truth_id": "GT-002",
        "alarm_id": "ALM-002",
        "sensor_id": "SNS-PIPE-002",
        "equipment_type": "PIPE",
        "equipment_id": "PIPE-002",
        "issue_type": "BLOCKAGE",
        "value": 4.0,
        "quality": "GOOD",
        "severity": "HIGH",
        "rule": "Pipe pressure above 3.5 BAR for 30 latest readings."
    },
    {
        "simulation_id": "SIM-2026-000003",
        "ground_truth_id": "GT-003",
        "alarm_id": "ALM-003",
        "sensor_id": "SNS-PUMP-001",
        "equipment_type": "PUMP",
        "equipment_id": "PUMP-001",
        "issue_type": "PUMP_DEGRADATION",
        "value": 46.8,
        "quality": "GOOD",
        "severity": "HIGH",
        "rule": "Pump flow below 50 percent of rated capacity."
    },
    {
        "simulation_id": "SIM-2026-000004",
        "ground_truth_id": "GT-004",
        "alarm_id": "ALM-004",
        "sensor_id": "SNS-PUMP-002",
        "equipment_type": "PUMP",
        "equipment_id": "PUMP-002",
        "issue_type": "SENSOR_FAULT",
        "value": 9999.0,
        "quality": "BAD",
        "severity": "CRITICAL",
        "rule": "Sensor reports BAD quality and an unrealistic flow reading."
    }
]


def inject_anomalies():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        with connection:
            latest_time = connection.execute("""
                SELECT MAX(recorded_at) FROM Telemetry
            """).fetchone()[0]

            if latest_time is None:
                raise ValueError("Telemetry data not found.")

            for scenario in SCENARIOS:
                sensor_id = scenario["sensor_id"]

                # Verify that the sensor exists.
                sensor = connection.execute("""
                    SELECT sensor_id
                    FROM Sensor
                    WHERE sensor_id = ?
                """, (sensor_id,)).fetchone()

                if sensor is None:
                    raise ValueError(f"Sensor not found: {sensor_id}")

                # Change the latest 30 readings.
                cursor = connection.execute("""
                    UPDATE Telemetry
                    SET reading_value = ?,
                        quality_status = ?
                    WHERE telemetry_id IN (
                        SELECT telemetry_id
                        FROM Telemetry
                        WHERE sensor_id = ?
                        ORDER BY recorded_at DESC
                        LIMIT 30
                    )
                """, (
                    scenario["value"],
                    scenario["quality"],
                    sensor_id
                ))

                if cursor.rowcount != 30:
                    raise ValueError(
                        f"Expected 30 readings for {sensor_id}, "
                        f"updated {cursor.rowcount}"
                    )

                simulation_id = scenario["simulation_id"]
                equipment_type = scenario["equipment_type"]
                equipment_id = scenario["equipment_id"]
                issue_type = scenario["issue_type"]

                # Record the simulation.
                connection.execute("""
                    INSERT OR IGNORE INTO SimulationRun (
                        simulation_id,
                        facility_id,
                        simulation_name,
                        scenario_type,
                        input_configuration,
                        result_summary,
                        status,
                        started_at,
                        completed_at
                    )
                    VALUES (?, 'FAC-001', ?, ?, ?, ?, 'COMPLETED', ?, ?)
                """, (
                    simulation_id,
                    issue_type + " scenario",
                    issue_type,
                    json.dumps(scenario),
                    "Injected into 30 latest sensor readings.",
                    latest_time,
                    latest_time
                ))

                # Record the known expected label.
                connection.execute("""
                    INSERT OR IGNORE INTO GroundTruth (
                        ground_truth_id,
                        facility_id,
                        simulation_id,
                        equipment_type,
                        equipment_id,
                        issue_type,
                        is_anomaly,
                        rule_description,
                        recorded_at
                    )
                    VALUES (?, 'FAC-001', ?, ?, ?, ?, 1, ?, ?)
                """, (
                    scenario["ground_truth_id"],
                    simulation_id,
                    equipment_type,
                    equipment_id,
                    issue_type,
                    scenario["rule"],
                    latest_time
                ))

                # Create an alarm.
                connection.execute("""
                    INSERT OR IGNORE INTO Alarm (
                        alarm_id,
                        facility_id,
                        equipment_type,
                        equipment_id,
                        alarm_type,
                        severity,
                        description,
                        detected_at
                    )
                    VALUES (?, 'FAC-001', ?, ?, ?, ?, ?, ?)
                """, (
                    scenario["alarm_id"],
                    equipment_type,
                    equipment_id,
                    issue_type,
                    scenario["severity"],
                    scenario["rule"],
                    latest_time
                ))

                # Record the change in event history.
                connection.execute("""
                    INSERT OR IGNORE INTO EventHistory (
                        event_id,
                        facility_id,
                        simulation_id,
                        equipment_type,
                        equipment_id,
                        event_type,
                        previous_state,
                        new_state,
                        event_description,
                        event_timestamp
                    )
                    VALUES (?, 'FAC-001', ?, ?, ?,
                            'ANOMALY_INJECTED', 'NORMAL',
                            ?, ?, ?)
                """, (
                    "EVT-" + scenario["ground_truth_id"],
                    simulation_id,
                    equipment_type,
                    equipment_id,
                    issue_type,
                    scenario["rule"],
                    latest_time
                ))

                print(f"Injected: {issue_type}")

        print("\nAll four scenarios processed successfully!")

    finally:
        connection.close()


if __name__ == "__main__":
    inject_anomalies()
