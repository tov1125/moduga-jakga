"""
JWT 인증 및 보안 유틸리티 모듈
토큰 생성, 검증, 사용자 인증 의존성을 제공합니다.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from supabase import Client

from app.core.config import Settings, get_settings
from app.core.database import get_supabase

# Bearer 토큰 스키마
bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(
    subject: str,
    settings: Settings,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """
    JWT 액세스 토큰 생성

    Args:
        subject: 토큰 주체 (보통 사용자 ID)
        settings: 애플리케이션 설정
        extra_claims: 추가 클레임 데이터

    Returns:
        인코딩된 JWT 토큰 문자열
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": expire,
    }
    if extra_claims:
        payload.update(extra_claims)

    token: str = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token


def verify_token(token: str, settings: Settings) -> dict[str, Any]:
    """
    JWT 토큰 검증 및 페이로드 반환

    Args:
        token: JWT 토큰 문자열
        settings: 애플리케이션 설정

    Returns:
        디코딩된 토큰 페이로드

    Raises:
        HTTPException: 토큰이 유효하지 않은 경우
    """
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    settings: Settings = Depends(get_settings),
    supabase: Client = Depends(get_supabase),
) -> dict[str, Any]:
    """
    현재 인증된 사용자 정보 반환 (FastAPI 의존성)

    Bearer 토큰에서 사용자 ID를 추출하고
    Supabase에서 프로필 정보를 조회합니다.

    Args:
        credentials: HTTP Bearer 인증 정보
        settings: 애플리케이션 설정
        supabase: Supabase 클라이언트

    Returns:
        사용자 프로필 정보 딕셔너리

    Raises:
        HTTPException: 인증 실패 시
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 정보가 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(credentials.credentials, settings)
    user_id: str | None = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰 페이로드입니다.",
        )

    # Supabase에서 사용자 프로필 조회
    response = supabase.table("profiles").select("*").eq("id", user_id).execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다.",
        )

    user_data: dict[str, Any] = response.data[0]
    return user_data
