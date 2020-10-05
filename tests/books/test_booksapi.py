from fastapi_todos.books.api import BooksApi
import pytest


@pytest.mark.asyncio
async def test_booksapi(printer):
    booksapi = BooksApi()
    book = await booksapi.fetch_book_details("0201558025")
    printer("Fetching Book  {}".format(book))
    assert book["title"] == "Concrete mathematics"