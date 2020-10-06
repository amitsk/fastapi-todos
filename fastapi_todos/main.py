from fastapi import FastAPI
from fastapi_todos.todos.routers import todos_router
from fastapi_todos.books.routers import books_router

app = FastAPI()
app.include_router(todos_router, prefix="/todos", tags=["todos"])
app.include_router(books_router, prefix="/books", tags=["books"])
