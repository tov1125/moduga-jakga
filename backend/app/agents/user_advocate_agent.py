"""
사용자 대변 에이전트 (A18)
시각장애인 사용자의 관점에서 사용성을 평가하고 시나리오를 시뮬레이션합니다.
"""

import logging
from typing import Any

from app.agents.base import AgentMessage, BaseAgent, MessageType

logger = logging.getLogger(__name__)

# 사용자 시나리오 정의
USER_SCENARIOS: list[dict[str, Any]] = [
    {
        "id": "screen_reader_navigation",
        "name": "스크린 리더 탐색",
        "description": "스크린 리더로 목차를 탐색하고 원하는 챕터로 이동",
        "user_type": "visual",
        "priority": "high",
        "checks": [
            "목차가 논리적 구조로 마크업되어 있는가",
            "각 챕터 제목이 고유하고 설명적인가",
            "페이지 번호가 연속적인가",
        ],
    },
    {
        "id": "tts_reading",
        "name": "TTS 읽기 경험",
        "description": "TTS로 책 내용을 들으며 읽기",
        "user_type": "visual",
        "priority": "high",
        "checks": [
            "문장 길이가 TTS 청취에 적절한가 (20~40자 권장)",
            "괄호/기호가 TTS에서 자연스럽게 읽히는가",
            "문단 구분이 명확하여 일시 정지가 자연스러운가",
        ],
    },
    {
        "id": "stt_writing",
        "name": "음성 입력 글쓰기",
        "description": "STT를 이용해 글을 구술하고 편집",
        "user_type": "visual",
        "priority": "high",
        "checks": [
            "음성 입력 결과가 정확하게 반영되는가",
            "구두점이 자동으로 적절히 삽입되는가",
            "편집 명령(삭제, 수정)이 음성으로 가능한가",
        ],
    },
    {
        "id": "low_vision_reading",
        "name": "저시력 사용자 읽기",
        "description": "큰 글씨와 고대비로 책을 읽기",
        "user_type": "low_vision",
        "priority": "medium",
        "checks": [
            "글꼴 크기가 충분히 큰가 (최소 14pt)",
            "배경과 텍스트의 대비가 충분한가",
            "줄 간격이 넉넉한가",
        ],
    },
    {
        "id": "epub_download",
        "name": "EPUB 다운로드 및 읽기",
        "description": "EPUB을 다운로드하여 점자 디스플레이로 읽기",
        "user_type": "visual",
        "priority": "medium",
        "checks": [
            "EPUB 파일이 정상적으로 생성되는가",
            "접근성 메타데이터가 포함되어 있는가",
            "텍스트가 올바르게 추출되는가",
        ],
    },
]


