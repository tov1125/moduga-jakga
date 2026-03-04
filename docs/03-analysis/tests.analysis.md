# Tests Gap Analysis Report

> **Analysis Type**: Gap Analysis (Design vs Implementation)
>
> **Project**: moduga-jakga (v0.1.0)
> **Analyst**: bkit-gap-detector
> **Date**: 2026-03-03
> **Design Doc**: CLAUDE.md Section 12 (Test Requirements)

### Pipeline References

| Phase | Document | Verification Target |
|-------|----------|---------------------|
| Phase 2 | CLAUDE.md | Test conventions, tooling requirements |
| Phase 8 | CLAUDE.md Section 12 | Test infrastructure requirements |
| CI/CD | `.github/workflows/ci.yml` | Pipeline correctness |

---

## 1. Analysis Overview

### 1.1 Analysis Purpose

CLAUDE.md Section 12 defines four categories of testing requirements for this accessibility-first application:
1. Unit/Integration tests: pytest (Backend), Vitest (Frontend)
2. Accessibility automated tests: axe-core, Lighthouse
3. Screen reader manual tests: VoiceOver, TalkBack, NVDA
4. Visually impaired user usability tests

This report analyzes the gap between those design requirements and the actual test implementation.

### 1.2 Analysis Scope

- **Design Document**: `CLAUDE.md` Section 12, plus overall architecture requirements
- **Backend Tests**: `backend/tests/` (6 test files + conftest.py)
- **Frontend Tests**: `frontend/tests/accessibility/` (5 test files) + `frontend/tests/e2e/` (1 file)
- **CI/CD**: `.github/workflows/ci.yml`
- **Analysis Date**: 2026-03-03

---

## 2. Gap Analysis (Design vs Implementation)

### 2.1 Backend Test Coverage by API Module

The backend router (`backend/app/api/v1/router.py`) registers 9 API modules. The test coverage status per module:

| API Module | Endpoints | Test File | Status | Tests |
|------------|:---------:|-----------|:------:|:-----:|
| auth | 4 (signup, login, logout, me) | `test_auth.py` | Covered | 6 |
| books | 5 (list, create, get, update, delete) | `test_books.py` | Covered | 10 |
| chapters | 5 (list, create, get, update, delete) | -- | Not covered | 0 |
| stt | 1 (WebSocket stream) | `test_stt.py` | Covered | 5 |
| tts | 2 (synthesize, voices) | -- | Not covered | 0 |
| writing | 3 (generate, rewrite, structure) | `test_writing.py` | Covered | 8 |
| editing | 5 (proofread, style-check, structure-review, full-review, report) | `test_editing.py` | Covered | 6 |
| design | 3 (cover/generate, cover/templates, layout/preview) | -- | Not covered | 0 |
| publishing | 3 (export, status, download) | `test_publishing.py` | Covered | 8 |

**Summary**: 9 modules, 6 covered, **3 modules completely untested** (chapters, tts, design).

Endpoint-level coverage:

| Design Endpoint | Implementation | Test | Status |
|-----------------|:-:|:-:|:------:|
| POST /auth/signup | Yes | Yes | Matched |
| POST /auth/login | Yes | Yes | Matched |
| POST /auth/logout | Yes | Yes | Matched |
| GET /auth/me | Yes | Yes | Matched |
| GET /books/ | Yes | Yes | Matched |
| POST /books/ | Yes | Yes | Matched |
| GET /books/{id} | Yes | Yes | Matched |
| PUT /books/{id} | Yes | Yes | Matched |
| DELETE /books/{id} | Yes | Yes | Matched |
| GET /books/{book_id}/chapters | Yes | No | Missing test |
| POST /books/{book_id}/chapters | Yes | No | Missing test |
| GET /chapters/{id} | Yes | No | Missing test |
| PUT /chapters/{id} | Yes | No | Missing test |
| DELETE /chapters/{id} | Yes | No | Missing test |
| WS /stt/stream | Yes | Yes | Matched |
| POST /tts/synthesize | Yes | No | Missing test |
| GET /tts/voices | Yes | No | Missing test |
| POST /writing/generate | Yes | Yes | Matched |
| POST /writing/rewrite | Yes | Yes | Matched |
| POST /writing/structure | Yes | Yes | Matched |
| POST /editing/proofread | Yes | Yes | Matched |
| POST /editing/style-check | Yes | Yes | Matched |
| POST /editing/structure-review | Yes | Yes | Matched |
| POST /editing/full-review | Yes | Yes | Matched |
| GET /editing/report/{book_id} | Yes | Yes | Matched |
| POST /design/cover/generate | Yes | No | Missing test |
| GET /design/cover/templates | Yes | No | Missing test |
| POST /design/layout/preview | Yes | No | Missing test |
| POST /publishing/export | Yes | Yes | Matched |
| GET /publishing/export/{id} | Yes | Yes | Matched |
| GET /publishing/download/{id} | Yes | Yes | Matched |

