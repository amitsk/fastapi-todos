from fastapi import FastAPI
from .todos.routers import todos_router
from .books.routers import books_router

app = FastAPI()
app.include_router(todos_router, prefix="/todos", tags=["todos"])
app.include_router(books_router, prefix="/books", tags=["books"])
