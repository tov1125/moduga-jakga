# Sprint 11: E2E 실검증 + 커버리지 향상

## 목표
FE/BE 코드 커버리지를 실질적으로 향상시키고, 테스트 기반을 강화한다.

## 작업 항목

### FE 커버리지 향상 (29.67% → 50%+)
- [ ] Header.test.tsx: next/link mock 추가로 4개 실패 수정
- [ ] api.test.ts: editing, design, publishing, tts, writing 엔드포인트 42개 테스트
- [ ] useAnnouncer.test.tsx: 5개 테스트 (Provider 컨텍스트, 에러 처리)
- [ ] Announcer.test.tsx: 4개 테스트 (aria-live 모드)
- [ ] Input.test.tsx: 5개 테스트 (기본 렌더링, className 병합)
- [ ] terms.test.tsx: 4개 테스트 (이용약관 정적 페이지)
- [ ] privacy.test.tsx: 4개 테스트 (개인정보처리방침)
- [ ] home.test.tsx: 6개 테스트 (랜딩 페이지, CTA, 3단계 설명)
- [ ] write.test.tsx: 8개 테스트 (새 책 폼, 라디오 버튼, 장르 선택)
- [ ] dashboard.test.tsx: 5개 테스트 (인증 상태별 렌더링, 도서 목록)
- [ ] settings.test.tsx: 4개 테스트 (로딩/비인증/인증 상태)
- [ ] login.test.tsx: 6개 테스트 (로그인 폼 필드 및 접근성)

### BE 커버리지 향상 (41% → 60%+)
- [ ] EditingService 테스트: proofread, check_style, review_structure, full_review, _generate_summary, _final_review (14개)
- [ ] SupabaseService 테스트: CRUD 13개 + 도메인 쿼리 7개
- [ ] PublishingService 테스트: escape 함수, resolve_cover_path, start_export (DOCX/PDF/EPUB) (14개)
- [ ] DesignService 테스트: STYLE_KEYWORDS, GENRE_KEYWORDS, _count_pdf_pages, generate_cover 에러, layout_preview 폴백 (7개)
- [ ] STTService 테스트: initialize, parse_recognition_result, process_audio_chunk, send_recognition, finalize (9개)
- [ ] WritingService 추가: generate_stream 정상 케이스 (1개)

## 수정/신규 파일

### FE 신규 테스트 (10개)
| 파일 | 테스트 수 |
|------|:---------:|
| tests/components/Header.test.tsx | 7 (수정) |
| tests/lib/api.test.ts | 42 (수정) |
| tests/hooks/useAnnouncer.test.tsx | 5 |
| tests/components/Announcer.test.tsx | 4 |
| tests/components/Input.test.tsx | 5 |
| tests/pages/terms.test.tsx | 4 |
| tests/pages/privacy.test.tsx | 4 |
| tests/pages/home.test.tsx | 6 |
| tests/pages/write.test.tsx | 8 |
| tests/pages/dashboard.test.tsx | 5 |
| tests/pages/settings.test.tsx | 4 |
| tests/pages/login.test.tsx | 6 |

### BE 신규 테스트 (1개 파일)
| 파일 | 테스트 수 |
|------|:---------:|
| tests/test_services_unit.py | 84 (18→84) |

## 성공 기준
- FE 커버리지 ≥ 50%
- BE 커버리지 ≥ 60%
- FE 전체 테스트 통과 (276개)
- BE 전체 테스트 통과 (268개, 1 known failure 제외)
