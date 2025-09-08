#! /bin/bash

export WORKER_CLASS=${WORKER_CLASS:-"uvicorn.workers.UvicornWorker"}
# Start Gunicorn
exec uv run gunicorn -k "$WORKER_CLASS" -c "$GUNICORN_CONF" "$APP_MODULE"
