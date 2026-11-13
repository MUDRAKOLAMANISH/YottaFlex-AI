
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "yottaflex.db"


def calibrate_valve_flow():
    connection = sqlite3.connect(DB_PATH)

    facilities = connection.execute("""
        SELECT facility_id, facility_name
        FROM Facility
        ORDER BY facility_id
    """).fetchall()

    for facility_id, facility_name in facilities:

        # Calculate normal expected pump flow
        pumps = connection.execute("""
            SELECT capacity_lpm
            FROM Pump
            WHERE facility_id = ?
        """, (facility_id,)).fetchall()

        expected_inflow = sum(
            capacity * 0.65 for (capacity,) in pumps
        )

        # Find all valve flow sensors
        valve_sensors = connection.execute("""
            SELECT sensor_id
            FROM Sensor
            WHERE facility_id = ?
              AND equipment_type = 'VALVE'
              AND sensor_type = 'FLOW'
        """, (facility_id,)).fetchall()

        if not valve_sensors:
            continue

        valve_count = len(valve_sensors)
        normal_valve_flow = expected_inflow / valve_count

        # Update only GOOD readings.
        # Keep the injected BAD sensor reading unchanged.
        for (sensor_id,) in valve_sensors:
            connection.execute("""
                UPDATE Telemetry
                SET reading_value = ?
                WHERE sensor_id = ?
                  AND quality_status = 'GOOD'
            """, (normal_valve_flow, sensor_id))

        print(f"\nFacility: {facility_name}")
        print(f"Expected pump inflow: {expected_inflow:.2f} LPM")
        print(f"Valve count: {valve_count}")
        print(f"New flow per valve: {normal_valve_flow:.2f} LPM")

    connection.commit()
    connection.close()

    print("\nValve flow calibration completed!")


if __name__ == "__main__":
    calibrate_valve_flow()
