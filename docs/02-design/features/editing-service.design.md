# Design: editing-service (4단계 편집 서비스 연동)

## 1. 아키텍처

### 1.1 컴포넌트 다이어그램
```
Client (curl / Frontend)
    │
    ▼
┌─────────────────────────────────────┐
│ FastAPI Router (editing.py)         │
│  POST /editing/proofread            │
│  POST /editing/style-check          │
│  POST /editing/structure-review     │
│  POST /editing/full-review  ← 수정  │
│  GET  /editing/report/{id}  ← 수정  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ EditingService (editing_service.py) │
│  proofread()                        │
│  check_style()                      │
│  review_structure()                 │
│  full_review()                      │
│  _final_review()                    │
└──────────────┬──────────────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
┌──────────────┐ ┌──────────────┐
│ OpenAI GPT-4o│ │ Supabase DB  │
│ (JSON mode)  │ │ editing_     │
│              │ │ reports 테이블│
└──────────────┘ └──────────────┘
```

### 1.2 데이터 플로우
```
[full-review 요청]
    │
    ├─ 1단계: review_structure() → flow_score, organization_score
    ├─ 2단계: check_style()      → consistency_score, issues
    ├─ 3단계: proofread()         → accuracy_score, corrections
    ├─ 4단계: _final_review()     → score, issues_count
    │
    ▼
[QualityReport 생성] → [editing_reports INSERT] → [응답 반환]
```

## 2. DB-API 매핑 설계

### 2.1 editing_reports 테이블 현재 구조

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | uuid | PK (auto) |
| book_id | uuid | FK → books |
| chapter_id | uuid (nullable) | FK → chapters |
| user_id | uuid | FK → profiles |
| stage | text | 편집 단계 ('full_review') |
| spelling_score | float8 | 3단계 교정 점수 |
| style_score | float8 | 2단계 문체 점수 |
| structure_score | float8 | 1단계 구조 점수 |
| readability_score | float8 | 4단계 최종검토 점수 |
| overall_score | float8 | 종합 점수 |
| issues | jsonb | 상세 이슈 데이터 |
| suggestions | jsonb | 권장사항 + 요약 |
| created_at | timestamptz | 생성 시각 |

### 2.2 DB ↔ QualityReport 매핑

```python
# [저장 시] QualityReport → DB INSERT 매핑
insert_data = {
    "book_id": report.book_id,
    "user_id": current_user["id"],
    "stage": "full_review",
    # 4단계별 개별 점수 매핑
    "structure_score": stage_scores.get("structure", 0.0),  # 1단계
    "style_score": stage_scores.get("content", 0.0),        # 2단계
    "spelling_score": stage_scores.get("proofread", 0.0),   # 3단계
    "readability_score": stage_scores.get("final", 0.0),    # 4단계
    "overall_score": report.overall_score,
    # jsonb 컬럼에 상세 데이터 저장
    "issues": {
        "stage_results": [sr.model_dump() for sr in report.stage_results],
        "total_issues": report.total_issues,
        "summary": report.summary,
    },
    "suggestions": report.recommendations,
}
```

```python
# [조회 시] DB row → QualityReport 매핑
report_data = db_row
stage_results_raw = report_data.get("issues", {}).get("stage_results", [])
stage_results = [
    StageResult(
        stage=EditingStage(sr["stage"]),
        score=sr["score"],
        issues_count=sr["issues_count"],
        feedback=sr["feedback"],
    )
    for sr in stage_results_raw
]

return QualityReport(
    book_id=report_data["book_id"],
    overall_score=report_data["overall_score"],
    stage_results=stage_results,
    total_issues=report_data.get("issues", {}).get("total_issues", 0),
    summary=report_data.get("issues", {}).get("summary", ""),
    recommendations=report_data.get("suggestions", []),
    created_at=str(report_data["created_at"]),
)
```

## 3. 수정 대상 파일 상세

### 3.1 `backend/app/api/v1/editing.py` — full_review 엔드포인트 수정

**변경 사항**: 편집 완료 후 결과를 editing_reports 테이블에 INSERT

```python
# 기존: report를 생성만 하고 반환
report = await editing_service.full_review(...)
return report

# 수정: report 생성 → DB 저장 → 반환
report = await editing_service.full_review(...)

# 4단계별 점수 추출
stage_scores = {}
for sr in report.stage_results:
    stage_scores[sr.stage.value] = sr.score

# DB 저장
insert_data = {
    "book_id": request.book_id,
    "user_id": current_user["id"],
    "stage": "full_review",
    "structure_score": stage_scores.get("structure", 0.0),
    "style_score": stage_scores.get("content", 0.0),
    "spelling_score": stage_scores.get("proofread", 0.0),
    "readability_score": stage_scores.get("final", 0.0),
    "overall_score": report.overall_score,
    "issues": {
        "stage_results": [sr.model_dump() for sr in report.stage_results],
        "total_issues": report.total_issues,
        "summary": report.summary,
    },
    "suggestions": report.recommendations,
}
supabase.table("editing_reports").insert(insert_data).execute()

return report
```