**Total endpoints**: 31
**Tested endpoints**: 21
**Untested endpoints**: 10
**Endpoint test coverage**: 67.7%

### 2.2 Backend Service-Level Test Coverage

| Service | Test File | Unit Tests | Status |
|---------|-----------|:----------:|:------:|
| `stt_service.py` | `test_stt.py` | 2 (buffer, parse) | Partial |
| `publishing_service.py` | `test_publishing.py` | 1 (export_docx) | Partial |
| `writing_service.py` | -- | 0 | Not covered |
| `editing_service.py` | -- | 0 | Not covered |
| `tts_service.py` | -- | 0 | Not covered |
| `design_service.py` | -- | 0 | Not covered |
| `spelling_service.py` | -- | 0 | Not covered |
| `supabase_service.py` | -- | 0 | Not covered |

**Service unit test coverage**: 2 of 8 services (25%)

### 2.3 Frontend Test Coverage

#### 2.3.1 Component Test Coverage

| Component | Location | Test | Status |
|-----------|----------|:----:|:------:|
| Button | `ui/Button.tsx` | `ui-components.test.tsx` | Covered |
| Modal | `ui/Modal.tsx` | `modal.test.tsx` | Covered |
| SkipLink | `ui/SkipLink.tsx` | `wcag-checklist.test.tsx` | Covered |
| Announcer | `ui/Announcer.tsx` | -- | Not covered |
| VoiceRecorder | `voice/VoiceRecorder.tsx` | `voice-first.test.tsx` | Covered |
| VoicePlayer | `voice/VoicePlayer.tsx` | -- | Not covered |
| VoiceCommand | `voice/VoiceCommand.tsx` | -- | Not covered |
| Navigation | `layout/Navigation.tsx` | `navigation.test.tsx` | Covered |
| Header | `layout/Header.tsx` | -- | Not covered |
| Footer | `layout/Footer.tsx` | -- | Not covered |
| WritingEditor | `writing/WritingEditor.tsx` | -- | Not covered |
| StreamingText | `writing/StreamingText.tsx` | -- | Not covered |
| ChapterList | `writing/ChapterList.tsx` | -- | Not covered |
| EditingPanel | `editing/EditingPanel.tsx` | -- | Not covered |
| QualityReport | `editing/QualityReport.tsx` | -- | Not covered |
| ExportPanel | `book/ExportPanel.tsx` | -- | Not covered |
| CoverDesigner | `book/CoverDesigner.tsx` | -- | Not covered |

**Tested**: 5 of 17 components (29.4%)
**Untested**: 12 components

#### 2.3.2 Hook Test Coverage

| Hook | Location | Test | Status |
|------|----------|:----:|:------:|
| useSTT | `hooks/useSTT.ts` | Mocked only | Not directly tested |
| useTTS | `hooks/useTTS.ts` | -- | Not covered |
| useVoiceCommand | `hooks/useVoiceCommand.ts` | -- | Not covered |
| useAnnouncer | `hooks/useAnnouncer.ts` | Mocked only | Not directly tested |
| useKeyboardNav | `hooks/useKeyboardNav.ts` | -- | Not covered |
| useSupabase | `hooks/useSupabase.ts` | Mocked only | Not directly tested |

