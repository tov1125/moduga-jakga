# Sprint 11 Design: E2E 실검증 + 커버리지 향상

## 설계 핵심

### FE 테스트 전략
1. **next/link mock 패턴**: jsdom에서 Next.js Link가 `<a>` 렌더링되지 않는 문제 → vi.mock으로 해결
2. **API 테스트 패턴**: mockFetch → mockResponse → assert URL/method/body
3. **페이지 테스트 패턴**: vi.mock으로 hooks(useSupabase, useAnnouncer) + next/navigation mock → render → assert

### BE 테스트 전략
1. **Service 유닛 패턴**: Settings mock + AsyncOpenAI mock → 비즈니스 로직 검증
2. **Supabase CRUD 패턴**: chain mock (table→select→eq→execute) → 반환값 검증
3. **외부 API mock**: httpx.AsyncClient mock (__aenter__/__aexit__) → 에러/성공 분기

### 커버리지 타겟
| 모듈 | Before | After | 전략 |
|------|:------:|:-----:|------|
| stt_service | 80% | 100% | 전체 흐름 (init→process→finalize→close) |
| supabase_service | 0% | 99% | CRUD + 도메인 쿼리 전수 |
| editing_service | 11% | 86% | 4단계 편집 각각 + full_review + _generate_summary |
| publishing_service | 35% | 54%+ | escape + DOCX/EPUB 생성 + start_export 에러 |
| design_service | 47% | 75% | 상수 검증 + _count_pdf_pages + generate_cover 에러 |
| tts_service | 80% | 90% | synthesize 성공/에러 |
| writing_service | 70% | 85% | generate_stream 정상 + rewrite |
| spelling_service | 78% | 87% | split_text + parse + apply_corrections |

## 파일 구조
```
frontend/tests/
├── components/
│   ├── Announcer.test.tsx (신규)
│   ├── Footer.test.tsx
│   ├── Header.test.tsx (수정)
│   └── Input.test.tsx (신규)
├── hooks/
│   └── useAnnouncer.test.tsx (신규)
├── lib/
│   └── api.test.ts (확장)
└── pages/
    ├── dashboard.test.tsx (신규)
    ├── home.test.tsx (신규)
    ├── login.test.tsx (신규)
    ├── privacy.test.tsx (신규)
    ├── settings.test.tsx (신규)
    ├── terms.test.tsx (신규)
    └── write.test.tsx (신규)

backend/tests/
└── test_services_unit.py (확장: 18→84 테스트)
    ├── TestWritingServiceUnit (5)
    ├── TestTTSServiceUnit (7)
    ├── TestSpellingServiceUnit (7)
    ├── TestEditingServiceUnit (14)
    ├── TestSupabaseServiceUnit (13)
    ├── TestPublishingServiceUnit (14)
    ├── TestDesignServiceUnit (7)
    ├── TestSupabaseServiceDomainUnit (7)
    ├── TestSTTServiceUnit (9)
    └── TestWritingServiceAdditional (1)
```
