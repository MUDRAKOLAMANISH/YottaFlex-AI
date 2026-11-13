
# Assumptions and Limitations

## 1. Project Scope

YottaFlex AI is a prototype for industrial water infrastructure monitoring and anomaly detection.

The project uses a synthetic dataset to demonstrate equipment monitoring, telemetry analysis, anomaly detection, event tracking, and mass balance evaluation.

It is not a certified hydraulic simulation or a production-ready industrial control system.

## 2. Dataset Assumptions

- The dataset contains three synthetic water facilities.
- Equipment consists of pumps, tanks, and valves.
- Telemetry readings are generated programmatically.
- A fixed random seed (20261022) is used for reproducibility.
- The generated dataset contains 100,000 telemetry readings.
- Sensor values represent simulated operating conditions, not measurements from real facilities.

## 3. Network Topology Assumptions

- Network connections are represented using nodes and edges.
- Pumps, tanks, and valves are represented as equipment nodes.
- Pipes represent connections between equipment nodes.
- The prototype uses a simplified synthetic network topology.
- The network does not model detailed hydraulic properties such as pressure losses, elevation, or fluid dynamics.

## 4. Anomaly Detection Assumptions

The detection engine uses predefined threshold-based rules.

### Leak

A leak is flagged when pipe pressure falls below 1.5 BAR.

### Blockage

A blockage is flagged when pipe pressure exceeds 3.5 BAR.

### Pump Degradation

Pump degradation is flagged when measured pump flow falls below 50% of rated capacity.

### Sensor Fault

A sensor fault is flagged when sensor quality is marked BAD.

The detection engine evaluates the latest 30 readings for each sensor.

These thresholds are prototype assumptions and may require calibration using real operational data.

## 5. Mass Balance Assumptions

Mass balance compares total pump inflow with total valve outflow.

- The median of the latest 30 readings is used for each valid flow sensor.
- Sensors with insufficient readings or invalid quality are excluded.
- Complete valid sensor coverage is required before evaluating a facility.
- An imbalance above 3% is flagged.

The calculation is a simplified operational flow comparison. It does not account for storage changes, leakage locations, measurement uncertainty, or detailed hydraulic behavior.

## 6. Data Quality Limitations

- Missing or invalid sensor readings can prevent reliable facility evaluation.
- A sensor reporting BAD quality is not treated as valid flow data.
- Synthetic data cannot represent every real-world sensor failure.
- The system depends on accurate equipment and sensor mappings.

## 7. Evaluation Limitations

The current synthetic test produced:

- True Positives: 4
- False Positives: 0
- False Negatives: 0
- True Negatives: 216

The reported 100% accuracy, precision, recall, and F1 score apply only to this controlled test dataset.

They should not be interpreted as guaranteed real-world performance.

## 8. Technical Limitations

- SQLite is used as the prototype database.
- Detection is based on predefined rules rather than trained machine learning models.
- The dashboard currently reads stored telemetry rather than a live industrial sensor stream.
- The topology is a simplified graph representation.
- The prototype does not directly control pumps, valves, or other physical equipment.

## 9. Future Improvements

- Integration with real-time industrial sensors.
- Machine learning-based anomaly detection.
- Predictive equipment maintenance.
- Detailed hydraulic network simulation.
- More advanced sensor validation.
- Automated alarm notifications.
- Improved historical trend analysis.

## 10. Conclusion

YottaFlex AI demonstrates a reproducible prototype for monitoring synthetic industrial water networks.

Its main purpose is to demonstrate database design, telemetry processing, anomaly detection, event history, network visualization, and mass balance evaluation while clearly documenting the assumptions and limitations.
