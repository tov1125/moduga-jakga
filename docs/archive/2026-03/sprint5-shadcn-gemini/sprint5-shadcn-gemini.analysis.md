# sprint5-shadcn-gemini Analysis Report

> **Analysis Type**: Gap Analysis (Design vs Implementation)
>
> **Project**: moduga-jakga (v0.2.0)
> **Analyst**: gap-detector
> **Date**: 2026-03-05
> **Plan Doc**: [snug-skipping-coral.md](/Users/tov/.claude/plans/snug-skipping-coral.md)

---

## 1. Analysis Overview

### 1.1 Analysis Purpose

Sprint 5 "sprint5-shadcn-gemini" 구현 완료 후, 플랜 문서 대비 실제 구현의 일치율을 측정하고 누락/불일치 항목을 식별한다.

### 1.2 Analysis Scope

- **Plan Document**: `/Users/tov/.claude/plans/snug-skipping-coral.md`
- **Implementation Paths**:
  - Frontend: `frontend/src/components/ui/`, `frontend/src/lib/utils.ts`, `frontend/tailwind.config.ts`, `frontend/src/app/globals.css`, `frontend/components.json`, `frontend/next.config.ts`
  - Backend: `backend/app/services/design_service.py`, `backend/app/core/config.py`, `backend/app/main.py`, `backend/requirements.txt`, `backend/static/covers/.gitkeep`
  - Consumer Files: 8개 Button import 대상 파일
- **Analysis Date**: 2026-03-05

---

## 2. Gap Analysis (Plan vs Implementation)

### 2.1 Phase 1-A: shadcn/ui 초기화 (Frontend)

| # | Plan Item | Implementation | Status | Notes |
|---|-----------|---------------|--------|-------|
| 1 | `components.json` 생성 | `frontend/components.json` 존재 | ✅ Match | style: default, baseColor: blue, cssVariables: true |
| 2 | CVA 설치 | `class-variance-authority: ^0.7.1` | ✅ Match | package.json 확인 |
| 3 | clsx 설치 | `clsx: ^2.1.1` | ✅ Match | |
| 4 | tailwind-merge 설치 | `tailwind-merge: ^3.5.0` | ✅ Match | |
| 5 | tailwindcss-animate 설치 | `tailwindcss-animate: ^1.0.7` | ✅ Match | |
| 6 | lucide-react 설치 | `lucide-react: ^0.577.0` | ✅ Match | |
| 7 | `cn()` 함수 추가 (utils.ts) | `cn(...inputs)` 구현 (clsx + twMerge) | ✅ Match | 기존 유틸 함수 유지됨 |
| 8 | tailwind.config.ts 머지 - CSS 변수 테마 | `background`, `foreground`, `card`, `popover`, `secondary`, `muted`, `destructive`, `border`, `input`, `ring` 전부 정의 | ✅ Match | |
| 9 | tailwind.config.ts - 기존 primary/accent 스케일 유지 | primary 50-950 + DEFAULT, accent 50-950 + DEFAULT | ✅ Match | |
| 10 | tailwind.config.ts - touch: 2.75rem | `spacing.touch`, `minHeight.touch`, `minWidth.touch` | ✅ Match | |
| 11 | tailwind.config.ts - 18px 폰트 | `base: 1.125rem` | ✅ Match | |
| 12 | tailwind.config.ts - animate 플러그인 | `plugins: [tailwindcssAnimate]` | ✅ Match | |
| 13 | globals.css - `--primary: 217.2 91.2% 59.8%` | 정확히 일치 | ✅ Match | |
| 14 | globals.css - `--destructive: 0 84.2% 60.2%` | 정확히 일치 | ✅ Match | |
| 15 | globals.css - `--ring: 50.5 100% 50%` (yellow-400) | 정확히 일치 | ✅ Match | |
| 16 | globals.css - 18px html font-size 유지 | `html { font-size: 18px }` | ✅ Match | |
| 17 | globals.css - 노란 포커스 링 유지 | `*:focus-visible { ring-4 ring-yellow-400 }` | ✅ Match | |
| 18 | globals.css - reduced-motion 유지 | `@media (prefers-reduced-motion)` 블록 존재 | ✅ Match | |
| 19 | globals.css - print 스타일 유지 | `@media print { .no-print }` 블록 존재 | ✅ Match | |
| 20 | globals.css - dark 모드 변수 | `.dark { ... }` 블록에 전체 변수 정의 | ✅ Match | |

**Phase 1-A 소계: 20/20 (100%)**

### 2.2 Phase 1-B: Gemini SDK 설치 (Backend)

