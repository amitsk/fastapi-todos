import fcntl
import json
import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from tinydb import TinyDB
from tinydb.storages import JSONStorage

from .models import TodoItem, TodoItemIn


class AtomicJSONStorage(JSONStorage):
    """JSONStorage that rewrites db.json via a temp file and os.replace.

    Two problems with the stock in-place write:

    * TinyDB seeks to 0 and writes, so a reader (or a second gunicorn worker)
      that opens the file between the overwrite and the truncation sees partial
      JSON and raises JSONDecodeError.
    * The long-lived file handle keeps pointing at the original inode. After
      os.replace swaps in a new inode, that handle still reads the old,
      unlinked one -- so this process would read its own writes as missing and
      the next write would discard them.

    Opening the path fresh on every read sidesteps both.
    """

    def __init__(self, path: str, create_dirs: bool = False, **kwargs: Any) -> None:
        super().__init__(path, create_dirs=create_dirs, **kwargs)
        self._path = Path(path)

    def read(self) -> dict[str, dict[str, Any]] | None:
        try:
            raw = self._path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None
        if not raw.strip():
            return None
        return json.loads(raw)

    def write(self, data: dict[str, dict[str, Any]]) -> None:
        tmp_path = self._path.with_name(f"{self._path.name}.{os.getpid()}.tmp")
        with open(tmp_path, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(data, **self.kwargs))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, self._path)

    def close(self) -> None:
        self._handle.close()


class TodoDB:
    def __init__(self, db_path: str = "db.json") -> None:
        # Plain JSONStorage, not CachingMiddleware: the cache only flushes on
        # close(), and nothing closes this handle, so every write would be lost
        # when the process exits.
        self._path = Path(db_path)
        self._lock_path = self._path.with_name(f"{self._path.name}.lock")
        self._db = TinyDB(db_path, storage=AtomicJSONStorage)

    @contextmanager
    def _exclusive(self) -> Iterator[None]:
        """Serialize read-modify-write cycles across processes.

        Gunicorn runs one worker per core and Kubernetes runs several pods.
        Two problems arise without this:

        * Concurrent read-modify-write lets each writer assign the same id, so
          the later write silently discards the earlier one.
        * TinyDB caches the next document id on the Table and only recomputes
          it when the table is emptied. A worker that has inserted once keeps
          handing out its cached id, which collides with what another worker
          has since written. Clearing it forces a re-read under the lock.
        """
        with open(self._lock_path, "w") as lock_handle:
            fcntl.flock(lock_handle, fcntl.LOCK_EX)
            try:
                self._db.table("_default")._next_id = None
                yield
            finally:
                fcntl.flock(lock_handle, fcntl.LOCK_UN)

    def close(self) -> None:
        self._db.close()

    def __enter__(self) -> TodoDB:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object,
    ) -> None:
        self.close()

    async def find_todo(self, todo_id: int) -> TodoItem | None:
        with self._exclusive():
            db_rec = self._db.get(doc_id=todo_id)
        if db_rec is None:
            return None

        return TodoItem(
            todo_id=db_rec.doc_id,
            name=db_rec["name"],
            description=db_rec["description"],
            completed=db_rec["completed"],
        )

    async def add_todo(self, todo_item: TodoItemIn) -> TodoItem:
        with self._exclusive():
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
        with self._exclusive():
            if not self._db.contains(doc_id=todo_id):
                return None
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

    async def remove_todo(self, todo_id: int) -> int | None:
        with self._exclusive():
            if not self._db.contains(doc_id=todo_id):
                return None
            self._db.remove(doc_ids=[todo_id])
        return todo_id
