/**
 * ThemeToggle 컴포넌트 테스트
 * 테마 순환(dark -> light -> system -> dark)과 aria-label 변경을 검증합니다.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ThemeToggle } from "@/components/ui/ThemeToggle";

let mockTheme = "dark";
const mockSetTheme = vi.fn();

vi.mock("next-themes", () => ({
  useTheme: () => ({
    theme: mockTheme,
    setTheme: mockSetTheme,
  }),
}));

describe("ThemeToggle", () => {
  beforeEach(() => {
    mockTheme = "dark";
    mockSetTheme.mockClear();
  });

  it("마운트 후 버튼이 렌더링된다", () => {
    render(<ThemeToggle />);
    const button = screen.getByRole("button");
    expect(button).toBeInTheDocument();
    expect(button).not.toBeDisabled();
  });

  it("dark 모드에서 aria-label이 '라이트 모드로 전환'이다", () => {
    mockTheme = "dark";
    render(<ThemeToggle />);
    const button = screen.getByRole("button");
    expect(button).toHaveAttribute("aria-label", "라이트 모드로 전환");
  });

  it("light 모드에서 aria-label이 '시스템 테마로 전환'이다", () => {
    mockTheme = "light";
    render(<ThemeToggle />);
    const button = screen.getByRole("button");
    expect(button).toHaveAttribute("aria-label", "시스템 테마로 전환");
  });

  it("system 모드에서 aria-label이 '다크 모드로 전환'이다", () => {
    mockTheme = "system";
    render(<ThemeToggle />);
    const button = screen.getByRole("button");
    expect(button).toHaveAttribute("aria-label", "다크 모드로 전환");
  });

  it("dark 모드에서 클릭 시 setTheme('light')가 호출된다", () => {
    mockTheme = "dark";
    render(<ThemeToggle />);
    fireEvent.click(screen.getByRole("button"));
    expect(mockSetTheme).toHaveBeenCalledWith("light");
  });

  it("light 모드에서 클릭 시 setTheme('system')이 호출된다", () => {
    mockTheme = "light";
    render(<ThemeToggle />);
    fireEvent.click(screen.getByRole("button"));
    expect(mockSetTheme).toHaveBeenCalledWith("system");
  });

  it("system 모드에서 클릭 시 setTheme('dark')가 호출된다", () => {
    mockTheme = "system";
    render(<ThemeToggle />);
    fireEvent.click(screen.getByRole("button"));
    expect(mockSetTheme).toHaveBeenCalledWith("dark");
  });
});