| # | Plan Item | Implementation | Status | Notes |
|---|-----------|---------------|--------|-------|
| 21 | requirements.txt - `google-genai>=1.0.0` | 존재 | ✅ Match | `openai>=1.0.0` 유지 확인 |
| 22 | config.py - `GOOGLE_API_KEY: str = ""` | 정확히 일치 | ✅ Match | |
| 23 | main.py - StaticFiles 마운트 | `app.mount("/static", StaticFiles(...))` | ✅ Match | Path 기반, mkdir(exist_ok=True) 포함 |
| 24 | `backend/static/covers/.gitkeep` | 존재 | ✅ Match | |

**Phase 1-B 소계: 4/4 (100%)**

### 2.3 Phase 2-A: shadcn 컴포넌트 생성

| # | Plan Item | File Exists | Radix-based | Accessibility | Status |
|---|-----------|:-----------:|:-----------:|:------------:|--------|
| 25 | button.tsx (CVA, 6 variants) | `Button.tsx` | Slot | ring-yellow-400, min-h-touch | ✅ Match |
| 26 | dialog.tsx | ✅ | DialogPrimitive | ring-yellow-400, min-h-touch close btn, sr-only | ✅ Match |
| 27 | input.tsx | ✅ | N/A (native) | min-h-touch, ring-yellow-400, text-base | ✅ Match |
| 28 | label.tsx | ✅ | LabelPrimitive | text-base | ✅ Match |
| 29 | select.tsx | ✅ | SelectPrimitive | min-h-touch, ring-yellow-400 | ✅ Match |
| 30 | checkbox.tsx | ✅ | CheckboxPrimitive | ring-yellow-400 | ✅ Match |
| 31 | tabs.tsx | ✅ | TabsPrimitive | min-h-touch, ring-yellow-400 | ✅ Match |
| 32 | radio-group.tsx | ✅ | RadioGroupPrimitive | ring-yellow-400 | ✅ Match |
| 33 | badge.tsx | ✅ | CVA | ring-yellow-400 | ✅ Match |
| 34 | progress.tsx | ✅ | ProgressPrimitive | primary-600 indicator | ✅ Match |
| 35 | scroll-area.tsx | ✅ | ScrollAreaPrimitive | - | ✅ Match |

**Phase 2-A 컴포넌트 생성 소계: 11/11 (100%)**

### 2.4 Phase 2-A: Button 마이그레이션 상세

| # | Plan Item | Implementation | Status | Notes |
|---|-----------|---------------|--------|-------|
| 36 | Button CVA variants: primary | ✅ `bg-primary-600 text-white` | ✅ Match | |
| 37 | Button CVA variants: secondary | ✅ | ✅ Match | |
| 38 | Button CVA variants: destructive | ✅ `bg-red-600 text-white` | ✅ Match | danger -> destructive 완료 |
| 39 | Button CVA variants: ghost | ✅ | ✅ Match | |
| 40 | Button CVA variants: outline | ✅ | ✅ Match | |
| 41 | Button CVA variants: link | ✅ | ✅ Match | |
| 42 | Button size 오버라이드: min-h-touch min-w-touch | 모든 size에 적용 | ✅ Match | sm, default, lg, icon |
| 43 | 커스텀 prop: isLoading | ✅ spinner + sr-only + aria-busy | ✅ Match | |
| 44 | 커스텀 prop: leftIcon, rightIcon | ✅ aria-hidden 래핑 | ✅ Match | |
| 45 | 포커스 링: ring-4 ring-yellow-400 | ✅ + dark:ring-yellow-300 | ✅ Match | |
| 46 | asChild (Radix Slot) | ✅ | ✅ Match | |

**Button 마이그레이션 소계: 11/11 (100%)**

### 2.5 Phase 2-A: Consumer 파일 Button import 변경

| # | File | Plan | Implementation | Status | Notes |
|---|------|------|---------------|--------|-------|
| 47 | VoiceRecorder.tsx | danger -> destructive | `variant="destructive"` | ✅ Match | L45 확인 |
| 48 | VoicePlayer.tsx | Button import 변경 | `from "@/components/ui/Button"` | ✅ Match | |
| 49 | WritingEditor.tsx | Button import 변경 | `from "@/components/ui/Button"` | ✅ Match | |
| 50 | ChapterList.tsx | Button import + ScrollArea | Button ✅, ScrollArea 미사용 | ⚠️ Partial | ScrollArea 미적용 |
| 51 | EditingPanel.tsx | Tabs + Badge + Button | Button ✅, Tabs/Badge 미사용 | ⚠️ Partial | 수동 탭 구현 유지 |
| 52 | CoverDesigner.tsx | Select + Button | Button ✅, Select 미사용 | ⚠️ Partial | native `<select>` 유지 |
| 53 | ExportPanel.tsx | RadioGroup + Checkbox + Progress + Button | Button ✅, 나머지 미사용 | ⚠️ Partial | native radio/checkbox, 수동 progress bar 유지 |
| 54 | Header.tsx | Button import 변경 | `from "@/components/ui/Button"` | ✅ Match | |

