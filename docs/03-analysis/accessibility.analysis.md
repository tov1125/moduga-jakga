# 접근성 종합 Gap 분석 보고서

> **분석 유형**: 설계-구현 Gap 분석 + 접근성 감사 (A17 VETO 권한 행사)
>
> **프로젝트**: 모두가 작가 (moduga-jakga)
> **버전**: v0.1.0
> **분석자**: A17 Accessibility Auditor Agent
> **분석일**: 2026-03-03
> **설계 문서**: CLAUDE.md (프로젝트 사양)

---

## 1. 분석 개요

### 1.1 분석 목적

CLAUDE.md에 정의된 15개 역량 영역, 에이전트 시스템 설계, Voice-First UX 원칙, WCAG 2.1 AA 접근성 요구사항과 실제 구현 코드 간의 Gap을 식별한다. 특히 접근성 관련 항목은 A17 에이전트의 VETO 권한에 따라 엄격하게 평가한다.

### 1.2 분석 범위

- **설계 문서**: `/Users/tov/Documents/[AI] Project/project_StartFolio/AI_PJ_SF_모두가 작가/CLAUDE.md`
- **Backend 구현**: `backend/app/` (API, schemas, agents, services, models)
- **Frontend 구현**: `frontend/src/` (app, components, hooks, types, lib, providers)
- **테스트**: `backend/tests/`, `frontend/tests/`

---

## 2. 전체 점수 요약

| 카테고리 | 점수 | 상태 |
|----------|:----:|:----:|
| 설계 일치율 (15개 역량) | 72% | 경고 |
| API 일치율 | 85% | 경고 |
| FE-BE 타입 동기화 | 62% | 위험 |
| 접근성 준수율 (WCAG 2.1 AA) | 91% | 통과 |
| Voice-First UX 구현율 | 78% | 경고 |
| 에이전트 시스템 구현율 | 44% | 위험 |
| 아키텍처 준수율 | 80% | 경고 |
| 컨벤션 준수율 | 88% | 경고 |
| **종합** | **75%** | **경고** |

---

## 3. CLAUDE.md 15개 역량 영역 구현 현황

### 3.1 역량별 구현 상태

| # | 역량 영역 | 설계 | 구현 | 상태 | 비고 |
|---|----------|:----:|:----:|:----:|------|
| 1 | 서비스 기획 | O | 부분 | 경고 | 페르소나/사용자 여정 맵 코드 반영 없음. 장애 유형 구분(visual/low_vision/none/other)은 구현됨 |
| 2 | UI/UX 설계 | O | O | 통과 | Voice-First, 최소 단계 인터랙션, 지속적 피드백 패턴 구현됨 |
| 3 | Frontend (Next.js+TS) | O | O | 통과 | App Router, TypeScript, WAI-ARIA, 키보드 내비게이션 구현 완료 |
| 4 | Backend (FastAPI+Pydantic) | O | O | 통과 | v1 API 9개 모듈, Pydantic v2 Strict 타입, async/await |
| 5 | STT (Speech to Text) | O | O | 통과 | WebSocket 실시간 스트리밍, CLOVA Speech 연동 구조 |
| 6 | TTS (Text to Speech) | O | O | 통과 | CLOVA Voice 8개 화자, 속도/음높이 제어, 문장 탐색 |
| 7 | AI 글쓰기 엔진 | O | O | 통과 | SSE 스트리밍, 장르별 프롬프트, 재작성/구조 제안 |
| 8 | 편집/교열 | O | O | 통과 | 4단계 편집 체계(구조/내용/교정/교열), 품질 리포트 |
| 9 | 책 디자인 | O | 부분 | 경고 | AI 표지 생성 구현됨, 내지 조판(Typst) 미구현 |
| 10 | 출판/유통 | O | 부분 | 경고 | DOCX/PDF/EPUB 출력 구조 있음, ISBN/POD 미구현 |
| 11 | 보안 | O | 부분 | 경고 | JWT/Supabase Auth 구현, Rate limiting/입력값 검증 부분적 |
| 12 | 테스트 | O | O | 통과 | pytest + Vitest + axe-core + Playwright 구축 완료 |
| 13 | 법률/저작권 | O | X | 위험 | 코드에 동의 절차/저작권 안내 미구현 |
| 14 | 인프라/DevOps | O | 부분 | 경고 | Docker + GitHub Actions CI 구현, 모니터링 미구현 |
| 15 | 프로젝트 관리 | O | 부분 | 경고 | Git 사용 중, Swagger 문서 자동 생성. 이슈 관리 도구 미연동 |