### 3.2 `backend/app/api/v1/editing.py` — get_quality_report 엔드포인트 수정

**변경 사항**: DB 조회 결과를 QualityReport로 올바르게 매핑

```python
# 기존: DB 컬럼명을 직접 사용 (stage_results 등이 없어서 실패)
# 수정: issues jsonb에서 stage_results 추출

report_data = report_resp.data[0]
issues_data = report_data.get("issues", {})
stage_results_raw = issues_data.get("stage_results", [])

stage_results = [
    StageResult(
        stage=EditingStage(sr["stage"]),
        score=sr["score"],
        issues_count=sr["issues_count"],
        feedback=sr["feedback"],
    )
    for sr in stage_results_raw
]

return QualityReport(
    book_id=report_data["book_id"],
    overall_score=report_data.get("overall_score", 0.0),
    stage_results=stage_results,
    total_issues=issues_data.get("total_issues", 0),
    summary=issues_data.get("summary", ""),
    recommendations=report_data.get("suggestions", []),
    created_at=str(report_data["created_at"]),
)
```

### 3.3 RLS 정책 확인

editing_reports 테이블에 필요한 RLS 정책:
- **SELECT**: `user_id = auth.uid()` (자신의 보고서만 조회)
- **INSERT**: `user_id = auth.uid()` (자신의 보고서만 생성)

> anon key로 INSERT 시 RLS 문제 발생 가능 → auth.py와 동일하게 확인 필요.
> 단, editing_reports INSERT는 인증된 사용자가 자신의 user_id로 생성하므로
> 기본 RLS 정책만으로 충분할 수 있음. 실제 테스트에서 확인.

## 4. 구현 순서

### Step 1: editing.py full_review DB 저장 로직 추가
- `import json` 추가 (이미 있을 수 있음)
- `TABLE_EDITING_REPORTS` import 추가
- full_review 엔드포인트에 INSERT 로직 삽입
- 에러 핸들링: DB INSERT 실패 시에도 report 반환 (경고 로그만)

### Step 2: editing.py get_quality_report DB 매핑 수정
- `StageResult`, `EditingStage` import 추가
- DB row → QualityReport 매핑 로직 교체

### Step 3: 실동작 검증 — 개별 엔드포인트
1. POST `/editing/proofread` — 한국어 텍스트 교정
2. POST `/editing/style-check` — 문체 분석
3. POST `/editing/structure-review` — 구조 검토

### Step 4: 실동작 검증 — full-review + report
1. POST `/editing/full-review` — 4단계 종합 편집 + DB 저장
2. GET `/editing/report/{book_id}` — 저장된 보고서 조회

### Step 5: E2E 워크플로우
1. 기존 테스트 도서에 챕터 내용 추가 (한국어 실제 글)
2. full-review 실행
3. report 조회 확인
4. 개별 편집 결과와 비교

## 5. 테스트 시나리오

### 5.1 proofread 테스트 데이터
```json
{
  "text": "오늘은 날씨가 너무 조아서 산책을 갔다. 바람이 시원하게 부러서 기분이 조았다.",
  "check_spelling": true,
  "check_grammar": true,
  "check_punctuation": true
}
```
**기대**: "조아서" → "좋아서", "부러서" → "불어서", "조았다" → "좋았다"

### 5.2 style-check 테스트 데이터
```json
{
  "text": "나는 산을 올랐다. I felt the wind on my face. 정상에서 바라본 풍경은 아름다웠다.",
  "genre": "essay"
}
```
**기대**: 한국어/영어 혼용 이슈 감지

### 5.3 full-review 테스트
```json
{
  "book_id": "6e05a90c-3fa8-412f-9980-d2a8f05cc734"
}
```
**기대**: 4단계 종합 보고서 + DB 저장 + 조회 성공

## 6. 성공 기준

| 항목 | 기준 |
|------|------|
| proofread | corrections 배열 반환, accuracy_score 0~100 |
| style-check | issues 배열 반환, consistency_score 0~100 |
| structure-review | flow_score + organization_score 반환 |
| full-review | 4개 StageResult + overall_score + DB 저장 |
| report 조회 | DB에서 최신 보고서 정상 조회, 모든 필드 매핑 |
| E2E | 도서→편집→보고서 전체 흐름 1회 완료 |

## 7. 변경 영향 범위

| 파일 | 변경 유형 | 영향도 |
|------|-----------|--------|
| `backend/app/api/v1/editing.py` | 수정 (2개 엔드포인트) | Medium |
| Supabase RLS (필요 시) | 정책 추가 | Low |
| 기존 다른 파일 | 변경 없음 | None |

> 서비스 레이어(editing_service.py)와 스키마(editing.py)는 수정 불필요.
> 라우터 레이어에서만 DB 저장/조회 매핑을 추가하면 됨.