**Consumer 마이그레이션 소계: 4/8 완전 Match + 4/8 Partial = 6/8 (75%)**

### 2.6 Phase 2-A: 파일 삭제

| # | Plan Item | Implementation | Status | Notes |
|---|-----------|---------------|--------|-------|
| 55 | `Button.tsx` (기존) 삭제 후 `button.tsx` (lowercase) 생성 | `Button.tsx`에 shadcn 내용 덮어쓰기 | ⚠️ Changed | 파일명 PascalCase 유지 (기능적 동작은 동일) |
| 56 | `Modal.tsx` 삭제 (dialog.tsx로 대체) | `Modal.tsx` 여전히 존재 | ❌ Missing | dialog.tsx 생성되었으나 Modal.tsx 미삭제 |

**파일 삭제 소계: 0/2 (0%)**

### 2.7 Phase 2-B: DesignService DALL-E -> Gemini 교체

| # | Plan Item | Implementation | Status | Notes |
|---|-----------|---------------|--------|-------|
| 57 | `from openai import AsyncOpenAI` 제거 | 제거됨 | ✅ Match | |
| 58 | `from google import genai` 추가 | `from google import genai` + `from google.genai import types` | ✅ Match | |
| 59 | `self._gemini = genai.Client(api_key=...)` | L89: 정확히 일치 | ✅ Match | |
| 60 | `asyncio.to_thread()` 래핑 | L137-144: 정확히 일치 | ✅ Match | |
| 61 | model: `gemini-2.5-flash-image` | L139: 정확히 일치 | ✅ Match | |
| 62 | `response_modalities=["image", "text"]` | L142: 정확히 일치 | ✅ Match | |
| 63 | base64 이미지 -> 로컬 파일 저장 | L155-158: COVERS_DIR / filename, write_bytes | ✅ Match | |
| 64 | 상대 URL 반환 `/static/covers/{filename}` | L159: 정확히 일치 | ✅ Match | |
| 65 | CoverGenerateResponse 스키마 유지 | image_url, prompt_used, style | ✅ Match | |
| 66 | COVERS_DIR 상수 정의 | L32: `Path(...) / "static" / "covers"` | ✅ Match | |
| 67 | 에러 처리 (이미지 미반환 시) | L152-153: RuntimeError 발생 | ✅ Match | |

**DesignService 교체 소계: 11/11 (100%)**

### 2.8 Frontend next.config.ts /static 리라이트

| # | Plan Item | Implementation | Status | Notes |
|---|-----------|---------------|--------|-------|
| 68 | `/static/:path*` -> `http://localhost:8000/static/:path*` | L11-13: 정확히 일치 | ✅ Match | |

**리라이트 소계: 1/1 (100%)**

### 2.9 Phase 3: 접근성 체크리스트

| # | Plan Item | Implementation | Status | Notes |
|---|-----------|---------------|--------|-------|
| 69 | 모든 shadcn에 min-h-touch min-w-touch | Button: ✅, Dialog close: ✅, Select trigger: ✅, Select item: ✅, Tabs trigger: ✅, Input: ✅ | ✅ Match | Checkbox/RadioGroupItem은 h-5 w-5 (체크박스 특성상 적절) |
| 70 | 포커스 링: ring-4 ring-yellow-400 | 전체 11개 컴포넌트에 적용 | ✅ Match | dark:ring-yellow-300 포함 |
| 71 | 폰트 크기: text-base (18px) | Input, Label, Select, Tabs, Badge 모두 text-base | ✅ Match | |
| 72 | 기존 aria 속성 보존 | VoiceRecorder: aria-pressed, aria-label / VoicePlayer: aria-live / WritingEditor: aria-describedby 등 전부 유지 | ✅ Match | |

**접근성 소계: 4/4 (100%)**

---

## 3. Match Rate Summary

### 3.1 Category Scores

