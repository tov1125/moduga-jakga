# A0 Orchestrator 종합보고서 생성

"종합보고서 작성해줘" 명령 시 이 스킬을 실행합니다.

## 트리거 키워드
- "종합보고서 작성해줘"
- "A0 보고서"
- "종합보고서"
- "/report-a0"

## 실행 절차

### Step 1: 프로젝트 현황 데이터 수집
다음 항목을 자동으로 수집합니다:

1. **PDCA 상태**: `docs/.pdca-status.json` 읽기
2. **코드베이스 규모**: Backend/Frontend 줄 수 계산
   - `backend/app/` 하위 전체 `.py` 파일
   - `frontend/src/` 하위 전체 `.tsx`, `.ts` 파일
3. **테스트 현황**: `backend/tests/`, `frontend/tests/` 테스트 파일 및 통과율
4. **Git 상태**: 미커밋 파일, 최근 커밋 이력
5. **아카이브 현황**: `docs/archive/` 완료된 PDCA 사이클

### Step 2: 에이전트별 분석 (A0~A18)
CLAUDE.md의 15개 역량 영역 + agent.md의 에이전트 체계를 기준으로:

| 에이전트 | 분석 대상 |
|---------|----------|
| A0 Orchestrator | 세션 수, PDCA 사이클 수, 릴레이 프로토콜 |
| A1 기획 | 페르소나, PRD, 비즈니스 모델 |
| A2 UI/UX | Voice-First 원칙, 스크린 리더 흐름 |
| A3 Frontend | 페이지/컴포넌트/Hook/Type/Lib 줄 수 |
| A4 Backend | API/Schema/Service/Agent/Model/Core 줄 수 |
| A5 STT | stt_service, useSTT, API endpoint |
| A6 TTS | tts_service, useTTS, VoicePlayer |
| A7 AI 글쓰기 | writing_service, writing_agent |
| A8 편집/교열 | editing_service, editing_agent, spelling |
| A9 책 디자인 | design_service, design_agent, CoverDesigner |
| A10 출판/유통 | publishing_service, ExportPanel |
| A11 보안 | security.py, deps.py, RLS |
| A12 테스트 | pytest 파일 수/줄 수, Vitest, axe-core |
| A13 법률/저작권 | 동의 절차, 이용약관 |
| A14 인프라 | Docker, CI/CD, 배포 설정 |
| A15 프로젝트 관리 | Git, PDCA, Sprint |
| A16 품질 보증 | Match Rate, Gap Analysis |
| A17 접근성 감사 | WCAG, axe-core, VoiceOver |
| A18 사용자 대변인 | user_advocate_agent |

각 에이전트별로 **수행 업무**와 **잔여 업무**를 구분하여 작성합니다.

### Step 3: DOCX 파일 생성
`docx/generate_a0_report.py` 스크립트를 실행하여 DOCX 파일을 생성합니다.

```bash
python3 docx/generate_a0_report.py
```

### Step 4: 버전 관리
파일명 형식: `AI_PJ_SF_A0 종합보고서_v{MAJOR}.{MINOR}.{PATCH}.docx`

| 변경 유형 | 버전 업 | 예시 |
|----------|--------|------|
| 단계(Sprint) 완료 | MAJOR (v1.0.0 → v2.0.0) | Sprint 2 완료 시 |
| 세부 내용 완료/추가 | MINOR (v0.1.0 → v0.2.0) | 에이전트 분석 추가 시 |
| 세세부 내용 변경 | PATCH (v0.0.1 → v0.0.2) | 오타 수정, 수치 갱신 시 |

**버전 규칙**:
- `generate_a0_report.py` 내 `output_path`의 버전 번호를 업데이트
- 이전 버전 파일은 삭제하지 않고 보존
- 최신 버전만 `generate_a0_report.py`의 기본 출력으로 설정

### Step 5: 보고서 포함 섹션 (필수)

1. **표지** — 프로젝트명, 보고 일자, 문서 버전
2. **목차**
3. **프로젝트 개요** — 기술 스택, 코드베이스 규모
4. **PDCA 사이클 현황** — 완료된 사이클 목록, 평균 Match Rate
5. **에이전트별 상세 분석** — A0~A18 수행/잔여 업무
6. **코드베이스 상세 규모** — API, Agent, Schema, Service, 테스트별 줄 수
7. **전체 진행률 요약** — 구조/테스트/연동/접근성/배포/법률
8. **긴급 조치 필요 사항** — P0~P3 우선순위
9. **다음 Sprint 권장 순서**
10. **A0 Orchestrator 판단** — 종합 평가 및 권고

### Step 6: 결과 보고
생성 완료 후 사용자에게 다음을 보고:
- 저장 경로
- 파일명 및 버전
- 포함된 섹션 수
- 주요 변경 사항 (이전 버전 대비)

## 주의사항
- 보고서 데이터는 **실시간 수집**합니다 (캐시 사용 금지)
- `generate_a0_report.py` 스크립트 내용도 데이터 변경 시 업데이트합니다
- DOCX 저장 위치는 항상 `docx/` 폴더입니다
- 이전 버전 파일은 삭제하지 않습니다
