"""
도서 CRUD API 엔드포인트
도서의 생성, 조회, 수정, 삭제를 처리합니다.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.api.deps import get_current_user, get_supabase
from app.models.base import TABLE_BOOKS
from app.schemas.book import BookCreate, BookListResponse, BookResponse, BookUpdate

router = APIRouter()


@router.get(
    "/",
    response_model=BookListResponse,
    summary="내 도서 목록 조회",
)
async def list_books(
    current_user: dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> BookListResponse:
    """현재 사용자의 도서 목록을 반환합니다."""
    response = (
        supabase.table(TABLE_BOOKS)
        .select("*")
        .eq("user_id", current_user["id"])
        .order("created_at", desc=True)
        .execute()
    )

    books = [
        BookResponse(
            id=book["id"],
            user_id=book["user_id"],
            title=book["title"],
            genre=book["genre"],
            description=book.get("description", ""),
            target_audience=book.get("target_audience", ""),
            status=book["status"],
            chapter_count=book.get("chapter_count", 0),
            word_count=book.get("word_count", 0),
            created_at=str(book["created_at"]),
            updated_at=str(book["updated_at"]),
        )
        for book in response.data
    ]

    return BookListResponse(books=books, total=len(books))


@router.post(
    "/",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="도서 생성",
)
async def create_book(
    request: BookCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> BookResponse:
    """새 도서를 생성합니다."""
    book_data = {
        "user_id": current_user["id"],
        "title": request.title,
        "genre": request.genre.value,
        "description": request.description,
        "target_audience": request.target_audience,
        "status": "draft",
        "chapter_count": 0,
        "word_count": 0,
    }

    response = supabase.table(TABLE_BOOKS).insert(book_data).execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="도서 생성에 실패했습니다.",
        )

    book = response.data[0]
    return BookResponse(
        id=book["id"],
        user_id=book["user_id"],
        title=book["title"],
        genre=book["genre"],
        description=book.get("description", ""),
        target_audience=book.get("target_audience", ""),
        status=book["status"],
        chapter_count=book.get("chapter_count", 0),
        word_count=book.get("word_count", 0),
        created_at=str(book["created_at"]),
        updated_at=str(book["updated_at"]),
    )


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    summary="도서 상세 조회",
)
async def get_book(
    book_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> BookResponse:
    """특정 도서의 상세 정보를 반환합니다."""
    response = (
        supabase.table(TABLE_BOOKS)
        .select("*")
        .eq("id", book_id)
        .eq("user_id", current_user["id"])
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="도서를 찾을 수 없습니다.",
        )

    book = response.data[0]
    return BookResponse(
        id=book["id"],
        user_id=book["user_id"],
        title=book["title"],
        genre=book["genre"],
        description=book.get("description", ""),
        target_audience=book.get("target_audience", ""),
        status=book["status"],
        chapter_count=book.get("chapter_count", 0),
        word_count=book.get("word_count", 0),
        created_at=str(book["created_at"]),
        updated_at=str(book["updated_at"]),
    )


@router.put(
    "/{book_id}",
    response_model=BookResponse,
    summary="도서 수정",
)
async def update_book(
    book_id: str,
    request: BookUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> BookResponse:
    """도서 정보를 수정합니다."""
    # 도서 소유권 확인
    existing = (
        supabase.table(TABLE_BOOKS)
        .select("id")
        .eq("id", book_id)
        .eq("user_id", current_user["id"])
        .execute()
    )
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="도서를 찾을 수 없습니다.",
        )

    # None이 아닌 필드만 업데이트
    update_data: dict[str, Any] = {}
    if request.title is not None:
        update_data["title"] = request.title
    if request.genre is not None:
        update_data["genre"] = request.genre.value
    if request.description is not None:
        update_data["description"] = request.description
    if request.target_audience is not None:
        update_data["target_audience"] = request.target_audience
    if request.status is not None:
        update_data["status"] = request.status.value

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 내용이 없습니다.",
        )

    response = (
        supabase.table(TABLE_BOOKS)
        .update(update_data)
        .eq("id", book_id)
        .eq("user_id", current_user["id"])
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="도서 수정에 실패했습니다.",
        )

    book = response.data[0]
    return BookResponse(
        id=book["id"],
        user_id=book["user_id"],
        title=book["title"],
        genre=book["genre"],
        description=book.get("description", ""),
        target_audience=book.get("target_audience", ""),
        status=book["status"],
        chapter_count=book.get("chapter_count", 0),
        word_count=book.get("word_count", 0),
        created_at=str(book["created_at"]),
        updated_at=str(book["updated_at"]),
    )


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="도서 삭제",
)
async def delete_book(
    book_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> None:
    """도서를 삭제합니다. 관련 챕터도 함께 삭제됩니다."""
    # 도서 소유권 확인
    existing = (
        supabase.table(TABLE_BOOKS)
        .select("id")
        .eq("id", book_id)
        .eq("user_id", current_user["id"])
        .execute()
    )
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="도서를 찾을 수 없습니다.",
        )

    # 도서 삭제 (CASCADE로 챕터도 함께 삭제됨)
    supabase.table(TABLE_BOOKS).delete().eq("id", book_id).execute()
