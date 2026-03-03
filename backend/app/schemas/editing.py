"""
편집 관련 Pydantic 스키마
4단계 편집(구조편집, 내용편집, 교정, 최종검토) 스키마를 정의합니다.
"""

from enum import Enum

from pydantic import Field, StrictBool, StrictFloat, StrictInt, StrictStr

from app.schemas.base import StrictBaseModel


class EditingStage(str, Enum):
    """편집 단계 열거형"""
    STRUCTURE = "structure"     # 1단계: 구조 편집
    CONTENT = "content"         # 2단계: 내용 편집
    PROOFREAD = "proofread"     # 3단계: 교정/교열
    FINAL = "final"             # 4단계: 최종 검토


class SeverityLevel(str, Enum):
    """심각도 수준 열거형"""
    ERROR = "error"         # 오류 (반드시 수정 필요)
    WARNING = "warning"     # 경고 (수정 권장)
    INFO = "info"           # 정보 (참고 사항)
    SUGGESTION = "suggestion"  # 제안 (선택적)


class ProofreadRequest(StrictBaseModel):
    """교정 요청 스키마"""
    text: StrictStr = Field(..., min_length=1)
    check_spelling: StrictBool = True         # 맞춤법 검사
    check_grammar: StrictBool = True          # 문법 검사
    check_punctuation: StrictBool = True      # 구두점 검사


class CorrectionItem(StrictBaseModel):
    """교정 항목 스키마"""
    original: StrictStr                 # 원본 텍스트
    corrected: StrictStr                # 수정 텍스트
    reason: StrictStr                   # 수정 이유
    position_start: StrictInt = Field(..., ge=0)  # 시작 위치
    position_end: StrictInt = Field(..., ge=0)    # 끝 위치
    severity: SeverityLevel


class ProofreadResult(StrictBaseModel):
    """교정 결과 스키마"""
    corrected_text: StrictStr           # 전체 교정된 텍스트
    corrections: list[CorrectionItem]
    total_corrections: StrictInt
    accuracy_score: StrictFloat = Field(..., ge=0.0, le=100.0)  # 정확도 점수


class StyleCheckRequest(StrictBaseModel):
    """문체 일관성 검사 요청 스키마"""
    text: StrictStr = Field(..., min_length=1)
    reference_style: StrictStr = Field(default="")  # 참조할 문체 샘플
    genre: StrictStr = Field(default="")             # 장르


class StyleIssue(StrictBaseModel):
    """문체 이슈 항목"""
    text_excerpt: StrictStr             # 문제 부분 발췌
    issue: StrictStr                    # 이슈 설명
    suggestion: StrictStr               # 개선 제안
    severity: SeverityLevel


class StyleCheckResult(StrictBaseModel):
    """문체 일관성 검사 결과 스키마"""
    issues: list[StyleIssue]
    consistency_score: StrictFloat = Field(..., ge=0.0, le=100.0)  # 일관성 점수
    overall_feedback: StrictStr         # 전체 피드백


class StructureReviewRequest(StrictBaseModel):
    """구조 검토 요청 스키마"""
    book_id: StrictStr
    chapters: list[StrictStr]           # 챕터 내용 목록


class StructureReviewResult(StrictBaseModel):
    """구조 검토 결과 스키마"""
    flow_score: StrictFloat = Field(..., ge=0.0, le=100.0)          # 흐름 점수
    organization_score: StrictFloat = Field(..., ge=0.0, le=100.0) # 구성 점수
    feedback: list[StrictStr]           # 피드백 목록
    suggestions: list[StrictStr]        # 개선 제안 목록


class FullReviewRequest(StrictBaseModel):
    """전체 4단계 편집 요청 스키마"""
    book_id: StrictStr
    include_stages: list[EditingStage] = [
        EditingStage.STRUCTURE,
        EditingStage.CONTENT,
        EditingStage.PROOFREAD,
        EditingStage.FINAL,
    ]


class StageResult(StrictBaseModel):
    """개별 편집 단계 결과"""
    stage: EditingStage
    score: StrictFloat = Field(..., ge=0.0, le=100.0)
    issues_count: StrictInt
    feedback: StrictStr


class QualityReport(StrictBaseModel):
    """품질 보고서 스키마"""
    book_id: StrictStr
    overall_score: StrictFloat = Field(..., ge=0.0, le=100.0)  # 종합 품질 점수
    stage_results: list[StageResult]
    total_issues: StrictInt
    summary: StrictStr                  # 종합 평가
    recommendations: list[StrictStr]    # 권장 사항
    created_at: StrictStr
