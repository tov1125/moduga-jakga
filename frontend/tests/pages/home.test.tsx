import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import HomePage from "@/app/page";

describe("HomePage", () => {
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

  it("로그인 링크가 존재한다", () => {
    render(<HomePage />);
    const login = screen.getByLabelText("로그인 페이지로 이동");
    expect(login).toBeInTheDocument();
    expect(login).toHaveAttribute("href", "/login");
  });

  it("3단계 이용 방법이 표시된다", () => {
    render(<HomePage />);
    expect(screen.getByText("말하기")).toBeInTheDocument();
    expect(screen.getByText("AI와 함께 쓰기")).toBeInTheDocument();
    expect(screen.getByText("출판하기")).toBeInTheDocument();
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

  it("작품 샘플 캐러셀이 존재한다", () => {
    render(<HomePage />);
    expect(screen.getByLabelText("작품 샘플 캐러셀")).toBeInTheDocument();
  });

  it("최종 CTA 섹션이 존재한다", () => {
    render(<HomePage />);
    const finalCta = screen.getByLabelText(
      "무료로 시작하기 - 회원가입 페이지로 이동",
    );
    expect(finalCta).toBeInTheDocument();
    expect(finalCta).toHaveAttribute("href", "/signup");
  });
});
