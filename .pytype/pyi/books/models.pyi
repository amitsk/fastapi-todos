# (generated with --quick)

from typing import Any, Dict, List

BaseModel: Any

class Author(Any):
    name: str
    url: str

class Book(Any):
    authors: List[Author]
    identifiers: Dict[str, Any]
    isbn: str
    publish_date: str
    publishers: List[Publisher]
    subjects: List[Subject]
    subtitle: str
    title: str
    url: str

class Publisher(Any):
    name: str

class Subject(Any):
    name: str
    url: str