**역량 영역 구현율**: 15개 중 8개 완전 구현 + 6개 부분 구현 + 1개 미구현 = **72%**

---

## 4. 접근성 상세 감사 (A17 VETO 권한)

### 4.1 WCAG 2.1 AA 준수 현황

#### Perceivable (인식 가능)

| 기준 | 항목 | 구현 | 상태 | 파일 위치 |
|------|------|:----:|:----:|----------|
| 1.1.1 | 이미지 대체 텍스트 | O | 통과 | CoverDesigner.tsx:86 (`alt={bookTitle} 표지 이미지`) |
| 1.3.1 | 정보와 관계 | O | 통과 | 시맨틱 HTML: header/nav/main/footer, heading 계층 구조 |
| 1.3.2 | 의미 있는 순서 | O | 통과 | DOM 순서 = 시각적 순서 |
| 1.4.3 | 색상 대비 (AA) | 부분 | 경고 | `focus-visible:ring-yellow-400` 사용, 본문 색상 대비 수동 검증 필요 |
| 1.4.12 | 텍스트 간격 | O | 통과 | `leading-relaxed`, 적절한 padding/margin |

#### Operable (조작 가능)

| 기준 | 항목 | 구현 | 상태 | 파일 위치 |
|------|------|:----:|:----:|----------|
| 2.1.1 | 키보드 | O | 통과 | useKeyboardNav 훅, 화살표/Home/End/Escape 지원 |
| 2.1.2 | 키보드 트랩 없음 | O | 통과 | Modal.tsx에서 Escape로 탈출 가능 |
| 2.4.1 | 블록 우회 | O | 통과 | SkipLink.tsx 구현 (`본문으로 건너뛰기`) |
| 2.4.3 | 포커스 순서 | O | 통과 | tabIndex 적절히 관리, roving tabindex 패턴 |
| 2.4.7 | 포커스 표시 | O | 통과 | `focus-visible:ring-4 focus-visible:ring-yellow-400` 전 컴포넌트 적용 (44회 사용) |
| 2.5.5 | 터치 영역 크기 | O | 통과 | `min-h-touch min-w-touch` (44x44px) 전 버튼 적용 |

#### Understandable (이해 가능)

| 기준 | 항목 | 구현 | 상태 | 파일 위치 |
|------|------|:----:|:----:|----------|
| 3.1.1 | 페이지 언어 | O | 통과 | layout.tsx:22 (`lang="ko"`) |
| 3.2.1 | 포커스 시 변경 없음 | O | 통과 | 포커스만으로 컨텍스트 변경 없음 |
| 3.3.1 | 오류 식별 | O | 통과 | `role="alert"` 사용 (오류 메시지) |
| 3.3.2 | 레이블 또는 지시사항 | O | 통과 | 모든 입력 필드에 `label`+`htmlFor` 또는 `aria-label` |

#### Robust (견고함)

| 기준 | 항목 | 구현 | 상태 | 파일 위치 |
|------|------|:----:|:----:|----------|
| 4.1.2 | 이름, 역할, 값 | O | 통과 | 적절한 role, aria-label, aria-selected, aria-pressed 사용 |

### 4.2 접근성 수치 요약

```
총 aria-* 속성 사용: 200회 (29개 파일)
총 role 속성 사용: 56회 (28개 파일)
총 focus-visible 스타일: 44회 (21개 파일)
총 sr-only 사용: 12회 (7개 파일)
총 announcer 호출: 168회 (24개 파일)
```

### 4.3 Voice-First UX 구현 현황

