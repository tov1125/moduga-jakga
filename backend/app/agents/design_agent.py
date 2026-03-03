"""
디자인 에이전트 (A9)
DesignService를 에이전트 프로토콜로 감싸서 표지 및 내지 디자인을 수행합니다.
"""

import logging
from typing import Any

from app.agents.base import AgentMessage, BaseAgent, MessageType
from app.core.config import get_settings
from app.schemas.book import Genre
from app.schemas.design import CoverStyle, PageSize
from app.services.design_service import DesignService

logger = logging.getLogger(__name__)


class DesignAgent(BaseAgent):
    """
    디자인 에이전트 (A9)
    DALL-E를 사용한 표지 생성과 Typst 기반 내지 조판을 담당합니다.
    """

    def __init__(self) -> None:
        super().__init__(
            name="design_agent",
            description="도서 디자인 에이전트 - 표지 생성, 내지 레이아웃",
        )
        settings = get_settings()
        self._service = DesignService(settings=settings)

    async def execute(self, message: AgentMessage) -> AgentMessage:
        """
        디자인 작업을 실행합니다.

        지원 작업:
        - generate_cover: 표지 이미지 생성
        - layout_preview: 내지 레이아웃 미리보기

        Args:
            message: 디자인 요청 메시지

        Returns:
            디자인 결과 메시지
        """
        action = message.payload.get("action", "generate_cover")
        correlation_id = message.correlation_id

        try:
            if action == "generate_cover":
                result = await self._handle_cover(message.payload)
            elif action == "layout_preview":
                result = await self._handle_layout(message.payload)
            else:
                return self.create_message(
                    to_agent=message.from_agent,
                    message_type=MessageType.ERROR,
                    payload={"error": f"알 수 없는 디자인 작업: {action}"},
                    correlation_id=correlation_id,
                )

            return self.create_message(
                to_agent=message.from_agent,
                message_type=MessageType.FEEDBACK,
                payload={"action": action, "result": result},
                correlation_id=correlation_id,
            )

        except Exception as e:
            logger.error(f"디자인 에이전트 오류: {e}")
            return self.create_message(
                to_agent=message.from_agent,
                message_type=MessageType.ERROR,
                payload={"error": "디자인 처리 중 내부 오류가 발생했습니다.", "action": action},
                correlation_id=correlation_id,
            )

    async def _handle_cover(self, payload: dict[str, Any]) -> dict[str, Any]:
        """표지 생성 작업을 처리합니다."""
        genre = Genre(payload.get("genre", "essay"))
        style = CoverStyle(payload.get("style", "minimalist"))

        result = await self._service.generate_cover(
            book_title=payload.get("book_title", ""),
            author_name=payload.get("author_name", ""),
            genre=genre,
            style=style,
            description=payload.get("description", ""),
            color_scheme=payload.get("color_scheme", ""),
        )

        return {
            "image_url": result.image_url,
            "prompt_used": result.prompt_used,
            "style": result.style.value,
        }

    async def _handle_layout(self, payload: dict[str, Any]) -> dict[str, Any]:
        """레이아웃 미리보기 작업을 처리합니다."""
        page_size = PageSize(payload.get("page_size", "A5"))

        result = await self._service.generate_layout_preview(
            book_id=payload.get("book_id", ""),
            page_size=page_size,
            font_size=payload.get("font_size", 11.0),
            line_spacing=payload.get("line_spacing", 1.6),
        )

        return {
            "preview_url": result.preview_url,
            "total_pages": result.total_pages,
            "page_size": result.page_size.value,
        }

    async def review(self, artifacts: list[dict[str, Any]]) -> dict[str, Any]:
        """
        디자인 산출물을 검토합니다.

        Args:
            artifacts: 디자인 결과 목록

        Returns:
            검토 결과 (표지 품질, 레이아웃 적합성 등)
        """
        issues: list[str] = []

        for idx, artifact in enumerate(artifacts):
            # 표지 이미지 URL 확인
            if artifact.get("action") == "generate_cover":
                if not artifact.get("result", {}).get("image_url"):
                    issues.append(f"산출물 {idx + 1}: 표지 이미지가 생성되지 않았습니다")

            # 레이아웃 페이지 수 확인
            if artifact.get("action") == "layout_preview":
                total_pages = artifact.get("result", {}).get("total_pages", 0)
                if total_pages < 1:
                    issues.append(f"산출물 {idx + 1}: 레이아웃 페이지가 0입니다")

        approved = len(issues) == 0
        score = 100.0 - (len(issues) * 20.0)

        return {
            "approved": approved,
            "score": max(0.0, score),
            "issues": issues,
            "feedback": "디자인이 양호합니다." if approved else "디자인 수정이 필요합니다.",
        }
