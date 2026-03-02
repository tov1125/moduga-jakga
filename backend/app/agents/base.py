"""
에이전트 기본 모듈
모든 에이전트가 상속하는 기본 클래스와 메시지 프로토콜을 정의합니다.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from pydantic import BaseModel


class MessageType(str, Enum):
    """에이전트 간 메시지 유형 열거형"""
    HANDOFF = "handoff"                   # 작업 위임
    REVIEW_REQUEST = "review_request"     # 검토 요청
    FEEDBACK = "feedback"                 # 피드백
    APPROVAL = "approval"                 # 승인
    REJECTION = "rejection"               # 거부
    STATUS_UPDATE = "status_update"       # 상태 업데이트
    ERROR = "error"                       # 오류


class AgentMessage(BaseModel):
    """에이전트 간 통신 메시지"""
    from_agent: str                       # 발신 에이전트 이름
    to_agent: str                         # 수신 에이전트 이름
    message_type: MessageType             # 메시지 유형
    payload: dict[str, Any]               # 메시지 데이터
    correlation_id: str = ""              # 작업 추적 ID


class AgentResult(BaseModel):
    """에이전트 실행 결과"""
    success: bool
    agent_name: str
    message: str
    data: dict[str, Any] = {}
    artifacts: list[dict[str, Any]] = []  # 생성물 (파일, 텍스트 등)


class BaseAgent(ABC):
    """
    에이전트 기본 추상 클래스.
    모든 에이전트는 이 클래스를 상속하여 execute와 review를 구현해야 합니다.
    """

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, message: AgentMessage) -> AgentMessage:
        """
        에이전트의 주요 작업을 실행합니다.

        Args:
            message: 수신된 에이전트 메시지

        Returns:
            처리 결과를 담은 응답 메시지
        """
        ...

    @abstractmethod
    async def review(self, artifacts: list[dict[str, Any]]) -> dict[str, Any]:
        """
        생성물을 검토하고 피드백을 반환합니다.

        Args:
            artifacts: 검토할 생성물 목록

        Returns:
            검토 결과 딕셔너리 (승인 여부, 피드백, 점수 등)
        """
        ...

    def create_message(
        self,
        to_agent: str,
        message_type: MessageType,
        payload: dict[str, Any],
        correlation_id: str = "",
    ) -> AgentMessage:
        """응답 메시지를 생성합니다."""
        return AgentMessage(
            from_agent=self.name,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
            correlation_id=correlation_id,
        )
