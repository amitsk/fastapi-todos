from fastapi import FastAPI
from fastapi_todos.todos.routers import router as todos_router

app = FastAPI()
app.include_router(todos_router, prefix="/todos", tags=["todos"])
