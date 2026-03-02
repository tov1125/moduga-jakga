"""
도서 디자인 서비스 모듈
DALL-E를 활용한 표지 생성과 Typst 기반 내지 조판을 제공합니다.
"""

import logging
import os
import subprocess
import tempfile
from typing import Any

from openai import AsyncOpenAI
from supabase import Client

from app.core.config import Settings
from app.models.base import TABLE_CHAPTERS
from app.schemas.book import Genre
from app.schemas.design import (
    CoverGenerateResponse,
    CoverStyle,
    LayoutPreviewResponse,
    PageSize,
)

logger = logging.getLogger(__name__)

# 표지 스타일별 DALL-E 프롬프트 키워드
STYLE_KEYWORDS: dict[str, str] = {
    CoverStyle.MINIMALIST.value: "minimalist design, clean layout, lots of white space, elegant typography",
    CoverStyle.ILLUSTRATED.value: "hand-drawn illustration, artistic, warm colors, detailed artwork",
    CoverStyle.PHOTOGRAPHIC.value: "photographic, cinematic lighting, realistic, high quality",
    CoverStyle.TYPOGRAPHY.value: "bold typography, creative text layout, font art, typographic design",
    CoverStyle.ABSTRACT.value: "abstract art, geometric shapes, modern design, contemporary",
}

# 장르별 DALL-E 프롬프트 키워드
GENRE_KEYWORDS: dict[str, str] = {
    Genre.ESSAY.value: "peaceful, contemplative, nature-inspired, subtle colors",
    Genre.NOVEL.value: "dramatic, atmospheric, storytelling, evocative",
    Genre.POEM.value: "lyrical, delicate, ethereal, soft tones",
    Genre.AUTOBIOGRAPHY.value: "personal, timeless, classic, warm",
    Genre.CHILDREN.value: "colorful, playful, whimsical, cheerful, cartoon-style",
    Genre.NON_FICTION.value: "professional, informative, structured, clean",
    Genre.OTHER.value: "creative, unique, eye-catching",
}

# Typst 내지 레이아웃 템플릿
TYPST_TEMPLATE = """
#set page(
  paper: "{page_size}",
  margin: (
    top: {margin_top}mm,
    bottom: {margin_bottom}mm,
    left: {margin_left}mm,
    right: {margin_right}mm,
  ),
)

#set text(
  font: "Noto Sans CJK KR",
  size: {font_size}pt,
  lang: "ko",
)

#set par(
  leading: {line_spacing}em,
  justify: true,
)

// 목차
#outline(indent: 1em)
#pagebreak()

{content}
"""


