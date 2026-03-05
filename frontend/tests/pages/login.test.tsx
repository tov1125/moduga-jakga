import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import LoginPage from "@/app/(auth)/login/page";

vi.mock("next/link", () => ({
  default: ({ href, children, ...props }: Record<string, unknown>) => (
    <a href={href as string} {...props}>{children as React.ReactNode}</a>
  ),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("@/hooks/useAnnouncer", () => ({
  useAnnouncer: () => ({
    announcePolite: vi.fn(),
    announceAssertive: vi.fn(),
  }),
}));

vi.mock("@/hooks/useSupabase", () => ({
  useSupabase: () => ({ refreshUser: vi.fn() }),
}));

vi.mock("@/lib/api", () => ({
  auth: { login: vi.fn() },
}));

describe("LoginPage", () => {
  it("로그인 제목이 렌더링된다", () => {
    render(<LoginPage />);
    expect(screen.getByRole("heading", { level: 1, name: "로그인" })).toBeInTheDocument();
  });

  it("이메일 입력 필드가 존재한다", () => {
    render(<LoginPage />);
    expect(screen.getByLabelText("이메일")).toBeInTheDocument();
  });

  it("비밀번호 입력 필드가 존재한다", () => {
    render(<LoginPage />);
    expect(screen.getByLabelText("비밀번호")).toBeInTheDocument();
  });

  it("로그인 버튼이 존재한다", () => {
    render(<LoginPage />);
    expect(screen.getByRole("button", { name: "로그인" })).toBeInTheDocument();
  });

  it("회원가입 링크가 존재한다", () => {
    render(<LoginPage />);
    expect(screen.getByText("회원가입")).toBeInTheDocument();
  });

  it("양식에 aria-label이 설정되어 있다", () => {
    render(<LoginPage />);
    expect(screen.getByLabelText("로그인 양식")).toBeInTheDocument();
  });
});
