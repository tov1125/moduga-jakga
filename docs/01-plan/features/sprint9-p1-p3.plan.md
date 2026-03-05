# Sprint 9 Plan: P1~P3 구현

## Context
Sprint 8까지 10회 PDCA 사이클(평균 97.24%)을 완료했다. A0 종합보고서 v3.0.0에서 식별한 P1~P3 긴급 조치 항목을 Sprint 9로 진행한다. P3의 "고대비 테마"는 사용자 요청에 따라 **다크모드**로 변경한다.

## 범위 (P1~P3)

| 우선순위 | 작업 | 담당 |
|---------|------|------|
| P1 | STT WebSocket 프로토콜 보완 (인증/설정 메시지) | A5 |
| P1 | Vercel 배포 설정 (Frontend) | A14 |
| P2 | 코드 커버리지 측정 및 보고 | A12 |
| P2 | VoiceOver 접근성 수동 테스트 체크리스트 | A17 |
| P2 | 편집 Undo 기능 구현 | A8 |
| P3 | 다크모드 토글 (next-themes + shadcn) | A3/A17 |
| P3 | 이용약관/개인정보처리방침/AI 저작권 동의 | A13 |

---

## Phase 1: 다크모드 (P3 — 기반 작업, 모든 후속 작업에 영향)

> 다크모드를 먼저 구현하는 이유: CSS 변수, 컴포넌트 dark: prefix가 이미 100% 준비되어 있어 최소 변경으로 완료 가능. 이후 추가되는 법률 페이지 등에 자동 적용됨.

### 1-1. next-themes 설치
```bash
cd frontend && npm install next-themes
```

### 1-2. tailwind.config.ts 수정
- `darkMode: "media"` → `darkMode: "class"` 변경 (next-themes의 class 기반 토글과 호환)
- **파일**: `frontend/tailwind.config.ts:11`

### 1-3. ThemeProvider 생성
- **새 파일**: `frontend/src/providers/ThemeProvider.tsx`
```tsx
"use client"
import { ThemeProvider as NextThemesProvider } from "next-themes"
import type { ReactNode } from "react"

export function ThemeProvider({ children }: { children: ReactNode }) {
  return (
    <NextThemesProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
      {children}
    </NextThemesProvider>
  )
}
```

### 1-4. layout.tsx 수정
- `<html>` 태그에 `suppressHydrationWarning` 추가
- **파일**: `frontend/src/app/layout.tsx:22`

### 1-5. ClientLayout.tsx 수정
- `ThemeProvider`를 최외곽에 감싸기
- **파일**: `frontend/src/app/ClientLayout.tsx`
```
<ThemeProvider>
  <SupabaseProvider>
    ...기존 구조...
  </SupabaseProvider>
</ThemeProvider>
```

### 1-6. ThemeToggle 컴포넌트 생성
- **새 파일**: `frontend/src/components/ui/ThemeToggle.tsx`
- `useTheme()` 훅으로 light/dark/system 전환
- 접근성: `aria-label="테마 변경"`, 키보드 조작 가능
- 아이콘: 해/달 SVG (system일 때 모니터 아이콘)

### 1-7. Header.tsx에 토글 배치
- 로고 옆 또는 사용자 메뉴 영역에 ThemeToggle 추가
- **파일**: `frontend/src/components/layout/Header.tsx`

---

## Phase 2: 법률/저작권 동의 (P3)

### 2-1. 이용약관 페이지
- **새 파일**: `frontend/src/app/terms/page.tsx`
- 내용: 서비스 이용약관 (AI 생성물 저작권 포함)
- 접근성: 시맨틱 HTML, heading 구조

### 2-2. 개인정보처리방침 페이지
- **새 파일**: `frontend/src/app/privacy/page.tsx`
- 내용: 음성 데이터 수집/처리/보관 정책, 장애 정보 민감정보 처리

### 2-3. 회원가입 동의 체크박스 추가
- **수정 파일**: `frontend/src/app/(auth)/signup/page.tsx`
- 3개 필수 체크박스:
  1. "이용약관에 동의합니다" (링크: /terms)
  2. "개인정보처리방침에 동의합니다" (링크: /privacy)
  3. "AI 생성 글의 저작권 정책에 동의합니다"
- shadcn Checkbox 컴포넌트 사용
- 동의하지 않으면 가입 버튼 비활성화

---

## Phase 3: STT WebSocket 프로토콜 보완 (P1)

### 3-1. useSTT.ts 프로토콜 메시지 추가
- **수정 파일**: `frontend/src/hooks/useSTT.ts`
- WebSocket 연결 후:
  1. 인증 메시지 전송: `{ type: "auth", token: accessToken }`
  2. 설정 메시지 전송: `{ type: "config", language: "ko" }`
