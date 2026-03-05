import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import TermsPage from "@/app/terms/page";

describe("TermsPage", () => {
  it("페이지 제목이 렌더링된다", () => {
    render(<TermsPage />);
    expect(screen.getByRole("heading", { level: 1, name: "이용약관" })).toBeInTheDocument();
  });

  it("6개 조항 heading이 모두 표시된다", () => {
    render(<TermsPage />);
    expect(screen.getByText("제1조 (목적)")).toBeInTheDocument();
    expect(screen.getByText("제2조 (서비스 내용)")).toBeInTheDocument();
    expect(screen.getByText("제3조 (AI 생성물의 저작권)")).toBeInTheDocument();
    expect(screen.getByText("제4조 (이용자의 의무)")).toBeInTheDocument();
    expect(screen.getByText("제5조 (서비스 제한 및 중단)")).toBeInTheDocument();
    expect(screen.getByText("제6조 (면책 조항)")).toBeInTheDocument();
  });

  it("article 요소로 감싸져 있다", () => {
    render(<TermsPage />);
    expect(screen.getByRole("article")).toBeInTheDocument();
  });

  it("시행일이 표시된다", () => {
    render(<TermsPage />);
    expect(screen.getByText(/시행일: 2026년 3월 1일/)).toBeInTheDocument();
  });
});