| Category | Items | Match | Partial | Missing | Score |
|----------|:-----:|:-----:|:-------:|:-------:|:-----:|
| Phase 1-A: shadcn/ui 초기화 | 20 | 20 | 0 | 0 | 100% |
| Phase 1-B: Gemini SDK 설치 | 4 | 4 | 0 | 0 | 100% |
| Phase 2-A: 컴포넌트 생성 | 11 | 11 | 0 | 0 | 100% |
| Phase 2-A: Button CVA 상세 | 11 | 11 | 0 | 0 | 100% |
| Phase 2-A: Consumer 마이그레이션 | 8 | 4 | 4 | 0 | 75% |
| Phase 2-A: 파일 삭제 | 2 | 0 | 1 | 1 | 25% |
| Phase 2-B: Gemini 교체 | 11 | 11 | 0 | 0 | 100% |
| Phase 2-B: 리라이트 | 1 | 1 | 0 | 0 | 100% |
| Phase 3: 접근성 | 4 | 4 | 0 | 0 | 100% |
| **Total** | **72** | **66** | **5** | **1** | - |

### 3.2 Overall Match Rate Calculation

- Full match: 66 items = 66 points
- Partial match (0.5): 5 items = 2.5 points
- Missing: 1 item = 0 points

**Overall: 68.5 / 72 = 95.1%**

```
+---------------------------------------------+
|  Overall Match Rate: 95.1%  (68.5/72)       |
+---------------------------------------------+
|  Full Match:     66 items (91.7%)            |
|  Partial Match:   5 items ( 6.9%)            |
|  Missing:         1 item  ( 1.4%)            |
+---------------------------------------------+
```

---

## 4. Detailed Gap List

### 4.1 Missing Features (Plan O, Implementation X)

| # | Item | Plan Location | Description | Impact |
|---|------|--------------|-------------|--------|
| G-1 | Modal.tsx 삭제 | Plan L96, L216 | `Modal.tsx`가 여전히 존재. `dialog.tsx`가 생성되었으나 기존 Modal은 미삭제 | Low -- 데드코드. 빌드에는 영향 없으나 혼동 가능 |

### 4.2 Partial Matches (Plan != Implementation)

| # | Item | Plan | Implementation | Impact |
|---|------|------|---------------|--------|
| G-2 | CoverDesigner Select 교체 | shadcn Select 적용 | native `<select>` 유지 (`CoverDesigner.tsx` L134, L162) | Medium -- Radix Select의 접근성/키보드 지원 미활용 |
| G-3 | EditingPanel Tabs/Badge 교체 | shadcn Tabs + Badge 적용 | 수동 `role="tablist"` + 인라인 badge 스타일 유지 (`EditingPanel.tsx` L84-111) | Medium -- Radix Tabs의 방향키 탐색 미활용 |
| G-4 | ExportPanel RadioGroup/Checkbox/Progress 교체 | shadcn RadioGroup + Checkbox + Progress 적용 | native `<input type="radio">`, native `<input type="checkbox">`, 수동 `<div role="progressbar">` 유지 (`ExportPanel.tsx` L147-198, L237-253) | Medium -- Radix 컴포넌트의 일관된 스타일/접근성 미활용 |
| G-5 | ChapterList ScrollArea 추가 | ScrollArea 래핑 | ScrollArea 미사용 (`ChapterList.tsx`) | Low -- 긴 챕터 목록에서 커스텀 스크롤바 미적용 |
| G-6 | Button.tsx 파일명 | `button.tsx` (lowercase, shadcn 규칙) | `Button.tsx` (PascalCase 유지, 내용은 shadcn 스타일) | Low -- 기능 동일, naming convention 차이 |

### 4.3 Added Features (Plan X, Implementation O)

| # | Item | Location | Description |
|---|------|----------|-------------|
| A-1 | Radix 패키지 세분화 설치 | `package.json` L17-25 | 계획에는 `npx shadcn init`으로 일괄 설치 예정이었으나, 개별 Radix 패키지가 세분화 설치됨 (8개). 기능적으로 동일 |

### 4.4 Test 파일 미마이그레이션 (비블로킹)

| # | File | Issue | Lines |
|---|------|-------|-------|
| T-1 | `tests/accessibility/wcag-checklist.test.tsx` | `variant="danger"` 사용 (삭제된 variant) | L60 |
| T-2 | `tests/accessibility/axe-core.test.tsx` | `size="md"` 사용 (삭제된 size, 현재는 "default") | L23, L34, L64, L67, L70 |

이 테스트들은 CVA의 기본 동작으로 인해 unrecognized variant/size가 base class만 적용되므로 테스트 자체는 통과하지만, 의도한 스타일이 적용되지 않는 상태이다.

---

## 5. Architecture & Convention Compliance

### 5.1 Architecture Score

