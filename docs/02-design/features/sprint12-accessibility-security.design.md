# Sprint 12 Design: 접근성 VETO + 보안 강화

## 1. BE 보안 헤더 미들웨어

### 파일: `backend/app/main.py` (수정)

```python
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(self), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'"
    return response
```

## 2. FE Next.js 보안 헤더

### 파일: `frontend/next.config.ts` (수정)

```typescript
headers: async () => [{
  source: "/:path*",
  headers: [
    { key: "X-Content-Type-Options", value: "nosniff" },
    { key: "X-Frame-Options", value: "DENY" },
    { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
    { key: "Permissions-Policy", value: "camera=(), microphone=(self), geolocation=()" },
  ],
}]
```

## 3. CORS 강화

### 파일: `backend/app/main.py` (수정)

```python
allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
allow_headers=["Authorization", "Content-Type", "Accept"],
```

## 4. Rate Limiting

### 파일: `backend/app/core/rate_limit.py` (신규)

- slowapi 기반
- 일반 API: 60req/min
- AI API (writing, editing, design): 10req/min
- 키: IP 기반 (Authorization 헤더 우선)

## 5. axe-core 접근성 테스트

### 파일: `frontend/tests/accessibility/axe.test.tsx` (신규)

- vitest-axe 또는 jest-axe 사용
- 주요 페이지 렌더링 → axe 자동 분석
- WCAG 2.1 AA 레벨 위반 검출

## 6. 보안 테스트

### 파일: `backend/tests/test_security_headers.py` (신규)

- 보안 헤더 존재 확인
- CORS 헤더 검증
- Rate Limiting 429 응답 검증

## 파일 변경 목록

| 파일 | 유형 |
|------|------|
| backend/app/main.py | 수정 (보안 헤더 + CORS) |
| backend/app/core/rate_limit.py | 신규 |
| backend/tests/test_security_headers.py | 신규 |
| frontend/next.config.ts | 수정 (보안 헤더) |
| frontend/tests/accessibility/axe.test.tsx | 신규 |
