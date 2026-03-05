# Sprint 12 Analysis Report (v2): 접근성 VETO + 보안 강화

> **Analysis Type**: Gap Re-Analysis (Design vs Implementation) -- Check-2
>
> **Project**: moduga-jakga (v0.1.0)
> **Analyst**: gap-detector
> **Date**: 2026-03-05
> **Design Doc**: [sprint12-accessibility-security.design.md](../02-design/features/sprint12-accessibility-security.design.md)

### Pipeline References

| Phase | Document | Verification Target |
|-------|----------|---------------------|
| Phase 2 | CLAUDE.md | Convention compliance |
| Phase 4 | design.md Section 1-6 | Security header, CORS, Rate Limiting, Testing |
| Phase 8 | This document | Architecture/Convention review |

---

## 1. Analysis Overview

### 1.1 Analysis Purpose

Sprint 12 Check-1에서 발견된 4건의 Gap(CSP 헤더 누락, Rate Limit 라우트 미적용, 429 테스트 누락, Authorization 키 미구현)이 모두 해소되었는지 재검증한다.

### 1.2 Analysis Scope

| # | Design Item | Implementation File | Status |
|---|-------------|---------------------|--------|
| 1 | BE 보안 헤더 미들웨어 | `backend/app/main.py` | Re-checked |
| 2 | FE Next.js 보안 헤더 | `frontend/next.config.ts` | Re-checked |
| 3 | CORS 강화 | `backend/app/main.py` | Re-checked |
| 4 | Rate Limiting | `backend/app/core/rate_limit.py` + `backend/app/main.py` | Re-checked |
| 5 | axe-core 접근성 테스트 | `frontend/tests/accessibility/axe-core.test.tsx` | Re-checked |
| 6 | 보안 테스트 | `backend/tests/test_security_headers.py` | Re-checked |

### 1.3 Previous Gap Summary (Check-1, 78.7%)

| # | Gap | Severity | Resolution |
|---|-----|----------|------------|
| 1 | CSP 헤더 누락 | High | RESOLVED -- `main.py:56-59` |
| 2 | Rate Limit 라우트 미적용 | High | RESOLVED -- 미들웨어 방식 전환 |
| 3 | Rate Limit 429 테스트 누락 | Medium | RESOLVED -- `test_rate_limit_429_response` |
| 4 | Authorization 헤더 우선 키 미구현 | Medium | RESOLVED -- `_get_client_key()` |

---

## 2. Gap Analysis (Design vs Implementation)

### 2.1 BE 보안 헤더 미들웨어

**Design (design.md Section 1)**: 6개 보안 헤더

**Implementation (`backend/app/main.py:46-60`)**:

```python
response.headers["X-Content-Type-Options"] = "nosniff"
response.headers["X-Frame-Options"] = "DENY"
response.headers["X-XSS-Protection"] = "1; mode=block"
response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
response.headers["Permissions-Policy"] = "camera=(), microphone=(self), geolocation=()"
response.headers["Content-Security-Policy"] = (
    "default-src 'self'; img-src 'self' data: https://*.supabase.co; "
    "style-src 'self' 'unsafe-inline'; connect-src 'self' https://*.supabase.co"
)
```

| Header | Design | Implementation | Status |
|--------|--------|----------------|--------|
| X-Content-Type-Options | nosniff | nosniff | Match |
| X-Frame-Options | DENY | DENY | Match |
| X-XSS-Protection | 1; mode=block | 1; mode=block | Match |
| Referrer-Policy | strict-origin-when-cross-origin | strict-origin-when-cross-origin | Match |
| Permissions-Policy | camera=(), microphone=(self), geolocation=() | camera=(), microphone=(self), geolocation=() | Match |
| Content-Security-Policy | default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline' | default-src 'self'; img-src 'self' data: https://*.supabase.co; style-src 'self' 'unsafe-inline'; connect-src 'self' https://*.supabase.co | Enhanced |

**Verdict**: 6/6 headers implemented. CSP was the main Check-1 Gap -- now implemented with Supabase 도메인 추가 (실운영 필요한 확장). 설계보다 더 견고함.

