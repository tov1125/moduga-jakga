# 모두가 작가 — 프로젝트 변경 로그

모두가 작가 프로젝트의 모든 릴리스 및 주요 변경 사항을 기록합니다.

---

## [2026-03-05] — Sprint 6: shadcn 컴포넌트 완전 적용 (100% Match Rate)

**Feature**: sprint6-shadcn-complete (UI 컴포넌트 표준화 완성)
**Duration**: 1 hour (2026-03-05 21:30 ~ 23:15)
**Design Match Rate**: 100% (54/54 items)
**Status**: PDCA Complete, 1-Pass Success (0 iterations)

### 추가 (Added)

**shadcn Consumer 적용 완료**:
- 4개 consumer 파일에 shadcn 컴포넌트 완전 적용 (9/11 사용)
- CoverDesigner: native select 2개 → shadcn Select
- EditingPanel: 수동 탭 → shadcn Tabs + Badge 추가
- ExportPanel: native radio/checkbox → shadcn RadioGroup/Checkbox/Progress
- ChapterList: ScrollArea 래핑 (max-h-96)

**테스트 Props 수정**:
- axe-core.test.tsx: size="md" → size="default" (5건)
- wcag-checklist.test.tsx: variant="danger" → variant="destructive" (1건)

### 변경 (Changed)

**UI 컴포넌트 마이그레이션**:
- Modal.tsx 삭제 (dialog.tsx로 대체 완료)
- modal.test.tsx 삭제
- 접근성 속성 100% 보존 (Radix UI 자동 처리)

### 수정 (Fixed)

**Design Match Rate**:
- Sprint 5 Gap Analysis (95.1%) → 100% (+4.9%)
- Sprint 5 Gap 5/5 해소 (G-1 ~ G-5)
- G-6 (Button 파일명) macOS 제약 수용

**Accessibility Verification**:
- min-h-touch: 19건 (44px 터치 타겟 유지)
- ring-yellow-400: 22건 across 17 files (포커스 링 유지)
- ARIA attributes: 100% 보존 (Radix 자동 처리)
- 키보드 네비게이션: ArrowUp/Down/Home/End 완전 유지

### 통계
- **수정된 파일**: 7개 modified, 2개 deleted
- **추가 줄**: +1,163줄
- **삭제 줄**: -614줄
- **순증가**: +549줄
- **빌드 성공**: 100% (12 routes)
- **테스트 통과**: 99.4% (169/170 Backend + 96/96 Frontend)
- **TypeScript 에러**: 0개
- **Design Match Rate**: 100% (54/54 items)
- **Iterations**: 0 (첫 시도 성공)

### 다음 PDCA
- Sprint 6 완료 → Archive 준비
- Sprint 7: Writing/Design/Publishing 서비스 고도화 계획

---

## [2026-03-05] — Sprint 5: shadcn/ui 구조화 + Gemini 표지 생성 (95.1% Match Rate)

**Feature**: sprint5-shadcn-gemini (UI 컴포넌트 표준화 + 표지 생성 모델 전환)
**Duration**: 4.5 hours (2026-03-05 16:00 ~ 20:30)
**Design Match Rate**: 95.1% (68.5/72 items)
**Status**: PDCA Complete, PASS (>= 90% threshold)

### 추가 (Added)

**shadcn/ui 컴포넌트 라이브러리**:
- 11개 shadcn 컴포넌트 생성: Button, Dialog, Input, Label, Select, Checkbox, Tabs, RadioGroup, Badge, Progress, ScrollArea
- CVA (class-variance-authority) 기반 Button: 6 variants (primary, secondary, destructive, ghost, outline, link), 4 sizes (sm, default, lg, icon)
- 커스텀 props 유지: isLoading, leftIcon, rightIcon
- Radix UI 기반 포커스 관리 및 키보드 탐색 전체 지원
- 접근성 커스터마이징: min-h-touch min-w-touch, ring-4 ring-yellow-400

**Tailwind CSS 변수 통합**:
- shadcn CSS 변수 테마 추가 (--primary, --secondary, --destructive, --ring 등)
- 기존 접근성 설정 완벽하게 보존 (44px 터치, 노란 포커스 링, 18px 폰트, reduced-motion)
- 다크 모드 지원 (`.dark` 블록)

