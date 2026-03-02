"""
출판/내보내기 API 엔드포인트
도서 내보내기(DOCX, PDF, EPUB) 생성, 상태 조회, 다운로드를 처리합니다.
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from supabase import Client

from app.api.deps import get_current_user, get_supabase
from app.core.config import Settings, get_settings
from app.models.base import TABLE_BOOKS, TABLE_EXPORTS
from app.schemas.publishing import ExportRequest, ExportResponse, ExportStatus, ExportStatusEnum
from app.services.publishing_service import PublishingService

router = APIRouter()


@router.post(
    "/export",
    response_model=ExportResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="도서 내보내기",
)
async def export_book(
    request: ExportRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
    supabase: Client = Depends(get_supabase),
) -> ExportResponse:
    """
    도서를 지정된 형식(DOCX, PDF, EPUB)으로 내보냅니다.
    비동기 처리되며, 내보내기 ID로 상태를 추적할 수 있습니다.
    """
    # 도서 소유권 확인
    book_resp = (
        supabase.table(TABLE_BOOKS)
        .select("*")
        .eq("id", request.book_id)
        .eq("user_id", current_user["id"])
        .execute()
    )
    if not book_resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="도서를 찾을 수 없습니다.",
        )

    # 내보내기 레코드 생성
    export_id = str(uuid.uuid4())
    export_data = {
        "id": export_id,
        "book_id": request.book_id,
        "user_id": current_user["id"],
        "format": request.format.value,
        "status": ExportStatusEnum.PENDING.value,
        "progress": 0.0,
    }

    export_resp = supabase.table(TABLE_EXPORTS).insert(export_data).execute()
    if not export_resp.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="내보내기 요청 생성에 실패했습니다.",
        )

    # 비동기 내보내기 처리 시작 (백그라운드 태스크)
    publishing_service = PublishingService(settings=settings)
    try:
        await publishing_service.start_export(
            export_id=export_id,
            book_data=book_resp.data[0],
            export_format=request.format,
            page_size=request.page_size,
            include_cover=request.include_cover,
            include_toc=request.include_toc,
            accessibility_tags=request.accessibility_tags,
            supabase=supabase,
        )
    except Exception as e:
        # 내보내기 시작 실패 시 상태 업데이트
        supabase.table(TABLE_EXPORTS).update({
            "status": ExportStatusEnum.FAILED.value,
            "error_message": str(e),
        }).eq("id", export_id).execute()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"내보내기 시작에 실패했습니다: {str(e)}",
        ) from e

    return ExportResponse(
        export_id=export_id,
        book_id=request.book_id,
        format=request.format,
        status=ExportStatusEnum.PROCESSING,
        created_at=str(export_resp.data[0]["created_at"]),
    )


@router.get(
    "/export/{export_id}",
    response_model=ExportStatus,
    summary="내보내기 상태 조회",
)
async def get_export_status(
    export_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> ExportStatus:
    """내보내기 작업의 현재 상태를 조회합니다."""
    response = (
        supabase.table(TABLE_EXPORTS)
        .select("*")
        .eq("id", export_id)
        .eq("user_id", current_user["id"])
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="내보내기 작업을 찾을 수 없습니다.",
        )

    export_data = response.data[0]
    return ExportStatus(
        export_id=export_data["id"],
        book_id=export_data["book_id"],
        format=export_data["format"],
        status=export_data["status"],
        progress=export_data.get("progress", 0.0),
        error_message=export_data.get("error_message"),
        created_at=str(export_data["created_at"]),
    )


@router.get(
    "/download/{export_id}",
    summary="내보내기 파일 다운로드",
)
async def download_export(
    export_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> FileResponse:
    """완료된 내보내기 파일을 다운로드합니다."""
    response = (
        supabase.table(TABLE_EXPORTS)
        .select("*")
        .eq("id", export_id)
        .eq("user_id", current_user["id"])
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="내보내기 작업을 찾을 수 없습니다.",
        )

    export_data = response.data[0]

    if export_data["status"] != ExportStatusEnum.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="내보내기가 아직 완료되지 않았습니다.",
        )

    file_path = export_data.get("file_path")
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="내보내기 파일을 찾을 수 없습니다.",
        )

    # MIME 타입 결정
    format_mime_map: dict[str, str] = {
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pdf": "application/pdf",
        "epub": "application/epub+zip",
    }
    media_type = format_mime_map.get(export_data["format"], "application/octet-stream")

    # 파일명 생성
    book_resp = supabase.table(TABLE_BOOKS).select("title").eq("id", export_data["book_id"]).execute()
    book_title = book_resp.data[0]["title"] if book_resp.data else "book"
    filename = f"{book_title}.{export_data['format']}"

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename,
    )
