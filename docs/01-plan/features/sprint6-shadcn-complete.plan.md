# Plan: sprint6-shadcn-complete

## 개요

Sprint 5에서 생성한 11개 shadcn/ui 컴포넌트를 4개 consumer 파일에 완전 적용하고, 레거시 Modal.tsx를 삭제하며, 테스트 파일의 삭제된 Props를 수정한다.

## 배경

Sprint 5 Gap Analysis(95.1%)에서 식별된 6개 Gap:
- G-1: Modal.tsx 미삭제
- G-2: CoverDesigner.tsx — native select 유지
- G-3: EditingPanel.tsx — 수동 탭 구현 유지
- G-4: ExportPanel.tsx — native radio/checkbox 유지
- G-5: ChapterList.tsx — ScrollArea 미래핑
- G-6: Button 파일명 PascalCase (macOS 제약 — 해결 불가, 수용)

추가 발견: 테스트 파일에서 삭제된 Props 사용 (size="md", variant="danger")

## 목표

- Sprint 5 Gap 100% 해소 (G-6 제외)
- shadcn 컴포넌트 활용률: 11/11 (현재 1/11 Button만 적용)
- 테스트 전체 통과: Backend 170/170, Frontend 빌드 + 테스트 통과

## 작업 범위

### Phase 0: 테스트 수정 (선행, 5분)

| 파일 | 변경 | 라인 |
|------|------|------|
| tests/accessibility/axe-core.test.tsx | `size="md"` → `size="default"` | L23, L34, L64, L67, L70 (5건) |
| tests/accessibility/wcag-checklist.test.tsx | `variant="danger"` → `variant="destructive"` | L60 (1건) |

### Phase 1: CoverDesigner.tsx — Select 교체 (15분)

**현재**: native `<select>` 2개 (장르 L134-152, 스타일 L162-180)
**목표**: shadcn `Select` + `SelectTrigger` + `SelectValue` + `SelectContent` + `SelectItem`

교체 사항:
- 장르 선택 select → Select 컴포넌트 (GENRE_OPTIONS 데이터 그대로)
- 스타일 선택 select → Select 컴포넌트 (STYLE_OPTIONS 데이터 그대로)
- 커스텀 radiogroup (템플릿 선택) → 유지 (이미 접근성 완료)
- label-input 연결 유지 (htmlFor)

접근성 보존:
- `aria-label`, `role="region"` 유지
- min-h-touch 터치 타겟 유지
- 노란색 포커스 링 유지

### Phase 2: EditingPanel.tsx — Tabs + Badge 교체 (20분)

**현재**: 수동 button tablist (L84-111), inline span 배지 (L191-222)
**목표**: shadcn `Tabs`/`TabsList`/`TabsTrigger`/`TabsContent` + `Badge`

교체 사항:
- STAGE_ORDER 기반 수동 탭 → Tabs 컴포넌트
- suggestion.type 배지 (grammar/style/structure/content) → Badge variant
- 상태 배지 ("적용됨"/"거절됨") → Badge (default/destructive)

접근성 보존:
- Radix Tabs가 role="tablist"/role="tab"/aria-selected 자동 처리
- role="tabpanel" + aria-label 자동 처리
- 키보드 방향키 탐색 Radix 기본 제공

### Phase 3: ExportPanel.tsx — RadioGroup + Checkbox + Progress 교체 (20분)

**현재**: native radio (L131-169), native checkbox 2개 (L177-198), div progress (L238-252)
**목표**: shadcn `RadioGroup`/`RadioGroupItem` + `Checkbox` + `Progress` + `Label`

교체 사항:
- FORMAT_LABELS 기반 radio → RadioGroup + RadioGroupItem
- includeCover checkbox → Checkbox 컴포넌트
- includeToc checkbox → Checkbox 컴포넌트
- div progressbar → Progress 컴포넌트
- fieldset/legend 구조 유지

접근성 보존:
- Radix RadioGroup이 aria-checked 자동 처리
- Radix Checkbox가 aria-checked 자동 처리
- Radix Progress가 role="progressbar" + aria-valuemin/max/now 자동 처리
- role="status" + aria-live="polite" 유지

### Phase 4: ChapterList.tsx — ScrollArea 래핑 (5분)

**현재**: `<ol>` 직접 렌더링, 스크롤 처리 없음
**목표**: `<ScrollArea>` 래핑

교체 사항:
- `<ol>` 전체를 `<ScrollArea className="h-96">` 래핑
- 기존 키보드 내비게이션 (ArrowDown/Up/Home/End) 완전 유지
- useAnnouncer() 연동 유지

### Phase 5: Modal.tsx 삭제 (5분)

삭제 대상:
- `frontend/src/components/ui/Modal.tsx` — 삭제
- `frontend/tests/accessibility/modal.test.tsx` — 삭제 (있는 경우)

확인: Modal.tsx를 import하는 파일 없음 (Explore 에이전트 확인 완료)

### Phase 6: 검증 (10분)

- TypeScript 빌드: `cd frontend && npx tsc --noEmit`
- Frontend 빌드: `npm run build`
- Backend 테스트: `cd backend && ./venv/bin/pytest tests/ -v`
- Frontend 테스트: `cd frontend && npm run test:run`

## 수정 대상 파일 목록

| 파일 | 작업 | Phase |
|------|------|-------|
| tests/accessibility/axe-core.test.tsx | size="md" → size="default" (5건) | 0 |
| tests/accessibility/wcag-checklist.test.tsx | variant="danger" → variant="destructive" (1건) | 0 |
| components/book/CoverDesigner.tsx | native select → shadcn Select | 1 |
| components/editing/EditingPanel.tsx | 수동 탭 → shadcn Tabs + Badge | 2 |
| components/book/ExportPanel.tsx | native radio/checkbox → shadcn RadioGroup/Checkbox/Progress | 3 |
| components/writing/ChapterList.tsx | ScrollArea 래핑 | 4 |
| components/ui/Modal.tsx | 삭제 | 5 |

## 비수정 파일

- components/ui/Button.tsx — Sprint 5에서 완료
- components/ui/dialog.tsx — Sprint 5에서 생성 완료
- 나머지 shadcn 컴포넌트 — 변경 불필요

## 예상 소요 시간

| Phase | 작업 | 시간 |
|-------|------|------|
| 0 | 테스트 수정 | 5분 |
| 1 | CoverDesigner Select | 15분 |
| 2 | EditingPanel Tabs+Badge | 20분 |
| 3 | ExportPanel Radio+Checkbox+Progress | 20분 |
| 4 | ChapterList ScrollArea | 5분 |
| 5 | Modal 삭제 | 5분 |
| 6 | 검증 | 10분 |
| **합계** | | **~1.5시간** |

## 성공 기준

- [ ] native select/radio/checkbox 0개 (consumer 파일 기준)
- [ ] Modal.tsx 삭제 완료
- [ ] TypeScript 에러 0개
- [ ] Frontend 빌드 성공
- [ ] Backend 테스트 전체 통과
- [ ] 접근성 유지: 44px 터치, 노란 포커스 링, 18px 폰트, aria 속성
