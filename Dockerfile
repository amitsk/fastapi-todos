FROM python:3.13-slim  as base
#https://github.com/astral-sh/uv-docker-example/blob/main/multistage.Dockerfile

# Setup env
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Turns off writing .pyc files; superfluous on an ephemeral container.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Disable Python downloads, because we want to use the system interpreter
# across both images. If using a managed Python version, it needs to be
# copied from the build image into the final image; see `standalone.Dockerfile`
# for an example.
ENV UV_PYTHON_DOWNLOADS=0
FROM base AS builder


# RUN apt-get update && apt-get install -y --no-install-recommends g++
# install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM base AS runtime

# Extra python env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1


ENV APP_MODULE="fastapi_todos.main:app"
ENV PORT 8000
ENV PYTHONPATH=/home/appuser:$PYTHONPATH

# Create and switch to a new user
RUN useradd --create-home appuser
WORKDIR /home/appuser

# Copy virtual env from python-deps stage
# It is important to use the image that matches the builder, as the path to the
# Python executable must be the same, e.g., using `python:3.11-slim-bookworm`
# will fail.

# Copy the application from the builder
COPY --from=builder --chown=appuser:appuser /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"


EXPOSE ${PORT}
COPY start.sh .
RUN chmod +x ./start.sh
COPY gunicorn.conf.py .
USER appuser

CMD ["./start.sh"]