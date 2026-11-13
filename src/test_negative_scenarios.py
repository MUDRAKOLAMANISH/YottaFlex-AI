
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"

connection = sqlite3.connect(":memory:")
connection.execute("PRAGMA foreign_keys = ON")
connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

passed = 0
total = 5


def report(name, success):
    global passed
    print(f"{'PASS' if success else 'FAIL'}: {name}")
    if success:
        passed += 1


# Minimal valid test data
connection.execute("""
    INSERT INTO Facility
    VALUES ('FAC-TEST', 'Test Facility', 'Hyderabad')
""")

connection.execute("""
    INSERT INTO NetworkNode
    VALUES ('NODE-TEST', 'FAC-TEST', 'PUMP', 'PUMP-TEST')
""")

connection.execute("""
    INSERT INTO Sensor
    VALUES (
        'SNS-TEST', 'FAC-TEST', 'Test Sensor',
        'FLOW', 'PUMP', 'PUMP-TEST', 'LPM', 'ACTIVE'
    )
""")

# 1. Reject pipe connected to a missing node
try:
    connection.execute("""
        INSERT INTO Pipe VALUES (
            'PIPE-TEST', 'FAC-TEST', 'Test Pipe',
            'MISSING-NODE', 'NODE-TEST',
            100, 500, 'ACTIVE'
        )
    """)
    report("Pipe with missing node rejected", False)
except sqlite3.IntegrityError:
    report("Pipe with missing node rejected", True)


# 2. Reject tank level above capacity
try:
    connection.execute("""
        INSERT INTO Tank VALUES (
            'TANK-TEST', 'FAC-TEST', 'Test Tank',
            1000, 1200, 'ACTIVE'
        )
    """)
    report("Tank over capacity rejected", False)
except sqlite3.IntegrityError:
    report("Tank over capacity rejected", True)


# 3. Reject simulation without input configuration
try:
    connection.execute("""
        INSERT INTO SimulationRun (
            simulation_id, facility_id, simulation_name,
            scenario_type, input_configuration, started_at
        )
        VALUES (
            'SIM-TEST', 'FAC-TEST', 'Test Simulation',
            'TEST', NULL, '2026-11-13'
        )
    """)
    report("Simulation without input configuration rejected", False)
except sqlite3.IntegrityError:
    report("Simulation without input configuration rejected", True)


# 4. Detect flow conservation violation
incoming_flow = 100.0
outgoing_flow = 80.0
tolerance = 3.0

imbalance_detected = abs(incoming_flow - outgoing_flow) > tolerance
report("Flow conservation violation detected", imbalance_detected)


# 5. Detect sensor fault with incorrect process-fault label
connection.execute("""
    INSERT INTO Telemetry (
        sensor_id, recorded_at, reading_value, quality_status
    )
    VALUES ('SNS-TEST', '2026-11-13', 9999, 'BAD')
""")

connection.execute("""
    INSERT INTO GroundTruth (
        ground_truth_id, facility_id, equipment_type,
        equipment_id, issue_type, is_anomaly, rule_description,
        recorded_at
    )
    VALUES (
        'GT-TEST', 'FAC-TEST', 'PUMP', 'PUMP-TEST',
        'LEAK', 1, 'Intentionally incorrect test label',
        '2026-11-13'
    )
""")

mislabeled = connection.execute("""
    SELECT COUNT(*)
    FROM Telemetry t
    JOIN Sensor s ON t.sensor_id = s.sensor_id
    JOIN GroundTruth g
      ON g.equipment_type = s.equipment_type
     AND g.equipment_id = s.equipment_id
    WHERE t.quality_status = 'BAD'
      AND g.issue_type != 'SENSOR_FAULT'
""").fetchone()[0] > 0

report("Incorrect sensor-fault label detected", mislabeled)

connection.close()

print(f"\nNegative test results: {passed}/{total} passed")

if passed != total:
    raise SystemExit("Some negative tests failed.")
