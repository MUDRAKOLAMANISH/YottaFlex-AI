
# YottaFlex AI — Validation Summary

## 1. Project Overview

YottaFlex AI is a synthetic water infrastructure monitoring and anomaly detection system.

This document summarizes the validation checks performed on the database, telemetry, anomaly detection results, and mass balance calculations.

## 2. Dataset Validation

| Validation Item | Expected / Actual Result | Status |
|---|---:|---|
| Facilities | 3 | PASS |
| Pumps | 20 | PASS |
| Tanks | 30 | PASS |
| Valves | 60 | PASS |
| Network Nodes | 110 | PASS |
| Pipes | 110 | PASS |
| Sensors | 220 | PASS |
| Telemetry Records | 100,000 | PASS |
| Duplicate telemetry records | 0 | PASS |
| Missing sensor references | 0 | PASS |

## 3. Database Integrity

The following checks were performed:

- Primary key uniqueness.
- Foreign key integrity.
- Required field constraints.
- Tank capacity validation.
- Valve state and opening percentage validation.
- Pipe connection validation.
- Sensor measurement category validation.
- Telemetry quality status validation.

Database schema constraints and application-level checks are used to maintain data integrity.

## 4. Anomaly Detection Validation

Four controlled anomaly scenarios were injected into the synthetic dataset.

| Anomaly Type | Equipment | Injected Value | Detection |
|---|---|---:|---|
| LEAK | PIPE-001 | 1.2 | Detected |
| BLOCKAGE | PIPE-002 | 4.0 | Detected |
| PUMP_DEGRADATION | PUMP-001 | 46.8 | Detected |
| SENSOR_FAULT | PUMP-002 | 9999.0 | Detected |

### Detection Evaluation

| Metric | Result |
|---|---:|
| True Positives | 4 |
| False Positives | 0 |
| False Negatives | 0 |
| True Negatives | 216 |
| Accuracy | 100% |
| Precision | 100% |
| Recall | 100% |
| F1 Score | 100% |

Note: These metrics are from a controlled synthetic dataset. They do not represent real-world industrial detection performance. The 216 records treated as normal are the remaining labelled equipment records in this evaluation.

## 5. Mass Balance Validation

| Facility | Pump Flow (LPM) | Valve Flow (LPM) | Imbalance | Result |
|---|---:|---:|---:|---|
| Hyderabad Water Plant | Incomplete | N/A | N/A | Sensor Data Incomplete |
| Karimnagar Water Plant | 666.50 | 669.50 | 0.45% | Balanced |
| Warangal Water Plant | 601.27 | 598.00 | 0.55% | Balanced |

Hyderabad is not classified as balanced because one pump sensor has invalid data.

## 6. Export Validation

All 13 database tables were exported into CSV and JSON formats.

| Export Check | Result |
|---|---|
| CSV files | 13 |
| JSON files | 13 |
| Total export files | 26 |
| SHA-256 checksum report | Generated |
| Export errors | None observed |

OperatingMode currently contains zero records.

## 7. Reproducibility

A SHA-256 checksum script was executed on all 26 exported files.

The checksum report is stored at:

`docs/reproducibility_checksums.json`

This records the current export file fingerprints. A complete two-run regeneration comparison has not yet been performed.

## 8. Known Limitations

- Dataset is synthetic and uses a fixed seed.
- The system is a monitoring demonstration, not a hydraulic engineering simulator.
- Hyderabad mass balance cannot be confirmed because of incomplete sensor data.
- Anomaly evaluation uses controlled injected scenarios.
- Some equipment relationships require application-level validation.
- OperatingMode currently has no seeded records.
- Full two-run regeneration and checksum comparison remain pending.

## 9. Conclusion

The current implementation successfully creates and validates a synthetic water infrastructure dataset, monitors telemetry, detects four controlled anomaly types, evaluates mass balance where sensor coverage is sufficient, and exports database records in CSV and JSON formats.

Further work is required for complete reproducibility testing and advanced operating-mode simulation.
