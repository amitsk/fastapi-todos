from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_todos.todos.db import TodoDB
from fastapi_todos.todos.routers import todos_router


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """A client whose requests hit a TodoDB backed by a temp file."""
    database = TodoDB(db_path=str(tmp_path / "todos.json"))
    monkeypatch.setattr("fastapi_todos.todos.routers.db", database)
    app = FastAPI()
    app.include_router(todos_router, prefix="/todos", tags=["todos"])
    with TestClient(app) as test_client:
        yield test_client
    database.close()


def test_created_todo_is_returned_with_201(client: TestClient) -> None:
    response = client.post("/todos/", json={"name": "write tests"})

    assert response.status_code == 201
    assert response.json() == {
        "todo_id": 1,
        "name": "write tests",
        "description": None,
        "completed": False,
    }


def test_created_todo_is_readable_by_id(client: TestClient) -> None:
    created = client.post("/todos/", json={"name": "round trip"}).json()

    response = client.get(f"/todos/{created['todo_id']}")

    assert response.status_code == 200
    assert response.json()["name"] == "round trip"


def test_todo_created_by_one_request_survives_into_the_next(client: TestClient) -> None:
    """Multi-worker deployments hit this: a write must be visible to a
    later, independent request."""
    first = client.post("/todos/", json={"name": "first"}).json()
    second = client.post("/todos/", json={"name": "second"}).json()

    assert client.get(f"/todos/{first['todo_id']}").status_code == 200
    assert client.get(f"/todos/{second['todo_id']}").status_code == 200


def test_todo_written_through_the_api_persists_to_disk(
    client: TestClient, tmp_path: Path
) -> None:
    db_file = tmp_path / "todos.json"
    client.post("/todos/", json={"name": "durable through api"})

    assert db_file.stat().st_size > 0
    assert "durable through api" in db_file.read_text()


def test_unknown_todo_returns_404(client: TestClient) -> None:
    assert client.get("/todos/9999").status_code == 404


def test_update_of_unknown_todo_returns_404(client: TestClient) -> None:
    assert client.put("/todos/9999", json={"name": "nope"}).status_code == 404


def test_delete_of_unknown_todo_returns_404(client: TestClient) -> None:
    assert client.delete("/todos/9999").status_code == 404


def test_delete_returns_204_with_no_body(client: TestClient) -> None:
    created = client.post("/todos/", json={"name": "doomed"}).json()

    response = client.delete(f"/todos/{created['todo_id']}")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/todos/{created['todo_id']}").status_code == 404


def test_update_changes_the_stored_todo(client: TestClient) -> None:
    created = client.post("/todos/", json={"name": "before"}).json()

    response = client.put(
        f"/todos/{created['todo_id']}", json={"name": "after", "completed": True}
    )

    assert response.status_code == 200
    assert client.get(f"/todos/{created['todo_id']}").json() == {
        "todo_id": created["todo_id"],
        "name": "after",
        "description": None,
        "completed": True,
    }


def test_empty_name_is_rejected_with_422(client: TestClient) -> None:
    assert client.post("/todos/", json={"name": ""}).status_code == 422


def test_non_integer_todo_id_is_rejected_with_422(client: TestClient) -> None:
    assert client.get("/todos/abc").status_code == 422
