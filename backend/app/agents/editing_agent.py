"""
편집 에이전트 (A8)
EditingService를 에이전트 프로토콜로 감싸서 반복적 편집 피드백 루프를 제공합니다.
"""

import logging
from typing import Any

from app.agents.base import AgentMessage, BaseAgent, MessageType
from app.core.config import get_settings
from app.services.editing_service import EditingService

logger = logging.getLogger(__name__)

# 편집 반복 최대 횟수 (무한 루프 방지)
MAX_EDITING_ITERATIONS = 3

# 편집 승인 임계 점수
APPROVAL_THRESHOLD = 75.0


class EditingAgent(BaseAgent):
    """
    편집 에이전트 (A8)
    4단계 편집을 수행하고, 품질 기준을 충족할 때까지
    반복적으로 피드백을 제공합니다.
    """

    def __init__(self) -> None:
        super().__init__(
            name="editing_agent",
            description="4단계 편집 에이전트 - 구조, 내용, 교정, 최종 검토",
        )
        settings = get_settings()
        self._service = EditingService(settings=settings)

    async def execute(self, message: AgentMessage) -> AgentMessage:
        """
        편집 작업을 실행합니다.

        반복적 편집 루프:
        1. 교정/문체 검사 실행
        2. 품질 점수 확인
        3. 기준 미달 시 피드백 제공 및 재검사 요청
        4. 기준 충족 또는 최대 반복 도달 시 종료

        Args:
            message: 편집 요청 메시지

        Returns:
            편집 결과 메시지
        """
        action = message.payload.get("action", "full_review")
        correlation_id = message.correlation_id

        try:
            if action == "proofread":
                result = await self._handle_proofread(message.payload)
            elif action == "style_check":
                result = await self._handle_style_check(message.payload)
            elif action == "structure_review":
                result = await self._handle_structure_review(message.payload)
            elif action == "full_review":
                result = await self._handle_full_review_with_loop(message.payload)
            else:
                return self.create_message(
                    to_agent=message.from_agent,
                    message_type=MessageType.ERROR,
                    payload={"error": f"알 수 없는 편집 작업: {action}"},
                    correlation_id=correlation_id,
                )

            # 점수에 따라 승인/거부 결정
            score = result.get("score", 0.0)
            msg_type = (
                MessageType.APPROVAL if score >= APPROVAL_THRESHOLD
                else MessageType.REJECTION
            )

            return self.create_message(
                to_agent=message.from_agent,
                message_type=msg_type,
                payload={"action": action, "result": result},
                correlation_id=correlation_id,
            )

        except Exception as e:
            logger.error(f"편집 에이전트 오류: {e}")
            return self.create_message(
                to_agent=message.from_agent,
                message_type=MessageType.ERROR,
                payload={"error": str(e), "action": action},
                correlation_id=correlation_id,
            )

    async def _handle_proofread(self, payload: dict[str, Any]) -> dict[str, Any]:
        """교정 작업을 처리합니다."""
        text = payload.get("text", "")
        result = await self._service.proofread(text)
        return {
            "corrected_text": result.corrected_text,
            "corrections_count": result.total_corrections,
            "score": result.accuracy_score,
        }

    async def _handle_style_check(self, payload: dict[str, Any]) -> dict[str, Any]:
        """문체 검사 작업을 처리합니다."""
        text = payload.get("text", "")
        genre = payload.get("genre", "")
        result = await self._service.check_style(text, genre=genre)
        return {
            "issues_count": len(result.issues),
            "score": result.consistency_score,
            "feedback": result.overall_feedback,
        }

    async def _handle_structure_review(self, payload: dict[str, Any]) -> dict[str, Any]:
        """구조 검토 작업을 처리합니다."""
        chapters = payload.get("chapters", [])
        result = await self._service.review_structure(chapters)
        avg_score = (result.flow_score + result.organization_score) / 2
        return {
            "flow_score": result.flow_score,
            "organization_score": result.organization_score,
            "score": avg_score,
            "feedback": result.feedback,
            "suggestions": result.suggestions,
        }

    async def _handle_full_review_with_loop(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        반복적 편집 루프를 포함한 전체 검토를 수행합니다.
        품질 기준을 충족하거나 최대 반복 횟수에 도달할 때까지 반복합니다.
        """
        book_id = payload.get("book_id", "")
        chapters = payload.get("chapters", [])
        iteration = 0
        best_score = 0.0
        all_feedback: list[str] = []

        while iteration < MAX_EDITING_ITERATIONS:
            iteration += 1
            logger.info(
                f"편집 반복 {iteration}/{MAX_EDITING_ITERATIONS} (도서: {book_id})"
            )

            # 전체 편집 수행
            report = await self._service.full_review(
                book_id=book_id,
                chapters=chapters,
            )

            current_score = report.overall_score
            all_feedback.append(
                f"[반복 {iteration}] 점수: {current_score:.1f} - {report.summary}"
            )

            if current_score > best_score:
                best_score = current_score

            # 품질 기준 충족 시 종료
            if current_score >= APPROVAL_THRESHOLD:
                logger.info(
                    f"편집 품질 기준 충족 (점수: {current_score:.1f})"
                )
                break

            logger.info(
                f"편집 품질 미달 ({current_score:.1f} < {APPROVAL_THRESHOLD}), "
                f"피드백 제공 후 재검사"
            )

        return {
            "book_id": book_id,
            "score": best_score,
            "iterations": iteration,
            "feedback_history": all_feedback,
            "recommendations": report.recommendations if report else [],
            "approved": best_score >= APPROVAL_THRESHOLD,
        }

    async def review(self, artifacts: list[dict[str, Any]]) -> dict[str, Any]:
        """
        편집 산출물을 검토합니다.

        Args:
            artifacts: 편집 결과 목록

        Returns:
            검토 결과
        """
        if not artifacts:
            return {
                "approved": False,
                "score": 0.0,
                "feedback": "검토할 산출물이 없습니다.",
            }

        avg_score = sum(a.get("score", 0.0) for a in artifacts) / len(artifacts)
        approved = avg_score >= APPROVAL_THRESHOLD

        return {
            "approved": approved,
            "score": avg_score,
            "feedback": (
                "편집 품질이 우수합니다." if approved
                else f"편집 품질 개선이 필요합니다 (현재: {avg_score:.1f}, 기준: {APPROVAL_THRESHOLD})"
            ),
        }
