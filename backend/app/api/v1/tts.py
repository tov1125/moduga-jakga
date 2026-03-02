"""
TTS (텍스트→음성) API 엔드포인트
CLOVA Voice를 이용한 음성 합성을 처리합니다.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response

from app.api.deps import get_current_user
from app.core.config import Settings, get_settings
from app.schemas.tts import (
    TTSSynthesizeRequest,
    TTSVoice,
    TTSVoiceId,
    TTSVoiceListResponse,
)
from app.services.tts_service import TTSService

router = APIRouter()

# 지원 음성 목록 (CLOVA Voice 화자 정보)
AVAILABLE_VOICES: list[TTSVoice] = [
    TTSVoice(
        id=TTSVoiceId.NARA,
        name="나라",
        gender="female",
        description="차분한 여성 낭독체",
        language="ko-KR",
    ),
    TTSVoice(
        id=TTSVoiceId.NARA_CALL,
        name="나라 (통화)",
        gender="female",
        description="여성 통화체",
        language="ko-KR",
    ),
    TTSVoice(
        id=TTSVoiceId.NMINSANG,
        name="민상",
        gender="male",
        description="차분한 남성 낭독체",
        language="ko-KR",
    ),
    TTSVoice(
        id=TTSVoiceId.NHAJUN,
        name="하준",
        gender="male",
        description="남성 아동 음성",
        language="ko-KR",
    ),
    TTSVoice(
        id=TTSVoiceId.NDAIN,
        name="다인",
        gender="female",
        description="여성 아동 음성",
        language="ko-KR",
    ),
    TTSVoice(
        id=TTSVoiceId.NJIYUN,
        name="지윤",
        gender="female",
        description="밝은 톤의 여성 음성",
        language="ko-KR",
    ),
    TTSVoice(
        id=TTSVoiceId.JINHO,
        name="진호",
        gender="male",
        description="남성 뉴스체",
        language="ko-KR",
    ),
    TTSVoice(
        id=TTSVoiceId.MIJIN,
        name="미진",
        gender="female",
        description="여성 뉴스체",
        language="ko-KR",
    ),
]


@router.post(
    "/synthesize",
    summary="음성 합성",
    response_class=Response,
    responses={
        200: {
            "content": {"audio/mpeg": {}},
            "description": "합성된 음성 오디오 (MP3)",
        },
    },
)
async def synthesize_speech(
    request: TTSSynthesizeRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> Response:
    """
    텍스트를 음성으로 변환합니다.
    CLOVA Voice API를 사용하여 MP3 오디오를 반환합니다.
    """
    if not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="변환할 텍스트를 입력해주세요.",
        )

    # 텍스트 길이 제한 (CLOVA Voice API 제한)
    if len(request.text) > 5000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="텍스트가 너무 깁니다. 5,000자 이하로 입력해주세요.",
        )

    tts_service = TTSService(settings=settings)

    try:
        audio_bytes = await tts_service.synthesize(
            text=request.text,
            voice_id=request.voice_id.value,
            speed=request.speed,
            pitch=request.pitch,
            volume=request.volume,
            alpha=request.alpha,
        )

        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3",
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"음성 합성에 실패했습니다: {str(e)}",
        ) from e


@router.get(
    "/voices",
    response_model=TTSVoiceListResponse,
    summary="사용 가능한 음성 목록",
)
async def list_voices(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> TTSVoiceListResponse:
    """사용 가능한 TTS 음성 목록을 반환합니다."""
    return TTSVoiceListResponse(
        voices=AVAILABLE_VOICES,
        total=len(AVAILABLE_VOICES),
    )
