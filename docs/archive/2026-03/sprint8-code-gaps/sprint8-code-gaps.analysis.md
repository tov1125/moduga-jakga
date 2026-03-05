# sprint8-code-gaps Analysis Report

> **Analysis Type**: Gap Analysis (Plan vs Implementation)
>
> **Project**: moduga-jakga
> **Version**: v0.2.0
> **Analyst**: gap-detector
> **Date**: 2026-03-06
> **Plan Doc**: [sprint8-code-gaps.plan.md](../01-plan/features/sprint8-code-gaps.plan.md)

---

## 1. Analysis Overview

### 1.1 Analysis Purpose

Sprint 8 Plan에서 정의한 6개 코드 Gap 수정 항목이 실제 구현과 일치하는지 검증한다.

### 1.2 Analysis Scope

- **Plan Document**: `docs/01-plan/features/sprint8-code-gaps.plan.md`
- **Implementation Files** (4개):
  - `backend/app/api/v1/design.py`
  - `backend/app/schemas/publishing.py`
  - `backend/app/services/design_service.py`
  - `backend/app/services/publishing_service.py`
- **Analysis Date**: 2026-03-06

---

## 2. Gap-by-Gap Verification

### Gap 1: LayoutPreview /tmp 경로 (CRITICAL)

| Item | Plan | Implementation | Status |
|------|------|----------------|--------|
| Target file | `design_service.py` - `_compile_typst()` | `design_service.py:261-299` | MATCH |
| Problem | TemporaryDirectory 블록 종료 시 파일 삭제 | -- | -- |
| Fix: static/previews/ 저장 | PDF를 `static/previews/`에 저장 | `PREVIEWS_DIR` 상수(L33) + `shutil.copy2(tmp_pdf, dest_path)` (L296) | MATCH |
| Fix: URL 반환 형식 | `/static/previews/xxx.pdf` | `f"/static/previews/{preview_id}.pdf"` (L298) | MATCH |
| PREVIEWS_DIR 디렉토리 생성 | 암시적 | `PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)` (L271) | MATCH |

**Checklist (4/4)**:
- [x] `PREVIEWS_DIR` 상수 정의 (`static/previews/`)
- [x] `mkdir(parents=True, exist_ok=True)` 호출
- [x] `shutil.copy2()` 로 temp -> static 복사
- [x] preview_url이 `/static/previews/{id}.pdf` 형식 반환

**Result**: PASS (4/4)

---

### Gap 2: include_cover 파라미터 전달 (HIGH)

| Item | Plan | Implementation | Status |
|------|------|----------------|--------|
| Target file | `publishing_service.py` - `start_export()` | `publishing_service.py:30-121` | MATCH |
| Fix: cover_image_path 결정 | `include_cover + cover_url` 기반 | `_resolve_cover_path()` (L509-519) 호출 (L78-82) | MATCH |
| DOCX: `doc.add_picture()` | 표지 이미지 삽입 | `doc.add_picture(cover_image_path, width=Inches(5.0))` (L157) + page break | MATCH |
| PDF: Typst `#image()` | 표지 삽입 | `#image("{escaped_path}", width: 100%)` (L257) + pagebreak | MATCH |
| EPUB: 표지 xhtml 추가 | 표지 페이지 추가 | `epub.EpubItem` (L356-361) + `book.set_cover()` (L363) | MATCH |
| 3개 함수 시그니처 | `cover_image_path` 파라미터 | DOCX(L129), PDF(L218), EPUB(L326) 모두 수신 | MATCH |

**Checklist (6/6)**:
- [x] `start_export()`에서 `cover_image_path` 결정 로직
- [x] `_resolve_cover_path()` 유틸리티 메서드 구현
- [x] `_export_docx()`에 `cover_image_path` 전달 + 삽입
- [x] `_export_pdf()`에 `cover_image_path` 전달 + Typst `#image()` 삽입
- [x] `_export_epub()`에 `cover_image_path` 전달 + EpubItem 삽입
- [x] `os.path.exists()` 가드 조건 (DOCX:L156, PDF:L253, EPUB:L353)

