"""
backend/app/core/ 모듈 단위 테스트
config.py (Settings, cors_origins_list, get_settings)
security.py (create_access_token, verify_token)
"""

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException


# ---------------------------------------------------------------------------
# config.py 테스트
# ---------------------------------------------------------------------------

# Settings 생성에 필요한 최소 환경변수
_BASE_ENV = {
    "SUPABASE_URL": "https://test.supabase.co",
    "SUPABASE_KEY": "test-key",
    "SUPABASE_SERVICE_KEY": "test-service-key",
    "OPENAI_API_KEY": "test-openai-key",
    "CLOVA_SPEECH_SECRET": "test",
    "CLOVA_SPEECH_INVOKE_URL": "https://test",
    "CLOVA_VOICE_CLIENT_ID": "test",
    "CLOVA_VOICE_CLIENT_SECRET": "test",
    "JWT_SECRET_KEY": "test-jwt-secret",
}


class TestSettings:
    """Settings 클래스 테스트"""

    def test_cors_origins_list_단일(self):
        """CORS 단일 origin 파싱"""
        env = {**_BASE_ENV, "CORS_ORIGINS": "http://localhost:3000"}
        with patch.dict(os.environ, env, clear=False):
            from app.core.config import Settings

            s = Settings()
            assert s.cors_origins_list == ["http://localhost:3000"]

    def test_cors_origins_list_복수(self):
        """CORS 복수 origin 파싱 (쉼표 구분)"""
        env = {
            **_BASE_ENV,
            "CORS_ORIGINS": "http://localhost:3000, https://example.com, https://app.vercel.app",
        }
        with patch.dict(os.environ, env, clear=False):
            from app.core.config import Settings

            s = Settings()
            assert s.cors_origins_list == [
                "http://localhost:3000",
                "https://example.com",
                "https://app.vercel.app",
            ]

    def test_cors_origins_list_공백_트림(self):
        """CORS origin 앞뒤 공백이 제거되는지 확인"""
        env = {**_BASE_ENV, "CORS_ORIGINS": "  http://a.com , http://b.com  "}
        with patch.dict(os.environ, env, clear=False):
            from app.core.config import Settings

            s = Settings()
            assert s.cors_origins_list == ["http://a.com", "http://b.com"]

    def test_기본_cors_origin(self):
        """CORS_ORIGINS 미설정 시 기본값 http://localhost:3000"""
        env = {**_BASE_ENV}
        env.pop("CORS_ORIGINS", None)
        with patch.dict(os.environ, env, clear=False):
            from app.core.config import Settings

            s = Settings()
            assert "http://localhost:3000" in s.cors_origins_list

    def test_get_settings_반환타입(self):
        """get_settings()가 Settings 인스턴스를 반환"""
        env = {**_BASE_ENV}
        with patch.dict(os.environ, env, clear=False):
            from app.core.config import Settings, get_settings

            result = get_settings()
            assert isinstance(result, Settings)

    def test_jwt_기본값(self):
        """JWT 기본 설정값 확인"""
        env = {**_BASE_ENV}
        with patch.dict(os.environ, env, clear=False):
            from app.core.config import Settings

            s = Settings()
            assert s.JWT_ALGORITHM == "HS256"
            assert s.JWT_EXPIRE_MINUTES == 1440


# ---------------------------------------------------------------------------
# security.py 테스트
# ---------------------------------------------------------------------------


class TestSecurity:
    """JWT 토큰 생성/검증 테스트"""

    def test_토큰_생성_및_검증(self, mock_settings: MagicMock):
        """create_access_token → verify_token 라운드트립"""
        from app.core.security import create_access_token, verify_token

        token = create_access_token(subject="user-123", settings=mock_settings)
        payload = verify_token(token, mock_settings)
        assert payload["sub"] == "user-123"

    def test_잘못된_토큰_검증_실패(self, mock_settings: MagicMock):
        """유효하지 않은 토큰은 HTTPException 401 발생"""
        from app.core.security import verify_token

        with pytest.raises(HTTPException) as exc_info:
            verify_token("invalid-token", mock_settings)
        assert exc_info.value.status_code == 401

    def test_extra_claims_포함(self, mock_settings: MagicMock):
        """extra_claims가 토큰 페이로드에 포함"""
        from app.core.security import create_access_token, verify_token

        token = create_access_token(
            subject="user-123",
            settings=mock_settings,
            extra_claims={"role": "admin"},
        )
        payload = verify_token(token, mock_settings)
        assert payload["role"] == "admin"

    def test_토큰에_iat_exp_포함(self, mock_settings: MagicMock):
        """토큰 페이로드에 iat, exp 클레임 포함"""
        from app.core.security import create_access_token, verify_token

        token = create_access_token(subject="user-456", settings=mock_settings)
        payload = verify_token(token, mock_settings)
        assert "iat" in payload
        assert "exp" in payload

    def test_다른_시크릿으로_검증_실패(self, mock_settings: MagicMock):
        """다른 JWT 시크릿키로는 검증 실패"""
        from app.core.security import create_access_token, verify_token

        token = create_access_token(subject="user-789", settings=mock_settings)

        wrong_settings = MagicMock()
        wrong_settings.JWT_SECRET_KEY = "wrong-secret-key"
        wrong_settings.JWT_ALGORITHM = "HS256"

        with pytest.raises(HTTPException) as exc_info:
            verify_token(token, wrong_settings)
        assert exc_info.value.status_code == 401

    def test_토큰_문자열_타입(self, mock_settings: MagicMock):
        """create_access_token은 str 타입 반환"""
        from app.core.security import create_access_token

        token = create_access_token(subject="user-abc", settings=mock_settings)
        assert isinstance(token, str)
        assert len(token) > 0
