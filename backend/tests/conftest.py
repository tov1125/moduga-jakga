"""
테스트 픽스처 모듈
테스트에 사용되는 공통 픽스처(클라이언트, 모의 객체 등)를 정의합니다.
"""

from typing import Any, AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def mock_settings() -> MagicMock:
    """모의 애플리케이션 설정"""
    settings = MagicMock()
    settings.SUPABASE_URL = "https://test.supabase.co"
    settings.SUPABASE_KEY = "test-anon-key"
    settings.SUPABASE_SERVICE_KEY = "test-service-key"
    settings.OPENAI_API_KEY = "test-openai-key"
    settings.CLOVA_SPEECH_SECRET = "test-clova-speech-secret"
    settings.CLOVA_SPEECH_INVOKE_URL = "https://test.clova.ai"
    settings.CLOVA_VOICE_CLIENT_ID = "test-clova-voice-id"
    settings.CLOVA_VOICE_CLIENT_SECRET = "test-clova-voice-secret"
    settings.JWT_SECRET_KEY = "test-jwt-secret-key-for-testing-only"
    settings.JWT_ALGORITHM = "HS256"
    settings.JWT_EXPIRE_MINUTES = 1440
    settings.CORS_ORIGINS = "http://localhost:3000"
    settings.cors_origins_list = ["http://localhost:3000"]
    return settings


@pytest.fixture
def mock_supabase() -> MagicMock:
    """모의 Supabase 클라이언트"""
    client = MagicMock()

    # 기본 테이블 쿼리 모의 설정
    table_mock = MagicMock()
    table_mock.select.return_value = table_mock
    table_mock.insert.return_value = table_mock
    table_mock.update.return_value = table_mock
    table_mock.delete.return_value = table_mock
    table_mock.eq.return_value = table_mock
    table_mock.order.return_value = table_mock
    table_mock.limit.return_value = table_mock
    table_mock.execute.return_value = MagicMock(data=[], count=0)

    client.table.return_value = table_mock

    # Auth 모의 설정
    auth_mock = MagicMock()
    client.auth = auth_mock

    return client


@pytest.fixture
def mock_openai() -> MagicMock:
    """모의 OpenAI 클라이언트"""
    client = MagicMock()

    # Chat completion 모의 설정
    chat_mock = MagicMock()
    completion_mock = MagicMock()
    completion_mock.choices = [
        MagicMock(
            message=MagicMock(content='{"text": "test response"}'),
            delta=MagicMock(content="test chunk"),
        )
    ]
    chat_mock.create = AsyncMock(return_value=completion_mock)
    client.chat.completions = chat_mock

    # Image generation 모의 설정
    images_mock = MagicMock()
    image_result = MagicMock()
    image_result.data = [MagicMock(url="https://test.com/image.png")]
    images_mock.generate = AsyncMock(return_value=image_result)
    client.images = images_mock

    return client


@pytest.fixture
def sample_user() -> dict[str, Any]:
    """테스트용 사용자 데이터"""
    return {
        "id": "test-user-id-12345",
        "email": "test@example.com",
        "display_name": "테스트 사용자",
        "disability_type": "visual",
        "is_active": True,
        "created_at": "2025-01-01T00:00:00+00:00",
        "updated_at": "2025-01-01T00:00:00+00:00",
    }


@pytest.fixture
def sample_book() -> dict[str, Any]:
    """테스트용 도서 데이터"""
    return {
        "id": "test-book-id-12345",
        "user_id": "test-user-id-12345",
        "title": "테스트 도서",
        "genre": "essay",
        "description": "테스트용 에세이 도서입니다.",
        "target_audience": "일반 독자",
        "status": "draft",
        "chapter_count": 3,
        "word_count": 5000,
        "created_at": "2025-01-01T00:00:00+00:00",
        "updated_at": "2025-01-01T00:00:00+00:00",
    }


@pytest.fixture
def sample_chapter() -> dict[str, Any]:
    """테스트용 챕터 데이터"""
    return {
        "id": "test-chapter-id-12345",
        "book_id": "test-book-id-12345",
        "title": "제1장: 시작",
        "content": "봄이 오면 산에 들에 진달래 꽃이 피고...",
        "order": 1,
        "status": "draft",
        "word_count": 150,
        "created_at": "2025-01-01T00:00:00+00:00",
        "updated_at": "2025-01-01T00:00:00+00:00",
    }


@pytest.fixture
def auth_token(mock_settings: MagicMock) -> str:
    """테스트용 JWT 토큰"""
    from app.core.security import create_access_token

    return create_access_token(
        subject="test-user-id-12345",
        settings=mock_settings,
    )


@pytest.fixture
def auth_headers(auth_token: str) -> dict[str, str]:
    """인증 헤더"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def client(
    mock_settings: MagicMock,
    mock_supabase: MagicMock,
    sample_user: dict[str, Any],
) -> Generator[TestClient, None, None]:
    """FastAPI 테스트 클라이언트"""
    with (
        patch("app.core.config.get_settings", return_value=mock_settings),
        patch("app.core.database._create_supabase_client", return_value=mock_supabase),
    ):
        # 사용자 인증 모의 - 프로필 조회 시 샘플 사용자 반환
        profile_query = MagicMock()
        profile_query.select.return_value = profile_query
        profile_query.eq.return_value = profile_query
        profile_query.execute.return_value = MagicMock(data=[sample_user])

        def mock_table(name: str) -> MagicMock:
            if name == "profiles":
                return profile_query
            # 기본 테이블 모의
            default = MagicMock()
            default.select.return_value = default
            default.insert.return_value = default
            default.update.return_value = default
            default.delete.return_value = default
            default.eq.return_value = default
            default.order.return_value = default
            default.limit.return_value = default
            default.execute.return_value = MagicMock(data=[], count=0)
            return default

        mock_supabase.table.side_effect = mock_table

        from app.main import app

        with TestClient(app) as test_client:
            yield test_client
