"""
디자인 관련 Pydantic 스키마
표지 생성, 템플릿, 내지 레이아웃 스키마를 정의합니다.
"""

from enum import Enum

from pydantic import StrictFloat, StrictInt, StrictStr

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
    book_title: StrictStr
    author_name: StrictStr
    genre: Genre
    style: CoverStyle = CoverStyle.MINIMALIST
    description: StrictStr = ""         # 표지에 대한 추가 설명
    color_scheme: StrictStr = ""        # 선호 색상 (예: "따뜻한 톤", "파란색 계열")


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
    font_size: StrictFloat = 11.0       # 본문 글꼴 크기 (pt)
    line_spacing: StrictFloat = 1.6     # 줄간격 배율
    margin_top: StrictFloat = 20.0      # 상단 여백 (mm)
    margin_bottom: StrictFloat = 20.0   # 하단 여백 (mm)
    margin_left: StrictFloat = 20.0     # 좌측 여백 (mm)
    margin_right: StrictFloat = 15.0    # 우측 여백 (mm)


class LayoutPreviewResponse(StrictBaseModel):
    """내지 레이아웃 미리보기 응답 스키마"""
    preview_url: StrictStr              # 미리보기 PDF/이미지 URL
    total_pages: StrictInt              # 예상 총 페이지 수
    page_size: PageSize
