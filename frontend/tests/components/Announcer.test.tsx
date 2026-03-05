import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Announcer } from "@/components/ui/Announcer";

describe("Announcer", () => {
  it("polite 모드로 렌더링된다 (기본값)", () => {
    render(<Announcer message="안내 메시지" />);
    const el = screen.getByRole("status");
    expect(el).toBeInTheDocument();
    expect(el).toHaveAttribute("aria-live", "polite");
    expect(el).toHaveTextContent("안내 메시지");
  });

  it("assertive 모드로 렌더링된다", () => {
    render(<Announcer message="긴급 메시지" mode="assertive" />);
    const el = screen.getByRole("alert");
    expect(el).toBeInTheDocument();
    expect(el).toHaveAttribute("aria-live", "assertive");
    expect(el).toHaveTextContent("긴급 메시지");
  });

  it("aria-atomic 속성이 true이다", () => {
    render(<Announcer message="테스트" />);
    expect(screen.getByRole("status")).toHaveAttribute("aria-atomic", "true");
  });

  it("sr-only 클래스로 시각적으로 숨겨진다", () => {
    render(<Announcer message="숨겨진 메시지" />);
    expect(screen.getByRole("status")).toHaveClass("sr-only");
  });
});
