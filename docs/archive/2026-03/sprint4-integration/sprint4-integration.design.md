# Sprint 4 Design: 서비스 실연동 + Voice-First 완성

## 1. CoverDesigner 파라미터 수정

### 1.1 상수 정의
- `GENRE_OPTIONS`: 7개 (essay, novel, poem, autobiography, children, non_fiction, other) — BE `Genre` enum과 일치
- `STYLE_OPTIONS`: 5개 (minimalist, illustrated, photographic, typography, abstract) — BE `CoverStyle` enum과 일치

### 1.2 Props 확장
- `bookId: string` 제거 (사용하지 않음)
- `authorName?: string` 추가
- `bookGenre?: string` 추가

### 1.3 State 추가
- `genre` state: `bookGenre || "essay"` 초기값
- `style` state: `"minimalist"` 초기값

### 1.4 API 호출 수정
- `design.generateCover()` 호출 시:
  - `genre`: state 값 (string)
  - `style`: state 값 (string)
  - `author_name`: `authorName || "작가"`
  - `book_title`: `bookTitle`

### 1.5 UI 요소
- genre `<select>` dropdown (id="cover-genre")
- style `<select>` dropdown (id="cover-style")
- 접근성: label + focus-visible ring
- 위치: 표지 미리보기와 생성 버튼 사이

### 1.6 useCallback 의존성
- `handleGenerateCover`: `[bookTitle, authorName, genre, style, announcePolite, announceAssertive]`

## 2. TTS 속도 매핑

### 2.1 변환 공식
- FE range: 0.5 ~ 2.0 (1.0 = normal)
- BE range: -5 ~ 5 (0 = normal)
- 공식: `beSpeed = Math.max(-5, Math.min(5, (feSpeed - 1.0) * 5.0))`

### 2.2 적용 위치
- `frontend/src/lib/api.ts` > `tts.synthesize()` 메서드 내부
- 기존: `speed: speed ?? 0.0`
- 변경: `const feSpeed = speed ?? 1.0; const beSpeed = clamp((feSpeed - 1.0) * 5.0, -5, 5);`

## 3. Design 페이지 확장

### 3.1 State 추가
- `pageSize`: string, 초기값 `"B5"`
- `lineSpacing`: number, 초기값 `1.6`

### 3.2 UI 요소
- 판형 `<select>` (id="page-size"): A5, B5, A4, paperback
- 줄 간격 `<input type="range">` (id="line-spacing"): 1.0~2.5, step 0.1
- 접근성: aria-valuenow, aria-valuemin, aria-valuemax, aria-label

### 3.3 API 호출 확장
- `designApi.layoutPreview()`:
  - `page_size`: pageSize state
  - `font_size`: fontSize state
  - `line_spacing`: lineSpacing state

### 3.4 CoverDesigner props 전달
- `authorName={book?.author_name}`
- `bookGenre={book?.genre}`

### 3.5 useCallback 의존성
- `handlePreviewLayout`: `[bookId, pageSize, fontSize, lineSpacing, announcePolite, announceAssertive]`

## 4. ExportPanel 옵션 확장

### 4.1 Props 확장
- `bookTitle?: string` 추가

### 4.2 State 추가
- `includeCover`: boolean, 초기값 `true`
- `includeToc`: boolean, 초기값 `true`

### 4.3 UI 요소
- "포함 항목" 섹션 (포맷 선택과 내보내기 버튼 사이)
- 표지 포함 `<input type="checkbox">`
- 목차 포함 `<input type="checkbox">`
- 접근성: label wrapping, min-h-touch

### 4.4 API 호출 확장
- `publishing.exportBook()`:
  - `include_cover`: includeCover state
  - `include_toc`: includeToc state

### 4.5 다운로드 파일명
- 기존: `export.${format}`
- 변경: `${bookTitle}.${format}` (bookTitle 있을 때) / `export.${format}` (없을 때)

### 4.6 useCallback 의존성
- `handleExport`: `[bookId, selectedFormat, includeCover, includeToc, announcePolite, announceAssertive]`

## 5. Publish 페이지 수정
- `ExportPanel`에 `bookTitle={book?.title}` prop 전달

## 6. 테스트 수정

### 6.1 QualityReport 테스트 mock
- 기존 mock (overallScore, grammarScore 등)을 실제 `QualityReport` 타입에 맞게 수정
- `book_id`, `overall_score`, `stage_results[]`, `total_issues`, `summary`, `recommendations[]`, `created_at`
- 테스트 assertion: "문제 목록" → "권장 사항 목록", "심각도 배지" → "권장 배지"

## 7. STT WebSocket (확인 사항)
- `backend/app/api/v1/stt.py`에 `@router.websocket("/stream")` 이미 구현됨
- 3단계 프로토콜: auth token → config → audio streaming
- 추가 작업 불필요

## 8. Write 페이지 통합 (확인 사항)
- VoiceRecorder → handleTranscript → content 이미 연결됨
- WritingApi.generate SSE → StreamingText → content 이미 연결됨
- VoicePlayer TTS 이미 연결됨
- 추가 작업 불필요
