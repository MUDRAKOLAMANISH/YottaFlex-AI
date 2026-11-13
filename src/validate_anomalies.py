
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "yottaflex.db"

connection = sqlite3.connect(DB_PATH)

checks = {
    "Telemetry records": """
        SELECT COUNT(*) FROM Telemetry
    """,
    "Simulation runs": """
        SELECT COUNT(*) FROM SimulationRun
    """,
    "Ground-truth labels": """
        SELECT COUNT(*) FROM GroundTruth
    """,
    "Alarms": """
        SELECT COUNT(*) FROM Alarm
    """,
    "Event-history records": """
        SELECT COUNT(*) FROM EventHistory
    """
}

print("ANOMALY VALIDATION")
print("------------------")

results = {}

for name, query in checks.items():
    count = connection.execute(query).fetchone()[0]
    results[name] = count
    print(f"{name}: {count}")

expected = {
    "Telemetry records": 100000,
    "Simulation runs": 4,
    "Ground-truth labels": 4,
    "Alarms": 4,
    "Event-history records": 4
}

# Check the 30 modified readings for each sensor.
scenarios = [
    ("SNS-PIPE-001", 1.2, "GOOD"),
    ("SNS-PIPE-002", 4.0, "GOOD"),
    ("SNS-PUMP-001", 46.8, "GOOD"),
    ("SNS-PUMP-002", 9999.0, "BAD")
]

readings_valid = True

for sensor_id, expected_value, expected_quality in scenarios:
    actual = connection.execute("""
        SELECT COUNT(*)
        FROM Telemetry
        WHERE sensor_id = ?
          AND reading_value = ?
          AND quality_status = ?
    """, (sensor_id, expected_value, expected_quality)).fetchone()[0]

    print(f"{sensor_id}: {actual} matching readings")

    if actual != 30:
        readings_valid = False

counts_valid = results == expected

print("\nResult:")

if counts_valid and readings_valid:
    print("SUCCESS: All anomaly validation checks passed!")
else:
    print("WARNING: Some checks failed. Review the output.")

connection.close()
