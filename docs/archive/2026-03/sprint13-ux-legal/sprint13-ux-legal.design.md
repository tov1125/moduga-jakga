# Sprint 13 Design: UX 고도화 + 법률 + 베타 준비

## 1. 이용약관 페이지

### 파일: `frontend/src/app/terms/page.tsx` (신규)
- 시맨틱 HTML: `<article>`, `<h1>`, `<h2>`, `<section>`
- 내용: 서비스 이용약관, AI 생성물 저작권 조항 포함
- 접근성: heading 계층 구조, aria-label

## 2. 개인정보처리방침 페이지

### 파일: `frontend/src/app/privacy/page.tsx` (신규)
- 음성 데이터 수집/처리/보관 정책
- 장애 정보 민감정보 처리 조항
- 동일한 시맨틱 HTML 구조

## 3. 회원가입 동의 체크박스

### 파일: `frontend/src/app/(auth)/signup/page.tsx` (수정)
- shadcn Checkbox 3개:
  1. 이용약관 동의 (필수, /terms 링크)
  2. 개인정보처리방침 동의 (필수, /privacy 링크)
  3. AI 생성 글 저작권 정책 동의 (필수)
- 모두 체크해야 가입 버튼 활성화

## 4. 편집 Undo/Redo 기능

### 파일: `frontend/src/hooks/useEditHistory.ts` (신규)
```typescript
interface EditHistory {
  push(content: string): void;
  undo(): string | null;
  redo(): string | null;
  canUndo: boolean;
  canRedo: boolean;
}
```
- 히스토리 스택 최대 50개
- 키보드 단축키: Ctrl+Z (Undo), Ctrl+Shift+Z (Redo)

### 파일: `frontend/src/app/write/[bookId]/edit/page.tsx` (수정)
- handleAcceptSuggestion 전에 push(currentContent)
- Undo/Redo 버튼 (상단 툴바)
- aria-label="되돌리기", aria-label="다시 실행"

## 5. 에러 바운더리

### 파일: `frontend/src/components/ErrorBoundary.tsx` (신규)
- React Error Boundary 클래스 컴포넌트
- fallback UI: "오류가 발생했습니다. 새로고침해주세요."
- 접근성: role="alert", aria-live="assertive"

### 파일: `frontend/src/app/ClientLayout.tsx` (수정)
- ErrorBoundary로 최외곽 래핑

## 파일 변경 목록

| 파일 | 유형 |
|------|------|
| frontend/src/app/terms/page.tsx | 신규 |
| frontend/src/app/privacy/page.tsx | 신규 |
| frontend/src/app/(auth)/signup/page.tsx | 수정 |
| frontend/src/hooks/useEditHistory.ts | 신규 |
| frontend/src/app/write/[bookId]/edit/page.tsx | 수정 |
| frontend/src/components/ErrorBoundary.tsx | 신규 |
| frontend/src/app/ClientLayout.tsx | 수정 |
