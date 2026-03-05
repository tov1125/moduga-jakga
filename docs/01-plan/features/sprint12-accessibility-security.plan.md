# Sprint 12: 접근성 VETO + 보안 강화

## 목표
A17 접근성 감사 조건부 통과 항목 보완 + 보안 기초 강화

## 작업 항목

### 보안 강화
1. BE 보안 헤더 미들웨어 추가 (X-Content-Type-Options, X-Frame-Options, HSTS 등)
2. FE Next.js 보안 헤더 추가 (next.config.ts headers)
3. CORS allow_methods/allow_headers 제한
4. Rate Limiting 미들웨어 (slowapi 기반, AI API 분리 제한)
5. 보안 헤더/Rate Limiting 테스트

### 접근성 보강
6. axe-core 접근성 자동 테스트 추가 (vitest-axe)
7. 색상 대비 검증 테스트

## 성공 기준
- 보안 헤더 6종 적용
- Rate Limiting AI API 5req/min
- axe-core 자동 테스트 통과
- 기존 테스트 전부 통과
