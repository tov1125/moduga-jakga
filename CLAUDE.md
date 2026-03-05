# 모두가 작가 - 시각장애인 작가 지원 웹 애플리케이션

## 프로젝트 개요

시각장애인도 글을 쓰는 작가가 될 수 있도록 돕는 웹 애플리케이션.
사용자가 STT(Speech to Text)로 대화하면 텍스트를 생성하고, AI가 이를 바탕으로 글을 작성하여 최종적으로 책으로 출판할 수 있는 구조.

> **핵심 가치**: "말하다 → 글이 되다 → 책이 되다 → 작가가 되다"

## 기술 스택

### Google Gemini 모델 사용 규칙 (필수 준수)

| 용도 | 모델 | 비고 |
|------|------|------|
| 책 디자인 (표지 생성, 디자인 서비스) | `gemini-2.5-flash` | design_service.py에서 사용 |
| 홈페이지 UI 리디자인 | `gemini-3.1-pro-preview` | 리디자인 전용, 다른 용도 사용 금지 |

> **주의**: 책 디자인 작업에 `gemini-3.1-pro-preview`를 사용하지 마세요. 반드시 `gemini-2.5-flash`를 사용합니다.

### Frontend
- **프레임워크**: Next.js (App Router)
- **언어**: TypeScript
- **핵심 요구사항**: 웹 접근성(WCAG 2.1 AA 이상), 스크린 리더 호환, 키보드 전용 탐색

### Backend
- **프레임워크**: FastAPI
- **타입 힌트**: Pydantic v2 기반 엄격한 타입 지정 필수
  - 모든 요청/응답 모델은 `BaseModel` 상속
  - `StrictStr`, `StrictInt` 등 Strict 타입 사용
  - `Field`로 제약 조건 명시 (min_length, ge, le 등)
- **언어**: Python 3.10+

```python
# 타입 힌트 규칙 예시
from pydantic import BaseModel, Field, StrictStr, StrictInt

class UserProfile(BaseModel):
    name: StrictStr = Field(..., min_length=1, max_length=50)
    age: StrictInt = Field(..., ge=0, le=150)
    disability_type: StrictStr
```

## 필요 역량 (15개 영역)

### 1. 서비스 기획
- 시각장애인 사용자 리서치 (전맹/저시력 등 장애 정도별 구분)
- 페르소나 정의 및 사용자 여정 맵
- 기능 정의서(PRD), 비즈니스 모델 설계
- 장애인차별금지법, 웹 접근성 인증, 개인정보보호법 이해

### 2. UI/UX 설계
- 접근성 중심 설계 (시각 의존도 최소화)
- 음성 기반 UX (Voice-First 원칙)
- 최소 단계 인터랙션 (Minimal Steps)
- 지속적 음성/소리 피드백 (Continuous Feedback)
- 스크린 리더 흐름을 고려한 와이어프레임/프로토타입 (Figma 등)

### 3. Frontend (Next.js + TypeScript)
- React/Next.js 컴포넌트 설계, SSR/CSR, App Router, API Routes
- TypeScript 타입 시스템, 인터페이스/제네릭
- WAI-ARIA, 스크린 리더 호환, 키보드 내비게이션
- Web Speech API 또는 외부 STT SDK 통합
- 음성 입력 → 텍스트 → AI 글 작성 흐름의 상태 관리

### 4. Backend (FastAPI + Pydantic)
- FastAPI 라우팅, 의존성 주입, 미들웨어, WebSocket
- Pydantic v2 BaseModel 기반 엄격한 스키마 정의
- DB 설계: 사용자/작품/세션 모델링 (SQLAlchemy 등)
- 인증/인가: JWT 또는 OAuth2

### 5. STT (Speech to Text)
- 한국어 인식률이 높은 서비스 선정 필수
- 후보: CLOVA Speech(네이버), Google Cloud STT, OpenAI Whisper, 카카오 음성인식
- 실시간 스트리밍 음성 전송 (WebSocket)

### 6. TTS (Text to Speech)
- 한국어 자연스러운 TTS (CLOVA Voice, Google TTS, Azure TTS 등)
- 낭독 제어: 속도 조절, 일시정지, 특정 문장 반복 재생
- 시스템 안내음 vs 글 낭독 음성 구분

### 7. AI 글쓰기 엔진
- LLM API 연동 (Claude API, OpenAI API 등)
- 대화 텍스트 → 문학적 글로 변환하는 프롬프트 엔지니어링
- SSE/WebSocket 기반 실시간 글 생성 스트리밍
- 맞춤법 교정, 문체 조정 후처리 파이프라인

