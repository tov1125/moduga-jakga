"""
Pydantic v2 Strict 타입 스키마 검증 테스트
타입 안전성 위반 0건을 보장합니다 (A16 품질 게이트 gate_1_code).

검증 항목:
  - Strict 타입 적용 (str에 int 불가 등)
  - Enum 값 검증
  - 필수 필드 누락 시 에러
"""

import pytest
from pydantic import ValidationError


class TestAuthSchemas:
    """인증 스키마 타입 안전성 테스트"""

    def test_signup_request_valid(self) -> None:
        from app.schemas.auth import DisabilityType, SignUpRequest

        req = SignUpRequest(
            email="user@example.com",
            password="StrongPass123!",
            display_name="사용자",
            disability_type=DisabilityType.VISUAL,
        )
        assert req.email == "user@example.com"

    def test_signup_request_missing_email(self) -> None:
        from app.schemas.auth import SignUpRequest

        with pytest.raises(ValidationError) as exc_info:
            SignUpRequest(
                password="StrongPass123!",
                display_name="사용자",
            )  # type: ignore[call-arg]
        assert "email" in str(exc_info.value)

    def test_signup_request_strict_type(self) -> None:
        """Strict 모드에서 int는 str 필드에 불가"""
        from app.schemas.auth import SignUpRequest

        with pytest.raises(ValidationError):
            SignUpRequest(
                email=12345,  # type: ignore[arg-type]
                password="StrongPass123!",
                display_name="사용자",
            )

    def test_login_request_valid(self) -> None:
        from app.schemas.auth import LoginRequest

        req = LoginRequest(
            email="user@example.com",
            password="Password123!",
        )
        assert req.email == "user@example.com"


class TestBookSchemas:
    """도서 스키마 타입 안전성 테스트"""

    def test_genre_enum_valid(self) -> None:
        from app.schemas.book import Genre

        assert Genre.ESSAY == "essay"
        assert Genre.NOVEL == "novel"
        assert Genre.POEM == "poem"
        assert Genre.AUTOBIOGRAPHY == "autobiography"

    def test_genre_enum_invalid(self) -> None:
        from app.schemas.book import Genre

        with pytest.raises(ValueError):
            Genre("invalid_genre")

    def test_book_create_valid(self) -> None:
        from app.schemas.book import BookCreate, Genre

        req = BookCreate(
            title="테스트 도서",
            genre=Genre.ESSAY,
        )
        assert req.title == "테스트 도서"

    def test_book_create_invalid_genre(self) -> None:
        from app.schemas.book import BookCreate

        with pytest.raises(ValidationError):
            BookCreate(
                title="테스트 도서",
                genre="invalid_genre",  # type: ignore[arg-type]
            )


class TestWritingSchemas:
    """글쓰기 스키마 타입 안전성 테스트"""

    def test_generate_request_valid(self) -> None:
        from app.schemas.book import Genre
        from app.schemas.writing import GenerateRequest

        req = GenerateRequest(
            prompt="오늘 아침에 산책을 하면서 느낀 점을 이야기하겠습니다.",
            genre=Genre.ESSAY,
        )
        assert req.prompt is not None

    def test_generate_request_empty_prompt(self) -> None:
        """빈 프롬프트는 스키마에서 허용 (엔드포인트에서 400 처리)"""
        from app.schemas.book import Genre
        from app.schemas.writing import GenerateRequest

        req = GenerateRequest(
            prompt="",
            genre=Genre.ESSAY,
        )
        assert req.prompt == ""


class TestEditingSchemas:
    """편집 스키마 타입 안전성 테스트"""

    def test_proofread_request_valid(self) -> None:
        from app.schemas.editing import ProofreadRequest

        req = ProofreadRequest(text="맞춤법을 검사할 문장입니다.")
        assert req.text == "맞춤법을 검사할 문장입니다."

    def test_proofread_request_strict_type(self) -> None:
        """Strict 모드에서 int는 str 필드에 불가"""
        from app.schemas.editing import ProofreadRequest

        with pytest.raises(ValidationError):
            ProofreadRequest(text=12345)  # type: ignore[arg-type]


class TestDesignSchemas:
    """디자인 스키마 타입 안전성 테스트"""

    def test_cover_style_enum(self) -> None:
        from app.schemas.design import CoverStyle

        assert CoverStyle.MINIMALIST == "minimalist"
        assert CoverStyle.ILLUSTRATED == "illustrated"

    def test_page_size_enum(self) -> None:
        from app.schemas.design import PageSize

        assert PageSize.A5 == "A5"
        assert PageSize.B5 == "B5"


class TestTTSSchemas:
    """TTS 스키마 타입 안전성 테스트"""

    def test_synthesize_request_valid(self) -> None:
        from app.schemas.tts import TTSSynthesizeRequest

        req = TTSSynthesizeRequest(text="음성으로 변환할 텍스트입니다.")
        assert req.text is not None

    def test_synthesize_request_strict_type(self) -> None:
        """Strict 모드에서 int는 str 필드에 불가"""
        from app.schemas.tts import TTSSynthesizeRequest

        with pytest.raises(ValidationError):
            TTSSynthesizeRequest(text=12345)  # type: ignore[arg-type]


class TestPublishingSchemas:
    """출판 스키마 타입 안전성 테스트"""

    def test_export_format_enum(self) -> None:
        from app.schemas.publishing import ExportFormat

        assert ExportFormat.DOCX == "docx"
        assert ExportFormat.PDF == "pdf"
        assert ExportFormat.EPUB == "epub"