**Hook direct tests**: 0 of 6 (0%)

#### 2.3.3 Page Test Coverage

| Page | Location | Test | Status |
|------|----------|:----:|:------:|
| Landing (/) | `app/page.tsx` | E2E partial | Partial |
| Login (/login) | `app/(auth)/login/page.tsx` | E2E partial | Partial |
| Signup (/signup) | `app/(auth)/signup/page.tsx` | -- | Not covered |
| Dashboard | `app/dashboard/page.tsx` | -- | Not covered |
| Write | `app/write/page.tsx` | -- | Not covered |
| Write Book | `app/write/[bookId]/page.tsx` | -- | Not covered |
| Edit | `app/write/[bookId]/edit/page.tsx` | -- | Not covered |
| Review | `app/write/[bookId]/review/page.tsx` | -- | Not covered |
| Design | `app/design/[bookId]/page.tsx` | -- | Not covered |
| Publish | `app/publish/[bookId]/page.tsx` | -- | Not covered |
| Settings | `app/settings/page.tsx` | -- | Not covered |

**Tested pages**: 2 of 11 via E2E (18.2%), none via unit tests

### 2.4 Accessibility Test Coverage

| WCAG Category | Design Requirement | Implementation | Status |
|---------------|-------------------|----------------|:------:|
| **Perceivable** | Alt text, color independence | `wcag-checklist.test.tsx` (2 tests) | Partial |
| **Operable** | Keyboard nav, focus, skip link | `navigation.test.tsx` (13 tests), `wcag-checklist.test.tsx` (3 tests) | Good |
| **Understandable** | Korean UI, error messages | `wcag-checklist.test.tsx` (1 test) | Minimal |
| **Robust** | Valid ARIA, correct roles | `wcag-checklist.test.tsx` (2 tests), `ui-components.test.tsx` (11 tests), `modal.test.tsx` (9 tests) | Good |
| **Voice-First** | STT/TTS feedback, voice commands | `voice-first.test.tsx` (9 tests) | Good (single component) |
| **axe-core automated** | Full page axe scan | -- | Not implemented |
| **Lighthouse CI** | Score >= 90 | -- | Not implemented |
| **Screen reader manual** | VoiceOver, TalkBack, NVDA | -- | Not implemented (by design) |
| **User testing** | Visually impaired participants | -- | Not implemented (by design) |

### 2.5 E2E Test Coverage

| Test Area | Implementation | Status |
|-----------|:-:|:------:|
| Landing page basic a11y | `accessibility.spec.ts` | Covered |
| Heading hierarchy | `accessibility.spec.ts` | Covered |
| Link accessibility | `accessibility.spec.ts` | Covered |
| Tab navigation | `accessibility.spec.ts` | Covered |
| Login form labels | `accessibility.spec.ts` | Covered |
| Skip link functionality | `accessibility.spec.ts` | Covered |
| Full user flow (login -> write -> publish) | -- | Not covered |
| Voice recording E2E | -- | Not covered |
| Book creation/editing E2E | -- | Not covered |
| Export/download E2E | -- | Not covered |

### 2.6 Match Rate Summary

```
+-----------------------------------------------+
|  Backend API Endpoint Coverage: 67.7%          |
|----------------------------------------------+
|  Tested:          21 / 31 endpoints (67.7%)   |
|  Untested:        10 endpoints (32.3%)        |
|    - chapters:     5 endpoints                |
|    - tts:          2 endpoints                |
|    - design:       3 endpoints                |
+-----------------------------------------------+

+-----------------------------------------------+
|  Backend Service Unit Coverage: 25.0%          |
|----------------------------------------------+
|  Tested:          2 / 8 services (25.0%)      |
|  Untested:        6 services (75.0%)          |
+-----------------------------------------------+

+-----------------------------------------------+
|  Frontend Component Coverage: 29.4%            |
|----------------------------------------------+
|  Tested:          5 / 17 components (29.4%)   |
|  Untested:        12 components (70.6%)       |
+-----------------------------------------------+

+-----------------------------------------------+
|  Frontend Hook Coverage: 0.0%                  |
|----------------------------------------------+
|  Directly tested: 0 / 6 hooks (0.0%)         |
+-----------------------------------------------+

+-----------------------------------------------+
|  Page Coverage: 18.2%                          |
|----------------------------------------------+
|  Tested:          2 / 11 pages (18.2%)        |
|  Untested:        9 pages (81.8%)             |
+-----------------------------------------------+
```

