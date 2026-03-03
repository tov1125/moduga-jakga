"""책 디자인(Design) API 엔드포인트 테스트.

표지 생성, 템플릿 조회, 레이아웃 미리보기에 대한 단위 테스트를 제공합니다.
- POST /api/v1/design/cover/generate (표지 생성)
- GET /api/v1/design/cover/templates (템플릿 조회)
- POST /api/v1/design/layout/preview (레이아웃 미리보기)
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestGenerateCover:
    """POST /api/v1/design/cover/generate 테스트."""

    @patch("app.api.v1.design.DesignService")
    def test_표지_정상_생성(
        self,
        mock_design_cls: MagicMock,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """표지를 정상적으로 생성한다."""
        mock_service = MagicMock()
        mock_service.generate_cover = AsyncMock(
            return_value={
                "image_url": "https://example.com/cover.png",
                "prompt_used": "에세이 미니멀 표지",
                "style": "minimalist",
            }
        )
        mock_design_cls.return_value = mock_service

        response = client.post(
            "/api/v1/design/cover/generate",
            headers=auth_headers,
            json={
                "book_title": "나의 첫 에세이",
                "author_name": "테스트 작가",
                "genre": "essay",
                "style": "minimalist",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "image_url" in data

    @patch("app.api.v1.design.DesignService")
    def test_표지_생성_서비스_오류_시_500(
        self,
        mock_design_cls: MagicMock,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """디자인 서비스 오류 시 500 에러를 반환한다."""
        mock_service = MagicMock()
        mock_service.generate_cover = AsyncMock(
            side_effect=Exception("이미지 생성 실패")
        )
        mock_design_cls.return_value = mock_service

        response = client.post(
            "/api/v1/design/cover/generate",
            headers=auth_headers,
            json={
                "book_title": "테스트",
                "author_name": "작가",
                "genre": "essay",
                "style": "minimalist",
            },
        )

        assert response.status_code == 500

    def test_미인증_표지_생성_거부(
        self,
        client: TestClient,
    ) -> None:
        """인증 없이 표지 생성 시 401 에러를 반환한다."""
        response = client.post(
            "/api/v1/design/cover/generate",
            json={
                "book_title": "테스트",
                "author_name": "작가",
                "genre": "essay",
                "style": "minimalist",
            },
        )
        assert response.status_code == 401


class TestListTemplates:
    """GET /api/v1/design/cover/templates 테스트."""

    def test_템플릿_목록_정상_조회(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """표지 템플릿 목록을 정상적으로 조회한다."""
        response = client.get(
            "/api/v1/design/cover/templates",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert "total" in data
        assert data["total"] > 0

    def test_템플릿에_필수_필드_포함(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """템플릿 목록의 각 항목에 필수 필드가 포함되어 있다."""
        response = client.get(
            "/api/v1/design/cover/templates",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        for template in data["templates"]:
            assert "id" in template
            assert "name" in template
            assert "genre" in template
            assert "style" in template

    def test_미인증_템플릿_조회_거부(
        self,
        client: TestClient,
    ) -> None:
        """인증 없이 템플릿 조회 시 401 에러를 반환한다."""
        response = client.get("/api/v1/design/cover/templates")
        assert response.status_code == 401


class TestPreviewLayout:
    """POST /api/v1/design/layout/preview 테스트."""

    @patch("app.api.v1.design.DesignService")
    def test_레이아웃_미리보기_성공(
        self,
        mock_design_cls: MagicMock,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
        sample_book: dict[str, Any],
    ) -> None:
        """레이아웃 미리보기를 정상적으로 생성한다."""
        book_id = sample_book["id"]

        books_mock = MagicMock()
        books_mock.select.return_value = books_mock
        books_mock.eq.return_value = books_mock
        books_mock.execute.return_value = MagicMock(data=[{"id": book_id}])

        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "books":
                return books_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        mock_service = MagicMock()
        mock_service.generate_layout_preview = AsyncMock(
            return_value=MagicMock(
                preview_url="https://example.com/layout.png",
                total_pages=120,
                page_size="A5",
            )
        )
        mock_design_cls.return_value = mock_service

        response = client.post(
            "/api/v1/design/layout/preview",
            headers=auth_headers,
            json={
                "book_id": book_id,
                "page_size": "A5",
                "font_size": 11.0,
                "line_spacing": 1.6,
            },
        )

        assert response.status_code == 200

    def test_존재하지_않는_도서_레이아웃_요청_시_404(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
    ) -> None:
        """존재하지 않는 도서의 레이아웃 요청 시 404 에러를 반환한다."""
        books_mock = MagicMock()
        books_mock.select.return_value = books_mock
        books_mock.eq.return_value = books_mock
        books_mock.execute.return_value = MagicMock(data=[])

        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "books":
                return books_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        response = client.post(
            "/api/v1/design/layout/preview",
            headers=auth_headers,
            json={
                "book_id": "nonexistent-book",
                "page_size": "A5",
            },
        )

        assert response.status_code == 404

    def test_미인증_레이아웃_거부(
        self,
        client: TestClient,
    ) -> None:
        """인증 없이 레이아웃 미리보기 요청 시 401 에러를 반환한다."""
        response = client.post(
            "/api/v1/design/layout/preview",
            json={"book_id": "test", "page_size": "A5"},
        )
        assert response.status_code == 401
