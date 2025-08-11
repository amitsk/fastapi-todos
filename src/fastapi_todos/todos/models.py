from typing import Optional
from pydantic import BaseModel


class TodoItemIn(BaseModel):
    name: str
    description: Optional[str] = None
    completed: bool


class TodoItem(BaseModel):
    todo_id: int
    name: str
    description: Optional[str] = None
    completed: bool
