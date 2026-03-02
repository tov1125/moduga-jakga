"""
TTS(텍스트→음성) 관련 Pydantic 스키마
CLOVA Voice 음성 합성 요청 및 응답 스키마를 정의합니다.
"""

from enum import Enum

from pydantic import StrictFloat, StrictInt, StrictStr

from app.schemas.base import StrictBaseModel


class TTSVoiceId(str, Enum):
    """TTS 음성 ID 열거형 (CLOVA Voice 화자)"""
    NARA = "nara"           # 여성 차분한 낭독체
    NARA_CALL = "nara_call" # 여성 통화체
    NMINSANG = "nminsang"   # 남성 차분한 낭독체
    NHAJUN = "nhajun"       # 남성 아동
    NDAIN = "ndain"         # 여성 아동
    NJIYUN = "njiyun"       # 여성 밝은 톤
    JINHO = "jinho"         # 남성 뉴스체
    MIJIN = "mijin"         # 여성 뉴스체


class TTSSynthesizeRequest(StrictBaseModel):
    """TTS 음성 합성 요청 스키마"""
    text: StrictStr
    voice_id: TTSVoiceId = TTSVoiceId.NARA
    speed: StrictFloat = 0.0        # -5.0 ~ 5.0 (0이 기본)
    pitch: StrictFloat = 0.0        # -5.0 ~ 5.0
    volume: StrictFloat = 0.0       # -5.0 ~ 5.0
    alpha: StrictFloat = 0.0        # 음색 보정 -5.0 ~ 5.0


class TTSVoice(StrictBaseModel):
    """TTS 음성 정보 스키마"""
    id: TTSVoiceId
    name: StrictStr
    gender: StrictStr
    description: StrictStr
    language: StrictStr = "ko-KR"


class TTSVoiceListResponse(StrictBaseModel):
    """TTS 음성 목록 응답 스키마"""
    voices: list[TTSVoice]
    total: StrictInt
