
import sqlite3
from pathlib import Path

# Find the project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database and schema file locations
DB_PATH = BASE_DIR / "database" / "yottaflex.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"


def get_connection():
    """Create a connection to the SQLite database."""
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    """Create all database tables using schema.sql."""
    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with get_connection() as connection:
        connection.executescript(schema)

    print("Database initialized successfully!")


if __name__ == "__main__":
    initialize_database()