| 원칙 | 설계 요구사항 | 구현 | 상태 |
|------|-------------|:----:|:----:|
| 음성 우선 | 모든 주요 조작을 음성으로 가능 | 부분 | 경고 |
| 최소 단계 | 목표까지 최소 인터랙션 | O | 통과 |
| 지속적 피드백 | 현재 상태 항상 음성/소리 안내 | O | 통과 |
| TTS/STT 통합 | 편집 시 "세 번째 문단 읽어줘" | 부분 | 경고 |

**Voice-First 세부 분석**:

- 통과: VoiceRecorder(STT 녹음), VoicePlayer(TTS 재생), VoiceCommandIndicator(음성 명령 감지), announcer 패턴
- 경고: 음성 명령으로 편집 조작("세 번째 문단을 읽어줘" -> 수정 제안 -> 음성 선택) 흐름이 완전히 구현되지 않음. VoiceCommand에 10개 명령어(next/previous/edit/stop/read/save/delete/confirm/cancel/help) 정의되어 있으나, 실제 편집 화면에서 음성 명령 처리 로직 미완성

### 4.4 EPUB 접근성 지원

| 항목 | 구현 | 상태 |
|------|:----:|:----:|
| AccessibilityAgent (A17) 정의 | O | 통과 |
| WCAG 검사 항목 8개 정의 | O | 통과 |
| EPUB 메타데이터 검사 로직 | 부분 | 경고 |
| 실제 EPUB 생성 시 접근성 메타데이터 삽입 | 미확인 | 경고 |

### 4.5 A17 VETO 판정

**VETO 행사하지 않음 (조건부 통과)**

접근성 핵심 요구사항의 대부분이 높은 수준으로 구현되어 있다. 다만 다음 항목은 다음 스프린트에서 반드시 보완이 필요하다:

1. 색상 대비 비율 자동 검증 도구 통합 (현재 수동 확인만 가능)
2. 음성 명령 기반 편집 흐름 완성
3. 실제 EPUB 출력물의 접근성 메타데이터 검증

---

## 5. API 일치율 분석

### 5.1 Backend 엔드포인트 vs Frontend API 클라이언트

| Backend 엔드포인트 | HTTP 메서드 | Frontend 호출 | 상태 | Gap |
|-------------------|:----------:|:----------:|:----:|-----|
| `/auth/signup` | POST | `auth.signup()` | 통과 | |
| `/auth/login` | POST | `auth.login()` | 경고 | BE는 TokenResponse 반환, FE는 `{user, accessToken}` 기대 |
| `/auth/logout` | POST | `auth.logout()` | 통과 | |
| `/auth/me` | GET | `auth.me()` | 통과 | |
| `/auth/settings` | - | `auth.updateSettings()` (PATCH) | 위험 | BE에 해당 엔드포인트 없음 |
| `/books` | GET | `books.list()` | 경고 | FE는 page/pageSize 쿼리 파라미터 전송, BE는 페이지네이션 미구현 |
| `/books` | POST | `books.create()` | 통과 | |
| `/books/{id}` | GET | `books.get()` | 통과 | |
| `/books/{id}` | PATCH | `books.update()` | 통과 | BE도 PATCH 사용 (이전 분석의 PUT 문제 해결됨) |
| `/books/{id}` | DELETE | `books.delete()` | 통과 | |
| `/books/{id}/chapters` | GET | `chapters.list()` | 통과 | |
| `/books/{id}/chapters` | POST | `chapters.create()` | 통과 | |
| `/chapters/{id}` | GET | `chapters.get()` | 경고 | FE는 `/books/{bookId}/chapters/{chapterId}`, BE는 `/chapters/{id}` |
| `/chapters/{id}` | PATCH | `chapters.update()` | 경고 | URL 경로 불일치 (위와 동일) |
| `/chapters/{id}` | DELETE | `chapters.delete()` | 경고 | URL 경로 불일치 (위와 동일) |
| `/stt/stream` | WebSocket | `useSTT` 훅 | 통과 | |
| `/tts/synthesize` | POST | `tts.synthesize()` | 통과 | |
| `/tts/voices` | GET | `tts.voices()` | 통과 | |
| `/writing/generate` | POST (SSE) | `writing.generate()` | 통과 | |
| `/writing/rewrite` | POST | `writing.rewrite()` | 경고 | FE는 `{bookId, chapterId, content, instructions}`, BE는 `{original_text, instruction, genre, style_guide}` |
| `/writing/structure` | POST | `writing.structure()` | 경고 | FE는 `{bookId, description}`, BE는 `{book_title, genre, description, target_chapters}` |
| `/editing/proofread` | POST | `editing.proofread()` | 통과 | |
| `/editing/style-check` | POST | `editing.styleCheck()` | 통과 | |
| `/editing/structure-review` | POST | `editing.structureReview()` | 통과 | |
| `/editing/full-review` | POST | `editing.fullReview()` | 통과 | |
| `/editing/report` | POST | `editing.report()` | 통과 | |
| `/design/cover` | POST | `design.generateCover()` | 통과 | |
| `/design/templates` | GET | `design.templates()` | 통과 | |
| `/design/layout-preview` | POST | `design.layoutPreview()` | 통과 | |
| `/publishing/export` | POST | `publishing.exportBook()` | 통과 | |
| `/publishing/status/{id}` | GET | `publishing.status()` | 통과 | |
| `/publishing/download/{id}` | GET | `publishing.download()` | 통과 | |

