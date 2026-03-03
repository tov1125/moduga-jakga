"""
품질 보증 에이전트 (A16)
전체 파이프라인의 산출물이 품질 기준을 충족하는지 검증합니다.
"""

import logging
from typing import Any

from app.agents.base import AgentMessage, BaseAgent, MessageType

logger = logging.getLogger(__name__)

# 품질 게이트 기준
QUALITY_GATES: dict[str, dict[str, Any]] = {
    "writing": {
        "min_word_count": 500,          # 최소 글자 수
        "min_chapter_count": 1,         # 최소 챕터 수
        "max_repetition_ratio": 0.3,    # 반복 비율 상한
    },
    "editing": {
        "min_accuracy_score": 80.0,     # 최소 정확도 점수
        "min_style_score": 70.0,        # 최소 문체 일관성 점수
        "max_error_count": 10,          # 최대 오류 허용 수
    },
    "design": {
        "cover_required": True,         # 표지 필수 여부
        "min_pages": 10,                # 최소 페이지 수
    },
    "publishing": {
        "file_generated": True,         # 파일 생성 필수
        "min_file_size": 1024,          # 최소 파일 크기 (bytes)
    },
}


class QualityAgent(BaseAgent):
    """
    품질 보증 에이전트 (A16)
    각 단계의 산출물이 정의된 품질 게이트를 통과하는지 검증합니다.
    """

    def __init__(self) -> None:
        super().__init__(
            name="quality_agent",
            description="품질 보증 에이전트 - 품질 게이트 검증 및 종합 평가",
        )

    async def execute(self, message: AgentMessage) -> AgentMessage:
        """
        품질 검증을 실행합니다.

        Args:
            message: 검증 요청 메시지

        Returns:
            검증 결과 메시지
        """
        stage = message.payload.get("stage", "")
        artifacts = message.payload.get("artifacts", [])
        correlation_id = message.correlation_id

        try:
            result = await self._validate_quality_gate(stage, artifacts)

            msg_type = (
                MessageType.APPROVAL if result["passed"]
                else MessageType.REJECTION
            )

            return self.create_message(
                to_agent=message.from_agent,
                message_type=msg_type,
                payload={"stage": stage, "result": result},
                correlation_id=correlation_id,
            )

        except Exception as e:
            logger.error(f"품질 검증 오류: {e}")
            return self.create_message(
                to_agent=message.from_agent,
                message_type=MessageType.ERROR,
                payload={"error": "품질 검증 중 내부 오류가 발생했습니다.", "stage": stage},
                correlation_id=correlation_id,
            )

    async def _validate_quality_gate(
        self,
        stage: str,
        artifacts: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        특정 단계의 품질 게이트를 검증합니다.

        Args:
            stage: 검증할 단계 이름
            artifacts: 검증할 산출물 목록

        Returns:
            검증 결과 (통과 여부, 세부 결과, 점수)
        """
        gate = QUALITY_GATES.get(stage)
        if not gate:
            return {
                "passed": True,
                "score": 100.0,
                "details": f"'{stage}' 단계에 대한 품질 게이트가 정의되지 않았습니다.",
                "violations": [],
            }

        violations: list[str] = []

        if stage == "writing":
            violations.extend(self._check_writing_quality(artifacts, gate))
        elif stage == "editing":
            violations.extend(self._check_editing_quality(artifacts, gate))
        elif stage == "design":
            violations.extend(self._check_design_quality(artifacts, gate))
        elif stage == "publishing":
            violations.extend(self._check_publishing_quality(artifacts, gate))

        passed = len(violations) == 0
        score = max(0.0, 100.0 - len(violations) * 15.0)

        return {
            "passed": passed,
            "score": score,
            "stage": stage,
            "violations": violations,
            "details": (
                f"품질 게이트 통과 ({stage})"
                if passed
                else f"품질 게이트 미통과: {len(violations)}개 위반 ({stage})"
            ),
        }

    def _check_writing_quality(
        self,
        artifacts: list[dict[str, Any]],
        gate: dict[str, Any],
    ) -> list[str]:
        """글쓰기 품질을 검사합니다."""
        violations: list[str] = []

        total_words = sum(a.get("word_count", 0) for a in artifacts)
        if total_words < gate.get("min_word_count", 0):
            violations.append(
                f"총 글자 수({total_words})가 최소 기준({gate['min_word_count']})에 미달합니다."
            )

        if len(artifacts) < gate.get("min_chapter_count", 0):
            violations.append(
                f"챕터 수({len(artifacts)})가 최소 기준({gate['min_chapter_count']})에 미달합니다."
            )

        return violations

    def _check_editing_quality(
        self,
        artifacts: list[dict[str, Any]],
        gate: dict[str, Any],
    ) -> list[str]:
        """편집 품질을 검사합니다."""
        violations: list[str] = []

        for a in artifacts:
            score = a.get("score", 0.0)
            if score < gate.get("min_accuracy_score", 0):
                violations.append(
                    f"정확도 점수({score:.1f})가 최소 기준({gate['min_accuracy_score']})에 미달합니다."
                )

            error_count = a.get("corrections_count", 0)
            if error_count > gate.get("max_error_count", 0):
                violations.append(
                    f"오류 수({error_count})가 허용 범위({gate['max_error_count']})를 초과합니다."
                )

        return violations

    def _check_design_quality(
        self,
        artifacts: list[dict[str, Any]],
        gate: dict[str, Any],
    ) -> list[str]:
        """디자인 품질을 검사합니다."""
        violations: list[str] = []

        has_cover = any(
            a.get("result", {}).get("image_url") for a in artifacts
        )
        if gate.get("cover_required", False) and not has_cover:
            violations.append("표지 이미지가 필수이지만 생성되지 않았습니다.")

        for a in artifacts:
            pages = a.get("result", {}).get("total_pages", 0)
            if pages > 0 and pages < gate.get("min_pages", 0):
                violations.append(
                    f"페이지 수({pages})가 최소 기준({gate['min_pages']})에 미달합니다."
                )

        return violations

    def _check_publishing_quality(
        self,
        artifacts: list[dict[str, Any]],
        gate: dict[str, Any],
    ) -> list[str]:
        """출판 품질을 검사합니다."""
        violations: list[str] = []

        for a in artifacts:
            file_path = a.get("result", {}).get("file_path", "")
            if gate.get("file_generated", False) and not file_path:
                violations.append("내보내기 파일이 생성되지 않았습니다.")

        return violations

    async def review(self, artifacts: list[dict[str, Any]]) -> dict[str, Any]:
        """
        모든 단계의 산출물을 종합 검토합니다.

        Args:
            artifacts: 전체 산출물 목록

        Returns:
            종합 검토 결과
        """
        all_violations: list[str] = []

        for artifact in artifacts:
            stage = artifact.get("stage", "")
            stage_artifacts = artifact.get("artifacts", [artifact])
            result = await self._validate_quality_gate(stage, stage_artifacts)
            all_violations.extend(result.get("violations", []))

        passed = len(all_violations) == 0
        score = max(0.0, 100.0 - len(all_violations) * 10.0)

        return {
            "approved": passed,
            "score": score,
            "total_violations": len(all_violations),
            "violations": all_violations,
            "feedback": (
                "모든 품질 게이트를 통과했습니다." if passed
                else f"총 {len(all_violations)}개의 품질 기준 위반이 발견되었습니다."
            ),
        }
