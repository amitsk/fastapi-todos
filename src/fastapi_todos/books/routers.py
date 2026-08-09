from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from .api import BooksApi
from .models import Book

books_router = APIRouter()
books_api = BooksApi()


@books_router.get(
    "/{isbn}",
    tags=["books"],
    status_code=status.HTTP_200_OK,
    response_model=Book,
    response_class=JSONResponse,
)
async def get_book(isbn: str) -> Book:
    book = await books_api.fetch_book_details(isbn)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return Book.model_validate(book)
