"""
오케스트레이터 에이전트 (A0)
전체 작업 흐름을 관리하고 적절한 에이전트에게 작업을 위임합니다.
"""

import logging
from typing import Any

from app.agents.base import AgentMessage, BaseAgent, MessageType

logger = logging.getLogger(__name__)

# 에이전트 라우팅 맵: 작업 유형 → 담당 에이전트 이름
TASK_ROUTING: dict[str, str] = {
    "write": "writing_agent",           # A7: AI 글쓰기
    "edit": "editing_agent",            # A8: 편집
    "design": "design_agent",           # A9: 디자인
    "publish": "publishing_agent",      # A10: 출판
    "quality_check": "quality_agent",   # A16: 품질 검증
    "accessibility": "accessibility_agent",  # A17: 접근성 감사
    "user_test": "user_advocate_agent",      # A18: 사용자 대변
}


class OrchestratorAgent(BaseAgent):
    """
    오케스트레이터 에이전트 (A0)
    작업을 분석하고 적절한 전문 에이전트에게 라우팅합니다.
    파이프라인 흐름: 글쓰기 → 편집 → 디자인 → 출판
    """

    def __init__(self) -> None:
        super().__init__(
            name="orchestrator",
            description="전체 워크플로우를 관리하는 오케스트레이터 에이전트",
        )
        self._agents: dict[str, BaseAgent] = {}
        self._pipeline_order = [
            "writing_agent",
            "editing_agent",
            "design_agent",
            "publishing_agent",
        ]

    def register_agent(self, agent: BaseAgent) -> None:
        """에이전트를 등록합니다."""
        self._agents[agent.name] = agent
        logger.info(f"에이전트 등록: {agent.name}")

    async def execute(self, message: AgentMessage) -> AgentMessage:
        """
        수신된 메시지를 분석하고 적절한 에이전트에게 라우팅합니다.

        Args:
            message: 작업 요청 메시지

        Returns:
            처리 결과 메시지
        """
        task_type = message.payload.get("task_type", "")
        target_agent_name = TASK_ROUTING.get(task_type)

        if not target_agent_name:
            return self.create_message(
                to_agent=message.from_agent,
                message_type=MessageType.ERROR,
                payload={
                    "error": f"알 수 없는 작업 유형: {task_type}",
                    "available_tasks": list(TASK_ROUTING.keys()),
                },
                correlation_id=message.correlation_id,
            )

        target_agent = self._agents.get(target_agent_name)
        if not target_agent:
            return self.create_message(
                to_agent=message.from_agent,
                message_type=MessageType.ERROR,
                payload={
                    "error": f"에이전트를 찾을 수 없습니다: {target_agent_name}",
                },
                correlation_id=message.correlation_id,
            )

        logger.info(
            f"작업 라우팅: {task_type} → {target_agent_name} "
            f"(correlation_id: {message.correlation_id})"
        )

        # 대상 에이전트에게 작업 위임
        delegated_message = self.create_message(
            to_agent=target_agent_name,
            message_type=MessageType.HANDOFF,
            payload=message.payload,
            correlation_id=message.correlation_id,
        )

        result = await target_agent.execute(delegated_message)
        return result

    async def execute_pipeline(
        self,
        book_id: str,
        stages: list[str] | None = None,
    ) -> list[AgentMessage]:
        """
        전체 파이프라인을 순차 실행합니다.
        글쓰기 → 편집 → 디자인 → 출판 흐름을 관리합니다.

        Args:
            book_id: 도서 ID
            stages: 실행할 단계 목록 (None이면 전체)

        Returns:
            각 단계의 결과 메시지 목록
        """
        pipeline = stages or self._pipeline_order
        results: list[AgentMessage] = []

        for agent_name in pipeline:
            agent = self._agents.get(agent_name)
            if not agent:
                logger.warning(f"파이프라인 에이전트 누락: {agent_name}")
                continue

            message = self.create_message(
                to_agent=agent_name,
                message_type=MessageType.HANDOFF,
                payload={"book_id": book_id},
                correlation_id=f"pipeline-{book_id}",
            )

            try:
                result = await agent.execute(message)
                results.append(result)

                # 거부 또는 오류 시 파이프라인 중단
                if result.message_type in (MessageType.REJECTION, MessageType.ERROR):
                    logger.warning(
                        f"파이프라인 중단: {agent_name} - {result.payload}"
                    )
                    break

            except Exception as e:
                logger.error(f"파이프라인 오류 ({agent_name}): {e}")
                error_msg = self.create_message(
                    to_agent="orchestrator",
                    message_type=MessageType.ERROR,
                    payload={"error": "파이프라인 처리 중 내부 오류가 발생했습니다.", "stage": agent_name},
                    correlation_id=f"pipeline-{book_id}",
                )
                results.append(error_msg)
                break

        return results

    async def review(self, artifacts: list[dict[str, Any]]) -> dict[str, Any]:
        """
        전체 워크플로우의 산출물을 종합 검토합니다.

        Args:
            artifacts: 각 에이전트의 산출물 목록

        Returns:
            종합 검토 결과
        """
        total_artifacts = len(artifacts)
        approved = sum(1 for a in artifacts if a.get("approved", False))

        return {
            "total_artifacts": total_artifacts,
            "approved": approved,
            "rejected": total_artifacts - approved,
            "overall_status": "approved" if approved == total_artifacts else "needs_review",
            "summary": (
                f"총 {total_artifacts}개 산출물 중 {approved}개 승인, "
                f"{total_artifacts - approved}개 검토 필요"
            ),
        }
