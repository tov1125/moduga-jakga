"""
Pydantic v2 Strict 타입 및 Field 제약 조건 검증 테스트
타입 안전성, 범위 유효성, Enum 동기화를 보장합니다.

검증 항목:
  - Strict 타입 적용 (str에 int 불가 등)
  - StrictBool 적용 (bool에 int/str 불가)
  - Field 제약 조건 (min_length, max_length, ge, le)
  - Enum 값 검증 및 FE/BE 동기화
  - 필수 필드 누락 시 에러
"""

import pytest
from pydantic import ValidationError

from app.schemas.auth import (
    DisabilityType,
    LoginRequest,
    SignUpRequest,
)
from app.schemas.book import (
    BookCreate,
    BookStatus,
    BookUpdate,
    Genre,
)
from app.schemas.chapter import (
    ChapterCreate,
    ChapterStatus,
    ChapterUpdate,
)
from app.schemas.design import (
    CoverGenerateRequest,
    CoverStyle,
    LayoutPreviewRequest,
    PageSize,
)
from app.schemas.editing import (
    CorrectionItem,
    EditingStage,
    ProofreadRequest,
    ProofreadResult,
    QualityReport,
    SeverityLevel,
    StageResult,
    StyleCheckResult,
    StructureReviewResult,
)
from app.schemas.publishing import (
    ExportFormat,
    ExportRequest,
    ExportStatus,
    ExportStatusEnum,
)
from app.schemas.tts import TTSSynthesizeRequest, TTSVoiceId
from app.schemas.writing import (
    ChapterSuggestion,
    GenerateChunk,
    GenerateRequest,
    StructureRequest,
)


# ─── Auth 스키마 ──────────────────────────────────────────────────────────────


