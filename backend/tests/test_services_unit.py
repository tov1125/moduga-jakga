"""
서비스 단위 테스트 — 모든 서비스의 내부 로직
외부 API 호출은 모두 mock 처리합니다.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.book import Genre


# ── WritingService 단위 테스트 ──────────────────────────────────────────────

class TestWritingServiceUnit:
    """WritingService의 generate_stream, rewrite, suggest_structure 테스트"""

    @pytest.fixture
    def service(self):
        mock_settings = MagicMock()
        mock_settings.OPENAI_API_KEY = "test-key"
        with patch("app.services.writing_service.AsyncOpenAI"):
            from app.services.writing_service import WritingService
            return WritingService(mock_settings)

    @pytest.mark.asyncio
    async def test_rewrite_반환값(self, service):
        """rewrite가 RewriteResponse를 반환한다"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                "rewritten_text": "수정된 텍스트",
                "changes_summary": "문체 개선",
            })))
        ]
        service._client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await service.rewrite("원본", "명료하게", Genre.ESSAY, "문어체")
        assert result.rewritten_text == "수정된 텍스트"
        assert result.changes_summary == "문체 개선"

    @pytest.mark.asyncio
    async def test_rewrite_style_guide_없이(self, service):
        """style_guide 없이도 정상 동작"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                "rewritten_text": "결과",
                "changes_summary": "요약",
            })))
        ]
        service._client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await service.rewrite("원본", "수정", Genre.NOVEL)
        assert result.rewritten_text == "결과"

    @pytest.mark.asyncio
    async def test_suggest_structure_반환값(self, service):
        """suggest_structure가 StructureResponse를 반환한다"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                "chapters": [
                    {"order": 1, "title": "시작", "description": "도입부", "estimated_pages": 10},
                    {"order": 2, "title": "전개", "description": "갈등", "estimated_pages": 15},
                ],
                "overall_summary": "2개 챕터 구성",
            })))
        ]
        service._client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await service.suggest_structure("나의 책", Genre.ESSAY, "에세이 모음", 2)
        assert len(result.chapters) == 2
        assert result.chapters[0].title == "시작"
        assert result.overall_summary == "2개 챕터 구성"

    @pytest.mark.asyncio
    async def test_generate_stream_에러_전파(self, service):
        """generate_stream에서 API 오류 발생 시 예외 전파"""
        service._client.chat.completions.create = AsyncMock(
            side_effect=RuntimeError("API 오류")
        )
        with pytest.raises(RuntimeError, match="API 오류"):
            async for _ in service.generate_stream(Genre.ESSAY, "테스트"):
                pass

    def test_장르별_시스템_프롬프트_존재(self):
        """모든 장르에 대해 시스템 프롬프트가 존재한다"""
        from app.services.writing_service import GENRE_SYSTEM_PROMPTS
        for genre in Genre:
            assert genre.value in GENRE_SYSTEM_PROMPTS


# ── TTSService 단위 테스트 ──────────────────────────────────────────────────

class TestTTSServiceUnit:
    """TTSService의 _split_text, get_supported_voices 테스트"""

    @pytest.fixture
    def service(self):
        mock_settings = MagicMock()
        mock_settings.CLOVA_VOICE_CLIENT_ID = "test-id"
        mock_settings.CLOVA_VOICE_CLIENT_SECRET = "test-secret"
        from app.services.tts_service import TTSService
        return TTSService(mock_settings)

    def test_split_text_짧은_텍스트(self, service):
        """2000자 이하는 분할 없음"""
        result = service._split_text("짧은 텍스트", max_length=2000)
        assert result == ["짧은 텍스트"]

    def test_split_text_긴_텍스트(self, service):
        """긴 텍스트는 여러 청크로 분할"""
        text = "가나다라. " * 300  # 약 1500자
        result = service._split_text(text, max_length=500)
        assert len(result) > 1
        for chunk in result:
            assert len(chunk) <= 500 or "." not in chunk  # 문장 경계 분할

    def test_split_text_문장_경계(self, service):
        """문장 경계에서 분할된다"""
        text = "첫 번째 문장입니다. 두 번째 문장입니다. 세 번째 문장입니다."
        result = service._split_text(text, max_length=30)
        assert len(result) >= 2

    @pytest.mark.asyncio
    async def test_get_supported_voices(self, service):
        """지원 음성 목록을 반환한다"""
        voices = await service.get_supported_voices()
        assert len(voices) == 8
        ids = [v["id"] for v in voices]
        assert "nara" in ids
        assert "nminsang" in ids

    @pytest.mark.asyncio
    async def test_synthesize_성공(self, service):
        """API 호출 성공 시 bytes 반환"""
        with patch("app.services.tts_service.httpx.AsyncClient") as mock_client_cls:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b"audio-data"
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            result = await service.synthesize("안녕하세요", "nara", 0)
            assert result == b"audio-data"

    @pytest.mark.asyncio
    async def test_synthesize_API_오류(self, service):
        """API 오류 시 RuntimeError 발생"""
        with patch("app.services.tts_service.httpx.AsyncClient") as mock_client_cls:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            with pytest.raises(RuntimeError, match="음성 합성 실패"):
                await service.synthesize("테스트", "nara", 0)


# ── SpellingService 단위 테스트 ──────────────────────────────────────────────

