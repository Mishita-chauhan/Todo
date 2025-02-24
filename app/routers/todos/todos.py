from datetime import datetime

from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from .models import NotFoundException, Todo, TodoId, TodoRecord
from .schemas import TodoCreate, TodoUpdate
from .models import TodoModel

router = APIRouter()

@router.post("", response_model=TodoId)
async def create_todo(payload: TodoCreate, db: AsyncSession = Depends(get_db)) -> TodoId:
    """
    Create a new Todo
    """
    now = datetime.utcnow()
    new_todo = TodoModel(
        title=payload.title,
        completed=payload.completed,
        created_date=now,
        updated_date=now,
    )
    db.add(new_todo)
    await db.commit()
    await db.refresh(new_todo)
    return TodoId(id=new_todo.id)

@router.get("/{id}", response_model=TodoRecord, responses={404: {"description": "Not Found", "model": NotFoundException}})
async def get_todo(id: int, db: AsyncSession = Depends(get_db)) -> TodoRecord:
    """
    Get a Todo
    """
    result = await db.execute(select(TodoModel).filter(TodoModel.id == id))
    todo = result.scalars().first()
    if not todo:
        raise HTTPException(status_code=404, detail="Not Found")
    return TodoRecord.from_orm(todo)

@router.get("", response_model=list[TodoRecord])
async def get_todos(db: AsyncSession = Depends(get_db)) -> list[TodoRecord]:
    """
    Get Todos
    """
    result = await db.execute(select(TodoModel))
    todos = result.scalars().all()
    return [TodoRecord.from_orm(todo) for todo in todos]

@router.put("/{id}", response_model=TodoId, responses={404: {"description": "Not Found", "model": NotFoundException}})
async def update_todo(id: int, payload: TodoUpdate, db: AsyncSession = Depends(get_db)) -> TodoId:
    """
    Update a Todo
    """
    result = await db.execute(select(TodoModel).filter(TodoModel.id == id))
    todo = result.scalars().first()
    if not todo:
        raise HTTPException(status_code=404, detail="Not Found")
    
    todo.title = payload.title
    todo.completed = payload.completed
    todo.updated_date = datetime.utcnow()
    
    await db.commit()
    await db.refresh(todo)
    return TodoId(id=todo.id)

@router.delete("/{id}", response_model=bool, responses={404: {"description": "Not Found", "model": NotFoundException}})
async def delete_todo(id: int, db: AsyncSession = Depends(get_db)) -> bool:
    """
    Delete a Todo
    """
    result = await db.execute(select(TodoModel).filter(TodoModel.id == id))
    todo = result.scalars().first()
    if not todo:
        raise HTTPException(status_code=404, detail="Not Found")
    
    await db.delete(todo)
    await db.commit()
    return True