### 8. 편집/교열
- 4단계 편집 체계:
  - 구조 편집: 전체 흐름, 챕터 구성, 논리 순서 검토
  - 내용 편집: 문장 다듬기, 문체 통일, 표현력 향상
  - 교정: 맞춤법, 띄어쓰기, 문법 오류 수정
  - 교열: 최종 조판 후 오탈자, 레이아웃 오류 확인
- 음성 기반 편집 UX: "세 번째 문단을 읽어줘" → 수정 제안 → 음성으로 선택
- 원고 품질 리포트: 맞춤법, 문체 일관성, 구조 완성도, 가독성 점수
- 도구: 네이버 맞춤법 검사기 API, py-hanspell, konlpy, LLM

### 9. 책 디자인
- **AI 모델: 반드시 `gemini-2.5-flash` 사용** (표지 이미지 생성, 디자인 관련 모든 작업)
- `gemini-3.1-pro-preview`는 홈페이지 UI 리디자인 전용 — 책 디자인에 절대 사용 금지
- 표지: AI 이미지 생성 + 장르별 템플릿 합성, 음성으로 선택/수정
- 내지 조판: LaTeX(XeLaTeX) 또는 Typst 기반 고품질 조판 (InDesign 85% 수준)
- 한글 폰트: 나눔명조, 본명조 등
- 판형: 신국판(152x225mm), 46판 등 한국 출판 표준
- 장르별 내지 템플릿: 에세이, 소설, 시, 자서전
- 인쇄 규격: CMYK, 재단선, 도련, 300dpi

### 10. 출판/유통
- 출력 포맷: DOCX(편집용), PDF(인쇄용/화면용), EPUB(전자책용)
- HWPX는 제외 — 포맷 복잡도 대비 라이브러리 지원 부족
- ISBN 발급 프로세스 (국립중앙도서관)
- 전자책 플랫폼: 리디북스, 밀리의서재, 교보문고, 알라딘
- POD(주문형 인쇄): 부크크, 교보POD
- Python 라이브러리: python-docx, WeasyPrint/ReportLab, ebooklib

### 11. 보안
- 음성 데이터 암호화 및 저장 정책
- 장애 정보는 민감 정보 — 별도 동의 필수 (개인정보보호법)
- OAuth2/JWT 기반 인증
- API Rate limiting, CORS, 입력값 검증

### 12. 테스트
- 단위/통합 테스트: pytest(BE), Jest/Vitest(FE)
- 접근성 자동 테스트: axe-core, Lighthouse
- 스크린 리더 수동 테스트: VoiceOver, TalkBack, NVDA
- 시각장애인 당사자 사용성 테스트

### 13. 법률/저작권
- AI 생성물 저작권 (AI가 작성한 글의 저자는 누구인가)
- 음성 데이터 수집/처리/보관 동의 절차
- 장애인차별금지법, 웹 접근성 의무
- AI 보조 글의 투고/출판 시 플랫폼별 제약 사항

### 14. 인프라/DevOps
- Docker: 프론트엔드/백엔드 컨테이너화
- CI/CD: GitHub Actions 등 자동 배포
- 클라우드: Vercel(FE) + AWS/GCP(BE)
- 모니터링: 오류 추적, 로깅

### 15. 프로젝트 관리
- 애자일/스크럼 기반 스프린트 개발
- Git 브랜치 전략, 코드 리뷰
- 이슈 관리: GitHub Issues 또는 Jira
- API 문서(Swagger), 접근성 가이드라인 문서화

## 아키텍처 흐름

```
시각장애인 사용자
    │ (음성 입력)
    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Next.js FE   │────▶│  FastAPI BE   │────▶│  STT 서비스   │
│  (TypeScript) │◀────│  (Pydantic)   │◀────│  (CLOVA 등)  │
└──────────────┘     └──────┬───────┘     └──────────────┘
    │                       │
    ▼                       ▼
┌──────────────┐     ┌──────────────┐
│  TTS 음성     │     │  AI LLM API  │
│  피드백       │     │  (글 작성)    │
└──────────────┘     └──────┬───────┘
                            │
                     ┌──────▼───────┐
                     │  편집/교열     │
                     │  (4단계 편집)  │
                     └──────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │   DOCX   │ │   PDF    │ │  EPUB    │
        │  편집용   │ │  출판용   │ │ 전자책용  │
        └──────────┘ └──────────┘ └──────────┘
```

## 개발 우선순위 로드맵

1. **1단계**: STT 서비스 선정 + 한국어 인식률 PoC
2. **2단계**: FastAPI 백엔드 뼈대 + Pydantic 모델 설계
3. **3단계**: Next.js 프론트엔드 + 접근성 기반 UI
4. **4단계**: AI 글쓰기 엔진 연동
5. **5단계**: 편집/교열 시스템 구축
6. **6단계**: 책 디자인 파이프라인 (표지 + 내지 조판)
7. **7단계**: 출판/유통 연동 (DOCX, PDF, EPUB 출력)
8. **8단계**: 접근성 테스트 + 실사용자 피드백

