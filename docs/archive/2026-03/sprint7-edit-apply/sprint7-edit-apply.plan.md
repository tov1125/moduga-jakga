# Sprint 7: 편집 제안 적용 + FE↔BE 통합 검증

## 개요

**Feature**: `sprint7-edit-apply`
**Phase**: Plan
**우선순위**: P0 (핵심 기능 갭)
**관련 에이전트**: A3 Frontend + A4 Backend + A8 편집 + A17 접근성 감사

## 문제 정의

### 핵심 갭: 편집 제안이 실제 텍스트에 적용되지 않음

`frontend/src/app/write/[bookId]/edit/page.tsx`의 `handleAcceptSuggestion`이 UI 상태(`accepted: true`)만 변경하고, **실제 챕터 텍스트에 수정을 반영하지 않음**.

```typescript
// 현재 코드 (line 132-137) — UI만 업데이트
const handleAcceptSuggestion = useCallback((suggestionId: string) => {
  setSuggestions((prev) =>
    prev.map((s) => (s.id === suggestionId ? { ...s, accepted: true } : s))
  );
}, []);
```

**사용자 영향**: 시각장애인 사용자가 "적용" 버튼을 누르면 TTS로 "적용됨"이라고 안내받지만, 실제 글은 변경되지 않음. **핵심 가치 "글이 되다"의 신뢰성 훼손**.

## 수정 범위

### 1. 편집 제안 적용 로직 구현

**파일**: `frontend/src/app/write/[bookId]/edit/page.tsx`

#### 1-A. 개별 제안 적용 (`handleAcceptSuggestion`)

제안 유형별 적용 전략:

| 단계 | 유형 | position 데이터 | 적용 방식 |
|------|------|:---------------:|----------|
| proofread/final | grammar | `{start, end}` 유효 | 위치 기반 텍스트 교체 |
| content | style | `{0, 0}` | `original` → `suggested` 문자열 검색 교체 |
| structure | structure | `{0, 0}`, original="" | 텍스트 교체 불가 — 참고용 피드백 |

```typescript
// 의사 코드
handleAcceptSuggestion(suggestionId) {
  const suggestion = suggestions.find(s => s.id === suggestionId);

  if (suggestion.type === "structure") {
    // 구조 제안은 참고용 — UI 상태만 변경
    setSuggestions(prev => mark accepted);
    return;
  }

  let updatedContent = activeChapter.content;

  if (suggestion.position.start > 0 || suggestion.position.end > 0) {
    // 위치 기반 교체 (proofread)
    updatedContent = content.slice(0, suggestion.position.start)
      + suggestion.suggested
      + content.slice(suggestion.position.end);
  } else if (suggestion.original) {
    // 문자열 검색 교체 (style)
    updatedContent = content.replace(suggestion.original, suggestion.suggested);
  }

  // 1) 로컬 상태 업데이트
  setActiveChapter({...activeChapter, content: updatedContent});

  // 2) 나머지 제안의 position 보정 (길이 변화분)
  adjustRemainingPositions(suggestions, suggestion, lengthDelta);

  // 3) UI 상태 업데이트
  setSuggestions(prev => mark accepted);

  // 4) BE 저장 (debounce)
  debouncedSave(bookId, activeChapter.id, updatedContent);

  // 5) 접근성 알림
  announcePolite("수정이 적용되었습니다");
}
```

#### 1-B. 전체 적용 (`handleAcceptAll`)

**전략**: position이 있는 제안은 **뒤에서 앞으로** 적용하여 위치 이동 방지.

```typescript
handleAcceptAll() {
  const pending = suggestions.filter(s => s.accepted === null && s.type !== "structure");

  // 위치 기반 제안: 뒤에서 앞으로 정렬
  const sorted = [...pending].sort((a, b) => b.position.start - a.position.start);

  let content = activeChapter.content;
  for (const s of sorted) {
    if (s.position.start > 0 || s.position.end > 0) {
      content = content.slice(0, s.position.start) + s.suggested + content.slice(s.position.end);
    } else if (s.original) {
      content = content.replace(s.original, s.suggested);
    }
  }

  setActiveChapter({...activeChapter, content});
  setSuggestions(prev => markAllAccepted);
  saveToBE(bookId, activeChapter.id, content);
  announcePolite(`${pending.length}개 수정이 모두 적용되었습니다`);
}
```

#### 1-C. 자동 저장 (debounce)

적용 후 BE 저장은 **500ms debounce**로 처리하여 연속 적용 시 요청 폭주 방지.

```typescript
const debouncedSave = useDebouncedCallback(
  async (bookId, chapterId, content) => {
    try {
      await chaptersApi.update(bookId, chapterId, { content });
      announcePolite("저장되었습니다");
    } catch {
      announceAssertive("저장에 실패했습니다. 다시 시도해주세요.");
    }
  },
  500
);
```

### 2. 챕터 콘텐츠 동기화

현재 `activeChapter`는 초기 로드 시점의 스냅샷이므로, 편집 적용 후 로컬 상태와 동기화 필요.

**변경 사항**:
- `activeChapter`의 `content`를 편집 적용 시 즉시 업데이트
- `chapters` 배열에서도 해당 챕터 content 동기화
- 챕터 전환 시 저장 확인 프롬프트 (미저장 변경이 있는 경우)

### 3. 접근성 (A17 VETO 기준)

| 요구사항 | 구현 |
|---------|------|
| 적용 결과 음성 알림 | `announcePolite("수정이 적용되었습니다")` |
| 저장 실패 알림 | `announceAssertive("저장에 실패했습니다")` |
| 구조 제안 구분 안내 | "구조 제안은 참고용입니다" 별도 안내 |
| 되돌리기 안내 | 적용 후 "되돌리기 가능합니다" 알림 |

## 수정 대상 파일

| 파일 | 변경 내용 | 영향도 |
|------|----------|:------:|
| `frontend/src/app/write/[bookId]/edit/page.tsx` | 핵심: 제안 적용 + 저장 로직 | HIGH |
| `frontend/src/components/editing/EditingPanel.tsx` | 구조 제안 "참고용" 표시 구분 | LOW |

## 테스트 계획

### 단위 테스트

1. **위치 기반 교체** — proofread 제안으로 텍스트 정확히 교체되는지
2. **문자열 검색 교체** — style 제안으로 original→suggested 교체
3. **전체 적용 역순** — 여러 제안 동시 적용 시 위치 꼬임 없음
4. **구조 제안 무교체** — structure 제안은 텍스트 변경 없음

### 통합 테스트

5. **저장 연동** — 적용 후 `chaptersApi.update()` 호출 확인
6. **챕터 전환** — 다른 챕터로 이동 시 이전 변경 보존
7. **접근성 알림** — aria-live 영역에 올바른 메시지 출력

## 의존성

- `frontend/src/lib/api.ts` — 이미 `chaptersApi.update()` 구현됨 ✅
- `backend/app/api/v1/editing.py` — 변경 불필요 ✅
- `frontend/src/types/book.ts` — `EditSuggestion.position` 타입 이미 존재 ✅

## 예상 소요

- 파일 수정: 1~2개
- 코드 변경: ~80줄
- 테스트: 기존 editing 테스트 확장
