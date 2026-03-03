"""
도서 관련 Pydantic 스키마
도서 생성, 수정, 응답 스키마를 정의합니다.
"""

from enum import Enum

from pydantic import Field, StrictBool, StrictInt, StrictStr

from app.schemas.base import StrictBaseModel


class Genre(str, Enum):
    """장르 열거형"""
    ESSAY = "essay"                   # 수필/에세이
    NOVEL = "novel"                   # 소설
    POEM = "poem"                     # 시
    AUTOBIOGRAPHY = "autobiography"   # 자서전
    CHILDREN = "children"             # 동화
    NON_FICTION = "non_fiction"        # 논픽션
    OTHER = "other"                   # 기타


class BookStatus(str, Enum):
    """도서 상태 열거형"""
    DRAFT = "draft"           # 초안 작성 중
    WRITING = "writing"       # 집필 중
    EDITING = "editing"       # 편집 중
    DESIGNING = "designing"   # 디자인 중
    COMPLETED = "completed"   # 완성됨
    PUBLISHED = "published"   # 출판됨


class BookCreate(StrictBaseModel):
    """도서 생성 요청 스키마"""
    title: StrictStr = Field(..., min_length=1, max_length=200)
    genre: Genre
    description: StrictStr = Field(default="", max_length=2000)
    target_audience: StrictStr = Field(default="", max_length=200)


class BookUpdate(StrictBaseModel):
    """도서 수정 요청 스키마"""
    title: StrictStr | None = Field(default=None, min_length=1, max_length=200)
    genre: Genre | None = None
    description: StrictStr | None = Field(default=None, max_length=2000)
    target_audience: StrictStr | None = Field(default=None, max_length=200)
    status: BookStatus | None = None


class BookResponse(StrictBaseModel):
    """도서 응답 스키마"""
    id: StrictStr
    user_id: StrictStr
    title: StrictStr
    genre: Genre
    description: StrictStr
    target_audience: StrictStr
    status: BookStatus
    chapter_count: StrictInt
    word_count: StrictInt
    created_at: StrictStr
    updated_at: StrictStr


class BookListResponse(StrictBaseModel):
    """도서 목록 응답 스키마 (페이지네이션 포함)"""
    success: StrictBool = True
    data: list[BookResponse]
    total: StrictInt
    page: StrictInt
    page_size: StrictInt
    total_pages: StrictInt