## 코딩 컨벤션

### Backend (Python/FastAPI)
- 모든 함수에 타입 힌트 필수
- Pydantic BaseModel로 모든 요청/응답 스키마 정의
- Strict 타입 우선 사용 (StrictStr, StrictInt 등)
- async/await 비동기 처리

### Frontend (TypeScript/Next.js)
- 모든 컴포넌트에 TypeScript 인터페이스 정의
- WAI-ARIA 속성 필수 적용
- 키보드 탐색 가능하도록 tabIndex, onKeyDown 처리

## 핵심 설계 원칙

1. **음성 우선 (Voice-First)**: 모든 주요 조작을 음성으로 가능하게
2. **최소 단계 (Minimal Steps)**: 목표까지 최소한의 인터랙션으로 도달
3. **지속적 피드백 (Continuous Feedback)**: 현재 상태를 항상 음성/소리로 안내
4. **엄격한 타입 안전성**: Pydantic Strict 타입으로 런타임 에러 사전 방지

## 에이전트 권한 계층 (Agent Authority Hierarchy)

> **최상위 권한 문서**: `agent.md`가 이 프로젝트의 에이전트 시스템 최상위 설계 문서이다.
> 모든 외부 에이전트 도구(bkit 등)는 agent.md의 에이전트 체계에 종속된다.

### 권한 순서 (Authority Order)

```
Level 0 (최상위): agent.md의 A0 Orchestrator — 전체 워크플로우 최종 결정권
Level 1 (감사권): agent.md의 A17 접근성 감사 — VETO(거부권) 보유
Level 1 (감사권): agent.md의 A16 품질 보증 — 품질 게이트 차단권
Level 1 (감사권): agent.md의 A18 사용자 대변인 — 사용자 관점 차단권
Level 2 (전문가): agent.md의 A1~A15 전문 에이전트 — 도메인별 실행 권한
Level 3 (도구):   bkit 에이전트 — Level 2 에이전트의 실행 도구로 동작
```

### 핵심 규칙

1. **agent.md 우선**: agent.md에 정의된 역할, 릴레이 프로토콜, 품질 게이트, 에스컬레이션 규칙이 bkit 에이전트의 기본 동작보다 우선한다.
2. **bkit은 실행 도구**: bkit 에이전트는 agent.md의 에이전트가 정의한 작업을 실행하는 도구(tool)로 사용된다. bkit 에이전트가 독자적으로 워크플로우를 결정하지 않는다.
3. **VETO 존중**: A17(접근성)의 거부권은 어떤 bkit 에이전트의 출력보다 우선한다. 접근성 기준 미달 시 배포/출판 불가.
4. **품질 게이트 적용**: bkit 에이전트의 모든 결과물은 agent.md의 5개 품질 게이트(코드/STT/글쓰기/책/접근성)를 통과해야 한다.
5. **릴레이 프로토콜 준수**: 에이전트 간 작업 전달은 agent.md의 릴레이 프로토콜(handoff/review_request/feedback/escalation)을 따른다.

### bkit → agent.md 바인딩 (실행 도구 매핑)

| agent.md 에이전트 | bkit 실행 도구 | 관계 |
|---|---|---|
| A0 Orchestrator | `bkit:cto-lead` | A0가 지시, cto-lead가 실행 |
| A1 기획 | `bkit:product-manager` | A1이 지시, PM이 실행 |
| A2 UI/UX | `bkit:frontend-architect` | A2가 지시, FA가 UI 설계 실행 |
| A3 Frontend | `bkit:frontend-architect` | A3이 지시, FA가 구현 실행 |
| A4 Backend | `bkit:bkend-expert` | A4가 지시, BE가 구현 실행 |
| A11 보안 | `bkit:security-architect` | A11이 지시, SA가 감사 실행 |
| A12 테스트 | `bkit:qa-strategist` + `bkit:qa-monitor` | A12가 지시, QA가 실행 |
| A14 인프라 | `bkit:infra-architect` | A14가 지시, IA가 구축 실행 |
| A15 프로젝트 | `bkit:pipeline-guide` | A15가 지시, PG가 안내 실행 |
| A16 품질 보증 | `bkit:code-analyzer` + `bkit:gap-detector` | A16이 지시, 분석/검증 실행 |
| A17 접근성 감사 | `bkit:design-validator` + `bkit:gap-detector` | A17이 지시, 검증 실행 |
| PDCA 반복 | `bkit:pdca-iterator` | A16 품질 미달 시 자동 반복 |
| 보고서 | `bkit:report-generator` | A15 요청 시 보고서 생성 |
| 아키텍처 전략 | `bkit:enterprise-expert` | A0 요청 시 전략 자문 |
