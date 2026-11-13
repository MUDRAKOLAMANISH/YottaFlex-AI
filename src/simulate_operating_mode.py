
import json
from datetime import datetime
from db import get_connection

BASELINE_SPEED = 65
NEW_SPEED = 80

connection = get_connection()

try:
    facilities = connection.execute("""
        SELECT facility_id, facility_name
        FROM Facility
        ORDER BY facility_id
    """).fetchall()

    print("\nOPERATING MODE SIMULATION")
    print("=========================")
    print(f"Baseline pump speed: {BASELINE_SPEED}%")
    print(f"New pump speed: {NEW_SPEED}%")

    for facility_id, facility_name in facilities:

        total_capacity = connection.execute("""
            SELECT COALESCE(SUM(capacity_lpm), 0)
            FROM Pump
            WHERE facility_id = ?
              AND status = 'ACTIVE'
        """, (facility_id,)).fetchone()[0]

        baseline_flow = total_capacity * BASELINE_SPEED / 100
        simulated_flow = total_capacity * NEW_SPEED / 100
        increase = simulated_flow - baseline_flow

        mode_id = f"MODE-80-{facility_id}"
        simulation_id = f"SIM-OP-80-{facility_id}"

        now = datetime.now().isoformat(timespec="seconds")

        config = {
            "baseline_speed_percentage": BASELINE_SPEED,
            "new_speed_percentage": NEW_SPEED,
            "pump_capacity_lpm": total_capacity,
            "model": "Linear proportional estimate"
        }

        result = {
            "baseline_estimated_flow_lpm": round(baseline_flow, 2),
            "simulated_estimated_flow_lpm": round(simulated_flow, 2),
            "estimated_increase_lpm": round(increase, 2)
        }

        connection.execute("""
            INSERT OR IGNORE INTO OperatingMode (
                mode_id, facility_id, mode_name, description,
                pump_speed_percentage, created_at, status
            )
            VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE')
        """, (
            mode_id, facility_id, "High Output Mode",
            "Simulated operation at 80% pump speed",
            NEW_SPEED, now
        ))

        connection.execute("""
            INSERT OR IGNORE INTO SimulationRun (
                simulation_id, facility_id, simulation_name,
                scenario_type, input_configuration,
                result_summary, status, started_at, completed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, 'COMPLETED', ?, ?)
        """, (
            simulation_id, facility_id,
            "Pump Speed Increase Simulation",
            "OPERATING_MODE_CHANGE",
            json.dumps(config),
            json.dumps(result),
            now, now
        ))

        print(f"\n{facility_name}")
        print(f"Total pump capacity: {total_capacity:.2f} LPM")
        print(f"Baseline estimated flow: {baseline_flow:.2f} LPM")
        print(f"Simulated estimated flow: {simulated_flow:.2f} LPM")
        print(f"Estimated increase: {increase:.2f} LPM")

    connection.commit()
    print("\nSimulation records saved successfully!")

except Exception:
    connection.rollback()
    raise

finally:
    connection.close()
