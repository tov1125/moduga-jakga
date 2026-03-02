"""
CLOVA Voice TTS 서비스 모듈
텍스트를 음성으로 변환하는 기능을 제공합니다.
"""

import logging
from typing import Any

import httpx

from app.core.config import Settings

logger = logging.getLogger(__name__)

# CLOVA Voice API 엔드포인트
CLOVA_VOICE_API_URL = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"


class TTSService:
    """CLOVA Voice 텍스트→음성 변환 서비스"""

    def __init__(self, settings: Settings) -> None:
        self._client_id = settings.CLOVA_VOICE_CLIENT_ID
        self._client_secret = settings.CLOVA_VOICE_CLIENT_SECRET

    async def synthesize(
        self,
        text: str,
        voice_id: str = "nara",
        speed: float = 0.0,
        pitch: float = 0.0,
        volume: float = 0.0,
        alpha: float = 0.0,
    ) -> bytes:
        """
        텍스트를 음성으로 변환합니다.

        Args:
            text: 변환할 텍스트 (최대 5,000자)
            voice_id: 음성 화자 ID
            speed: 발화 속도 (-5.0 ~ 5.0, 기본 0)
            pitch: 음높이 (-5.0 ~ 5.0, 기본 0)
            volume: 음량 (-5.0 ~ 5.0, 기본 0)
            alpha: 음색 보정 (-5.0 ~ 5.0, 기본 0)

        Returns:
            MP3 오디오 바이트 데이터

        Raises:
            RuntimeError: CLOVA Voice API 호출 실패 시
        """
        headers = {
            "X-NCP-APIGW-API-KEY-ID": self._client_id,
            "X-NCP-APIGW-API-KEY": self._client_secret,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        # 긴 텍스트를 청크로 분할하여 처리
        text_chunks = self._split_text(text, max_length=2000)
        audio_parts: list[bytes] = []

        async with httpx.AsyncClient(timeout=60.0) as client:
            for chunk in text_chunks:
                data = {
                    "speaker": voice_id,
                    "text": chunk,
                    "volume": str(int(volume)),
                    "speed": str(int(speed)),
                    "pitch": str(int(pitch)),
                    "alpha": str(int(alpha)),
                    "format": "mp3",
                }

                try:
                    response = await client.post(
                        CLOVA_VOICE_API_URL,
                        headers=headers,
                        data=data,
                    )

                    if response.status_code == 200:
                        audio_parts.append(response.content)
                    else:
                        error_msg = response.text
                        logger.error(
                            f"CLOVA Voice API 오류: {response.status_code} - {error_msg}"
                        )
                        raise RuntimeError(
                            f"음성 합성 실패 (상태 코드: {response.status_code})"
                        )

                except httpx.TimeoutException as e:
                    logger.error("CLOVA Voice API 타임아웃")
                    raise RuntimeError("음성 합성 시간 초과") from e

        # 모든 청크의 오디오를 합침
        return b"".join(audio_parts)

    def _split_text(self, text: str, max_length: int = 2000) -> list[str]:
        """
        텍스트를 CLOVA Voice API 제한에 맞게 분할합니다.
        문장 단위로 분할하여 자연스러운 끊김을 유지합니다.

        Args:
            text: 분할할 텍스트
            max_length: 청크당 최대 글자 수

        Returns:
            분할된 텍스트 리스트
        """
        if len(text) <= max_length:
            return [text]

        chunks: list[str] = []
        current_chunk = ""

        # 문장 구분자로 분할
        sentences = text.replace(".", ".\n").replace("!", "!\n").replace("?", "?\n").split("\n")

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(current_chunk) + len(sentence) + 1 <= max_length:
                current_chunk += (" " + sentence) if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                # 문장 자체가 max_length를 초과하면 강제 분할
                if len(sentence) > max_length:
                    for i in range(0, len(sentence), max_length):
                        chunks.append(sentence[i:i + max_length])
                    current_chunk = ""
                else:
                    current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    async def get_supported_voices(self) -> list[dict[str, Any]]:
        """
        지원하는 음성 목록을 반환합니다.

        Returns:
            음성 정보 딕셔너리 리스트
        """
        return [
            {"id": "nara", "name": "나라", "gender": "female", "description": "차분한 여성 낭독체"},
            {"id": "nara_call", "name": "나라(통화)", "gender": "female", "description": "여성 통화체"},
            {"id": "nminsang", "name": "민상", "gender": "male", "description": "차분한 남성 낭독체"},
            {"id": "nhajun", "name": "하준", "gender": "male", "description": "남성 아동 음성"},
            {"id": "ndain", "name": "다인", "gender": "female", "description": "여성 아동 음성"},
            {"id": "njiyun", "name": "지윤", "gender": "female", "description": "밝은 톤의 여성 음성"},
            {"id": "jinho", "name": "진호", "gender": "male", "description": "남성 뉴스체"},
            {"id": "mijin", "name": "미진", "gender": "female", "description": "여성 뉴스체"},
        ]
