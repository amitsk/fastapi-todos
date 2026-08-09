from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from loguru import logger

from .db import TodoDB
from .models import TodoItem, TodoItemIn

todos_router = APIRouter()
db = TodoDB()


@todos_router.get(
    "/{todo_id}",
    tags=["todos"],
    status_code=status.HTTP_200_OK,
    response_model=TodoItem,
    response_class=JSONResponse,
)
async def get_todo(todo_id: int) -> TodoItem:
    todo_item = await db.find_todo(todo_id=todo_id)
    if not todo_item:
        logger.warning("Todo item not found {}", todo_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TODO not found")
    return todo_item


@todos_router.post(
    "/",
    tags=["todos"],
    status_code=status.HTTP_201_CREATED,
    response_model=TodoItem,
    response_class=JSONResponse,
)
async def create_todo(item: TodoItemIn) -> TodoItem:
    logger.info("Creating Todo")
    return await db.add_todo(item)


@todos_router.put(
    "/{todo_id}",
    tags=["todos"],
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=TodoItem,
)
async def update_todo(todo_id: int, item: TodoItemIn) -> TodoItem:
    logger.info("Updating Todo {}", todo_id)
    todo_item = await db.update_todo(todo_id, item)
    if not todo_item:
        logger.warning("Todo not found {}", todo_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TODO not found")
    return todo_item


@todos_router.delete(
    "/{todo_id}",
    tags=["todos"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_todo(todo_id: int) -> None:
    todo_item_id = await db.remove_todo(todo_id)
    if not todo_item_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TODO not found")
