"""A0 Orchestrator 종합보고서 DOCX 생성 스크립트"""
import os
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn


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

    # ── 표지 ──
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
        ("보고 일자", "2026-03-03"),
        ("프로젝트 버전", "MVP v0.1.0"),
        ("문서 버전", "v0.1.0"),
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

    # ── 목차 ──
    doc.add_heading("목차", level=1)
    toc_items = [
        "1. 프로젝트 개요",
        "2. PDCA 사이클 완료 현황",
        "3. 에이전트별 상세 업무 분석 (A0~A18)",
        "4. 코드베이스 규모 분석",
        "5. 전체 진행률 요약",
        "6. 긴급 조치 필요 사항",
        "7. 다음 Sprint 권장 순서",
        "8. A0 Orchestrator 판단",
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
        ["계층", "기술", "버전/비고"],
        [
            ["Frontend", "Next.js + React + TypeScript + Tailwind CSS", "Next.js 15, React 19"],
            ["Backend", "FastAPI + Pydantic v2 (Strict)", "Python 3.12"],
            ["Database", "Supabase (PostgreSQL + Auth + RLS)", "클라우드"],
            ["AI", "OpenAI GPT (글 생성)", "gpt-4 계열"],
            ["STT", "CLOVA Speech (네이버)", "한국어 특화"],
            ["TTS", "CLOVA Voice (네이버)", "한국어 자연스러운 음성"],
            ["조판", "Typst", "책 내지 조판"],
            ["컨테이너", "Docker + docker-compose", "로컬/CI 환경"],
            ["CI/CD", "GitHub Actions", "4단계 파이프라인"],
        ]
    )

    doc.add_heading("코드베이스 규모", level=2)
    add_styled_table(doc,
        ["영역", "줄 수", "파일 수"],
        [
            ["Backend 전체", "7,219줄", "~45 파일"],
            ["Frontend 전체", "6,875줄", "~38 파일"],
            ["Backend 테스트", "2,819줄", "10 파일"],
            ["Frontend 테스트", "1,217줄", "10 파일"],
            ["합계", "18,130줄", "~103 파일"],
        ]
    )

    doc.add_page_break()

    # ══════════════════════════════════════════
    # 2. PDCA 사이클 완료 현황
    # ══════════════════════════════════════════
    doc.add_heading("2. PDCA 사이클 완료 현황", level=1)

    doc.add_paragraph("총 3회의 PDCA 사이클을 완료하여 평균 Match Rate 94.1%를 달성했습니다.")

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
    run = p.add_run("평균 Match Rate: 94.1%")
    run.bold = True

    doc.add_page_break()

    # ══════════════════════════════════════════
    # 3. 에이전트별 상세 업무 분석
    # ══════════════════════════════════════════
    doc.add_heading("3. 에이전트별 상세 업무 분석 (A0~A18)", level=1)

    agents = [
        {
            "id": "A0", "name": "Orchestrator (전체 조율)",
            "done": [
                "8단계 로드맵 설계 및 순서 결정",
                "19세션 관리, PDCA 3사이클 오케스트레이션",
                "에이전트 간 릴레이 프로토콜 적용",
            ],
            "todo": [
                "실제 API 연동 후 통합 워크플로우 테스트 조율",
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
                "페이지 13 TSX (2,854줄): login, signup, dashboard, settings, write, edit, review, design, publish 등",
                "컴포넌트 15 TSX (2,383줄): Voice, Writing, Editing, Book, UI, Layout",
                "Providers 3 TSX (293줄): Announcer, Voice, Supabase",
                "Hooks 6 TS (689줄): useSTT, useTTS, useVoiceCommand, useKeyboardNav 등",
                "Types 5 TS (285줄): book, user, api, voice, index",
                "Lib 4 TS (664줄): api.ts(515줄), utils.ts, supabase/client, supabase/server",
                "FE-BE 타입 동기화 98.3% Match Rate (Act-3 완료)",
            ],
            "todo": [
                "실제 Supabase Auth 연결 (현재 mock)",
                "실제 API 엔드포인트 연동 (api.ts 32개 함수)",
                "Web Speech API 실제 연결",
                "미테스트 컴포넌트 6개 (CoverDesigner, ExportPanel, ChapterList, StreamingText, Header, Navigation)",
                "미테스트 Hook 4개 (useSTT, useTTS, useAnnouncer, useSupabase)",
            ],
        },
        {
            "id": "A4", "name": "Backend (FastAPI + Pydantic) — 7,219줄",
            "done": [
                "API Endpoints 9+router (1,849줄): auth, books, chapters, writing, editing, design, publishing, stt, tts",
                "Schemas Pydantic v2 10개 (626줄): Strict 타입 적용",
                "Services 8개 (2,292줄): 비즈니스 로직 계층",
                "Agents AI 8개 (1,820줄): orchestrator, writing, editing, design, publishing, quality, accessibility, user_advocate",
                "Models ORM 4개 (~400줄): user, book, chapter, export",
                "Core 3개 (~232줄): config, database, security",
            ],
            "todo": [
                "Supabase 실제 연결 (현재 mock service)",
                "OpenAI API 키 발급 및 연결",
                "CLOVA Speech/Voice 실제 연동",
                "DB 마이그레이션 스크립트 작성",
                "WebSocket 실시간 스트리밍 구현",
            ],
        },
        {
            "id": "A5", "name": "STT (Speech to Text)",
            "done": [
                "STT 서비스 아키텍처 설계 (CLOVA Speech 선정)",
                "stt_service.py (158줄) — 인터페이스 구현",
                "useSTT.ts Hook (176줄) — 프론트 인터페이스",
                "API endpoint stt.py (100줄), 스키마 stt.py (40줄)",
            ],
            "todo": [
                "CLOVA Speech API 키 발급 및 실제 연동",
                "WebSocket 실시간 음성 스트리밍 구현",
                "한국어 인식률 PoC 테스트",
                "오프라인 fallback (Whisper 로컬 모델)",
            ],
        },
        {
            "id": "A6", "name": "TTS (Text to Speech)",
            "done": [
                "TTS 서비스 아키텍처 설계 (CLOVA Voice 선정)",
                "tts_service.py (159줄) — 인터페이스 구현",
                "useTTS.ts Hook (245줄) — 프론트 인터페이스",
                "API endpoint tts.py (156줄), 스키마 tts.py (47줄)",
                "VoicePlayer 컴포넌트 (192줄)",
            ],
            "todo": [
                "CLOVA Voice API 실제 연동",
                "낭독 속도 조절, 일시정지, 반복 재생 UX",
                "시스템 안내음 vs 글 낭독 음성 구분",
            ],
        },
        {
            "id": "A7", "name": "AI 글쓰기 엔진",
            "done": [
                "writing_service.py (262줄) — LLM 연동 인터페이스",
                "writing_agent.py (171줄) — 프롬프트 체인",
                "API endpoint writing.py (164줄)",
                "WritingEditor 컴포넌트 (154줄), StreamingText (99줄)",
            ],
            "todo": [
                "OpenAI API 실제 연동 (현재 placeholder)",
                "대화 → 문학적 글 변환 프롬프트 엔지니어링",
                "SSE 기반 실시간 글 생성 스트리밍",
                "문체/장르별 프롬프트 최적화",
            ],
        },
        {
            "id": "A8", "name": "편집/교열",
            "done": [
                "editing_service.py (514줄) — 4단계 편집 체계 설계",
                "editing_agent.py (212줄) — AI 편집 에이전트",
                "API endpoint editing.py (264줄)",
                "EditingPanel.tsx (282줄), QualityReport.tsx (145줄)",
                "spelling_service.py (201줄) — 맞춤법 교정 서비스",
            ],
            "todo": [
                "네이버 맞춤법 검사기 API 연동",
                "4단계 편집 파이프라인 실제 동작 구현",
                '음성 기반 편집 UX ("세 번째 문단을 읽어줘")',
                "원고 품질 리포트 실제 분석 로직",
            ],
        },
        {
            "id": "A9", "name": "책 디자인",
            "done": [
                "design_service.py (287줄) — 표지/내지 설계 서비스",
                "design_agent.py (147줄) — AI 디자인 에이전트",
                "API endpoint design.py (185줄), 스키마 design.py (80줄)",
                "CoverDesigner.tsx (192줄) — 표지 디자인 UI",
            ],
            "todo": [
                "AI 이미지 생성 (DALL-E/Midjourney) 연동",
                "Typst 기반 내지 조판 파이프라인",
                "장르별 템플릿 (에세이, 소설, 시, 자서전)",
                "한국 출판 표준 판형 (신국판 152x225mm)",
                "CMYK, 재단선, 도련, 300dpi 인쇄 규격",
            ],
        },
        {
            "id": "A10", "name": "출판/유통",
            "done": [
                "publishing_service.py (465줄) — 출판 파이프라인",
                "publishing_agent.py (119줄)",
                "API endpoint publishing.py (197줄), 스키마 publishing.py (58줄)",
                "ExportPanel.tsx (243줄) — 내보내기 UI",
            ],
            "todo": [
                "DOCX 생성 (python-docx)",
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
                "security.py — JWT 기반 인증 구현",
                "API deps.py — 의존성 주입 보안 계층",
                "Supabase RLS 설계",
            ],
            "todo": [
                "음성 데이터 암호화 정책 구현",
                "장애 정보 별도 동의 절차 (개인정보보호법)",
                "API Rate limiting 적용",
                "CORS 정책 운영 환경 설정",
                "입력값 검증 강화 (XSS, SQL Injection)",
                "OWASP Top 10 점검",
            ],
        },
        {
            "id": "A12", "name": "테스트 — PDCA Cycle #1 완료 (91%)",
            "done": [
                "Backend 테스트: 10파일, 2,819줄, 170개 테스트 전체 통과",
                "Frontend 테스트: 10파일, 1,217줄, 106개 테스트",
                "접근성 테스트: axe-core 6파일 (WCAG 2.1 AA)",
            ],
            "todo": [
                "미테스트 FE 컴포넌트 6개 + Hook 4개",
                "api.ts 32개 함수 단위 테스트",
                "통합 테스트 (E2E: Playwright)",
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
                "AI 보조 글 출판 시 플랫폼별 제약 정리",
            ],
        },
        {
            "id": "A14", "name": "인프라/DevOps",
            "done": [
                "Docker + docker-compose 설정 완료",
                "GitHub Actions CI/CD 4단계 파이프라인",
                "  Stage 1: Backend Tests (pytest + ruff + mypy)",
                "  Stage 2: Frontend Tests (Vitest + axe-core)",
                "  Stage 3: Frontend Build 검증",
                "  Stage 4: Quality Gate (조건부 통과)",
            ],
            "todo": [
                "Vercel 배포 설정 (Frontend)",
                "AWS/GCP 배포 설정 (Backend)",
                "환경별 .env 분리 (dev/staging/prod)",
                "모니터링/로깅 시스템 (Sentry, DataDog)",
                "HTTPS/SSL 인증서 설정",
            ],
        },
        {
            "id": "A15", "name": "프로젝트 관리",
            "done": [
                "PDCA 방법론 기반 개발 관리 (3사이클)",
                "Git 이력 관리 (4커밋)",
                "API 문서 자동화 (FastAPI Swagger)",
            ],
            "todo": [
                "미커밋 변경사항 54파일 (+1,884/-642) 커밋",
                ".pdca-status.json 17개 유령 피처 정리",
                "Sprint 2 계획 수립",
                "README.md 업데이트",
            ],
        },
        {
            "id": "A16", "name": "품질 보증",
            "done": [
                "3회 PDCA Gap Analysis 수행",
                "평균 Match Rate 94.1% 달성",
                "코드-설계 동기화 검증 (gap-detector 3회)",
            ],
            "todo": [
                "실제 API 연동 후 통합 품질 검증",
                "성능 프로파일링 (BE 응답시간, FE 렌더링)",
                "코드 커버리지 목표 80% 이상",
            ],
        },
        {
            "id": "A17", "name": "접근성 감사 (VETO권 보유)",
            "done": [
                "WAI-ARIA 속성 전체 적용 감사",
                "SkipLink, Announcer, 키보드 내비게이션 구현 검증",
                "axe-core 기반 자동 접근성 테스트 6파일",
                "WCAG 2.1 AA 체크리스트 테스트",
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
    # 4. 코드베이스 상세 규모
    # ══════════════════════════════════════════
    doc.add_heading("4. 코드베이스 상세 규모", level=1)

    doc.add_heading("Backend API Endpoints", level=2)
    add_styled_table(doc,
        ["엔드포인트", "줄 수", "담당 에이전트"],
        [
            ["auth.py", "246줄", "A4 + A11"],
            ["books.py", "259줄", "A4"],
            ["chapters.py", "278줄", "A4"],
            ["writing.py", "164줄", "A7"],
            ["editing.py", "264줄", "A8"],
            ["design.py", "185줄", "A9"],
            ["publishing.py", "197줄", "A10"],
            ["stt.py", "100줄", "A5"],
            ["tts.py", "156줄", "A6"],
            ["합계", "1,849줄", "-"],
        ]
    )

    doc.add_heading("Backend AI Agents", level=2)
    add_styled_table(doc,
        ["에이전트", "줄 수", "역할"],
        [
            ["orchestrator.py", "179줄", "전체 워크플로우 조율"],
            ["writing_agent.py", "171줄", "LLM 프롬프트 체인"],
            ["editing_agent.py", "212줄", "4단계 편집"],
            ["design_agent.py", "147줄", "표지/내지 디자인"],
            ["publishing_agent.py", "119줄", "출판 파이프라인"],
            ["quality_agent.py", "248줄", "품질 분석"],
            ["accessibility_agent.py", "322줄", "접근성 검증"],
            ["user_advocate_agent.py", "330줄", "사용자 관점"],
            ["합계", "1,820줄", "-"],
        ]
    )

    doc.add_heading("Backend 테스트", level=2)
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
            ["test_tts.py", "164줄", "TTS API"],
            ["test_auth.py", "163줄", "인증 API"],
            ["test_stt.py", "127줄", "STT API"],
            ["합계", "2,819줄", "-"],
        ]
    )

    doc.add_page_break()

    # ══════════════════════════════════════════
    # 5. 전체 진행률 요약
    # ══════════════════════════════════════════
    doc.add_heading("5. 전체 진행률 요약", level=1)

    progress_data = [
        ["구조 구현 (코드 뼈대 + 스키마 + API + FE 페이지)", "100%", "완료"],
        ["테스트 (BE 170개 + FE 106개 / E2E 미완)", "65%", "진행 중"],
        ["실제 연동 (Supabase, OpenAI, CLOVA)", "5%", "미착수"],
        ["접근성 (자동 테스트 완료 / 수동 미완)", "50%", "진행 중"],
        ["배포 (Docker+CI 완료 / Vercel+AWS 미설정)", "20%", "진행 중"],
        ["법률/정책 (설계 단계 정리만 완료)", "5%", "미착수"],
    ]
    add_styled_table(doc,
        ["영역", "진행률", "상태"],
        progress_data,
    )

    doc.add_page_break()

    # ══════════════════════════════════════════
    # 6. 긴급 조치 필요 사항
    # ══════════════════════════════════════════
    doc.add_heading("6. 긴급 조치 필요 사항 (A0 지시)", level=1)

    add_styled_table(doc,
        ["우선순위", "작업", "담당 에이전트", "난이도"],
        [
            ["P0", "미커밋 54파일 커밋", "A15", "LOW"],
            ["P0", "pdca-status 17개 유령 피처 정리", "A15", "LOW"],
            ["P1", ".env 실제 키 발급 (Supabase, OpenAI, CLOVA)", "A14", "MEDIUM"],
            ["P1", "Supabase DB 마이그레이션 + Auth 연결", "A4", "HIGH"],
            ["P2", "OpenAI API 연동 (글쓰기 엔진)", "A7", "MEDIUM"],
            ["P2", "CLOVA STT/TTS 실제 연동", "A5, A6", "MEDIUM"],
            ["P3", "Vercel + AWS 배포", "A14", "HIGH"],
            ["P3", "VoiceOver 수동 접근성 테스트", "A17", "HIGH"],
        ]
    )

    doc.add_page_break()

    # ══════════════════════════════════════════
    # 7. 다음 Sprint 권장 순서
    # ══════════════════════════════════════════
    doc.add_heading("7. 다음 Sprint 권장 순서", level=1)

    p = doc.add_paragraph()
    run = p.add_run('Sprint 2: "실제 연동 Sprint"')
    run.bold = True
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x2B, 0x57, 0x9A)

    sprint_items = [
        "[A15] 커밋 + 상태 정리",
        "[A14] .env 키 발급, Supabase 프로젝트 생성",
        "[A4]  Supabase Auth + DB 연결",
        "[A7]  OpenAI API 글쓰기 연동",
        "[A5]  CLOVA Speech STT PoC",
        "[A6]  CLOVA Voice TTS 연동",
        "[A12] 통합 테스트 (E2E)",
        "[A17] VoiceOver 접근성 수동 검증",
    ]
    for i, item in enumerate(sprint_items, 1):
        doc.add_paragraph(f"{i}. {item}")

    doc.add_page_break()

    # ══════════════════════════════════════════
    # 8. A0 Orchestrator 판단
    # ══════════════════════════════════════════
    doc.add_heading("8. A0 Orchestrator 판단", level=1)

    p = doc.add_paragraph()
    run = p.add_run(
        "구조적 뼈대는 100% 완성되었으나, 실제 외부 서비스 연동률이 5%로 "
        "MVP 실동작까지 가장 큰 병목입니다. "
        "Sprint 2에서는 Supabase → OpenAI → CLOVA 순으로 실제 연동에 집중해야 합니다."
    )
    run.font.size = Pt(11)

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
    run = p.add_run("모두가 작가 프로젝트 총괄 에이전트")
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    # ── 저장 ──
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, "AI_PJ_SF_A0 종합보고서_v0.1.0.docx")
    doc.save(output_path)
    print(f"저장 완료: {output_path}")
    return output_path


if __name__ == "__main__":
    create_report()
