"""
인증 관련 Pydantic 스키마
회원가입, 로그인, 토큰, 사용자 응답 스키마를 정의합니다.
"""

from enum import Enum

from pydantic import StrictBool, StrictStr

from app.schemas.base import StrictBaseModel


class DisabilityType(str, Enum):
    """장애 유형 열거형"""
    VISUAL = "visual"           # 시각장애
    LOW_VISION = "low_vision"   # 저시력
    NONE = "none"               # 비장애
    OTHER = "other"             # 기타


class SignUpRequest(StrictBaseModel):
    """회원가입 요청 스키마"""
    email: StrictStr
    password: StrictStr
    display_name: StrictStr
    disability_type: DisabilityType = DisabilityType.NONE


class LoginRequest(StrictBaseModel):
    """로그인 요청 스키마"""
    email: StrictStr
    password: StrictStr


class TokenResponse(StrictBaseModel):
    """토큰 응답 스키마"""
    access_token: StrictStr
    token_type: StrictStr = "bearer"
    expires_in: StrictStr


class UserResponse(StrictBaseModel):
    """사용자 정보 응답 스키마"""
    id: StrictStr
    email: StrictStr
    display_name: StrictStr
    disability_type: DisabilityType
    is_active: StrictBool = True
    created_at: StrictStr


class LogoutResponse(StrictBaseModel):
    """로그아웃 응답 스키마"""
    message: StrictStr = "로그아웃되었습니다."
