# Plan: editing-service (4단계 편집 서비스 연동)

## 1. 개요

### 1.1 피처 설명
시각장애인 작가가 작성한 글을 AI가 4단계 편집 체계로 검토하고 품질 보고서를 제공하는 서비스.
OpenAI GPT-4o를 사용하여 구조 편집, 내용 편집, 교정/교열, 최종 검토를 수행합니다.

### 1.2 배경
- Sprint 2에서 OpenAI 글쓰기 서비스(writing)가 실동작 검증 완료
- 편집 서비스 코드(API, Service, Schema)가 이미 구현되어 있으나 **실동작 미검증**
- 편집 결과를 DB에 저장하는 로직이 **누락**되어 있음

### 1.3 목표
1. 편집 서비스 4개 엔드포인트 실동작 검증 (OpenAI API 호출)
2. 편집 보고서 DB 저장 로직 구현 (editing_reports 테이블)
3. 전체 편집 워크플로우 E2E 테스트 (도서 생성 → 챕터 작성 → 4단계 편집 → 보고서 조회)

## 2. 현재 상태 분석

### 2.1 이미 구현된 코드

| 파일 | 상태 | 설명 |
|------|------|------|
| `backend/app/api/v1/editing.py` | 완성 | 5개 API 엔드포인트 |
| `backend/app/services/editing_service.py` | 완성 | 4단계 편집 로직 (OpenAI GPT-4o) |
| `backend/app/schemas/editing.py` | 완성 | Pydantic v2 Strict 스키마 |
| `backend/app/api/v1/router.py` | 완성 | `/editing` prefix 등록 |

### 2.2 API 엔드포인트 목록

| 엔드포인트 | 메서드 | 설명 | 실동작 |
|---|---|---|---|
| `/editing/proofread` | POST | 맞춤법/문법 교정 | 미검증 |
| `/editing/style-check` | POST | 문체 일관성 검사 | 미검증 |
| `/editing/structure-review` | POST | 구조 검토 | 미검증 |
| `/editing/full-review` | POST | 전체 4단계 편집 | 미검증 |
| `/editing/report/{book_id}` | GET | 품질 보고서 조회 | 미검증 |

### 2.3 발견된 Gap (결함)

#### Gap 1: 편집 보고서 DB 미저장 (Critical)
- `full_review` 엔드포인트가 QualityReport를 반환하지만 editing_reports 테이블에 저장하지 않음
- `get_quality_report` 엔드포인트는 editing_reports 테이블에서 읽으려 하지만 데이터가 없어 항상 404
- **수정 필요**: full_review 실행 후 결과를 editing_reports 테이블에 INSERT

#### Gap 2: editing_reports 테이블 구조 확인 필요
- Supabase에 editing_reports 테이블 존재 확인
- 컬럼 구조가 QualityReport 스키마와 일치하는지 확인
- RLS 정책 확인

#### Gap 3: 개별 편집 결과 히스토리 미관리
- proofread, style-check 등 개별 결과가 저장되지 않음
- Sprint 3에서는 full-review 보고서만 저장 (개별 결과 저장은 향후 과제)

## 3. 구현 계획

### Phase 1: DB 연동 (필수)
1. editing_reports 테이블 구조 확인 및 필요 시 마이그레이션
2. `editing.py` full_review 엔드포인트에 DB 저장 로직 추가
3. DB 저장 후 QualityReport 반환

### Phase 2: 실동작 검증 (필수)
1. POST `/editing/proofread` — 한국어 맞춤법/문법 교정 테스트
2. POST `/editing/style-check` — 문체 일관성 검사 테스트
3. POST `/editing/structure-review` — 구조 검토 테스트
4. POST `/editing/full-review` — 전체 4단계 편집 테스트 (도서+챕터 필요)
5. GET `/editing/report/{book_id}` — 저장된 보고서 조회 테스트

### Phase 3: E2E 워크플로우 검증
1. 로그인 → 도서 생성 → 챕터 2개 생성 (실제 글 내용)
2. 전체 4단계 편집 실행
3. 품질 보고서 조회 확인
4. 개별 편집(proofread, style-check) 추가 검증

## 4. 기술 상세

### 4.1 수정 대상 파일

| 파일 | 변경 사항 |
|------|-----------|
| `backend/app/api/v1/editing.py` | full_review에 DB 저장 로직 추가 |
| Supabase migration (필요 시) | editing_reports 테이블 컬럼 확인/수정 |

### 4.2 편집 보고서 DB 저장 구조
```python
# full_review 엔드포인트 수정
report = await editing_service.full_review(...)

# DB에 보고서 저장
report_data = {
    "book_id": request.book_id,
    "user_id": current_user["id"],
    "overall_score": report.overall_score,
    "stage_results": [sr.model_dump() for sr in report.stage_results],
    "total_issues": report.total_issues,
    "summary": report.summary,
    "recommendations": report.recommendations,
}
supabase.table("editing_reports").insert(report_data).execute()
```

### 4.3 의존성
- OpenAI API Key (이미 설정됨, 실동작 확인됨)
- Supabase editing_reports 테이블
- 테스트용 도서 + 챕터 (이미 생성됨: book_id=6e05a90c-...)

## 5. 성공 기준

| 기준 | 목표 |
|------|------|
| proofread 실동작 | 한국어 교정 결과 + corrections 배열 반환 |
| style-check 실동작 | 문체 이슈 + consistency_score 반환 |
| structure-review 실동작 | flow_score + organization_score 반환 |
| full-review 실동작 | 4단계 종합 QualityReport + DB 저장 |
| report 조회 | DB에서 최신 보고서 정상 조회 |
| 전체 E2E | 도서→챕터→편집→보고서 전체 흐름 완료 |

## 6. 리스크

| 리스크 | 대응 |
|--------|------|
| OpenAI JSON 응답 파싱 실패 | `response_format={"type": "json_object"}` 사용으로 최소화 |
| 긴 텍스트 토큰 초과 | 각 단계별 텍스트 길이 제한 (최대 3,000자 샘플) |
| editing_reports 테이블 구조 불일치 | Supabase에서 확인 후 필요 시 마이그레이션 |

## 7. 예상 소요

- Phase 1 (DB 연동): 1 cycle
- Phase 2 (실동작 검증): 1 cycle
- Phase 3 (E2E): 1 cycle
- **총 3 cycles**

## 8. 담당 에이전트

| 역할 | 에이전트 |
|------|----------|
| 총괄 | A0 Orchestrator |
| Backend 구현 | A4 Backend (bkit:bkend-expert) |
| AI 연동 | A7 AI 글쓰기 엔진 |
| 편집 도메인 | A8 편집/교열 |
| 품질 검증 | A16 품질 보증 (bkit:code-analyzer) |