**Result**: PASS (6/6)

---

### Gap 3: ExportResponse.file_size_bytes 타입 (MEDIUM)

| Item | Plan | Implementation | Status |
|------|------|----------------|--------|
| Target file | `publishing.py` | `publishing.py:57` | MATCH |
| Before | `StrictStr \| None` | -- | -- |
| After | `StrictInt \| None = None` | `file_size_bytes: StrictInt \| None = None` | MATCH |

**Checklist (2/2)**:
- [x] 타입이 `StrictInt`로 변경됨
- [x] 기본값 `None` 유지

**Result**: PASS (2/2)

---

### Gap 4: docstring DALL-E -> Gemini (LOW)

| Item | Plan | Implementation | Status |
|------|------|----------------|--------|
| Target file | `backend/app/api/v1/design.py` - `generate_cover()` | `design.py:92` | MATCH |
| Before | "DALL-E를 사용하여" | -- | -- |
| After | "Google Gemini를 사용하여" | `"Google Gemini를 사용하여 도서 표지 이미지를 생성합니다."` | MATCH |

**Checklist (1/1)**:
- [x] `design.py` generate_cover docstring 변경 완료

**Result**: PASS (1/1)

**Warning**: 범위 외 잔존 DALL-E 참조 2건 (Plan 미지정, non-blocking)
- `backend/app/agents/design_agent.py:21` - "DALL-E를 사용한 표지 생성"
- `backend/app/schemas/design.py:44` - "DALL-E에 전달한 프롬프트"

---

### Gap 5: 템플릿 preview_url 빈 문자열 (MEDIUM)

| Item | Plan | Implementation | Status |
|------|------|----------------|--------|
| Target file | `backend/app/api/v1/design.py` - `DEFAULT_TEMPLATES` | `design.py:29-78` | MATCH |
| Before | `/static/templates/*.png` (6개) | -- | -- |
| After | 빈 문자열 `""` | 6개 모두 `preview_url=""` | MATCH |

**Checklist (2/2)**:
- [x] 6개 템플릿 모두 `preview_url=""` 설정
- [x] 프론트엔드에서 placeholder 표시 위임 (Plan 명시)

**Result**: PASS (2/2)

---

### Gap 6: Gemini 429 RESOURCE_EXHAUSTED 에러 핸들링 (MEDIUM)

| Item | Plan | Implementation | Status |
|------|------|----------------|--------|
| Service layer | `design_service.py` - `generate_cover()` | L168-175 | MATCH |
| 429/RESOURCE_EXHAUSTED 감지 | 문자열 매칭 | `"429" in err_msg or "resource_exhausted" in err_msg` | MATCH |
| 사용자 친화적 메시지 | RuntimeError + 메시지 | `RuntimeError("AI 이미지 생성 API 사용량 한도에 도달했습니다...")` | MATCH |
| API layer 전달 | HTTPException 상세화 | `HTTP_429_TOO_MANY_REQUESTS` + detail 메시지 (design.py:115-118) | MATCH |

**Checklist (4/4)**:
- [x] Service: `except Exception` 블록에서 429/RESOURCE_EXHAUSTED 문자열 감지
- [x] Service: `RuntimeError`로 사용자 친화적 메시지 래핑
- [x] API: `RuntimeError` 캐치 후 "사용량 한도" 키워드 확인
- [x] API: `HTTP_429_TOO_MANY_REQUESTS` 상태 코드 반환

**Result**: PASS (4/4)

---

## 3. Build & Test Verification

| Criterion | Plan | Status | Notes |
|-----------|------|--------|-------|
| tsc 0 errors | Required | PASS | Do 단계에서 확인됨 |
| pytest 전체 통과 (signup 제외) | Required | PASS | 169/170 (signup 1건 기존 실패) |
| vitest 전체 통과 | Required | PASS | 96/96 통과 |
| Next.js build 성공 | Required | PASS | Do 단계에서 확인됨 |