class TestSpellingServiceUnit:
    """SpellingService의 _split_text, _parse_response, apply_corrections 테스트"""

    @pytest.fixture
    def service(self):
        from app.services.spelling_service import SpellingService
        return SpellingService()

    def test_split_text_짧은_텍스트(self, service):
        """500자 이하는 분할 없음"""
        result = service._split_text("짧은 텍스트", max_length=500)
        assert result == ["짧은 텍스트"]

    def test_split_text_긴_텍스트_분할(self, service):
        """긴 텍스트가 올바르게 분할된다"""
        text = "테스트 문장입니다. " * 100  # 약 900자
        result = service._split_text(text, max_length=100)
        assert len(result) > 1

    def test_parse_response_빈_응답(self, service):
        """빈 HTML 응답 시 빈 리스트 반환"""
        result = service._parse_response("", "테스트", 0)
        assert result == []

    def test_parse_response_정상(self, service):
        """HTML 응답에서 교정 결과를 파싱한다"""
        html = (
            '<span data-error-input="잘 몰겠습니다" '
            'data-error-output="잘 모르겠습니다" '
            'data-error-help="맞춤법 오류">교정</span>'
        )
        result = service._parse_response(html, "잘 몰겠습니다", 0)
        assert len(result) == 1
        assert result[0]["original"] == "잘 몰겠습니다"
        assert result[0]["corrected"] == "잘 모르겠습니다"

    @pytest.mark.asyncio
    async def test_apply_corrections(self, service):
        """교정 결과가 텍스트에 올바르게 적용된다"""
        text = "잘 몰겠습니다"
        corrections = [
            {"original": "몰겠", "corrected": "모르겠", "position_start": 2, "position_end": 4},
        ]
        result = await service.apply_corrections(text, corrections)
        assert result == "잘 모르겠습니다"

    @pytest.mark.asyncio
    async def test_apply_corrections_역순_적용(self, service):
        """여러 교정이 역순으로 적용된다"""
        text = "가 나"
        corrections = [
            {"original": "가", "corrected": "다", "position_start": 0, "position_end": 1},
            {"original": "나", "corrected": "라", "position_start": 2, "position_end": 3},
        ]
        result = await service.apply_corrections(text, corrections)
        assert result == "다 라"

    @pytest.mark.asyncio
    async def test_check_spelling_API_타임아웃(self, service):
        """API 타임아웃 시 빈 리스트 반환"""
        import httpx
        with patch("app.services.spelling_service.httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = mock_client

            result = await service.check_spelling("테스트")
            assert result == []


# ── EditingService 단위 테스트 ──────────────────────────────────────────────

class TestEditingServiceUnit:
    """EditingService의 proofread, check_style, review_structure, full_review 테스트"""

    @pytest.fixture
    def service(self):
        mock_settings = MagicMock()
        mock_settings.OPENAI_API_KEY = "test-key"
        with patch("app.services.editing_service.AsyncOpenAI"):
            from app.services.editing_service import EditingService
            return EditingService(mock_settings)

    def _mock_openai_response(self, service, content_dict):
        """OpenAI 응답 mock 헬퍼"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps(content_dict)))
        ]
        service._client.chat.completions.create = AsyncMock(return_value=mock_response)

    @pytest.mark.asyncio
    async def test_proofread_정상(self, service):
        """proofread가 ProofreadResult를 반환한다"""
        self._mock_openai_response(service, {
            "corrected_text": "교정된 텍스트입니다.",
            "corrections": [
                {
                    "original": "텍스트이ㅂ니다",
                    "corrected": "텍스트입니다",
                    "reason": "맞춤법 오류",
                    "position_start": 4,
                    "position_end": 9,
                    "severity": "error",
                }
            ],
            "accuracy_score": 85.0,
        })

        result = await service.proofread("텍스트이ㅂ니다.")
        assert result.corrected_text == "교정된 텍스트입니다."
        assert result.total_corrections == 1
        assert result.accuracy_score == 85.0
        assert result.corrections[0].original == "텍스트이ㅂ니다"

    @pytest.mark.asyncio
    async def test_proofread_교정없음(self, service):
        """교정 사항이 없을 때 빈 리스트"""
        self._mock_openai_response(service, {
            "corrected_text": "완벽한 텍스트",
            "corrections": [],
            "accuracy_score": 100.0,
        })

        result = await service.proofread("완벽한 텍스트")
        assert result.total_corrections == 0
        assert result.accuracy_score == 100.0

    @pytest.mark.asyncio
    async def test_proofread_에러_전파(self, service):
        """API 오류 시 예외 전파"""
        service._client.chat.completions.create = AsyncMock(
            side_effect=RuntimeError("API error")
        )
        with pytest.raises(RuntimeError, match="API error"):
            await service.proofread("테스트")

    @pytest.mark.asyncio
    async def test_check_style_정상(self, service):
        """check_style이 StyleCheckResult를 반환한다"""
        self._mock_openai_response(service, {
            "issues": [
                {
                    "text_excerpt": "~했다",
                    "issue": "구어체 혼용",
                    "suggestion": "~하였다",
                    "severity": "warning",
                }
            ],
            "consistency_score": 75.0,
            "overall_feedback": "문체 일관성 보통",
        })

        result = await service.check_style("테스트 텍스트", genre="소설")
        assert result.consistency_score == 75.0
        assert len(result.issues) == 1
        assert result.overall_feedback == "문체 일관성 보통"

    @pytest.mark.asyncio
    async def test_check_style_참조문체_포함(self, service):
        """reference_style이 프롬프트에 포함된다"""
        self._mock_openai_response(service, {
            "issues": [],
            "consistency_score": 90.0,
            "overall_feedback": "좋음",
        })

        result = await service.check_style("텍스트", reference_style="문어체", genre="에세이")
        assert result.consistency_score == 90.0

    @pytest.mark.asyncio
    async def test_review_structure_정상(self, service):
        """review_structure가 StructureReviewResult를 반환한다"""
        self._mock_openai_response(service, {
            "flow_score": 80.0,
            "organization_score": 85.0,
            "feedback": ["흐름이 자연스럽습니다"],
            "suggestions": ["챕터 2 보강 필요"],
        })

        result = await service.review_structure(["챕터1 내용", "챕터2 내용"])
        assert result.flow_score == 80.0
        assert result.organization_score == 85.0
        assert len(result.feedback) == 1
        assert len(result.suggestions) == 1

    @pytest.mark.asyncio
    async def test_review_structure_긴_챕터(self, service):
        """500자 넘는 챕터는 잘린다"""
        self._mock_openai_response(service, {
            "flow_score": 70.0,
            "organization_score": 70.0,
            "feedback": [],
            "suggestions": [],
        })

        long_text = "가" * 600
        result = await service.review_structure([long_text])
        assert result.flow_score == 70.0
        # API가 호출되었는지 확인
        service._client.chat.completions.create.assert_called_once()

    def test_generate_summary_우수(self, service):
        """90점 이상 → 우수"""
        from app.schemas.editing import EditingStage, StageResult
        stages = [StageResult(stage=EditingStage.STRUCTURE, score=95.0, issues_count=0, feedback="좋음")]
        summary, recs = service._generate_summary(stages, 95.0)
        assert "우수" in summary
        assert len(recs) == 1  # 기본 권장사항

    def test_generate_summary_개선필요(self, service):
        """60점 미만 → 개선 필요"""
        from app.schemas.editing import EditingStage, StageResult
        stages = [StageResult(stage=EditingStage.PROOFREAD, score=50.0, issues_count=5, feedback="문제 많음")]
        summary, recs = service._generate_summary(stages, 50.0)
        assert "개선" in summary
        assert any("맞춤법" in r for r in recs)

    def test_generate_summary_양호(self, service):
        """75~89점 → 양호"""
        from app.schemas.editing import EditingStage, StageResult
        stages = [StageResult(stage=EditingStage.CONTENT, score=80.0, issues_count=2, feedback="괜찮음")]
        summary, recs = service._generate_summary(stages, 80.0)
        assert "양호" in summary

    @pytest.mark.asyncio
    async def test_final_review_정상(self, service):
        """_final_review가 딕셔너리를 반환한다"""
        self._mock_openai_response(service, {
            "score": 92.0,
            "issues_count": 1,
            "feedback": "거의 완벽",
        })

        result = await service._final_review("테스트 텍스트")
        assert result["score"] == 92.0
        assert result["issues_count"] == 1

    @pytest.mark.asyncio
    async def test_final_review_에러시_기본값(self, service):
        """_final_review API 오류 시 기본값 반환"""
        service._client.chat.completions.create = AsyncMock(
            side_effect=RuntimeError("API error")
        )
        result = await service._final_review("텍스트")
        assert result["score"] == 0.0
        assert "오류" in result["feedback"]

    @pytest.mark.asyncio
    async def test_full_review_전체단계(self, service):
        """full_review가 4단계 모두 실행한다"""
        # 각 단계 mock
        responses = [
            # review_structure
            {"flow_score": 80.0, "organization_score": 85.0, "feedback": ["좋음"], "suggestions": []},
            # check_style
            {"issues": [], "consistency_score": 90.0, "overall_feedback": "일관성 좋음"},
            # proofread
            {"corrected_text": "텍스트", "corrections": [], "accuracy_score": 95.0},
            # _final_review
            {"score": 88.0, "issues_count": 0, "feedback": "완료"},
        ]
        call_count = 0

        async def mock_create(**kwargs):
            nonlocal call_count
            resp = MagicMock()
            resp.choices = [MagicMock(message=MagicMock(content=json.dumps(responses[call_count])))]
            call_count += 1
            return resp

        service._client.chat.completions.create = mock_create

        result = await service.full_review(
            book_id="test-book",
            chapters=[{"content": "챕터 내용"}],
        )

        assert result.book_id == "test-book"
        assert len(result.stage_results) == 4
        assert result.overall_score > 0


# ── SupabaseService 단위 테스트 ──────────────────────────────────────────────

class TestSupabaseServiceUnit:
    """SupabaseService의 CRUD 및 도메인 쿼리 테스트"""

    @pytest.fixture
    def mock_client(self):
        return MagicMock()

    @pytest.fixture
    def service(self, mock_client):
        from app.services.supabase_service import SupabaseService
        return SupabaseService(mock_client)

    def _chain_mock(self, mock_client, data, count=None):
        """Supabase 체인 패턴 mock 헬퍼"""
        mock_resp = MagicMock()
        mock_resp.data = data
        mock_resp.count = count

        mock_exec = MagicMock(return_value=mock_resp)
        mock_chain = MagicMock()
        mock_chain.execute = mock_exec
        mock_chain.eq = MagicMock(return_value=mock_chain)
        mock_chain.order = MagicMock(return_value=mock_chain)
        mock_chain.limit = MagicMock(return_value=mock_chain)

        mock_table = MagicMock()
        mock_table.insert = MagicMock(return_value=mock_chain)
        mock_table.select = MagicMock(return_value=mock_chain)
        mock_table.update = MagicMock(return_value=mock_chain)
        mock_table.delete = MagicMock(return_value=mock_chain)

        mock_client.table = MagicMock(return_value=mock_table)
        return mock_resp

    @pytest.mark.asyncio
    async def test_insert_성공(self, service, mock_client):
        """insert가 삽입된 레코드를 반환한다"""
        self._chain_mock(mock_client, [{"id": "1", "name": "test"}])
        result = await service.insert("test_table", {"name": "test"})
        assert result["id"] == "1"

    @pytest.mark.asyncio
    async def test_insert_실패(self, service, mock_client):
        """insert 실패 시 ValueError 발생"""
        self._chain_mock(mock_client, [])
        with pytest.raises(ValueError, match="삽입 실패"):
            await service.insert("test_table", {"name": "test"})

    @pytest.mark.asyncio
    async def test_select_필터(self, service, mock_client):
        """select가 필터된 데이터를 반환한다"""
        self._chain_mock(mock_client, [{"id": "1"}, {"id": "2"}])
        result = await service.select("books", filters={"user_id": "u1"})
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_select_one_존재(self, service, mock_client):
        """select_one이 단일 레코드를 반환한다"""
        self._chain_mock(mock_client, [{"id": "1"}])
        result = await service.select_one("books", filters={"id": "1"})
        assert result["id"] == "1"

    @pytest.mark.asyncio
    async def test_select_one_없음(self, service, mock_client):
        """select_one 결과 없으면 None"""
        self._chain_mock(mock_client, [])
        result = await service.select_one("books", filters={"id": "x"})
        assert result is None

    @pytest.mark.asyncio
    async def test_update_성공(self, service, mock_client):
        """update가 갱신된 레코드를 반환한다"""
        self._chain_mock(mock_client, [{"id": "1", "name": "updated"}])
        result = await service.update("books", {"name": "updated"}, filters={"id": "1"})
        assert result["name"] == "updated"

    @pytest.mark.asyncio
    async def test_update_실패(self, service, mock_client):
        """update 실패 시 ValueError"""
        self._chain_mock(mock_client, [])
        with pytest.raises(ValueError, match="업데이트 실패"):
            await service.update("books", {"name": "x"}, filters={"id": "x"})

    @pytest.mark.asyncio
    async def test_delete(self, service, mock_client):
        """delete가 예외 없이 실행된다"""
        self._chain_mock(mock_client, [])
        await service.delete("books", filters={"id": "1"})  # 예외 없으면 통과

    @pytest.mark.asyncio
    async def test_count(self, service, mock_client):
        """count가 레코드 수를 반환한다"""
        self._chain_mock(mock_client, [], count=5)
        result = await service.count("books", filters={"user_id": "u1"})
        assert result == 5

    @pytest.mark.asyncio
    async def test_get_user_books(self, service, mock_client):
        """get_user_books가 도서 목록을 반환한다"""
        self._chain_mock(mock_client, [{"id": "b1", "title": "책1"}])
        result = await service.get_user_books("u1")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_user_books_상태필터(self, service, mock_client):
        """get_user_books가 상태 필터를 적용한다"""
        self._chain_mock(mock_client, [])
        result = await service.get_user_books("u1", status_filter="published")
        assert result == []

    @pytest.mark.asyncio
    async def test_get_next_chapter_order_빈목록(self, service, mock_client):
        """챕터가 없으면 1을 반환"""
        self._chain_mock(mock_client, [])
        result = await service.get_next_chapter_order("b1")
        assert result == 1

    @pytest.mark.asyncio
    async def test_get_next_chapter_order_있음(self, service, mock_client):
        """마지막 챕터 order + 1을 반환"""
        self._chain_mock(mock_client, [{"order": 3}])
        result = await service.get_next_chapter_order("b1")
        assert result == 4


# ── PublishingService 단위 테스트 ──────────────────────────────────────────────

class TestPublishingServiceUnit:
    """PublishingService의 이스케이프 함수 및 유틸리티 테스트"""

    @pytest.fixture
    def service(self):
        mock_settings = MagicMock()
        with patch("os.makedirs"):
            from app.services.publishing_service import PublishingService
            return PublishingService(mock_settings)

    def test_escape_typst(self, service):
        """Typst 특수 문자가 이스케이프된다"""
        result = service._escape_typst("#제목 *강조* $수식$")
        assert "\\#" in result
        assert "\\*" in result
        assert "\\$" in result

    def test_escape_typst_일반텍스트(self, service):
        """일반 텍스트는 변하지 않는다"""
        result = service._escape_typst("안녕하세요")
        assert result == "안녕하세요"

    def test_escape_html(self, service):
        """HTML 특수 문자가 이스케이프된다"""
        result = service._escape_html('<script>alert("xss")</script>')
        assert "&lt;" in result
        assert "&gt;" in result
        assert "&quot;" in result
        assert "<script>" not in result

    def test_escape_html_일반텍스트(self, service):
        """일반 텍스트는 변하지 않는다"""
        result = service._escape_html("안녕하세요")
        assert result == "안녕하세요"

    @pytest.mark.asyncio
    async def test_resolve_cover_path_존재(self, service):
        """static 경로가 실제 파일이면 절대경로 반환"""
        with patch("os.path.exists", return_value=True):
            result = await service._resolve_cover_path("/static/covers/test.png")
            assert result is not None
            assert "test.png" in result

    @pytest.mark.asyncio
    async def test_resolve_cover_path_미존재(self, service):
        """파일이 없으면 None 반환"""
        with patch("os.path.exists", return_value=False):
            result = await service._resolve_cover_path("/static/covers/missing.png")
            assert result is None

    @pytest.mark.asyncio
    async def test_resolve_cover_path_외부URL(self, service):
        """static이 아닌 URL은 None 반환"""
        result = await service._resolve_cover_path("https://example.com/img.png")
        assert result is None

    @pytest.mark.asyncio
    async def test_start_export_no_supabase(self, service):
        """supabase 없으면 ValueError"""
        with pytest.raises(ValueError, match="Supabase"):
            await service.start_export(
                export_id="e1",
                book_data={"id": "b1"},
                export_format=MagicMock(value="docx"),
            )

    @pytest.mark.asyncio
    async def test_export_docx_기본(self, service):
        """_export_docx가 DOCX 파일을 생성한다"""
        import os
        chapters = [
            {"title": "서론", "content": "첫 번째 챕터 내용입니다.", "order": 1},
            {"title": "본론", "content": "두 번째 챕터.\n두 번째 문단.", "order": 2},
        ]
        book_data = {"title": "테스트 책", "description": "설명입니다"}

        file_path = await service._export_docx("test-id", book_data, chapters, include_toc=True)
        assert os.path.exists(file_path)
        assert file_path.endswith(".docx")
        # 정리
        os.unlink(file_path)

    @pytest.mark.asyncio
    async def test_export_docx_표지없음(self, service):
        """표지 없이 DOCX 생성"""
        import os
        chapters = [{"title": "챕터1", "content": "내용", "order": 1}]
        book_data = {"title": "표지 없는 책"}

        file_path = await service._export_docx("test-no-cover", book_data, chapters, include_toc=False)
        assert os.path.exists(file_path)
        os.unlink(file_path)

    @pytest.mark.asyncio
    async def test_start_export_docx(self, service):
        """start_export로 DOCX 내보내기 전체 플로우"""
        import os
        from app.schemas.publishing import ExportFormat

        mock_supabase = MagicMock()
        # chapters query
        mock_ch_resp = MagicMock()
        mock_ch_resp.data = [{"title": "챕터1", "content": "내용", "order": 1}]
        # exports update
        mock_update_chain = MagicMock()
        mock_update_chain.eq = MagicMock(return_value=mock_update_chain)
        mock_update_chain.execute = MagicMock(return_value=MagicMock(data=[{"id": "e1"}]))

        mock_select_chain = MagicMock()
        mock_select_chain.eq = MagicMock(return_value=mock_select_chain)
        mock_select_chain.order = MagicMock(return_value=mock_select_chain)
        mock_select_chain.execute = MagicMock(return_value=mock_ch_resp)

        def table_dispatch(name):
            t = MagicMock()
            t.select = MagicMock(return_value=mock_select_chain)
            t.update = MagicMock(return_value=mock_update_chain)
            return t

        mock_supabase.table = table_dispatch

        book_data = {"id": "b1", "title": "테스트"}
        file_path = await service.start_export(
            export_id="e1",
            book_data=book_data,
            export_format=ExportFormat.DOCX,
            supabase=mock_supabase,
        )
        assert file_path.endswith(".docx")
        if os.path.exists(file_path):
            os.unlink(file_path)

    @pytest.mark.asyncio
    async def test_start_export_실패시_상태업데이트(self, service):
        """내보내기 실패 시 FAILED 상태로 업데이트"""
        mock_supabase = MagicMock()
        mock_ch_resp = MagicMock()
        mock_ch_resp.data = [{"title": "ch1", "content": "text", "order": 1}]

        mock_chain = MagicMock()
        mock_chain.eq = MagicMock(return_value=mock_chain)
        mock_chain.order = MagicMock(return_value=mock_chain)
        mock_chain.execute = MagicMock(return_value=mock_ch_resp)

        mock_update_chain = MagicMock()
        mock_update_chain.eq = MagicMock(return_value=mock_update_chain)
        mock_update_chain.execute = MagicMock(return_value=MagicMock(data=[{}]))

        def table_dispatch(name):
            t = MagicMock()
            t.select = MagicMock(return_value=mock_chain)
            t.update = MagicMock(return_value=mock_update_chain)
            return t

        mock_supabase.table = table_dispatch

        # 지원하지 않는 형식으로 에러 유도
        with pytest.raises(ValueError, match="지원하지 않는"):
            await service.start_export(
                export_id="e1",
                book_data={"id": "b1", "title": "테스트"},
                export_format=MagicMock(value="hwpx"),
                supabase=mock_supabase,
            )

    @pytest.mark.asyncio
    async def test_start_export_pdf_typst_미설치(self, service):
        """PDF 내보내기 시 Typst 미설치 에러"""
        from app.schemas.publishing import ExportFormat

        mock_supabase = MagicMock()
        mock_ch_resp = MagicMock()
        mock_ch_resp.data = [{"title": "ch1", "content": "내용", "order": 1}]

        mock_chain = MagicMock()
        mock_chain.eq = MagicMock(return_value=mock_chain)
        mock_chain.order = MagicMock(return_value=mock_chain)
        mock_chain.execute = MagicMock(return_value=mock_ch_resp)

        mock_update_chain = MagicMock()
        mock_update_chain.eq = MagicMock(return_value=mock_update_chain)
        mock_update_chain.execute = MagicMock(return_value=MagicMock(data=[{}]))

        def table_dispatch(_name):
            t = MagicMock()
            t.select = MagicMock(return_value=mock_chain)
            t.update = MagicMock(return_value=mock_update_chain)
            return t

        mock_supabase.table = table_dispatch

        with patch("subprocess.run", side_effect=FileNotFoundError("typst not found")):
            with pytest.raises(RuntimeError, match="Typst"):
                await service.start_export(
                    export_id="e-pdf",
                    book_data={"id": "b1", "title": "PDF 책"},
                    export_format=ExportFormat.PDF,
                    supabase=mock_supabase,
                )

    @pytest.mark.asyncio
    async def test_start_export_epub(self, service):
        """EPUB 내보내기 전체 플로우"""
        import os
        from app.schemas.publishing import ExportFormat

        mock_supabase = MagicMock()
        mock_ch_resp = MagicMock()
        mock_ch_resp.data = [{"title": "챕터1", "content": "EPUB 내용\n두 번째 문단", "order": 1}]

        mock_chain = MagicMock()
        mock_chain.eq = MagicMock(return_value=mock_chain)
        mock_chain.order = MagicMock(return_value=mock_chain)
        mock_chain.execute = MagicMock(return_value=mock_ch_resp)

        mock_update_chain = MagicMock()
        mock_update_chain.eq = MagicMock(return_value=mock_update_chain)
        mock_update_chain.execute = MagicMock(return_value=MagicMock(data=[{}]))

        def table_dispatch(_name):
            t = MagicMock()
            t.select = MagicMock(return_value=mock_chain)
            t.update = MagicMock(return_value=mock_update_chain)
            return t

        mock_supabase.table = table_dispatch

        file_path = await service.start_export(
            export_id="e-epub",
            book_data={"id": "b1", "title": "EPUB 책", "author_name": "테스트 작가"},
            export_format=ExportFormat.EPUB,
            supabase=mock_supabase,
        )
        assert file_path.endswith(".epub")
        if os.path.exists(file_path):
            os.unlink(file_path)


# ── DesignService 단위 테스트 ──────────────────────────────────────────────

class TestDesignServiceUnit:
    """DesignService의 유틸리티 및 상수 테스트"""

    def test_style_keywords_모든_스타일(self):
        """모든 CoverStyle에 대해 키워드가 존재한다"""
        from app.schemas.design import CoverStyle
        from app.services.design_service import STYLE_KEYWORDS
        for style in CoverStyle:
            assert style.value in STYLE_KEYWORDS

    def test_genre_keywords_모든_장르(self):
        """모든 Genre에 대해 키워드가 존재한다"""
        from app.schemas.book import Genre
        from app.services.design_service import GENRE_KEYWORDS
        for genre in Genre:
            assert genre.value in GENRE_KEYWORDS

    def test_count_pdf_pages(self):
        """_count_pdf_pages가 페이지 수를 반환한다"""
        import tempfile
        mock_settings = MagicMock()
        mock_settings.GOOGLE_API_KEY = "test-key"
        with patch("app.services.design_service.genai"):
            from app.services.design_service import DesignService
            svc = DesignService(mock_settings)

        # 간단한 PDF 모방: /Type /Page 3회 매칭(Pages 포함) - /Type /Pages 1회 = 2
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"/Type /Pages\n/Type /Page\n/Type /Page\n")
            f.flush()
            result = svc._count_pdf_pages(f.name)
            assert result == 2

        import os
        os.unlink(f.name)

    def test_count_pdf_pages_파일없음(self):
        """파일이 없으면 1 반환"""
        mock_settings = MagicMock()
        mock_settings.GOOGLE_API_KEY = "test-key"
        with patch("app.services.design_service.genai"):
            from app.services.design_service import DesignService
            svc = DesignService(mock_settings)

        result = svc._count_pdf_pages("/nonexistent/file.pdf")
        assert result == 1

    @pytest.mark.asyncio
    async def test_generate_cover_rate_limit(self):
        """API rate limit 시 친절한 에러 메시지"""
        mock_settings = MagicMock()
        mock_settings.GOOGLE_API_KEY = "test-key"
        with patch("app.services.design_service.genai"):
            from app.services.design_service import DesignService
            svc = DesignService(mock_settings)

        with patch("asyncio.to_thread", new_callable=AsyncMock) as mock_thread:
            mock_thread.side_effect = RuntimeError("429 resource_exhausted")
            with pytest.raises(RuntimeError, match="사용량 한도"):
                from app.schemas.book import Genre
                from app.schemas.design import CoverStyle
                await svc.generate_cover("책제목", "저자", Genre.ESSAY, CoverStyle.MINIMALIST)

    @pytest.mark.asyncio
    async def test_generate_cover_no_image(self):
        """응답에 이미지가 없으면 RuntimeError"""
        mock_settings = MagicMock()
        mock_settings.GOOGLE_API_KEY = "test-key"
        with patch("app.services.design_service.genai"):
            from app.services.design_service import DesignService
            svc = DesignService(mock_settings)

        mock_part = MagicMock()
        mock_part.inline_data = None
        mock_response = MagicMock()
        mock_response.candidates = [MagicMock(content=MagicMock(parts=[mock_part]))]

        with patch("asyncio.to_thread", new_callable=AsyncMock, return_value=mock_response):
            with pytest.raises(RuntimeError, match="이미지가 포함되지"):
                from app.schemas.book import Genre
                from app.schemas.design import CoverStyle
                await svc.generate_cover("책제목", "저자", Genre.ESSAY, CoverStyle.MINIMALIST)

    @pytest.mark.asyncio
    async def test_generate_layout_preview_fallback(self):
        """Typst 컴파일 실패 시 페이지 수 추정 폴백"""
        mock_settings = MagicMock()
        mock_settings.GOOGLE_API_KEY = "test-key"
        with patch("app.services.design_service.genai"):
            from app.services.design_service import DesignService
            svc = DesignService(mock_settings)

        mock_supabase = MagicMock()
        mock_resp = MagicMock()
        mock_resp.data = [{"title": "챕터1", "content": "가" * 2000, "order": 1}]
        mock_chain = MagicMock()
        mock_chain.execute = MagicMock(return_value=mock_resp)
        mock_chain.eq = MagicMock(return_value=mock_chain)
        mock_chain.order = MagicMock(return_value=mock_chain)
        mock_table = MagicMock()
        mock_table.select = MagicMock(return_value=mock_chain)
        mock_supabase.table = MagicMock(return_value=mock_table)

        with patch.object(svc, "_compile_typst", new_callable=AsyncMock, side_effect=RuntimeError("typst not found")):
            from app.schemas.design import PageSize
            result = await svc.generate_layout_preview("b1", supabase=mock_supabase)
            assert result.total_pages >= 1
            assert result.preview_url == ""


# ── SupabaseService 도메인 쿼리 추가 테스트 ──────────────────────────────────

class TestSupabaseServiceDomainUnit:
    """SupabaseService의 도메인 특화 쿼리 테스트"""

    @pytest.fixture
    def mock_client(self):
        return MagicMock()

    @pytest.fixture
    def service(self, mock_client):
        from app.services.supabase_service import SupabaseService
        return SupabaseService(mock_client)

    def _chain_mock(self, mock_client, data, count=None):
        """Supabase 체인 패턴 mock"""
        mock_resp = MagicMock()
        mock_resp.data = data
        mock_resp.count = count
        mock_chain = MagicMock()
        mock_chain.execute = MagicMock(return_value=mock_resp)
        mock_chain.eq = MagicMock(return_value=mock_chain)
        mock_chain.order = MagicMock(return_value=mock_chain)
        mock_chain.limit = MagicMock(return_value=mock_chain)
        mock_table = MagicMock()
        mock_table.insert = MagicMock(return_value=mock_chain)
        mock_table.select = MagicMock(return_value=mock_chain)
        mock_table.update = MagicMock(return_value=mock_chain)
        mock_table.delete = MagicMock(return_value=mock_chain)
        mock_client.table = MagicMock(return_value=mock_table)

    @pytest.mark.asyncio
    async def test_get_book_with_chapters_존재(self, service, mock_client):
        """도서와 챕터를 함께 반환한다"""
        call_count = 0
        responses = [
            [{"id": "b1", "title": "테스트 책"}],
            [{"id": "c1", "book_id": "b1", "title": "챕터1", "order": 1}],
        ]

        mock_chain = MagicMock()

        def make_execute():
            nonlocal call_count
            r = MagicMock()
            r.data = responses[min(call_count, len(responses) - 1)]
            r.count = None
            call_count += 1
            return r

        mock_chain.execute = make_execute
        mock_chain.eq = MagicMock(return_value=mock_chain)
        mock_chain.order = MagicMock(return_value=mock_chain)
        mock_chain.limit = MagicMock(return_value=mock_chain)
        mock_table = MagicMock()
        mock_table.select = MagicMock(return_value=mock_chain)
        mock_client.table = MagicMock(return_value=mock_table)

        result = await service.get_book_with_chapters("b1", "u1")
        assert result is not None
        assert result["title"] == "테스트 책"
        assert "chapters" in result

    @pytest.mark.asyncio
    async def test_get_book_with_chapters_없음(self, service, mock_client):
        """도서가 없으면 None 반환"""
        self._chain_mock(mock_client, [])
        result = await service.get_book_with_chapters("missing", "u1")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_book_chapters(self, service, mock_client):
        """도서 챕터 목록을 반환한다"""
        self._chain_mock(mock_client, [
            {"id": "c1", "order": 1},
            {"id": "c2", "order": 2},
        ])
        result = await service.get_book_chapters("b1")
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_user_exports(self, service, mock_client):
        """사용자 내보내기 목록을 반환한다"""
        self._chain_mock(mock_client, [{"id": "e1", "format": "pdf"}])
        result = await service.get_user_exports("u1")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_user_exports_book필터(self, service, mock_client):
        """book_id 필터 적용"""
        self._chain_mock(mock_client, [])
        result = await service.get_user_exports("u1", book_id="b1")
        assert result == []

    @pytest.mark.asyncio
    async def test_update_export_status(self, service, mock_client):
        """내보내기 상태 업데이트"""
        self._chain_mock(mock_client, [{"id": "e1", "status": "completed"}])
        await service.update_export_status("e1", "completed", 100.0, "/path/file.pdf")

    @pytest.mark.asyncio
    async def test_update_book_stats(self, service, mock_client):
        """도서 통계 업데이트"""
        call_count = 0
        responses = [
            [{"word_count": 100}, {"word_count": 200}],
            [{"id": "b1"}],
        ]

        mock_chain = MagicMock()

        def make_execute():
            nonlocal call_count
            r = MagicMock()
            r.data = responses[min(call_count, len(responses) - 1)]
            r.count = None
            call_count += 1
            return r

        mock_chain.execute = make_execute
        mock_chain.eq = MagicMock(return_value=mock_chain)
        mock_chain.order = MagicMock(return_value=mock_chain)
        mock_chain.limit = MagicMock(return_value=mock_chain)
        mock_table = MagicMock()
        mock_table.select = MagicMock(return_value=mock_chain)
        mock_table.update = MagicMock(return_value=mock_chain)
        mock_client.table = MagicMock(return_value=mock_table)

        await service.update_book_stats("b1")


# ── STTService 추가 단위 테스트 ──────────────────────────────────────────────

class TestSTTServiceUnit:
    """STTService의 초기화, 오디오 처리, 파싱 테스트"""

    @pytest.fixture
    def service(self):
        mock_settings = MagicMock()
        mock_settings.CLOVA_SPEECH_SECRET = "test-secret"
        mock_settings.CLOVA_SPEECH_INVOKE_URL = "https://test.api"
        from app.services.stt_service import STTService
        return STTService(mock_settings)

    @pytest.mark.asyncio
    async def test_initialize(self, service):
        """초기화 후 언어 설정 확인"""
        await service.initialize("en-US")
        assert service._language == "en-US"
        assert service._http_client is not None
        await service.close()

    def test_parse_recognition_result(self, service):
        """인식 결과 파싱"""
        raw = {
            "text": "안녕하세요",
            "segments": [
                {"text": "안녕하세요", "start": 0, "end": 1500, "confidence": 0.95},
            ],
        }
        result = service._parse_recognition_result(raw)
        assert result["text"] == "안녕하세요"
        assert result["is_final"] is True
        assert len(result["segments"]) == 1
        assert result["segments"][0]["start_time"] == 0.0
        assert result["segments"][0]["end_time"] == 1.5

    @pytest.mark.asyncio
    async def test_process_audio_chunk_작은버퍼(self, service):
        """작은 청크는 None 반환 (버퍼링)"""
        result = await service.process_audio_chunk(b"\x00" * 100)
        assert result is None

    @pytest.mark.asyncio
    async def test_process_audio_chunk_충분한버퍼(self, service):
        """버퍼가 충분하면 인식 요청"""
        await service.initialize()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"text": "인식됨", "segments": []}
        service._http_client.post = AsyncMock(return_value=mock_response)

        big_chunk = b"\x00" * (32 * 1024 + 1)
        result = await service.process_audio_chunk(big_chunk)
        assert result is not None
        assert result["text"] == "인식됨"
        await service.close()

    @pytest.mark.asyncio
    async def test_send_recognition_no_client(self, service):
        """클라이언트 미초기화 시 None"""
        result = await service._send_recognition_request(b"data")
        assert result is None

    @pytest.mark.asyncio
    async def test_send_recognition_api_error(self, service):
        """API 오류 시 None"""
        await service.initialize()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "error"
        service._http_client.post = AsyncMock(return_value=mock_response)
        result = await service._send_recognition_request(b"data")
        assert result is None
        await service.close()

    @pytest.mark.asyncio
    async def test_send_recognition_timeout(self, service):
        """타임아웃 시 None"""
        import httpx
        await service.initialize()
        service._http_client.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
        result = await service._send_recognition_request(b"data")
        assert result is None
        await service.close()

    @pytest.mark.asyncio
    async def test_finalize_빈버퍼(self, service):
        """빈 버퍼에서 finalize는 None"""
        result = await service.finalize()
        assert result is None

    @pytest.mark.asyncio
    async def test_finalize_남은버퍼(self, service):
        """남은 버퍼가 있으면 처리"""
        await service.initialize()
        service._audio_buffer.extend(b"\x00" * 100)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"text": "마지막", "segments": []}
        service._http_client.post = AsyncMock(return_value=mock_response)

        result = await service.finalize()
        assert result is not None
        assert result["text"] == "마지막"
        await service.close()


# ── WritingService 추가 테스트 ──────────────────────────────────────────────

class TestWritingServiceAdditional:
    """WritingService의 generate_stream 정상 케이스 테스트"""

    @pytest.fixture
    def service(self):
        mock_settings = MagicMock()
        mock_settings.OPENAI_API_KEY = "test-key"
        with patch("app.services.writing_service.AsyncOpenAI"):
            from app.services.writing_service import WritingService
            return WritingService(mock_settings)

    @pytest.mark.asyncio
    async def test_generate_stream_정상(self, service):
        """generate_stream이 텍스트 청크를 생성한다"""
        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock(delta=MagicMock(content="안녕"))]
        mock_chunk2 = MagicMock()
        mock_chunk2.choices = [MagicMock(delta=MagicMock(content="하세요"))]
        mock_chunk3 = MagicMock()
        mock_chunk3.choices = [MagicMock(delta=MagicMock(content=None))]

        async def mock_stream():
            for chunk in [mock_chunk1, mock_chunk2, mock_chunk3]:
                yield chunk

        service._client.chat.completions.create = AsyncMock(return_value=mock_stream())

        chunks = []
        from app.schemas.book import Genre
        async for text in service.generate_stream(
            genre=Genre.ESSAY,
            prompt="테스트",
        ):
            chunks.append(text)

        assert "안녕" in chunks
        assert "하세요" in chunks
