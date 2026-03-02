"""
CLOVA Speech STT 서비스 모듈
실시간 음성 인식(STT) 기능을 제공합니다.
gRPC 또는 REST API를 통해 CLOVA Speech와 통신합니다.
"""

import json
import logging
from typing import Any

import httpx

from app.core.config import Settings

logger = logging.getLogger(__name__)


class STTService:
    """CLOVA Speech 음성 인식 서비스"""

    def __init__(self, settings: Settings) -> None:
        self._secret = settings.CLOVA_SPEECH_SECRET
        self._invoke_url = settings.CLOVA_SPEECH_INVOKE_URL
        self._language = "ko-KR"
        self._http_client: httpx.AsyncClient | None = None
        self._audio_buffer: bytearray = bytearray()
        # 최소 버퍼 크기 (32KB) - 너무 작은 청크는 모아서 전송
        self._min_buffer_size = 32 * 1024

    async def initialize(self, language: str = "ko-KR") -> None:
        """
        STT 세션을 초기화합니다.

        Args:
            language: 인식 언어 코드 (ko-KR, en-US, ja-JP)
        """
        self._language = language
        self._audio_buffer = bytearray()
        self._http_client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"STT 세션 초기화 완료 (언어: {language})")

    async def process_audio_chunk(self, audio_data: bytes) -> dict[str, Any] | None:
        """
        오디오 청크를 처리하고 인식 결과를 반환합니다.

        Args:
            audio_data: PCM 16bit, 16kHz, Mono 오디오 데이터

        Returns:
            인식 결과 딕셔너리 또는 None (아직 결과가 없는 경우)
        """
        self._audio_buffer.extend(audio_data)

        # 버퍼가 최소 크기에 도달하면 인식 요청
        if len(self._audio_buffer) >= self._min_buffer_size:
            result = await self._send_recognition_request(bytes(self._audio_buffer))
            self._audio_buffer.clear()
            return result

        return None

    async def _send_recognition_request(self, audio_data: bytes) -> dict[str, Any] | None:
        """
        CLOVA Speech REST API로 음성 인식 요청을 전송합니다.

        Args:
            audio_data: 인식할 오디오 데이터

        Returns:
            인식 결과 딕셔너리
        """
        if not self._http_client:
            logger.error("HTTP 클라이언트가 초기화되지 않았습니다.")
            return None

        headers = {
            "X-CLOVASPEECH-API-KEY": self._secret,
            "Content-Type": "application/octet-stream",
        }

        params = {
            "lang": self._language,
            "completion": "sync",
        }

        try:
            response = await self._http_client.post(
                f"{self._invoke_url}/recognizer/upload",
                headers=headers,
                params=params,
                content=audio_data,
            )

            if response.status_code == 200:
                result_data = response.json()
                return self._parse_recognition_result(result_data)
            else:
                logger.error(
                    f"CLOVA Speech API 오류: {response.status_code} - {response.text}"
                )
                return None

        except httpx.TimeoutException:
            logger.warning("CLOVA Speech API 타임아웃")
            return None
        except Exception as e:
            logger.error(f"STT 요청 중 오류: {e}")
            return None

    def _parse_recognition_result(self, raw_result: dict[str, Any]) -> dict[str, Any]:
        """
        CLOVA Speech 응답을 파싱하여 표준 형식으로 변환합니다.

        Args:
            raw_result: CLOVA Speech API 원본 응답

        Returns:
            표준화된 인식 결과
        """
        text = raw_result.get("text", "")
        segments_raw = raw_result.get("segments", [])

        segments = []
        for seg in segments_raw:
            segments.append({
                "text": seg.get("text", ""),
                "start_time": seg.get("start", 0) / 1000.0,  # ms → sec
                "end_time": seg.get("end", 0) / 1000.0,
                "confidence": seg.get("confidence", 0.0),
            })

        return {
            "text": text,
            "is_final": True,
            "segments": segments,
        }

    async def finalize(self) -> dict[str, Any] | None:
        """
        남은 버퍼를 모두 처리하고 최종 결과를 반환합니다.
        세션 종료 시 호출합니다.
        """
        if self._audio_buffer:
            result = await self._send_recognition_request(bytes(self._audio_buffer))
            self._audio_buffer.clear()
            return result
        return None

    async def close(self) -> None:
        """STT 세션을 종료하고 리소스를 정리합니다."""
        # 남은 버퍼 처리
        await self.finalize()

        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

        logger.info("STT 세션 종료")
