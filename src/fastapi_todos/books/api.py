from collections.abc import Mapping
from typing import Any

import httpx
from httpx import Timeout
from loguru import logger

# https://openlibrary.org/api/books?bibkeys=ISBN%3A0201558025&format=json&jscmd=data
BASE_URL = "https://openlibrary.org/api/books"


class BooksApi:
    books_timeout = Timeout(timeout=10.0)

    async def fetch_book_details(self, isbn: str) -> Mapping[str, Any] | None:
        book_params = {"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"}
        async with httpx.AsyncClient(timeout=self.books_timeout, http2=True) as client:
            resp = await client.get(BASE_URL, params=book_params)
            if resp.is_success:
                resp_json = resp.json()
                book = resp_json.get(f"ISBN:{isbn}")
                if book is not None:
                    return {**book, "isbn": isbn}

            logger.info("No record found for ISBN {}", isbn)
            return None
