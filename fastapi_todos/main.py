from fastapi_todos.custom_logging import init_logging
from fastapi import FastAPI
from .todos import todos_router
from .books import books_router


init_logging()

app = FastAPI()

app.include_router(todos_router, prefix="/todos", tags=["todos"])
app.include_router(books_router, prefix="/books", tags=["books"])
