
import sqlite3
from pathlib import Path
from statistics import median

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "yottaflex.db"


def check_flow_balance():
    connection = sqlite3.connect(DB_PATH)

    facilities = connection.execute("""
        SELECT facility_id, facility_name
        FROM Facility
        ORDER BY facility_id
    """).fetchall()

    print("\nFLOW DATA DIAGNOSTIC")
    print("--------------------")

    for facility_id, facility_name in facilities:

        sensors = connection.execute("""
            SELECT sensor_id, equipment_type
            FROM Sensor
            WHERE facility_id = ?
              AND sensor_type = 'FLOW'
            ORDER BY sensor_id
        """, (facility_id,)).fetchall()

        pump_total = 0
        valve_total = 0

        for sensor_id, equipment_type in sensors:
            readings = connection.execute("""
                SELECT reading_value
                FROM Telemetry
                WHERE sensor_id = ?
                  AND quality_status = 'GOOD'
                ORDER BY recorded_at DESC
                LIMIT 30
            """, (sensor_id,)).fetchall()

            if not readings:
                continue

            flow = median([row[0] for row in readings])

            if equipment_type == "PUMP":
                pump_total += flow
            elif equipment_type == "VALVE":
                valve_total += flow

        difference = pump_total - valve_total

        print(f"\nFacility: {facility_name}")
        print(f"Pump inflow: {pump_total:.2f} LPM")
        print(f"Valve outflow: {valve_total:.2f} LPM")
        print(f"Difference: {difference:.2f} LPM")

    connection.close()


if __name__ == "__main__":
    check_flow_balance()