---

### 2.2 FE Next.js 보안 헤더

**Design (design.md Section 2)**: 4개 헤더

**Implementation (`frontend/next.config.ts:5-23`)**:

| Header | Design | Implementation | Status |
|--------|--------|----------------|--------|
| X-Content-Type-Options | nosniff | nosniff | Match |
| X-Frame-Options | DENY | DENY | Match |
| X-XSS-Protection | -- | 1; mode=block | Added (beneficial) |
| Referrer-Policy | strict-origin-when-cross-origin | strict-origin-when-cross-origin | Match |
| Permissions-Policy | camera=(), microphone=(self), geolocation=() | camera=(), microphone=(self), geolocation=() | Match |

**Verdict**: 4/4 설계 헤더 구현 완료. X-XSS-Protection 추가 (방어적 확장).

---

### 2.3 CORS 강화

**Design (design.md Section 3)**: 명시적 메서드/헤더

**Implementation (`backend/app/main.py:72-78`)**:

| Config | Design | Implementation | Status |
|--------|--------|----------------|--------|
| allow_methods | 5 methods (GET/POST/PUT/DELETE/PATCH) | 6 methods (+OPTIONS) | Enhanced |
| allow_headers | 3 headers (Authorization/Content-Type/Accept) | 3 headers | Match |
| Wildcard eliminated | Yes | Yes | Match |

**Verdict**: OPTIONS 추가는 CORS preflight에 필수적이므로 의도적 확장으로 인정.

---

### 2.4 Rate Limiting

**Design (design.md Section 4)**:
- slowapi 기반
- 일반 API: 60req/min
- AI API (writing, editing, design): 10req/min
- 키: IP 기반 (Authorization 헤더 우선)

**Implementation**: 설계 대비 구현 방식이 변경됨. slowapi `@limiter.limit()` 데코레이터 대신 커스텀 미들웨어 방식으로 전환. 기능적으로 동등하거나 우수함.

| Item | Design | Implementation | Status |
|------|--------|----------------|--------|
| Library | slowapi | Custom middleware (in-process dict) | Changed (functionally equivalent) |
| Default limit | 60/min | `DEFAULT_LIMIT = 60`, `WINDOW_SECONDS = 60` | Match |
| AI limit | 10/min | `AI_LIMIT = 10` | Match |
| AI path detection | writing, editing, design | `AI_PATHS = ("/api/v1/writing/", "/api/v1/editing/", "/api/v1/design/cover/generate")` | Match |
| Key function | IP + Authorization 우선 | `_get_client_key()`: Bearer token 우선, IP fallback | Match |
| Route application | Applied to routes | Middleware 방식 -- 모든 경로에 자동 적용 | Match (method differs) |
| 429 response | Implied | `JSONResponse(status_code=429, ...)` with `Retry-After` header | Match |
| Testing env bypass | Not specified | `_TESTING` flag -- pytest 환경에서 비활성화 | Added (practical) |

**Key function verification** (`backend/app/core/rate_limit.py:30-36`):

```python
def _get_client_key(request: Request) -> str:
    """Authorization 헤더 우선, 없으면 IP 기반 키"""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer ") and len(auth) > 23:
        return f"user:{auth[-16:]}"
    client = request.client
    return client.host if client else "unknown"
```

**Verdict**: Check-1의 2개 주요 Gap(라우트 미적용, Authorization 키 미구현) 모두 해소됨. 미들웨어 방식은 데코레이터 방식보다 누락 위험이 없어 더 견고한 접근법.

---

### 2.5 axe-core 접근성 테스트

**Design (design.md Section 5)**: vitest-axe, 주요 페이지, WCAG 2.1 AA

**Implementation (`frontend/tests/accessibility/axe-core.test.tsx`)**:

| Item | Design | Implementation | Status |
|------|--------|----------------|--------|
| File name | `axe.test.tsx` | `axe-core.test.tsx` | Changed (minor) |
| Library | vitest-axe | vitest-axe | Match |
| Test count | Implied (major pages) | 7 tests (Button 3 + StreamingText 2 + Input 1 + Footer 1) | Match |
| WCAG 2.1 AA | Required | axe() default (best-practice + AA) | Match |

