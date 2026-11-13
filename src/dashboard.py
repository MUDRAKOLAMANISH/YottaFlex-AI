
import sqlite3
from pathlib import Path
from statistics import median

import pandas as pd
import streamlit as st
import networkx as nx
import plotly.graph_objects as go


# ---------------- PROJECT CONFIGURATION ----------------

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "yottaflex.db"

st.set_page_config(
    page_title="YottaFlex AI | Water Intelligence",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------- CUSTOM CSS ----------------

st.markdown("""

<style>
/* MAIN BACKGROUND */
.stApp {
    background: linear-gradient(135deg, #071426, #10243d);
    color: #f1f5f9;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: #091629;
    border-right: 1px solid #29415e;
}

[data-testid="stSidebar"] * {
    color: #e8f1fc !important;
}

[data-testid="stHeader"] {
    background: transparent;
}

/* GENERAL TEXT */
.stMarkdown p,
.stMarkdown li,
.stMarkdown span {
    color: #e5edf8;
}

.stCaption,
[data-testid="stCaptionContainer"] {
    color: #bdcce0 !important;
}

label,
[data-testid="stWidgetLabel"] p {
    color: #f1f5f9 !important;
    font-weight: 600 !important;
}

/* HEADINGS */
.main-title {
    font-size: 36px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.8px;
}

.subtitle {
    color: #c2d2e6;
    font-size: 16px;
    margin-bottom: 25px;
}

.section-title {
    font-size: 23px;
    font-weight: 750;
    color: #ffffff;
    margin-top: 22px;
    margin-bottom: 14px;
}

/* BRAND */
.brand {
    color: #56c8ff;
    font-size: 25px;
    font-weight: 850;
}

/* KPI CARDS */
.metric-card {
    background: linear-gradient(145deg, #193553, #102943);
    border: 1px solid #3b5c7d;
    padding: 23px;
    border-radius: 15px;
    min-height: 125px;
}

.metric-label {
    color: #c6d7eb;
    font-size: 14px;
    font-weight: 700;
}

.metric-value {
    color: #ffffff;
    font-size: 32px;
    font-weight: 850;
    margin-top: 10px;
}

/* STREAMLIT METRICS */
[data-testid="stMetricLabel"] {
    color: #cbd9ea !important;
    font-size: 14px !important;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 800 !important;
}

[data-testid="stMetricDelta"] {
    color: #d6e6f7 !important;
}

/* INPUTS AND SELECT BOXES */
[data-baseweb="select"] > div {
    background-color: #172e49;
    border-color: #496582;
    color: #ffffff;
}

[data-baseweb="select"] * {
    color: #ffffff !important;
}

input, textarea {
    color: #ffffff !important;
}

/* DATA TABLES */
[data-testid="stDataFrame"] {
    border: 1px solid #3b5877;
    border-radius: 10px;
}

[data-testid="stDataFrame"] * {
    font-size: 14px;
}

/* ALERTS */
.stAlert {
    border-radius: 11px;
}

/* DIVIDERS */
hr {
    border-color: #35516f;
}

/* BUTTONS */
.stButton button {
    background: #1769aa;
    color: #ffffff;
    border: 1px solid #438ac3;
    border-radius: 9px;
    font-weight: 700;
}

.stButton button:hover {
    background: #2185ce;
    color: #ffffff;
}
/* SIDEBAR NAVIGATION */

.nav-menu {
    display: flex;
    flex-direction: column;
    gap: 9px;
}

.nav-menu a {
    display: block;
    padding: 12px;
    color: #ffffff !important;
    background: #142b45;
    border: 1px solid #355474;
    border-radius: 9px;
    text-decoration: none !important;
    font-size: 14px;
    font-weight: 700;
}

.nav-menu a:hover {
    background: #20517b;
    border-color: #56c8ff;
}

/* FOOTER */
footer {
    visibility: hidden;
}
</style>

""", unsafe_allow_html=True)


# ---------------- DATABASE CONNECTION ----------------

def get_connection():
    connection = sqlite3.connect(DB_PATH)
    return connection


# ---------------- FACILITY DATA ----------------

def load_facilities():

    with get_connection() as connection:

        return pd.read_sql_query("""
            SELECT facility_id, facility_name
            FROM Facility
            ORDER BY facility_id
        """, connection)


# ---------------- ALARM DATA ----------------

def load_alarms():

    with get_connection() as connection:

        return pd.read_sql_query("""
            SELECT *
            FROM Alarm
            ORDER BY alarm_id
        """, connection)
    
def load_event_history():
    with get_connection() as connection:
        data = pd.read_sql_query("""
            SELECT
                event_id,
                facility_id,
                simulation_id,
                equipment_type,
                equipment_id,
                event_type,
                previous_state,
                new_state,
                event_description,
                event_timestamp
            FROM EventHistory
            ORDER BY event_timestamp DESC
            LIMIT 100
        """, connection)

    return data



# ---------------- NETWORK TOPOLOGY DATA ----------------

def load_network_data(facility_id):

    with get_connection() as connection:

        nodes = pd.read_sql_query("""
            SELECT node_id, equipment_type, equipment_id
            FROM NetworkNode
            WHERE facility_id = ?
        """, connection, params=(facility_id,))

        pipes = pd.read_sql_query("""
            SELECT pipe_id, source_node_id,
                   target_node_id, status
            FROM Pipe
            WHERE facility_id = ?
        """, connection, params=(facility_id,))

    return nodes, pipes


# ---------------- TELEMETRY DATA ----------------

def load_sensors(facility_id):

    with get_connection() as connection:

        return pd.read_sql_query("""
            SELECT sensor_id, sensor_name,
                   sensor_type, unit
            FROM Sensor
            WHERE facility_id = ?
            ORDER BY sensor_type, sensor_id
        """, connection, params=(facility_id,))


def load_sensor_telemetry(sensor_id):

    with get_connection() as connection:

        data = pd.read_sql_query("""
            SELECT recorded_at, reading_value, quality_status
            FROM Telemetry
            WHERE sensor_id = ?
            ORDER BY recorded_at DESC
            LIMIT 100
        """, connection, params=(sensor_id,))

    return data.sort_values("recorded_at")


# ---------------- MASS BALANCE CALCULATION ----------------

def load_mass_balance():

    results = []

    with get_connection() as connection:

        facilities_data = connection.execute("""
            SELECT facility_id, facility_name
            FROM Facility
            ORDER BY facility_id
        """).fetchall()

        for facility_id, facility_name in facilities_data:

            flows = {}

            for equipment_type in ["PUMP", "VALVE"]:

                sensors = connection.execute("""
                    SELECT sensor_id
                    FROM Sensor
                    WHERE facility_id = ?
                      AND equipment_type = ?
                      AND sensor_type = 'FLOW'
                """, (facility_id, equipment_type)).fetchall()

                total_flow = 0.0
                valid_count = 0
                invalid_count = 0

                for (sensor_id,) in sensors:

                    readings = connection.execute("""
                        SELECT reading_value, quality_status
                        FROM Telemetry
                        WHERE sensor_id = ?
                        ORDER BY recorded_at DESC
                        LIMIT 30
                    """, (sensor_id,)).fetchall()

                    if len(readings) < 30 or any(
                        row[1] != "GOOD" for row in readings
                    ):
                        invalid_count += 1
                        continue

                    values = [row[0] for row in readings]

                    total_flow += median(values)
                    valid_count += 1

                flows[equipment_type] = {
                    "total": total_flow,
                    "valid": valid_count,
                    "total_sensors": len(sensors),
                    "invalid": invalid_count
                }

            pump = flows["PUMP"]
            valve = flows["VALVE"]

            facility_result = {
                "Facility": facility_name,
                "Pump Inflow (LPM)": "N/A",
                "Valve Outflow (LPM)": "N/A",
                "Imbalance (%)": "N/A",
                "Valid Pump Sensors": (
                    f'{pump["valid"]}/{pump["total_sensors"]}'
                ),
                "Valid Valve Sensors": (
                    f'{valve["valid"]}/{valve["total_sensors"]}'
                ),
                "Status": ""
            }

            if (
                pump["valid"] != pump["total_sensors"]
                or valve["valid"] != valve["total_sensors"]
            ):
                facility_result["Status"] = "SENSOR DATA INCOMPLETE"

            elif (
                pump["total_sensors"] == 0
                or valve["total_sensors"] == 0
            ):
                facility_result["Status"] = "INSUFFICIENT FLOW DATA"

            elif valve["total"] == 0:
                facility_result["Status"] = "INSUFFICIENT FLOW DATA"

            else:

                difference = pump["total"] - valve["total"]

                imbalance = (
                    abs(difference) / valve["total"]
                ) * 100

                facility_result["Pump Inflow (LPM)"] = round(
                    pump["total"], 2
                )

                facility_result["Valve Outflow (LPM)"] = round(
                    valve["total"], 2
                )

                facility_result["Imbalance (%)"] = round(
                    imbalance, 2
                )

                if imbalance > 3.0:
                    facility_result["Status"] = "IMBALANCE DETECTED"
                else:
                    facility_result["Status"] = "BALANCED"

            results.append(facility_result)

    return pd.DataFrame(results)


# ---------------- DATABASE VALIDATION ----------------

if not DB_PATH.exists():

    st.error("Database not found. Please initialize the database first.")
    st.stop()


# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.markdown(
        '<div class="brand">💧 YottaFlex AI</div>',
        unsafe_allow_html=True
    )

    st.caption("WATER INTELLIGENCE PLATFORM")

    st.divider()



    st.markdown("""
<div class="nav-menu">
    <a href="#dashboard">🏠 Dashboard</a>
    <a href="#facilities">🏭 Facilities</a>
    <a href="#anomaly-monitoring">⚠️ Anomaly Monitoring</a>
    <a href="#mass-balance">⚖️ Mass Balance</a>
    <a href="#network-overview">🌐 Network Overview</a>
    <a href="#telemetry-monitoring">📈 Telemetry Monitoring</a>
</div>
""", unsafe_allow_html=True)

    st.divider()

    st.caption("SYSTEM STATUS")

    st.divider()

    st.caption("SYSTEM STATUS")
    st.markdown("""
<div style="
    background-color: #123c32;
    border: 1px solid #20c997;
    border-radius: 9px;
    padding: 10px;
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
">
    🟢 DATABASE CONNECTED
</div>
""", unsafe_allow_html=True)
    st.caption("Version 1.0 | Prototype")


