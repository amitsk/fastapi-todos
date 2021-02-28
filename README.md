# API - fastapi-todos

This is a demo project for building an API using FastAPI https://fastapi.tiangolo.com/

It uses

- Fast API - https://fastapi.tiangolo.com/
- Pydantic - https://pydantic-docs.helpmanual.io/usage/models/
- aiohttp https://docs.aiohttp.org/en/stable/
- orjson https://github.com/ijl/orjson
- uvicorn https://github.com/encode/uvicorn
- TinyDB https://github.com/msiemens/tinydb
- Gunicorn https://gunicorn.org/

## Building

- Install Python3.x
- Install pipenv https://pipenv.pypa.io/en/latest/
- Clone from github
- Build - Install, test, lint `make build`
- Tests can be run with `make test`

## Running APIs

- After build is done run `uvicorn fastapi_todos.main:app --reload`
- Navigate to http://127.0.0.1:8000/docs to view the Open API docs

## Endpoints

- todos : http://127.0.0.1:8000/todos => CRUD endpoints agaist In-Memory TinyDB
- books : http://127.0.0.1:8000/books => Get a book's details by ISBN. Uses aiohttp to call OpenAPI

## Running in Docker

- Based off `python:3.8-slim`. Around 260MB image size
- `docker build -t myimage . `
- `docker run -p 8000:8000 myimage`

## Configuration

- `gunicorn.conf.py`

## Json Logging using Loguru

- `custom_logging.py`
