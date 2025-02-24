import sqlite3
from app.config import settings

def get_db_connection():
    connection = sqlite3.connect(settings.sqlite_db_path)
    connection.row_factory = sqlite3.Row
    return connection

db = get_db_connection()