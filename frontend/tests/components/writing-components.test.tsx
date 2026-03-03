/**
 * Writing 컴포넌트 접근성 테스트
 * WritingEditor, StreamingText, ChapterList 컴포넌트의
 * ARIA 속성, 키보드 접근성, 스크린 리더 호환성을 검증합니다.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { WritingEditor } from "@/components/writing/WritingEditor";
import { StreamingText } from "@/components/writing/StreamingText";
import { ChapterList } from "@/components/writing/ChapterList";

// Mock useAnnouncer
vi.mock("@/hooks/useAnnouncer", () => ({
  useAnnouncer: () => ({
    announcePolite: vi.fn(),
    announceAssertive: vi.fn(),
  }),
}));

describe("WritingEditor 접근성", () => {
  const defaultProps = {
    content: "테스트 내용입니다.",
    onChange: vi.fn(),
    onSave: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("편집기 영역에 role=region이 있다", () => {
    render(<WritingEditor {...defaultProps} />);
    const region = screen.getByRole("region", { name: /글쓰기 편집기/ });
    expect(region).toBeInTheDocument();
  });

  it("텍스트 영역에 aria-label이 있다", () => {
    render(<WritingEditor {...defaultProps} chapterTitle="제1장" />);
    const textarea = screen.getByRole("textbox");
    expect(textarea).toHaveAttribute("aria-label");
  });

  it("저장 버튼에 aria-label이 있다", () => {
    render(<WritingEditor {...defaultProps} />);
    const saveBtn = screen.getByRole("button", { name: /저장/ });
    expect(saveBtn).toBeInTheDocument();
  });

  it("Ctrl+S로 저장할 수 있다", async () => {
    render(<WritingEditor {...defaultProps} />);
    const textarea = screen.getByRole("textbox");

    fireEvent.keyDown(textarea, { key: "s", ctrlKey: true });

    expect(defaultProps.onSave).toHaveBeenCalled();
  });

  it("글자 수를 aria-label로 표시한다", () => {
    render(<WritingEditor {...defaultProps} content="가나다라" />);
    const wordCount = screen.getByLabelText(/작성됨/);
    expect(wordCount).toBeInTheDocument();
  });

  it("저장 중일 때 버튼이 비활성화된다", () => {
    render(<WritingEditor {...defaultProps} isSaving={true} />);
    const saveBtn = screen.getByRole("button", { name: /저장/ });
    expect(saveBtn).toBeDisabled();
  });
});

describe("StreamingText 접근성", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("텍스트 영역에 role=region이 있다", () => {
    render(<StreamingText text="테스트" isStreaming={false} />);
    const region = screen.getByRole("region", { name: /AI 생성 텍스트/ });
    expect(region).toBeInTheDocument();
  });

  it("스트리밍 중 상태 표시가 있다", () => {
    render(<StreamingText text="텍스트 생성 중" isStreaming={true} />);
    const status = screen.getByRole("status");
    expect(status).toBeInTheDocument();
  });

  it("텍스트 영역에 aria-live=polite가 있다", () => {
    const { container } = render(
      <StreamingText text="테스트 내용" isStreaming={false} />
    );
    const liveRegion = container.querySelector("[aria-live='polite']");
    expect(liveRegion).toBeInTheDocument();
  });

  it("스트리밍 애니메이션은 aria-hidden이다", () => {
    const { container } = render(
      <StreamingText text="생성 중" isStreaming={true} />
    );
    const hiddenElements = container.querySelectorAll("[aria-hidden='true']");
    expect(hiddenElements.length).toBeGreaterThan(0);
  });
});

describe("ChapterList 접근성", () => {
  const chapters = [
    {
      id: "ch-1",
      book_id: "book-1",
      title: "제1장: 시작",
      content: "내용",
      order: 1,
      status: "draft" as const,
      word_count: 100,
      created_at: "2026-01-01",
      updated_at: "2026-01-01",
    },
    {
      id: "ch-2",
      book_id: "book-1",
      title: "제2장: 전개",
      content: "내용2",
      order: 2,
      status: "draft" as const,
      word_count: 200,
      created_at: "2026-01-01",
      updated_at: "2026-01-01",
    },
  ];

  const defaultProps = {
    chapters,
    activeChapterId: "ch-1",
    onSelectChapter: vi.fn(),
    onAddChapter: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("챕터 목록에 role=listbox가 있다", () => {
    render(<ChapterList {...defaultProps} />);
    const listbox = screen.getByRole("listbox", { name: /챕터 선택/ });
    expect(listbox).toBeInTheDocument();
  });

  it("각 챕터에 role=option이 있다", () => {
    render(<ChapterList {...defaultProps} />);
    const options = screen.getAllByRole("option");
    expect(options.length).toBe(2);
  });

  it("활성 챕터에 aria-selected=true가 있다", () => {
    render(<ChapterList {...defaultProps} />);
    const activeOption = screen.getByRole("option", { name: /제1장/ });
    expect(activeOption).toHaveAttribute("aria-selected", "true");
  });

  it("비활성 챕터에 aria-selected=false가 있다", () => {
    render(<ChapterList {...defaultProps} />);
    const inactiveOption = screen.getByRole("option", { name: /제2장/ });
    expect(inactiveOption).toHaveAttribute("aria-selected", "false");
  });

  it("nav 요소에 aria-label이 있다", () => {
    render(<ChapterList {...defaultProps} />);
    const nav = screen.getByRole("navigation", { name: /챕터 목록/ });
    expect(nav).toBeInTheDocument();
  });

  it("챕터 추가 버튼이 있다", () => {
    render(<ChapterList {...defaultProps} />);
    const addBtn = screen.getByRole("button", { name: /챕터 추가/ });
    expect(addBtn).toBeInTheDocument();
  });

  it("삭제 버튼에 aria-label이 있다", () => {
    render(
      <ChapterList {...defaultProps} onRemoveChapter={vi.fn()} />
    );
    const deleteButtons = screen.getAllByRole("button", { name: /삭제/ });
    expect(deleteButtons.length).toBeGreaterThan(0);
  });
});
