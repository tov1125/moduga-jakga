"""
챕터 CRUD API 엔드포인트 테스트
챕터 목록 조회, 생성, 수정, 삭제 테스트
"""

from typing import Any
from unittest.mock import MagicMock

from fastapi.testclient import TestClient


class TestListChapters:
    """챕터 목록 조회 테스트"""

    def test_list_chapters_success(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
        sample_chapter: dict[str, Any],
        sample_book: dict[str, Any],
    ) -> None:
        """도서의 챕터 목록 조회"""
        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "books":
                books_mock = MagicMock()
                books_mock.select.return_value = books_mock
                books_mock.eq.return_value = books_mock
                books_mock.execute.return_value = MagicMock(data=[sample_book])
                return books_mock
            if name == "chapters":
                chapters_mock = MagicMock()
                chapters_mock.select.return_value = chapters_mock
                chapters_mock.eq.return_value = chapters_mock
                chapters_mock.order.return_value = chapters_mock
                chapters_mock.execute.return_value = MagicMock(data=[sample_chapter])
                return chapters_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        response = client.get(
            "/api/v1/books/test-book-id-12345/chapters",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["chapters"]) == 1
        assert data["chapters"][0]["title"] == "제1장: 시작"

    def test_list_chapters_unauthenticated(self, client: TestClient) -> None:
        """인증 없이 챕터 목록 조회 시도"""
        response = client.get("/api/v1/books/test-book-id-12345/chapters")
        assert response.status_code == 401