# ---------------- MAIN DASHBOARD ----------------
st.markdown('<div id="dashboard"></div>', unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">Water Infrastructure Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-powered monitoring and anomaly detection for industrial water systems'
    '</div>',
    unsafe_allow_html=True
)


# ---------------- LOAD DATA ----------------

try:

    facilities = load_facilities()
    alarms = load_alarms()
    mass_balance_data = load_mass_balance()

except sqlite3.Error as error:

    st.error(f"Database error: {error}")
    st.stop()
st.markdown("""
<div style="
    background: linear-gradient(110deg, #153653, #172b45);
    border: 1px solid #3b6488;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 20px;
">
    <h3 style="color:#ffffff; margin:0 0 10px 0;">
        Project Overview
    </h3>
    <p style="color:#e0edfa; font-size:15px; line-height:1.7; margin:0;">
        YottaFlex AI monitors industrial water infrastructure across
        multiple facilities. It analyzes sensor telemetry, identifies
        abnormal equipment behavior, evaluates pump-to-valve flow balance,
        and maintains an event history to support operational monitoring.
    </p>
</div>
""", unsafe_allow_html=True)    


# ---------------- SYSTEM OVERVIEW ----------------

st.markdown(
    '<div class="section-title">System Overview</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

metrics = [
    (col1, "TOTAL FACILITIES", len(facilities)),
    (col2, "DETECTED ANOMALIES", len(alarms)),
    (col3, "DATABASE STATUS", "CONNECTED")
]

for column, label, value in metrics:

    with column:

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)


