# Source Manifest

## 1. Data Sources

This project uses synthetic data generated specifically for the YottaFlex AI water infrastructure simulation.

No external private, confidential, or real-world operational datasets were used.

## 2. Random Seed

- Random seed: 20261022
- Telemetry generation: Python and NumPy
- Total telemetry records: 100,000
- Facilities: 3
- Pumps: 20
- Tanks: 30
- Valves: 60
- Sensors: 220

## 3. Generation Scripts

| Script | Purpose |
|---|---|
| src/seed_data.py | Creates infrastructure master data |
| src/generate_telemetry.py | Generates synthetic telemetry |
| src/inject_anomalies.py | Injects controlled anomaly scenarios |
| src/create_pump_curves.py | Creates synthetic pump curve reference points |
| src/simulate_operating_mode.py | Simulates operating-mode changes |

## 4. Anomaly Rules

- Low pipe pressure: Leak
- High pipe pressure: Blockage
- Low pump flow: Pump degradation
- Invalid sensor reading: Sensor fault

## 5. Assumptions

Pump curve points are synthetic reference values, not manufacturer-certified curves.

Operating-mode flow estimates use a simplified linear capacity assumption, not a full hydraulic simulation.

## 6. Reproducibility

The telemetry generator uses a fixed random seed of 20261022.

Export checksums are recorded in:

`docs/reproducibility_checksums.json`

The SQL database export is available at:

`exports/yottaflex_seed.sql`