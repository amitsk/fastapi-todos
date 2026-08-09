from typing import Any

from pydantic import BaseModel


class Author(BaseModel):
    name: str
    url: str


class Publisher(BaseModel):
    name: str


class Subject(BaseModel):
    url: str
    name: str


class Book(BaseModel):
    isbn: str
    subtitle: str | None = None
    url: str
    title: str
    identifiers: dict[str, Any] = {}
    publishers: list[Publisher] = []
    authors: list[Author] = []
    subjects: list[Subject] = []
    publish_date: str | None = None
