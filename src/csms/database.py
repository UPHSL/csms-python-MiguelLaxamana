import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent / "csms.db"


def get_connection(database_path=DATABASE_PATH):
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(database_path=DATABASE_PATH):
    connection = get_connection(database_path)

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS residents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                address TEXT NOT NULL,
                contact_number TEXT NOT NULL,
                email TEXT NOT NULL,
                status TEXT NOT NULL
            )
            """
        )

        connection.commit()
    finally:
        connection.close()