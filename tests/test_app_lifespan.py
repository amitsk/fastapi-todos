from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from fastapi_todos.main import app
from fastapi_todos.todos.db import TodoDB


@pytest.fixture
def db_file(tmp_path: Path) -> Path:
    return tmp_path / "todos.json"


def test_app_shuts_down_the_todo_db(
    db_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The app owns the DB handle, so it must close it on shutdown; an
    unclosed TinyDB leaks the handle and skips any final flush."""
    database = TodoDB(db_path=str(db_file))
    closed: list[bool] = []
    original_close = database.close

    def tracking_close() -> None:
        closed.append(True)
        original_close()

    monkeypatch.setattr(database, "close", tracking_close)
    monkeypatch.setattr("fastapi_todos.todos.routers.db", database)

    with TestClient(app) as client:
        assert client.get("/health").status_code == 200

    assert closed, "app did not close the todo db on shutdown"


def test_health_reports_ok(db_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("fastapi_todos.todos.routers.db", TodoDB(db_path=str(db_file)))

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_todo_created_via_the_app_reaches_the_configured_db(
    db_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = TodoDB(db_path=str(db_file))
    monkeypatch.setattr("fastapi_todos.todos.routers.db", database)

    with TestClient(app) as client:
        created = client.post("/todos/", json={"name": "via app"})

    assert created.status_code == 201
    assert created.json()["name"] == "via app"
    assert "via app" in db_file.read_text()
