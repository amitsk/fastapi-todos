import json
from collections.abc import Iterator
from pathlib import Path

import pytest

from fastapi_todos.todos.db import TodoDB
from fastapi_todos.todos.models import TodoItemIn


@pytest.fixture
def db_file(tmp_path: Path) -> Path:
    return tmp_path / "todos.json"


@pytest.fixture
def db(db_file: Path) -> Iterator[TodoDB]:
    database = TodoDB(db_path=str(db_file))
    yield database
    database.close()


async def test_written_todo_is_on_disk_before_close(db: TodoDB, db_file: Path) -> None:
    """CachingMiddleware buffers writes until close() and the app never closes,
    so a restart loses everything. Writes must hit the file immediately."""
    await db.add_todo(TodoItemIn(name="durable", description="persist me"))

    assert db_file.stat().st_size > 0, "write was buffered in memory, not persisted"


async def test_data_survives_reopening_the_file(db_file: Path) -> None:
    """The restart case: what one TodoDB wrote must be visible to the next."""
    first = TodoDB(db_path=str(db_file))
    await first.add_todo(TodoItemIn(name="survives", completed=False))
    # Deliberately no close(): simulates the process going away without a
    # shutdown hook.

    second = TodoDB(db_path=str(db_file))
    try:
        stored = await second.find_todo(1)
        assert stored is not None, "todo written by the first handle is gone"
        assert stored.name == "survives"
    finally:
        second.close()
        first.close()


async def test_update_is_on_disk_before_close(db: TodoDB, db_file: Path) -> None:
    await db.add_todo(TodoItemIn(name="before"))
    await db.update_todo(1, TodoItemIn(name="after", completed=True))

    records = json.loads(db_file.read_text())["_default"]
    assert records["1"]["name"] == "after"
    assert records["1"]["completed"] is True


async def test_delete_is_on_disk_before_close(db: TodoDB, db_file: Path) -> None:
    await db.add_todo(TodoItemIn(name="doomed"))
    await db.remove_todo(1)

    records = json.loads(db_file.read_text())["_default"]
    assert "1" not in records, "deleted todo still on disk"
