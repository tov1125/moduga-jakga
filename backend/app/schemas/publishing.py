"""
출판/내보내기 관련 Pydantic 스키마
도서 내보내기(DOCX, PDF, EPUB) 요청 및 상태 스키마를 정의합니다.
"""

from enum import Enum

from pydantic import StrictBool, StrictFloat, StrictStr

from app.schemas.base import StrictBaseModel
from app.schemas.design import PageSize


class ExportFormat(str, Enum):
    """내보내기 형식 열거형"""
    DOCX = "docx"
    PDF = "pdf"
    EPUB = "epub"


class ExportStatusEnum(str, Enum):
    """내보내기 상태 열거형"""
    PENDING = "pending"         # 대기 중
    PROCESSING = "processing"   # 처리 중
    COMPLETED = "completed"     # 완료
    FAILED = "failed"           # 실패


class ExportRequest(StrictBaseModel):
    """내보내기 요청 스키마"""
    book_id: StrictStr
    format: ExportFormat
    page_size: PageSize = PageSize.A5
    include_cover: StrictBool = True          # 표지 포함 여부
    include_toc: StrictBool = True            # 목차 포함 여부
    accessibility_tags: StrictBool = True     # 접근성 태그 포함 여부 (EPUB)


class ExportStatus(StrictBaseModel):
    """내보내기 상태 조회 응답 스키마"""
    export_id: StrictStr
    book_id: StrictStr
    format: ExportFormat
    status: ExportStatusEnum
    progress: StrictFloat = 0.0               # 진행률 (0.0 ~ 100.0)
    error_message: StrictStr | None = None
    created_at: StrictStr


class ExportResponse(StrictBaseModel):
    """내보내기 완료 응답 스키마"""
    export_id: StrictStr
    book_id: StrictStr
    format: ExportFormat
    status: ExportStatusEnum
    download_url: StrictStr | None = None
    file_size_bytes: StrictStr | None = None
    created_at: StrictStr
