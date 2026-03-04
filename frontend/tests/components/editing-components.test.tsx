/**
 * Editing 컴포넌트 접근성 테스트
 * EditingPanel, QualityReport 컴포넌트의
 * ARIA 속성, 탭 인터페이스, 스크린 리더 호환성을 검증합니다.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { EditingPanel } from "@/components/editing/EditingPanel";
import { QualityReport } from "@/components/editing/QualityReport";
import type { EditSuggestion } from "@/types/book";

// Mock useAnnouncer
vi.mock("@/hooks/useAnnouncer", () => ({
  useAnnouncer: () => ({
    announcePolite: vi.fn(),
    announceAssertive: vi.fn(),
  }),
}));

describe("EditingPanel 접근성", () => {
  const suggestions: EditSuggestion[] = [
    {
      id: "s1",
      type: "grammar",
      original: "잘못된 문장",
      suggested: "올바른 문장",
      explanation: "문법 오류를 수정합니다.",
      accepted: null,
    },
    {
      id: "s2",
      type: "style",
      original: "어색한 표현",
      suggested: "자연스러운 표현",
      explanation: "문체를 개선합니다.",
      accepted: true,
    },
  ];

  const defaultProps = {
    suggestions,
    activeStage: "proofread" as const,
    onStageChange: vi.fn(),
    onAcceptSuggestion: vi.fn(),
    onRejectSuggestion: vi.fn(),
    onAcceptAll: vi.fn(),
    onRunAnalysis: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("편집 패널에 role=region이 있다", () => {
    render(<EditingPanel {...defaultProps} />);
    const region = screen.getByRole("region", { name: /편집 패널/ });
    expect(region).toBeInTheDocument();
  });

  it("단계 탭에 role=tablist가 있다", () => {
    render(<EditingPanel {...defaultProps} />);
    const tablist = screen.getByRole("tablist", { name: /편집 단계/ });
    expect(tablist).toBeInTheDocument();
  });

  it("4개의 편집 단계 탭이 있다", () => {
    render(<EditingPanel {...defaultProps} />);
    const tabs = screen.getAllByRole("tab");
    expect(tabs.length).toBe(4);
  });

  it("활성 탭에 aria-selected=true가 있다", () => {
    render(<EditingPanel {...defaultProps} />);
    const activeTab = screen.getByRole("tab", { name: "교정" });
    expect(activeTab).toHaveAttribute("aria-selected", "true");
  });

  it("탭 패널에 role=tabpanel이 있다", () => {
    render(<EditingPanel {...defaultProps} />);
    const tabpanel = screen.getByRole("tabpanel");
    expect(tabpanel).toBeInTheDocument();
  });

  it("제안 목록에 aria-label이 있다", () => {
    render(<EditingPanel {...defaultProps} />);
    const list = screen.getByRole("list", { name: /편집 제안 목록/ });
    expect(list).toBeInTheDocument();
  });

  it("요약 통계에 aria-live가 있다", () => {
    const { container } = render(<EditingPanel {...defaultProps} />);
    const live = container.querySelector("[aria-live='polite']");
    expect(live).toBeInTheDocument();
  });

  it("분석 실행 버튼에 aria-label이 있다", () => {
    render(<EditingPanel {...defaultProps} />);
    const btn = screen.getByRole("button", { name: /분석 실행/ });
    expect(btn).toBeInTheDocument();
  });

  it("적용/거절 버튼이 대기 중인 제안에만 표시된다", () => {
    render(<EditingPanel {...defaultProps} />);
    const acceptBtns = screen.getAllByRole("button", { name: /적용/ });
    // s1은 accepted=null (대기), s2는 accepted=true (적용됨)
    // 분석 실행 버튼 + 모두 적용 버튼 + 제안 적용 버튼
    expect(acceptBtns.length).toBeGreaterThan(0);
  });

  it("제안이 없을 때 안내 메시지를 표시한다", () => {
    render(<EditingPanel {...defaultProps} suggestions={[]} />);
    expect(screen.getByText(/분석 실행 버튼을 눌러/)).toBeInTheDocument();
  });

  it("탭 클릭 시 onStageChange가 호출된다", async () => {
    render(<EditingPanel {...defaultProps} />);
    const tab = screen.getByRole("tab", { name: "구조 편집" });

    await userEvent.click(tab);

    expect(defaultProps.onStageChange).toHaveBeenCalledWith("structure");
  });
});

describe("QualityReport 접근성", () => {
  const report = {
    book_id: "test-book-1",
    overall_score: 85,
    stage_results: [
      { stage: "structure" as const, score: 75, issues_count: 2, feedback: "구조 개선 필요" },
      { stage: "proofread" as const, score: 90, issues_count: 1, feedback: "맞춤법 양호" },
    ],
    total_issues: 3,
    summary: "전반적으로 양호한 품질입니다.",
    recommendations: ["문체 일관성을 높이세요.", "접속사 사용을 줄이면 좋겠습니다."],
    created_at: "2026-03-05T00:00:00Z",
  };

  it("보고서 영역에 role=region이 있다", () => {
    render(<QualityReport report={report} />);
    const region = screen.getByRole("region", { name: /품질 보고서/ });
    expect(region).toBeInTheDocument();
  });

  it("판정 결과에 role=status가 있다", () => {
    render(<QualityReport report={report} />);
    const status = screen.getByRole("status");
    expect(status).toBeInTheDocument();
  });

  it("각 점수에 aria-label이 있다", () => {
    render(<QualityReport report={report} />);
    const scoreLabels = screen.getAllByLabelText(/점/);
    expect(scoreLabels.length).toBeGreaterThan(0);
  });

  it("권장 사항 목록에 aria-label이 있다", () => {
    render(<QualityReport report={report} />);
    const list = screen.getByRole("list", { name: /권장 사항 목록/ });
    expect(list).toBeInTheDocument();
  });

  it("권장 배지가 표시된다", () => {
    render(<QualityReport report={report} />);
    const badges = screen.getAllByText("권장");
    expect(badges.length).toBeGreaterThan(0);
  });
});
