from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse

from .db import TodoDB
from .models import TodoItem, TodoItemIn

from loguru import logger

todos_router = APIRouter()
db = TodoDB()

not_found_response = JSONResponse(
    status_code=404, content={"message": "TODO not found"}
)


@todos_router.get(
    "/{todo_id}",
    tags=["todos"],
    status_code=status.HTTP_200_OK,
    response_model=TodoItem,
    response_class=JSONResponse,
)
async def get_todo(todo_id: int, response: Response):
    todo_item = await db.find_todo(todo_id=todo_id)
    if not todo_item:
        logger.warning(" Todo item Not found {}", todo_id)
        return not_found_response
    else:
        return todo_item


@todos_router.post(
    "/",
    tags=["todos"],
    status_code=status.HTTP_201_CREATED,
    response_model=TodoItem,
    response_class=JSONResponse,
)
async def create_todo(item: TodoItemIn):
    logger.info(" Creating Todo  ")
    return await db.add_todo(item)


@todos_router.put(
    "/{todo_id}",
    tags=["todos"],
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
)
async def update_todo(todo_id: int, item: TodoItem, response: Response):
    todo_item = await db.update_todo(todo_id, item)
    if not todo_item:
        logger.warning(" Not found Todo {} ", todo_id)
        return not_found_response
    else:
        logger.info(" Updating Todo  {}", todo_id)
        return todo_item


@todos_router.delete(
    "/{todo_id}", tags=["todos"], status_code=status.HTTP_204_NO_CONTENT
)
async def delete_todo(todo_id: int, response: Response):
    todo_item_id = await db.remove_todo(todo_id)
    if not todo_item_id:
        return not_found_response
    else:
        return None
