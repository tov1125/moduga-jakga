"""
편집 API 엔드포인트
4단계 편집(구조편집, 내용편집, 교정, 최종검토)을 처리합니다.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.api.deps import get_current_user, get_supabase
from app.core.config import Settings, get_settings
from app.models.base import TABLE_BOOKS, TABLE_CHAPTERS, TABLE_EDITING_REPORTS
from app.schemas.editing import (
    EditingStage,
    FullReviewRequest,
    ProofreadRequest,
    ProofreadResult,
    QualityReport,
    StageResult,
    StyleCheckRequest,
    StyleCheckResult,
    StructureReviewRequest,
    StructureReviewResult,
)
from app.services.editing_service import EditingService

router = APIRouter()


@router.post(
    "/proofread",
    response_model=ProofreadResult,
    summary="맞춤법/문법 교정",
)
async def proofread(
    request: ProofreadRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> ProofreadResult:
    """
    텍스트의 맞춤법, 문법, 구두점 오류를 교정합니다.
    3단계 교정/교열에 해당합니다.
    """
    if not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="교정할 텍스트를 입력해주세요.",
        )

    editing_service = EditingService(settings=settings)

    try:
        result = await editing_service.proofread(
            text=request.text,
            check_spelling=request.check_spelling,
            check_grammar=request.check_grammar,
            check_punctuation=request.check_punctuation,
        )
        return result
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="교정 처리에 실패했습니다.",
        )


@router.post(
    "/style-check",
    response_model=StyleCheckResult,
    summary="문체 일관성 검사",
)
async def style_check(
    request: StyleCheckRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> StyleCheckResult:
    """
    텍스트의 문체 일관성을 검사합니다.
    2단계 내용 편집의 문체 관련 검사에 해당합니다.
    """
    if not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="검사할 텍스트를 입력해주세요.",
        )

    editing_service = EditingService(settings=settings)

    try:
        result = await editing_service.check_style(
            text=request.text,
            reference_style=request.reference_style,
            genre=request.genre,
        )
        return result
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="문체 검사에 실패했습니다.",
        )


@router.post(
    "/structure-review",
    response_model=StructureReviewResult,
    summary="구조 검토",
)
async def structure_review(
    request: StructureReviewRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
    supabase: Client = Depends(get_supabase),
) -> StructureReviewResult:
    """
    도서의 전체 구조(챕터 흐름, 구성)를 검토합니다.
    1단계 구조 편집에 해당합니다.
    """
    # 도서 소유권 확인
    book_resp = (
        supabase.table(TABLE_BOOKS)
        .select("id")
        .eq("id", request.book_id)
        .eq("user_id", current_user["id"])
        .execute()
    )
    if not book_resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="도서를 찾을 수 없습니다.",
        )

    editing_service = EditingService(settings=settings)

    try:
        result = await editing_service.review_structure(
            chapters=request.chapters,
        )
        return result
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="구조 검토에 실패했습니다.",
        )


@router.post(
    "/full-review",
    response_model=QualityReport,
    summary="전체 4단계 편집",
)
async def full_review(
    request: FullReviewRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
    supabase: Client = Depends(get_supabase),
) -> QualityReport:
    """
    도서에 대해 전체 4단계 편집을 수행합니다.

    1단계 - 구조 편집: 전체 흐름과 챕터 구성 검토
    2단계 - 내용 편집: 문장 개선, 문체 일관성 검사
    3단계 - 교정/교열: 맞춤법, 문법 교정
    4단계 - 최종 검토: 조판 후 오탈자 확인
    """
    # 도서 소유권 확인
    book_resp = (
        supabase.table(TABLE_BOOKS)
        .select("id")
        .eq("id", request.book_id)
        .eq("user_id", current_user["id"])
        .execute()
    )
    if not book_resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="도서를 찾을 수 없습니다.",
        )

    # 도서의 모든 챕터 가져오기
    chapters_resp = (
        supabase.table(TABLE_CHAPTERS)
        .select("*")
        .eq("book_id", request.book_id)
        .order("order", desc=False)
        .execute()
    )

    if not chapters_resp.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="편집할 챕터가 없습니다.",
        )

    editing_service = EditingService(settings=settings)

    try:
        report = await editing_service.full_review(
            book_id=request.book_id,
            chapters=chapters_resp.data,
            include_stages=request.include_stages,
        )

        # 4단계별 점수 추출
        stage_scores: dict[str, float] = {}
        for sr in report.stage_results:
            stage_scores[sr.stage.value] = sr.score

        # editing_reports 테이블에 저장
        insert_data = {
            "book_id": request.book_id,
            "user_id": current_user["id"],
            "stage": "full_review",
            "structure_score": stage_scores.get("structure", 0.0),
            "style_score": stage_scores.get("content", 0.0),
            "spelling_score": stage_scores.get("proofread", 0.0),
            "readability_score": stage_scores.get("final", 0.0),
            "overall_score": report.overall_score,
            "issues": {
                "stage_results": [sr.model_dump() for sr in report.stage_results],
                "total_issues": report.total_issues,
                "summary": report.summary,
            },
            "suggestions": report.recommendations,
        }
        try:
            supabase.table(TABLE_EDITING_REPORTS).insert(insert_data).execute()
        except Exception:
            pass  # DB 저장 실패해도 report는 반환

        return report
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="전체 편집에 실패했습니다.",
        )


@router.get(
    "/report/{book_id}",
    response_model=QualityReport,
    summary="품질 보고서 조회",
)
async def get_quality_report(
    book_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
    supabase: Client = Depends(get_supabase),
) -> QualityReport:
    """
    도서의 최신 품질 보고서를 조회합니다.
    이전에 실행한 편집 결과를 확인할 수 있습니다.
    """
    # 도서 소유권 확인
    book_resp = (
        supabase.table(TABLE_BOOKS)
        .select("id")
        .eq("id", book_id)
        .eq("user_id", current_user["id"])
        .execute()
    )
    if not book_resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="도서를 찾을 수 없습니다.",
        )

    # 편집 보고서 조회
    report_resp = (
        supabase.table("editing_reports")
        .select("*")
        .eq("book_id", book_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if not report_resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="품질 보고서가 없습니다. 먼저 편집을 실행해주세요.",
        )

    report_data = report_resp.data[0]
    issues_data = report_data.get("issues", {})
    if isinstance(issues_data, list):
        issues_data = {}
    stage_results_raw = issues_data.get("stage_results", [])

    stage_results = [
        StageResult(
            stage=EditingStage(sr["stage"]),
            score=sr["score"],
            issues_count=sr["issues_count"],
            feedback=sr["feedback"],
        )
        for sr in stage_results_raw
    ]

    return QualityReport(
        book_id=report_data["book_id"],
        overall_score=report_data.get("overall_score", 0.0),
        stage_results=stage_results,
        total_issues=issues_data.get("total_issues", 0),
        summary=issues_data.get("summary", ""),
        recommendations=report_data.get("suggestions", []),
        created_at=str(report_data["created_at"]),
    )