class TestCreateChapter:
    """챕터 생성 테스트"""

    def test_create_chapter_success(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
        sample_chapter: dict[str, Any],
        sample_book: dict[str, Any],
    ) -> None:
        """정상적인 챕터 생성"""
        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "books":
                books_mock = MagicMock()
                books_mock.select.return_value = books_mock
                books_mock.update.return_value = books_mock
                books_mock.eq.return_value = books_mock
                books_mock.execute.return_value = MagicMock(data=[sample_book])
                return books_mock
            if name == "chapters":
                chapters_mock = MagicMock()
                chapters_mock.insert.return_value = chapters_mock
                chapters_mock.select.return_value = chapters_mock
                chapters_mock.eq.return_value = chapters_mock
                chapters_mock.execute.return_value = MagicMock(data=[sample_chapter])
                return chapters_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        response = client.post(
            "/api/v1/books/test-book-id-12345/chapters",
            headers=auth_headers,
            json={
                "title": "제1장: 시작",
                "content": "봄이 오면 산에 들에 진달래 꽃이 피고...",
                "order": 1,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "제1장: 시작"

    def test_create_chapter_invalid_type(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """잘못된 타입으로 챕터 생성 시도 (title에 int)"""
        response = client.post(
            "/api/v1/books/test-book-id-12345/chapters",
            headers=auth_headers,
            json={"title": 12345, "order": 1},
        )
        assert response.status_code == 422

    def test_create_chapter_book_not_found(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
    ) -> None:
        """존재하지 않는 도서에 챕터 생성 시 404 에러를 반환한다."""
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
            "/api/v1/books/nonexistent-book/chapters",
            headers=auth_headers,
            json={"title": "테스트 챕터"},
        )

        assert response.status_code == 404

    def test_create_chapter_unauthenticated(self, client: TestClient) -> None:
        """인증 없이 챕터 생성 시 401 에러를 반환한다."""
        response = client.post(
            "/api/v1/books/test-book-id-12345/chapters",
            json={"title": "테스트"},
        )
        assert response.status_code == 401


class TestGetChapter:
    """챕터 단건 조회 테스트"""

    def test_get_chapter_success(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
        sample_chapter: dict[str, Any],
        sample_book: dict[str, Any],
    ) -> None:
        """도서 내 챕터 상세 조회 — /books/{book_id}/chapters/{chapter_id} 경로."""
        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "books":
                books_mock = MagicMock()
                books_mock.select.return_value = books_mock
                books_mock.eq.return_value = books_mock
                books_mock.execute.return_value = MagicMock(data=[sample_book])
                return books_mock
            if name == "chapters":
                chapters_mock = MagicMock()
                chapters_mock.select.return_value = chapters_mock
                chapters_mock.eq.return_value = chapters_mock
                chapters_mock.execute.return_value = MagicMock(data=[sample_chapter])
                return chapters_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        response = client.get(
            f"/api/v1/books/{sample_book['id']}/chapters/{sample_chapter['id']}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_chapter["id"]
        assert data["title"] == sample_chapter["title"]

    def test_get_chapter_not_found(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
        sample_book: dict[str, Any],
    ) -> None:
        """존재하지 않는 챕터 조회 시 404 에러를 반환한다."""
        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "books":
                books_mock = MagicMock()
                books_mock.select.return_value = books_mock
                books_mock.eq.return_value = books_mock
                books_mock.execute.return_value = MagicMock(data=[sample_book])
                return books_mock
            if name == "chapters":
                chapters_mock = MagicMock()
                chapters_mock.select.return_value = chapters_mock
                chapters_mock.eq.return_value = chapters_mock
                chapters_mock.execute.return_value = MagicMock(data=[])
                return chapters_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        response = client.get(
            f"/api/v1/books/{sample_book['id']}/chapters/nonexistent-id",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_get_chapter_unauthenticated(self, client: TestClient) -> None:
        """인증 없이 챕터 조회 시 401 에러를 반환한다."""
        response = client.get("/api/v1/books/test-book-id-12345/chapters/test-id")
        assert response.status_code == 401


class TestUpdateChapter:
    """챕터 수정 테스트"""

    def test_update_chapter_success(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
        sample_chapter: dict[str, Any],
        sample_book: dict[str, Any],
    ) -> None:
        """챕터를 정상적으로 수정한다 — /books/{book_id}/chapters/{chapter_id} 경로."""
        updated = {**sample_chapter, "title": "수정된 제목"}
        original_side_effect = mock_supabase.table.side_effect
        call_count = {"chapters": 0}

        def table_mock(name: str) -> MagicMock:
            if name == "books":
                books_mock = MagicMock()
                books_mock.select.return_value = books_mock
                books_mock.update.return_value = books_mock
                books_mock.eq.return_value = books_mock
                books_mock.execute.return_value = MagicMock(data=[sample_book])
                return books_mock
            if name == "chapters":
                call_count["chapters"] += 1
                mock = MagicMock()
                mock.select.return_value = mock
                mock.eq.return_value = mock
                mock.update.return_value = mock
                if call_count["chapters"] <= 1:
                    mock.execute.return_value = MagicMock(data=[sample_chapter])
                else:
                    mock.execute.return_value = MagicMock(data=[updated])
                return mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        response = client.patch(
            f"/api/v1/books/{sample_book['id']}/chapters/{sample_chapter['id']}",
            headers=auth_headers,
            json={"title": "수정된 제목"},
        )

        assert response.status_code == 200

    def test_update_chapter_not_found(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
        sample_book: dict[str, Any],
    ) -> None:
        """존재하지 않는 챕터 수정 시 404 에러를 반환한다."""
        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "books":
                books_mock = MagicMock()
                books_mock.select.return_value = books_mock
                books_mock.eq.return_value = books_mock
                books_mock.execute.return_value = MagicMock(data=[sample_book])
                return books_mock
            if name == "chapters":
                chapters_mock = MagicMock()
                chapters_mock.select.return_value = chapters_mock
                chapters_mock.eq.return_value = chapters_mock
                chapters_mock.execute.return_value = MagicMock(data=[])
                return chapters_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        response = client.patch(
            f"/api/v1/books/{sample_book['id']}/chapters/nonexistent-id",
            headers=auth_headers,
            json={"title": "수정"},
        )

        assert response.status_code == 404

    def test_update_chapter_unauthenticated(self, client: TestClient) -> None:
        """인증 없이 챕터 수정 시 401 에러를 반환한다."""
        response = client.patch(
            "/api/v1/books/test-book-id-12345/chapters/test-id",
            json={"title": "수정"},
        )
        assert response.status_code == 401


class TestDeleteChapter:
    """챕터 삭제 테스트"""

    def test_delete_chapter_success(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
        sample_chapter: dict[str, Any],
        sample_book: dict[str, Any],
    ) -> None:
        """챕터를 정상적으로 삭제한다 — /books/{book_id}/chapters/{chapter_id} 경로."""
        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "books":
                books_mock = MagicMock()
                books_mock.select.return_value = books_mock
                books_mock.update.return_value = books_mock
                books_mock.eq.return_value = books_mock
                books_mock.execute.return_value = MagicMock(data=[sample_book])
                return books_mock
            if name == "chapters":
                mock = MagicMock()
                mock.select.return_value = mock
                mock.eq.return_value = mock
                mock.delete.return_value = mock
                mock.execute.return_value = MagicMock(data=[sample_chapter], count=0)
                return mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        response = client.delete(
            f"/api/v1/books/{sample_book['id']}/chapters/{sample_chapter['id']}",
            headers=auth_headers,
        )

        assert response.status_code == 204

    def test_delete_chapter_not_found(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_supabase: MagicMock,
        sample_book: dict[str, Any],
    ) -> None:
        """존재하지 않는 챕터 삭제 시 404 에러를 반환한다."""
        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "books":
                books_mock = MagicMock()
                books_mock.select.return_value = books_mock
                books_mock.eq.return_value = books_mock
                books_mock.execute.return_value = MagicMock(data=[sample_book])
                return books_mock
            if name == "chapters":
                chapters_mock = MagicMock()
                chapters_mock.select.return_value = chapters_mock
                chapters_mock.eq.return_value = chapters_mock
                chapters_mock.execute.return_value = MagicMock(data=[])
                return chapters_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        response = client.delete(
            f"/api/v1/books/{sample_book['id']}/chapters/nonexistent-id",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_delete_chapter_unauthenticated(self, client: TestClient) -> None:
        """인증 없이 챕터 삭제 시 401 에러를 반환한다."""
        response = client.delete("/api/v1/books/test-book-id-12345/chapters/test-id")
        assert response.status_code == 401
