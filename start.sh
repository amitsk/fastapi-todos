#!/usr/bin/env bash
set -euo pipefail

# Runtime image has the project venv on PATH (no uv required).
export WORKER_CLASS="${WORKER_CLASS:-uvicorn.workers.UvicornWorker}"
export GUNICORN_CONF="${GUNICORN_CONF:-./gunicorn.conf.py}"
export APP_MODULE="${APP_MODULE:-fastapi_todos.main:app}"

exec gunicorn -k "${WORKER_CLASS}" -c "${GUNICORN_CONF}" "${APP_MODULE}"
