"""
인증 관련 Pydantic 스키마
회원가입, 로그인, 토큰, 사용자 응답 스키마를 정의합니다.
"""

from enum import Enum

from typing import Optional

from pydantic import Field, StrictBool, StrictFloat, StrictStr

from app.schemas.base import StrictBaseModel


class DisabilityType(str, Enum):
    """장애 유형 열거형"""
    VISUAL = "visual"           # 시각장애
    LOW_VISION = "low_vision"   # 저시력
    NONE = "none"               # 비장애
    OTHER = "other"             # 기타


class SignUpRequest(StrictBaseModel):
    """회원가입 요청 스키마"""
    email: StrictStr = Field(..., min_length=5, max_length=255)
    password: StrictStr = Field(..., min_length=8, max_length=128)
    display_name: StrictStr = Field(..., min_length=1, max_length=50)
    disability_type: DisabilityType = DisabilityType.NONE


class LoginRequest(StrictBaseModel):
    """로그인 요청 스키마"""
    email: StrictStr = Field(..., min_length=5, max_length=255)
    password: StrictStr = Field(..., min_length=8, max_length=128)


class TokenResponse(StrictBaseModel):
    """토큰 응답 스키마"""
    access_token: StrictStr
    token_type: StrictStr = "bearer"
    expires_in: StrictStr


class LoginResponse(StrictBaseModel):
    """로그인 응답 스키마 — FE와 동기화된 형식"""
    user: "UserResponse"
    access_token: StrictStr
    token_type: StrictStr = "bearer"
    expires_in: StrictStr


class UserResponse(StrictBaseModel):
    """사용자 정보 응답 스키마"""
    id: StrictStr
    email: StrictStr
    display_name: StrictStr
    disability_type: DisabilityType
    voice_speed: StrictFloat = 1.0
    voice_type: StrictStr = "default"
    is_active: StrictBool = True
    created_at: StrictStr
    updated_at: Optional[StrictStr] = None


class UserSettingsUpdate(StrictBaseModel):
    """사용자 설정 업데이트 스키마"""
    display_name: Optional[StrictStr] = Field(None, min_length=1, max_length=50)
    disability_type: Optional[DisabilityType] = None
    voice_speed: Optional[StrictFloat] = Field(None, ge=0.5, le=2.0)
    voice_type: Optional[StrictStr] = Field(None, max_length=50)


class LogoutResponse(StrictBaseModel):
    """로그아웃 응답 스키마"""
    message: StrictStr = "로그아웃되었습니다."


# Forward reference 해결
LoginResponse.model_rebuild()
