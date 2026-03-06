"""
공통 API 의존성 모듈
여러 라우터에서 공유하는 의존성을 재내보내기합니다.
"""

from typing import Any

from fastapi import Depends
from supabase import Client

from app.core.database import get_supabase as _get_supabase
from app.core.database import get_supabase_admin as _get_supabase_admin
from app.core.security import get_current_user as _get_current_user

# 의존성 재내보내기 (import 경로 통일 목적)


async def get_current_user(
    user: dict[str, Any] = Depends(_get_current_user),
) -> dict[str, Any]:
    """현재 인증된 사용자 정보 반환"""
    return user


def get_supabase(
    client: Client = Depends(_get_supabase_admin),
) -> Client:
    """Supabase 클라이언트 반환 (service role — RLS 우회)"""
    return client


def get_supabase_anon(
    client: Client = Depends(_get_supabase),
) -> Client:
    """Supabase anon 클라이언트 (Auth 전용: sign_up, sign_in)"""
    return client