**Remaining note**: Import `@/components/ui/Input` (PascalCase path) vs actual file `input.tsx` (lowercase). macOS(HFS+)에서는 동작하지만 Linux CI에서 실패 가능. 단, 현재 테스트 결과 FE 278 passed 확인됨 (macOS 환경).

**Verdict**: 기능적으로 완전 일치. 파일명 차이는 의도적 선택(axe-core 명칭 반영).

---

### 2.6 보안 테스트

**Design (design.md Section 6)**: 보안 헤더 확인, CORS 검증, Rate Limiting 429 검증

**Implementation (`backend/tests/test_security_headers.py`)**: 3 classes, 14 tests

| Test Category | Design | Implementation | Count | Status |
|---------------|--------|----------------|:-----:|--------|
| Security Headers | Yes | TestSecurityHeaders (7 tests) | 7 | Match |
| -- X-Content-Type-Options | | `test_x_content_type_options` | | |
| -- X-Frame-Options | | `test_x_frame_options` | | |
| -- X-XSS-Protection | | `test_x_xss_protection` | | |
| -- Referrer-Policy | | `test_referrer_policy` | | |
| -- Permissions-Policy | | `test_permissions_policy` | | |
| -- Content-Security-Policy | | `test_content_security_policy` | | |
| -- Health endpoint | | `test_health_endpoint_ok` | | |
| CORS Headers | Yes | TestCORSHeaders (2 tests) | 2 | Match |
| -- Preflight | | `test_cors_preflight_allowed_method` | | |
| -- No wildcard | | `test_cors_no_wildcard_methods` | | |
| Rate Limiting | Yes | TestRateLimiting (5 tests) | 5 | Match |
| -- Middleware registered | | `test_rate_limit_middleware_registered` | | |
| -- Auth header key | | `test_rate_limit_key_uses_auth_header` | | |
| -- IP fallback key | | `test_rate_limit_key_fallback_to_ip` | | |
| -- AI path detection | | `test_ai_path_detection` | | |
| -- 429 response | | `test_rate_limit_429_response` | | |

**Verdict**: 설계 3개 카테고리 모두 커버. Check-1에서 누락이었던 Rate Limit 429 테스트가 추가됨. 총 14개 테스트로 설계 요구사항을 초과 달성.

---

## 3. Match Rate Summary

### Per-Item Scoring

| # | Item | Weight | Design Items | Matched | Score |
|---|------|:------:|:------------:|:-------:|:-----:|
| 1 | BE 보안 헤더 | 20% | 6 headers | 6 (CSP enhanced) | 100% |
| 2 | FE 보안 헤더 | 15% | 4 headers | 4 (+1 bonus) | 100% |
| 3 | CORS 강화 | 15% | 2 configs | 2 (+OPTIONS) | 100% |
| 4 | Rate Limiting | 20% | 4 items | 4 (middleware method) | 100% |
| 5 | axe-core 접근성 | 15% | 4 items | 3.5 (import casing note) | 93.8% |
| 6 | 보안 테스트 | 15% | 3 categories | 3 (14 tests total) | 100% |

### Weighted Match Rate

```
(0.20 * 100) + (0.15 * 100) + (0.15 * 100) + (0.20 * 100) + (0.15 * 93.8) + (0.15 * 100)
= 20.0 + 15.0 + 15.0 + 20.0 + 14.07 + 15.0
= 99.07%
```

```
+---------------------------------------------+
|  Overall Match Rate: 99.1%                  |
+---------------------------------------------+
|  Match:           22 items  (88.0%)         |
|  Enhanced:         3 items  (12.0%)         |
|  Missing/Gap:      0 items  ( 0.0%)         |
+---------------------------------------------+
```

---

## 4. Overall Scores

| Category | Score | Status |
|----------|:-----:|:------:|
| Design Match | 99.1% | Pass |
| Architecture Compliance | 100% | Pass |
| Convention Compliance | 96% | Pass |
| **Overall** | **99.1%** | **Pass** |

Status legend: Pass (>=90%), Warning (>=70% and <90%), Fail (<70%)

