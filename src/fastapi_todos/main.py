from fastapi import FastAPI

from fastapi_todos.custom_logging import init_logging

from .books import books_router
from .todos import todos_router

init_logging()

app = FastAPI(
    title="FastAPI Todos",
    description="Demo API: Todos (TinyDB) and Books (Open Library)",
    version="0.1.0",
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
