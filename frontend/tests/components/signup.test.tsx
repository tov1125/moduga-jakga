/**
 * 회원가입 페이지 테스트
 * 동의 체크박스 3개 조합에 따른 버튼 활성화 및 접근성을 검증합니다.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import SignupPage from "@/app/(auth)/signup/page";

vi.mock("@/hooks/useAnnouncer", () => ({
  useAnnouncer: () => ({
    announceAssertive: vi.fn(),
    announcePolite: vi.fn(),
  }),
}));

vi.mock("@/lib/api", () => ({
  auth: { signup: vi.fn() },
}));

describe("회원가입 페이지", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("초기 상태에서 회원가입 버튼이 disabled이다", () => {
    render(<SignupPage />);
    const submitButton = screen.getByRole("button", { name: "회원가입" });
    expect(submitButton).toBeDisabled();
  });

  it("체크박스 3개 모두 체크하면 회원가입 버튼이 enabled된다", async () => {
    const user = userEvent.setup();
    render(<SignupPage />);

    const checkboxes = screen.getAllByRole("checkbox");
    expect(checkboxes).toHaveLength(3);

    for (const checkbox of checkboxes) {
      await user.click(checkbox);
    }

    const submitButton = screen.getByRole("button", { name: "회원가입" });
    expect(submitButton).not.toBeDisabled();
  });

  it("체크박스 2개만 체크하면 버튼이 여전히 disabled이다", async () => {
    const user = userEvent.setup();
    render(<SignupPage />);

    const checkboxes = screen.getAllByRole("checkbox");
    await user.click(checkboxes[0]);
    await user.click(checkboxes[1]);

    const submitButton = screen.getByRole("button", { name: "회원가입" });
    expect(submitButton).toBeDisabled();
  });

  it("이메일 라벨이 input과 올바르게 연결되어 있다", () => {
    render(<SignupPage />);
    const emailInput = screen.getByLabelText(/이메일/);
    expect(emailInput).toBeInTheDocument();
    expect(emailInput).toHaveAttribute("id", "signup-email");
  });

  it("비밀번호 라벨이 input과 올바르게 연결되어 있다", () => {
    render(<SignupPage />);
    const passwordInput = screen.getByLabelText(/^비밀번호 \*$/);
    expect(passwordInput).toBeInTheDocument();
    expect(passwordInput).toHaveAttribute("id", "signup-password");
  });

  it("이름 라벨이 input과 올바르게 연결되어 있다", () => {
    render(<SignupPage />);
    const nameInput = screen.getByLabelText(/이름/);
    expect(nameInput).toBeInTheDocument();
    expect(nameInput).toHaveAttribute("id", "signup-name");
  });

  it("form에 '회원가입 양식' aria-label이 존재한다", () => {
    render(<SignupPage />);
    const form = screen.getByRole("form", { name: "회원가입 양식" });
    expect(form).toBeInTheDocument();
  });
});
