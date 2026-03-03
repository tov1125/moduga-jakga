"""
4단계 편집 서비스 모듈
구조 편집, 내용 편집, 교정/교열, 최종 검토를 제공합니다.

편집 단계:
    1단계 - 구조 편집: 전체 흐름과 챕터 구성 검토
    2단계 - 내용 편집: 문장 개선, 문체 일관성 검사
    3단계 - 교정/교열: 맞춤법, 문법, 구두점 교정
    4단계 - 최종 검토: 조판 후 오탈자 확인
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any

from openai import AsyncOpenAI

from app.core.config import Settings
from app.schemas.editing import (
    CorrectionItem,
    EditingStage,
    ProofreadResult,
    QualityReport,
    SeverityLevel,
    StageResult,
    StyleCheckResult,
    StyleIssue,
    StructureReviewResult,
)

logger = logging.getLogger(__name__)


class EditingService:
    """4단계 편집 엔진 서비스"""

    def __init__(self, settings: Settings) -> None:
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = "gpt-4o"

    # ──────────────────────────────────────────────
    # 3단계: 교정/교열
    # ──────────────────────────────────────────────

    async def proofread(
        self,
        text: str,
        check_spelling: bool = True,
        check_grammar: bool = True,
        check_punctuation: bool = True,
    ) -> ProofreadResult:
        """
        텍스트의 맞춤법, 문법, 구두점 오류를 교정합니다.

        Args:
            text: 교정할 텍스트
            check_spelling: 맞춤법 검사 여부
            check_grammar: 문법 검사 여부
            check_punctuation: 구두점 검사 여부

        Returns:
            교정 결과 (수정된 텍스트, 교정 항목 목록, 정확도 점수)
        """
        check_items = []
        if check_spelling:
            check_items.append("맞춤법")
        if check_grammar:
            check_items.append("문법")
        if check_punctuation:
            check_items.append("구두점/띄어쓰기")

        system_prompt = (
            "당신은 한국어 교정/교열 전문가입니다. "
            f"다음 항목을 검사하세요: {', '.join(check_items)}. "
            "JSON 형식으로 교정 결과를 반환하세요."
        )

        user_message = (
            f"[교정할 텍스트]\n{text}\n\n"
            "JSON 형식으로 응답하세요:\n"
            "{\n"
            '  "corrected_text": "교정된 전체 텍스트",\n'
            '  "corrections": [\n'
            "    {\n"
            '      "original": "원본 표현",\n'
            '      "corrected": "수정 표현",\n'
            '      "reason": "수정 이유",\n'
            '      "position_start": 0,\n'
            '      "position_end": 5,\n'
            '      "severity": "error|warning|info|suggestion"\n'
            "    }\n"
            "  ],\n"
            '  "accuracy_score": 85.0\n'
            "}"
        )

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=4096,
                temperature=0.2,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or "{}"
            result: dict[str, Any] = json.loads(content)

            corrections = [
                CorrectionItem(
                    original=c.get("original", ""),
                    corrected=c.get("corrected", ""),
                    reason=c.get("reason", ""),
                    position_start=c.get("position_start", 0),
                    position_end=c.get("position_end", 0),
                    severity=SeverityLevel(c.get("severity", "info")),
                )
                for c in result.get("corrections", [])
            ]

            return ProofreadResult(
                corrected_text=result.get("corrected_text", text),
                corrections=corrections,
                total_corrections=len(corrections),
                accuracy_score=result.get("accuracy_score", 100.0),
            )

        except Exception as e:
            logger.error(f"교정 처리 중 오류: {e}")
            raise

    # ──────────────────────────────────────────────
    # 2단계: 내용 편집 (문체 검사)
    # ──────────────────────────────────────────────

    async def check_style(
        self,
        text: str,
        reference_style: str = "",
        genre: str = "",
    ) -> StyleCheckResult:
        """
        텍스트의 문체 일관성을 검사합니다.

        Args:
            text: 검사할 텍스트
            reference_style: 참조할 문체 샘플
            genre: 장르

        Returns:
            문체 검사 결과 (이슈 목록, 일관성 점수, 피드백)
        """
        system_prompt = (
            "당신은 문체 분석 전문가입니다. "
            "텍스트의 문체 일관성, 어조, 표현의 적절성을 분석하세요."
        )

        user_parts = [f"[검사할 텍스트]\n{text}"]
        if reference_style:
            user_parts.append(f"\n[참조 문체]\n{reference_style}")
        if genre:
            user_parts.append(f"\n[장르: {genre}]")

        user_parts.append(
            "\n\nJSON 형식으로 응답하세요:\n"
            "{\n"
            '  "issues": [\n'
            "    {\n"
            '      "text_excerpt": "문제 부분",\n'
            '      "issue": "이슈 설명",\n'
            '      "suggestion": "개선 제안",\n'
            '      "severity": "warning|info|suggestion"\n'
            "    }\n"
            "  ],\n"
            '  "consistency_score": 80.0,\n'
            '  "overall_feedback": "전체 피드백"\n'
            "}"
        )

        user_message = "\n".join(user_parts)

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=4096,
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or "{}"
            result: dict[str, Any] = json.loads(content)

            issues = [
                StyleIssue(
                    text_excerpt=iss.get("text_excerpt", ""),
                    issue=iss.get("issue", ""),
                    suggestion=iss.get("suggestion", ""),
                    severity=SeverityLevel(iss.get("severity", "info")),
                )
                for iss in result.get("issues", [])
            ]

            return StyleCheckResult(
                issues=issues,
                consistency_score=result.get("consistency_score", 100.0),
                overall_feedback=result.get("overall_feedback", ""),
            )

        except Exception as e:
            logger.error(f"문체 검사 중 오류: {e}")
            raise

    # ──────────────────────────────────────────────
    # 1단계: 구조 편집
    # ──────────────────────────────────────────────

    async def review_structure(
        self,
        chapters: list[str],
    ) -> StructureReviewResult:
        """
        도서의 전체 구조를 검토합니다.

        Args:
            chapters: 챕터 내용 목록

        Returns:
            구조 검토 결과 (흐름 점수, 구성 점수, 피드백, 제안)
        """
        system_prompt = (
            "당신은 출판 편집자입니다. "
            "도서의 챕터 구조, 흐름, 구성을 분석하고 개선점을 제안하세요."
        )

        chapters_text = ""
        for i, ch in enumerate(chapters, 1):
            # 각 챕터의 처음 500자만 사용 (토큰 절약)
            preview = ch[:500] + "..." if len(ch) > 500 else ch
            chapters_text += f"\n[챕터 {i}]\n{preview}\n"

        user_message = (
            f"다음 도서의 구조를 검토해주세요:\n{chapters_text}\n\n"
            "JSON 형식으로 응답하세요:\n"
            "{\n"
            '  "flow_score": 75.0,\n'
            '  "organization_score": 80.0,\n'
            '  "feedback": ["피드백1", "피드백2"],\n'
            '  "suggestions": ["제안1", "제안2"]\n'
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
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or "{}"
            result: dict[str, Any] = json.loads(content)

            return StructureReviewResult(
                flow_score=result.get("flow_score", 0.0),
                organization_score=result.get("organization_score", 0.0),
                feedback=result.get("feedback", []),
                suggestions=result.get("suggestions", []),
            )

        except Exception as e:
            logger.error(f"구조 검토 중 오류: {e}")
            raise

    # ──────────────────────────────────────────────
    # 전체 4단계 편집
    # ──────────────────────────────────────────────

    async def full_review(
        self,
        book_id: str,
        chapters: list[dict[str, Any]],
        include_stages: list[EditingStage] | None = None,
    ) -> QualityReport:
        """
        도서에 대해 전체 4단계 편집을 수행합니다.

        Args:
            book_id: 도서 ID
            chapters: 챕터 데이터 목록
            include_stages: 포함할 편집 단계 (None이면 모두 포함)

        Returns:
            종합 품질 보고서
        """
        if include_stages is None:
            include_stages = list(EditingStage)

        stage_results: list[StageResult] = []
        total_issues = 0

        # 모든 챕터 내용 합치기
        all_content = "\n\n".join(
            ch.get("content", "") for ch in chapters if ch.get("content")
        )

        chapter_contents = [ch.get("content", "") for ch in chapters if ch.get("content")]

        # 1단계: 구조 편집
        if EditingStage.STRUCTURE in include_stages:
            try:
                structure_result = await self.review_structure(chapter_contents)
                avg_score = (structure_result.flow_score + structure_result.organization_score) / 2
                issues = len(structure_result.feedback) + len(structure_result.suggestions)
                total_issues += issues
                stage_results.append(StageResult(
                    stage=EditingStage.STRUCTURE,
                    score=avg_score,
                    issues_count=issues,
                    feedback="; ".join(structure_result.feedback[:3]),
                ))
            except Exception as e:
                logger.error(f"구조 편집 단계 오류: {e}")
                stage_results.append(StageResult(
                    stage=EditingStage.STRUCTURE,
                    score=0.0,
                    issues_count=0,
                    feedback="구조 편집 실패: 내부 오류가 발생했습니다.",
                ))

        # 2단계: 내용 편집 (문체 검사)
        if EditingStage.CONTENT in include_stages:
            try:
                # 전체 내용의 일부만 사용 (비용 절약)
                sample_text = all_content[:3000]
                style_result = await self.check_style(sample_text)
                total_issues += len(style_result.issues)
                stage_results.append(StageResult(
                    stage=EditingStage.CONTENT,
                    score=style_result.consistency_score,
                    issues_count=len(style_result.issues),
                    feedback=style_result.overall_feedback,
                ))
            except Exception as e:
                logger.error(f"내용 편집 단계 오류: {e}")
                stage_results.append(StageResult(
                    stage=EditingStage.CONTENT,
                    score=0.0,
                    issues_count=0,
                    feedback="내용 편집 실패: 내부 오류가 발생했습니다.",
                ))

        # 3단계: 교정/교열
        if EditingStage.PROOFREAD in include_stages:
            try:
                sample_text = all_content[:3000]
                proofread_result = await self.proofread(sample_text)
                total_issues += proofread_result.total_corrections
                stage_results.append(StageResult(
                    stage=EditingStage.PROOFREAD,
                    score=proofread_result.accuracy_score,
                    issues_count=proofread_result.total_corrections,
                    feedback=f"총 {proofread_result.total_corrections}개 교정 사항 발견",
                ))
            except Exception as e:
                logger.error(f"교정 단계 오류: {e}")
                stage_results.append(StageResult(
                    stage=EditingStage.PROOFREAD,
                    score=0.0,
                    issues_count=0,
                    feedback="교정 실패: 내부 오류가 발생했습니다.",
                ))

        # 4단계: 최종 검토
        if EditingStage.FINAL in include_stages:
            try:
                final_result = await self._final_review(all_content[:2000])
                total_issues += final_result.get("issues_count", 0)
                stage_results.append(StageResult(
                    stage=EditingStage.FINAL,
                    score=final_result.get("score", 0.0),
                    issues_count=final_result.get("issues_count", 0),
                    feedback=final_result.get("feedback", ""),
                ))
            except Exception as e:
                logger.error(f"최종 검토 단계 오류: {e}")
                stage_results.append(StageResult(
                    stage=EditingStage.FINAL,
                    score=0.0,
                    issues_count=0,
                    feedback="최종 검토 실패: 내부 오류가 발생했습니다.",
                ))

        # 종합 점수 계산
        if stage_results:
            overall_score = sum(sr.score for sr in stage_results) / len(stage_results)
        else:
            overall_score = 0.0

        # 종합 평가 및 권장 사항 생성
        summary, recommendations = self._generate_summary(stage_results, overall_score)

        return QualityReport(
            book_id=book_id,
            overall_score=overall_score,
            stage_results=stage_results,
            total_issues=total_issues,
            summary=summary,
            recommendations=recommendations,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    async def _final_review(self, text: str) -> dict[str, Any]:
        """
        4단계 최종 검토를 수행합니다.
        조판 후 나타날 수 있는 오탈자, 레이아웃 관련 이슈를 확인합니다.

        Args:
            text: 검토할 텍스트

        Returns:
            검토 결과 딕셔너리
        """
        system_prompt = (
            "당신은 출판 최종 교정 담당자입니다. "
            "조판된 원고에서 남은 오탈자, 불필요한 공백, "
            "문단 구분 오류 등을 최종 확인하세요."
        )

        user_message = (
            f"[최종 검토 대상 텍스트]\n{text}\n\n"
            "JSON 형식으로 응답하세요:\n"
            "{\n"
            '  "score": 90.0,\n'
            '  "issues_count": 3,\n'
            '  "feedback": "최종 검토 피드백"\n'
            "}"
        )

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=1024,
                temperature=0.2,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or "{}"
            result: dict[str, Any] = json.loads(content)
            return result

        except Exception as e:
            logger.error(f"최종 검토 중 오류: {e}")
            return {"score": 0.0, "issues_count": 0, "feedback": "최종 검토 중 오류가 발생했습니다."}

    def _generate_summary(
        self,
        stage_results: list[StageResult],
        overall_score: float,
    ) -> tuple[str, list[str]]:
        """
        편집 결과를 종합하여 평가와 권장 사항을 생성합니다.

        Args:
            stage_results: 각 단계별 결과
            overall_score: 종합 점수

        Returns:
            (종합 평가 문자열, 권장 사항 리스트)
        """
        # 종합 평가
        if overall_score >= 90:
            summary = "우수한 품질입니다. 출판 준비가 거의 완료되었습니다."
        elif overall_score >= 75:
            summary = "양호한 수준입니다. 몇 가지 개선 사항을 반영하면 출판 준비가 됩니다."
        elif overall_score >= 60:
            summary = "보통 수준입니다. 주요 이슈를 해결한 후 재검토가 필요합니다."
        else:
            summary = "개선이 필요합니다. 각 단계별 피드백을 참고하여 수정해주세요."

        # 권장 사항
        recommendations: list[str] = []
        for sr in stage_results:
            if sr.score < 70:
                stage_name_map = {
                    EditingStage.STRUCTURE: "구조",
                    EditingStage.CONTENT: "내용/문체",
                    EditingStage.PROOFREAD: "맞춤법/문법",
                    EditingStage.FINAL: "최종 검수",
                }
                stage_name = stage_name_map.get(sr.stage, sr.stage.value)
                recommendations.append(
                    f"{stage_name} 부분을 집중적으로 개선해주세요. (현재 점수: {sr.score:.1f})"
                )

        if not recommendations:
            recommendations.append("전반적으로 양호합니다. 세부 피드백을 참고하여 마무리하세요.")

        return summary, recommendations
