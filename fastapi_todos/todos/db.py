from fastapi_todos.todos.models import TodoItem
from typing import Dict, Optional
from atomic import AtomicLong


class TodoDB:
    def __init__(self):
        self.atomic = AtomicLong(0)

    def find_item(self, item_id: int) -> Optional[TodoItem]:
        return None

    def add_item(self, item_id: int, TodoItem) -> Optional[TodoItem]:
        self.atomic += 1
        key = self.atomic.value
        return None

    def update_item(self, item_id: int) -> Optional[TodoItem]:
        return None

    def remove_item(self, item_id: int) -> Optional[TodoItem]:
        return None
