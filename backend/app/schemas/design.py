"""
디자인 관련 Pydantic 스키마
표지 생성, 템플릿, 내지 레이아웃 스키마를 정의합니다.
"""

from enum import Enum

from pydantic import Field, StrictFloat, StrictInt, StrictStr

from app.schemas.base import StrictBaseModel
from app.schemas.book import Genre


class CoverStyle(str, Enum):
    """표지 스타일 열거형"""
    MINIMALIST = "minimalist"       # 미니멀리즘
    ILLUSTRATED = "illustrated"     # 일러스트
    PHOTOGRAPHIC = "photographic"   # 사진 기반
    TYPOGRAPHY = "typography"       # 타이포그래피
    ABSTRACT = "abstract"           # 추상적


class PageSize(str, Enum):
    """페이지 크기 열거형"""
    A5 = "A5"                       # 148 x 210 mm
    B5 = "B5"                       # 176 x 250 mm
    A4 = "A4"                       # 210 x 297 mm
    PAPERBACK = "paperback"         # 127 x 203 mm (5 x 8 inch)


class CoverGenerateRequest(StrictBaseModel):
    """표지 생성 요청 스키마"""
    book_title: StrictStr = Field(..., min_length=1, max_length=200)
    author_name: StrictStr = Field(..., min_length=1, max_length=100)
    genre: Genre
    style: CoverStyle = CoverStyle.MINIMALIST
    description: StrictStr = Field(default="", max_length=1000)
    color_scheme: StrictStr = Field(default="", max_length=100)


class CoverGenerateResponse(StrictBaseModel):
    """표지 생성 응답 스키마"""
    image_url: StrictStr                # 생성된 표지 이미지 URL
    prompt_used: StrictStr              # DALL-E에 전달한 프롬프트
    style: CoverStyle


class CoverTemplate(StrictBaseModel):
    """표지 템플릿 스키마"""
    id: StrictStr
    name: StrictStr
    genre: Genre
    style: CoverStyle
    preview_url: StrictStr
    description: StrictStr


class CoverTemplateListResponse(StrictBaseModel):
    """표지 템플릿 목록 응답 스키마"""
    templates: list[CoverTemplate]
    total: StrictInt


class LayoutPreviewRequest(StrictBaseModel):
    """내지 레이아웃 미리보기 요청 스키마"""
    book_id: StrictStr
    page_size: PageSize = PageSize.A5
    font_size: StrictFloat = Field(default=11.0, ge=8.0, le=24.0)
    line_spacing: StrictFloat = Field(default=1.6, ge=1.0, le=3.0)
    margin_top: StrictFloat = Field(default=20.0, ge=5.0, le=50.0)
    margin_bottom: StrictFloat = Field(default=20.0, ge=5.0, le=50.0)
    margin_left: StrictFloat = Field(default=20.0, ge=5.0, le=50.0)
    margin_right: StrictFloat = Field(default=15.0, ge=5.0, le=50.0)


class LayoutPreviewResponse(StrictBaseModel):
    """내지 레이아웃 미리보기 응답 스키마"""
    preview_url: StrictStr              # 미리보기 PDF/이미지 URL
    total_pages: StrictInt              # 예상 총 페이지 수
    page_size: PageSize
