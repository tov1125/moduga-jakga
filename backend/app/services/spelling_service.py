"""
한국어 맞춤법 검사 서비스 모듈
외부 맞춤법 검사 API 또는 py-hanspell을 활용하여 교정 기능을 제공합니다.
"""

import logging
import re
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# 부산대 한국어 맞춤법 검사기 API 엔드포인트
HANSPELL_API_URL = "https://speller.cs.pusan.ac.kr/results"


class SpellingService:
    """한국어 맞춤법 검사 서비스"""

    def __init__(self) -> None:
        self._timeout = 15.0

    async def check_spelling(self, text: str) -> list[dict[str, Any]]:
        """
        텍스트의 맞춤법을 검사합니다.

        Args:
            text: 검사할 텍스트

        Returns:
            교정 결과 리스트. 각 항목:
                - original: 원본 표현
                - corrected: 수정 표현
                - reason: 수정 이유
                - position_start: 시작 위치
                - position_end: 끝 위치
        """
        corrections: list[dict[str, Any]] = []

        # 텍스트를 500자 단위로 분할하여 검사
        chunks = self._split_text(text, max_length=500)
        offset = 0

        for chunk in chunks:
            chunk_corrections = await self._check_chunk(chunk, offset)
            corrections.extend(chunk_corrections)
            offset += len(chunk)

        return corrections

    async def _check_chunk(
        self,
        text: str,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        텍스트 청크에 대해 맞춤법 검사를 수행합니다.

        Args:
            text: 검사할 텍스트 청크
            offset: 원본 텍스트 내 시작 위치 오프셋

        Returns:
            교정 결과 리스트
        """
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    HANSPELL_API_URL,
                    data={"text1": text},
                )

                if response.status_code != 200:
                    logger.warning(
                        f"맞춤법 검사 API 오류: {response.status_code}"
                    )
                    return []

                return self._parse_response(response.text, text, offset)

        except httpx.TimeoutException:
            logger.warning("맞춤법 검사 API 타임아웃")
            return []
        except Exception as e:
            logger.error(f"맞춤법 검사 중 오류: {e}")
            return []

    def _parse_response(
        self,
        html_response: str,
        original_text: str,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        맞춤법 검사 API 응답을 파싱합니다.

        Args:
            html_response: API HTML 응답
            original_text: 원본 텍스트
            offset: 위치 오프셋

        Returns:
            파싱된 교정 결과 리스트
        """
        corrections: list[dict[str, Any]] = []

        try:
            # 간단한 정규식 기반 파싱 (API 응답 형식에 따라 조정 필요)
            # data-error-type, data-error-input, data-error-output 속성 추출
            error_pattern = re.compile(
                r'data-error-input="([^"]*)".*?'
                r'data-error-output="([^"]*)".*?'
                r'data-error-help="([^"]*)"',
                re.DOTALL,
            )

            matches = error_pattern.findall(html_response)

            for original, corrected, reason in matches:
                # 원본 텍스트에서 위치 찾기
                pos = original_text.find(original)
                if pos >= 0:
                    corrections.append({
                        "original": original,
                        "corrected": corrected,
                        "reason": reason if reason else "맞춤법 오류",
                        "position_start": offset + pos,
                        "position_end": offset + pos + len(original),
                    })

        except Exception as e:
            logger.error(f"맞춤법 검사 결과 파싱 오류: {e}")

        return corrections

    def _split_text(self, text: str, max_length: int = 500) -> list[str]:
        """
        텍스트를 적절한 크기로 분할합니다.

        Args:
            text: 분할할 텍스트
            max_length: 청크당 최대 길이

        Returns:
            분할된 텍스트 리스트
        """
        if len(text) <= max_length:
            return [text]

        chunks: list[str] = []
        current = 0

        while current < len(text):
            end = min(current + max_length, len(text))

            # 문장 경계에서 분할
            if end < len(text):
                # 마지막 문장 부호 위치 찾기
                last_period = text.rfind(".", current, end)
                last_question = text.rfind("?", current, end)
                last_exclaim = text.rfind("!", current, end)
                split_pos = max(last_period, last_question, last_exclaim)

                if split_pos > current:
                    end = split_pos + 1

            chunks.append(text[current:end])
            current = end

        return chunks

    async def apply_corrections(
        self,
        text: str,
        corrections: list[dict[str, Any]],
    ) -> str:
        """
        교정 결과를 텍스트에 적용합니다.

        Args:
            text: 원본 텍스트
            corrections: 교정 항목 리스트

        Returns:
            교정이 적용된 텍스트
        """
        # 위치 역순으로 정렬 (뒤에서부터 수정해야 위치가 틀어지지 않음)
        sorted_corrections = sorted(
            corrections,
            key=lambda c: c["position_start"],
            reverse=True,
        )

        result = text
        for correction in sorted_corrections:
            start = correction["position_start"]
            end = correction["position_end"]
            result = result[:start] + correction["corrected"] + result[end:]

        return result