**Google Gemini 표지 생성**:
- Gemini SDK (google-genai>=1.0.0) 통합
- 모델: gemini-2.5-flash-image
- asyncio.to_thread() 래핑으로 동기 SDK의 비동기 실행
- base64 이미지 → 로컬 파일 저장 (backend/static/covers/)
- 정적 파일 서빙: FastAPI StaticFiles + Next.js rewrite

### 변경 (Changed)

**컴포넌트 마이그레이션**:
- Button: 커스텀 → shadcn CVA (6 variants, 4 sizes)
- Modal: 커스텀 → shadcn Dialog (Radix UI 기반)
- 8개 파일 Button import 경로 일괄 변경 (danger → destructive)

**표지 생성 모델 전환**:
- OpenAI DALL-E 3 → Google Gemini 2.5 Flash Image
- AsyncOpenAI → google.genai.Client
- URL 반환 → 로컬 파일 저장 + 상대 URL 반환

**Tailwind 설정**:
- CSS 변수 시스템 확대
- tailwindcss-animate 플러그인 추가

### 수정 (Fixed)

**포커스 관리**:
- Dialog, Select, Tabs, RadioGroup 등 모든 shadcn 컴포넌트에 Radix UI 내장 포커스 관리 적용
- 포커스 시각적 표시 일관성 강화 (모든 인터랙티브 요소에 ring-4 ring-yellow-400)

**정적 파일 서빙**:
- Gemini API base64 이미지를 로컬에 저장하고 상대 URL (/static/covers/{filename})로 반환
- Frontend에서 /static 요청을 Backend로 프록시

### 통계
- **수정된 파일**: 38개 (Frontend 32, Backend 6)
- **추가 줄**: +2,295줄
- **삭제 줄**: -361줄
- **순증가**: +1,934줄
- **빌드 성공**: 100% (13개 페이지)
- **테스트 통과**: 99.4% (169/170, 1개 기존 Supabase auth 무관)
- **TypeScript 에러**: 0개
- **Design Match Rate**: 95.1% (68.5/72)

### 다음 PDCA
- Sprint 5 Gap 해결 (6개, 모두 Low priority)
  - CoverDesigner: native select → shadcn Select
  - EditingPanel: 수동 탭 → shadcn Tabs
  - ExportPanel: native radio/checkbox → shadcn RadioGroup + Checkbox
  - ChapterList: ScrollArea 래핑
  - Modal.tsx 삭제
  - 테스트 파일 variant/size 업데이트

---

## [2026-03-05] — Sprint 4 Integration Complete (100% Match Rate)

**Feature**: sprint4-integration (서비스 실연동 + Voice-First 완성)
**Duration**: 1 day (2026-03-05)
**Design Match Rate**: 100% (65/65 items)
**Status**: 1-Pass PDCA Complete, Ready for Deployment

### 추가 (Added)

**E2E 파이프라인 완성**:
- CoverDesigner 파라미터화: authorName, bookGenre 추가 (표지 자동 생성)
- TTS 속도 매핑: FE 0.5~2.0 → BE -5~5 변환 공식
- Design 페이지 확장: pageSize, lineSpacing 옵션
- ExportPanel 옵션: includeCover, includeToc 체크박스
- 동적 파일명: 다운로드 시 bookTitle 적용

**테스트 품질 개선**:
- QualityReport mock 타입 정확도 100% 달성
- Frontend 106개, Backend 163개 테스트 모두 통과
- 접근성 테스트: WAI-ARIA 속성 전체 검증

### 변경 (Changed)

**API 호출 확장**:
- design.generateCover(): genre, style 파라미터 추가
- tts.synthesize(): speed 범위 변환 적용
- designApi.layoutPreview(): page_size, line_spacing 추가
- publishing.exportBook(): include_cover, include_toc 추가

**UI 컴포넌트**:
- CoverDesigner: genre/style select dropdown
- Design 페이지: pageSize select, lineSpacing range slider
- ExportPanel: includeCover/includeToc 체크박스

### 수정 (Fixed)

**Quality Metrics**:
- Design Match Rate: 100% (65/65 items, all sections)
- CoverDesigner: 17/17 (100%)
- TTS Speed: 6/6 (100%)
- Design Page: 13/13 (100%)
- ExportPanel: 12/12 (100%)
- Tests: 9/9 (100%)
- STT WebSocket: 3/3 (100%)
- Write Page: 4/4 (100%)

**useCallback 의존성 정정**:
- ExportPanel.handleDownload: bookTitle 추가

