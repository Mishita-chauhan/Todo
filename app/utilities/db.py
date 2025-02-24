import sqlite3
def get_db_connection():
    connection = sqlite3.connect(settings.sqlite_db_path)
    connection.row_factory = sqlite3.Row  # Enables dictionary-like row access
    return connection

db = get_db_connection()