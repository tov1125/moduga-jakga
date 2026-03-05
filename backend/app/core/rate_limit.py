"""
Rate Limiting 미들웨어 모듈
경로 패턴 기반 요청 제한 (미들웨어 방식)
"""

import os
import time
from collections import defaultdict

from starlette.requests import Request
from starlette.responses import JSONResponse

# 테스트 환경 감지 (pytest 실행 시 비활성화)
_TESTING = os.environ.get("TESTING", "") == "1" or "pytest" in os.environ.get("_", "")

# 기본 제한: 60회/분
DEFAULT_LIMIT = 60
# AI API 제한: 10회/분
AI_LIMIT = 10
# 시간 윈도우 (초)
WINDOW_SECONDS = 60

# AI 경로 패턴 (이 경로에는 AI_LIMIT 적용)
AI_PATHS = ("/api/v1/writing/", "/api/v1/editing/", "/api/v1/design/cover/generate")

# 요청 카운터: { key: [timestamp, ...] }
_request_counts: dict[str, list[float]] = defaultdict(list)


def _get_client_key(request: Request) -> str:
    """Authorization 헤더 우선, 없으면 IP 기반 키"""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer ") and len(auth) > 23:
        return f"user:{auth[-16:]}"
    client = request.client
    return client.host if client else "unknown"


def _is_ai_path(path: str) -> bool:
    """AI 엔드포인트 경로인지 확인"""
    return any(path.startswith(p) for p in AI_PATHS)


async def rate_limit_middleware(request: Request, call_next):
    """경로 패턴 기반 Rate Limiting 미들웨어"""
    if _TESTING:
        return await call_next(request)

    path = request.url.path
    client_key = _get_client_key(request)
    is_ai = _is_ai_path(path)
    limit = AI_LIMIT if is_ai else DEFAULT_LIMIT

    rate_key = f"{client_key}:{'ai' if is_ai else 'general'}"
    now = time.time()

    # 시간 윈도우 밖의 오래된 항목 제거
    cutoff = now - WINDOW_SECONDS
    _request_counts[rate_key] = [t for t in _request_counts[rate_key] if t > cutoff]

    if len(_request_counts[rate_key]) >= limit:
        return JSONResponse(
            status_code=429,
            content={"detail": "요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요."},
            headers={"Retry-After": str(WINDOW_SECONDS)},
        )

    _request_counts[rate_key].append(now)
    response = await call_next(request)
    return response
