"""
STT (음성→텍스트) WebSocket API 엔드포인트
CLOVA Speech를 이용한 실시간 음성 인식을 처리합니다.
"""

import json
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.config import get_settings
from app.core.security import verify_token
from app.services.stt_service import STTService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/stream")
async def stt_stream(websocket: WebSocket) -> None:
    """
    WebSocket을 통한 실시간 STT 스트리밍 엔드포인트

    프로토콜:
    1. 클라이언트가 WebSocket 연결 후 첫 메시지로 인증 토큰 전송
    2. 두 번째 메시지로 STT 설정(언어, 옵션) JSON 전송
    3. 이후 바이너리 오디오 청크를 계속 전송
    4. 서버는 인식 결과를 JSON으로 반환

    오디오 포맷: PCM 16bit, 16kHz, Mono
    """
    await websocket.accept()

    settings = get_settings()
    stt_service: STTService | None = None

    try:
        # 1단계: 인증 토큰 수신 및 검증
        auth_message = await websocket.receive_text()
        auth_data: dict[str, Any] = json.loads(auth_message)
        token = auth_data.get("token", "")

        try:
            verify_token(token, settings)
        except Exception:
            await websocket.send_json({"error": "인증에 실패했습니다."})
            await websocket.close(code=4001, reason="인증 실패")
            return

        await websocket.send_json({"status": "인증 완료"})

        # 2단계: STT 설정 수신
        config_message = await websocket.receive_text()
        config_data: dict[str, Any] = json.loads(config_message)
        language = config_data.get("language", "ko-KR")

        # STT 서비스 초기화
        stt_service = STTService(settings=settings)
        await stt_service.initialize(language=language)

        await websocket.send_json({
            "status": "STT 세션 시작",
            "language": language,
        })

        # 3단계: 오디오 스트리밍 수신 및 인식 결과 반환
        while True:
            # 바이너리 오디오 데이터 수신
            audio_data = await websocket.receive_bytes()

            if not audio_data:
                continue

            # STT 서비스로 오디오 전송 및 결과 수신
            result = await stt_service.process_audio_chunk(audio_data)

            if result:
                await websocket.send_json({
                    "text": result.get("text", ""),
                    "is_final": result.get("is_final", False),
                    "segments": result.get("segments", []),
                })

    except WebSocketDisconnect:
        logger.info("STT WebSocket 연결이 종료되었습니다.")
    except json.JSONDecodeError:
        await websocket.send_json({"error": "잘못된 JSON 형식입니다."})
        await websocket.close(code=4002, reason="잘못된 메시지 형식")
    except Exception as e:
        logger.error(f"STT 스트리밍 중 오류 발생: {e}")
        try:
            await websocket.send_json({"error": f"STT 처리 중 오류: {str(e)}"})
            await websocket.close(code=4000, reason="서버 오류")
        except Exception:
            pass
    finally:
        # STT 서비스 정리
        if stt_service:
            await stt_service.close()