class TestSignUpRequest:
    """SignUpRequest Strict 타입 + Field 제약 조건"""

    def test_valid(self) -> None:
        req = SignUpRequest(
            email="user@example.com",
            password="StrongPass123!",
            display_name="사용자",
            disability_type=DisabilityType.VISUAL,
        )
        assert req.email == "user@example.com"
        assert req.disability_type == DisabilityType.VISUAL

    def test_default_disability(self) -> None:
        req = SignUpRequest(
            email="user@example.com",
            password="securepass",
            display_name="홍길동",
        )
        assert req.disability_type == DisabilityType.NONE

    def test_missing_email(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            SignUpRequest(
                password="StrongPass123!",
                display_name="사용자",
            )  # type: ignore[call-arg]
        assert "email" in str(exc_info.value)

    def test_strict_type_rejects_int(self) -> None:
        with pytest.raises(ValidationError):
            SignUpRequest(
                email=12345,  # type: ignore[arg-type]
                password="StrongPass123!",
                display_name="사용자",
            )

    def test_email_too_short(self) -> None:
        with pytest.raises(ValidationError):
            SignUpRequest(email="a@b", password="securepass", display_name="이름")

    def test_password_too_short(self) -> None:
        with pytest.raises(ValidationError):
            SignUpRequest(email="user@example.com", password="short", display_name="이름")

    def test_password_too_long(self) -> None:
        with pytest.raises(ValidationError):
            SignUpRequest(
                email="user@example.com",
                password="x" * 129,
                display_name="이름",
            )

    def test_display_name_empty(self) -> None:
        with pytest.raises(ValidationError):
            SignUpRequest(email="user@example.com", password="securepass", display_name="")

    def test_display_name_too_long(self) -> None:
        with pytest.raises(ValidationError):
            SignUpRequest(
                email="user@example.com",
                password="securepass",
                display_name="가" * 51,
            )


class TestLoginRequest:
    """LoginRequest Field 제약 조건"""

    def test_valid(self) -> None:
        req = LoginRequest(email="user@example.com", password="Password123!")
        assert req.email == "user@example.com"

    def test_email_too_short(self) -> None:
        with pytest.raises(ValidationError):
            LoginRequest(email="a@b", password="securepass")

    def test_password_too_short(self) -> None:
        with pytest.raises(ValidationError):
            LoginRequest(email="user@example.com", password="short")


# ─── Book 스키마 ──────────────────────────────────────────────────────────────


class TestBookCreate:
    """BookCreate Field 제약 조건"""

    def test_valid(self) -> None:
        req = BookCreate(title="테스트 도서", genre=Genre.ESSAY)
        assert req.title == "테스트 도서"
        assert req.description == ""

    def test_title_empty(self) -> None:
        with pytest.raises(ValidationError):
            BookCreate(title="", genre=Genre.NOVEL)

    def test_title_too_long(self) -> None:
        with pytest.raises(ValidationError):
            BookCreate(title="가" * 201, genre=Genre.NOVEL)

    def test_description_too_long(self) -> None:
        with pytest.raises(ValidationError):
            BookCreate(title="제목", genre=Genre.ESSAY, description="가" * 2001)

    def test_invalid_genre(self) -> None:
        with pytest.raises(ValidationError):
            BookCreate(title="도서", genre="invalid_genre")  # type: ignore[arg-type]

    def test_all_genres(self) -> None:
        for g in Genre:
            book = BookCreate(title="제목", genre=g)
            assert book.genre == g


class TestBookUpdate:
    """BookUpdate Field 제약 조건"""

    def test_partial_update(self) -> None:
        update = BookUpdate(title="새 제목")
        assert update.title == "새 제목"
        assert update.genre is None

    def test_all_none(self) -> None:
        update = BookUpdate()
        assert update.title is None
        assert update.status is None

    def test_title_too_long(self) -> None:
        with pytest.raises(ValidationError):
            BookUpdate(title="가" * 201)


# ─── Chapter 스키마 ───────────────────────────────────────────────────────────


class TestChapterCreate:
    """ChapterCreate Field 제약 조건"""

    def test_valid(self) -> None:
        ch = ChapterCreate(title="1장 시작")
        assert ch.order == 1
        assert ch.content == ""

    def test_title_empty(self) -> None:
        with pytest.raises(ValidationError):
            ChapterCreate(title="")

    def test_order_zero(self) -> None:
        with pytest.raises(ValidationError):
            ChapterCreate(title="챕터", order=0)

    def test_order_negative(self) -> None:
        with pytest.raises(ValidationError):
            ChapterCreate(title="챕터", order=-1)


class TestChapterUpdate:
    """ChapterUpdate Field 제약 조건"""

    def test_partial_update(self) -> None:
        update = ChapterUpdate(order=5)
        assert update.order == 5
        assert update.title is None

    def test_order_zero(self) -> None:
        with pytest.raises(ValidationError):
            ChapterUpdate(order=0)


# ─── Writing 스키마 ───────────────────────────────────────────────────────────


class TestGenerateRequest:
    """GenerateRequest Field 제약 조건"""

    def test_valid(self) -> None:
        req = GenerateRequest(
            prompt="오늘 아침 산책에 대해 써줘",
            genre=Genre.ESSAY,
        )
        assert req.max_tokens == 1024
        assert req.temperature == 0.7

    def test_prompt_empty(self) -> None:
        with pytest.raises(ValidationError):
            GenerateRequest(genre=Genre.NOVEL, prompt="")

    def test_max_tokens_zero(self) -> None:
        with pytest.raises(ValidationError):
            GenerateRequest(genre=Genre.NOVEL, prompt="테스트", max_tokens=0)

    def test_max_tokens_too_large(self) -> None:
        with pytest.raises(ValidationError):
            GenerateRequest(genre=Genre.NOVEL, prompt="테스트", max_tokens=5000)

    def test_temperature_negative(self) -> None:
        with pytest.raises(ValidationError):
            GenerateRequest(genre=Genre.NOVEL, prompt="테스트", temperature=-0.1)

    def test_temperature_too_high(self) -> None:
        with pytest.raises(ValidationError):
            GenerateRequest(genre=Genre.NOVEL, prompt="테스트", temperature=2.1)

    def test_temperature_boundary(self) -> None:
        req0 = GenerateRequest(genre=Genre.NOVEL, prompt="테스트", temperature=0.0)
        assert req0.temperature == 0.0
        req2 = GenerateRequest(genre=Genre.NOVEL, prompt="테스트", temperature=2.0)
        assert req2.temperature == 2.0


class TestGenerateChunk:
    """GenerateChunk StrictBool 테스트"""

    def test_valid(self) -> None:
        chunk = GenerateChunk(text="안녕하세요", is_done=True)
        assert chunk.is_done is True

    def test_strict_bool_rejects_int(self) -> None:
        with pytest.raises(ValidationError):
            GenerateChunk(text="텍스트", is_done=1)  # type: ignore[arg-type]

    def test_strict_bool_rejects_string(self) -> None:
        with pytest.raises(ValidationError):
            GenerateChunk(text="텍스트", is_done="true")  # type: ignore[arg-type]


class TestStructureRequest:
    """StructureRequest Field 제약 조건"""

    def test_valid(self) -> None:
        req = StructureRequest(
            book_title="나의 책",
            genre=Genre.AUTOBIOGRAPHY,
            description="인생 이야기",
        )
        assert req.target_chapters == 10

    def test_target_chapters_zero(self) -> None:
        with pytest.raises(ValidationError):
            StructureRequest(
                book_title="제목", genre=Genre.ESSAY,
                description="설명", target_chapters=0,
            )

    def test_target_chapters_too_large(self) -> None:
        with pytest.raises(ValidationError):
            StructureRequest(
                book_title="제목", genre=Genre.ESSAY,
                description="설명", target_chapters=101,
            )


class TestChapterSuggestion:
    """ChapterSuggestion Field 제약 조건"""

    def test_valid(self) -> None:
        cs = ChapterSuggestion(
            order=1, title="서론", description="소개", estimated_pages=5,
        )
        assert cs.order == 1

    def test_order_zero(self) -> None:
        with pytest.raises(ValidationError):
            ChapterSuggestion(
                order=0, title="서론", description="소개", estimated_pages=5,
            )

    def test_estimated_pages_zero(self) -> None:
        with pytest.raises(ValidationError):
            ChapterSuggestion(
                order=1, title="서론", description="소개", estimated_pages=0,
            )


# ─── Editing 스키마 ───────────────────────────────────────────────────────────


class TestProofreadRequest:
    """ProofreadRequest StrictBool 테스트"""

    def test_valid(self) -> None:
        req = ProofreadRequest(text="맞춤법을 검사할 문장입니다.")
        assert req.check_spelling is True
        assert req.check_grammar is True

    def test_text_empty(self) -> None:
        with pytest.raises(ValidationError):
            ProofreadRequest(text="")

    def test_strict_type_rejects_int(self) -> None:
        with pytest.raises(ValidationError):
            ProofreadRequest(text=12345)  # type: ignore[arg-type]

    def test_strict_bool_rejects_int(self) -> None:
        with pytest.raises(ValidationError):
            ProofreadRequest(text="텍스트", check_spelling=1)  # type: ignore[arg-type]

    def test_strict_bool_rejects_string(self) -> None:
        with pytest.raises(ValidationError):
            ProofreadRequest(text="텍스트", check_grammar="yes")  # type: ignore[arg-type]


class TestProofreadResult:
    """ProofreadResult accuracy_score 범위"""

    def _make(self, score: float) -> ProofreadResult:
        return ProofreadResult(
            corrected_text="수정됨", corrections=[],
            total_corrections=0, accuracy_score=score,
        )

    def test_valid(self) -> None:
        assert self._make(85.5).accuracy_score == 85.5

    def test_boundary(self) -> None:
        assert self._make(0.0).accuracy_score == 0.0
        assert self._make(100.0).accuracy_score == 100.0

    def test_negative(self) -> None:
        with pytest.raises(ValidationError):
            self._make(-1.0)

    def test_over_100(self) -> None:
        with pytest.raises(ValidationError):
            self._make(100.1)


class TestCorrectionItem:
    """CorrectionItem position 범위"""

    def test_valid(self) -> None:
        item = CorrectionItem(
            original="원본", corrected="수정", reason="이유",
            position_start=0, position_end=2,
            severity=SeverityLevel.WARNING,
        )
        assert item.position_start == 0

    def test_position_negative(self) -> None:
        with pytest.raises(ValidationError):
            CorrectionItem(
                original="원본", corrected="수정", reason="이유",
                position_start=-1, position_end=2,
                severity=SeverityLevel.ERROR,
            )


class TestStageResult:
    """StageResult score 범위"""

    def test_valid(self) -> None:
        sr = StageResult(
            stage=EditingStage.PROOFREAD, score=90.0,
            issues_count=3, feedback="좋습니다",
        )
        assert sr.score == 90.0

    def test_score_over_100(self) -> None:
        with pytest.raises(ValidationError):
            StageResult(
                stage=EditingStage.STRUCTURE, score=101.0,
                issues_count=0, feedback="피드백",
            )


class TestQualityReportSchema:
    """QualityReport overall_score 범위"""

    def test_valid(self) -> None:
        qr = QualityReport(
            book_id="book-1", overall_score=88.0,
            stage_results=[], total_issues=0,
            summary="우수", recommendations=[],
            created_at="2026-01-01T00:00:00Z",
        )
        assert qr.overall_score == 88.0

    def test_score_negative(self) -> None:
        with pytest.raises(ValidationError):
            QualityReport(
                book_id="book-1", overall_score=-5.0,
                stage_results=[], total_issues=0,
                summary="요약", recommendations=[],
                created_at="2026-01-01T00:00:00Z",
            )


class TestStructureReviewResult:
    """StructureReviewResult score 범위"""

    def test_valid(self) -> None:
        srr = StructureReviewResult(
            flow_score=75.0, organization_score=80.0,
            feedback=["좋음"], suggestions=["개선"],
        )
        assert srr.flow_score == 75.0

    def test_flow_score_over_100(self) -> None:
        with pytest.raises(ValidationError):
            StructureReviewResult(
                flow_score=101.0, organization_score=80.0,
                feedback=[], suggestions=[],
            )


class TestStyleCheckResult:
    """StyleCheckResult consistency_score 범위"""

    def test_valid(self) -> None:
        scr = StyleCheckResult(
            issues=[], consistency_score=92.0,
            overall_feedback="일관성이 높습니다",
        )
        assert scr.consistency_score == 92.0

    def test_over_100(self) -> None:
        with pytest.raises(ValidationError):
            StyleCheckResult(
                issues=[], consistency_score=100.1,
                overall_feedback="피드백",
            )


# ─── TTS 스키마 ───────────────────────────────────────────────────────────────


class TestTTSSynthesizeRequest:
    """TTSSynthesizeRequest Field 제약 조건"""

    def test_valid(self) -> None:
        req = TTSSynthesizeRequest(text="음성으로 변환할 텍스트입니다.")
        assert req.speed == 0.0
        assert req.voice_id == TTSVoiceId.NARA

    def test_strict_type_rejects_int(self) -> None:
        with pytest.raises(ValidationError):
            TTSSynthesizeRequest(text=12345)  # type: ignore[arg-type]

    def test_text_empty(self) -> None:
        with pytest.raises(ValidationError):
            TTSSynthesizeRequest(text="")

    def test_text_too_long(self) -> None:
        with pytest.raises(ValidationError):
            TTSSynthesizeRequest(text="가" * 5001)

    def test_speed_boundary(self) -> None:
        req = TTSSynthesizeRequest(text="테스트", speed=-5.0)
        assert req.speed == -5.0
        req2 = TTSSynthesizeRequest(text="테스트", speed=5.0)
        assert req2.speed == 5.0

    def test_speed_too_low(self) -> None:
        with pytest.raises(ValidationError):
            TTSSynthesizeRequest(text="테스트", speed=-5.1)

    def test_speed_too_high(self) -> None:
        with pytest.raises(ValidationError):
            TTSSynthesizeRequest(text="테스트", speed=5.1)

    def test_pitch_out_of_range(self) -> None:
        with pytest.raises(ValidationError):
            TTSSynthesizeRequest(text="테스트", pitch=6.0)

    def test_volume_out_of_range(self) -> None:
        with pytest.raises(ValidationError):
            TTSSynthesizeRequest(text="테스트", volume=-6.0)

    def test_alpha_out_of_range(self) -> None:
        with pytest.raises(ValidationError):
            TTSSynthesizeRequest(text="테스트", alpha=5.1)


# ─── Design 스키마 ────────────────────────────────────────────────────────────


class TestCoverGenerateRequest:
    """CoverGenerateRequest Field 제약 조건"""

    def test_valid(self) -> None:
        req = CoverGenerateRequest(
            book_title="나의 책", author_name="홍길동", genre=Genre.ESSAY,
        )
        assert req.style == CoverStyle.MINIMALIST

    def test_title_empty(self) -> None:
        with pytest.raises(ValidationError):
            CoverGenerateRequest(
                book_title="", author_name="저자", genre=Genre.NOVEL,
            )

    def test_author_empty(self) -> None:
        with pytest.raises(ValidationError):
            CoverGenerateRequest(
                book_title="제목", author_name="", genre=Genre.NOVEL,
            )


class TestLayoutPreviewRequest:
    """LayoutPreviewRequest Field 제약 조건"""

    def test_valid_defaults(self) -> None:
        req = LayoutPreviewRequest(book_id="book-1")
        assert req.font_size == 11.0
        assert req.page_size == PageSize.A5

    def test_font_size_too_small(self) -> None:
        with pytest.raises(ValidationError):
            LayoutPreviewRequest(book_id="book-1", font_size=7.0)

    def test_font_size_too_large(self) -> None:
        with pytest.raises(ValidationError):
            LayoutPreviewRequest(book_id="book-1", font_size=25.0)

    def test_line_spacing_range(self) -> None:
        with pytest.raises(ValidationError):
            LayoutPreviewRequest(book_id="book-1", line_spacing=0.5)
        with pytest.raises(ValidationError):
            LayoutPreviewRequest(book_id="book-1", line_spacing=3.5)

    def test_margin_range(self) -> None:
        with pytest.raises(ValidationError):
            LayoutPreviewRequest(book_id="book-1", margin_top=4.0)
        with pytest.raises(ValidationError):
            LayoutPreviewRequest(book_id="book-1", margin_left=51.0)

    def test_margin_boundary(self) -> None:
        req = LayoutPreviewRequest(
            book_id="book-1",
            margin_top=5.0, margin_bottom=50.0,
            margin_left=5.0, margin_right=50.0,
        )
        assert req.margin_top == 5.0
        assert req.margin_bottom == 50.0

    def test_cover_style_enum(self) -> None:
        assert CoverStyle.MINIMALIST == "minimalist"
        assert CoverStyle.ILLUSTRATED == "illustrated"

    def test_page_size_enum(self) -> None:
        assert PageSize.A5 == "A5"
        assert PageSize.B5 == "B5"


# ─── Publishing 스키마 ────────────────────────────────────────────────────────


class TestExportRequest:
    """ExportRequest StrictBool 테스트"""

    def test_valid(self) -> None:
        req = ExportRequest(book_id="book-1", format=ExportFormat.PDF)
        assert req.include_cover is True
        assert req.accessibility_tags is True

    def test_strict_bool_rejects_int(self) -> None:
        with pytest.raises(ValidationError):
            ExportRequest(
                book_id="book-1", format=ExportFormat.EPUB,
                include_cover=1,  # type: ignore[arg-type]
            )

    def test_export_format_enum(self) -> None:
        assert ExportFormat.DOCX == "docx"
        assert ExportFormat.PDF == "pdf"
        assert ExportFormat.EPUB == "epub"


class TestExportStatus:
    """ExportStatus progress 범위"""

    def _make(self, progress: float) -> ExportStatus:
        return ExportStatus(
            export_id="exp-1", book_id="book-1",
            format=ExportFormat.DOCX,
            status=ExportStatusEnum.PROCESSING,
            progress=progress,
            created_at="2026-01-01T00:00:00Z",
        )

    def test_valid(self) -> None:
        assert self._make(50.0).progress == 50.0

    def test_negative(self) -> None:
        with pytest.raises(ValidationError):
            self._make(-1.0)

    def test_over_100(self) -> None:
        with pytest.raises(ValidationError):
            self._make(101.0)


# ─── Enum 동기화 검증 (FE/BE 일치 확인) ───────────────────────────────────────


class TestEnumSync:
    """FE/BE Enum 값 동기화 검증"""

    def test_disability_type_values(self) -> None:
        expected = {"visual", "low_vision", "none", "other"}
        actual = {e.value for e in DisabilityType}
        assert actual == expected

    def test_book_status_values(self) -> None:
        expected = {"draft", "writing", "editing", "designing", "completed", "published"}
        actual = {e.value for e in BookStatus}
        assert actual == expected

    def test_chapter_status_values(self) -> None:
        expected = {"draft", "writing", "completed", "editing", "finalized"}
        actual = {e.value for e in ChapterStatus}
        assert actual == expected

    def test_genre_values(self) -> None:
        expected = {
            "essay", "novel", "poem", "autobiography",
            "children", "non_fiction", "other",
        }
        actual = {e.value for e in Genre}
        assert actual == expected

    def test_editing_stage_values(self) -> None:
        expected = {"structure", "content", "proofread", "final"}
        actual = {e.value for e in EditingStage}
        assert actual == expected

    def test_export_format_values(self) -> None:
        expected = {"docx", "pdf", "epub"}
        actual = {e.value for e in ExportFormat}
        assert actual == expected

    def test_severity_level_values(self) -> None:
        expected = {"error", "warning", "info", "suggestion"}
        actual = {e.value for e in SeverityLevel}
        assert actual == expected

    def test_genre_invalid_value(self) -> None:
        with pytest.raises(ValueError):
            Genre("invalid_genre")
