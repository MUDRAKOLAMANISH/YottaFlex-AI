
import sqlite3
from db import get_connection

connection = get_connection()

try:
    connection.execute("""
        INSERT INTO Pump (
            pump_id,
            facility_id,
            pump_name,
            capacity_lpm,
            status
        )
        VALUES (
            'PUMP-TEST',
            'FAC-999',
            'Test Pump',
            100,
            'ACTIVE'
        )
    """)

    connection.commit()
    print("ERROR: Invalid facility was accepted!")

except sqlite3.IntegrityError as error:
    print("SUCCESS: Invalid relationship rejected!")
    print("Reason:", error)

finally:
    connection.close()