- localStorage에서 `access_token` 읽기 (기존 api.ts 패턴 재사용)

---

## Phase 4: 편집 Undo 기능 (P2)

### 4-1. useEditHistory 커스텀 훅 생성
- **새 파일**: `frontend/src/hooks/useEditHistory.ts`
- 히스토리 스택 (최대 50개)
- `push(content)`: 스냅샷 저장
- `undo()`: 이전 상태 복원
- `redo()`: 다음 상태 복원
- `canUndo` / `canRedo`: boolean 상태

### 4-2. edit/page.tsx에 통합
- **수정 파일**: `frontend/src/app/write/[bookId]/edit/page.tsx`
- `handleAcceptSuggestion`과 `handleAcceptAll` 호출 전에 `push(currentContent)` 호출
- Undo/Redo 버튼 추가 (상단 툴바 영역)
- 키보드 단축키: `Ctrl+Z` (Undo), `Ctrl+Shift+Z` (Redo)
- 접근성: `aria-label="되돌리기"`, `aria-label="다시 실행"`

---

## Phase 5: Vercel 배포 설정 (P1)

### 5-1. Frontend Dockerfile 프로덕션 빌드
- **수정 파일**: `frontend/Dockerfile`
- Multi-stage build: `npm run build` → `npm start`

### 5-2. Vercel 프로젝트 설정
- `vercel.json` 생성 또는 Vercel CLI로 연결
- 환경변수: `NEXT_PUBLIC_API_URL` 설정
- API 리라이트: `/api/v1/*` → Backend URL

---

## Phase 6: 코드 커버리지 측정 (P2)

### 6-1. Frontend 커버리지 실행
```bash
cd frontend && npx vitest run --coverage
```
- 이미 vitest.config.ts에 threshold 80% 설정됨
- 결과 확인 및 미달 영역 식별

### 6-2. Backend 커버리지 실행
```bash
cd backend && ./venv/bin/pytest --cov=app --cov-report=term-missing
```
- 미커버 영역 식별

---

## Phase 7: VoiceOver 접근성 체크리스트 (P2)

### 7-1. 수동 테스트 체크리스트 문서
- **새 파일**: `docs/03-analysis/voiceover-checklist.md`
- 홈페이지 → 로그인 → 대시보드 → 글쓰기 → 편집 → 출판 경로별
- 각 페이지: 스크린 리더 읽기 순서, 키보드 탐색, aria-live 동작 확인

---

## 수정 파일 요약

| 파일 | 변경 유형 |
|------|----------|
| `frontend/tailwind.config.ts` | 수정 (darkMode: "class") |
| `frontend/src/app/layout.tsx` | 수정 (suppressHydrationWarning) |
| `frontend/src/app/ClientLayout.tsx` | 수정 (ThemeProvider 추가) |
| `frontend/src/providers/ThemeProvider.tsx` | **신규** |
| `frontend/src/components/ui/ThemeToggle.tsx` | **신규** |
| `frontend/src/components/layout/Header.tsx` | 수정 (토글 배치) |
| `frontend/src/app/terms/page.tsx` | **신규** |
| `frontend/src/app/privacy/page.tsx` | **신규** |
| `frontend/src/app/(auth)/signup/page.tsx` | 수정 (동의 체크박스) |
| `frontend/src/hooks/useSTT.ts` | 수정 (프로토콜 메시지) |
| `frontend/src/hooks/useEditHistory.ts` | **신규** |
| `frontend/src/app/write/[bookId]/edit/page.tsx` | 수정 (Undo/Redo) |
| `frontend/Dockerfile` | 수정 (프로덕션 빌드) |
| `docs/03-analysis/voiceover-checklist.md` | **신규** |

**신규 6개 / 수정 8개 = 총 14개 파일**

---

## 검증 계획

1. **다크모드**: `npm run dev` → 토글 클릭 → light/dark/system 전환 확인, 새로고침 후 테마 유지
2. **법률 페이지**: `/terms`, `/privacy` 접속 확인, 회원가입 시 체크박스 미체크 → 버튼 비활성화
3. **STT**: WebSocket 연결 → 콘솔에서 인증/설정 메시지 전송 확인
4. **Undo**: 편집 제안 수락 → Ctrl+Z → 원본 복원 확인
5. **Vercel**: `vercel deploy --prod` 또는 `vercel` CLI 배포 확인
6. **커버리지**: `vitest --coverage` → 80% 이상 확인
7. **테스트**: `npm run test` (vitest 96개) + `pytest` (169개) 전체 통과
8. **TypeScript**: `npx tsc --noEmit` → 0 errors
