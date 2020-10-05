from typing import Any
from async_timeout import timeout
from fastapi import params
from .models import Book
import aiohttp
import orjson

# https://openlibrary.org/api/books?bibkeys=ISBN%3A0201558025&format=json&jscmd=data
BASE_URL = "https://openlibrary.org/api/books"


class BooksApi:
    books_timeout = aiohttp.ClientTimeout(total=30.0)

    @staticmethod
    def books_serialize(obj: Any) -> str:
        return orjson.dumps(obj).decode("utf-8")

    def __init__(self) -> None:
        self._http_session = aiohttp.ClientSession(
            json_serialize=BooksApi.books_serialize,
            timeout=BooksApi.books_timeout,
        )

    def __exit__(self, exc_type, exc_value, traceback):
        self._http_session.close()

    async def fetch_book_details(self, isbn: str):
        params = {"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"}
        async with self._http_session.get(BASE_URL, params=params) as resp:
            resp_json = await resp.json()
            return resp_json.get(f"ISBN:{isbn}", None)
