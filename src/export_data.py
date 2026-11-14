
import sqlite3
import json
import csv
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "yottaflex.db"
EXPORT_DIR = BASE_DIR / "exports"

# All database tables
TABLES = [
    "Facility",
    "Pump",
    "Tank",
    "Valve",
    "NetworkNode",
    "Pipe",
    "Sensor",
    "Telemetry",
    "OperatingMode",
    "Alarm",
    "SimulationRun",
    "EventHistory",
    "GroundTruth",
    "PumpCurvePoint"
]


def export_table(connection, table_name):
    """Export one database table to CSV and JSON."""

    cursor = connection.execute(f'SELECT * FROM "{table_name}"')
    columns = [item[0] for item in cursor.description]
    rows = cursor.fetchall()

    records = [
        dict(zip(columns, row))
        for row in rows
    ]

    # Export CSV
    csv_path = EXPORT_DIR / f"{table_name}.csv"

    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(records)

    # Export JSON
    json_path = EXPORT_DIR / f"{table_name}.json"

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4, ensure_ascii=False)

    print(
        f"{table_name}: {len(records)} records exported"
    )


def main():
    """Export all database tables."""

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    try:
        for table in TABLES:
            export_table(connection, table)

        print("\nAll CSV and JSON exports completed!")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
