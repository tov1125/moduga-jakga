"""
STT(음성→텍스트) 관련 Pydantic 스키마
CLOVA Speech 음성 인식 설정 및 결과 스키마를 정의합니다.
"""

from enum import Enum

from pydantic import StrictBool, StrictFloat, StrictStr

from app.schemas.base import StrictBaseModel


class STTLanguage(str, Enum):
    """STT 지원 언어 열거형"""
    KOREAN = "ko-KR"
    ENGLISH = "en-US"
    JAPANESE = "ja-JP"


class STTConfig(StrictBaseModel):
    """STT 세션 설정 스키마"""
    language: STTLanguage = STTLanguage.KOREAN
    enable_punctuation: StrictBool = True
    enable_disfluency_filter: StrictBool = True  # 더듬거림 필터


class STTSegment(StrictBaseModel):
    """STT 인식 구간 스키마"""
    text: StrictStr
    start_time: StrictFloat
    end_time: StrictFloat
    confidence: StrictFloat


class STTResult(StrictBaseModel):
    """STT 인식 결과 스키마"""
    text: StrictStr
    is_final: StrictBool
    segments: list[STTSegment] = []
    language: STTLanguage = STTLanguage.KOREAN
