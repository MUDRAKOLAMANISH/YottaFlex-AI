
import sqlite3
from db import get_connection

connection = get_connection()

try:
    connection.execute("BEGIN")

    # Temporary facility for testing
    connection.execute("""
        INSERT INTO Facility
        VALUES ('FAC-TEST', 'Test Facility', 'Hyderabad')
    """)

    # This tank is invalid: 1200 liters in a 1000-liter tank
    connection.execute("""
        INSERT INTO Tank (
            tank_id,
            facility_id,
            tank_name,
            capacity_liters,
            current_level_liters,
            status
        )
        VALUES (
            'TANK-TEST',
            'FAC-TEST',
            'Test Tank',
            1000,
            1200,
            'ACTIVE'
        )
    """)

    print("ERROR: Invalid tank data was accepted!")

except sqlite3.IntegrityError as error:
    print("SUCCESS: Invalid tank data rejected!")
    print("Reason:", error)

finally:
    connection.rollback()
    connection.close()