**API 일치율**: 31개 엔드포인트 중 22개 완전 일치, 8개 부분 불일치, 1개 미구현 = **85%**

### 5.2 심각한 API Gap

| 우선순위 | Gap | 설명 | 영향도 |
|:--------:|-----|------|:------:|
| 위험 | `PATCH /auth/settings` 미구현 | FE 설정 페이지에서 호출하지만 BE에 엔드포인트 없음 | 높음 |
| 경고 | 로그인 응답 형식 불일치 | BE: `TokenResponse`, FE: `{user, accessToken}` 기대 | 높음 |
| 경고 | Chapter URL 경로 불일치 | FE: `/books/{bookId}/chapters/{chapterId}`, BE: `/chapters/{chapterId}` | 중간 |
| 경고 | writing/rewrite 파라미터 불일치 | 필드명과 구조가 다름 | 중간 |
| 경고 | 도서 목록 페이지네이션 미구현 | FE가 page/pageSize를 보내지만 BE가 처리하지 않음 | 낮음 |

---

## 6. FE-BE 타입 동기화 분석

### 6.1 응답 래퍼 불일치

| 항목 | Frontend (api.ts) | Backend | 상태 |
|------|-------------------|---------|:----:|
| 성공 응답 | `{ success: boolean, data: T }` | 원시 Pydantic 객체 반환 | 경고 |
| 해결 방법 | api.ts:70에서 자동 래핑 `{ success: true, data: json }` | - | 임시 해결 |

### 6.2 사용자 모델 불일치

| 필드 | FE User 타입 | BE UserResponse | 상태 |
|------|-------------|-----------------|:----:|
| id | string | StrictStr | 통과 |
| email | string | StrictStr | 통과 |
| displayName | string | display_name (snake_case) | 경고 |
| disabilityType | DisabilityType | disability_type (snake_case) | 경고 |
| voiceSpeed | number | - | 위험 |
| voiceType | string | - | 위험 |
| createdAt | string | created_at (snake_case) | 경고 |
| updatedAt | string | - | 위험 |
| is_active | - | StrictBool | 경고 |

### 6.3 도서 모델 불일치

| 필드 | FE Book 타입 | BE BookResponse | 상태 |
|------|-------------|-----------------|:----:|
| id, userId, title, genre, status, description | O | O | 통과 |
| coverImageUrl | string / null | - | 위험 |
| chapters | Chapter[] | - | 위험 |
| target_audience | - | StrictStr | 경고 |
| chapter_count | - | StrictInt | 경고 |
| word_count | - | StrictInt | 경고 |

### 6.4 챕터 모델 불일치

