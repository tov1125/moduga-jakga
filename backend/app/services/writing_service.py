"""
AI 글쓰기 서비스 모듈
OpenAI GPT를 사용하여 장르별 글 생성, 재작성, 구조 제안을 제공합니다.
"""

import json
import logging
from typing import Any, AsyncGenerator

from openai import AsyncOpenAI

from app.core.config import Settings
from app.schemas.book import Genre
from app.schemas.writing import (
    ChapterSuggestion,
    RewriteResponse,
    StructureResponse,
)

logger = logging.getLogger(__name__)

# 장르별 시스템 프롬프트 템플릿
GENRE_SYSTEM_PROMPTS: dict[str, str] = {
    Genre.ESSAY.value: (
        "당신은 한국의 수필/에세이 전문 작가입니다. "
        "따뜻하고 성찰적인 문체로, 일상에서 의미를 찾는 글을 씁니다. "
        "독자가 공감할 수 있는 개인적인 이야기를 자연스럽게 풀어내세요. "
        "지나치게 화려한 수식보다는 솔직하고 담백한 표현을 사용하세요."
    ),
    Genre.NOVEL.value: (
        "당신은 한국 소설 전문 작가입니다. "
        "생생한 묘사와 매력적인 캐릭터로 몰입감 있는 이야기를 만듭니다. "
        "대화와 서술을 적절히 배합하고, 갈등과 해결의 구조를 갖추세요. "
        "장면 전환이 자연스럽고, 독자의 감정을 이끌어내세요."
    ),
    Genre.POEM.value: (
        "당신은 한국 시인입니다. "
        "감각적인 이미지와 음악적 리듬을 가진 시를 씁니다. "
        "은유와 상징을 활용하되, 이해하기 어렵지 않도록 균형을 잡으세요. "
        "행과 연의 구분을 적절히 사용하여 호흡을 조절하세요."
    ),
    Genre.AUTOBIOGRAPHY.value: (
        "당신은 자서전 전문 작가입니다. "
        "저자의 삶의 경험을 시간순으로 정리하면서도 핵심 메시지가 드러나게 합니다. "
        "진솔한 목소리로 독자에게 다가가세요. "
        "인생의 전환점과 교훈을 명확히 전달하세요."
    ),
    Genre.CHILDREN.value: (
        "당신은 동화 작가입니다. "
        "쉽고 재미있는 문장으로 아이들의 상상력을 자극하는 이야기를 씁니다. "
        "교훈이 자연스럽게 녹아들도록 하고, 의성어/의태어를 활용하세요. "
        "밝고 따뜻한 분위기를 유지하세요."
    ),
    Genre.NON_FICTION.value: (
        "당신은 논픽션 작가입니다. "
        "사실에 기반한 정보를 명확하고 이해하기 쉽게 전달합니다. "
        "논리적인 구성과 신뢰성 있는 근거를 제시하세요. "
        "전문 용어는 쉽게 풀어서 설명하세요."
    ),
    Genre.OTHER.value: (
        "당신은 다재다능한 한국 작가입니다. "
        "사용자의 요청에 맞는 적절한 문체와 구성으로 글을 씁니다. "
        "맥락에 맞게 유연하게 대응하세요."
    ),
}


