# 모두가 작가 — 프로젝트 변경 로그

모두가 작가 프로젝트의 모든 릴리스 및 주요 변경 사항을 기록합니다.

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
