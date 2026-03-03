"""
도서 CRUD API 엔드포인트 테스트
도서 목록 조회, 생성, 상세 조회, 수정, 삭제 테스트
"""

from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient


class TestListBooks:
    """도서 목록 조회 테스트"""

    def test_list_books_empty(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """도서가 없을 때 빈 목록 반환"""
        response = client.get("/api/v1/books/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total"] == 0
        assert data["data"] == []
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] == 1

    def test_list_books_with_data(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
        sample_book: dict[str, Any],
    ) -> None:
        """도서가 있을 때 목록 반환"""
        books_mock = MagicMock()
        books_mock.select.return_value = books_mock
        books_mock.eq.return_value = books_mock
        books_mock.order.return_value = books_mock
        books_mock.range.return_value = books_mock
        books_mock.execute.return_value = MagicMock(data=[sample_book], count=1)

        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "books":
                return books_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        response = client.get("/api/v1/books/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total"] == 1
        assert data["data"][0]["title"] == "테스트 도서"
        assert data["page"] == 1

    def test_list_books_unauthenticated(self, client: TestClient) -> None:
        """인증 없이 도서 목록 조회 시도"""
        response = client.get("/api/v1/books/")
        assert response.status_code == 401


class TestCreateBook:
    """도서 생성 테스트"""

    def test_create_book_success(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
        sample_book: dict[str, Any],
    ) -> None:
        """정상적인 도서 생성"""
        insert_mock = MagicMock()
        insert_mock.insert.return_value = insert_mock
        insert_mock.execute.return_value = MagicMock(data=[sample_book])

        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "books":
                return insert_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        response = client.post(
            "/api/v1/books/",
            headers=auth_headers,
            json={
                "title": "테스트 도서",
                "genre": "essay",
                "description": "테스트용 에세이 도서입니다.",
                "target_audience": "일반 독자",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "테스트 도서"
        assert data["genre"] == "essay"
        assert data["status"] == "draft"

    def test_create_book_invalid_genre(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """잘못된 장르로 도서 생성 시도"""
        response = client.post(
            "/api/v1/books/",
            headers=auth_headers,
            json={
                "title": "테스트",
                "genre": "invalid_genre",
            },
        )
        assert response.status_code == 422


class TestGetBook:
    """도서 상세 조회 테스트"""

    def test_get_book_success(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
        sample_book: dict[str, Any],
    ) -> None:
        """정상적인 도서 조회"""
        select_mock = MagicMock()
        select_mock.select.return_value = select_mock
        select_mock.eq.return_value = select_mock
        select_mock.execute.return_value = MagicMock(data=[sample_book])

        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "books":
                return select_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        response = client.get(
            "/api/v1/books/test-book-id-12345",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-book-id-12345"

    def test_get_book_not_found(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
    ) -> None:
        """존재하지 않는 도서 조회"""
        select_mock = MagicMock()
        select_mock.select.return_value = select_mock
        select_mock.eq.return_value = select_mock
        select_mock.execute.return_value = MagicMock(data=[])

        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "books":
                return select_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        response = client.get(
            "/api/v1/books/non-existent-id",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestUpdateBook:
    """도서 수정 테스트"""

    def test_update_book_title(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
        sample_book: dict[str, Any],
    ) -> None:
        """도서 제목 수정"""
        updated_book = {**sample_book, "title": "수정된 도서 제목"}

        update_mock = MagicMock()
        update_mock.select.return_value = update_mock
        update_mock.update.return_value = update_mock
        update_mock.eq.return_value = update_mock
        update_mock.execute.return_value = MagicMock(data=[updated_book])

        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "books":
                return update_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        response = client.patch(
            "/api/v1/books/test-book-id-12345",
            headers=auth_headers,
            json={"title": "수정된 도서 제목"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "수정된 도서 제목"


class TestDeleteBook:
    """도서 삭제 테스트"""

    def test_delete_book_success(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
        sample_book: dict[str, Any],
    ) -> None:
        """정상적인 도서 삭제"""
        delete_mock = MagicMock()
        delete_mock.select.return_value = delete_mock
        delete_mock.delete.return_value = delete_mock
        delete_mock.eq.return_value = delete_mock
        delete_mock.execute.return_value = MagicMock(data=[sample_book])

        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "books":
                return delete_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        response = client.delete(
            "/api/v1/books/test-book-id-12345",
            headers=auth_headers,
        )

        assert response.status_code == 204
