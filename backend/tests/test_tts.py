"""TTS(Text-to-Speech) API 엔드포인트 테스트.

음성 합성 및 음성 목록 조회에 대한 단위 테스트를 제공합니다.
- POST /api/v1/tts/synthesize (음성 합성)
- GET /api/v1/tts/voices (음성 목록)
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestSynthesizeSpeech:
    """POST /api/v1/tts/synthesize 테스트."""

    @patch("app.api.v1.tts.TTSService")
    def test_음성_합성_성공(
        self,
        mock_tts_cls: MagicMock,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """텍스트를 정상적으로 음성 합성한다."""
        mock_service = MagicMock()
        mock_service.synthesize = AsyncMock(return_value=b"fake-audio-bytes")
        mock_tts_cls.return_value = mock_service

        response = client.post(
            "/api/v1/tts/synthesize",
            headers=auth_headers,
            json={
                "text": "안녕하세요. 테스트 음성입니다.",
                "voice_id": "nara",
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"
        assert response.content == b"fake-audio-bytes"

    def test_빈_텍스트_합성_시_400(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """빈 텍스트로 합성 요청 시 400 에러를 반환한다."""
        response = client.post(
            "/api/v1/tts/synthesize",
            headers=auth_headers,
            json={
                "text": "   ",
                "voice_id": "nara",
            },
        )

        assert response.status_code == 400

    def test_긴_텍스트_합성_시_422(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """5000자 초과 텍스트 합성 시 422(Pydantic 검증 오류)를 반환한다."""
        long_text = "가" * 5001

        response = client.post(
            "/api/v1/tts/synthesize",
            headers=auth_headers,
            json={
                "text": long_text,
                "voice_id": "nara",
            },
        )

        assert response.status_code == 422

    @patch("app.api.v1.tts.TTSService")
    def test_서비스_오류_시_500(
        self,
        mock_tts_cls: MagicMock,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """TTS 서비스 오류 시 500 에러를 반환한다."""
        mock_service = MagicMock()
        mock_service.synthesize = AsyncMock(
            side_effect=Exception("CLOVA API 연결 실패")
        )
        mock_tts_cls.return_value = mock_service

        response = client.post(
            "/api/v1/tts/synthesize",
            headers=auth_headers,
            json={
                "text": "테스트 텍스트",
                "voice_id": "nara",
            },
        )

        assert response.status_code == 500

    def test_미인증_합성_거부(
        self,
        client: TestClient,
    ) -> None:
        """인증 없이 합성 시 401 에러를 반환한다."""
        response = client.post(
            "/api/v1/tts/synthesize",
            json={"text": "테스트", "voice_id": "nara"},
        )
        assert response.status_code == 401


class TestListVoices:
    """GET /api/v1/tts/voices 테스트."""

    def test_음성_목록_정상_조회(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """사용 가능한 음성 목록을 정상적으로 조회한다."""
        response = client.get(
            "/api/v1/tts/voices",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "voices" in data
        assert "total" in data
        assert data["total"] > 0
        assert len(data["voices"]) == data["total"]

    def test_음성_목록에_필수_필드_포함(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """음성 목록의 각 항목에 필수 필드가 포함되어 있다."""
        response = client.get(
            "/api/v1/tts/voices",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        for voice in data["voices"]:
            assert "id" in voice
            assert "name" in voice
            assert "gender" in voice
            assert "language" in voice

    def test_미인증_음성_목록_거부(
        self,
        client: TestClient,
    ) -> None:
        """인증 없이 음성 목록 조회 시 401 에러를 반환한다."""
        response = client.get("/api/v1/tts/voices")
        assert response.status_code == 401
