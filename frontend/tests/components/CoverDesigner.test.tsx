/**
 * CoverDesigner 컴포넌트 테스트
 * 장르/스타일 선택, AI 표지 생성, 템플릿 로드, 에러 처리를 검증합니다.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { CoverDesigner } from "@/components/book/CoverDesigner";

// --- Mocks ---
vi.mock("@/hooks/useAnnouncer", () => ({
  useAnnouncer: () => ({
    announcePolite: vi.fn(),
    announceAssertive: vi.fn(),
  }),
}));

const mockGenerateCover = vi.fn();
const mockTemplates = vi.fn();
vi.mock("@/lib/api", () => ({
  design: {
    generateCover: (...args: unknown[]) => mockGenerateCover(...args),
    templates: (...args: unknown[]) => mockTemplates(...args),
  },
}));

describe("CoverDesigner", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("제목 '표지 디자인'이 렌더링된다", () => {
    render(<CoverDesigner bookTitle="테스트 책" />);
    expect(screen.getByText("표지 디자인")).toBeInTheDocument();
  });

  it("표지가 없을 때 안내 메시지가 표시된다", () => {
    render(<CoverDesigner bookTitle="테스트 책" />);
    expect(screen.getByText(/아직 표지가 없습니다/)).toBeInTheDocument();
  });

  it("표지 URL이 있을 때 이미지가 렌더링된다", () => {
    render(<CoverDesigner bookTitle="테스트 책" currentCoverUrl="https://example.com/cover.jpg" />);
    const img = screen.getByAltText("테스트 책 표지 이미지");
    expect(img).toBeInTheDocument();
  });

  it("장르 선택 라벨이 존재한다", () => {
    render(<CoverDesigner bookTitle="테스트 책" />);
    expect(screen.getByText("장르")).toBeInTheDocument();
  });

  it("스타일 선택 라벨이 존재한다", () => {
    render(<CoverDesigner bookTitle="테스트 책" />);
    expect(screen.getByText("스타일")).toBeInTheDocument();
  });

  it("AI 표지 생성 버튼이 존재한다", () => {
    render(<CoverDesigner bookTitle="테스트 책" />);
    const btn = screen.getByRole("button", { name: "AI 표지 생성" });
    expect(btn).toBeInTheDocument();
  });

  it("표지가 있을 때 버튼 텍스트가 '표지 다시 생성'", () => {
    render(<CoverDesigner bookTitle="테스트 책" currentCoverUrl="https://example.com/cover.jpg" />);
    const btn = screen.getByRole("button", { name: "표지 다시 생성" });
    expect(btn).toBeInTheDocument();
  });

  it("템플릿 불러오기 버튼이 존재한다", () => {
    render(<CoverDesigner bookTitle="테스트 책" />);
    const btn = screen.getByRole("button", { name: "템플릿 불러오기" });
    expect(btn).toBeInTheDocument();
  });

  it("region 역할과 aria-label이 설정되어 있다", () => {
    render(<CoverDesigner bookTitle="테스트 책" />);
    expect(screen.getByRole("region", { name: "표지 디자이너" })).toBeInTheDocument();
  });

  it("표지 생성 실패 시 에러 메시지 표시", async () => {
    mockGenerateCover.mockRejectedValueOnce(new Error("Gemini error"));

    render(<CoverDesigner bookTitle="테스트 책" />);
    fireEvent.click(screen.getByRole("button", { name: "AI 표지 생성" }));

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("표지 생성에 실패했습니다");
  });
});