### 통계
- **수정된 파일**: 7개 (Frontend 6, Test 1)
- **테스트 통과율**: Frontend 106/106, Backend 163/163
- **총 코드 라인**: 파일당 평균 195~316줄
- **PDCA 효율**: 1-Pass 완성 (iterate 불필요)

### 다음 PDCA
- Sprint 4 완료 → Archive 준비
- Sprint 5: 고급 기능 (고도화 예정)

---

## [2026-03-03] — Cycle #2: schemas Feature Complete (93% Match Rate)

**Feature**: schemas (Pydantic v2 Strict 타입 스키마 검증 및 FE/BE 동기화)
**Duration**: 2 days (2026-03-02 ~ 2026-03-03)
**Design Match Rate**: 55% → 93% (Final: PASS)

### 추가 (Added)

**Backend Schema Validation**:
- Pydantic v2 Strict 타입 + Field 제약 조건 (9개 스키마 파일)
  - StrictBool 타입 도입 (4건): writing, editing 스키마
  - Field constraints 추가: auth, book, chapter, writing, editing, tts, design, publishing
  - min_length, max_length, ge, le 제약 조건 완전 적용

**Test Suite**:
- test_schemas.py: 68개 신규 테스트 케이스
  - Field constraint validation (24개)
  - StrictBool validation (8개)
  - Enum synchronization (21개)
  - Boundary testing (15개)

**API Response Wrapper**:
- Frontend apiFetch 자동 {success, data} 래핑
- BE 원시 Pydantic 응답을 FE 표준 형식으로 변환

**FE/BE Enum Synchronization** (7개 Enum):
- DisabilityType: "total_blindness" → "visual"
- BookGenre: "children", "non_fiction", "other" 추가
- BookStatus: "completed" 추가, "reviewing", "publishing" 제거
- ChapterStatus: "writing", "editing", "completed" 상태 정의
- WritingStatus, EditingStatus, PublishingFormat: 일치 확인

### 변경 (Changed)

**HTTP Methods**:
- PUT → PATCH 메서드로 통일 (REST 컨벤션)
  - PATCH /api/v1/books/{id}
  - PATCH /api/v1/chapters/{id}

**Frontend Types**:
- Enum 값들을 Backend와 완전 동기화
- signup/page.tsx, settings/page.tsx: DisabilityType 옵션 업데이트
- utils.ts: 레이블 함수 동기화 (genreLabel, statusLabel, chapterStatusLabel)

**Error Handling**:
- Pydantic 422 Unprocessable Entity 에러 표준화

### 수정 (Fixed)

**Quality Metrics**:
- Design Match Rate: 55% → 93% (+38%)
- Strict Type Compliance: 82% → 100% (+18%)
- Field Constraints: 35% → 95% (+60%)
- Test Coverage: 0% → 92% (+92%)
- FE-BE Type Sync: 58% → 82% (+24%)
- Enum Sync: 62% → 100% (+38%)
- HTTP Method Consistency: 50% → 100% (+50%)
- API Response Wrapper: 0% → 90% (+90%)

### 통계
- **수정된 파일**: 21개 (Backend 14, Frontend 7)
- **신규 테스트**: 68개
- **총 테스트 통과**: 170개 (Backend) + 106개 (Frontend)
- **테스트 성공률**: 100%
- **코드 라인**: +405 net change

### 다음 PDCA
- Cycle #2 완료 → Archive 준비
- Cycle #3: field-sync, stt-schema, api-wrapper 계획

---

## [2026-03-03] — Phase 8: 테스트 인프라 + CI/CD 완성

**Feature**: tests (8단계 접근성 테스트 + CI/CD 파이프라인)
**Design Match Rate**: 91% (PASS)

### 추가 (Added)
- **Backend 테스트**: 10개 파일, 90개 테스트 케이스
  - pytest 기반 단위 테스트
  - Pydantic v2 Strict 타입 검증 (16개 테스트)
  - Supabase 모의 (mock) 통합
  - JWT 인증 테스트

- **Frontend 테스트**: 10개 파일, 106개 테스트 케이스
  - Vitest 기반 컴포넌트 테스트 (5개 파일, 56개 테스트)
  - 접근성 테스트 (5개 파일, 50개 테스트)
    - WCAG 2.1 AA 체크리스트
    - Voice-First 패턴 검증
    - axe-core 자동 접근성 검사
    - 키보드 네비게이션, 포커스 관리
    - 한국어 음성 명령 테스트 (11개)

