# from fastapi_todos.custom_logging import sink
from fastapi_todos.custom_logging import init_logging
from fastapi import FastAPI
from .todos.routers import todos_router
from .books.routers import books_router

# from loguru import logger

init_logging()

app = FastAPI()

# logger.add(sink)
app.include_router(todos_router, prefix="/todos", tags=["todos"])
app.include_router(books_router, prefix="/books", tags=["books"])