class DesignService:
    """도서 디자인 서비스"""

    def __init__(self, settings: Settings) -> None:
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_cover(
        self,
        book_title: str,
        author_name: str,
        genre: Genre,
        style: CoverStyle = CoverStyle.MINIMALIST,
        description: str = "",
        color_scheme: str = "",
    ) -> CoverGenerateResponse:
        """
        DALL-E를 사용하여 도서 표지 이미지를 생성합니다.

        Args:
            book_title: 책 제목
            author_name: 저자 이름
            genre: 장르
            style: 표지 스타일
            description: 추가 설명
            color_scheme: 색상 테마

        Returns:
            생성된 표지 정보 (이미지 URL, 사용된 프롬프트, 스타일)
        """
        # DALL-E 프롬프트 구성
        prompt_parts = [
            "Book cover design for a Korean book.",
            f'Title: "{book_title}"',
            f'Author: "{author_name}"',
            STYLE_KEYWORDS.get(style.value, ""),
            GENRE_KEYWORDS.get(genre.value, ""),
        ]

        if description:
            prompt_parts.append(f"Theme: {description}")
        if color_scheme:
            prompt_parts.append(f"Color scheme: {color_scheme}")

        prompt_parts.extend([
            "Professional book cover, high quality, print-ready.",
            "Vertical orientation (portrait), suitable for book printing.",
            "No text overlapping, clear composition.",
        ])

        prompt = " ".join(prompt_parts)

        try:
            response = await self._client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792",  # 세로 비율 (표지 비율)
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url or ""

            return CoverGenerateResponse(
                image_url=image_url,
                prompt_used=prompt,
                style=style,
            )

        except Exception as e:
            logger.error(f"표지 생성 중 오류: {e}")
            raise

    async def generate_layout_preview(
        self,
        book_id: str,
        page_size: PageSize = PageSize.A5,
        font_size: float = 11.0,
        line_spacing: float = 1.6,
        margins: dict[str, float] | None = None,
        supabase: Client | None = None,
    ) -> LayoutPreviewResponse:
        """
        도서의 내지 레이아웃 미리보기를 생성합니다.
        Typst를 사용하여 PDF를 생성합니다.

        Args:
            book_id: 도서 ID
            page_size: 페이지 크기
            font_size: 본문 글꼴 크기 (pt)
            line_spacing: 줄간격 배율
            margins: 여백 설정 (mm)
            supabase: Supabase 클라이언트

        Returns:
            미리보기 정보 (미리보기 URL, 총 페이지 수, 페이지 크기)
        """
        if margins is None:
            margins = {"top": 20.0, "bottom": 20.0, "left": 20.0, "right": 15.0}

        # 챕터 내용 조회
        content_parts: list[str] = []
        if supabase:
            chapters_resp = (
                supabase.table(TABLE_CHAPTERS)
                .select("title, content, order")
                .eq("book_id", book_id)
                .order("order", desc=False)
                .execute()
            )

            for ch in chapters_resp.data:
                title = ch.get("title", "")
                text = ch.get("content", "")
                content_parts.append(f"= {title}\n\n{text}\n\n")

        content = "\n".join(content_parts) if content_parts else "// 내용이 없습니다."

        # 페이지 크기 매핑
        page_size_map: dict[str, str] = {
            PageSize.A5.value: "a5",
            PageSize.B5.value: "b5",
            PageSize.A4.value: "a4",
            PageSize.PAPERBACK.value: "us-letter",
        }
        typst_page_size = page_size_map.get(page_size.value, "a5")

        # Typst 소스 생성
        typst_source = TYPST_TEMPLATE.format(
            page_size=typst_page_size,
            margin_top=margins.get("top", 20.0),
            margin_bottom=margins.get("bottom", 20.0),
            margin_left=margins.get("left", 20.0),
            margin_right=margins.get("right", 15.0),
            font_size=font_size,
            line_spacing=line_spacing,
            content=content,
        )

        # Typst 컴파일
        try:
            preview_url, total_pages = await self._compile_typst(typst_source)
        except Exception as e:
            logger.warning(f"Typst 컴파일 실패 (폴백 사용): {e}")
            # 페이지 수 추정 (대략적 계산)
            total_chars = sum(len(part) for part in content_parts)
            # A5 기준 한 페이지에 약 800자
            estimated_pages = max(1, total_chars // 800)
            preview_url = ""
            total_pages = estimated_pages

        return LayoutPreviewResponse(
            preview_url=preview_url,
            total_pages=total_pages,
            page_size=page_size,
        )

    async def _compile_typst(self, source: str) -> tuple[str, int]:
        """
        Typst 소스를 PDF로 컴파일합니다.

        Args:
            source: Typst 소스 코드

        Returns:
            (생성된 PDF 경로, 총 페이지 수) 튜플
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            src_path = os.path.join(tmp_dir, "book.typ")
            pdf_path = os.path.join(tmp_dir, "book.pdf")

            # Typst 소스 저장
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(source)

            # Typst 컴파일 실행
            result = subprocess.run(
                ["typst", "compile", src_path, pdf_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                raise RuntimeError(f"Typst 컴파일 오류: {result.stderr}")

            # 페이지 수 확인 (Typst 출력에서 추출하거나 PDF에서 계산)
            total_pages = self._count_pdf_pages(pdf_path)

            # 실제 서비스에서는 파일을 스토리지에 업로드하고 URL 반환
            # 여기서는 로컬 경로를 반환
            return pdf_path, total_pages

    def _count_pdf_pages(self, pdf_path: str) -> int:
        """
        PDF 파일의 페이지 수를 반환합니다.

        Args:
            pdf_path: PDF 파일 경로

        Returns:
            페이지 수
        """
        try:
            with open(pdf_path, "rb") as f:
                content = f.read()
                # 간단한 PDF 페이지 수 추정 (/Page 객체 수 카운팅)
                page_count = content.count(b"/Type /Page") - content.count(b"/Type /Pages")
                return max(1, page_count)
        except Exception:
            return 1
