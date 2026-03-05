"""
모두가 작가 - FastAPI 애플리케이션 엔트리포인트
시각장애인을 위한 AI 기반 글쓰기 플랫폼 백엔드
"""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.rate_limit import rate_limit_middleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """애플리케이션 수명 주기 관리 (시작/종료 이벤트)"""
    # 시작 시 초기화 작업
    settings = get_settings()
    print(f"[모두가 작가] 서버 시작 - CORS 허용 출처: {settings.cors_origins_list}")
    yield
    # 종료 시 정리 작업
    print("[모두가 작가] 서버 종료")


app = FastAPI(
    title="모두가 작가 API",
    description=(
        "시각장애인을 위한 AI 기반 글쓰기 플랫폼.\n\n"
        "STT(음성→텍스트), TTS(텍스트→음성), AI 글쓰기 보조, "
        "4단계 편집, 표지 디자인, 출판 내보내기 기능을 제공합니다."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# 보안 헤더 + Rate Limiting 미들웨어
@app.middleware("http")
async def add_security_headers(request: Request, call_next) -> Response:  # noqa: ARG001
    """모든 응답에 보안 헤더를 추가합니다."""
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(self), geolocation=()"
    )
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data: https://*.supabase.co; "
        "style-src 'self' 'unsafe-inline'; connect-src 'self' https://*.supabase.co"
    )
    return response


# Rate Limiting 미들웨어
@app.middleware("http")
async def apply_rate_limit(request: Request, call_next):
    """경로 패턴 기반 Rate Limiting"""
    return await rate_limit_middleware(request, call_next)


# CORS 미들웨어 설정 (강화: 와일드카드 → 명시적 목록)
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# 정적 파일 서빙 (AI 생성 표지 이미지 등)
_static_dir = Path(__file__).resolve().parent.parent / "static"
_static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")

# API v1 라우터 마운트
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health", tags=["시스템"])
async def health_check() -> dict[str, Any]:
    """서버 상태 확인 엔드포인트"""
    return {
        "status": "healthy",
        "service": "모두가 작가 API",
        "version": "0.1.0",
    }
