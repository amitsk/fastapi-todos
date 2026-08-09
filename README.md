# API - fastapi-todos

Demo project for building an API with [FastAPI](https://fastapi.tiangolo.com/).

## Stack

- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [Uvicorn](https://www.uvicorn.org/) / [Gunicorn](https://gunicorn.org/)
- [TinyDB](https://github.com/msiemens/tinydb) (todos persistence)
- [HTTPX](https://www.python-httpx.org/) (Open Library books client)
- [Loguru](https://loguru.readthedocs.io/) (JSON logging)
- [uv](https://docs.astral.sh/uv/) (package management)

## Building

- Install uv: https://docs.astral.sh/uv/getting-started/installation/
- Install Python 3.13: `uv python install 3.13`
- Clone the repo
- Install, test, and lint: `make build`
- Tests only: `make test`

## Running APIs

- After build: `make app`
- OpenAPI docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

## Endpoints

| Path | Description |
|------|-------------|
| `/todos` | CRUD against a local TinyDB file (`db.json`) |
| `/books/{isbn}` | Book details by ISBN via [Open Library API](https://openlibrary.org/dev/docs/api/books) |
| `/health` | Liveness probe |

## Running in Docker

- Base image: `python:3.13-slim` (multi-stage with uv)
- Build: `docker build -t fastapi/todos .`
- Run: `docker run --name todos-container -p 8000:8000 --rm -d fastapi/todos`

## Configuration

- Gunicorn: `gunicorn.conf.py` (bind, workers, timeouts; env overrides)
- Logging: `src/fastapi_todos/custom_logging.py` (Loguru JSON)
- Useful env vars: `PORT`, `LOG_LEVEL`, `WEB_CONCURRENCY`, `WORKERS_PER_CORE`, `TIMEOUT`

## Kubernetes

Requires working `minikube` and `kubectl`.

```bash
eval $(minikube -p minikube docker-env)
minikube start
docker build -t fastapi/todos .
kubectl apply -f deployments/k8s/deployments.yaml
kubectl apply -f deployments/k8s/service.yaml
minikube service --url fastapi-todos-svc
```

Open `<URL>/docs` for Swagger UI.
