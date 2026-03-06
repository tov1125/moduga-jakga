# 사용자 여정 시뮬레이션 보고서

> **작성일**: 2026-03-06
> **범위**: 회원가입 → 로그인 → 작품 생성 → 글쓰기 → 편집 → 검토 → 디자인 → 출판 → 설정
> **분석 대상**: Frontend 10개 페이지 + Backend 9개 API 모듈 + 공통 인프라

---

## 1. 요약

| 심각도 | 건수 | 주요 영역 |
|--------|:----:|----------|
| Critical | 3 | RLS 보안, STT 프로토콜/필드명 |
| High | 8 | 인증 흐름, 성능, 데이터 무결성, 검토/출판 |
| Medium | 18 | UX 개선, 에러 핸들링, 타입 불일치 |
| Low | 8 | 코드 품질, 미미한 UX |
| **총계** | **37** | |

---

## 2. Critical (즉시 수정)

### C-01. STT 결과 필드명 불일치 — STT 기능 전면 불가

| 항목 | 내용 |
|------|------|
| **위치** | `useSTT.ts` vs `stt.py` |
| **원인** | BE → `is_final` (snake_case), FE → `isFinal` (camelCase) |
| **증상** | `result.isFinal`이 항상 undefined → 최종 텍스트가 편집기에 반영 안 됨 |
| **수정** | FE에서 `result.is_final`로 변경 또는 BE에서 camelCase 전송 |

### C-02. STT WebSocket 프로토콜 불일치

| 항목 | 내용 |
|------|------|
| **위치** | `useSTT.ts` vs `stt.py` |
| **원인** | FE: `{ type: "auth", token }` / BE: `{ token }` (type 필드 무시). FE가 인증 응답을 기다리지 않고 config 즉시 전송 |
| **증상** | 간헐적 STT 연결 실패, 언어 코드 불일치 (`"ko"` vs `"ko-KR"`) |
| **수정** | FE에서 인증 응답 await 후 config 전송, 언어 코드 `"ko-KR"` 통일 |

### C-03. deps.py RLS 전면 우회 — 보안 방어선 제거

| 항목 | 내용 |
|------|------|
| **위치** | `backend/app/api/deps.py` |
| **원인** | `get_supabase`가 service_role 클라이언트를 반환 → RLS 완전 무력화 |
| **증상** | 현재 코드의 user_id 필터가 정상이면 동작하지만, 필터 누락 시 타 사용자 데이터 접근 가능 |
| **수정** | 장기적으로 RLS 정책을 service_role 호환으로 설계하거나, application-level 필터 검증 테스트 강화 |

---

## 3. High (금주 내 수정 권장)

| ID | 문제 | 위치 | 영향 |
|----|------|------|------|
| H-01 | JWT 토큰 만료 시 자동 리프레시 없음 | `api.ts` | 장시간 작업 중 401 → 데이터 유실 |
| H-02 | security.py가 anon client로 profiles 조회 | `security.py` | RLS 조건에 따라 인증 실패 가능 |
| H-03 | auth.users 전체 목록 순회 O(N) | `auth.py:74` | 사용자 증가 시 회원가입 타임아웃 |
| H-04 | Auth 계정↔profiles 불일치 시 교착 상태 | `auth.py` | 가입도 로그인도 불가 |
| H-05 | 오디오 형식 불일치 (WebM vs PCM) | `useSTT.ts` | CLOVA가 WebM 미지원 시 인식 실패 |
| H-06 | 검토 페이지 "전체 검토"가 이전 보고서만 조회 | `review/page.tsx:62` | 새 검토 실행 안 됨, 첫 검토 시 404 |
| H-07 | ExportResponse.file_size_bytes 타입 불일치 | `book.ts` | string vs number |
| H-08 | 다운로드 시 서버 파일 존재 확인 없음 | `publishing.py:193` | 파일 삭제 시 500 에러 |

---

## 4. Medium (다음 Sprint 수정)

| ID | 문제 | 위치 |
|----|------|------|
| M-01 | SSE 에러가 텍스트로 편집기에 삽입됨 | `api.ts` SSE 파서 |
| M-02 | 빈 prompt로 AI 생성 시 불명확한 에러 | `write/[bookId]/page.tsx` |
| M-03 | 미인증 사용자 대시보드/글쓰기 접근 시 불명확 | `dashboard/page.tsx`, `write/page.tsx` |
| M-04 | 로그인 후 refreshUser 실패 시 혼란 | `login/page.tsx` |
| M-05 | LoginRequest password min_length=8 | `schemas/auth.py` |
| M-06 | 비밀번호 강도 검증 없음 | `schemas/auth.py` |
| M-07 | 빈 content 편집 분석 시 에러 | `edit/page.tsx` |
| M-08 | debounced save 실패 시 재시도 없음 | `edit/page.tsx` |
| M-09 | 표지에 "작가" 대신 실제 필명 표시 | `design/[bookId]/page.tsx` |
| M-10 | fontFamily 설정이 API에 전달 안 됨 | `design/[bookId]/page.tsx` |
| M-11 | 표지 URL이 DB에 저장되지 않아 유실 | `CoverDesigner.tsx` |
| M-12 | 내보내기 상태 폴링 실패 무시 → 무한 대기 | `ExportPanel.tsx` |
| M-13 | 빈 displayName 저장 시 422 | `settings/page.tsx` |
| M-14 | API 응답 래핑 패턴 불일치 | `api.ts` |
| M-15 | 빈 챕터 배열로 구조 검토 시 무의미한 호출 | `edit/page.tsx` |
| M-16 | PaginatedResponse 구조 잠재적 불일치 | `dashboard/page.tsx` |
| M-17 | description undefined 전송 잠재적 422 | `write/page.tsx` |
| M-18 | 편집 빈 content 구조 검토 LLM 비용 | `edit/page.tsx` |

