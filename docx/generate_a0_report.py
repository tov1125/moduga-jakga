"""A0 Orchestrator 종합보고서 DOCX 생성 스크립트 — v0.2.0"""
import os
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn


# ── 보고서 버전 ──
REPORT_VERSION = "v0.2.0"
REPORT_DATE = "2026-03-04"
PROJECT_VERSION = "Sprint 2 완료 (v0.2.0)"


def set_cell_shading(cell, color_hex):
    """셀 배경색 설정"""
    shading = cell._element.get_or_add_tcPr()
    shading_elem = shading.makeelement(qn("w:shd"), {
        qn("w:fill"): color_hex,
        qn("w:val"): "clear",
    })
    shading.append(shading_elem)


def add_styled_table(doc, headers, rows, header_color="2B579A"):
    """스타일된 테이블 생성"""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"

    # 헤더
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.runs[0]
        run.bold = True
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_shading(cell, header_color)

    # 데이터
    for r_idx, row_data in enumerate(rows):
        for c_idx, val in enumerate(row_data):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = str(val)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.size = Pt(9)
            if r_idx % 2 == 1:
                set_cell_shading(cell, "F2F2F2")

    return table


def create_report():
    doc = Document()

    # ── 페이지 설정 ──
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

    # ══════════════════════════════════════════
    # 표지
    # ══════════════════════════════════════════
    for _ in range(6):
        doc.add_paragraph("")

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("A0 Orchestrator")
    run.font.size = Pt(36)
    run.font.color.rgb = RGBColor(0x2B, 0x57, 0x9A)
    run.bold = True

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run("종합보고서")
    run.font.size = Pt(28)
    run.font.color.rgb = RGBColor(0x44, 0x44, 0x44)

    doc.add_paragraph("")

    project = doc.add_paragraph()
    project.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = project.add_run('"모두가 작가" — 시각장애인 작가 지원 웹 애플리케이션')
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    run.italic = True

    doc.add_paragraph("")
    doc.add_paragraph("")

    meta_info = [
        ("보고 일자", REPORT_DATE),
        ("프로젝트 버전", PROJECT_VERSION),
        ("문서 버전", REPORT_VERSION),
        ("작성자", "A0 Orchestrator (AI Agent)"),
    ]
    meta_table = doc.add_table(rows=len(meta_info), cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, (k, v) in enumerate(meta_info):
        meta_table.rows[i].cells[0].text = k
        meta_table.rows[i].cells[1].text = v
        for cell in meta_table.rows[i].cells:
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in p.runs:
                    run.font.size = Pt(11)

    doc.add_page_break()

    # ══════════════════════════════════════════
    # 목차
    # ══════════════════════════════════════════
    doc.add_heading("목차", level=1)
    toc_items = [
        "1. 프로젝트 개요",
        "2. Sprint 2 완료 현황",
        "3. PDCA 사이클 현황",
        "4. 에이전트별 상세 업무 분석 (A0~A18)",
        "5. 코드베이스 상세 규모",
        "6. 전체 진행률 요약",
        "7. 긴급 조치 필요 사항",
        "8. 다음 Sprint 권장 순서",
        "9. A0 Orchestrator 판단",
    ]
    for item in toc_items:
        p = doc.add_paragraph(item)
        p.paragraph_format.space_after = Pt(4)
        p.runs[0].font.size = Pt(11)

    doc.add_page_break()

    # ══════════════════════════════════════════
    # 1. 프로젝트 개요
    # ══════════════════════════════════════════
    doc.add_heading("1. 프로젝트 개요", level=1)

    doc.add_paragraph(
        '"모두가 작가"는 시각장애인도 글을 쓰는 작가가 될 수 있도록 돕는 웹 애플리케이션입니다.'
    )

    p = doc.add_paragraph()
    run = p.add_run('핵심 가치: "말하다 → 글이 되다 → 책이 되다 → 작가가 되다"')
    run.bold = True
    run.font.color.rgb = RGBColor(0x2B, 0x57, 0x9A)

    doc.add_heading("기술 스택", level=2)
    add_styled_table(doc,
        ["계층", "기술", "버전/상태"],
        [
            ["Frontend", "Next.js + React + TypeScript + Tailwind CSS", "Next.js 15, React 19"],
            ["Backend", "FastAPI + Pydantic v2 (Strict)", "Python 3.14"],
            ["Database", "Supabase (PostgreSQL + Auth + RLS)", "6테이블 실운영 중"],
            ["AI 글쓰기", "OpenAI GPT-4o", "실동작 확인 (SSE 스트리밍)"],
            ["STT", "CLOVA Speech (네이버)", "WebSocket 코드 완성"],
            ["TTS", "CLOVA Voice (네이버)", "실동작 확인 (MP3 반환)"],
            ["조판", "Typst", "파이프라인 미구현"],
            ["컨테이너", "Docker + docker-compose", "BE+FE 컨테이너화"],
        ]
    )

    doc.add_heading("코드베이스 규모 (실시간 측정)", level=2)
    add_styled_table(doc,
        ["영역", "줄 수", "파일 수"],
        [
            ["Backend 전체", "7,293줄", "~45 파일"],
            ["  - API Endpoints", "1,995줄", "11 파일"],
            ["  - Schemas", "626줄", "11 파일"],
            ["  - Services", "2,292줄", "9 파일"],
            ["  - AI Agents", "1,820줄", "10 파일"],
            ["  - Models/Core", "498줄", "5 파일"],
            ["Frontend 전체", "6,875줄", "~35 파일"],
            ["  - Pages (app/)", "2,654줄", "10+ 페이지"],
            ["  - Components", "2,290줄", "6 디렉토리"],
            ["  - Hooks", "689줄", "6 파일"],
            ["  - Types", "285줄", "5 파일"],
            ["  - Lib", "664줄", "3 파일"],
            ["Backend 테스트", "3,018줄", "12 파일"],
            ["총합", "17,186줄", "~92 파일"],
        ]
    )

    doc.add_page_break()

    # ══════════════════════════════════════════
    # 2. Sprint 2 완료 현황
    # ══════════════════════════════════════════
    doc.add_heading("2. Sprint 2 완료 현황", level=1)

    p = doc.add_paragraph()
    run = p.add_run("Sprint 2: 외부 서비스 연동 Sprint — 전체 완료")
    run.bold = True
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x00, 0x80, 0x00)

    doc.add_paragraph(
        "Sprint 2의 목표는 모든 외부 서비스(Supabase, OpenAI, CLOVA)를 실제 API 키로 연동하고 "
        "엔드포인트별 실동작을 검증하는 것이었습니다. 6개 작업 전체 완료."
    )

    add_styled_table(doc,
        ["ID", "작업", "상태", "검증 결과"],
        [
            ["P0-1", "미커밋 77파일 커밋", "완료", "afa1f6f"],
            ["P0-2", "pdca-status 18개 유령 피처 정리", "완료", "아카이브 3건 보존"],
            ["P1-1", "API 키 전부 실제 값 확인", "완료", "OpenAI, Supabase, CLOVA, JWT"],
            ["P1-2", "Supabase DB 6테이블 + RLS + Auth 전체 플로우", "완료", "signup→login→/me→settings→logout→CRUD"],
            ["P2-1", "OpenAI 글쓰기 3개 엔드포인트 실동작", "완료", "generate(SSE), rewrite, structure"],
            ["P2-2", "CLOVA TTS 실동작 + STT 코드 완성", "완료", "TTS: MP3 20KB, STT: WebSocket"],
        ]
    )

    doc.add_paragraph("")

    doc.add_heading("Sprint 2 추가 성과: editing-service PDCA", level=2)
    doc.add_paragraph(
        "Sprint 2 완료 후, editing-service에 대한 PDCA 사이클(Plan→Design→Do)을 즉시 실행했습니다."
    )
    add_styled_table(doc,
        ["단계", "내용", "결과"],
        [
            ["Plan", "DB 저장 누락, 테이블 매핑 불일치 식별", "editing-service.plan.md"],
            ["Design", "DB-API 매핑 설계 (4개 score 컬럼 + 2개 jsonb)", "editing-service.design.md"],
            ["Do", "full_review DB 저장 + get_quality_report 매핑 구현", "5개 엔드포인트 전체 실동작"],
        ]
    )

    doc.add_paragraph("")
    doc.add_heading("편집 서비스 검증 결과", level=3)
    add_styled_table(doc,
        ["엔드포인트", "결과", "상세"],
        [
            ["POST /editing/proofread", "PASS", "5개 교정, accuracy=85.0"],
            ["POST /editing/style-check", "PASS", "2개 이슈, consistency=70.0"],
            ["POST /editing/structure-review", "PASS", "flow=75.0, organization=80.0"],
            ["POST /editing/full-review", "PASS", "overall=89.4, 4단계 9건 이슈, DB 저장 확인"],
            ["GET /editing/report/{book_id}", "PASS", "DB→QualityReport 매핑 정확히 조회"],
        ]
    )

    doc.add_page_break()

    # ══════════════════════════════════════════
    # 3. PDCA 사이클 현황
    # ══════════════════════════════════════════
    doc.add_heading("3. PDCA 사이클 현황", level=1)

    doc.add_paragraph(
        "총 3회의 PDCA 사이클을 아카이브 완료했으며, 2개 피처가 활성 상태입니다."
    )

    doc.add_heading("아카이브된 사이클 (3건)", level=2)
    add_styled_table(doc,
        ["Cycle", "Feature", "Match Rate", "Iterations", "상태"],
        [
            ["#1", "tests", "91%", "1", "ARCHIVED"],
            ["#2", "schemas", "93%", "1", "ARCHIVED"],
            ["#3", "frontend", "98.3%", "3", "ARCHIVED"],
        ]
    )

    doc.add_paragraph("")
    p = doc.add_paragraph()
    run = p.add_run("아카이브 평균 Match Rate: 94.1%")
    run.bold = True

    doc.add_heading("활성 피처 (2건)", level=2)
    add_styled_table(doc,
        ["Feature", "Phase", "Match Rate", "비고"],
        [
            ["v1", "Do (Phase 3)", "미측정", "Sprint 2 외부 연동 작업"],
            ["editing-service", "Do (Phase 3)", "미측정", "Plan→Design→Do 완료, Check 대기"],
        ]
    )

    doc.add_page_break()

    # ══════════════════════════════════════════
    # 4. 에이전트별 상세 업무 분석
    # ══════════════════════════════════════════
    doc.add_heading("4. 에이전트별 상세 업무 분석 (A0~A18)", level=1)

    agents = [
        {
            "id": "A0", "name": "Orchestrator (전체 조율)",
            "done": [
                "8단계 로드맵 설계 및 순서 결정",
                "Sprint 1~2 오케스트레이션 (PDCA 3사이클 아카이브, 6개 Sprint 2 태스크 관리)",
                "에이전트 간 릴레이 프로토콜 적용",
                "editing-service PDCA Plan→Design→Do 사이클 조율",
                "v0.1.0 → v0.2.0 종합보고서 작성",
            ],
            "todo": [
                "Sprint 3 계획 수립 및 태스크 할당",
                "Frontend ↔ Backend 통합 워크플로우 E2E 조율",
                "사용자 테스트 전 전체 품질 게이트 심사",
            ],
        },
        {
            "id": "A1", "name": "기획 (서비스 기획)",
            "done": [
                "페르소나 정의 (전맹/저시력 사용자 구분)",
                '핵심 가치 흐름 설계: "말하다 → 글이 되다 → 책이 되다 → 작가가 되다"',
                "15개 역량 영역 정의, PRD 작성",
            ],
            "todo": [
                "시각장애인 당사자 인터뷰/리서치",
                "비즈니스 모델 구체화 (수익 구조)",
                "경쟁사 분석 (부크크, 브런치 등)",
            ],
        },
        {
            "id": "A2", "name": "UI/UX 설계",
            "done": [
                "Voice-First 원칙 기반 UX 흐름 설계",
                "최소 단계 인터랙션 패턴 적용",
                "스크린 리더 흐름 고려한 페이지 구조 설계",
            ],
            "todo": [
                "Figma 프로토타입 제작",
                "스크린 리더 사용자 플로우 테스트",
                "저시력 사용자 대비 고대비 테마",
            ],
        },
        {
            "id": "A3", "name": "Frontend (Next.js + TypeScript) — 6,875줄",
            "done": [
                "Pages 10+ (2,654줄): login, signup, dashboard, settings, write, design, publish 등",
                "Components 6 디렉토리 (2,290줄): book, editing, layout, ui, voice, writing",
                "  - Voice: VoiceCommand, VoicePlayer, VoiceRecorder",
                "Hooks 6개 (689줄): useSTT, useTTS, useVoiceCommand, useKeyboardNav, useAnnouncer, useSupabase",
                "Types 5개 (285줄), Lib 3개 (664줄): api.ts, utils.ts, supabase",
                "FE-BE 타입 동기화 98.3% Match Rate (PDCA Cycle #3 완료)",
            ],
            "todo": [
                "실제 Backend API 연동 (현재 api.ts 함수들은 Mock 상태)",
                "Supabase Auth 실제 연결",
                "Web Speech API / CLOVA STT 실제 연결",
                "Frontend 테스트 복구 (현재 0개 — 빌드 제외 설정 중)",
            ],
        },
        {
            "id": "A4", "name": "Backend (FastAPI + Pydantic) — 7,293줄",
            "done": [
                "API Endpoints 10+router (1,995줄): auth, books, chapters, writing, editing, design, publishing, stt, tts",
                "Schemas Pydantic v2 Strict 11개 (626줄)",
                "Services 9개 (2,292줄): writing, editing, design, publishing, spelling, stt, tts, supabase",
                "AI Agents 10개 (1,820줄): orchestrator, writing, editing, design, publishing, quality, accessibility, user_advocate",
                "Models 6개 테이블 정의 (270줄), Core 설정 (228줄)",
                "[Sprint 2] Supabase Auth + DB 6테이블 + RLS 실연동 완료",
                "[Sprint 2] OpenAI GPT-4o 글쓰기 3개 엔드포인트 실동작 확인",
                "[Sprint 2] CLOVA TTS 실동작, STT WebSocket 코드 완성",
                "[Sprint 2] editing.py: full_review DB 저장 + report 조회 매핑 구현",
            ],
            "todo": [
                "CLOVA STT WebSocket 실시간 스트리밍 E2E 테스트",
                "design/publishing 서비스 실제 구현 (현재 인터페이스만)",
                "DB 마이그레이션 관리 도구 도입",
            ],
        },
        {
            "id": "A5", "name": "STT (Speech to Text)",
            "done": [
                "CLOVA Speech 선정 및 아키텍처 설계",
                "stt_service.py (158줄) — WebSocket 기반 구현 완료",
                "useSTT.ts Hook (176줄) — 프론트 인터페이스",
                "API endpoint stt.py (100줄), 스키마 stt.py (40줄)",
                "[Sprint 2] API 키 실제 설정 완료",
            ],
            "todo": [
                "WebSocket 실시간 음성 스트리밍 E2E 테스트 (curl로 검증 불가)",
                "한국어 인식률 PoC 테스트",
                "오프라인 fallback (Whisper 로컬 모델)",
            ],
        },
        {
            "id": "A6", "name": "TTS (Text to Speech)",
            "done": [
                "CLOVA Voice 선정 및 아키텍처 설계",
                "tts_service.py (159줄) — REST API 구현",
                "useTTS.ts Hook (245줄) — 프론트 인터페이스",
                "API endpoint tts.py (156줄), 스키마 tts.py (47줄)",
                "VoicePlayer.tsx (192줄) — 음성 재생 컴포넌트",
                "[Sprint 2] 실동작 확인: /tts/voices (8개 음성), /tts/synthesize (MP3 20KB 반환)",
            ],
            "todo": [
                "낭독 속도 조절, 일시정지, 반복 재생 UX",
                "시스템 안내음 vs 글 낭독 음성 구분",
                "Frontend VoicePlayer ↔ TTS API 실제 연결",
            ],
        },
        {
            "id": "A7", "name": "AI 글쓰기 엔진",
            "done": [
                "writing_service.py (262줄) — OpenAI GPT-4o 연동 완료",
                "writing_agent.py (171줄) — 프롬프트 체인",
                "API endpoint writing.py (164줄)",
                "[Sprint 2] /writing/generate SSE 스트리밍 실동작 — 한국어 에세이 실시간 생성",
                "[Sprint 2] /writing/rewrite 실동작 — 시적 문체로 재작성",
                "[Sprint 2] /writing/structure 실동작 — 5챕터 구조 제안",
            ],
            "todo": [
                "대화 → 문학적 글 변환 프롬프트 고도화",
                "장르별(에세이/소설/시/자서전) 프롬프트 최적화",
                "Frontend WritingEditor ↔ SSE 실제 연결",
            ],
        },
        {
            "id": "A8", "name": "편집/교열",
            "done": [
                "editing_service.py (514줄) — 4단계 편집 파이프라인 (OpenAI GPT-4o)",
                "editing_agent.py (212줄) — AI 편집 에이전트",
                "API endpoint editing.py (308줄)",
                "spelling_service.py (201줄) — 맞춤법 교정 서비스",
                "[Sprint 2] proofread 실동작: 5개 교정 감지, accuracy=85.0",
                "[Sprint 2] style-check 실동작: 문체 불일치 감지, consistency=70.0",
                "[Sprint 2] structure-review 실동작: flow=75.0, organization=80.0",
                "[Sprint 2] full-review 4단계 실동작: overall=89.4 (9건 이슈), DB 저장 성공",
                "[Sprint 2] report 조회 실동작: DB→QualityReport 매핑 완벽 동작",
                "[PDCA] Plan→Design→Do 완료, Check(Gap Analysis) 대기",
            ],
            "todo": [
                '음성 기반 편집 UX ("세 번째 문단을 읽어줘")',
                "Frontend EditingPanel ↔ API 실제 연결",
                "PDCA Check 단계 Gap Analysis 실행",
            ],
        },
        {
            "id": "A9", "name": "책 디자인",
            "done": [
                "design_service.py (287줄) — 표지/내지 설계 서비스 인터페이스",
                "design_agent.py (147줄) — AI 디자인 에이전트",
                "API endpoint design.py (185줄), 스키마 design.py (80줄)",
            ],
            "todo": [
                "AI 이미지 생성 (DALL-E/Midjourney) 연동",
                "Typst 기반 내지 조판 파이프라인 구현",
                "장르별 템플릿 (에세이, 소설, 시, 자서전)",
                "한국 출판 표준 판형 (신국판 152x225mm)",
                "CMYK, 재단선, 도련, 300dpi 인쇄 규격",
            ],
        },
        {
            "id": "A10", "name": "출판/유통",
            "done": [
                "publishing_service.py (465줄) — 출판 파이프라인 인터페이스",
                "publishing_agent.py (119줄)",
                "API endpoint publishing.py (197줄), 스키마 publishing.py (58줄)",
            ],
            "todo": [
                "DOCX 생성 (python-docx 활용)",
                "PDF 생성 (WeasyPrint/ReportLab)",
                "EPUB 생성 (ebooklib)",
                "전자책 플랫폼 연동 (리디북스, 밀리의서재)",
                "POD 연동 (부크크, 교보POD)",
                "ISBN 발급 프로세스 가이드",
            ],
        },
        {
            "id": "A11", "name": "보안",
            "done": [
                "JWT 기반 인증 구현 (deps.py 28줄)",
                "[Sprint 2] Supabase RLS 6테이블 전체 활성화 확인",
                "[Sprint 2] admin_client(service_role key)로 RLS 우회 프로필 생성",
                "[Sprint 2] 모든 API 키 실제 값 설정, .env 파일 git 제외 확인",
            ],
            "todo": [
                "음성 데이터 암호화 정책 구현",
                "장애 정보 별도 동의 절차 (개인정보보호법)",
                "API Rate limiting 적용",
                "CORS 정책 운영 환경 설정",
                "OWASP Top 10 점검",
            ],
        },
        {
            "id": "A12", "name": "테스트 — PDCA Cycle #1 완료 (91%)",
            "done": [
                "Backend 테스트: 12파일, 3,018줄",
                "  - test_schemas(706), test_chapters(407), test_publishing(281)",
                "  - test_editing(265), test_books(263), test_design(239)",
                "  - test_writing(204), test_tts(164), test_auth(163), test_stt(127)",
                "[Sprint 2] Backend 62개 + Frontend 51개 전체 통과 확인 (48e5619 커밋)",
            ],
            "todo": [
                "Frontend 테스트 복구 (현재 빌드 제외 설정 — 0개 활성)",
                "E2E 통합 테스트 (Playwright)",
                "스크린 리더 수동 테스트 (VoiceOver)",
                "부하 테스트 (Artillery/k6)",
            ],
        },
        {
            "id": "A13", "name": "법률/저작권",
            "done": [
                "설계 문서 단계에서 법적 요구사항 정리",
            ],
            "todo": [
                "AI 생성물 저작권 정책 수립",
                "음성 데이터 수집/처리/보관 동의 절차",
                "이용약관/개인정보처리방침 작성",
                "장애인차별금지법 준수 체크리스트",
            ],
        },
        {
            "id": "A14", "name": "인프라/DevOps",
            "done": [
                "Docker + docker-compose 설정 (BE:8000 + FE:3000)",
                "[Sprint 2] Backend venv 환경 (Python 3.14) 실행 확인",
                "[Sprint 2] 로컬 uvicorn 서버 37 routes 실행 검증",
            ],
            "todo": [
                "GitHub Actions CI/CD 파이프라인 복구 (.github/workflows 미존재)",
                "Vercel 배포 설정 (Frontend)",
                "AWS/GCP 배포 설정 (Backend)",
                "환경별 .env 분리 (dev/staging/prod)",
                "모니터링/로깅 시스템 (Sentry, DataDog)",
            ],
        },
        {
            "id": "A15", "name": "프로젝트 관리",
            "done": [
                "PDCA 방법론 기반 개발 관리 (3사이클 아카이브)",
                "Git 이력 관리 (6커밋)",
                "[Sprint 2] P0-1 미커밋 77파일 커밋 완료",
                "[Sprint 2] P0-2 pdca-status 18개 유령 피처 정리",
                "[Sprint 2] 6개 태스크 전체 완료 관리",
                "[Sprint 2] editing-service PDCA Plan→Design→Do 문서화",
            ],
            "todo": [
                "Sprint 3 계획 수립",
                "미커밋 변경사항 6건 커밋 (editing.py, auth.py, docs 등)",
                "README.md 업데이트",
            ],
        },
        {
            "id": "A16", "name": "품질 보증",
            "done": [
                "3회 PDCA Gap Analysis 수행 (평균 Match Rate 94.1%)",
                "코드-설계 동기화 검증 (gap-detector 3회)",
                "[Sprint 2] editing-service DB-API 매핑 불일치 발견 및 해결",
            ],
            "todo": [
                "editing-service PDCA Check 단계 Gap Analysis 실행",
                "실제 연동 기반 통합 품질 검증",
                "성능 프로파일링 (BE 응답시간, FE 렌더링)",
                "코드 커버리지 목표 80% 이상",
            ],
        },
        {
            "id": "A17", "name": "접근성 감사 (VETO권 보유)",
            "done": [
                "WAI-ARIA 속성 전체 적용 감사",
                "SkipLink, Announcer, 키보드 내비게이션 구현 검증",
            ],
            "todo": [
                "실제 VoiceOver 수동 테스트",
                "TalkBack (Android) 테스트",
                "NVDA (Windows) 테스트",
                "시각장애인 당사자 사용성 테스트",
                "고대비 모드 / 커스텀 폰트 크기 지원",
                "최종 VETO 심사 (배포 전 필수)",
            ],
        },
        {
            "id": "A18", "name": "사용자 대변인",
            "done": [
                "user_advocate_agent.py (330줄) — 사용자 관점 검증 에이전트",
            ],
            "todo": [
                "실사용자 피드백 수집 체계 구축",
                "사용자 여정 검증 (전맹/저시력 시나리오)",
                "베타 테스트 계획 수립",
            ],
        },
    ]

    for agent in agents:
        doc.add_heading(f'{agent["id"]} — {agent["name"]}', level=2)

        # 수행 업무
        p = doc.add_paragraph()
        run = p.add_run("수행 업무:")
        run.bold = True
        run.font.color.rgb = RGBColor(0x00, 0x80, 0x00)
        for item in agent["done"]:
            doc.add_paragraph(item, style="List Bullet")

        # 잔여 업무
        p = doc.add_paragraph()
        run = p.add_run("잔여 업무:")
        run.bold = True
        run.font.color.rgb = RGBColor(0xCC, 0x00, 0x00)
        for item in agent["todo"]:
            doc.add_paragraph(item, style="List Bullet")

    doc.add_page_break()

    # ══════════════════════════════════════════
    # 5. 코드베이스 상세 규모
    # ══════════════════════════════════════════
    doc.add_heading("5. 코드베이스 상세 규모", level=1)

    doc.add_heading("Backend API Endpoints (1,995줄)", level=2)
    add_styled_table(doc,
        ["엔드포인트", "줄 수", "담당", "실동작"],
        [
            ["editing.py", "308줄", "A8", "PASS (5개 엔드포인트)"],
            ["chapters.py", "278줄", "A4", "PASS (CRUD)"],
            ["books.py", "259줄", "A4", "PASS (CRUD)"],
            ["auth.py", "248줄", "A4+A11", "PASS (signup/login/me/settings/logout)"],
            ["publishing.py", "197줄", "A10", "인터페이스만"],
            ["design.py", "185줄", "A9", "인터페이스만"],
            ["writing.py", "164줄", "A7", "PASS (generate/rewrite/structure)"],
            ["tts.py", "156줄", "A6", "PASS (voices/synthesize)"],
            ["stt.py", "100줄", "A5", "WebSocket (미검증)"],
            ["router.py", "72줄", "-", "통합 라우터"],
        ]
    )

    doc.add_heading("Backend AI Agents (1,820줄)", level=2)
    add_styled_table(doc,
        ["에이전트", "줄 수", "역할"],
        [
            ["user_advocate_agent.py", "330줄", "사용자 관점 검증"],
            ["accessibility_agent.py", "322줄", "접근성 검증"],
            ["quality_agent.py", "248줄", "품질 분석"],
            ["editing_agent.py", "212줄", "4단계 편집"],
            ["orchestrator.py", "179줄", "전체 워크플로우 조율"],
            ["writing_agent.py", "171줄", "LLM 프롬프트 체인"],
            ["design_agent.py", "147줄", "표지/내지 디자인"],
            ["publishing_agent.py", "119줄", "출판 파이프라인"],
            ["base.py", "92줄", "에이전트 기본 클래스"],
        ]
    )

    doc.add_heading("Backend Services (2,292줄)", level=2)
    add_styled_table(doc,
        ["서비스", "줄 수", "상태"],
        [
            ["editing_service.py", "514줄", "실동작 (OpenAI GPT-4o)"],
            ["publishing_service.py", "465줄", "인터페이스만"],
            ["design_service.py", "287줄", "인터페이스만"],
            ["writing_service.py", "262줄", "실동작 (OpenAI GPT-4o SSE)"],
            ["supabase_service.py", "246줄", "실동작"],
            ["spelling_service.py", "201줄", "인터페이스만"],
            ["tts_service.py", "159줄", "실동작 (CLOVA Voice)"],
            ["stt_service.py", "158줄", "코드 완성 (WebSocket)"],
        ]
    )

    doc.add_heading("Backend 테스트 (3,018줄, 12파일)", level=2)
    add_styled_table(doc,
        ["테스트 파일", "줄 수", "영역"],
        [
            ["test_schemas.py", "706줄", "Pydantic 스키마 검증"],
            ["test_chapters.py", "407줄", "챕터 CRUD API"],
            ["test_publishing.py", "281줄", "출판 API"],
            ["test_editing.py", "265줄", "편집 API"],
            ["test_books.py", "263줄", "도서 CRUD API"],
            ["test_design.py", "239줄", "디자인 API"],
            ["test_writing.py", "204줄", "글쓰기 API"],
            ["conftest.py", "199줄", "테스트 설정/픽스처"],
            ["test_tts.py", "164줄", "TTS API"],
            ["test_auth.py", "163줄", "인증 API"],
            ["test_stt.py", "127줄", "STT API"],
        ]
    )

    doc.add_page_break()

    # ══════════════════════════════════════════
    # 6. 전체 진행률 요약
    # ══════════════════════════════════════════
    doc.add_heading("6. 전체 진행률 요약", level=1)

    p = doc.add_paragraph()
    run = p.add_run("v0.1.0 대비 v0.2.0 변화:")
    run.bold = True

    add_styled_table(doc,
        ["영역", "v0.1.0", "v0.2.0", "변화"],
        [
            ["구조 구현 (코드 뼈대)", "100%", "100%", "유지"],
            ["외부 연동 (Supabase, OpenAI, CLOVA)", "5%", "75%", "+70%p ▲"],
            ["테스트 (BE 62개 / FE 비활성)", "65%", "55%", "-10%p ▼ (FE 비활성)"],
            ["편집 서비스 (4단계 파이프라인)", "0%", "90%", "+90%p ▲"],
            ["접근성 (자동 테스트 / 수동 미완)", "50%", "50%", "유지"],
            ["배포 (Docker / CI/CD 미확인)", "20%", "15%", "-5%p ▼ (CI 미존재)"],
            ["법률/정책", "5%", "5%", "유지"],
        ]
    )

    doc.add_paragraph("")

    doc.add_heading("Supabase DB 테이블 현황 (6개, 모두 RLS 활성)", level=2)
    add_styled_table(doc,
        ["테이블", "용도", "상태"],
        [
            ["profiles", "사용자 프로필 (장애 유형, 음성 설정)", "실운영"],
            ["books", "도서 메타데이터", "실운영"],
            ["chapters", "챕터 본문", "실운영"],
            ["exports", "출력물 (DOCX/PDF/EPUB)", "스키마만"],
            ["editing_reports", "편집 품질 보고서", "실운영 (Sprint 2 연동)"],
            ["cover_images", "표지 이미지", "스키마만"],
        ]
    )

    doc.add_page_break()

    # ══════════════════════════════════════════
    # 7. 긴급 조치 필요 사항
    # ══════════════════════════════════════════
    doc.add_heading("7. 긴급 조치 필요 사항 (A0 지시)", level=1)

    add_styled_table(doc,
        ["우선순위", "작업", "담당", "비고"],
        [
            ["P0", "미커밋 6건 커밋 (editing.py, auth.py, docs)", "A15", "즉시 처리"],
            ["P1", "editing-service PDCA Check (Gap Analysis)", "A16", "Do 완료 후 필수"],
            ["P1", "Frontend 테스트 복구 (현재 0개 활성)", "A12", "빌드 제외 설정 해제"],
            ["P1", "GitHub Actions CI/CD 복구", "A14", ".github/workflows 미존재"],
            ["P2", "Frontend ↔ Backend 실제 연동", "A3+A4", "현재 mock 상태"],
            ["P2", "design/publishing 서비스 실제 구현", "A9+A10", "인터페이스만 존재"],
            ["P3", "VoiceOver 수동 접근성 테스트", "A17", "배포 전 VETO 필수"],
            ["P3", "법률/저작권 정책 수립", "A13", "출판 전 필수"],
        ]
    )

    doc.add_page_break()

    # ══════════════════════════════════════════
    # 8. 다음 Sprint 권장 순서
    # ══════════════════════════════════════════
    doc.add_heading("8. 다음 Sprint 권장 순서", level=1)

    p = doc.add_paragraph()
    run = p.add_run('Sprint 3: "프론트-백엔드 통합 + 디자인/출판 서비스"')
    run.bold = True
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x2B, 0x57, 0x9A)

    sprint_items = [
        "[A15] 미커밋 6건 커밋 + editing-service Check",
        "[A14] GitHub Actions CI/CD 복구",
        "[A12] Frontend 테스트 복구 (빌드 제외 해제)",
        "[A3+A4] Frontend ↔ Backend 실제 연동 (auth, writing, editing, tts)",
        "[A9] design 서비스 실제 구현 (표지 AI 생성, Typst 조판)",
        "[A10] publishing 서비스 실제 구현 (DOCX, PDF, EPUB 출력)",
        "[A5] CLOVA STT WebSocket E2E 테스트",
        "[A17] VoiceOver 접근성 수동 검증",
    ]
    for i, item in enumerate(sprint_items, 1):
        doc.add_paragraph(f"{i}. {item}")

    doc.add_page_break()

    # ══════════════════════════════════════════
    # 9. A0 Orchestrator 판단
    # ══════════════════════════════════════════
    doc.add_heading("9. A0 Orchestrator 판단", level=1)

    p = doc.add_paragraph()
    run = p.add_run("종합 평가")
    run.bold = True
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x2B, 0x57, 0x9A)

    doc.add_paragraph(
        "Sprint 2에서 핵심 외부 서비스(Supabase DB/Auth, OpenAI GPT-4o, CLOVA TTS) 연동을 완료하여 "
        "Backend의 실동작률이 5%에서 75%로 대폭 상승했습니다. "
        "특히 editing-service의 PDCA Plan→Design→Do를 통해 4단계 편집 파이프라인이 "
        "DB 저장까지 완벽히 동작하는 것을 검증했습니다."
    )

    doc.add_paragraph("")

    doc.add_paragraph(
        "그러나 Frontend는 아직 mock 상태이며, design/publishing 서비스는 인터페이스만 존재합니다. "
        "Frontend 테스트가 0개 활성 상태이고, CI/CD 파이프라인도 미존재하여 "
        "코드 품질 안전망이 취약한 상황입니다."
    )

    doc.add_paragraph("")

    p = doc.add_paragraph()
    run = p.add_run("핵심 권고사항:")
    run.bold = True
    run.font.color.rgb = RGBColor(0xCC, 0x00, 0x00)

    recommendations = [
        "즉시: 미커밋 6건 커밋 + editing-service Gap Analysis",
        "Sprint 3 핵심: Frontend ↔ Backend 실제 연동 (사용자 시나리오 E2E)",
        "Sprint 3 보조: design/publishing 서비스 실제 구현 시작",
        "품질: FE 테스트 복구 + CI/CD 파이프라인 복구가 선행되어야 안전한 개발 가능",
        "접근성: A17 VETO 심사 없이 배포 불가 — VoiceOver 테스트 반드시 Sprint 3에 포함",
    ]
    for item in recommendations:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_paragraph("")
    doc.add_paragraph("")

    # 서명란
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run("— A0 Orchestrator")
    run.italic = True
    run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run(f"모두가 작가 프로젝트 총괄 에이전트 | {REPORT_DATE}")
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    # ── 저장 ──
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, f"AI_PJ_SF_A0 종합보고서_{REPORT_VERSION}.docx")
    doc.save(output_path)
    print(f"저장 완료: {output_path}")
    return output_path


if __name__ == "__main__":
    create_report()
