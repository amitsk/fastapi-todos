from typing import Any, Mapping, Optional

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

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._http_session.close()

    async def fetch_book_details(self, isbn: str) -> Optional[Mapping[str, Any]]:
        book_params = {"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"}
        async with self._http_session.get(BASE_URL, params=book_params) as resp:
            if resp.status == 200:
                resp_json = await resp.json()
                if resp_json:
                    book = resp_json.get(f"ISBN:{isbn}", None)
                    book["isbn"] = isbn
                    return book

            return None
