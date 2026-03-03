"""
디자인 API 엔드포인트
표지 생성, 템플릿 목록, 내지 레이아웃 미리보기를 처리합니다.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.api.deps import get_current_user, get_supabase
from app.core.config import Settings, get_settings
from app.models.base import TABLE_BOOKS
from app.schemas.book import Genre
from app.schemas.design import (
    CoverGenerateRequest,
    CoverGenerateResponse,
    CoverStyle,
    CoverTemplate,
    CoverTemplateListResponse,
    LayoutPreviewRequest,
    LayoutPreviewResponse,
)
from app.services.design_service import DesignService

router = APIRouter()

# 기본 표지 템플릿 목록
DEFAULT_TEMPLATES: list[CoverTemplate] = [
    CoverTemplate(
        id="tpl_essay_minimal",
        name="에세이 미니멀",
        genre=Genre.ESSAY,
        style=CoverStyle.MINIMALIST,
        preview_url="/static/templates/essay_minimal.png",
        description="깔끔하고 여백을 살린 에세이 표지",
    ),
    CoverTemplate(
        id="tpl_novel_illustrated",
        name="소설 일러스트",
        genre=Genre.NOVEL,
        style=CoverStyle.ILLUSTRATED,
        preview_url="/static/templates/novel_illustrated.png",
        description="분위기 있는 일러스트 소설 표지",
    ),
    CoverTemplate(
        id="tpl_poem_typography",
        name="시집 타이포",
        genre=Genre.POEM,
        style=CoverStyle.TYPOGRAPHY,
        preview_url="/static/templates/poem_typography.png",
        description="아름다운 타이포그래피 시집 표지",
    ),
    CoverTemplate(
        id="tpl_auto_photo",
        name="자서전 포토",
        genre=Genre.AUTOBIOGRAPHY,
        style=CoverStyle.PHOTOGRAPHIC,
        preview_url="/static/templates/auto_photo.png",
        description="사진 기반 자서전 표지",
    ),
    CoverTemplate(
        id="tpl_children_illustrated",
        name="동화 일러스트",
        genre=Genre.CHILDREN,
        style=CoverStyle.ILLUSTRATED,
        preview_url="/static/templates/children_illustrated.png",
        description="밝고 따뜻한 동화책 표지",
    ),
    CoverTemplate(
        id="tpl_abstract_general",
        name="추상 범용",
        genre=Genre.OTHER,
        style=CoverStyle.ABSTRACT,
        preview_url="/static/templates/abstract_general.png",
        description="모든 장르에 어울리는 추상적 표지",
    ),
]


@router.post(
    "/cover/generate",
    response_model=CoverGenerateResponse,
    summary="AI 표지 생성",
)
async def generate_cover(
    request: CoverGenerateRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> CoverGenerateResponse:
    """
    DALL-E를 사용하여 도서 표지 이미지를 생성합니다.
    장르, 스타일, 색상 테마를 기반으로 적합한 표지를 만듭니다.
    """
    if not request.book_title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="책 제목을 입력해주세요.",
        )

    design_service = DesignService(settings=settings)

    try:
        result = await design_service.generate_cover(
            book_title=request.book_title,
            author_name=request.author_name,
            genre=request.genre,
            style=request.style,
            description=request.description,
            color_scheme=request.color_scheme,
        )
        return result
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="표지 생성에 실패했습니다.",
        )


@router.get(
    "/cover/templates",
    response_model=CoverTemplateListResponse,
    summary="표지 템플릿 목록",
)
async def list_cover_templates(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> CoverTemplateListResponse:
    """사용 가능한 표지 템플릿 목록을 반환합니다."""
    return CoverTemplateListResponse(
        templates=DEFAULT_TEMPLATES,
        total=len(DEFAULT_TEMPLATES),
    )


@router.post(
    "/layout/preview",
    response_model=LayoutPreviewResponse,
    summary="내지 레이아웃 미리보기",
)
async def preview_layout(
    request: LayoutPreviewRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
    supabase: Client = Depends(get_supabase),
) -> LayoutPreviewResponse:
    """
    도서의 내지 레이아웃 미리보기를 생성합니다.
    페이지 크기, 글꼴, 여백 등을 설정하고 결과를 미리 볼 수 있습니다.
    """
    # 도서 소유권 확인
    book_resp = (
        supabase.table(TABLE_BOOKS)
        .select("id")
        .eq("id", request.book_id)
        .eq("user_id", current_user["id"])
        .execute()
    )
    if not book_resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="도서를 찾을 수 없습니다.",
        )

    design_service = DesignService(settings=settings)

    try:
        result = await design_service.generate_layout_preview(
            book_id=request.book_id,
            page_size=request.page_size,
            font_size=request.font_size,
            line_spacing=request.line_spacing,
            margins={
                "top": request.margin_top,
                "bottom": request.margin_bottom,
                "left": request.margin_left,
                "right": request.margin_right,
            },
            supabase=supabase,
        )
        return result
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="레이아웃 미리보기 생성에 실패했습니다.",
        )
