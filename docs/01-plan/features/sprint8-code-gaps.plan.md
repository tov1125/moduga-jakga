# Sprint 8 Plan — 코드 Gap 수정

## 개요
Sprint 8 E2E 검증에서 발견된 코드 레벨 Gap 6건을 수정한다.

## 목표
- 출판/디자인 서비스의 실동작 버그 해소
- 타입 안전성 복구
- Gemini 에러 핸들링 강화

## 수정 항목

### Gap 1: LayoutPreview /tmp 경로 반환 (CRITICAL)
- **파일**: `backend/app/services/design_service.py` — `_compile_typst()`
- **문제**: `TemporaryDirectory` with 블록 종료 시 파일 삭제됨 → 반환된 경로 접근 불가
- **수정**: PDF를 `static/previews/` 에 저장하고 URL 반환
- **검증**: preview_url이 `/static/previews/xxx.pdf` 형식

### Gap 2: include_cover 파라미터 무시 (HIGH)
- **파일**: `backend/app/services/publishing_service.py` — `start_export()`
- **문제**: `include_cover=True`를 `_export_docx`, `_export_epub`에 전달하지 않음
- **수정**: 각 export 함수에 include_cover 전달, cover_url이 있으면 이미지 삽입
  - DOCX: `doc.add_picture()` 로 표지 이미지 삽입
  - EPUB: 표지 xhtml 페이지 추가
  - PDF: Typst `#image()` 매크로로 표지 삽입

### Gap 3: ExportResponse.file_size_bytes 타입 오류 (MEDIUM)
- **파일**: `backend/app/schemas/publishing.py`
- **문제**: `file_size_bytes: StrictStr | None` → 정수여야 함
- **수정**: `file_size_bytes: StrictInt | None = None`

### Gap 4: design.py docstring "DALL-E" → Gemini (LOW)
- **파일**: `backend/app/api/v1/design.py` — `generate_cover()` docstring
- **문제**: "DALL-E를 사용하여" → "Google Gemini를 사용하여"
- **수정**: docstring 1줄 변경

### Gap 5: 템플릿 preview_url 파일 미존재 (MEDIUM)
- **파일**: `backend/app/api/v1/design.py` — `DEFAULT_TEMPLATES`
- **문제**: `/static/templates/*.png` 6개 파일 없음
- **수정**: preview_url을 빈 문자열로 변경하고 프론트엔드에서 placeholder 표시
  - 실제 이미지는 Gemini quota 복구 후 생성

### Gap 6: Gemini 429 에러 핸들링 (MEDIUM)
- **파일**: `backend/app/services/design_service.py` — `generate_cover()`
- **문제**: 429 RESOURCE_EXHAUSTED 시 일반 Exception으로 처리
- **수정**: `google.genai.errors.ClientError` 캐치하여 사용자 친화적 메시지 반환
- **스키마**: CoverGenerateResponse에 error 필드 추가하거나 HTTPException 상세화

## 수정 제외 (별도 Sprint)
- Gap 7: CoverDesigner 템플릿 적용 로직 — FE 대규모 변경 필요
- Playwright E2E 테스트 작성 — 환경 구성 필요

## 검증 기준
- [ ] tsc 0 errors
- [ ] pytest 전체 통과 (signup 제외)
- [ ] vitest 전체 통과
- [ ] Next.js build 성공

## 영향 범위
- `backend/app/services/design_service.py` (Gap 1, 6)
- `backend/app/services/publishing_service.py` (Gap 2)
- `backend/app/schemas/publishing.py` (Gap 3)
- `backend/app/api/v1/design.py` (Gap 4, 5)
