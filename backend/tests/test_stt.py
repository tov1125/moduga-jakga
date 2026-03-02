"""
STT WebSocket 엔드포인트 테스트
WebSocket을 통한 실시간 음성 인식 테스트
"""

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestSTTWebSocket:
    """STT WebSocket 스트리밍 테스트"""

    def test_websocket_connection(
        self,
        client: TestClient,
        auth_token: str,
        mock_settings: MagicMock,
    ) -> None:
        """WebSocket 연결 및 인증 테스트"""
        with patch("app.api.v1.stt.get_settings", return_value=mock_settings):
            with patch("app.api.v1.stt.verify_token") as mock_verify:
                mock_verify.return_value = {"sub": "test-user-id"}

                with client.websocket_connect("/api/v1/stt/stream") as websocket:
                    # 1단계: 인증 토큰 전송
                    websocket.send_text(json.dumps({"token": auth_token}))
                    response = websocket.receive_json()
                    assert response["status"] == "인증 완료"

                    # 2단계: STT 설정 전송
                    with patch("app.api.v1.stt.STTService") as mock_stt:
                        mock_service = AsyncMock()
                        mock_service.initialize = AsyncMock()
                        mock_service.process_audio_chunk = AsyncMock(return_value=None)
                        mock_service.close = AsyncMock()
                        mock_stt.return_value = mock_service

                        websocket.send_text(json.dumps({"language": "ko-KR"}))
                        response = websocket.receive_json()
                        assert response["status"] == "STT 세션 시작"

    def test_websocket_auth_failure(
        self,
        client: TestClient,
        mock_settings: MagicMock,
    ) -> None:
        """잘못된 토큰으로 WebSocket 연결 시도"""
        with patch("app.api.v1.stt.get_settings", return_value=mock_settings):
            with patch(
                "app.api.v1.stt.verify_token",
                side_effect=Exception("Invalid token"),
            ):
                with client.websocket_connect("/api/v1/stt/stream") as websocket:
                    # 잘못된 토큰 전송
                    websocket.send_text(json.dumps({"token": "invalid-token"}))
                    response = websocket.receive_json()
                    assert "error" in response

    def test_websocket_invalid_json(
        self,
        client: TestClient,
        mock_settings: MagicMock,
    ) -> None:
        """잘못된 JSON 형식 메시지 전송"""
        with patch("app.api.v1.stt.get_settings", return_value=mock_settings):
            with client.websocket_connect("/api/v1/stt/stream") as websocket:
                # 잘못된 JSON 전송
                websocket.send_text("not-valid-json{{{")
                response = websocket.receive_json()
                assert "error" in response


class TestSTTService:
    """STT 서비스 유닛 테스트"""

    @pytest.mark.asyncio
    async def test_process_audio_chunk_below_threshold(
        self,
        mock_settings: MagicMock,
    ) -> None:
        """최소 버퍼 크기 미만의 오디오 청크 처리"""
        from app.services.stt_service import STTService

        service = STTService(settings=mock_settings)
        await service.initialize()

        # 작은 오디오 데이터 (버퍼 미달)
        small_chunk = b"\x00" * 100
        result = await service.process_audio_chunk(small_chunk)

        # 버퍼가 차지 않으면 None 반환
        assert result is None

        await service.close()

    @pytest.mark.asyncio
    async def test_parse_recognition_result(
        self,
        mock_settings: MagicMock,
    ) -> None:
        """CLOVA Speech 응답 파싱 테스트"""
        from app.services.stt_service import STTService

        service = STTService(settings=mock_settings)

        raw_result = {
            "text": "안녕하세요",
            "segments": [
                {
                    "text": "안녕하세요",
                    "start": 0,
                    "end": 1500,
                    "confidence": 0.95,
                }
            ],
        }

        result = service._parse_recognition_result(raw_result)

        assert result["text"] == "안녕하세요"
        assert result["is_final"] is True
        assert len(result["segments"]) == 1
        assert result["segments"][0]["confidence"] == 0.95
