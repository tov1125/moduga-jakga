"""
출판 에이전트 (A10)
PublishingService를 에이전트 프로토콜로 감싸서 내보내기 작업을 수행합니다.
"""

import logging
from typing import Any

from app.agents.base import AgentMessage, BaseAgent, MessageType
from app.core.config import get_settings
from app.schemas.design import PageSize
from app.schemas.publishing import ExportFormat
from app.services.publishing_service import PublishingService

logger = logging.getLogger(__name__)


class PublishingAgent(BaseAgent):
    """
    출판 에이전트 (A10)
    도서를 DOCX, PDF, EPUB 형식으로 내보내는 작업을 담당합니다.
    """

    def __init__(self) -> None:
        super().__init__(
            name="publishing_agent",
            description="출판/내보내기 에이전트 - DOCX, PDF, EPUB 생성",
        )
        settings = get_settings()
        self._service = PublishingService(settings=settings)

    async def execute(self, message: AgentMessage) -> AgentMessage:
        """
        내보내기 작업을 실행합니다.

        Args:
            message: 내보내기 요청 메시지

        Returns:
            내보내기 결과 메시지
        """
        action = message.payload.get("action", "export")
        correlation_id = message.correlation_id

        try:
            if action == "export":
                result = await self._handle_export(message.payload)
            else:
                return self.create_message(
                    to_agent=message.from_agent,
                    message_type=MessageType.ERROR,
                    payload={"error": f"알 수 없는 출판 작업: {action}"},
                    correlation_id=correlation_id,
                )

            return self.create_message(
                to_agent=message.from_agent,
                message_type=MessageType.APPROVAL,
                payload={"action": action, "result": result},
                correlation_id=correlation_id,
            )

        except Exception as e:
            logger.error(f"출판 에이전트 오류: {e}")
            return self.create_message(
                to_agent=message.from_agent,
                message_type=MessageType.ERROR,
                payload={"error": "출판 처리 중 내부 오류가 발생했습니다.", "action": action},
                correlation_id=correlation_id,
            )

    async def _handle_export(self, payload: dict[str, Any]) -> dict[str, Any]:
        """내보내기 작업을 처리합니다."""
        export_id = payload.get("export_id", "")
        book_data = payload.get("book_data", {})
        export_format = ExportFormat(payload.get("format", "pdf"))
        page_size = PageSize(payload.get("page_size", "A5"))

        file_path = await self._service.start_export(
            export_id=export_id,
            book_data=book_data,
            export_format=export_format,
            page_size=page_size,
            include_cover=payload.get("include_cover", True),
            include_toc=payload.get("include_toc", True),
            accessibility_tags=payload.get("accessibility_tags", True),
        )

        return {
            "export_id": export_id,
            "file_path": file_path,
            "format": export_format.value,
        }

    async def review(self, artifacts: list[dict[str, Any]]) -> dict[str, Any]:
        """
        내보내기 산출물을 검토합니다.

        Args:
            artifacts: 내보내기 결과 목록

        Returns:
            검토 결과 (파일 생성 확인, 형식 적합성 등)
        """
        issues: list[str] = []

        for idx, artifact in enumerate(artifacts):
            file_path = artifact.get("result", {}).get("file_path", "")
            if not file_path:
                issues.append(f"산출물 {idx + 1}: 파일이 생성되지 않았습니다")

        approved = len(issues) == 0

        return {
            "approved": approved,
            "score": 100.0 if approved else 0.0,
            "issues": issues,
            "feedback": "내보내기가 성공적으로 완료되었습니다." if approved else "내보내기 문제가 있습니다.",
        }
