/**
 * ExportPanel 컴포넌트 테스트
 * 형식 선택, 옵션 체크박스, 내보내기 버튼, 에러 표시를 검증합니다.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ExportPanel } from "@/components/book/ExportPanel";

// --- Mocks ---
vi.mock("@/hooks/useAnnouncer", () => ({
  useAnnouncer: () => ({
    announcePolite: vi.fn(),
    announceAssertive: vi.fn(),
  }),
}));

const mockExportBook = vi.fn();
const mockStatus = vi.fn();
const mockDownload = vi.fn();
vi.mock("@/lib/api", () => ({
  publishing: {
    exportBook: (...args: unknown[]) => mockExportBook(...args),
    status: (...args: unknown[]) => mockStatus(...args),
    download: (...args: unknown[]) => mockDownload(...args),
  },
}));

describe("ExportPanel", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("제목 '작품 내보내기'가 렌더링된다", () => {
    render(<ExportPanel bookId="test-book" />);
    expect(screen.getByText("작품 내보내기")).toBeInTheDocument();
  });

  it("3가지 파일 형식 라디오 버튼이 존재한다", () => {
    render(<ExportPanel bookId="test-book" />);
    expect(screen.getByText("Word 문서 (DOCX)")).toBeInTheDocument();
    expect(screen.getByText("PDF 문서")).toBeInTheDocument();
    expect(screen.getByText("전자책 (EPUB)")).toBeInTheDocument();
  });

  it("표지 포함 / 목차 포함 체크박스가 존재한다", () => {
    render(<ExportPanel bookId="test-book" />);
    expect(screen.getByLabelText("표지 포함")).toBeInTheDocument();
    expect(screen.getByLabelText("목차 포함")).toBeInTheDocument();
  });

  it("내보내기 시작 버튼이 존재한다", () => {
    render(<ExportPanel bookId="test-book" />);
    const btn = screen.getByRole("button", { name: /내보내기/ });
    expect(btn).toBeInTheDocument();
    expect(btn).not.toBeDisabled();
  });

  it("region 역할과 aria-label이 설정되어 있다", () => {
    render(<ExportPanel bookId="test-book" />);
    expect(screen.getByRole("region", { name: "내보내기 및 다운로드" })).toBeInTheDocument();
  });

  it("내보내기 API 호출 실패 시 에러 메시지 표시", async () => {
    mockExportBook.mockRejectedValueOnce(new Error("API error"));

    render(<ExportPanel bookId="test-book" />);
    const btn = screen.getByRole("button", { name: /내보내기/ });

    fireEvent.click(btn);

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("내보내기를 시작할 수 없습니다");
  });

  it("내보내기 성공 시 상태 표시 영역이 나타난다", async () => {
    mockExportBook.mockResolvedValueOnce({
      data: {
        export_id: "exp-1",
        book_id: "test-book",
        format: "pdf",
        status: "pending",
        created_at: "2026-03-06",
      },
    });

    render(<ExportPanel bookId="test-book" />);
    const btn = screen.getByRole("button", { name: /내보내기/ });

    fireEvent.click(btn);

    const status = await screen.findByRole("status");
    expect(status).toBeInTheDocument();
  });
});
