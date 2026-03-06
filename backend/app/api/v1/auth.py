"""
인증 API 엔드포인트
회원가입, 로그인, 로그아웃, 사용자 정보 조회를 처리합니다.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.api.deps import get_current_user, get_supabase
from app.core.config import Settings, get_settings
from app.core.database import get_supabase_admin
from app.core.security import create_access_token
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    SignUpRequest,
    UserResponse,
    UserSettingsUpdate,
)

router = APIRouter()


def _build_user_response(profile: dict[str, Any]) -> UserResponse:
    """프로필 딕셔너리를 UserResponse로 변환합니다."""
    return UserResponse(
        id=profile["id"],
        email=profile["email"],
        display_name=profile["display_name"],
        disability_type=profile["disability_type"],
        voice_speed=profile.get("voice_speed", 1.0),
        voice_type=profile.get("voice_type", "default"),
        is_active=profile.get("is_active", True),
        created_at=str(profile["created_at"]),
        updated_at=str(profile["updated_at"]) if profile.get("updated_at") else None,
    )


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
)
async def signup(
    request: SignUpRequest,
    supabase: Client = Depends(get_supabase),
    admin_client: Client = Depends(get_supabase_admin),
    settings: Settings = Depends(get_settings),
) -> UserResponse:
    """
    새 사용자를 등록합니다.
    Supabase Auth로 계정을 생성하고 프로필 테이블에 추가 정보를 저장합니다.
    이메일 확인을 자동으로 처리하여 즉시 로그인 가능합니다.
    """
    try:
        # 이미 존재하는 이메일인지 확인
        existing = (
            admin_client.table("profiles")
            .select("id")
            .eq("email", request.email)
            .execute()
        )
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 가입된 이메일입니다. 로그인을 시도해 주세요.",
            )

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

        # 이메일 자동 확인 (관리자 권한으로 즉시 활성화)
        try:
            admin_client.auth.admin.update_user_by_id(
                user_id, {"email_confirm": True}
            )
        except Exception:
            pass  # 이미 확인된 경우 무시

        # 프로필 테이블에 추가 정보 저장
        profile_data = {
            "id": user_id,
            "email": request.email,
            "display_name": request.display_name,
            "disability_type": request.disability_type.value,
        }
        profile_response = admin_client.table("profiles").insert(profile_data).execute()

        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="프로필 생성에 실패했습니다.",
            )

        profile = profile_response.data[0]
        return _build_user_response(profile)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"회원가입 처리 중 오류가 발생했습니다: {e}",
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="로그인",
)
async def login(
    request: LoginRequest,
    supabase: Client = Depends(get_supabase),
    settings: Settings = Depends(get_settings),
) -> LoginResponse:
    """
    이메일과 비밀번호로 로그인합니다.
    인증 성공 시 사용자 정보와 JWT 액세스 토큰을 반환합니다.
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

        # 프로필 조회
        profile_resp = (
            supabase.table("profiles")
            .select("*")
            .eq("id", user_id)
            .execute()
        )

        if not profile_resp.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자 프로필을 찾을 수 없습니다.",
            )

        # JWT 토큰 생성
        access_token = create_access_token(
            subject=user_id,
            settings=settings,
            extra_claims={"email": request.email},
        )

        return LoginResponse(
            user=_build_user_response(profile_resp.data[0]),
            access_token=access_token,
            token_type="bearer",
            expires_in=str(settings.JWT_EXPIRE_MINUTES),
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인에 실패했습니다.",
        )


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
    return _build_user_response(current_user)


@router.patch(
    "/settings",
    response_model=UserResponse,
    summary="사용자 설정 변경",
)
async def update_settings(
    request: UserSettingsUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> UserResponse:
    """
    사용자 프로필 및 음성 설정을 업데이트합니다.
    변경할 필드만 전송하면 됩니다.
    """
    update_data: dict[str, Any] = {}
    if request.display_name is not None:
        update_data["display_name"] = request.display_name
    if request.disability_type is not None:
        update_data["disability_type"] = request.disability_type.value
    if request.voice_speed is not None:
        update_data["voice_speed"] = request.voice_speed
    if request.voice_type is not None:
        update_data["voice_type"] = request.voice_type

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 내용이 없습니다.",
        )

    response = (
        supabase.table("profiles")
        .update(update_data)
        .eq("id", current_user["id"])
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="설정 변경에 실패했습니다.",
        )

    return _build_user_response(response.data[0])