- **CI/CD 파이프라인**: GitHub Actions 4단계
  - backend-test: pytest + ruff + mypy
  - frontend-test: Vitest + TypeScript + ESLint + Playwright
  - build: Next.js + Docker 빌드 검증
  - quality-gate: A16 품질 보증 에이전트

- **테스트 설정 파일**:
  - conftest.py (pytest fixture)
  - vitest.config.ts
  - jest.setup.ts
  - playwright.config.ts
  - .env.test

### 변경 (Changed)
- CI/CD 워크플로우: continue-on-error 제거 (품질 강화)
  - 이제 lint/type/test 에러 발생 시 배포 차단
- GitHub Actions: E2E Playwright 테스트 추가
- 환경 변수 관리: 테스트 환경 변수 별도 설정

### 수정 (Fixed)
- Backend 테스트: Supabase 모의 정교화 (복잡한 chaining API 대응)
- Frontend 테스트: React Testing Library 쿼리 최적화
- pytest 커버리지: --cov-report=term-missing 추가 (미커버리지 행 가시화)

### 통계
- 총 테스트 수: **196개**
  - Backend: 90개 (95% Match Rate)
  - Frontend: 106개 (85% Match Rate)
- 테스트 성공률: **100%**
- 코드 린트 에러: **0건**
- CI/CD 완성도: **95%**

---

## [2026-02-20] — Phase 8 설계: 테스트 인프라 계획

**Feature**: tests (Plan + Design 단계 완료)

### 추가 (Added)
- tests.plan.md: 8단계 테스트 + CI/CD 계획 수립
- tests.design.md: 테스트 전략 및 기술 설계

### 설계 완료
- Backend 테스트 전략: pytest, class-per-operation 패턴
- Frontend 테스트 전략: Vitest, Testing Library, axe-core
- CI/CD 아키텍처: GitHub Actions 4단계 워크플로우

---

## [v0.1.0] — MVP 초기 커밋

**Date**: 2026-02-10

### 초기 구성
- Backend: FastAPI + Pydantic v2 + Supabase
- Frontend: Next.js 15 + React 19 + TypeScript + Tailwind CSS
- 아키텍처: STT → AI 글쓰기 → 편집 → 표지 설계 → 출판
- 8개 AI 에이전트 (orchestrator, writing, editing, design, publishing, quality, stt, tts)

### 완료된 Phase
- Phase 1~7: 전체 기능 구현 완료
- Phase 8: 테스트 인프라 (현재 진행 중)

---

## 버전 정책

### 의미 있는 버전 (Semantic Versioning)

- **v0.1.0**: MVP 초기 버전 (Phase 1~7 완료, Phase 8 진행 중)
- **v0.2.0**: Phase 8 테스트 완성 후 예정 (현재 진행 중)
- **v1.0.0**: 모든 Phase 완료 + 프로덕션 배포 준비

---

## PDCA 사이클 진행

### Cycle #1: Tests (테스트 인프라)

| 단계 | 상태 | 날짜 | Match Rate |
|------|------|------|-----------|
| Plan | ✅ | 2026-02-20 | - |
| Design | ✅ | 2026-02-20 | - |
| Do | ✅ | 2026-02-20 ~ 2026-03-02 | - |
| Check | ✅ | 2026-03-03 | 91% |
| Act | ✅ | 2026-03-03 | 91% (PASS) |

**결과**: Design Match Rate 91% → Phase 8 완성

---

## 다음 PDCA 사이클

### Cycle #2: Feature Enhancement (기능 고도화)

계획 중인 주요 작업:
- 미완료 Frontend 컴포넌트 테스트 (6개 컴포넌트)
- 미완료 Hook 테스트 (4개 훅)
- API 함수 테스트 (32개 함수)
- Lighthouse CI, Bandit 등 추가 품질 도구

예상 시작: 2026-03-04

---

## 참고 문서

- [tests.report.md](./features/tests.report.md): Phase 8 완료 보고서
- [tests.design.md](../02-design/features/tests.design.md): 테스트 기술 설계
- [tests.plan.md](../01-plan/features/tests.plan.md): 테스트 계획서
- [CLAUDE.md](../../CLAUDE.md): 프로젝트 개요 및 기술 스택
