# (generated with --quick)

from typing import Any, Optional

BaseModel: Any

class TodoItem(Any):
    completed: bool
    description: Optional[str]
    name: str
    todo_id: int

class TodoItemIn(Any):
    completed: bool
    description: Optional[str]
    name: str
