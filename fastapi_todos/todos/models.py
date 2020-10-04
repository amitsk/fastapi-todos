from typing import Optional
from pydantic import BaseModel


class TodoItem(BaseModel):
    todo_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    completed: bool