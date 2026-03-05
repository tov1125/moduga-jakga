import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import DashboardPage from "@/app/dashboard/page";

vi.mock("next/link", () => ({
  default: ({ href, children, ...props }: Record<string, unknown>) => (
    <a href={href as string} {...props}>{children as React.ReactNode}</a>
  ),
}));

const mockUser = { display_name: "작가" };
let currentUser: typeof mockUser | null = null;
let authLoading = false;

vi.mock("@/hooks/useSupabase", () => ({
  useSupabase: () => ({
    user: currentUser,
    isLoading: authLoading,
  }),
}));

vi.mock("@/hooks/useAnnouncer", () => ({
  useAnnouncer: () => ({
    announce: vi.fn(),
    announcePolite: vi.fn(),
    announceAssertive: vi.fn(),
  }),
}));

const mockList = vi.fn();
vi.mock("@/lib/api", () => ({
  books: { list: (...args: unknown[]) => mockList(...args) },
}));

describe("DashboardPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    currentUser = null;
    authLoading = false;
  });

  it("미인증 시 로그인 필요 메시지가 표시된다", () => {
    currentUser = null;
    authLoading = false;
    render(<DashboardPage />);
    expect(screen.getByText("로그인이 필요합니다")).toBeInTheDocument();
  });

  it("로딩 중 상태가 표시된다", () => {
    authLoading = true;
    render(<DashboardPage />);
    expect(screen.getByText("불러오는 중...")).toBeInTheDocument();
  });

  it("인증 후 빈 목록일 때 안내가 표시된다", async () => {
    currentUser = mockUser;
    mockList.mockResolvedValueOnce({ data: [] });
    render(<DashboardPage />);
    await waitFor(() => {
      expect(screen.getByText("아직 작품이 없습니다")).toBeInTheDocument();
    });
  });

  it("인증 후 작품 목록이 표시된다", async () => {
    currentUser = mockUser;
    mockList.mockResolvedValueOnce({
      data: [
        {
          id: "b1",
          title: "나의 에세이",
          genre: "essay",
          status: "writing",
          description: "테스트",
          chapter_count: 3,
          updated_at: new Date().toISOString(),
        },
      ],
    });
    render(<DashboardPage />);
    await waitFor(() => {
      expect(screen.getByText("나의 에세이")).toBeInTheDocument();
    });
  });

  it("새 작품 만들기 링크가 표시된다", async () => {
    currentUser = mockUser;
    mockList.mockResolvedValueOnce({ data: [] });
    render(<DashboardPage />);
    await waitFor(() => {
      expect(screen.getByLabelText("새 작품 만들기")).toBeInTheDocument();
    });
  });
});
