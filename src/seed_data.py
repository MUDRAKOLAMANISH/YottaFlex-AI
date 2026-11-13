
from db import get_connection

def create_facilities():
    connection = get_connection()

    facilities = [
        ("FAC-001", "Hyderabad Water Plant", "Hyderabad"),
        ("FAC-002", "Karimnagar Water Plant", "Karimnagar"),
        ("FAC-003", "Warangal Water Plant", "Warangal")
    ]

    connection.executemany("""
        INSERT OR IGNORE INTO Facility (
            facility_id,
            facility_name,
            location
        )
        VALUES (?, ?, ?)
    """, facilities)

    connection.commit()
    connection.close()

    print("3 facilities created successfully!")



def create_pumps():
    connection = get_connection()

    pumps = [
        (f"PUMP-{i:03d}", facility, f"Pump {i}", capacity, "ACTIVE")
        for i, (facility, capacity) in enumerate([
            ("FAC-001", 120),
            ("FAC-001", 150),
            ("FAC-001", 180),
            ("FAC-001", 100),
            ("FAC-001", 160),
            ("FAC-001", 140),
            ("FAC-001", 200),
            ("FAC-002", 130),
            ("FAC-002", 170),
            ("FAC-002", 110),
            ("FAC-002", 190),
            ("FAC-002", 150),
            ("FAC-002", 180),
            ("FAC-002", 100),
            ("FAC-003", 140),
            ("FAC-003", 160),
            ("FAC-003", 120),
            ("FAC-003", 200),
            ("FAC-003", 170),
            ("FAC-003", 130)
        ], start=1)
    ]

    connection.executemany("""
        INSERT OR IGNORE INTO Pump (
            pump_id,
            facility_id,
            pump_name,
            capacity_lpm,
            status
        )
        VALUES (?, ?, ?, ?, ?)
    """, pumps)

    connection.commit()
    connection.close()

    print("20 pumps created successfully!")

def create_tanks():
    connection = get_connection()

    tanks = []

    for i in range(1, 31):
        if i <= 10:
            facility = "FAC-001"
        elif i <= 20:
            facility = "FAC-002"
        else:
            facility = "FAC-003"

        capacity = 5000 + (i * 100)
        current_level = capacity * 0.60

        tanks.append((
            f"TANK-{i:03d}",
            facility,
            f"Storage Tank {i}",
            capacity,
            current_level,
            "ACTIVE"
        ))

    connection.executemany("""
        INSERT OR IGNORE INTO Tank (
            tank_id,
            facility_id,
            tank_name,
            capacity_liters,
            current_level_liters,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, tanks)

    connection.commit()
    connection.close()

    print("30 tanks created successfully!")

def create_valves():
    connection = get_connection()

    valves = []

    states = ["OPEN", "CLOSED", "PARTIALLY_OPEN"]

    for i in range(1, 61):
        if i <= 20:
            facility = "FAC-001"
        elif i <= 40:
            facility = "FAC-002"
        else:
            facility = "FAC-003"

        state = states[(i - 1) % 3]

        opening = {
            "OPEN": 100,
            "CLOSED": 0,
            "PARTIALLY_OPEN": 50
        }[state]

        valves.append((
            f"VALVE-{i:03d}",
            facility,
            f"Control Valve {i}",
            state,
            opening
        ))

    connection.executemany("""
        INSERT OR IGNORE INTO Valve (
            valve_id,
            facility_id,
            valve_name,
            state,
            opening_percentage
        )
        VALUES (?, ?, ?, ?, ?)
    """, valves)

    connection.commit()
    connection.close()

    print("60 valves created successfully!")

def create_network_nodes():
    connection = get_connection()

    nodes = []

    equipment_tables = [
        ("Pump", "PUMP", "pump_id"),
        ("Tank", "TANK", "tank_id"),
        ("Valve", "VALVE", "valve_id")
    ]

    for table, equipment_type, id_column in equipment_tables:
        records = connection.execute(
            f"SELECT {id_column}, facility_id FROM {table}"
        ).fetchall()

        for equipment_id, facility_id in records:
            node_id = f"NODE-{equipment_id}"

            nodes.append((
                node_id,
                facility_id,
                equipment_type,
                equipment_id
            ))

    connection.executemany("""
        INSERT OR IGNORE INTO NetworkNode (
            node_id,
            facility_id,
            equipment_type,
            equipment_id
        )
        VALUES (?, ?, ?, ?)
    """, nodes)

    connection.commit()
    connection.close()

    print(f"{len(nodes)} network nodes created successfully!")

def create_pipes():
    connection = get_connection()

    facilities = connection.execute("""
        SELECT facility_id
        FROM Facility
        ORDER BY facility_id
    """).fetchall()

    pipes = []
    pipe_number = 1

    for (facility_id,) in facilities:
        nodes = connection.execute("""
            SELECT node_id
            FROM NetworkNode
            WHERE facility_id = ?
            ORDER BY node_id
        """, (facility_id,)).fetchall()

        node_ids = [row[0] for row in nodes]

        for i in range(len(node_ids)):
            source = node_ids[i]
            target = node_ids[(i + 1) % len(node_ids)]

            pipes.append((
                f"PIPE-{pipe_number:03d}",
                facility_id,
                f"Connecting Pipe {pipe_number}",
                source,
                target,
                200.0,
                250.0,
                "ACTIVE"
            ))

            pipe_number += 1

    connection.executemany("""
        INSERT OR IGNORE INTO Pipe (
            pipe_id,
            facility_id,
            pipe_name,
            source_node_id,
            target_node_id,
            diameter_mm,
            max_flow_lpm,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, pipes)

    connection.commit()
    connection.close()

    print(f"{len(pipes)} pipes created successfully!")

def create_sensors():
    connection = get_connection()

    equipment_tables = [
        ("Pump", "PUMP", "pump_id", "FLOW"),
        ("Tank", "TANK", "tank_id", "LEVEL"),
        ("Valve", "VALVE", "valve_id", "FLOW"),
        ("Pipe", "PIPE", "pipe_id", "PRESSURE")
    ]

    sensors = []

    for table, equipment_type, id_column, sensor_type in equipment_tables:
        records = connection.execute(
            f"SELECT {id_column}, facility_id FROM {table}"
        ).fetchall()

        for equipment_id, facility_id in records:
            sensor_id = f"SNS-{equipment_id}"

            unit = {
                "FLOW": "LPM",
                "LEVEL": "LITERS",
                "PRESSURE": "BAR"
            }[sensor_type]

            sensors.append((
                sensor_id,
                facility_id,
                f"{sensor_type} Sensor for {equipment_id}",
                sensor_type,
                equipment_type,
                equipment_id,
                unit,
                "ACTIVE"
            ))

    connection.executemany("""
        INSERT OR IGNORE INTO Sensor (
            sensor_id,
            facility_id,
            sensor_name,
            sensor_type,
            equipment_type,
            equipment_id,
            unit,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, sensors)

    connection.commit()
    connection.close()

    print(f"{len(sensors)} sensors created successfully!")






if __name__ == "__main__":
    create_facilities()
    create_pumps()
    create_tanks()
    create_valves()
    create_network_nodes()
    create_pipes()
    create_sensors()