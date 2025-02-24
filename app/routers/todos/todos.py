from datetime import datetime
from fastapi import APIRouter, HTTPException, Path
from app.utilities.db import get_db_connection
from .models import NotFoundException, Todo, TodoId, TodoRecord

router = APIRouter()

@router.post("", response_model=TodoId)
async def create_todo(payload: Todo) -> TodoId:
    """
    Create a new Todo
    """
    now = datetime.utcnow()
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO todos (title, completed, created_date, updated_date) VALUES (?, ?, ?, ?)",
        (payload.title, payload.completed, now, now),
    )
    db.commit()
    todo_id = cursor.lastrowid
    db.close()

    return TodoId(id=todo_id)

@router.get("/{id}", response_model=TodoRecord, responses={404: {"description": "Not Found", "model": NotFoundException}})
async def get_todo(id: int = Path(description="Todo ID")) -> TodoRecord:
    """
    Get a Todo
    """
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM todos WHERE id = ?", (id,))
    row = cursor.fetchone()
    db.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Not Found")

    return TodoRecord(
        id=row["id"],
        title=row["title"],
        completed=row["completed"],
        created_date=row["created_date"],
        updated_date=row["updated_date"],
    )

@router.get("", response_model=list[TodoRecord])
async def get_todos() -> list[TodoRecord]:
    """
    Get Todos
    """
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM todos")
    rows = cursor.fetchall()
    db.close()

    return [
        TodoRecord(
            id=row["id"],
            title=row["title"],
            completed=row["completed"],
            created_date=row["created_date"],
            updated_date=row["updated_date"],
        )
        for row in rows
    ]

@router.put("/{id}", response_model=TodoId, responses={404: {"description": "Not Found", "model": NotFoundException}})
async def update_todo(payload: Todo, id: int = Path(description="Todo ID")) -> TodoId:
    """
    Update a Todo
    """
    now = datetime.utcnow()
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE todos SET title = ?, completed = ?, updated_date = ? WHERE id = ?",
        (payload.title, payload.completed, now, id),
    )
    db.commit()

    if cursor.rowcount == 0:
        db.close()
        raise HTTPException(status_code=404, detail="Not Found")

    db.close()
    return TodoId(id=id)

@router.delete("/{id}", response_model=bool, responses={404: {"description": "Not Found", "model": NotFoundException}})
async def delete_todo(id: int = Path(description="Todo ID")) -> bool:
    """
    Delete a Todo
    """
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("DELETE FROM todos WHERE id = ?", (id,))
    db.commit()

    if cursor.rowcount == 0:
        db.close()
        raise HTTPException(status_code=404, detail="Not Found")

    db.close()
    return True