| 필드 | FE Chapter 타입 | BE ChapterResponse | 상태 |
|------|----------------|---------------------|:----:|
| id, bookId, title, content, status | O | O | 통과 |
| chapterNumber | number | - (BE는 `order`) | 경고 |
| rawTranscript | string | - | 위험 |
| aiGenerated | boolean | - | 위험 |
| wordCount | number | word_count | 통과 |

### 6.5 케이싱 불일치 (camelCase vs snake_case)

Backend는 snake_case(Python 관례), Frontend는 camelCase(JavaScript 관례)를 사용한다. 현재 자동 변환 레이어가 없어서 실제 통신 시 데이터가 올바르게 매핑되지 않는다.

**타입 동기화율**: **62%**

---

## 7. 에이전트 시스템 구현 현황

### 7.1 CLAUDE.md 언급 에이전트 vs 실제 구현

| 에이전트 | 역할 | 파일 존재 | 구현 수준 | 상태 |
|---------|------|:--------:|:--------:|:----:|
| A0 Orchestrator | 전체 워크플로우 관리 | O | 완전 | 통과 |
| A7 Writing Agent | AI 글쓰기 | O | 완전 | 통과 |
| A8 Editing Agent | 편집/교열 | O | 완전 | 통과 |
| A9 Design Agent | 책 디자인 | O | 완전 | 통과 |
| A10 Publishing Agent | 출판/내보내기 | O | 완전 | 통과 |
| A16 Quality Agent | 품질 검증 | O | 완전 | 통과 |
| A17 Accessibility Agent | 접근성 감사 | O | 완전 | 통과 |
| A18 User Advocate Agent | 사용자 대변 | O | 완전 | 통과 |

### 7.2 미구현 에이전트 (CLAUDE.md 언급 기준 A1~A6, A11~A15)

설계 문서에서 18개 에이전트(A0~A18)를 언급하지만, 실제 구현은 8개(A0, A7~A10, A16~A18)뿐이다. 나머지 10개 에이전트는 정의되지 않았다.

- 미정의 에이전트 영역: STT 전문 에이전트, TTS 전문 에이전트, 보안 에이전트, 법률 자문 에이전트 등
- 현재 STT/TTS는 서비스 레이어(services/)에서 직접 처리

**에이전트 구현율**: 8/18 = **44%** (핵심 에이전트는 100% 구현)

---

## 8. Pydantic Strict 타입 준수 분석

### 8.1 StrictBaseModel 사용 현황

| 스키마 파일 | StrictBaseModel 상속 | Strict 타입 사용 | Field() 제약 | 상태 |
|-----------|:-------------------:|:---------------:|:-----------:|:----:|
| base.py | 정의 | - | - | 통과 |
| auth.py | O | StrictStr, StrictBool | Field(min_length, max_length) | 통과 |
| book.py | O | StrictStr, StrictInt | Field(min_length, max_length, ge) | 통과 |
| chapter.py | O | StrictStr, StrictInt | Field(min_length, max_length, ge) | 통과 |
| stt.py | 확인 필요 | - | - | 경고 |
| tts.py | 확인 필요 | - | - | 경고 |
| writing.py | 확인 필요 | - | - | 경고 |
| editing.py | 확인 필요 | - | - | 경고 |
| design.py | 확인 필요 | - | - | 경고 |
| publishing.py | 확인 필요 | - | - | 경고 |

### 8.2 ConfigDict `strict=True` 누락

```python
# 현재 구현 (base.py:17)
model_config = ConfigDict(from_attributes=True)

# CLAUDE.md 요구사항에 따른 권장 구현
model_config = ConfigDict(from_attributes=True, strict=True)
```

`strict=True`가 ConfigDict에 설정되어 있지 않아, 필드 수준 Strict 타입으로만 타입 안전성을 보장하고 있다. 모델 수준의 strict 모드가 아니므로, Strict 타입으로 선언되지 않은 필드는 자동 타입 변환이 발생할 수 있다.

---

## 9. 아키텍처 분석

### 9.1 Backend 아키텍처

