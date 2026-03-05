# Sprint 10: 배포 + 커버리지 + E2E Planning Document

> **Summary**: Vercel 실제 배포, 테스트 커버리지 임계값 달성, Playwright E2E 사용자 흐름 테스트
>
> **Project**: 모두가 작가
> **Author**: A0 Orchestrator
> **Date**: 2026-03-06
> **Status**: Draft
> **PDCA Cycle**: #12

---

## 1. Overview

### 1.1 Purpose

Sprint 9까지 11회 PDCA 사이클(평균 97.53%)을 완료했다. 현재 배포 설정은 완료되었으나 실제 배포가 미실행 상태이며, 테스트 커버리지가 임계값(FE 80%, BE 80%)에 미달하고, E2E 테스트는 접근성 1파일만 존재한다. Sprint 10에서 이 3가지 핵심 품질 지표를 해결한다.

### 1.2 Background

- **Vercel**: `vercel.json` + `Dockerfile` + `next.config.ts(standalone)` 설정 완료, 실제 배포 미실행
- **커버리지**: FE 12.5% (threshold 80%), BE 41% (threshold 미설정)
- **E2E**: `accessibility.spec.ts` 1파일 (접근성만), 사용자 흐름 테스트 0건

### 1.3 Related Documents

- Sprint 9 Report: `docs/archive/2026-03/sprint9-p1-p3/sprint9-p1-p3.report.md`
- Sprint 8 Report: `docs/archive/2026-03/sprint8-code-gaps/sprint8-code-gaps.report.md`
- VoiceOver Checklist: `docs/03-analysis/voiceover-checklist.md`

---

## 2. Scope

### 2.1 In Scope

- [ ] Vercel 실제 배포 (vercel.json URL 교체 + `vercel deploy`)
- [ ] Frontend 테스트 커버리지 향상 (12.5% → 50%+ 목표)
- [ ] Backend 테스트 커버리지 향상 (41% → 60%+ 목표)
- [ ] Playwright E2E 사용자 흐름 테스트 3~5건 추가
- [ ] GitHub Actions CI 워크플로우 추가

### 2.2 Out of Scope

- 기술 부채 (DALL-E docstring, CoverDesigner 템플릿 이미지) — Sprint 11
- A0 종합보고서 v4.0.0 — Sprint 10 완료 후
- VoiceOver 수동 테스트 실행 — 배포 완료 후 별도 진행
- 커버리지 80% 전체 달성 — 점진적 향상 전략 (Sprint 10은 기반 구축)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-01 | vercel.json API URL을 실제 Backend 배포 URL로 교체 | High | Pending |
| FR-02 | `vercel deploy --prod` 실행 및 접속 확인 | High | Pending |
| FR-03 | FE 핵심 Hook 단위 테스트 추가 (useSTT, useEditHistory, useTTS) | High | Pending |
| FR-04 | FE 핵심 컴포넌트 테스트 추가 (ThemeToggle, ExportPanel, CoverDesigner) | Medium | Pending |
| FR-05 | BE 미커버 서비스 테스트 추가 (design_service, publishing_service) | Medium | Pending |
| FR-06 | Playwright E2E: 로그인 → 대시보드 흐름 | High | Pending |
| FR-07 | Playwright E2E: 글쓰기 → 저장 흐름 | High | Pending |
| FR-08 | Playwright E2E: 편집 제안 수락/Undo 흐름 | Medium | Pending |
| FR-09 | GitHub Actions CI: test + lint + tsc 자동 실행 | Medium | Pending |
| FR-10 | 커버리지 리포트 CI 연동 (PR 코멘트) | Low | Pending |

### 3.2 Non-Functional Requirements

| Category | Criteria | Measurement |
|----------|----------|-------------|
| Coverage | FE statements >= 50%, BE >= 60% | vitest --coverage, pytest --cov |
| E2E | 핵심 사용자 흐름 3건 이상 통과 | npx playwright test |
| Deploy | Vercel 프로덕션 URL 접속 가능 | HTTP 200 확인 |
| CI | main 브랜치 push 시 자동 실행 | GitHub Actions green |

---

## 4. Implementation Phases

### Phase 1: Vercel 실제 배포

> 배포를 먼저 진행하여 E2E 테스트의 실제 환경 검증 기반 마련

**1-1. Backend 배포 URL 확인**
- Backend이 이미 배포된 경우: 해당 URL 사용
- 미배포 시: Docker 로컬 또는 별도 클라우드 배포 필요 (이 Sprint 범위 외)
- 대안: Vercel API Routes 또는 환경변수로 분리

**1-2. vercel.json URL 교체**
- **수정 파일**: `frontend/vercel.json`
- `https://api.example.com` → 실제 Backend URL (환경변수 참조 또는 직접 교체)

**1-3. 환경변수 설정**
- `NEXT_PUBLIC_API_URL`: Vercel 프로젝트 환경변수로 설정
- Vercel CLI 또는 Dashboard에서 설정

**1-4. 배포 실행**
```bash
cd frontend
npx vercel --prod
```

**1-5. 배포 검증**
- 프로덕션 URL 접속 → 랜딩 페이지 렌더링 확인
- `/login`, `/signup` 페이지 라우팅 확인
- 다크모드 토글 동작 확인

---

### Phase 2: Frontend 커버리지 향상

> 현재 10개 테스트 파일, 96개 테스트. 커버리지 12.5% → 50%+ 목표

**2-1. useEditHistory Hook 테스트**
- **새 파일**: `frontend/tests/hooks/useEditHistory.test.ts`
- push/undo/redo 동작, canUndo/canRedo 상태, MAX_HISTORY 한도

