from typing import Any, Dict, List
from pydantic import BaseModel

#


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
    publish_date: str
    subtitle: str
    url: str
    title: str
    identifiers: Dict[str, Any]
    publishers: List[Publisher]
    authors: List[Author]
    subjects: List[Subject]
    publish_date: str
