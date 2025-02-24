import time
from typing import Any, Callable, TypeVar
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.todos import todos
from app.utilities.logger import logger
from app.utilities.db import get_db_connection

description = """
Build a simple Todo API with FastAPI and SQLite
"""

app = FastAPI(
    title="My Todo App",
    description=description,
    version="1.0.0",
    docs_url="/",
    root_path=settings.root_path,
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=["http://localhost:3000"],
)

F = TypeVar("F", bound=Callable[..., Any])

@app.middleware("http")
async def process_time_log_middleware(request: Request, call_next: F) -> Response:
    """
    Add API process time in response headers and log calls
    """
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = str(round(time.time() - start_time, 3))
    response.headers["X-Process-Time"] = process_time

    logger.info(
        "Method=%s Path=%s StatusCode=%s ProcessTime=%s",
        request.method,
        request.url.path,
        response.status_code,
        process_time,
    )

    return response

# 🚀 Include Todo Router (Now Uses SQLite)
app.include_router(
    todos.router,
    prefix="/v1/todos",
    tags=["todos"],
)

# ✅ Ensure database table exists before starting
def init_db():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed BOOLEAN DEFAULT 0,
            created_date TEXT NOT NULL,
            updated_date TEXT NOT NULL
        )
    """)
    db.commit()
    db.close()

init_db()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="debug",
        reload=True,
    )
