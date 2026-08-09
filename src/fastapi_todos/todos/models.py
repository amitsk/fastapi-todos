from pydantic import BaseModel, Field


class TodoItemIn(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None
    completed: bool = False


class TodoItem(BaseModel):
    todo_id: int
    name: str
    description: str | None = None
    completed: bool
