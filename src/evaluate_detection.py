
import sqlite3
from pathlib import Path

from detection_engine import detect_anomalies

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "yottaflex.db"


def evaluate_detection():
    connection = sqlite3.connect(DB_PATH)

    # Read equipment information
    sensors = connection.execute("""
        SELECT equipment_type, equipment_id
        FROM Sensor
    """).fetchall()

    # Get existing ground-truth labels
    existing = connection.execute("""
        SELECT equipment_type, equipment_id
        FROM GroundTruth
    """).fetchall()

    labelled = set(existing)

    timestamp = connection.execute("""
        SELECT MAX(recorded_at)
        FROM Telemetry
    """).fetchone()[0]

    # Add normal labels for remaining equipment
    normal_records = []

    for equipment_type, equipment_id in sensors:
        key = (equipment_type, equipment_id)

        if key not in labelled:
            facility = connection.execute("""
                SELECT facility_id
                FROM Sensor
                WHERE equipment_type = ? AND equipment_id = ?
                LIMIT 1
            """, (equipment_type, equipment_id)).fetchone()[0]

            normal_records.append((
                f"GT-NORMAL-{equipment_id}",
                facility,
                equipment_type,
                equipment_id,
                timestamp
            ))

    connection.executemany("""
        INSERT OR IGNORE INTO GroundTruth (
            ground_truth_id,
            facility_id,
            equipment_type,
            equipment_id,
            issue_type,
            is_anomaly,
            rule_description,
            recorded_at
        )
        VALUES (?, ?, ?, ?, 'NORMAL', 0,
                'Synthetic baseline operating condition', ?)
    """, normal_records)

    connection.commit()

    # Read actual anomaly and normal labels
    truth_rows = connection.execute("""
        SELECT equipment_type, equipment_id, is_anomaly
        FROM GroundTruth
    """).fetchall()

    actual_anomalies = {
        (equipment_type, equipment_id)
        for equipment_type, equipment_id, is_anomaly in truth_rows
        if is_anomaly == 1
    }

    normal_equipment = {
        (equipment_type, equipment_id)
        for equipment_type, equipment_id, is_anomaly in truth_rows
        if is_anomaly == 0
    }

    connection.close()

    # Get predictions from detection engine
    predictions = detect_anomalies()

    detected = {
        (item["equipment_type"], item["equipment_id"])
        for item in predictions
    }

    # Calculate confusion matrix
    tp = len(actual_anomalies & detected)
    fp = len(normal_equipment & detected)
    fn = len(actual_anomalies - detected)
    tn = len(normal_equipment - detected)

    total = tp + fp + fn + tn

    accuracy = (tp + tn) / total if total else 0
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0
    )

    print("\nDETECTION EVALUATION")
    print("--------------------")
    print("Ground-truth normal labels added:", len(normal_records))
    print("True Positives:", tp)
    print("False Positives:", fp)
    print("False Negatives:", fn)
    print("True Negatives:", tn)
    print("Total evaluated:", total)

    print("\nMETRICS")
    print("--------------------")
    print(f"Accuracy:  {accuracy:.2%}")
    print(f"Precision: {precision:.2%}")
    print(f"Recall:    {recall:.2%}")
    print(f"F1 Score:  {f1:.2%}")


if __name__ == "__main__":
    evaluate_detection()
