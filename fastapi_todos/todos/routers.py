from fastapi import APIRouter, Response, status
from .models import TodoItem

router = APIRouter()


@router.get("/todos/", tags=["todos"], status_code=201)
async def read_todos():
    return {"message": "Todos Application"}


@router.get("/todos/{todo_id}", tags=["todos"], status_code=status.HTTP_201_CREATED)
async def get_todo(todo_id: int, response: Response) -> TodoItem:
    return TodoItem()


@router.post("/todos/", tags=["todos"], status_code=status.HTTP_200_OK)
async def create_todo(todo_id: int, item: TodoItem) -> TodoItem:
    return TodoItem()


@router.put("/todos/{todo_id}", tags=["todos"], status_code=status.HTTP_200_OK)
async def update_todo(todo_id: int, item: TodoItem, response: Response) -> TodoItem:
    return TodoItem()


@router.delete(
    "/todos/{todo_id}", tags=["todos"], status_code=status.HTTP_204_NO_CONTENT
)
async def delete_todo(todo_id: int, response: Response) -> None:
    return None
