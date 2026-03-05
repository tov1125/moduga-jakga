/**
 * Header 컴포넌트 테스트
 * 로고, 네비게이션 링크, 테마 토글, 인증 상태별 렌더링을 검증합니다.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { Header } from "@/components/layout/Header";

// --- Mocks ---
const mockSignOut = vi.fn();
const mockPush = vi.fn();
let mockUser: { display_name: string } | null = null;

vi.mock("@/hooks/useSupabase", () => ({
  useSupabase: () => ({
    user: mockUser,
    signOut: mockSignOut,
    isLoading: false,
  }),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
  usePathname: () => "/",
}));

vi.mock("next/link", () => ({
  default: ({ href, children, ...props }: Record<string, unknown>) => (
    <a href={href as string} {...props}>{children as React.ReactNode}</a>
  ),
}));

vi.mock("@/components/ui/ThemeToggle", () => ({
  ThemeToggle: () => <button aria-label="테마 변경">테마</button>,
}));

describe("Header", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUser = null;
  });

  it("로고 '모두가 작가'가 렌더링된다", () => {
    render(<Header />);
    expect(screen.getByText("모두가 작가")).toBeInTheDocument();
  });

  it("로고에 홈 링크가 설정되어 있다", () => {
    render(<Header />);
    const logo = screen.getByLabelText("모두가 작가 - 홈으로 이동");
    expect(logo).toBeInTheDocument();
  });

  it("미인증 시 로그인/회원가입 링크가 표시된다", () => {
    render(<Header />);
    expect(screen.getByLabelText("로그인")).toBeInTheDocument();
    expect(screen.getByLabelText("회원가입")).toBeInTheDocument();
  });

  it("인증 시 사용자 이름과 로그아웃 버튼이 표시된다", () => {
    mockUser = { display_name: "테스트작가" };
    render(<Header />);
    expect(screen.getByText("테스트작가님")).toBeInTheDocument();
    expect(screen.getByLabelText("로그아웃")).toBeInTheDocument();
  });

  it("인증 시 설정 링크가 표시된다", () => {
    mockUser = { display_name: "작가" };
    render(<Header />);
    expect(screen.getByLabelText("설정")).toBeInTheDocument();
  });

  it("테마 토글이 존재한다", () => {
    render(<Header />);
    expect(screen.getByLabelText("테마 변경")).toBeInTheDocument();
  });

  it("banner 역할이 설정되어 있다", () => {
    render(<Header />);
    expect(screen.getByRole("banner")).toBeInTheDocument();
  });
});
