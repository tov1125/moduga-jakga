"""
편집 API 엔드포인트 테스트
교정, 문체 검사, 구조 검토, 전체 4단계 편집 테스트
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestProofread:
    """맞춤법/문법 교정 테스트"""

    def test_proofread_success(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_settings: MagicMock,
    ) -> None:
        """정상적인 교정 요청"""
        from app.schemas.editing import CorrectionItem, ProofreadResult, SeverityLevel

        mock_result = ProofreadResult(
            corrected_text="안녕하세요. 반갑습니다.",
            corrections=[
                CorrectionItem(
                    original="안녕하세여",
                    corrected="안녕하세요",
                    reason="맞춤법 오류",
                    position_start=0,
                    position_end=5,
                    severity=SeverityLevel.ERROR,
                ),
            ],
            total_corrections=1,
            accuracy_score=85.0,
        )

        with patch("app.api.v1.editing.EditingService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.proofread = AsyncMock(return_value=mock_result)
            mock_service_cls.return_value = mock_service

            response = client.post(
                "/api/v1/editing/proofread",
                headers=auth_headers,
                json={
                    "text": "안녕하세여. 반갑습니다.",
                    "check_spelling": True,
                    "check_grammar": True,
                    "check_punctuation": True,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total_corrections"] == 1
            assert data["accuracy_score"] == 85.0
            assert len(data["corrections"]) == 1

    def test_proofread_empty_text(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """빈 텍스트 교정 요청 시 400 에러"""
        response = client.post(
            "/api/v1/editing/proofread",
            headers=auth_headers,
            json={"text": "  "},
        )

        assert response.status_code == 400


class TestStyleCheck:
    """문체 일관성 검사 테스트"""

    def test_style_check_success(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_settings: MagicMock,
    ) -> None:
        """정상적인 문체 검사 요청"""
        from app.schemas.editing import SeverityLevel, StyleCheckResult, StyleIssue

        mock_result = StyleCheckResult(
            issues=[
                StyleIssue(
                    text_excerpt="이것은 매우 좋다.",
                    issue="구어체 사용",
                    suggestion="'이것은 매우 훌륭하다.'로 수정 권장",
                    severity=SeverityLevel.SUGGESTION,
                ),
            ],
            consistency_score=80.0,
            overall_feedback="전반적으로 양호하나 일부 구어체가 사용되었습니다.",
        )

        with patch("app.api.v1.editing.EditingService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.check_style = AsyncMock(return_value=mock_result)
            mock_service_cls.return_value = mock_service

            response = client.post(
                "/api/v1/editing/style-check",
                headers=auth_headers,
                json={
                    "text": "이것은 매우 좋다. 봄이 오면 꽃이 핀다.",
                    "genre": "essay",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["consistency_score"] == 80.0
            assert len(data["issues"]) == 1


class TestStructureReview:
    """구조 검토 테스트"""

    def test_structure_review_success(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_settings: MagicMock,
        mock_supabase: MagicMock,
        sample_book: dict[str, Any],
    ) -> None:
        """정상적인 구조 검토 요청"""
        from app.schemas.editing import StructureReviewResult

        # 도서 소유권 확인 모의
        books_mock = MagicMock()
        books_mock.select.return_value = books_mock
        books_mock.eq.return_value = books_mock
        books_mock.execute.return_value = MagicMock(data=[sample_book])

        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "books":
                return books_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        mock_result = StructureReviewResult(
            flow_score=75.0,
            organization_score=80.0,
            feedback=["챕터 간 연결이 양호합니다."],
            suggestions=["결론 챕터를 추가하세요."],
        )

        with patch("app.api.v1.editing.EditingService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.review_structure = AsyncMock(return_value=mock_result)
            mock_service_cls.return_value = mock_service

            response = client.post(
                "/api/v1/editing/structure-review",
                headers=auth_headers,
                json={
                    "book_id": "test-book-id-12345",
                    "chapters": ["첫 번째 챕터 내용", "두 번째 챕터 내용"],
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["flow_score"] == 75.0
            assert data["organization_score"] == 80.0


class TestFullReview:
    """전체 4단계 편집 테스트"""

    def test_full_review_no_chapters(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
        sample_book: dict[str, Any],
    ) -> None:
        """챕터가 없는 도서의 전체 편집 요청 시 400 에러"""
        books_mock = MagicMock()
        books_mock.select.return_value = books_mock
        books_mock.eq.return_value = books_mock
        books_mock.order.return_value = books_mock
        books_mock.execute.return_value = MagicMock(data=[sample_book])

        chapters_mock = MagicMock()
        chapters_mock.select.return_value = chapters_mock
        chapters_mock.eq.return_value = chapters_mock
        chapters_mock.order.return_value = chapters_mock
        chapters_mock.execute.return_value = MagicMock(data=[])

        original_side_effect = mock_supabase.table.side_effect

        call_count = {"books": 0}

        def table_mock(name: str) -> MagicMock:
            if name == "books":
                return books_mock
            if name == "chapters":
                return chapters_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        response = client.post(
            "/api/v1/editing/full-review",
            headers=auth_headers,
            json={
                "book_id": "test-book-id-12345",
            },
        )

        assert response.status_code == 400


class TestQualityReport:
    """품질 보고서 조회 테스트"""

    def test_get_report_not_found(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
        sample_book: dict[str, Any],
    ) -> None:
        """보고서가 없을 때 404 에러"""
        books_mock = MagicMock()
        books_mock.select.return_value = books_mock
        books_mock.eq.return_value = books_mock
        books_mock.execute.return_value = MagicMock(data=[sample_book])

        report_mock = MagicMock()
        report_mock.select.return_value = report_mock
        report_mock.eq.return_value = report_mock
        report_mock.order.return_value = report_mock
        report_mock.limit.return_value = report_mock
        report_mock.execute.return_value = MagicMock(data=[])

        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "books":
                return books_mock
            if name == "editing_reports":
                return report_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        response = client.get(
            "/api/v1/editing/report/test-book-id-12345",
            headers=auth_headers,
        )

        assert response.status_code == 404
