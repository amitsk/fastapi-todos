
from tinydb import TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage

from .models import TodoItem, TodoItemIn


class TodoDB:
    def __init__(self, db_path: str = "db.json") -> None:
        self._db = TinyDB(db_path, storage=CachingMiddleware(JSONStorage))

    def close(self) -> None:
        self._db.close()

    def __enter__(self) -> "TodoDB":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object,
    ) -> None:
        self.close()

    async def find_todo(self, todo_id: int) -> TodoItem | None:
        if self._db.contains(doc_id=todo_id):
            db_rec = self._db.get(doc_id=todo_id)
            if db_rec is None:
                return None

            return TodoItem(
                todo_id=db_rec.doc_id,
                name=db_rec["name"],
                description=db_rec["description"],
                completed=db_rec["completed"],
            )
        return None

    async def add_todo(self, todo_item: TodoItemIn) -> TodoItem:
        new_id = self._db.insert(todo_item.model_dump())
        return TodoItem(
            todo_id=new_id,
            name=todo_item.name,
            description=todo_item.description,
            completed=todo_item.completed,
        )

    async def update_todo(
        self,
        todo_id: int,
        todo_item: TodoItemIn,
    ) -> TodoItem | None:
        if self._db.contains(doc_id=todo_id):
            self._db.update(
                todo_item.model_dump(),
                doc_ids=[todo_id],
            )
            return TodoItem(
                todo_id=todo_id,
                name=todo_item.name,
                description=todo_item.description,
                completed=todo_item.completed,
            )
        return None

    async def remove_todo(self, todo_id: int) -> int | None:
        if self._db.contains(doc_id=todo_id):
            self._db.remove(doc_ids=[todo_id])
            return todo_id
        return None
