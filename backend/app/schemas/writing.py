"""
AI 글쓰기 관련 Pydantic 스키마
GPT 기반 글 생성, 재작성, 구조 제안 스키마를 정의합니다.
"""

from pydantic import StrictFloat, StrictInt, StrictStr

from app.schemas.base import StrictBaseModel
from app.schemas.book import Genre


class GenerateRequest(StrictBaseModel):
    """AI 글 생성 요청 스키마"""
    genre: Genre
    prompt: StrictStr                       # 사용자 지시 (예: "봄날의 산책에 대해 써줘")
    context: StrictStr = ""                 # 이전 맥락 (이미 쓴 내용)
    chapter_title: StrictStr = ""           # 챕터 제목
    max_tokens: StrictInt = 1024            # 최대 생성 토큰 수
    temperature: StrictFloat = 0.7          # 창작 온도 (0.0~2.0)


class GenerateChunk(StrictBaseModel):
    """SSE 스트리밍 청크 스키마"""
    text: StrictStr
    is_done: bool = False


class RewriteRequest(StrictBaseModel):
    """구간 재작성 요청 스키마"""
    original_text: StrictStr                # 원본 텍스트
    instruction: StrictStr                  # 재작성 지시사항
    genre: Genre
    style_guide: StrictStr = ""             # 문체 가이드


class RewriteResponse(StrictBaseModel):
    """구간 재작성 응답 스키마"""
    rewritten_text: StrictStr
    changes_summary: StrictStr              # 변경 사항 요약


class ChapterSuggestion(StrictBaseModel):
    """챕터 구조 제안 항목"""
    order: StrictInt
    title: StrictStr
    description: StrictStr
    estimated_pages: StrictInt


class StructureRequest(StrictBaseModel):
    """챕터 구조 제안 요청 스키마"""
    book_title: StrictStr
    genre: Genre
    description: StrictStr                  # 책 설명 / 주제
    target_chapters: StrictInt = 10         # 목표 챕터 수


class StructureResponse(StrictBaseModel):
    """챕터 구조 제안 응답 스키마"""
    chapters: list[ChapterSuggestion]
    overall_summary: StrictStr              # 전체 구조 요약