**2-2. ThemeToggle 컴포넌트 테스트**
- **새 파일**: `frontend/tests/components/ThemeToggle.test.tsx`
- light/dark/system 순환, aria-label 변경

**2-3. api.ts 핵심 함수 테스트**
- **새 파일**: `frontend/tests/lib/api.test.ts`
- fetch mock → login, getBooks, createBook 등 주요 API 함수

**2-4. 회원가입 동의 체크박스 테스트**
- **새 파일**: `frontend/tests/pages/signup.test.tsx`
- 3개 체크박스 미체크 → 버튼 비활성화, 모두 체크 → 활성화

**2-5. 커버리지 측정 및 기록**
```bash
cd frontend && npx vitest run --coverage
```

---

### Phase 3: Backend 커버리지 향상

> 현재 10개 테스트 파일, 170개 테스트. 커버리지 41% → 60%+ 목표

**3-1. design_service 테스트 보강**
- **수정 파일**: `backend/tests/test_design.py`
- Gemini API mock → 표지 생성 성공/실패/429 에러 케이스

**3-2. publishing_service 테스트 보강**
- **수정 파일**: `backend/tests/test_publishing.py`
- DOCX/PDF/EPUB 각 형식 출력 mock, include_cover 옵션 테스트

**3-3. core 모듈 테스트 추가**
- **새 파일**: `backend/tests/test_core.py`
- config.py 설정 로딩, security.py 토큰 검증

**3-4. 커버리지 측정**
```bash
cd backend && ./venv/bin/pytest --cov=app --cov-report=term-missing
```

---

### Phase 4: Playwright E2E 사용자 흐름

> 현재 접근성 1파일 → 사용자 흐름 3파일 추가

**4-1. 인증 흐름 E2E**
- **새 파일**: `frontend/tests/e2e/auth-flow.spec.ts`
- 로그인 → 대시보드 리다이렉트
- 잘못된 인증 → 에러 메시지 표시
- 로그아웃 → 랜딩 리다이렉트

**4-2. 글쓰기 흐름 E2E**
- **새 파일**: `frontend/tests/e2e/writing-flow.spec.ts`
- 대시보드 → 새 작품 만들기 → 글쓰기 페이지 진입
- 텍스트 입력 → 저장 확인

**4-3. 편집 흐름 E2E**
- **새 파일**: `frontend/tests/e2e/editing-flow.spec.ts`
- 편집 페이지 진입 → 탭 전환 → 분석 실행
- (모의) 제안 수락 → Undo 동작

---

### Phase 5: GitHub Actions CI

**5-1. CI 워크플로우 생성**
- **새 파일**: `.github/workflows/ci.yml`
- 트리거: push to main, PR
- Jobs:
  - `frontend-check`: tsc --noEmit + vitest + coverage report
  - `backend-check`: pytest + coverage report
  - `lint`: ESLint (FE)

---

## 5. Success Criteria

### 5.1 Definition of Done

- [ ] Vercel 프로덕션 URL 접속 가능 (또는 배포 설정 완료 + 대기)
- [ ] FE 커버리지 >= 50% (statements)
- [ ] BE 커버리지 >= 60%
- [ ] Playwright E2E 3건 이상 통과
- [ ] GitHub Actions CI green
- [ ] tsc --noEmit 0 errors
- [ ] vitest 전체 통과
- [ ] pytest 전체 통과 (기존 known issue 제외)

### 5.2 Quality Criteria

- [ ] 새 테스트에서 접근성 관련 assertion 포함
- [ ] CI에서 커버리지 리포트 생성
- [ ] E2E 테스트가 chromium + mobile-chrome 모두 통과

---

## 6. Risks and Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Backend 미배포로 Vercel API 리라이트 실패 | High | Medium | 환경변수로 API URL 분리, 로컬 프록시 대안 |
| FE 커버리지 50% 미달 | Medium | Low | 핵심 모듈 집중 테스트, threshold 점진 상향 |
| E2E 테스트 환경 불안정 | Medium | Medium | Playwright retry 설정, CI에서 headless 실행 |
| test_signup_success 기존 실패 | Low | High | CI에서 known issue 마킹 |

---

## 7. Modified Files Summary

| File | Type |
|------|------|
| `frontend/vercel.json` | 수정 |
| `frontend/tests/hooks/useEditHistory.test.ts` | **신규** |
| `frontend/tests/components/ThemeToggle.test.tsx` | **신규** |
| `frontend/tests/lib/api.test.ts` | **신규** |
| `frontend/tests/pages/signup.test.tsx` | **신규** |
| `backend/tests/test_design.py` | 수정 |
| `backend/tests/test_publishing.py` | 수정 |
| `backend/tests/test_core.py` | **신규** |
| `frontend/tests/e2e/auth-flow.spec.ts` | **신규** |
| `frontend/tests/e2e/writing-flow.spec.ts` | **신규** |
| `frontend/tests/e2e/editing-flow.spec.ts` | **신규** |
| `.github/workflows/ci.yml` | **신규** |

**신규 8개 / 수정 3개 = 총 11개 파일**

---

## 8. Next Steps

1. [ ] Do Phase 시작 — Phase 1~5 순서 구현
2. [ ] Gap Analysis — `/pdca analyze sprint10-deploy-coverage-e2e`
3. [ ] Report — `/pdca report sprint10-deploy-coverage-e2e`

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-03-06 | Initial draft | A0 Orchestrator |
