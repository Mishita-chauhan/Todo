import os
from datetime import datetime
import uvicorn
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from tortoise.contrib.fastapi import register_tortoise
from tortoise.models import Model
from tortoise import fields
from pydantic_settings import BaseSettings, SettingsConfigDict

# Ensure the 'instance' folder exists
DB_FOLDER = "instance"
DB_FILE = f"{DB_FOLDER}/todo.db"

if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

if not os.path.exists(DB_FILE):
    open(DB_FILE, 'w').close()  # Create an empty database file

# Load settings from .env
class Settings(BaseSettings):
    database_url: str = f"sqlite://{DB_FILE}"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

app = FastAPI()

# Database Model
class TodoModel(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    completed = fields.BooleanField(default=False)
    created_date = fields.DatetimeField(auto_now_add=True)
    updated_date = fields.DatetimeField(auto_now=True)

# Pydantic Schemas
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

# Create a new Todo
@app.post("/todos", response_model=TodoId)
async def create_todo(payload: Todo) -> TodoId:
    """
    Create a new Todo
    """
    todo = await TodoModel.create(title=payload.title, completed=payload.completed)
    return TodoId(id=todo.id)

# Get a single Todo
@app.get("/todos/{id}", response_model=TodoRecord, responses={404: {"model": NotFoundException}})
async def get_todo(id: int = Path(description="Todo ID")) -> TodoRecord:
    """
    Get a Todo by ID
    """
    todo = await TodoModel.get_or_none(id=id)
    if not todo:
        raise HTTPException(status_code=404, detail="Not Found")
    return TodoRecord(**todo.__dict__)

# Get all Todos
@app.get("/todos", response_model=list[TodoRecord])
async def get_todos() -> list[TodoRecord]:
    """
    Get all Todos
    """
    todos = await TodoModel.all()
    return [TodoRecord(**todo.__dict__) for todo in todos]

# Update a Todo
@app.put("/todos/{id}", response_model=TodoId, responses={404: {"model": NotFoundException}})
async def update_todo(payload: Todo, id: int = Path(description="Todo ID")) -> TodoId:
    """
    Update a Todo
    """
    todo = await TodoModel.get_or_none(id=id)
    if not todo:
        raise HTTPException(status_code=404, detail="Not Found")

    todo.title = payload.title
    todo.completed = payload.completed
    todo.updated_date = datetime.utcnow()
    await todo.save()
    
    return TodoId(id=id)

# Delete a Todo
@app.delete("/todos/{id}", response_model=bool, responses={404: {"model": NotFoundException}})
async def delete_todo(id: int = Path(description="Todo ID")) -> bool:
    """
    Delete a Todo
    """
    deleted_count = await TodoModel.filter(id=id).delete()
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not Found")

    return True

# Database Connection Setup
register_tortoise(
    app,
    db_url=settings.database_url,
    modules={"models": ["main"]},
    generate_schemas=True,  # This will automatically create tables if they don't exist
    add_exception_handlers=True,
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)
