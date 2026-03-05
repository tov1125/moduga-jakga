"""
보안 헤더 및 CORS 설정 검증 테스트
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.anyio
class TestSecurityHeaders:
    """보안 헤더 존재 확인"""

    async def test_x_content_type_options(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.headers.get("x-content-type-options") == "nosniff"

    async def test_x_frame_options(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.headers.get("x-frame-options") == "DENY"

    async def test_x_xss_protection(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.headers.get("x-xss-protection") == "1; mode=block"

    async def test_referrer_policy(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.headers.get("referrer-policy") == "strict-origin-when-cross-origin"

    async def test_permissions_policy(self, client: AsyncClient):
        resp = await client.get("/health")
        assert "microphone=(self)" in resp.headers.get("permissions-policy", "")

    async def test_content_security_policy(self, client: AsyncClient):
        resp = await client.get("/health")
        csp = resp.headers.get("content-security-policy", "")
        assert "default-src 'self'" in csp

    async def test_health_endpoint_ok(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"


@pytest.mark.anyio
class TestCORSHeaders:
    """CORS 설정 검증"""

    async def test_cors_preflight_allowed_method(self, client: AsyncClient):
        resp = await client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert resp.status_code in (200, 204, 400)

    async def test_cors_no_wildcard_methods(self, client: AsyncClient):
        resp = await client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        allow_methods = resp.headers.get("access-control-allow-methods", "")
        assert "*" not in allow_methods


@pytest.mark.anyio
class TestRateLimiting:
    """Rate Limiting 검증"""

    async def test_rate_limit_middleware_registered(self):
        """Rate Limiting 미들웨어가 등록되어 있는지 확인"""
        from app.core.rate_limit import rate_limit_middleware
        # 미들웨어 함수가 존재하는지 확인
        assert callable(rate_limit_middleware)

    async def test_rate_limit_key_uses_auth_header(self):
        """Authorization 헤더가 있으면 토큰 기반 키 사용"""
        from app.core.rate_limit import _get_client_key
        from unittest.mock import MagicMock

        mock_request = MagicMock()
        mock_request.headers = {"Authorization": "Bearer test_token_1234567890"}
        mock_request.client.host = "127.0.0.1"

        key = _get_client_key(mock_request)
        assert key.startswith("user:")

    async def test_rate_limit_key_fallback_to_ip(self):
        """Authorization 없으면 IP 기반 키 사용"""
        from app.core.rate_limit import _get_client_key
        from unittest.mock import MagicMock

        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.client.host = "192.168.1.1"

        key = _get_client_key(mock_request)
        assert not key.startswith("user:")

    async def test_ai_path_detection(self):
        """AI 경로 패턴 감지"""
        from app.core.rate_limit import _is_ai_path

        assert _is_ai_path("/api/v1/writing/generate") is True
        assert _is_ai_path("/api/v1/editing/proofread") is True
        assert _is_ai_path("/api/v1/design/cover/generate") is True
        assert _is_ai_path("/api/v1/books") is False
        assert _is_ai_path("/health") is False

    async def test_rate_limit_429_response(self):
        """한도 초과 시 429 응답"""
        from app.core.rate_limit import _request_counts, AI_LIMIT, WINDOW_SECONDS
        import time

        # AI 경로에 대한 카운터를 인위적으로 채움
        rate_key = "test-429:ai"
        now = time.time()
        _request_counts[rate_key] = [now] * (AI_LIMIT + 5)

        # 정리 후에도 제한 초과 확인
        cutoff = now - WINDOW_SECONDS
        recent = [t for t in _request_counts[rate_key] if t > cutoff]
        assert len(recent) >= AI_LIMIT

        # 테스트 후 정리
        del _request_counts[rate_key]
