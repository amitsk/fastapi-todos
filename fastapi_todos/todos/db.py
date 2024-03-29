from typing import Optional

from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

from .models import TodoItem, TodoItemIn


class TodoDB:
    def __init__(self) -> None:
        self._db = TinyDB("db.json", storage=CachingMiddleware(JSONStorage))

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._db.close()

    async def find_todo(self, todo_id: int) -> Optional[TodoItem]:
        if self._db.contains(doc_id=todo_id):
            db_rec = self._db.get(doc_id=todo_id)

            return TodoItem(
                todo_id=db_rec.doc_id,
                name=db_rec["name"],
                description=db_rec["description"],
                completed=db_rec["completed"],
            )
        return None

    async def add_todo(self, todo_item: TodoItemIn) -> Optional[TodoItem]:
        new_todo_in = todo_item.copy()
        new_id = self._db.insert(new_todo_in.dict())
        return TodoItem(
            todo_id=new_id,
            name=todo_item.name,
            description=todo_item.description,
            completed=todo_item.completed,
        )

    async def update_todo(
        self,
        todo_id: int,
        todo_item: TodoItem,
    ) -> Optional[TodoItem]:
        if self._db.contains(doc_id=todo_id):
            self._db.update(
                {
                    "name": todo_item.name,
                    "description": todo_item.description,
                    "completed": todo_item.completed,
                },
                doc_ids=[todo_id],
            )
            return TodoItem(
                todo_id=todo_id,
                name=todo_item.name,
                description=todo_item.description,
                completed=todo_item.completed,
            )
        return None

    async def remove_todo(self, todo_id: int) -> Optional[int]:
        if self._db.contains(doc_id=todo_id):
            self._db.remove(doc_ids=[todo_id])
            return todo_id
        return None
