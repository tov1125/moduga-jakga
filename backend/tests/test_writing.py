"""
AI 글쓰기 API 엔드포인트 테스트
글 생성 (SSE 스트리밍), 재작성, 구조 제안 테스트
"""

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestGenerateText:
    """AI 글 생성 테스트"""

    def test_generate_text_sse_stream(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_settings: MagicMock,
    ) -> None:
        """SSE 스트리밍 글 생성"""
        async def mock_stream(*args: Any, **kwargs: Any) -> Any:
            for chunk in ["봄이 ", "오면 ", "꽃이 핍니다."]:
                yield chunk

        with patch("app.api.v1.writing.WritingService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.generate_stream = mock_stream
            mock_service_cls.return_value = mock_service

            response = client.post(
                "/api/v1/writing/generate",
                headers=auth_headers,
                json={
                    "genre": "essay",
                    "prompt": "봄날의 산책에 대해 써줘",
                    "max_tokens": 512,
                    "temperature": 0.7,
                },
            )

            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")

            # SSE 데이터 확인
            content = response.text
            assert "data:" in content

    def test_generate_text_empty_prompt(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """빈 프롬프트로 생성 요청 시 400 에러"""
        response = client.post(
            "/api/v1/writing/generate",
            headers=auth_headers,
            json={
                "genre": "essay",
                "prompt": "  ",
            },
        )

        assert response.status_code == 400

    def test_generate_text_unauthenticated(self, client: TestClient) -> None:
        """인증 없이 글 생성 요청"""
        response = client.post(
            "/api/v1/writing/generate",
            json={
                "genre": "essay",
                "prompt": "테스트",
            },
        )

        assert response.status_code == 401


class TestRewriteText:
    """구간 재작성 테스트"""

    def test_rewrite_success(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_settings: MagicMock,
    ) -> None:
        """정상적인 재작성 요청"""
        from app.schemas.writing import RewriteResponse

        mock_result = RewriteResponse(
            rewritten_text="개선된 봄날의 이야기입니다.",
            changes_summary="문장을 더 자연스럽게 수정했습니다.",
        )

        with patch("app.api.v1.writing.WritingService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.rewrite = AsyncMock(return_value=mock_result)
            mock_service_cls.return_value = mock_service

            response = client.post(
                "/api/v1/writing/rewrite",
                headers=auth_headers,
                json={
                    "original_text": "봄날의 이야기입니다.",
                    "instruction": "더 자연스럽게 수정해줘",
                    "genre": "essay",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "rewritten_text" in data
            assert "changes_summary" in data

    def test_rewrite_empty_text(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """빈 텍스트 재작성 요청 시 400 에러"""
        response = client.post(
            "/api/v1/writing/rewrite",
            headers=auth_headers,
            json={
                "original_text": "  ",
                "instruction": "수정해줘",
                "genre": "essay",
            },
        )

        assert response.status_code == 400


class TestSuggestStructure:
    """챕터 구조 제안 테스트"""

    def test_suggest_structure_success(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_settings: MagicMock,
    ) -> None:
        """정상적인 구조 제안 요청"""
        from app.schemas.writing import ChapterSuggestion, StructureResponse

        mock_result = StructureResponse(
            chapters=[
                ChapterSuggestion(
                    order=1,
                    title="서론: 봄의 시작",
                    description="봄이 오는 과정을 묘사합니다.",
                    estimated_pages=15,
                ),
                ChapterSuggestion(
                    order=2,
                    title="본론: 봄의 한가운데",
                    description="봄의 절정을 묘사합니다.",
                    estimated_pages=20,
                ),
            ],
            overall_summary="봄을 주제로 한 2장 에세이 구조",
        )

        with patch("app.api.v1.writing.WritingService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.suggest_structure = AsyncMock(return_value=mock_result)
            mock_service_cls.return_value = mock_service

            response = client.post(
                "/api/v1/writing/structure",
                headers=auth_headers,
                json={
                    "book_title": "봄날의 산책",
                    "genre": "essay",
                    "description": "봄에 대한 에세이",
                    "target_chapters": 2,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["chapters"]) == 2
            assert "overall_summary" in data

    def test_suggest_structure_empty_title(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """빈 제목으로 구조 제안 요청 시 400 에러"""
        response = client.post(
            "/api/v1/writing/structure",
            headers=auth_headers,
            json={
                "book_title": "  ",
                "genre": "essay",
                "description": "테스트",
            },
        )

        assert response.status_code == 400