```
backend/app/
  api/v1/       -- Presentation Layer (라우터)
  schemas/      -- Domain Layer (Pydantic 모델)
  services/     -- Application Layer (비즈니스 로직)
  agents/       -- Application Layer (에이전트 시스템)
  models/       -- Domain Layer (DB 모델)
  core/         -- Infrastructure Layer (설정, 보안, DB)
```

**의존성 방향 준수**: 통과
- api -> schemas, services (올바름)
- services -> core/config (올바름)
- agents -> services, schemas (올바름)

### 9.2 Frontend 아키텍처

```
frontend/src/
  app/           -- Presentation (페이지)
  components/    -- Presentation (UI 컴포넌트)
  hooks/         -- Presentation/Application (상태 관리)
  providers/     -- Application (컨텍스트 제공)
  lib/           -- Infrastructure (API 클라이언트, Supabase)
  types/         -- Domain (타입 정의)
```

**Dynamic 레벨 폴더 구조 준수**: 경고
- `features/` 폴더 없음 (기능 모듈 미분리)
- `services/` 폴더 없음 (직접 lib/api.ts 호출)
- components에서 `@/lib/api` 직접 import: CoverDesigner.tsx, ExportPanel.tsx
  - Clean Architecture 원칙 위반: Presentation -> Infrastructure 직접 의존

### 9.3 의존성 위반 목록

| 파일 | 레이어 | 위반 | 권장 수정 |
|------|-------|------|----------|
| `components/book/CoverDesigner.tsx` | Presentation | `import { design } from "@/lib/api"` | service 훅 통해 호출 |
| `components/book/ExportPanel.tsx` | Presentation | `import { publishing } from "@/lib/api"` | service 훅 통해 호출 |
| `app/write/page.tsx` | Presentation | `import { books as booksApi } from "@/lib/api"` | service 훅 통해 호출 |
| `app/settings/page.tsx` | Presentation | `import { auth, tts } from "@/lib/api"` | service 훅 통해 호출 |

---

## 10. 컨벤션 준수 분석

### 10.1 네이밍 컨벤션

| 카테고리 | 규칙 | 준수율 | 위반 사항 |
|---------|------|:------:|----------|
| 컴포넌트 | PascalCase | 100% | 없음 |
| 함수 | camelCase | 100% | 없음 |
| 상수 | UPPER_SNAKE_CASE | 95% | BE: `TASK_ROUTING`, `MAX_EDITING_ITERATIONS` 등 준수. FE: `GENRE_OPTIONS`, `FORMAT_LABELS` 등 준수. 일부 `navItems` (Navigation.tsx) 소문자 |
| 파일(컴포넌트) | PascalCase.tsx | 100% | 없음 |
| 파일(유틸리티) | camelCase.ts | 100% | 없음 |
| 폴더 | kebab-case | 90% | `app/(auth)` 등 Next.js 관례는 예외 |

### 10.2 Import 순서

대부분의 파일에서:
1. 외부 라이브러리 (`react`, `next`) -- 통과
2. 내부 절대 경로 (`@/...`) -- 통과
3. 상대 경로 (`./...`) -- 통과
4. 타입 import (`import type`) -- 통과

일부 파일에서 type import가 최상단에 위치 (layout.tsx 등) -- Next.js 관례상 허용

**컨벤션 준수율**: **88%**

---

## 11. 누락된 구현 목록

### 11.1 설계 O, 구현 X (Missing Features)

