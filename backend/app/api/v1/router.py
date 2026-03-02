"""
API v1 라우터 모듈
모든 v1 엔드포인트 라우터를 통합합니다.
"""

from fastapi import APIRouter

from app.api.v1 import auth, books, chapters, design, editing, publishing, stt, tts, writing

api_v1_router = APIRouter()

# 인증 라우터
api_v1_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["인증"],
)

# 도서 관리 라우터
api_v1_router.include_router(
    books.router,
    prefix="/books",
    tags=["도서"],
)

# 챕터 관리 라우터
api_v1_router.include_router(
    chapters.router,
    tags=["챕터"],
)

# STT (음성→텍스트) 라우터
api_v1_router.include_router(
    stt.router,
    prefix="/stt",
    tags=["STT"],
)

# TTS (텍스트→음성) 라우터
api_v1_router.include_router(
    tts.router,
    prefix="/tts",
    tags=["TTS"],
)

# AI 글쓰기 라우터
api_v1_router.include_router(
    writing.router,
    prefix="/writing",
    tags=["AI 글쓰기"],
)

# 편집 라우터
api_v1_router.include_router(
    editing.router,
    prefix="/editing",
    tags=["편집"],
)

# 디자인 라우터
api_v1_router.include_router(
    design.router,
    prefix="/design",
    tags=["디자인"],
)

# 출판/내보내기 라우터
api_v1_router.include_router(
    publishing.router,
    prefix="/publishing",
    tags=["출판"],
)
