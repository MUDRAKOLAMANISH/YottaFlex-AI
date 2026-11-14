
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "yottaflex.db"

def create_pump_curves():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS PumpCurvePoint (
                curve_point_id TEXT PRIMARY KEY,
                pump_id TEXT NOT NULL,
                speed_percentage REAL NOT NULL,
                head_m REAL NOT NULL,
                flow_lpm REAL NOT NULL,
                source_type TEXT NOT NULL,
                FOREIGN KEY (pump_id) REFERENCES Pump(pump_id),
                CHECK (speed_percentage > 0 AND speed_percentage <= 100),
                CHECK (head_m >= 0),
                CHECK (flow_lpm >= 0),
                CHECK (source_type = 'SYNTHETIC_ASSUMPTION'),
                UNIQUE (pump_id, speed_percentage, head_m)
            )
        """)

        pumps = connection.execute("""
            SELECT pump_id, capacity_lpm
            FROM Pump
            ORDER BY pump_id
        """).fetchall()

        if not pumps:
            raise ValueError("No pumps found in the database.")

        points = []

        for pump_id, capacity in pumps:
            operating_points = [
                (1, 0.0, capacity * 1.20),
                (2, 20.0, capacity),
                (3, 40.0, capacity * 0.70)
            ]

            for number, head, flow in operating_points:
                points.append((
                    f"CURVE-{pump_id}-P{number}",
                    pump_id,
                    100.0,
                    head,
                    round(flow, 2),
                    "SYNTHETIC_ASSUMPTION"
                ))

        connection.executemany("""
            INSERT OR IGNORE INTO PumpCurvePoint (
                curve_point_id,
                pump_id,
                speed_percentage,
                head_m,
                flow_lpm,
                source_type
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, points)

        connection.commit()

        total = connection.execute(
            "SELECT COUNT(*) FROM PumpCurvePoint"
        ).fetchone()[0]

        print("Pump curve table created successfully!")
        print("Pumps:", len(pumps))
        print("Curve points inserted:", len(points))
        print("Total curve points in database:", total)

        if total != len(pumps) * 3:
            raise ValueError("Unexpected pump curve point count.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    create_pump_curves()
