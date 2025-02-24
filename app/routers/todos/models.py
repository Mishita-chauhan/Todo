from datetime import datetime
from pydantic import BaseModel
from app.utilities.db import db

class Todo(BaseModel):
    title: str
    completed: bool = False

class TodoId(BaseModel):
    id: int

class TodoRecord(TodoId, Todo):
    created_date: datetime
    updated_date: datetime

class NotFoundException(BaseModel):
    detail: str = "Not Found"

# Create the todos table if it doesn't exist
def initialize_db():
    with db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

initialize_db()