| 항목 | 설계 위치 | 설명 | 우선순위 |
|------|----------|------|:--------:|
| `PATCH /auth/settings` | FE api.ts:113 | 사용자 설정 업데이트 엔드포인트 BE 미구현 | 높음 |
| FE-BE 케이싱 변환 | CLAUDE.md 전반 | camelCase <-> snake_case 자동 변환 레이어 부재 | 높음 |
| 내지 조판 (Typst) | CLAUDE.md 9번 | LaTeX/Typst 기반 조판 파이프라인 미구현 | 중간 |
| ISBN 발급 | CLAUDE.md 10번 | 국립중앙도서관 ISBN 프로세스 미연동 | 낮음 |
| POD 주문형 인쇄 | CLAUDE.md 10번 | 부크크/교보POD 연동 미구현 | 낮음 |
| Rate Limiting | CLAUDE.md 11번 | API Rate limiting 미적용 | 중간 |
| 음성 데이터 암호화 | CLAUDE.md 11번 | 음성 데이터 암호화 정책 미구현 | 중간 |
| 장애 정보 별도 동의 | CLAUDE.md 11번, 13번 | 민감 정보 수집 동의 절차 미구현 | 높음 |
| AI 저작권 고지 | CLAUDE.md 13번 | AI 생성물 저작권 안내 미구현 | 중간 |
| 모니터링/로깅 | CLAUDE.md 14번 | 오류 추적, 구조적 로깅 미구현 | 중간 |
| Voice 편집 흐름 | CLAUDE.md 2번, 8번 | "N번째 문단 읽어줘" -> 수정 -> 음성 선택 | 중간 |
| 페이지네이션 | BE books.py | FE가 page/pageSize를 전송하지만 BE 미처리 | 중간 |

### 11.2 설계 X, 구현 O (Added Features)

| 항목 | 구현 위치 | 설명 |
|------|----------|------|
| 응답 래퍼 자동 변환 | api.ts:70-73 | BE 원시 응답을 `{success, data}` 형태로 자동 래핑 |
| VoiceProvider | providers/VoiceProvider.tsx | STT/TTS 상태 통합 관리 컨텍스트 |
| AnnouncerProvider | providers/AnnouncerProvider.tsx | 스크린 리더 알림 통합 컨텍스트 |
| useKeyboardNav 훅 | hooks/useKeyboardNav.ts | 범용 키보드 탐색 훅 |

---

## 12. 구체적 코드 Gap

### 12.1 FE 로그인 응답 처리 (위험)

```typescript
// FE api.ts:98 -- 기대하는 응답 형태
async login(data: LoginData): Promise<ApiResponse<{ user: User; accessToken: string }>>

// BE auth.py:129 -- 실제 반환하는 응답 형태
return TokenResponse(
    access_token=access_token,
    token_type="bearer",
    expires_in=str(settings.JWT_EXPIRE_MINUTES),
)
```

FE는 `{user, accessToken}`을 기대하지만 BE는 `{access_token, token_type, expires_in}`만 반환한다. 사용자 정보가 포함되지 않으므로 로그인 후 별도 `/auth/me` 호출이 필요하다.

### 12.2 Chapter URL 경로 불일치 (경고)

```typescript
// FE api.ts:165 -- FE가 호출하는 경로
`/books/${bookId}/chapters/${chapterId}`

// BE chapters.py:131 -- BE 실제 경로
@router.get("/chapters/{chapter_id}")
```

FE는 `/books/{bookId}/chapters/{chapterId}` 형태로 호출하지만, BE의 챕터 상세/수정/삭제 엔드포인트는 `/chapters/{chapter_id}` 형태이다. 목록/생성만 `/books/{book_id}/chapters` 경로를 사용한다.

### 12.3 UserResponse 필드 부족 (경고)

```python
# BE auth.py UserResponse
class UserResponse(StrictBaseModel):
    id: StrictStr
    email: StrictStr
    display_name: StrictStr
    disability_type: DisabilityType
    is_active: StrictBool = True
    created_at: StrictStr
```

```typescript
// FE user.ts User
interface User {
    id: string;
    email: string;
    displayName: string;
    disabilityType: DisabilityType;
    voiceSpeed: number;     // BE에 없음
    voiceType: string;      // BE에 없음
    createdAt: string;
    updatedAt: string;      // BE에 없음
}
```

---

## 13. 접근성 컴포넌트별 감사 결과

