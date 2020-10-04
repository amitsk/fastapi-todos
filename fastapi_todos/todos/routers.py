from typing import Awaitable, Coroutine

from fastapi.responses import ORJSONResponse as JSONResponse
from fastapi_todos.todos.db import TodoDB
from fastapi import APIRouter, Response, status
from .models import TodoItem

router = APIRouter()
db = TodoDB()

not_found_response = JSONResponse(
    status_code=404, content={"message": "Item not found"}
)


@router.get("/{todo_id}", tags=["todos"], status_code=status.HTTP_200_OK)
async def get_todo(todo_id: int, response: Response):
    todo_item = await db.find_todo(todo_id=todo_id)
    if not todo_item:
        return not_found_response
    else:
        return todo_item


@router.post("/", tags=["todos"], status_code=status.HTTP_201_CREATED)
async def create_todo(item: TodoItem):
    return await db.add_todo(item)


@router.put("/{todo_id}", tags=["todos"], status_code=status.HTTP_200_OK)
async def update_todo(todo_id: int, item: TodoItem, response: Response):
    todo_item = await db.update_todo(todo_id, item)
    if not todo_item:
        return not_found_response
    else:
        return todo_item


@router.delete("/{todo_id}", tags=["todos"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int, response: Response):
    todo_item_id = await db.remove_todo(todo_id)
    if not todo_item_id:
        return not_found_response
    else:
        return None
