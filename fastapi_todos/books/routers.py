from loguru import logger
from fastapi import APIRouter, Response, status

from fastapi.responses import ORJSONResponse

from fastapi import APIRouter, Response, status
from .models import Book
from .api import BooksApi

books_router = APIRouter()
books_api = BooksApi()

not_found_response = ORJSONResponse(
    status_code=404, content={"message": "Book not found"}
)


@books_router.get(
    "/{isbn}",
    tags=["books"],
    status_code=status.HTTP_200_OK,
    response_model=Book,
    response_class=ORJSONResponse,
)
async def get_book(isbn: str, response: Response):
    book = await books_api.fetch_book_details(isbn)
    if not book:
        return not_found_response
    else:
        return book