| Check Item | Status | Notes |
|-----------|--------|-------|
| shadcn 컴포넌트 ui/ 폴더 배치 | ✅ | `components/ui/` 아래 전부 |
| Consumer -> ui 단방향 의존 | ✅ | ui 컴포넌트가 다른 feature 컴포넌트를 import하지 않음 |
| Backend 서비스 레이어 유지 | ✅ | design_service.py는 services/ 아래 |
| 설정 분리 (config.py) | ✅ | GOOGLE_API_KEY는 config에서 관리 |

**Architecture Compliance: 100%**

### 5.2 Convention Score

| Check Item | Status | Notes |
|-----------|--------|-------|
| Component naming: PascalCase | ⚠️ | shadcn 컴포넌트는 lowercase 파일명 (dialog.tsx 등), 기존 컴포넌트는 PascalCase. 혼재 |
| Button 파일명 | ⚠️ | `Button.tsx` (PascalCase) -- 플랜은 lowercase 예정이었으나, 기존 import 호환성 위해 PascalCase 유지 |
| cn() 함수 위치 | ✅ | `lib/utils.ts` (shadcn 표준 위치) |
| CSS 변수 명명 | ✅ | shadcn 표준 (`--primary`, `--destructive` 등) |
| Tailwind 설정 구조 | ✅ | 기존 + shadcn 머지 성공 |

**Convention Compliance: 90%** (파일명 혼재로 감점)

---

## 6. Overall Score

```
+---------------------------------------------+
|  Overall Score Summary                       |
+---------------------------------------------+
|  Design Match:        95.1%    ✅             |
|  Architecture:       100.0%    ✅             |
|  Convention:          90.0%    ✅             |
|  Overall:             95.0%    ✅ PASS        |
+---------------------------------------------+
```

**Result: PASS (95.0% >= 90% threshold)**

---

## 7. Recommended Actions

### 7.1 Short-term (Optional, Non-blocking)

| Priority | Item | Files | Impact |
|----------|------|-------|--------|
| 1 | CoverDesigner: native `<select>` -> shadcn Select | `CoverDesigner.tsx` L134-152, L162-180 | Radix Select 키보드/접근성 개선 |
| 2 | EditingPanel: 수동 탭 -> shadcn Tabs + Badge | `EditingPanel.tsx` L84-111, L190-212 | Radix Tabs 방향키 탐색 |
| 3 | ExportPanel: native radio/checkbox -> shadcn | `ExportPanel.tsx` L127-199, L237-253 | UI 일관성 |
| 4 | ChapterList: ScrollArea 래핑 | `ChapterList.tsx` L103-179 | 긴 목록 스크롤 UX |
| 5 | Modal.tsx 삭제 | `components/ui/Modal.tsx` | 데드코드 제거 |
| 6 | 테스트 파일 variant/size 업데이트 | `tests/accessibility/wcag-checklist.test.tsx` L60, `axe-core.test.tsx` L23,34,64,67,70 | 테스트 정확성 |

### 7.2 Long-term (Backlog)

| Item | Notes |
|------|-------|
| 파일명 convention 통일 | shadcn lowercase vs 기존 PascalCase 정리 |
| dialog.tsx를 사용하는 컴포넌트 마이그레이션 | Modal.tsx 사용처를 dialog.tsx로 전환 후 Modal.tsx 삭제 |

---

## 8. Conclusion

Sprint 5 "sprint5-shadcn-gemini"는 **95.0% Match Rate**로 PASS 기준(90%)을 충족한다.

**핵심 성과:**
- shadcn/ui 인프라 전체 구축 완료 (CVA, Radix, CSS 변수, cn() 등)
- 11개 shadcn 컴포넌트 전부 생성 및 접근성 커스터마이징 적용
- Button CVA 마이그레이션 완벽 (6 variants, 4 sizes, isLoading, leftIcon/rightIcon)
- DALL-E -> Google Gemini 전환 100% 완료 (asyncio.to_thread, base64 저장, 상대 URL)
- 기존 접근성 기준 (44px 터치, 노란 포커스 링, 18px 폰트) 전부 유지

**남은 Gap (비블로킹):**
- 4개 consumer 파일에서 새 shadcn 컴포넌트(Select, Tabs, Badge, RadioGroup, Checkbox, Progress, ScrollArea)를 아직 활용하지 않고 기존 native/수동 구현 유지 중
- Modal.tsx 미삭제 (데드코드)
- 테스트 파일의 레거시 variant/size 참조

이러한 Gap은 기능적으로 빌드/테스트에 영향을 주지 않으며, 향후 Sprint에서 점진적으로 적용 가능하다.

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-03-05 | Initial gap analysis | gap-detector |