---

## 3. Code Quality Analysis

### 3.1 Test Infrastructure Quality

| Aspect | Implementation | Quality |
|--------|:-:|:------:|
| Test fixtures (conftest.py) | Well-structured, dependency_overrides pattern | Good |
| Mock strategy | Consistent MagicMock/AsyncMock usage | Good |
| Test organization | Class-based grouping by feature | Good |
| Test naming | Korean docstrings, clear intent | Good |
| Async test support | pytest-asyncio configured | Good |
| Frontend test setup | Comprehensive mocks (MediaRecorder, AudioContext, etc.) | Good |
| vitest config | Coverage thresholds defined (80/70/75/80) | Good |
| Playwright config | Desktop + Mobile Chrome projects | Good |

### 3.2 Test Pattern Issues

| Type | File | Description | Severity |
|------|------|-------------|:--------:|
| Incomplete mock | `test_stt.py` | WebSocket test uses deep patching, fragile | Warning |
| Missing negative tests | `test_books.py` | No test for concurrent update race condition | Info |
| Missing boundary tests | `test_writing.py` | No max_tokens boundary test | Info |
| No integration tests | All backend | Tests are pure unit with mocks, no actual DB integration | Warning |
| Coverage threshold not enforced | CI pipeline | `continue-on-error: true` on coverage step | Warning |

### 3.3 Security Test Issues

| Severity | Area | Issue | Recommendation |
|:--------:|------|-------|----------------|
| Warning | Auth | No test for JWT token expiration | Add expired token test |
| Warning | Auth | No test for token refresh flow | Add refresh token test |
| Warning | CORS | No CORS policy test | Add CORS validation test |
| Warning | Rate Limiting | No rate limit test | Add rate limit test |
| Info | Input Validation | Partial coverage (422 tests exist) | Expand boundary tests |

---

## 4. CI/CD Pipeline Analysis

### 4.1 Pipeline Structure

| Job | Purpose | Status | Issues |
|-----|---------|:------:|--------|
| `backend-test` | pytest + ruff + mypy | Configured | mypy is continue-on-error |
| `frontend-test` | Vitest + TypeScript + ESLint | Configured | TypeScript and ESLint are continue-on-error |
| `build` | Frontend build + Docker build | Configured | OK |
| `quality-gate` | Final pass/fail decision | Configured | OK |

### 4.2 Pipeline Gap Analysis

| Design Requirement | CI Implementation | Status |
|-------------------|:-:|:------:|
| pytest unit tests | `pytest tests/ -v --tb=short --cov=app` | Implemented |
| Vitest unit tests | `npm run test:run` | Implemented |
| Coverage reports | `npm run test:coverage` | Implemented (continue-on-error) |
| ruff lint | `ruff check app/ tests/` | Implemented |
| mypy type check | `mypy app/ --ignore-missing-imports` | Implemented (continue-on-error) |
| ESLint | `npm run lint` | Implemented (continue-on-error) |
| TypeScript check | `npx tsc --noEmit` | Implemented (continue-on-error) |
| Docker build | `docker build` for both | Implemented |
| Playwright E2E | -- | Not in CI |
| axe-core automated a11y | -- | Not in CI |
| Lighthouse CI | -- | Not in CI |
| Coverage threshold enforcement | -- | Not enforced (continue-on-error) |

### 4.3 Missing CI/CD Elements

| Element | Priority | Description |
|---------|:--------:|-------------|
| Playwright E2E in CI | High | E2E tests exist but not run in pipeline |
| axe-core CI integration | High | Critical for accessibility-first project |
| Lighthouse CI | Medium | Accessibility score tracking |
| Coverage gate enforcement | Medium | Currently continue-on-error, should fail CI |
| mypy strict enforcement | Low | Currently continue-on-error |