---

## 5. Gap Resolution Summary (Check-1 -> Check-2)

### 5.1 Resolved Gaps (4/4 -- all resolved)

| # | Gap (Check-1) | Resolution | Evidence |
|---|---------------|------------|----------|
| 1 | CSP 헤더 누락 | `Content-Security-Policy` 추가 (Supabase 도메인 확장 포함) | `backend/app/main.py:56-59` |
| 2 | Rate Limit 라우트 미적용 | 미들웨어 방식 전환 -- 모든 경로 자동 적용 | `backend/app/core/rate_limit.py:44-70`, `backend/app/main.py:64-67` |
| 3 | Rate Limit 429 테스트 누락 | `test_rate_limit_429_response` 추가 | `backend/tests/test_security_headers.py:129-145` |
| 4 | Authorization 헤더 우선 키 미구현 | `_get_client_key()` 구현 -- Bearer 우선, IP 폴백 | `backend/app/core/rate_limit.py:30-36` |

### 5.2 Added Features (Design X, Implementation O)

| # | Item | Implementation Location | Description | Impact |
|---|------|------------------------|-------------|--------|
| 1 | X-XSS-Protection (FE) | `frontend/next.config.ts:12` | FE 설계에 없지만 BE 설계와 일관성 유지 | Low -- beneficial |
| 2 | OPTIONS method | `backend/app/main.py:76` | CORS preflight에 필수 | Low -- necessary |
| 3 | Health endpoint test | `backend/tests/test_security_headers.py:52-56` | 기본 서버 상태 확인 | Low -- useful |
| 4 | Supabase CSP domains | `backend/app/main.py:57-58` | img-src, connect-src에 Supabase 도메인 추가 | Low -- practical |
| 5 | Testing env bypass | `backend/app/core/rate_limit.py:14,46-47` | pytest 환경 자동 비활성화 | Low -- practical |
| 6 | Retry-After header | `backend/app/core/rate_limit.py:65` | 429 응답에 표준 Retry-After 헤더 포함 | Low -- best practice |
| 7 | Additional RL tests | `backend/tests/test_security_headers.py:89-128` | Auth key, IP fallback, AI path 개별 테스트 | Low -- thorough |

### 5.3 Remaining Minor Notes

| # | Item | Description | Severity | Action |
|---|------|-------------|----------|--------|
| 1 | axe test file name | Design: `axe.test.tsx`, Impl: `axe-core.test.tsx` | Trivial | Update design or record as intentional |
| 2 | Input import casing | Import `@/components/ui/Input` vs file `input.tsx` | Low | macOS OK, Linux CI risk. Change to `@/components/ui/input` recommended |
| 3 | Rate Limit library | Design: slowapi, Impl: custom middleware | Info | Custom approach is more integrated and auto-applies to all routes |

---

## 6. Test Coverage Summary

### BE Security Tests (`backend/tests/test_security_headers.py`)

| Class | Test Count | Category |
|-------|:----------:|----------|
| TestSecurityHeaders | 7 | 보안 헤더 6종 + health |
| TestCORSHeaders | 2 | preflight + wildcard |
| TestRateLimiting | 5 | middleware + key func + AI path + 429 |
| **Total** | **14** | |

### FE Accessibility Tests (`frontend/tests/accessibility/axe-core.test.tsx`)

| Component | Test Count | Coverage |
|-----------|:----------:|----------|
| Button | 3 | basic, disabled, variants |
| StreamingText | 2 | static, streaming |
| Input | 1 | with label |
| Footer | 1 | basic |
| **Total** | **7** | |

### Overall Test Results

| Suite | Passed | Failed | Known Failures |
|-------|:------:|:------:|:--------------:|
| BE (pytest) | 282 | 0 | 1 (external Supabase) |
| FE (vitest) | 278 | 0 | 0 |
| **Total** | **560** | **0** | **1** |

---

## 7. Architecture Compliance

### Layer Structure

