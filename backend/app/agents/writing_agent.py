"""
AI 글쓰기 에이전트 (A7)
WritingService를 에이전트 프로토콜로 감싸서 글쓰기 작업을 수행합니다.
"""

import logging
from typing import Any

from app.agents.base import AgentMessage, BaseAgent, MessageType
from app.core.config import get_settings
from app.schemas.book import Genre
from app.services.writing_service import WritingService

logger = logging.getLogger(__name__)


class WritingAgent(BaseAgent):
    """
    AI 글쓰기 에이전트 (A7)
    사용자의 지시에 따라 장르별 글을 생성하고,
    구조 제안과 재작성 기능을 제공합니다.
    """

    def __init__(self) -> None:
        super().__init__(
            name="writing_agent",
            description="AI 기반 글쓰기 에이전트 - 장르별 글 생성, 재작성, 구조 제안",
        )
        settings = get_settings()
        self._service = WritingService(settings=settings)

    async def execute(self, message: AgentMessage) -> AgentMessage:
        """
        글쓰기 관련 작업을 실행합니다.

        지원 작업:
        - generate: 새 글 생성
        - rewrite: 기존 글 재작성
        - suggest_structure: 챕터 구조 제안

        Args:
            message: 작업 요청 메시지

        Returns:
            작업 결과 메시지
        """
        action = message.payload.get("action", "generate")
        correlation_id = message.correlation_id

        try:
            if action == "generate":
                result = await self._handle_generate(message.payload)
            elif action == "rewrite":
                result = await self._handle_rewrite(message.payload)
            elif action == "suggest_structure":
                result = await self._handle_structure(message.payload)
            else:
                return self.create_message(
                    to_agent=message.from_agent,
                    message_type=MessageType.ERROR,
                    payload={"error": f"알 수 없는 글쓰기 작업: {action}"},
                    correlation_id=correlation_id,
                )

            return self.create_message(
                to_agent=message.from_agent,
                message_type=MessageType.FEEDBACK,
                payload={"action": action, "result": result},
                correlation_id=correlation_id,
            )

        except Exception as e:
            logger.error(f"글쓰기 에이전트 오류: {e}")
            return self.create_message(
                to_agent=message.from_agent,
                message_type=MessageType.ERROR,
                payload={"error": "글쓰기 처리 중 내부 오류가 발생했습니다.", "action": action},
                correlation_id=correlation_id,
            )

    async def _handle_generate(self, payload: dict[str, Any]) -> dict[str, Any]:
        """글 생성 작업을 처리합니다."""
        genre = Genre(payload.get("genre", "essay"))
        prompt = payload.get("prompt", "")
        context = payload.get("context", "")
        chapter_title = payload.get("chapter_title", "")

        # 스트리밍 대신 전체 텍스트 수집
        generated_text = ""
        async for chunk in self._service.generate_stream(
            genre=genre,
            prompt=prompt,
            context=context,
            chapter_title=chapter_title,
        ):
            generated_text += chunk

        return {
            "generated_text": generated_text,
            "genre": genre.value,
            "word_count": len(generated_text.replace(" ", "").replace("\n", "")),
        }

    async def _handle_rewrite(self, payload: dict[str, Any]) -> dict[str, Any]:
        """재작성 작업을 처리합니다."""
        genre = Genre(payload.get("genre", "essay"))
        result = await self._service.rewrite(
            original_text=payload.get("original_text", ""),
            instruction=payload.get("instruction", ""),
            genre=genre,
            style_guide=payload.get("style_guide", ""),
        )
        return {
            "rewritten_text": result.rewritten_text,
            "changes_summary": result.changes_summary,
        }

    async def _handle_structure(self, payload: dict[str, Any]) -> dict[str, Any]:
        """구조 제안 작업을 처리합니다."""
        genre = Genre(payload.get("genre", "essay"))
        result = await self._service.suggest_structure(
            book_title=payload.get("book_title", ""),
            genre=genre,
            description=payload.get("description", ""),
            target_chapters=payload.get("target_chapters", 10),
        )
        return {
            "chapters": [ch.model_dump() for ch in result.chapters],
            "overall_summary": result.overall_summary,
        }

    async def review(self, artifacts: list[dict[str, Any]]) -> dict[str, Any]:
        """
        생성된 글의 품질을 검토합니다.

        Args:
            artifacts: 생성된 글 목록

        Returns:
            검토 결과 (승인 여부, 품질 점수, 피드백)
        """
        total_words = sum(
            a.get("word_count", 0) for a in artifacts
        )

        # 기본 품질 검증
        issues: list[str] = []

        for idx, artifact in enumerate(artifacts):
            text = artifact.get("generated_text", "")
            word_count = artifact.get("word_count", 0)

            # 최소 글자 수 확인
            if word_count < 100:
                issues.append(f"생성물 {idx + 1}: 내용이 너무 짧습니다 ({word_count}자)")

            # 빈 텍스트 확인
            if not text.strip():
                issues.append(f"생성물 {idx + 1}: 빈 텍스트입니다")

        approved = len(issues) == 0
        score = 100.0 - (len(issues) * 15.0)
        score = max(0.0, min(100.0, score))

        return {
            "approved": approved,
            "score": score,
            "total_words": total_words,
            "issues": issues,
            "feedback": "품질 기준을 충족합니다." if approved else "개선이 필요합니다.",
        }
