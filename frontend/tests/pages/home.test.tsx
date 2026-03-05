import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import HomePage from "@/app/page";

vi.mock("next/link", () => ({
  default: ({ href, children, ...props }: Record<string, unknown>) => (
    <a href={href as string} {...props}>{children as React.ReactNode}</a>
  ),
}));

describe("HomePage", () => {
  it("히어로 제목이 렌더링된다", () => {
    render(<HomePage />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(/당신의 이야기를/);
  });

  it("서비스 소개 섹션이 존재한다", () => {
    render(<HomePage />);
    expect(screen.getByLabelText("서비스 소개")).toBeInTheDocument();
  });

  it("시작하기 CTA 링크가 존재한다", () => {
    render(<HomePage />);
    const cta = screen.getByLabelText("시작하기 - 회원가입 페이지로 이동");
    expect(cta).toBeInTheDocument();
    expect(cta).toHaveAttribute("href", "/signup");
  });

  it("3단계 이용 방법이 표시된다", () => {
    render(<HomePage />);
    expect(screen.getByText(/1단계: 말하기/)).toBeInTheDocument();
    expect(screen.getByText(/2단계: AI와 함께 쓰기/)).toBeInTheDocument();
    expect(screen.getByText(/3단계: 출판하기/)).toBeInTheDocument();
  });

  it("접근성 안내 섹션이 존재한다", () => {
    render(<HomePage />);
    expect(screen.getByLabelText("접근성 안내")).toBeInTheDocument();
    expect(screen.getByText(/WCAG 2.1 AA/)).toBeInTheDocument();
  });

  it("이용 방법 섹션이 존재한다", () => {
    render(<HomePage />);
    expect(screen.getByLabelText("이용 방법")).toBeInTheDocument();
  });
});