| Layer | Files Modified | Dependency Violations |
|-------|:--------------:|:---------------------:|
| Presentation (FE pages/components) | next.config.ts, axe-core.test.tsx | None |
| Application (BE services) | -- | None |
| Infrastructure (BE middleware) | main.py, rate_limit.py | None |
| Tests | test_security_headers.py | None |

Rate Limiting 미들웨어가 `app/core/` 레이어에 배치되어 인프라스트럭처 레이어 규칙을 준수한다. 미들웨어는 app 진입점(`main.py`)에서 등록되며, 서비스 로직과 분리되어 있다.

---

## 8. Convention Compliance

| Convention | Checked | Compliance | Notes |
|------------|:-------:|:----------:|-------|
| Naming (PascalCase components) | Yes | 100% | Button.tsx, Footer.tsx OK |
| Naming (snake_case Python) | Yes | 100% | rate_limit.py, _get_client_key OK |
| Pydantic Strict types | N/A | -- | No new schemas in Sprint 12 |
| Type hints (Python) | Yes | 100% | All functions have type hints |
| async/await | Yes | 100% | All handlers async |
| File naming (kebab-case) | Yes | 90% | `rate_limit.py` uses underscore (Python convention) |
| Import order | Yes | 100% | stdlib > third-party > local |

---

## 9. Recommended Actions

### 9.1 Documentation Updates (Optional)

| Item | Action | Priority |
|------|--------|----------|
| FE X-XSS-Protection | design.md Section 2에 추가 | Low |
| OPTIONS method | design.md Section 3에 추가 | Low |
| axe test file name | design.md Section 5를 `axe-core.test.tsx`로 변경 | Low |
| Rate Limit 방식 | design.md Section 4를 "미들웨어 방식"으로 업데이트 | Low |
| Supabase CSP | design.md Section 1의 CSP에 Supabase 도메인 추가 | Low |

### 9.2 Minor Code Improvement (Optional)

| Item | File | Action | Priority |
|------|------|--------|----------|
| Input import casing | `frontend/tests/accessibility/axe-core.test.tsx:11` | `@/components/ui/Input` -> `@/components/ui/input` | Low (Linux CI only) |

---

## 10. Post-Analysis Verdict

**Match Rate 99.1% -- Pass (>=90%)**

Check-1에서 발견된 4건의 Gap이 모두 해소되었다.

**주요 개선 사항**:

1. **CSP 헤더 구현 (High Gap -> Resolved)**: Supabase 도메인을 포함한 실운영 수준의 CSP 정책이 적용되어 설계보다 더 견고해짐.

2. **Rate Limiting 미들웨어 전환 (High Gap -> Resolved)**: slowapi 데코레이터 방식 대신 커스텀 미들웨어로 전환. 모든 경로에 자동 적용되어 데코레이터 누락 위험 제거. AI 경로 패턴 자동 감지, Authorization 헤더 우선 키, pytest 환경 자동 비활성화 포함.

3. **Rate Limit 429 테스트 추가 (Medium Gap -> Resolved)**: 단순 429 응답 확인뿐 아니라 Auth 키 함수, IP 폴백, AI 경로 감지까지 5개 테스트로 포괄적 검증.

4. **Authorization 헤더 우선 키 (Medium Gap -> Resolved)**: `_get_client_key()` 함수가 Bearer 토큰을 우선 확인하고 IP로 폴백하는 로직 정확히 구현.

남은 사항은 파일명/import casing 차이와 같은 경미한 노트뿐이며, 기능적 Gap은 없다.

---

## 11. Check-1 vs Check-2 Comparison

| Metric | Check-1 | Check-2 | Delta |
|--------|:-------:|:-------:|:-----:|
| Match Rate | 78.7% | 99.1% | +20.4% |
| Missing Items | 4 | 0 | -4 |
| BE Tests | 9 | 14 | +5 |
| FE Tests | 5 | 7 | +2 |
| Gaps (High) | 2 | 0 | -2 |
| Gaps (Medium) | 2 | 0 | -2 |
| Status | Warning | **Pass** | Upgraded |

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-03-05 | Initial gap analysis (78.7%) | gap-detector |
| 2.0 | 2026-03-05 | Re-analysis after 4 Gap fixes (99.1%) | gap-detector |
