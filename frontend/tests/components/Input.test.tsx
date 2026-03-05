import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Input } from "@/components/ui/input";

describe("Input", () => {
  it("기본 input이 렌더링된다", () => {
    render(<Input aria-label="테스트 입력" />);
    expect(screen.getByLabelText("테스트 입력")).toBeInTheDocument();
  });

  it("type이 올바르게 전달된다", () => {
    render(<Input type="email" aria-label="이메일" />);
    expect(screen.getByLabelText("이메일")).toHaveAttribute("type", "email");
  });

  it("placeholder가 표시된다", () => {
    render(<Input placeholder="입력하세요" />);
    expect(screen.getByPlaceholderText("입력하세요")).toBeInTheDocument();
  });

  it("disabled 상태가 적용된다", () => {
    render(<Input disabled aria-label="비활성" />);
    expect(screen.getByLabelText("비활성")).toBeDisabled();
  });

  it("className이 병합된다", () => {
    render(<Input className="custom-class" aria-label="커스텀" />);
    expect(screen.getByLabelText("커스텀")).toHaveClass("custom-class");
  });
});
