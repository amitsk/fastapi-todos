from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi_todos.custom_logging import init_logging

from .books import books_router
from .todos import routers as todos_routers
from .todos import todos_router

init_logging()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Close the todos DB on shutdown so the handle is released and any
    pending write is flushed.

    The handle is looked up on the routers module at shutdown rather than
    captured at import, so routers stays the single owner of it.
    """
    yield
    todos_routers.db.close()


app = FastAPI(
    title="FastAPI Todos",
    description="Demo API: Todos (TinyDB) and Books (Open Library)",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(todos_router, prefix="/todos", tags=["todos"])
app.include_router(books_router, prefix="/books", tags=["books"])


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


def run() -> None:
    """Console entry point for `fastapi-todos` / `uv run fastapi-todos`."""
    import uvicorn

    uvicorn.run("fastapi_todos.main:app", host="0.0.0.0", port=8000, reload=False)
