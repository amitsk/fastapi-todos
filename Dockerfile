# https://github.com/astral-sh/uv-docker-example/blob/main/multistage.Dockerfile
FROM python:3.14-slim AS base

# Setup env
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    # Disable Python downloads; use the image interpreter in build + runtime.
    UV_PYTHON_DOWNLOADS=0

FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM base AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_MODULE=fastapi_todos.main:app \
    PORT=8000 \
    PYTHONPATH=/app/src \
    PATH="/app/.venv/bin:$PATH"

RUN useradd --create-home appuser

# Copy the application (and venv) from the builder
COPY --from=builder --chown=appuser:appuser /app /app

WORKDIR /app
# start.sh and gunicorn.conf.py arrived with /app; just make the script runnable.
RUN chmod +x ./start.sh

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

CMD ["./start.sh"]
