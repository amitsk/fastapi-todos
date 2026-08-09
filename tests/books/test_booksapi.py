import httpx
import pytest
import respx

from fastapi_todos.books.api import BASE_URL, BooksApi

ISBN = "0201558025"
BOOK_PAYLOAD = {
    "url": "http://openlibrary.org/books/OL1429049M/Concrete_mathematics",
    "title": "Concrete mathematics",
    "subtitle": "a foundation for computer science",
    "authors": [
        {
            "url": "http://openlibrary.org/authors/OL720958A/Ronald_L._Graham",
            "name": "Ronald L. Graham",
        }
    ],
    "publishers": [{"name": "Addison-Wesley"}],
    "publish_date": "1994",
    "subjects": [
        {
            "name": "Computer science",
            "url": "https://openlibrary.org/subjects/computer_science",
        }
    ],
    "identifiers": {"isbn_10": [ISBN], "openlibrary": ["OL1429049M"]},
}


@pytest.mark.asyncio
@respx.mock
async def test_fetch_book_details_success(printer):
    route = respx.get(BASE_URL).mock(
        return_value=httpx.Response(
            200,
            json={f"ISBN:{ISBN}": BOOK_PAYLOAD},
        )
    )

    booksapi = BooksApi()
    book = await booksapi.fetch_book_details(ISBN)

    printer(f"Fetching Book  {book}")
    assert route.called
    assert book is not None
    assert book["title"] == "Concrete mathematics"
    assert book["isbn"] == ISBN


@pytest.mark.asyncio
@respx.mock
async def test_fetch_book_details_not_found():
    respx.get(BASE_URL).mock(return_value=httpx.Response(200, json={}))

    booksapi = BooksApi()
    book = await booksapi.fetch_book_details("0000000000")

    assert book is None


@pytest.mark.asyncio
@respx.mock
async def test_fetch_book_details_http_error():
    respx.get(BASE_URL).mock(return_value=httpx.Response(503, text="unavailable"))

    booksapi = BooksApi()
    book = await booksapi.fetch_book_details(ISBN)

    assert book is None