**Result**: PASS (4/4)

---

## 4. Architecture & Convention Compliance

### 4.1 Architecture Compliance

| Item | Status | Notes |
|------|--------|-------|
| Service layer 분리 | PASS | design_service.py, publishing_service.py 독립 |
| API -> Service 단방향 의존 | PASS | design.py -> DesignService, publishing.py -> PublishingService |
| Schema 독립성 | PASS | schemas/publishing.py, schemas/design.py 외부 무의존 |
| Static 파일 경로 관리 | PASS | COVERS_DIR, PREVIEWS_DIR 상수로 관리 |

**Architecture Score**: 100%

### 4.2 Convention Compliance

| Item | Status | Notes |
|------|--------|-------|
| 함수 네이밍 (snake_case) | PASS | `_compile_typst`, `_resolve_cover_path`, `_export_docx` 등 |
| 상수 네이밍 (UPPER_SNAKE) | PASS | `COVERS_DIR`, `PREVIEWS_DIR`, `STYLE_KEYWORDS` 등 |
| Pydantic Strict 타입 사용 | PASS | `StrictInt`, `StrictStr`, `StrictBool`, `StrictFloat` |
| 타입 힌트 완전성 | PASS | 모든 함수에 반환 타입, 파라미터 타입 명시 |
| docstring 존재 | PASS | 모든 public 메서드에 docstring 포함 |
| import 순서 | PASS | stdlib -> third-party -> local 순서 |

**Convention Score**: 100%

---

## 5. Overall Score

### 5.1 Match Rate Summary

| Gap | Items | Passed | Rate |
|-----|:-----:|:------:|:----:|
| Gap 1: LayoutPreview /tmp 경로 | 4 | 4 | 100% |
| Gap 2: include_cover 전달 | 6 | 6 | 100% |
| Gap 3: file_size_bytes 타입 | 2 | 2 | 100% |
| Gap 4: docstring DALL-E->Gemini | 1 | 1 | 100% |
| Gap 5: 템플릿 preview_url | 2 | 2 | 100% |
| Gap 6: Gemini 429 핸들링 | 4 | 4 | 100% |
| Build & Test | 4 | 4 | 100% |
| **Total** | **23** | **23** | **100%** |

### 5.2 Overall Scores

| Category | Score | Status |
|----------|:-----:|:------:|
| Design Match | 100% | PASS |
| Architecture Compliance | 100% | PASS |
| Convention Compliance | 100% | PASS |
| **Overall** | **100%** | **PASS** |

---

## 6. Warnings (non-blocking)

### DALL-E 잔존 참조 (Plan 범위 외)

| File | Line | Content | Impact |
|------|------|---------|--------|
| `backend/app/agents/design_agent.py` | 21 | "DALL-E를 사용한 표지 생성" | LOW - docstring만 |
| `backend/app/schemas/design.py` | 44 | "DALL-E에 전달한 프롬프트" | LOW - 필드 주석만 |

이 2건은 Plan에서 명시적으로 `backend/app/api/v1/design.py` docstring만 수정 대상으로 지정했으므로 Gap으로 카운트하지 않는다. 후속 Sprint에서 일괄 정리 권장.

---

## 7. Recommended Actions

### Immediate Actions
- 없음 (모든 Gap 항목 100% 일치)

### Optional Follow-ups (별도 Sprint)
1. `design_agent.py`, `schemas/design.py`의 DALL-E 참조를 Gemini로 업데이트
2. Gap 7 (CoverDesigner 템플릿 적용 로직) - FE 대규모 변경 필요
3. Playwright E2E 테스트 작성
4. 표지 템플릿 실제 이미지 생성 (Gemini quota 복구 후)

---

## 8. Next Steps

- [x] Plan 문서 작성
- [x] Do 구현 완료
- [x] Check 분석 완료 (100%)
- [ ] Report 완료 보고서 작성 (`/pdca report sprint8-code-gaps`)

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-03-06 | Initial gap analysis | gap-detector |
