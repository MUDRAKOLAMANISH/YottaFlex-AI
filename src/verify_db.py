
import sqlite3

connection = sqlite3.connect("database/yottaflex.db")

tables = connection.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    AND name NOT LIKE 'sqlite_%'
    ORDER BY name
""").fetchall()

print("\nDatabase Tables:")
for table in tables:
    print("-", table[0])

print("\nTotal tables:", len(tables))

connection.close()
