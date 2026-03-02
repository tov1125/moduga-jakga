"""
모두가 작가 - FastAPI 애플리케이션 엔트리포인트
시각장애인을 위한 AI 기반 글쓰기 플랫폼 백엔드
"""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.core.config import get_settings


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

# CORS 미들웨어 설정
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
