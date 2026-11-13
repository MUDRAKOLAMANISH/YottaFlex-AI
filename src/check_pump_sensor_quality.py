
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "yottaflex.db"

connection = sqlite3.connect(DB_PATH)

sensors = connection.execute("""
    SELECT sensor_id, equipment_id, facility_id
    FROM Sensor
    WHERE equipment_type = 'PUMP'
      AND sensor_type = 'FLOW'
    ORDER BY sensor_id
""").fetchall()

print("\nPUMP SENSOR QUALITY CHECK")
print("-------------------------")

for sensor_id, equipment_id, facility_id in sensors:

    readings = connection.execute("""
        SELECT reading_value, quality_status
        FROM Telemetry
        WHERE sensor_id = ?
        ORDER BY recorded_at DESC
        LIMIT 5
    """, (sensor_id,)).fetchall()

    print(f"\n{equipment_id} | {sensor_id}")

    for value, quality in readings:
        print(f"Value: {value:.2f} | Quality: {quality}")

connection.close()
