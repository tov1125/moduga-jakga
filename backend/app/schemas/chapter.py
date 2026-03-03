"""
챕터 관련 Pydantic 스키마
챕터 생성, 수정, 응답 스키마를 정의합니다.
"""

from enum import Enum

from pydantic import Field, StrictInt, StrictStr

from app.schemas.base import StrictBaseModel


class ChapterStatus(str, Enum):
    """챕터 상태 열거형"""
    DRAFT = "draft"         # 초안
    WRITING = "writing"     # 작성 중
    COMPLETED = "completed" # 완료
    EDITING = "editing"     # 편집 중
    FINALIZED = "finalized" # 최종 확정


class ChapterCreate(StrictBaseModel):
    """챕터 생성 요청 스키마"""
    title: StrictStr = Field(..., min_length=1, max_length=200)
    order: StrictInt = Field(default=1, ge=1)
    content: StrictStr = Field(default="")


class ChapterUpdate(StrictBaseModel):
    """챕터 수정 요청 스키마"""
    title: StrictStr | None = Field(default=None, min_length=1, max_length=200)
    content: StrictStr | None = None
    order: StrictInt | None = Field(default=None, ge=1)
    status: ChapterStatus | None = None


class ChapterResponse(StrictBaseModel):
    """챕터 응답 스키마"""
    id: StrictStr
    book_id: StrictStr
    title: StrictStr
    content: StrictStr
    order: StrictInt
    status: ChapterStatus
    word_count: StrictInt
    created_at: StrictStr
    updated_at: StrictStr


class ChapterListResponse(StrictBaseModel):
    """챕터 목록 응답 스키마"""
    chapters: list[ChapterResponse]
    total: StrictInt