---

## 5. 사용자 여정별 흐름 검증 결과

### 5-1. 회원가입

```
[입력] → [FE 검증 (email, pw 8+, 약관)] → [POST /auth/signup]
  ├── 성공 → 로그인 페이지 이동 ✅
  ├── 409 중복 → "이미 가입된 이메일" + 로그인 링크 ✅ (신규)
  ├── profiles INSERT 실패 → auth 계정만 남는 교착 ⚠️ H-04
  └── auth.users 전체 순회 → 대규모 시 타임아웃 ⚠️ H-03
```

### 5-2. 로그인

```
[입력] → [POST /auth/login] → [토큰 저장] → [refreshUser] → [대시보드]
  ├── 성공 → localStorage에 access_token 저장 ✅
  ├── refreshUser 실패 → 대시보드에서 "로그인 필요" ⚠️ M-04
  └── 토큰 만료 → 자동 갱신 없음 ⚠️ H-01
```

### 5-3. 작품 생성

```
[제목+장르] → [POST /books] → [글쓰기 페이지 이동]
  ├── 성공 → /write/{bookId} 이동 ✅ (RLS 수정으로 정상화)
  ├── 미인증 → "작품 생성에 실패했습니다" (원인 불명) ⚠️ M-03
  └── RLS 우회로 INSERT 성공 ✅ (deps.py 수정 효과)
```

### 5-4. 글쓰기 (STT + AI 생성)

```
[음성 입력] → [WebSocket STT] → [텍스트 변환] → [AI 생성] → [챕터 저장]
  ├── STT: isFinal/is_final 불일치 → 최종 텍스트 미반영 🔴 C-01
  ├── STT: 오디오 형식 불일치 → 인식 실패 가능 ⚠️ H-05
  ├── AI 생성: SSE 에러가 텍스트로 삽입 ⚠️ M-01
  └── 저장: RLS 수정으로 정상 ✅
```

### 5-5. 편집

```
[교정/문체/구조 분석] → [제안 적용] → [자동 저장]
  ├── 분석: 빈 content 시 불명확 에러 ⚠️ M-07
  ├── 저장 실패: 재시도 없음 ⚠️ M-08
  └── 정상 흐름: RLS 수정으로 CRUD 동작 ✅
```

### 5-6. 검토

```
["전체 검토"] → editingApi.report(bookId) → 이전 보고서만 조회
  ├── 첫 검토: 보고서 없어 404 🔴 H-06
  └── 수정 필요: fullReview 호출로 변경
```

### 5-7. 표지 디자인

```
[표지 생성] → [Gemini AI] → [표지 URL]
  ├── 작가명: "작가"로 고정 ⚠️ M-09
  ├── 표지 URL: 페이지 이동 시 유실 ⚠️ M-11
  └── 생성 자체: 정상 ✅
```

### 5-8. 출판

```
[내보내기] → [폴링] → [다운로드]
  ├── 진행률: 하드코딩 50% ⚠️ Low
  ├── 폴링 실패: 무한 대기 ⚠️ M-12
  ├── 파일 미존재: 500 에러 ⚠️ H-08
  └── 정상 흐름: ✅
```

---

## 6. 우선 수정 로드맵

### Sprint 14-A: Critical 수정 (즉시)

1. **C-01**: `useSTT.ts` — `isFinal` → `is_final` 변경
2. **C-02**: `useSTT.ts` — 인증 응답 await + 언어 코드 통일
3. **H-01**: `api.ts` — 401 응답 시 로그인 리다이렉트 + "세션 만료" 안내

### Sprint 14-B: High 수정

4. **H-04**: `auth.py` — profiles 실패 시 auth 계정 롤백
5. **H-03**: `auth.py` — auth.users 전체 순회 제거 (profiles 중복 확인만 유지)
6. **H-06**: `review/page.tsx` — `editingApi.fullReview` 호출로 변경
7. **H-02**: `security.py` — admin client 사용으로 통일

### Sprint 14-C: Medium 수정

8. **M-01**: SSE 에러 파싱 개선
9. **M-09/M-11**: 표지 작가명 전달 + cover_url DB 저장
10. **M-03**: 미인증 자동 리다이렉트

---

## 7. 금일 수정 완료 사항

| 커밋 | 내용 |
|------|------|
| `d55b4a4` | 회원가입 중복 방지 3중 체크 (profiles + auth.users + INSERT 제약 조건) |
| `fe42c7b` | 중복 이메일 시 파란색 안내 박스 + "로그인하러 가기" 버튼 |
| `ebe51bf` | **deps.py → service role 전환으로 전체 API RLS 정상화** |

---

*보고서 끝*
