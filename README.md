
# YottaFlex AI – Water Infrastructure Monitoring System

AI-powered monitoring and anomaly detection for industrial water distribution networks.

## 1. Project Overview

YottaFlex AI is a Python-based prototype designed to monitor industrial water infrastructure across multiple facilities.

The system uses synthetic telemetry data, database-driven equipment information, anomaly detection rules, and mass balance calculations to identify potential operational issues.

It provides an interactive Streamlit dashboard to visualize network topology, monitor sensor readings, review detected anomalies, and evaluate facility health.

## 2. Key Features

- Multi-facility infrastructure monitoring
- Equipment and pipe network topology visualization
- Sensor telemetry monitoring and trend charts
- Rule-based anomaly detection
- Event history tracking
- Pump inflow and valve outflow mass balance analysis
- Sensor data quality validation
- Detection performance evaluation
- SQLite database integration
- Interactive Streamlit dashboard

## 3. Facilities

The prototype contains three synthetic facilities:

- Hyderabad Water Plant
- Karimnagar Water Plant
- Warangal Water Plant

The dataset includes:

- 20 pumps
- 30 tanks
- 60 valves
- 110 network nodes
- 110 pipe connections
- 220 sensors
- 100,000 telemetry readings

## 4. Anomaly Detection

The system detects four types of anomalies:

| Anomaly | Detection Rule |
|---|---|
| Leak | Pipe pressure below 1.5 BAR |
| Blockage | Pipe pressure above 3.5 BAR |
| Pump Degradation | Pump flow below 50% of rated capacity |
| Sensor Fault | Sensor reports BAD quality |

The detection engine analyzes the latest 30 telemetry readings for each sensor.

## 5. Mass Balance Monitoring

The system compares total pump inflow with total valve outflow.

Imbalance is calculated as:

Imbalance (%) = (Absolute difference between pump inflow and valve outflow / Valve outflow) × 100

A deviation above 3% is classified as an imbalance.

The system also checks sensor quality and data completeness before evaluating mass balance.

## 6. Technology Stack

- Python
- SQLite
- Pandas
- NumPy
- NetworkX
- Plotly
- Streamlit

## 7. Project Structure

```text
YottaFlex-AI/
│
├── database/
│   ├── schema.sql
│   └── yottaflex.db
│
├── data/
│
├── docs/
│
├── src/
│   ├── db.py
│   ├── seed_data.py
│   ├── generate_telemetry.py
│   ├── inject_anomalies.py
│   ├── detection_engine.py
│   ├── evaluate_detection.py
│   ├── validate_telemetry.py
│   ├── validate_anomalies.py
│   ├── mass_balance.py
│   ├── check_flow_balance.py
│   ├── calibrate_valve_flow.py
│   └── dashboard.py
│
├── main.py
├── requirements.txt
└── README.md
```

## 8. Installation and Setup

### Prerequisites

- Python 3.10 or higher
- pip

### Step 1: Clone the repository

```bash
git clone https://github.com/MUDRAKOLAMANISH/YottaFlex-AI.git
cd YottaFlex-AI
```

### Step 2: Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Launch the dashboard

```bash
streamlit run src/dashboard.py
```

Open the local URL displayed in the terminal.

## 9. Validation Results

The synthetic test dataset produced the following anomaly detection results:

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

These metrics represent performance on the controlled synthetic test dataset and do not establish real-world detection accuracy.

## 10. Mass Balance Results

| Facility | Imbalance | Result |
|---|---:|---|
| Hyderabad | N/A | Sensor Data Incomplete |
| Karimnagar | 0.45% | Balanced |
| Warangal | 0.55% | Balanced |

Hyderabad's mass balance is not evaluated because one pump sensor has invalid quality data.

## 11. Dashboard Modules

1. System Overview
2. Facility Overview
3. Network Topology
4. Telemetry Monitoring
5. Anomaly Monitoring
6. Mass Balance Monitoring
7. Facility Health Status
8. Event History

## 12. Assumptions and Limitations

- The dataset is synthetic and generated for prototype evaluation.
- Network topology represents a simplified network structure.
- Anomaly detection uses predefined threshold-based rules.
- Mass balance is an operational comparison, not a complete hydraulic simulation.
- Sensor coverage and data quality affect the reliability of mass balance results.
- The prototype has not been validated against real industrial water infrastructure.

## 13. Future Enhancements

- Real-time sensor integration
- Advanced anomaly detection using machine learning
- Predictive maintenance
- More detailed hydraulic simulation
- Automated alerts and notifications
- Historical analytics and reporting

## 14. Author

**Manish Mudrakola**

B.Tech – Computer Science and Information Technology

GitHub: [MUDRAKOLAMANISH](https://github.com/MUDRAKOLAMANISH)

---

*YottaFlex AI – Intelligent Industrial Water Infrastructure Monitoring*
## 📸 Dashboard Screenshots

### 1. Dashboard Overview
![Dashboard Overview](screenshots/dashboard-overview.png)

### 2. Anomaly Monitoring
![Anomaly Monitoring](screenshots/anomaly-monitoring.png)

### 3. Mass Balance Monitoring
![Mass Balance Monitoring](screenshots/mass-balance.png)