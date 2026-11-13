
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "yottaflex.db"

connection = sqlite3.connect(DB_PATH)

total = connection.execute(
    "SELECT COUNT(*) FROM Telemetry"
).fetchone()[0]

sensor_count = connection.execute(
    "SELECT COUNT(*) FROM Sensor"
).fetchone()[0]

sensors_without_readings = connection.execute("""
    SELECT COUNT(*)
    FROM Sensor s
    LEFT JOIN Telemetry t ON s.sensor_id = t.sensor_id
    WHERE t.telemetry_id IS NULL
""").fetchone()[0]

duplicate_readings = connection.execute("""
    SELECT COUNT(*)
    FROM (
        SELECT sensor_id, recorded_at
        FROM Telemetry
        GROUP BY sensor_id, recorded_at
        HAVING COUNT(*) > 1
    )
""").fetchone()[0]

foreign_key_errors = connection.execute(
    "PRAGMA foreign_key_check"
).fetchall()

print("TELEMETRY VALIDATION")
print("--------------------")
print("Total readings:", total)
print("Total sensors:", sensor_count)
print("Sensors without readings:", sensors_without_readings)
print("Duplicate sensor timestamps:", duplicate_readings)
print("Foreign key errors:", len(foreign_key_errors))

if (
    total == 100000
    and sensor_count == 220
    and sensors_without_readings == 0
    and duplicate_readings == 0
    and len(foreign_key_errors) == 0
):
    print("\nSUCCESS: All telemetry checks passed!")
else:
    print("\nWARNING: Some validation checks failed.")

connection.close()
