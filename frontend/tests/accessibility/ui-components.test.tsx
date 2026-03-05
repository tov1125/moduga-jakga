/**
 * A17 접근성 감사 에이전트 - UI 컴포넌트 접근성 테스트
 *
 * WCAG 2.1 AA 기준 검증:
 * - Perceivable: 대체 텍스트, 색상 독립, 확대 지원
 * - Operable: 키보드 조작, 포커스 표시, 시간 제한
 * - Understandable: 언어 명시, 오류 안내, 예측 가능
 * - Robust: 유효 마크업, ARIA 올바른 사용
 */
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Button } from "@/components/ui/Button";

// --- Button 접근성 테스트 ---
describe("Button 접근성", () => {
  it("버튼 역할(role)이 올바르게 설정됨", () => {
    render(<Button>저장</Button>);
    expect(screen.getByRole("button", { name: "저장" })).toBeInTheDocument();
  });

  it("aria-label로 버튼 목적을 설명할 수 있음", () => {
    render(<Button aria-label="녹음 시작">🎤</Button>);
    expect(screen.getByRole("button", { name: "녹음 시작" })).toBeInTheDocument();
  });

  it("토글 버튼에 aria-pressed가 설정됨", () => {
    render(
      <Button aria-pressed={true} aria-label="녹음 중">
        녹음
      </Button>
    );
    const button = screen.getByRole("button", { name: "녹음 중" });
    expect(button).toHaveAttribute("aria-pressed", "true");
  });

  it("로딩 상태에서 aria-busy가 설정됨", () => {
    render(<Button isLoading>저장 중</Button>);
    const button = screen.getByRole("button");
    expect(button).toHaveAttribute("aria-busy", "true");
  });

  it("로딩 상태에서 스크린리더용 텍스트 제공", () => {
    render(<Button isLoading>저장</Button>);
    expect(screen.getByText("처리 중입니다")).toBeInTheDocument();
  });

  it("비활성 상태에서 aria-disabled가 설정됨", () => {
    render(<Button disabled>제출</Button>);
    const button = screen.getByRole("button", { name: "제출" });
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute("aria-disabled", "true");
  });

  it("최소 터치 타겟 44x44px 이상 (min-h-touch, min-w-touch 클래스)", () => {
    render(<Button>테스트</Button>);
    const button = screen.getByRole("button", { name: "테스트" });
    // touch = 2.75rem = 44px 이 Tailwind config에 정의됨
    expect(button.className).toContain("min-h-touch");
    expect(button.className).toContain("min-w-touch");
  });

  it("포커스 표시가 명확함 (focus-visible 링 스타일)", () => {
    render(<Button>포커스 테스트</Button>);
    const button = screen.getByRole("button", { name: "포커스 테스트" });
    expect(button.className).toContain("focus-visible:ring-4");
    expect(button.className).toContain("focus-visible:ring-primary-600");
  });

  it("Enter 키로 버튼 활성화 가능", async () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>확인</Button>);
    const button = screen.getByRole("button", { name: "확인" });
    button.focus();
    await userEvent.keyboard("{Enter}");
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("Space 키로 버튼 활성화 가능", async () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>확인</Button>);
    const button = screen.getByRole("button", { name: "확인" });
    button.focus();
    await userEvent.keyboard(" ");
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("아이콘이 aria-hidden으로 스크린리더에서 숨겨짐", () => {
    render(
      <Button leftIcon={<span data-testid="icon">🔍</span>}>검색</Button>
    );
    const iconWrapper = screen.getByTestId("icon").parentElement;
    expect(iconWrapper).toHaveAttribute("aria-hidden", "true");
  });
});