---

## 5. Test Coverage vs Design Requirements

### 5.1 CLAUDE.md Section 12 Compliance

| Requirement | Status | Details |
|-------------|:------:|---------|
| Unit/Integration: pytest (BE) | Partial | 6/9 modules covered, 0 integration tests |
| Unit/Integration: Vitest (FE) | Partial | 5/17 components, 0/6 hooks, 0/11 pages directly |
| Accessibility: axe-core | Not implemented | vitest-axe installed but not used in any test |
| Accessibility: Lighthouse | Not implemented | Not configured |
| Screen reader: VoiceOver, TalkBack, NVDA | N/A | Manual testing, cannot be automated |
| User testing: visually impaired users | N/A | Requires human participants |

### 5.2 Coverage Summary Table

| Area | Current | Target | Status |
|------|:-------:|:------:|:------:|
| BE Endpoint Coverage | 67.7% | 90%+ | Below target |
| BE Service Unit Tests | 25.0% | 80%+ | Below target |
| FE Component Tests | 29.4% | 80%+ | Below target |
| FE Hook Tests | 0.0% | 75%+ | Below target |
| FE Page Tests | 18.2% | 60%+ | Below target |
| Accessibility Automated | 0% | 90%+ axe score | Not started |
| E2E User Flows | 0 flows | 3+ critical flows | Not started |

---

## 6. Clean Architecture Compliance (Test Structure)

### 6.1 Backend Test Organization

| Expected | Actual | Status |
|----------|--------|:------:|
| `tests/conftest.py` | Exists, well-structured | Matched |
| `tests/test_{module}.py` per API module | 6 of 9 modules | Partial |
| Separate `tests/services/` for service unit tests | Not separated | Missing |
| Separate `tests/integration/` | Not present | Missing |

### 6.2 Frontend Test Organization

| Expected | Actual | Status |
|----------|--------|:------:|
| `tests/setup.ts` | Exists, comprehensive mocks | Matched |
| `tests/accessibility/` | 5 test files, focused | Matched |
| `tests/e2e/` | 1 file (accessibility.spec.ts) | Partial |
| `tests/components/` | Not present | Missing |
| `tests/hooks/` | Not present | Missing |
| `tests/pages/` | Not present | Missing |

---

## 7. Convention Compliance

### 7.1 Test Naming Convention

| Category | Convention | Compliance | Violations |
|----------|-----------|:----------:|------------|
| Backend test files | `test_{module}.py` | 100% | None |
| Backend test functions | `test_{description}` | 100% | None |
| Backend test classes | `Test{Feature}` | 100% | None |
| Frontend test files | `{feature}.test.tsx` | 100% | None |
| Frontend E2E files | `{feature}.spec.ts` | 100% | None |
| Korean docstrings | Present on all BE tests | 100% | None |
| JSDoc comments | Present on all FE test files | 100% | None |

### 7.2 Test Quality Convention

| Convention | Implementation | Status |
|-----------|:-:|:------:|
| Each test has a single assertion focus | Yes | Good |
| Tests are independent (no shared state) | Yes | Good |
| Mocks are properly reset | `vi.clearAllMocks()` used | Good |
| Async tests properly handled | `@pytest.mark.asyncio` / `async` | Good |
| Type hints in all BE test functions | Return type `None` annotated | Good |

### 7.3 Convention Score

```
+-----------------------------------------------+
|  Convention Compliance: 95%                    |
|----------------------------------------------+
|  Naming:          100%                        |
|  Organization:     85% (missing directories)  |
|  Quality:          98%                        |
|  Documentation:    98%                        |
+-----------------------------------------------+
```

---

## 8. Overall Score

