from fastapi_todos.todos.models import TodoItem, TodoItemIn
from fastapi_todos.todos.db import TodoDB
import pytest


@pytest.mark.asyncio
async def test_db_operations():
    """
    docstring
    """
    todo_db = TodoDB()

    todo_item = TodoItemIn(name="test", description="Todo Item Test", completed=False)

    new_todo = await todo_db.add_todo(todo_item)
    assert new_todo == TodoItem(
        todo_id=1, name="test", description="Todo Item Test", completed=False
    )
    stored_todo = await todo_db.find_todo(1)
    assert stored_todo == TodoItem(
        todo_id=1, name="test", description="Todo Item Test", completed=False
    )
    assert await todo_db.find_todo(10000) is None

    stored_todo = await todo_db.update_todo(
        stored_todo.todo_id,
        TodoItem(
            todo_id=stored_todo.todo_id,
            name=stored_todo.name,
            description=stored_todo.description,
            completed=True,
        ),
    )

    stored_todo = await todo_db.find_todo(1)

    assert stored_todo == TodoItem(
        todo_id=1, name="test", description="Todo Item Test", completed=True
    )

    deleted_item_id = await todo_db.remove_todo(stored_todo.todo_id)
    assert deleted_item_id == stored_todo.todo_id
    assert await todo_db.find_todo(1) is None