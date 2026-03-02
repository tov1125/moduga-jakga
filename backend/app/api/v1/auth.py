"""
인증 API 엔드포인트
회원가입, 로그인, 로그아웃, 사용자 정보 조회를 처리합니다.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.api.deps import get_current_user, get_supabase
from app.core.config import Settings, get_settings
from app.core.security import create_access_token
from app.schemas.auth import (
    LoginRequest,
    LogoutResponse,
    SignUpRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter()


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
)
async def signup(
    request: SignUpRequest,
    supabase: Client = Depends(get_supabase),
    settings: Settings = Depends(get_settings),
) -> UserResponse:
    """
    새 사용자를 등록합니다.
    Supabase Auth로 계정을 생성하고 프로필 테이블에 추가 정보를 저장합니다.
    """
    try:
        # Supabase Auth로 사용자 생성
        auth_response = supabase.auth.sign_up(
            {
                "email": request.email,
                "password": request.password,
            }
        )

        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="회원가입에 실패했습니다.",
            )

        user_id = auth_response.user.id

        # 프로필 테이블에 추가 정보 저장
        profile_data = {
            "id": user_id,
            "email": request.email,
            "display_name": request.display_name,
            "disability_type": request.disability_type.value,
        }
        profile_response = supabase.table("profiles").insert(profile_data).execute()

        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="프로필 생성에 실패했습니다.",
            )

        profile = profile_response.data[0]
        return UserResponse(
            id=profile["id"],
            email=profile["email"],
            display_name=profile["display_name"],
            disability_type=profile["disability_type"],
            is_active=profile.get("is_active", True),
            created_at=str(profile["created_at"]),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"회원가입 처리 중 오류가 발생했습니다: {str(e)}",
        ) from e


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="로그인",
)
async def login(
    request: LoginRequest,
    supabase: Client = Depends(get_supabase),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    """
    이메일과 비밀번호로 로그인합니다.
    인증 성공 시 JWT 액세스 토큰을 반환합니다.
    """
    try:
        # Supabase Auth로 로그인
        auth_response = supabase.auth.sign_in_with_password(
            {
                "email": request.email,
                "password": request.password,
            }
        )

        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            )

        user_id = auth_response.user.id

        # JWT 토큰 생성
        access_token = create_access_token(
            subject=user_id,
            settings=settings,
            extra_claims={"email": request.email},
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=str(settings.JWT_EXPIRE_MINUTES),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"로그인에 실패했습니다: {str(e)}",
        ) from e


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="로그아웃",
)
async def logout(
    current_user: dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> LogoutResponse:
    """
    현재 사용자를 로그아웃합니다.
    서버 측 세션을 무효화합니다.
    """
    try:
        supabase.auth.sign_out()
    except Exception:
        pass  # 로그아웃 실패는 무시 (토큰 만료 등)

    return LogoutResponse(message="로그아웃되었습니다.")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="내 정보 조회",
)
async def get_me(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> UserResponse:
    """
    현재 로그인한 사용자의 프로필 정보를 반환합니다.
    """
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        display_name=current_user["display_name"],
        disability_type=current_user["disability_type"],
        is_active=current_user.get("is_active", True),
        created_at=str(current_user["created_at"]),
    )
