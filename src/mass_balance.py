
import sqlite3
from pathlib import Path
from statistics import median

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "yottaflex.db"

IMBALANCE_THRESHOLD = 3.0
MIN_VALID_COVERAGE = 1.0


def get_equipment_flow(connection, facility_id, equipment_type):
    sensors = connection.execute("""
        SELECT sensor_id
        FROM Sensor
        WHERE facility_id = ?
          AND equipment_type = ?
          AND sensor_type = 'FLOW'
    """, (facility_id, equipment_type)).fetchall()

    total_flow = 0.0
    valid_sensors = 0
    invalid_sensors = []

    for (sensor_id,) in sensors:
        # Get the latest 30 readings, regardless of quality
        readings = connection.execute("""
            SELECT reading_value, quality_status
            FROM Telemetry
            WHERE sensor_id = ?
            ORDER BY recorded_at DESC
            LIMIT 30
        """, (sensor_id,)).fetchall()

        if len(readings) < 30:
            invalid_sensors.append(sensor_id)
            continue

        # Reject sensors with any non-GOOD recent reading
        if any(row[1] != "GOOD" for row in readings):
            invalid_sensors.append(sensor_id)
            continue

        values = [row[0] for row in readings]
        total_flow += median(values)
        valid_sensors += 1

    return total_flow, valid_sensors, len(sensors), invalid_sensors


def detect_mass_imbalance():
    connection = sqlite3.connect(DB_PATH)

    try:
        facilities = connection.execute("""
            SELECT facility_id, facility_name
            FROM Facility
            ORDER BY facility_id
        """).fetchall()

        print("\nWATER MASS-BALANCE ANALYSIS")
        print("---------------------------")

        for facility_id, facility_name in facilities:

            inflow, valid_pumps, total_pumps, bad_pumps = (
                get_equipment_flow(connection, facility_id, "PUMP")
            )

            outflow, valid_valves, total_valves, bad_valves = (
                get_equipment_flow(connection, facility_id, "VALVE")
            )

            pump_coverage = (
                valid_pumps / total_pumps if total_pumps else 0
            )

            valve_coverage = (
                valid_valves / total_valves if total_valves else 0
            )

            print(f"\nFacility: {facility_name}")
            print(f"Valid pump sensors: {valid_pumps}/{total_pumps}")
            print(f"Valid valve sensors: {valid_valves}/{total_valves}")

            if bad_pumps:
                print("Invalid pump sensors:", ", ".join(bad_pumps))

            if bad_valves:
                print("Invalid valve sensors:", ", ".join(bad_valves))

            # Check data quality BEFORE calculating mass balance
            if (
                pump_coverage < MIN_VALID_COVERAGE
                or valve_coverage < MIN_VALID_COVERAGE
            ):
                print("Status: SENSOR DATA INCOMPLETE")
                print("Mass balance cannot be reliably evaluated.")
                continue

            if outflow == 0:
                print("Status: INSUFFICIENT FLOW DATA")
                continue

            difference = inflow - outflow
            imbalance_percentage = abs(difference) / outflow * 100

            print(f"Pump inflow: {inflow:.2f} LPM")
            print(f"Valve outflow: {outflow:.2f} LPM")
            print(f"Difference: {difference:.2f} LPM")
            print(f"Imbalance: {imbalance_percentage:.2f}%")

            if imbalance_percentage > IMBALANCE_THRESHOLD:
                status = "IMBALANCE DETECTED"
            else:
                status = "BALANCED"

            print(f"Status: {status}")

    finally:
        connection.close()


if __name__ == "__main__":
    detect_mass_imbalance()