class WritingService:
    """OpenAI GPT 기반 AI 글쓰기 서비스"""

    def __init__(self, settings: Settings) -> None:
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = "gpt-4o"

    async def generate_stream(
        self,
        genre: Genre,
        prompt: str,
        context: str = "",
        chapter_title: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        """
        SSE 스트리밍으로 글을 생성합니다.

        Args:
            genre: 장르
            prompt: 사용자 지시사항
            context: 이전 맥락 (이미 쓴 내용)
            chapter_title: 챕터 제목
            max_tokens: 최대 생성 토큰 수
            temperature: 창작 온도

        Yields:
            생성된 텍스트 청크
        """
        system_prompt = GENRE_SYSTEM_PROMPTS.get(genre.value, GENRE_SYSTEM_PROMPTS[Genre.OTHER.value])

        # 사용자 메시지 구성
        user_message_parts: list[str] = []

        if chapter_title:
            user_message_parts.append(f"[챕터 제목: {chapter_title}]")

        if context:
            user_message_parts.append(f"[이전 내용]\n{context}\n[이전 내용 끝]")

        user_message_parts.append(f"[작성 지시]\n{prompt}")

        user_message = "\n\n".join(user_message_parts)

        try:
            stream = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"글 생성 중 오류: {e}")
            raise

    async def rewrite(
        self,
        original_text: str,
        instruction: str,
        genre: Genre,
        style_guide: str = "",
    ) -> RewriteResponse:
        """
        특정 구간의 텍스트를 재작성합니다.

        Args:
            original_text: 원본 텍스트
            instruction: 재작성 지시사항
            genre: 장르
            style_guide: 문체 가이드

        Returns:
            재작성된 텍스트와 변경 사항 요약
        """
        system_prompt = (
            f"{GENRE_SYSTEM_PROMPTS.get(genre.value, GENRE_SYSTEM_PROMPTS[Genre.OTHER.value])}\n\n"
            "주어진 텍스트를 지시사항에 따라 재작성하세요. "
            "원본의 핵심 의미를 보존하면서 개선하세요."
        )

        if style_guide:
            system_prompt += f"\n\n[문체 가이드]\n{style_guide}"

        user_message = (
            f"[원본 텍스트]\n{original_text}\n\n"
            f"[재작성 지시사항]\n{instruction}\n\n"
            "JSON 형식으로 응답하세요:\n"
            '{"rewritten_text": "재작성된 텍스트", "changes_summary": "변경 사항 요약"}'
        )

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=2048,
                temperature=0.5,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or "{}"
            result: dict[str, Any] = json.loads(content)

            return RewriteResponse(
                rewritten_text=result.get("rewritten_text", original_text),
                changes_summary=result.get("changes_summary", "변경 사항 없음"),
            )

        except Exception as e:
            logger.error(f"재작성 중 오류: {e}")
            raise

    async def suggest_structure(
        self,
        book_title: str,
        genre: Genre,
        description: str,
        target_chapters: int = 10,
    ) -> StructureResponse:
        """
        도서의 챕터 구조를 제안합니다.

        Args:
            book_title: 책 제목
            genre: 장르
            description: 책 설명/주제
            target_chapters: 목표 챕터 수

        Returns:
            제안된 챕터 구조
        """
        system_prompt = (
            "당신은 출판 편집자로서 도서의 챕터 구조를 설계합니다. "
            "장르와 주제에 맞는 논리적이고 매력적인 구성을 제안하세요."
        )

        user_message = (
            f"다음 정보를 바탕으로 {target_chapters}개 챕터의 구조를 제안해주세요.\n\n"
            f"제목: {book_title}\n"
            f"장르: {genre.value}\n"
            f"설명: {description}\n\n"
            "JSON 형식으로 응답하세요:\n"
            "{\n"
            '  "chapters": [\n'
            '    {"order": 1, "title": "챕터 제목", "description": "챕터 설명", "estimated_pages": 15}\n'
            "  ],\n"
            '  "overall_summary": "전체 구조 요약"\n'
            "}"
        )

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=2048,
                temperature=0.6,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or "{}"
            result: dict[str, Any] = json.loads(content)

            chapters = [
                ChapterSuggestion(
                    order=ch.get("order", idx + 1),
                    title=ch.get("title", f"챕터 {idx + 1}"),
                    description=ch.get("description", ""),
                    estimated_pages=ch.get("estimated_pages", 10),
                )
                for idx, ch in enumerate(result.get("chapters", []))
            ]

            return StructureResponse(
                chapters=chapters,
                overall_summary=result.get("overall_summary", ""),
            )

        except Exception as e:
            logger.error(f"구조 제안 중 오류: {e}")
            raise