```
+-----------------------------------------------+
|  Overall Score: 52/100                         |
|----------------------------------------------+
|  Design Match:        45 points               |
|    - BE endpoints:     68% covered            |
|    - FE components:    29% covered            |
|    - Hooks/Pages:      ~9% covered            |
|  Test Quality:        85 points               |
|    - Well-structured conftest/setup           |
|    - Consistent patterns                      |
|    - Good naming/documentation                |
|  CI/CD Completeness:  55 points               |
|    - Core pipeline works                      |
|    - Missing E2E, axe-core, Lighthouse        |
|    - continue-on-error on critical steps      |
|  Accessibility Tests: 40 points               |
|    - Good ARIA/keyboard tests for 5 components|
|    - axe-core not integrated                  |
|    - Lighthouse not integrated                |
|  Convention:          95 points               |
|    - Naming, quality, docs all excellent      |
+-----------------------------------------------+
|  Weighted Overall:    52%                      |
|  Status:              Below Target             |
+-----------------------------------------------+
```

---

## 9. Differences Found

### 9.1 Missing Features (Design O, Implementation X)

| Item | Design Location | Description |
|------|-----------------|-------------|
| test_chapters.py | CLAUDE.md: chapters API | All 5 chapter CRUD endpoints untested |
| test_tts.py | CLAUDE.md: TTS service | POST /tts/synthesize and GET /tts/voices untested |
| test_design.py | CLAUDE.md: book design | All 3 design endpoints untested |
| axe-core integration | CLAUDE.md Section 12 | `vitest-axe` installed but never imported in tests |
| Lighthouse CI | CLAUDE.md Section 12 | Not configured anywhere |
| E2E user flow tests | CLAUDE.md: full user journey | No login-to-publish E2E flow |
| Hook unit tests | CLAUDE.md: FE testing | 0 of 6 hooks directly tested |
| Component tests (12 of 17) | CLAUDE.md: FE testing | VoicePlayer, VoiceCommand, Header, Footer, WritingEditor, StreamingText, ChapterList, EditingPanel, QualityReport, ExportPanel, CoverDesigner, Announcer |
| Page tests | CLAUDE.md: FE testing | 9 of 11 pages have no tests |
| Service unit tests | CLAUDE.md: BE testing | 6 of 8 services have no unit tests |
| Integration tests | CLAUDE.md Section 12 | No integration tests (all are unit with mocks) |
| Security tests | CLAUDE.md Section 11 | No JWT expiration, CORS, rate limit tests |

### 9.2 Added Features (Design X, Implementation O)

| Item | Implementation Location | Description |
|------|------------------------|-------------|
| E2E accessibility spec | `tests/e2e/accessibility.spec.ts` | Playwright a11y E2E not explicitly in CLAUDE.md but valuable |
| Voice-First specific tests | `tests/accessibility/voice-first.test.tsx` | Extends beyond CLAUDE.md Section 12 requirements |

### 9.3 Changed Features (Design != Implementation)

| Item | Design | Implementation | Impact |
|------|--------|----------------|:------:|
| Test count claim | "8 test files, 62 BE tests" | 6 test files found, not 8 | Medium |
| axe-core usage | "axe-core automated tests" | vitest-axe installed, never used | High |
| Lighthouse | "Lighthouse accessibility tests" | Not present | High |
| Coverage enforcement | Thresholds set (80/70/75/80) | CI uses continue-on-error | Medium |

---

## 10. Recommended Actions

### 10.1 Immediate Actions (High Priority)

| Priority | Item | Impact | Effort |
|:--------:|------|:------:|:------:|
| 1 | Create `test_chapters.py` for 5 CRUD endpoints | Coverage +16% | Medium |
| 2 | Create `test_tts.py` for synthesize + voices | Coverage +6.5% | Low |
| 3 | Create `test_design.py` for cover + layout | Coverage +9.7% | Medium |
| 4 | Integrate axe-core into existing Vitest tests | Accessibility | Low |
| 5 | Add Playwright E2E to CI pipeline | CI completeness | Low |

### 10.2 Short-term Actions (Within 1 Week)