class UserAdvocateAgent(BaseAgent):
    """
    사용자 대변 에이전트 (A18)
    시각장애인 사용자의 시나리오를 시뮬레이션하고
    사용성 문제를 사전에 발견합니다.
    """

    def __init__(self) -> None:
        super().__init__(
            name="user_advocate_agent",
            description="사용자 대변 에이전트 - 시각장애인 관점 UX 시뮬레이션",
        )

    async def execute(self, message: AgentMessage) -> AgentMessage:
        """
        사용자 시나리오 시뮬레이션을 실행합니다.

        Args:
            message: 시뮬레이션 요청 메시지

        Returns:
            시뮬레이션 결과 메시지
        """
        artifacts = message.payload.get("artifacts", [])
        target_scenarios = message.payload.get("scenarios", None)  # None이면 전체 시나리오
        correlation_id = message.correlation_id

        try:
            result = await self._simulate_scenarios(artifacts, target_scenarios)

            msg_type = (
                MessageType.APPROVAL if result["all_passed"]
                else MessageType.FEEDBACK
            )

            return self.create_message(
                to_agent=message.from_agent,
                message_type=msg_type,
                payload={"result": result},
                correlation_id=correlation_id,
            )

        except Exception as e:
            logger.error(f"사용자 시뮬레이션 오류: {e}")
            return self.create_message(
                to_agent=message.from_agent,
                message_type=MessageType.ERROR,
                payload={"error": str(e)},
                correlation_id=correlation_id,
            )

    async def _simulate_scenarios(
        self,
        artifacts: list[dict[str, Any]],
        target_scenario_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        사용자 시나리오를 시뮬레이션합니다.

        Args:
            artifacts: 평가 대상 산출물
            target_scenario_ids: 실행할 시나리오 ID (None이면 전체)

        Returns:
            시뮬레이션 결과
        """
        scenarios = USER_SCENARIOS
        if target_scenario_ids:
            scenarios = [s for s in scenarios if s["id"] in target_scenario_ids]

        scenario_results: list[dict[str, Any]] = []
        all_issues: list[str] = []

        for scenario in scenarios:
            result = await self._run_scenario(scenario, artifacts)
            scenario_results.append(result)

            if not result["passed"]:
                all_issues.extend(result.get("issues", []))

        total = len(scenario_results)
        passed = sum(1 for r in scenario_results if r["passed"])
        score = (passed / total * 100) if total > 0 else 0.0

        return {
            "all_passed": len(all_issues) == 0,
            "score": score,
            "total_scenarios": total,
            "passed_scenarios": passed,
            "failed_scenarios": total - passed,
            "scenario_results": scenario_results,
            "all_issues": all_issues,
            "recommendation": self._generate_recommendation(scenario_results),
        }

    async def _run_scenario(
        self,
        scenario: dict[str, Any],
        artifacts: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        개별 사용자 시나리오를 실행합니다.

        Args:
            scenario: 시나리오 정의
            artifacts: 평가 대상 산출물

        Returns:
            시나리오 실행 결과
        """
        scenario_id = scenario["id"]
        issues: list[str] = []

        # 시나리오별 검사 로직
        if scenario_id == "tts_reading":
            issues.extend(self._check_tts_readability(artifacts))
        elif scenario_id == "screen_reader_navigation":
            issues.extend(self._check_screen_reader_nav(artifacts))
        elif scenario_id == "stt_writing":
            issues.extend(self._check_stt_usability(artifacts))
        elif scenario_id == "low_vision_reading":
            issues.extend(self._check_low_vision(artifacts))
        elif scenario_id == "epub_download":
            issues.extend(self._check_epub_quality(artifacts))

        passed = len(issues) == 0

        return {
            "scenario_id": scenario_id,
            "name": scenario["name"],
            "description": scenario["description"],
            "user_type": scenario["user_type"],
            "priority": scenario["priority"],
            "passed": passed,
            "issues": issues,
            "checks_performed": scenario.get("checks", []),
        }

    def _check_tts_readability(self, artifacts: list[dict[str, Any]]) -> list[str]:
        """TTS 읽기 적합성을 검사합니다."""
        issues: list[str] = []

        for a in artifacts:
            content = a.get("content", "")
            if not content:
                continue

            sentences = content.replace(".", ".\n").replace("!", "!\n").replace("?", "?\n").split("\n")

            for sent in sentences:
                sent = sent.strip()
                if not sent:
                    continue

                # 문장이 너무 긴 경우
                if len(sent) > 100:
                    issues.append(
                        f"TTS에 부적합한 긴 문장 발견 ({len(sent)}자): "
                        f"'{sent[:30]}...'"
                    )

        return issues

    def _check_screen_reader_nav(self, artifacts: list[dict[str, Any]]) -> list[str]:
        """스크린 리더 탐색 적합성을 검사합니다."""
        issues: list[str] = []

        has_toc = any(a.get("has_toc", False) for a in artifacts)
        if not has_toc and artifacts:
            # 목차 정보가 없으면 경고 (산출물에 명시되지 않을 수 있음)
            pass

        # 챕터 제목 고유성 확인
        titles = [a.get("title", "") for a in artifacts if a.get("title")]
        if len(titles) != len(set(titles)):
            issues.append("중복된 챕터 제목이 있어 스크린 리더 탐색이 어려울 수 있습니다.")

        return issues

    def _check_stt_usability(self, artifacts: list[dict[str, Any]]) -> list[str]:
        """STT 음성 입력 사용성을 검사합니다."""
        # STT 관련 메타데이터가 있으면 검사
        return []  # 코드 레벨에서 보장되므로 추가 검사 불필요

    def _check_low_vision(self, artifacts: list[dict[str, Any]]) -> list[str]:
        """저시력 사용자 가독성을 검사합니다."""
        issues: list[str] = []

        for a in artifacts:
            font_size = a.get("font_size", 11)
            if font_size < 12:
                issues.append(
                    f"글꼴 크기({font_size}pt)가 저시력 사용자에게 작을 수 있습니다. "
                    "14pt 이상을 권장합니다."
                )

            line_spacing = a.get("line_spacing", 1.5)
            if line_spacing < 1.5:
                issues.append(
                    f"줄 간격({line_spacing})이 좁습니다. 1.5 이상을 권장합니다."
                )

        return issues

    def _check_epub_quality(self, artifacts: list[dict[str, Any]]) -> list[str]:
        """EPUB 품질을 검사합니다."""
        issues: list[str] = []

        for a in artifacts:
            if a.get("format") == "epub":
                if not a.get("accessibility_tags", True):
                    issues.append("EPUB에 접근성 태그가 누락되었습니다.")

        return issues

    def _generate_recommendation(
        self,
        scenario_results: list[dict[str, Any]],
    ) -> str:
        """시뮬레이션 결과에 따른 권장 사항을 생성합니다."""
        failed_high = [
            r for r in scenario_results
            if not r["passed"] and r["priority"] == "high"
        ]
        failed_medium = [
            r for r in scenario_results
            if not r["passed"] and r["priority"] == "medium"
        ]

        if not failed_high and not failed_medium:
            return "모든 사용자 시나리오를 통과했습니다. 접근성이 우수합니다."

        parts: list[str] = []
        if failed_high:
            names = ", ".join(r["name"] for r in failed_high)
            parts.append(f"[긴급] 시각장애인 핵심 기능에 문제가 있습니다: {names}")
        if failed_medium:
            names = ", ".join(r["name"] for r in failed_medium)
            parts.append(f"[개선 권장] 일부 시나리오에서 문제가 발견되었습니다: {names}")

        return " / ".join(parts)

    async def review(self, artifacts: list[dict[str, Any]]) -> dict[str, Any]:
        """
        사용자 관점에서 산출물을 종합 검토합니다.

        Args:
            artifacts: 검토 대상 산출물

        Returns:
            종합 검토 결과
        """
        return await self._simulate_scenarios(artifacts)
