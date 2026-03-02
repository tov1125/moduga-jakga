"""
Supabase 클라이언트 초기화 모듈
Supabase 연결을 생성하고 의존성 주입을 제공합니다.
"""

from functools import lru_cache
from typing import Generator

from supabase import Client, create_client

from app.core.config import get_settings


@lru_cache(maxsize=1)
def _create_supabase_client() -> Client:
    """Supabase 클라이언트 싱글톤 생성"""
    settings = get_settings()
    client: Client = create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_KEY,
    )
    return client


@lru_cache(maxsize=1)
def _create_supabase_admin_client() -> Client:
    """Supabase 관리자 클라이언트 생성 (서비스 키 사용)"""
    settings = get_settings()
    client: Client = create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_SERVICE_KEY,
    )
    return client


def get_supabase() -> Generator[Client, None, None]:
    """FastAPI 의존성: Supabase 클라이언트 제공"""
    client = _create_supabase_client()
    yield client


def get_supabase_admin() -> Generator[Client, None, None]:
    """FastAPI 의존성: Supabase 관리자 클라이언트 제공"""
    client = _create_supabase_admin_client()
    yield client
