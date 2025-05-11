# API - fastapi-todos

This is a demo project for building an API using FastAPI https://fastapi.tiangolo.com/

It uses

- Fast API - https://fastapi.tiangolo.com/
- Pydantic - https://pydantic-docs.helpmanual.io/usage/models/
- uvicorn https://github.com/encode/uvicorn
- TinyDB https://github.com/msiemens/tinydb
- Gunicorn https://gunicorn.org/

## Building


- Install uv https://docs.astral.sh/uv/getting-started/installation/
- Install Python3.13 `uv python install 3.13`
- Clone from github
- Build - Install, test, lint `make build`
- Tests can be run with `make test`

## Running APIs

- After build is done run `make app`
- Navigate to http://127.0.0.1:8000/docs to view the Open API docs

## Endpoints

- todos : http://127.0.0.1:8000/todos => CRUD endpoints agaist In-Memory TinyDB
- books : http://127.0.0.1:8000/books => Get a book's details by ISBN. Uses aiohttp to call OpenAPI

## Running in Docker

- Based off `python:3.13-slim`. Around 260MB image size
- `docker build -t fastapi/todos . `
- `docker run --name todos-container -p 8000:8000 --rm -d fastapi/todos`

## Configuration

- `gunicorn.conf.py`

## Json Logging using Loguru

- `custom_logging.py`

## Kubernetes

- Working installations of `minikube` and `kubectl`
- In a terminal `eval $(minikube -p minikube docker-env)`
- Build docker image
- `minikube start`
- Switch to `deployments/k8s`
- `kubectl create -f deployments.yaml`
- `kubectl create -f service.yaml`
- URL = `minikube service --url fastapi-todos-svc`
- Access the swagger console at <URL>/docs
