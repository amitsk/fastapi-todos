from typing import Any, Mapping, Optional

import httpx
from httpx import Timeout
from loguru import logger

# https://openlibrary.org/api/books?bibkeys=ISBN%3A0201558025&format=json&jscmd=data
BASE_URL = "https://openlibrary.org/api/books"


class BooksApi:
    books_timeout = Timeout(timeout=10.0)

    async def fetch_book_details(self, isbn: str) -> Optional[Mapping[str, Any]]:
        book_params = {"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"}
        async with httpx.AsyncClient(timeout=BooksApi.books_timeout) as client:
            resp = await client.get(BASE_URL, params=book_params)
            if resp.is_success:
                resp_json = resp.json()
                if resp_json:
                    book = resp_json.get(f"ISBN:{isbn}", None)
                    book["isbn"] = isbn
                    return book

            logger.info(" No record found for ISBN {}", isbn)
            return None
