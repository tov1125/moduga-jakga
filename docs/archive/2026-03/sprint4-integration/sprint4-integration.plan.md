# Sprint 4 Plan: 서비스 실연동 + Voice-First 완성

## 목표
Sprint 3에서 FE↔BE JWT 통합과 PDCA 5사이클 완주(평균 95.56%)를 달성.
Sprint 4에서는 남은 갭을 메워 "말하다 → 글이 되다 → 책이 되다" E2E 파이프라인 완성.

## 범위

### P0: 크리티컬 갭 수정
- P0-1: STT WebSocket 엔드포인트 (`backend/app/api/v1/stt.py`)
- P0-2: CoverDesigner genre/style/author 파라미터 매핑 (`frontend/src/components/book/CoverDesigner.tsx`)
- P0-3: TTS 속도 파라미터 FE→BE 변환 (`frontend/src/lib/api.ts`)

### P1: 페이지 통합
- P1-1: Write 페이지 음성+SSE 통합 (`frontend/src/app/write/[bookId]/page.tsx`)
- P1-2: Design 페이지 page_size, line_spacing, fontFamily 확장 (`frontend/src/app/design/[bookId]/page.tsx`)
- P1-3: ExportPanel include_cover/include_toc 옵션 + 파일명 개선 (`frontend/src/components/book/ExportPanel.tsx`)

### P2: E2E 검증
- Backend 테스트 전체 통과 (auth 제외 pre-existing)
- Frontend 테스트 전체 통과

## 대상 파일 (6개)
| 파일 | 변경 내용 |
|------|---------|
| `backend/app/api/v1/stt.py` | WebSocket `/stream` 엔드포인트 |
| `frontend/src/components/book/CoverDesigner.tsx` | genre/style UI, authorName/bookGenre props |
| `frontend/src/lib/api.ts` | TTS speed 매핑 (FE 0.5~2.0 → BE -5~5) |
| `frontend/src/app/design/[bookId]/page.tsx` | pageSize, lineSpacing UI, layoutPreview 파라미터 |
| `frontend/src/components/book/ExportPanel.tsx` | includeCover/includeToc 체크박스, bookTitle 파일명 |
| `frontend/src/app/publish/[bookId]/page.tsx` | bookTitle prop 전달 |