# ---------------- FACILITY OVERVIEW ----------------
st.markdown('<div id="facilities"></div>', unsafe_allow_html=True)

st.divider()

st.markdown(
    '<div class="section-title">🏭 Facility Overview</div>',
    unsafe_allow_html=True
)

st.dataframe(
    facilities,
    width="stretch",
    hide_index=True
)


# ---------------- NETWORK TOPOLOGY ----------------
st.markdown('<div id="network-overview"></div>', unsafe_allow_html=True)

st.divider()

st.markdown(
    '<div class="section-title">🌐 Network Topology Overview</div>',
    unsafe_allow_html=True
)

if not facilities.empty:

    selected_facility = st.selectbox(
        "Select Facility",
        facilities["facility_name"].tolist(),
        key="network_facility"
    )

    selected_facility_id = facilities.loc[
        facilities["facility_name"] == selected_facility,
        "facility_id"
    ].iloc[0]

    nodes, pipes = load_network_data(selected_facility_id)

    if not nodes.empty:

        graph = nx.Graph()

        for _, node in nodes.iterrows():

            graph.add_node(
                node["node_id"],
                equipment_id=node["equipment_id"],
                equipment_type=node["equipment_type"]
            )

        for _, pipe in pipes.iterrows():

            if (
                pipe["source_node_id"] in graph
                and pipe["target_node_id"] in graph
            ):

                graph.add_edge(
                    pipe["source_node_id"],
                    pipe["target_node_id"],
                    status=pipe["status"]
                )

        positions = nx.spring_layout(
            graph,
            seed=42,
            k=0.8
        )

        edge_x = []
        edge_y = []

        for source, target in graph.edges():

            x0, y0 = positions[source]
            x1, y1 = positions[target]

            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(width=1.5, color="#54708f"),
            hoverinfo="none",
            name="Pipes"
        )

        node_x = []
        node_y = []
        node_labels = []
        node_types = []
        node_colors = []

        color_map = {
            "PUMP": "#36a2eb",
            "TANK": "#2ecc71",
            "VALVE": "#f5a623"
        }

        for node_id in graph.nodes():

            x, y = positions[node_id]

            node_data = graph.nodes[node_id]

            equipment_id = node_data["equipment_id"]
            equipment_type = node_data["equipment_type"]

            node_x.append(x)
            node_y.append(y)
            node_labels.append(equipment_id)
            node_types.append(equipment_type)

            node_colors.append(
                color_map.get(equipment_type, "#ffffff")
            )

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=node_labels,
            textposition="top center",
            customdata=node_types,
            marker=dict(
                size=13,
                color=node_colors,
                line=dict(width=1, color="#ffffff")
            ),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Equipment Type: %{customdata}"
                "<extra></extra>"
            ),
            name="Equipment"
        )

        fig = go.Figure(
            data=[edge_trace, node_trace]
        )

        fig.update_layout(
            title=f"{selected_facility} - Network Connections",
            showlegend=False,
            height=600,
            paper_bgcolor="#101f35",
            plot_bgcolor="#101f35",
            font=dict(color="white"),
            xaxis=dict(visible=False, showgrid=False),
            yaxis=dict(visible=False, showgrid=False),
            margin=dict(l=20, r=20, t=50, b=20)
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

        st.caption(
            "🔵 Pumps     🟢 Tanks     🟠 Valves     "
            "Lines represent connecting pipes."
        )

        st.write(f"Total Equipment Nodes: **{len(nodes)}**")
        st.write(f"Total Pipe Connections: **{len(pipes)}**")

    else:

        st.warning("No network topology data found for this facility.")


# ---------------- TELEMETRY MONITORING ----------------
st.markdown('<div id="telemetry-monitoring"></div>', unsafe_allow_html=True)

st.divider()

st.markdown(
    '<div class="section-title">📈 Telemetry Monitoring</div>',
    unsafe_allow_html=True
)

if not facilities.empty:

    telemetry_facility = st.selectbox(
        "Select Facility for Telemetry",
        facilities["facility_name"].tolist(),
        key="telemetry_facility"
    )

    telemetry_facility_id = facilities.loc[
        facilities["facility_name"] == telemetry_facility,
        "facility_id"
    ].iloc[0]

    sensors = load_sensors(telemetry_facility_id)

    if not sensors.empty:

        sensor_options = {
            f'{row["sensor_name"]} ({row["sensor_type"]})':
            row["sensor_id"]
            for _, row in sensors.iterrows()
        }

        selected_sensor = st.selectbox(
            "Select Sensor",
            list(sensor_options.keys()),
            key="telemetry_sensor"
        )

        selected_sensor_id = sensor_options[selected_sensor]

        telemetry = load_sensor_telemetry(selected_sensor_id)

        if not telemetry.empty:

            latest_reading = telemetry.iloc[-1]

            selected_unit = sensors.loc[
                sensors["sensor_id"] == selected_sensor_id,
                "unit"
            ].iloc[0]

            metric_col1, metric_col2 = st.columns(2)

            with metric_col1:

                st.metric(
                    "Latest Reading",
                    f'{latest_reading["reading_value"]} {selected_unit}'
                )

            with metric_col2:

                st.metric(
                    "Sensor Quality",
                    str(latest_reading["quality_status"])
                )

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=telemetry["recorded_at"],
                    y=telemetry["reading_value"],
                    mode="lines+markers",
                    name="Sensor Reading",
                    line=dict(width=2),
                    marker=dict(size=5)
                )
            )

            fig.update_layout(
                title=f"Telemetry Trend - {selected_sensor}",
                xaxis_title="Recorded Time",
                yaxis_title=f"Sensor Reading ({selected_unit})",
                height=400,
                paper_bgcolor="#101f35",
                plot_bgcolor="#101f35",
                font=dict(color="white"),
                margin=dict(l=20, r=20, t=50, b=20)
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

            st.caption(
                f"Showing {len(telemetry)} recent readings. "
                "Sensor quality is displayed separately."
            )

            st.dataframe(
                telemetry.tail(10),
                width="stretch",
                hide_index=True
            )

        else:

            st.warning("No telemetry readings found for this sensor.")

    else:

        st.warning("No sensors found for this facility.")


# ---------------- ANOMALY MONITORING ----------------
st.markdown('<div id="anomaly-monitoring"></div>', unsafe_allow_html=True)

st.divider()

st.markdown(
    '<div class="section-title">⚠️ Anomaly Monitoring</div>',
    unsafe_allow_html=True
)

alarm_col1, alarm_col2 = st.columns(2)

with alarm_col1:

    st.metric("Total Detected Alarms", len(alarms))

with alarm_col2:

    if "severity" in alarms.columns:

        critical_count = (
            alarms["severity"].astype(str).str.upper() == "CRITICAL"
        ).sum()

        st.metric("Critical Alarms", int(critical_count))

    else:

        st.metric("Critical Alarms", 0)


if not alarms.empty:

    display_columns = [
        col for col in [
            "alarm_id",
            "equipment_id",
            "alarm_type",
            "severity",
            "status"
        ]
        if col in alarms.columns
    ]

    st.dataframe(
        alarms[display_columns],
        width="stretch",
        hide_index=True,
        column_config={
            "alarm_id": "Alarm ID",
            "equipment_id": "Equipment",
            "alarm_type": "Anomaly Type",
            "severity": "Severity",
            "status": "Status"
        }
    )

else:

    st.info("No anomaly records found.")


# ---------------- MASS BALANCE MONITORING ----------------
st.markdown('<div id="mass-balance"></div>', unsafe_allow_html=True)

st.divider()

st.markdown(
    '<div class="section-title">⚖️ Mass Balance Monitoring</div>',
    unsafe_allow_html=True
)

display_mass_balance = mass_balance_data.copy()

for column in [
    "Pump Inflow (LPM)",
    "Valve Outflow (LPM)",
    "Imbalance (%)"
]:

    display_mass_balance[column] = display_mass_balance[column].apply(
        lambda value: "N/A" if pd.isna(value) else str(value)
    )

st.dataframe(
    display_mass_balance,
    width="stretch",
    hide_index=True,
    column_config={
        "Facility": "Facility",
        "Pump Inflow (LPM)": "Pump Inflow (LPM)",
        "Valve Outflow (LPM)": "Valve Outflow (LPM)",
        "Imbalance (%)": "Imbalance (%)",
        "Valid Pump Sensors": "Valid Pump Sensors",
        "Valid Valve Sensors": "Valid Valve Sensors",
        "Status": "Facility Status"
    }
)


# ---------------- FACILITY STATUS SUMMARY ----------------

# ==============================
# EVENT HISTORY
# ==============================
st.markdown('<div id="event-history"></div>', unsafe_allow_html=True)

st.markdown("---")
st.subheader("📜 Event History")

event_data = load_event_history()

if not event_data.empty:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Events", len(event_data))

    with col2:
        st.metric("Facilities Affected", event_data["facility_id"].nunique())

    with col3:
        st.metric("Equipment Involved", event_data["equipment_id"].nunique())

    st.dataframe(
        event_data,
        width="stretch",
        hide_index=True
    )
else:
    st.info("No event history available.")


st.markdown(
    '<div class="section-title">Facility Health Status</div>',
    unsafe_allow_html=True
)

for _, row in mass_balance_data.iterrows():

    if row["Status"] == "BALANCED":

        st.success(
            f'{row["Facility"]}: BALANCED '
            f'({row["Imbalance (%)"]}% deviation)'
        )

    elif row["Status"] == "SENSOR DATA INCOMPLETE":

        st.warning(
            f'{row["Facility"]}: SENSOR DATA INCOMPLETE '
            '— Mass balance cannot be reliably evaluated.'
        )

    else:

        st.error(
            f'{row["Facility"]}: {row["Status"]}'
        )


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "YottaFlex AI | Intelligent Industrial Water Infrastructure Monitoring"
)
