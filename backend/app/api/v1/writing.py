"""
AI 글쓰기 API 엔드포인트
GPT 기반 글 생성, 재작성, 구조 제안을 처리합니다.
"""

import json
from typing import Any, AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_user
from app.core.config import Settings, get_settings
from app.schemas.writing import (
    GenerateRequest,
    RewriteRequest,
    RewriteResponse,
    StructureRequest,
    StructureResponse,
)
from app.services.writing_service import WritingService

router = APIRouter()


@router.post(
    "/generate",
    summary="AI 글 생성 (SSE 스트리밍)",
    response_class=StreamingResponse,
)
async def generate_text(
    request: GenerateRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> StreamingResponse:
    """
    AI를 이용해 글을 생성합니다.
    SSE(Server-Sent Events) 스트리밍으로 실시간 생성 결과를 전달합니다.

    장르별 특화 프롬프트 템플릿을 사용하여 해당 장르에 맞는 글을 생성합니다.
    """
    if not request.prompt.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="글 생성 지시사항을 입력해주세요.",
        )

    writing_service = WritingService(settings=settings)

    async def event_stream() -> AsyncGenerator[str, None]:
        """SSE 이벤트 스트림 생성기"""
        try:
            async for chunk in writing_service.generate_stream(
                genre=request.genre,
                prompt=request.prompt,
                context=request.context,
                chapter_title=request.chapter_title,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            ):
                # SSE 형식으로 전송
                data = json.dumps(
                    {"text": chunk, "is_done": False},
                    ensure_ascii=False,
                )
                yield f"data: {data}\n\n"

            # 완료 신호
            done_data = json.dumps(
                {"text": "", "is_done": True},
                ensure_ascii=False,
            )
            yield f"data: {done_data}\n\n"

        except Exception as e:
            error_data = json.dumps(
                {"error": f"글 생성 중 오류: {str(e)}"},
                ensure_ascii=False,
            )
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post(
    "/rewrite",
    response_model=RewriteResponse,
    summary="구간 재작성",
)
async def rewrite_text(
    request: RewriteRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> RewriteResponse:
    """
    특정 구간의 텍스트를 지시사항에 따라 재작성합니다.
    원본 텍스트와 지시사항을 기반으로 개선된 텍스트를 반환합니다.
    """
    if not request.original_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="재작성할 원본 텍스트를 입력해주세요.",
        )

    writing_service = WritingService(settings=settings)

    try:
        result = await writing_service.rewrite(
            original_text=request.original_text,
            instruction=request.instruction,
            genre=request.genre,
            style_guide=request.style_guide,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"재작성에 실패했습니다: {str(e)}",
        ) from e


@router.post(
    "/structure",
    response_model=StructureResponse,
    summary="챕터 구조 제안",
)
async def suggest_structure(
    request: StructureRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> StructureResponse:
    """
    도서의 챕터 구조를 AI가 제안합니다.
    장르, 주제, 목표 챕터 수를 기반으로 적합한 구조를 생성합니다.
    """
    if not request.book_title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="책 제목을 입력해주세요.",
        )

    writing_service = WritingService(settings=settings)

    try:
        result = await writing_service.suggest_structure(
            book_title=request.book_title,
            genre=request.genre,
            description=request.description,
            target_chapters=request.target_chapters,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"구조 제안에 실패했습니다: {str(e)}",
        ) from e
