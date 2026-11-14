
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

pump_count = connection.execute(
    "SELECT COUNT(*) FROM Pump"
).fetchone()[0]

curve_count = connection.execute(
    "SELECT COUNT(*) FROM PumpCurvePoint"
).fetchone()[0]

pumps_without_curves = connection.execute("""
    SELECT COUNT(*)
    FROM Pump p
    LEFT JOIN PumpCurvePoint c ON p.pump_id = c.pump_id
    WHERE c.curve_point_id IS NULL
""").fetchone()[0]

duplicate_curves = connection.execute("""
    SELECT COUNT(*)
    FROM (
        SELECT pump_id, speed_percentage, head_m
        FROM PumpCurvePoint
        GROUP BY pump_id, speed_percentage, head_m
        HAVING COUNT(*) > 1
    )
""").fetchone()[0]

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

print("TELEMETRY AND PUMP CURVE VALIDATION")
print("-----------------------------------")
print("Total readings:", total)
print("Total sensors:", sensor_count)
print("Total pumps:", pump_count)
print("Pump curve points:", curve_count)
print("Pumps without curves:", pumps_without_curves)
print("Duplicate curve groups:", duplicate_curves)
print("Sensors without readings:", sensors_without_readings)
print("Duplicate sensor timestamps:", duplicate_readings)
print("Foreign key errors:", len(foreign_key_errors))

if (
    total == 100000
    and sensor_count == 220
    and pump_count == 20
    and curve_count == 60
    and pumps_without_curves == 0
    and duplicate_curves == 0
    and sensors_without_readings == 0
    and duplicate_readings == 0
    and len(foreign_key_errors) == 0
):
    print("\nSUCCESS: All telemetry and pump curve checks passed!")
else:
    print("\nWARNING: Some validation checks failed.")

connection.close()
