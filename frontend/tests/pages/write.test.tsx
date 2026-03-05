import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import NewWritePage from "@/app/write/page";

const mockPush = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
}));

vi.mock("@/hooks/useAnnouncer", () => ({
  useAnnouncer: () => ({
    announce: vi.fn(),
    announcePolite: vi.fn(),
    announceAssertive: vi.fn(),
  }),
}));

vi.mock("@/lib/api", () => ({
  books: {
    create: vi.fn(),
  },
}));

describe("NewWritePage", () => {
  it("제목이 렌더링된다", () => {
    render(<NewWritePage />);
    expect(screen.getByRole("heading", { level: 1, name: "새 작품 만들기" })).toBeInTheDocument();
  });

  it("작품 제목 입력 필드가 존재한다", () => {
    render(<NewWritePage />);
    expect(screen.getByLabelText(/작품 제목/)).toBeInTheDocument();
  });

  it("4개 장르 라디오 버튼이 표시된다", () => {
    render(<NewWritePage />);
    const radios = screen.getAllByRole("radio");
    expect(radios).toHaveLength(4);
    expect(screen.getByText("에세이")).toBeInTheDocument();
    expect(screen.getByText("소설")).toBeInTheDocument();
    expect(screen.getByText("시")).toBeInTheDocument();
    expect(screen.getByText("자서전")).toBeInTheDocument();
  });

  it("에세이가 기본 선택되어 있다", () => {
    render(<NewWritePage />);
    const radios = screen.getAllByRole("radio");
    const essayRadio = radios.find((r) => r.getAttribute("value") === "essay");
    expect(essayRadio).toBeChecked();
  });

  it("설명 textarea가 존재한다", () => {
    render(<NewWritePage />);
    expect(screen.getByLabelText(/간단한 설명/)).toBeInTheDocument();
  });

  it("글쓰기 시작 버튼이 존재한다", () => {
    render(<NewWritePage />);
    expect(screen.getByLabelText("글쓰기 시작")).toBeInTheDocument();
  });

  it("양식 aria-label이 설정되어 있다", () => {
    render(<NewWritePage />);
    expect(screen.getByLabelText("새 작품 만들기 양식")).toBeInTheDocument();
  });

  it("장르 radiogroup이 존재한다", () => {
    render(<NewWritePage />);
    expect(screen.getByRole("radiogroup", { name: "장르 선택" })).toBeInTheDocument();
  });
});
