import asyncio
import json
import multiprocessing
from pathlib import Path

import pytest

from fastapi_todos.todos.db import TodoDB
from fastapi_todos.todos.models import TodoItemIn

WORKERS = 8


def _write_one(db_path: str, name: str) -> None:
    """Stand-in for a gunicorn worker process handling one request."""
    db = TodoDB(db_path=db_path)
    try:
        asyncio.run(db.add_todo(TodoItemIn(name=name)))
    except Exception as exc:  # noqa: BLE001 - surfaced via the exit code
        print(f"ERR {type(exc).__name__}: {exc}", flush=True)
        raise
    finally:
        db.close()


def _write_many(db_path: str, count: int) -> None:
    db = TodoDB(db_path=db_path)
    try:

        async def run() -> None:
            for index in range(count):
                await db.add_todo(TodoItemIn(name=f"n{index}"))

        asyncio.run(run())
    finally:
        db.close()


async def _read_names(db: TodoDB, limit: int) -> list[str]:
    names: list[str] = []
    for todo_id in range(1, limit):
        item = await db.find_todo(todo_id)
        if item is not None:
            names.append(item.name)
    return names


def _spawn_in_parallel(args: list[tuple[object, ...]]) -> list[int]:
    """Run each arg tuple in its own process, concurrently."""
    context = multiprocessing.get_context("spawn")
    processes = [context.Process(target=_write_one, args=arg) for arg in args]
    for process in processes:
        process.start()
    for process in processes:
        process.join(timeout=60)
    return [process.exitcode for process in processes]


@pytest.fixture
def db_file(tmp_path: Path) -> Path:
    return tmp_path / "todos.json"


def test_interleaved_writers_from_separate_handles_do_not_collide(db_file: Path) -> None:
    """TinyDB caches the next document id on the Table and only recomputes it
    when the table is emptied. Two handles that each insert -- as separate
    gunicorn workers do -- hand out the same id and the second insert raises
    "Document with ID N already exists"."""
    worker_a = TodoDB(db_path=str(db_file))
    worker_b = TodoDB(db_path=str(db_file))
    try:
        asyncio.run(worker_a.add_todo(TodoItemIn(name="a-first")))  # id 1
        asyncio.run(worker_b.add_todo(TodoItemIn(name="b-first")))  # id 2
        asyncio.run(worker_a.add_todo(TodoItemIn(name="a-second")))  # must be 3
        asyncio.run(worker_b.add_todo(TodoItemIn(name="b-second")))  # must be 4
        names = sorted(asyncio.run(_read_names(worker_a, limit=10)))
    finally:
        worker_a.close()
        worker_b.close()

    assert names == ["a-first", "a-second", "b-first", "b-second"]


def test_concurrent_writers_leave_readable_json(db_file: Path) -> None:
    """Unserialized read-modify-write leaves a half-written file and the next
    read raises JSONDecodeError."""
    exit_codes = _spawn_in_parallel(
        [(str(db_file), f"todo-{index}") for index in range(WORKERS)]
    )

    assert all(code == 0 for code in exit_codes), "a writer process crashed"
    json.loads(db_file.read_text())


def test_every_concurrent_write_is_retained(db_file: Path) -> None:
    """No silent lost updates: all concurrent writes must be readable."""
    exit_codes = _spawn_in_parallel(
        [(str(db_file), f"todo-{index}") for index in range(WORKERS)]
    )
    assert all(code == 0 for code in exit_codes)

    db = TodoDB(db_path=str(db_file))
    try:
        names = set(asyncio.run(_read_names(db, limit=WORKERS * 4)))
    finally:
        db.close()

    assert names == {f"todo-{index}" for index in range(WORKERS)}


def test_reads_do_not_fail_while_another_process_writes(db_file: Path) -> None:
    """A reader must never see a half-written file."""
    context = multiprocessing.get_context("spawn")
    writer = context.Process(target=_write_many, args=(str(db_file), WORKERS * 5))
    writer.start()
    try:
        for _ in range(WORKERS * 5):
            db = TodoDB(db_path=str(db_file))
            try:
                asyncio.run(_read_names(db, limit=WORKERS))
            finally:
                db.close()
    finally:
        writer.join(timeout=60)
