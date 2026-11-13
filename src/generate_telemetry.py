
import sqlite3
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "yottaflex.db"

SEED = 20261022
TOTAL_RECORDS = 100000


def generate_telemetry():
    rng = np.random.default_rng(SEED)
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    sensors = connection.execute("""
        SELECT sensor_id, sensor_type, equipment_type, equipment_id
        FROM Sensor
        ORDER BY sensor_id
    """).fetchall()

    if not sensors:
        raise ValueError("No sensors found. Generate sensors first.")

    # Calculate normal operating baselines
    pump_capacities = dict(connection.execute("""
        SELECT pump_id, capacity_lpm FROM Pump
    """).fetchall())

    tank_capacities = dict(connection.execute("""
        SELECT tank_id, capacity_liters FROM Tank
    """).fetchall())

    base_time = datetime(2026, 10, 22, 0, 0, 0)
    records = []
    remaining = TOTAL_RECORDS

    for index, (sensor_id, sensor_type, equipment_type, equipment_id) in enumerate(sensors):
        sensors_left = len(sensors) - index
        count = remaining // sensors_left
        remaining -= count

        if sensor_type == "FLOW":
            if equipment_type == "PUMP":
                baseline = pump_capacities[equipment_id] * 0.65
            else:
                baseline = 100.0
            variation = baseline * 0.05

        elif sensor_type == "PRESSURE":
            baseline = 2.5
            variation = 0.12

        else:
            baseline = tank_capacities[equipment_id] * 0.60
            variation = tank_capacities[equipment_id] * 0.02

        readings = rng.normal(baseline, variation, count)
        readings = np.maximum(readings, 0)

        for i, reading in enumerate(readings):
            timestamp = base_time + timedelta(minutes=i)

            records.append((
                sensor_id,
                timestamp.isoformat(),
                float(reading),
                "GOOD"
            ))

    connection.executemany("""
        INSERT INTO Telemetry (
            sensor_id,
            recorded_at,
            reading_value,
            quality_status
        )
        VALUES (?, ?, ?, ?)
    """, records)

    connection.commit()

    total = connection.execute(
        "SELECT COUNT(*) FROM Telemetry"
    ).fetchone()[0]

    connection.close()

    print(f"Telemetry records inserted: {len(records)}")
    print(f"Total telemetry records in database: {total}")


if __name__ == "__main__":
    generate_telemetry()
