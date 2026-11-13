
import sqlite3
from pathlib import Path
from statistics import median

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "yottaflex.db"


def detect_anomalies():
    connection = sqlite3.connect(DB_PATH)

    sensors = connection.execute("""
        SELECT sensor_id, sensor_type, equipment_type, equipment_id
        FROM Sensor
        ORDER BY sensor_id
    """).fetchall()

    detections = []

    pump_capacities = dict(connection.execute("""
        SELECT pump_id, capacity_lpm
        FROM Pump
    """).fetchall())

    for sensor_id, sensor_type, equipment_type, equipment_id in sensors:

        readings = connection.execute("""
            SELECT reading_value, quality_status
            FROM Telemetry
            WHERE sensor_id = ?
            ORDER BY recorded_at DESC
            LIMIT 30
        """, (sensor_id,)).fetchall()

        if not readings:
            continue

        values = [row[0] for row in readings]
        quality = [row[1] for row in readings]

        average_value = median(values)
        issue = None

        # Rule 1: Sensor fault
        if "BAD" in quality:
            issue = "SENSOR_FAULT"

        # Rule 2: Pipe leak or blockage
        elif equipment_type == "PIPE" and sensor_type == "PRESSURE":

            if average_value < 1.5:
                issue = "LEAK"

            elif average_value > 3.5:
                issue = "BLOCKAGE"

        # Rule 3: Pump degradation
        elif equipment_type == "PUMP" and sensor_type == "FLOW":

            capacity = pump_capacities[equipment_id]

            if average_value < capacity * 0.50:
                issue = "PUMP_DEGRADATION"

        if issue:
            detections.append({
    "sensor_id": sensor_id,
    "equipment_type": equipment_type,
    "equipment_id": equipment_id,
    "issue_type": issue,
    "measured_value": round(average_value, 2)
})

    connection.close()

    return detections


if __name__ == "__main__":
    results = detect_anomalies()

    print("\nANOMALY DETECTION RESULTS")
    print("------------------------")

    for result in results:
        print(
            result["issue_type"],
            "|",
            result["equipment_id"],
            "| Value:",
            result["measured_value"]
        )

    print("\nTotal anomalies detected:", len(results))