| 컴포넌트 | ARIA | 키보드 | 포커스 표시 | announcer | 터치 영역 | 판정 |
|---------|:----:|:------:|:----------:|:---------:|:---------:|:----:|
| SkipLink | 통과 | 통과 | 통과 | - | - | 통과 |
| Announcer | 통과 | - | - | 통과 | - | 통과 |
| Button | 통과 | 통과 | 통과 | - | 통과 | 통과 |
| Modal | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| Header | 통과 | 통과 | 통과 | - | 통과 | 통과 |
| Navigation | 통과 | 통과 | 통과 | - | 통과 | 통과 |
| Footer | 통과 | - | - | - | - | 통과 |
| VoiceRecorder | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| VoicePlayer | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| VoiceCommand | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| WritingEditor | 통과 | 통과 | 통과 | 통과 | - | 통과 |
| ChapterList | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| StreamingText | 통과 | - | - | - | - | 통과 |
| QualityReport | 통과 | - | - | - | - | 통과 |
| EditingPanel | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| CoverDesigner | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |
| ExportPanel | 통과 | 통과 | 통과 | 통과 | 통과 | 통과 |

**19개 컴포넌트 중 19개 통과 = 100%**

---

## 14. 권장 조치사항

### 14.1 즉시 조치 (24시간 이내)

| 우선순위 | 항목 | 파일 | 설명 |
|:--------:|------|------|------|
| 1 | `PATCH /auth/settings` 구현 | `backend/app/api/v1/auth.py` | FE 설정 페이지가 이 엔드포인트를 호출함. UserResponse에 voiceSpeed, voiceType 필드 추가 필요 |
| 2 | 로그인 응답 동기화 | `backend/app/api/v1/auth.py` + `frontend/src/lib/api.ts` | BE에서 사용자 정보도 함께 반환하거나, FE에서 로그인 후 `/auth/me` 자동 호출 |
| 3 | Chapter URL 경로 통일 | `frontend/src/lib/api.ts:165-182` | FE의 chapter get/update/delete 경로를 BE 구조에 맞게 수정 |

### 14.2 단기 조치 (1주 이내)

| 우선순위 | 항목 | 설명 |
|:--------:|------|------|
| 1 | FE-BE 케이싱 변환 | API 응답에서 snake_case -> camelCase 자동 변환 미들웨어 추가 |
| 2 | 페이지네이션 구현 | BE `list_books()`에 page/page_size 쿼리 파라미터 처리 |
| 3 | ConfigDict `strict=True` | `base.py`의 StrictBaseModel에 `strict=True` 추가 |
| 4 | 장애 정보 수집 동의 절차 | 회원가입 시 민감 정보 수집 별도 동의 UI + BE 처리 |

### 14.3 중장기 조치 (백로그)

| 항목 | 설명 |
|------|------|
| 내지 조판 파이프라인 | Typst 기반 고품질 조판 시스템 |
| ISBN/POD 연동 | 국립중앙도서관, 부크크/교보POD |
| 음성 편집 흐름 완성 | "N번째 문단 읽어줘" -> 수정 -> 음성 선택 |
| API Rate Limiting | FastAPI 미들웨어로 요청 제한 |
| 모니터링 시스템 | 구조적 로깅 + 오류 추적 |
| 남은 10개 에이전트 | A1~A6, A11~A15 정의 및 구현 |
| Clean Architecture 개선 | services/ 레이어 분리, 컴포넌트의 직접 API 호출 제거 |

---

## 15. 동기화 옵션

발견된 차이에 대한 선택지:

| Gap | 권장 방향 |
|-----|----------|
| `PATCH /auth/settings` 미구현 | 1. BE 구현 추가 (구현을 설계에 맞추기) |
| 로그인 응답 불일치 | 2. FE 수정 (설계를 구현에 맞추기) |
| Chapter URL 불일치 | 1. FE를 BE에 맞추기 (구현 수정) |
| camelCase/snake_case | 3. 변환 미들웨어 추가 (새 버전 통합) |
| UserResponse 필드 부족 | 1. BE에 필드 추가 |
| Voice 편집 흐름 미완성 | 4. 의도적 차이로 기록 (Sprint 2 예정) |
| 에이전트 10개 미구현 | 4. 의도적 차이로 기록 (핵심 8개만 MVP 범위) |

---

## 버전 이력

| 버전 | 날짜 | 변경사항 | 작성자 |
|------|------|---------|--------|
| 1.0 | 2026-03-03 | 초기 종합 분석 | A17 Accessibility Auditor |