| Priority | Item | Expected Impact |
|:--------:|------|-----------------|
| 1 | Add component tests for writing/* (WritingEditor, StreamingText, ChapterList) | FE coverage +17.6% |
| 2 | Add component tests for voice/* (VoicePlayer, VoiceCommand) | Voice-First validation |
| 3 | Add hook unit tests (useSTT, useTTS, useVoiceCommand) | Hook coverage +50% |
| 4 | Remove `continue-on-error` from coverage step in CI | Enforce quality gate |
| 5 | Add JWT expiration and CORS tests | Security coverage |
| 6 | Add Lighthouse CI step to workflow | Accessibility tracking |

### 10.3 Long-term Actions (Backlog)

| Item | Description |
|------|-------------|
| Integration test suite | Test with real Supabase test project (or testcontainers) |
| Full E2E user flow | Login -> create book -> write -> edit -> publish flow |
| Service-level unit tests | Direct tests for all 8 backend services |
| Page-level tests | Render tests for all 11 frontend pages |
| Performance tests | API response time benchmarks |
| Screen reader compatibility docs | Document manual VoiceOver/NVDA test results |

---

## 11. Design Document Updates Needed

The following items in CLAUDE.md or project memory need clarification:

- [ ] Project memory states "8 test files" for backend but only 6 exist (conftest.py is not a test file). Update count to 6.
- [ ] Clarify whether `vitest-axe` integration is a Phase 8 deliverable or deferred.
- [ ] Add E2E accessibility tests as an explicit requirement in Section 12.
- [ ] Document which CI steps should be strict (fail pipeline) vs advisory (continue-on-error).
- [ ] Specify coverage threshold targets per module (currently only global thresholds).

---

## 12. Test File Inventory

### Backend Tests (6 files)

| File | Path | Tests | Focus |
|------|------|:-----:|-------|
| conftest.py | `backend/tests/conftest.py` | (fixtures) | Mock settings, Supabase, OpenAI, sample data |
| test_auth.py | `backend/tests/test_auth.py` | 6 | Signup, login, logout, me |
| test_books.py | `backend/tests/test_books.py` | 10 | CRUD for books, auth checks |
| test_stt.py | `backend/tests/test_stt.py` | 5 | WebSocket auth, streaming, service unit |
| test_writing.py | `backend/tests/test_writing.py` | 8 | Generate, rewrite, structure |
| test_editing.py | `backend/tests/test_editing.py` | 6 | Proofread, style, structure review, full review, report |
| test_publishing.py | `backend/tests/test_publishing.py` | 8 | Export, status, download, DOCX service |

**Total backend tests**: 43 (user claim: 62 -- discrepancy may indicate tests were removed or count includes parameterized variants)

### Frontend Tests (6 files)

| File | Path | Tests | Focus |
|------|------|:-----:|-------|
| setup.ts | `frontend/tests/setup.ts` | (setup) | Global mocks, jest-dom, MediaRecorder, AudioContext |
| ui-components.test.tsx | `frontend/tests/accessibility/ui-components.test.tsx` | 11 | Button a11y: role, aria, keyboard, focus, touch target |
| modal.test.tsx | `frontend/tests/accessibility/modal.test.tsx` | 9 | Modal a11y: dialog, escape, focus trap, announcer |
| voice-first.test.tsx | `frontend/tests/accessibility/voice-first.test.tsx` | 9 | VoiceRecorder: aria-live, states, errors, SVG hidden |
| navigation.test.tsx | `frontend/tests/accessibility/navigation.test.tsx` | 13 | Navigation: menubar, aria-current, keyboard arrows |
| wcag-checklist.test.tsx | `frontend/tests/accessibility/wcag-checklist.test.tsx` | 8 | WCAG 4 principles: perceivable, operable, understandable, robust |
| accessibility.spec.ts | `frontend/tests/e2e/accessibility.spec.ts` | 7 | Playwright E2E: lang, headings, links, tab, skip link, form labels |

**Total frontend tests**: 57 (aligns roughly with user claim of 51 -- difference may be from test.each or describe blocks)

---

## 13. Next Steps

- [ ] Create missing backend test files (chapters, tts, design) to reach 90%+ endpoint coverage
- [ ] Integrate axe-core into at least 3 existing frontend test files
- [ ] Add Playwright E2E step to `.github/workflows/ci.yml`
- [ ] Remove `continue-on-error` from coverage and lint steps
- [ ] Write completion report after achieving 90% match rate

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-03-03 | Initial gap analysis | bkit-gap-detector |
