"""
출판/내보내기 API 엔드포인트 테스트
내보내기 생성, 상태 조회, 다운로드 테스트
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestExportBook:
    """도서 내보내기 테스트"""

    def test_export_book_success(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
        sample_book: dict[str, Any],
    ) -> None:
        """정상적인 도서 내보내기 요청"""
        books_mock = MagicMock()
        books_mock.select.return_value = books_mock
        books_mock.eq.return_value = books_mock
        books_mock.execute.return_value = MagicMock(data=[sample_book])

        export_data = {
            "id": "export-id-12345",
            "book_id": "test-book-id-12345",
            "user_id": "test-user-id-12345",
            "format": "pdf",
            "status": "pending",
            "progress": 0.0,
            "created_at": "2025-01-01T00:00:00+00:00",
        }
        exports_mock = MagicMock()
        exports_mock.insert.return_value = exports_mock
        exports_mock.update.return_value = exports_mock
        exports_mock.eq.return_value = exports_mock
        exports_mock.execute.return_value = MagicMock(data=[export_data])

        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "books":
                return books_mock
            if name == "exports":
                return exports_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        with patch("app.api.v1.publishing.PublishingService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.start_export = AsyncMock(return_value="/tmp/test.pdf")
            mock_service_cls.return_value = mock_service

            response = client.post(
                "/api/v1/publishing/export",
                headers=auth_headers,
                json={
                    "book_id": "test-book-id-12345",
                    "format": "pdf",
                    "page_size": "A5",
                    "include_cover": True,
                    "include_toc": True,
                    "accessibility_tags": True,
                },
            )

            assert response.status_code == 202
            data = response.json()
            assert data["format"] == "pdf"
            assert "export_id" in data

    def test_export_book_not_found(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
    ) -> None:
        """존재하지 않는 도서 내보내기 요청"""
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
            "/api/v1/publishing/export",
            headers=auth_headers,
            json={
                "book_id": "non-existent-id",
                "format": "pdf",
            },
        )

        assert response.status_code == 404

    def test_export_invalid_format(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """잘못된 내보내기 형식 요청"""
        response = client.post(
            "/api/v1/publishing/export",
            headers=auth_headers,
            json={
                "book_id": "test-book-id-12345",
                "format": "invalid_format",
            },
        )

        assert response.status_code == 422


class TestExportStatus:
    """내보내기 상태 조회 테스트"""

    def test_get_export_status_success(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
    ) -> None:
        """정상적인 상태 조회"""
        export_data = {
            "id": "export-id-12345",
            "book_id": "test-book-id-12345",
            "user_id": "test-user-id-12345",
            "format": "pdf",
            "status": "processing",
            "progress": 50.0,
            "error_message": None,
            "created_at": "2025-01-01T00:00:00+00:00",
        }

        exports_mock = MagicMock()
        exports_mock.select.return_value = exports_mock
        exports_mock.eq.return_value = exports_mock
        exports_mock.execute.return_value = MagicMock(data=[export_data])

        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "exports":
                return exports_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        response = client.get(
            "/api/v1/publishing/export/export-id-12345",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processing"
        assert data["progress"] == 50.0

    def test_get_export_status_not_found(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
    ) -> None:
        """존재하지 않는 내보내기 상태 조회"""
        exports_mock = MagicMock()
        exports_mock.select.return_value = exports_mock
        exports_mock.eq.return_value = exports_mock
        exports_mock.execute.return_value = MagicMock(data=[])

        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "exports":
                return exports_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        response = client.get(
            "/api/v1/publishing/export/non-existent-id",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestDownloadExport:
    """내보내기 파일 다운로드 테스트"""

    def test_download_not_completed(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
    ) -> None:
        """완료되지 않은 내보내기 다운로드 시도"""
        export_data = {
            "id": "export-id-12345",
            "book_id": "test-book-id-12345",
            "user_id": "test-user-id-12345",
            "format": "pdf",
            "status": "processing",
            "progress": 50.0,
            "file_path": None,
            "created_at": "2025-01-01T00:00:00+00:00",
        }

        exports_mock = MagicMock()
        exports_mock.select.return_value = exports_mock
        exports_mock.eq.return_value = exports_mock
        exports_mock.execute.return_value = MagicMock(data=[export_data])

        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "exports":
                return exports_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        response = client.get(
            "/api/v1/publishing/download/export-id-12345",
            headers=auth_headers,
        )

        assert response.status_code == 400


class TestPublishingService:
    """출판 서비스 유닛 테스트"""

    @pytest.mark.asyncio
    async def test_export_docx(self, mock_settings: MagicMock) -> None:
        """DOCX 내보내기 서비스 테스트"""
        from app.services.publishing_service import PublishingService

        service = PublishingService(settings=mock_settings)

        book_data = {
            "id": "test-book-id",
            "title": "테스트 도서",
            "description": "테스트 설명",
        }
        chapters = [
            {"title": "제1장", "content": "첫 번째 챕터 내용입니다.", "order": 1},
            {"title": "제2장", "content": "두 번째 챕터 내용입니다.", "order": 2},
        ]

        file_path = await service._export_docx(
            export_id="test-export-id",
            book_data=book_data,
            chapters=chapters,
            include_toc=True,
        )

        assert file_path.endswith(".docx")

        # 파일이 실제로 생성되었는지 확인
        import os

        assert os.path.exists(file_path)
        assert os.path.getsize(file_path) > 0

        # 정리
        os.remove(file_path)
