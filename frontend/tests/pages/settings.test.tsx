import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import SettingsPage from "@/app/settings/page";

const mockUser = {
  display_name: "테스트작가",
  disability_type: "visual",
  voice_speed: 1.0,
  voice_type: "default",
};

let currentUser: typeof mockUser | null = null;
let authLoading = false;

vi.mock("@/hooks/useSupabase", () => ({
  useSupabase: () => ({
    user: currentUser,
    refreshUser: vi.fn(),
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

vi.mock("@/lib/api", () => ({
  auth: { updateSettings: vi.fn().mockResolvedValue({ data: {} }) },
  tts: { voices: vi.fn().mockResolvedValue({ data: { voices: [], total: 0 } }) },
}));

describe("SettingsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    currentUser = null;
    authLoading = false;
  });

  it("로딩 중 상태가 표시된다", () => {
    authLoading = true;
    render(<SettingsPage />);
    expect(screen.getByText("불러오는 중...")).toBeInTheDocument();
  });

  it("미인증 시 로그인 안내가 표시된다", () => {
    currentUser = null;
    render(<SettingsPage />);
    expect(screen.getByText("설정을 변경하려면 로그인해 주세요.")).toBeInTheDocument();
  });

  it("인증 시 설정 페이지가 렌더링된다", async () => {
    currentUser = mockUser;
    render(<SettingsPage />);
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "설정" })).toBeInTheDocument();
    });
  });

  it("필명 입력 필드가 사용자 이름으로 초기화된다", async () => {
    currentUser = mockUser;
    render(<SettingsPage />);
    await waitFor(() => {
      expect(screen.getByLabelText(/필명/)).toHaveValue("테스트작가");
    });
  });
});
