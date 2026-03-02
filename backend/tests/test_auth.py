"""
인증 API 엔드포인트 테스트
회원가입, 로그인, 로그아웃, 사용자 정보 조회 테스트
"""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestSignUp:
    """회원가입 테스트"""

    def test_signup_success(
        self,
        client: TestClient,
        mock_supabase: MagicMock,
    ) -> None:
        """정상적인 회원가입 요청"""
        # Supabase Auth 모의 설정
        mock_user = MagicMock()
        mock_user.id = "new-user-id"
        mock_supabase.auth.sign_up.return_value = MagicMock(user=mock_user)

        # 프로필 생성 모의
        profile_data = {
            "id": "new-user-id",
            "email": "newuser@example.com",
            "display_name": "새 사용자",
            "disability_type": "visual",
            "is_active": True,
            "created_at": "2025-01-01T00:00:00+00:00",
        }

        # table 모의를 세밀하게 설정
        insert_mock = MagicMock()
        insert_mock.insert.return_value = insert_mock
        insert_mock.execute.return_value = MagicMock(data=[profile_data])

        original_side_effect = mock_supabase.table.side_effect

        def table_mock(name: str) -> MagicMock:
            if name == "profiles":
                profile_mock = MagicMock()
                profile_mock.select.return_value = profile_mock
                profile_mock.eq.return_value = profile_mock
                profile_mock.execute.return_value = MagicMock(data=[profile_data])
                profile_mock.insert.return_value = profile_mock
                return profile_mock
            return original_side_effect(name) if original_side_effect else MagicMock()

        mock_supabase.table.side_effect = table_mock

        response = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "StrongPassword123!",
                "display_name": "새 사용자",
                "disability_type": "visual",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["display_name"] == "새 사용자"

    def test_signup_missing_fields(self, client: TestClient) -> None:
        """필수 필드 누락 시 422 에러"""
        response = client.post(
            "/api/v1/auth/signup",
            json={"email": "test@example.com"},
        )
        assert response.status_code == 422


class TestLogin:
    """로그인 테스트"""

    def test_login_success(
        self,
        client: TestClient,
        mock_supabase: MagicMock,
        mock_settings: MagicMock,
    ) -> None:
        """정상적인 로그인 요청"""
        mock_user = MagicMock()
        mock_user.id = "test-user-id-12345"
        mock_supabase.auth.sign_in_with_password.return_value = MagicMock(user=mock_user)

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(
        self,
        client: TestClient,
        mock_supabase: MagicMock,
    ) -> None:
        """잘못된 인증 정보로 로그인 시도"""
        mock_supabase.auth.sign_in_with_password.side_effect = Exception("Invalid credentials")

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "WrongPassword",
            },
        )

        assert response.status_code == 401


class TestGetMe:
    """내 정보 조회 테스트"""

    def test_get_me_authenticated(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        sample_user: dict[str, Any],
    ) -> None:
        """인증된 사용자 정보 조회"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == sample_user["email"]
        assert data["display_name"] == sample_user["display_name"]

    def test_get_me_unauthenticated(self, client: TestClient) -> None:
        """인증 없이 사용자 정보 조회 시도"""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401


class TestLogout:
    """로그아웃 테스트"""

    def test_logout_success(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """정상적인 로그아웃"""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "로그아웃" in data["message"]
