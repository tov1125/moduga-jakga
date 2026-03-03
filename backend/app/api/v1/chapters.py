"""
챕터 CRUD API 엔드포인트
도서 내 챕터의 생성, 조회, 수정, 삭제를 처리합니다.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.api.deps import get_current_user, get_supabase
from app.models.base import TABLE_BOOKS, TABLE_CHAPTERS
from app.schemas.chapter import (
    ChapterCreate,
    ChapterListResponse,
    ChapterResponse,
    ChapterUpdate,
)

router = APIRouter()


async def _verify_book_ownership(
    book_id: str,
    user_id: str,
    supabase: Client,
) -> None:
    """도서 소유권을 검증합니다. 소유자가 아니면 404 예외를 발생시킵니다."""
    response = (
        supabase.table(TABLE_BOOKS)
        .select("id")
        .eq("id", book_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="도서를 찾을 수 없거나 접근 권한이 없습니다.",
        )


def _build_chapter_response(chapter: dict[str, Any]) -> ChapterResponse:
    """챕터 데이터를 응답 스키마로 변환합니다."""
    return ChapterResponse(
        id=chapter["id"],
        book_id=chapter["book_id"],
        title=chapter["title"],
        content=chapter.get("content", ""),
        order=chapter.get("order", 1),
        status=chapter["status"],
        word_count=chapter.get("word_count", 0),
        created_at=str(chapter["created_at"]),
        updated_at=str(chapter["updated_at"]),
    )


@router.get(
    "/books/{book_id}/chapters",
    response_model=ChapterListResponse,
    summary="챕터 목록 조회",
)
async def list_chapters(
    book_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> ChapterListResponse:
    """특정 도서의 챕터 목록을 순서대로 반환합니다."""
    await _verify_book_ownership(book_id, current_user["id"], supabase)

    response = (
        supabase.table(TABLE_CHAPTERS)
        .select("*")
        .eq("book_id", book_id)
        .order("order", desc=False)
        .execute()
    )

    chapters = [_build_chapter_response(ch) for ch in response.data]
    return ChapterListResponse(chapters=chapters, total=len(chapters))


@router.post(
    "/books/{book_id}/chapters",
    response_model=ChapterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="챕터 생성",
)
async def create_chapter(
    book_id: str,
    request: ChapterCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> ChapterResponse:
    """도서에 새 챕터를 추가합니다."""
    await _verify_book_ownership(book_id, current_user["id"], supabase)

    # 글자 수 계산
    word_count = len(request.content.replace(" ", "").replace("\n", ""))

    chapter_data = {
        "book_id": book_id,
        "title": request.title,
        "content": request.content,
        "order": request.order,
        "status": "draft",
        "word_count": word_count,
    }

    response = supabase.table(TABLE_CHAPTERS).insert(chapter_data).execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="챕터 생성에 실패했습니다.",
        )

    # 도서의 챕터 수 업데이트
    chapter_count_resp = (
        supabase.table(TABLE_CHAPTERS)
        .select("id", count="exact")
        .eq("book_id", book_id)
        .execute()
    )
    new_count = chapter_count_resp.count or 0
    supabase.table(TABLE_BOOKS).update({"chapter_count": new_count}).eq("id", book_id).execute()

    return _build_chapter_response(response.data[0])


@router.get(
    "/books/{book_id}/chapters/{chapter_id}",
    response_model=ChapterResponse,
    summary="챕터 상세 조회",
)
async def get_chapter(
    book_id: str,
    chapter_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> ChapterResponse:
    """특정 챕터의 상세 정보를 반환합니다."""
    await _verify_book_ownership(book_id, current_user["id"], supabase)

    response = (
        supabase.table(TABLE_CHAPTERS)
        .select("*")
        .eq("id", chapter_id)
        .eq("book_id", book_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="챕터를 찾을 수 없습니다.",
        )

    return _build_chapter_response(response.data[0])


@router.patch(
    "/books/{book_id}/chapters/{chapter_id}",
    response_model=ChapterResponse,
    summary="챕터 수정",
)
async def update_chapter(
    book_id: str,
    chapter_id: str,
    request: ChapterUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> ChapterResponse:
    """챕터 내용을 수정합니다."""
    await _verify_book_ownership(book_id, current_user["id"], supabase)

    # 챕터 조회
    existing = (
        supabase.table(TABLE_CHAPTERS)
        .select("*")
        .eq("id", chapter_id)
        .eq("book_id", book_id)
        .execute()
    )

    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="챕터를 찾을 수 없습니다.",
        )

    # None이 아닌 필드만 업데이트
    update_data: dict[str, Any] = {}
    if request.title is not None:
        update_data["title"] = request.title
    if request.content is not None:
        update_data["content"] = request.content
        update_data["word_count"] = len(
            request.content.replace(" ", "").replace("\n", "")
        )
    if request.order is not None:
        update_data["order"] = request.order
    if request.status is not None:
        update_data["status"] = request.status.value

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 내용이 없습니다.",
        )

    response = (
        supabase.table(TABLE_CHAPTERS)
        .update(update_data)
        .eq("id", chapter_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="챕터 수정에 실패했습니다.",
        )

    # 도서 전체 글자 수 재계산
    all_chapters = (
        supabase.table(TABLE_CHAPTERS)
        .select("word_count")
        .eq("book_id", book_id)
        .execute()
    )
    total_words = sum(ch.get("word_count", 0) for ch in all_chapters.data)
    supabase.table(TABLE_BOOKS).update({"word_count": total_words}).eq("id", book_id).execute()

    return _build_chapter_response(response.data[0])


@router.delete(
    "/books/{book_id}/chapters/{chapter_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="챕터 삭제",
)
async def delete_chapter(
    book_id: str,
    chapter_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> None:
    """챕터를 삭제합니다."""
    await _verify_book_ownership(book_id, current_user["id"], supabase)

    # 챕터 존재 확인
    existing = (
        supabase.table(TABLE_CHAPTERS)
        .select("id")
        .eq("id", chapter_id)
        .eq("book_id", book_id)
        .execute()
    )

    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="챕터를 찾을 수 없습니다.",
        )

    # 챕터 삭제
    supabase.table(TABLE_CHAPTERS).delete().eq("id", chapter_id).execute()

    # 도서 챕터 수 업데이트
    chapter_count_resp = (
        supabase.table(TABLE_CHAPTERS)
        .select("id", count="exact")
        .eq("book_id", book_id)
        .execute()
    )
    new_count = chapter_count_resp.count or 0
    supabase.table(TABLE_BOOKS).update({"chapter_count": new_count}).eq("id", book_id).execute()
