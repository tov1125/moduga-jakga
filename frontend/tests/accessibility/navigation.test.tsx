/**
 * A17 접근성 감사 에이전트 - 네비게이션 접근성 테스트
 *
 * WCAG 2.1 Operable 기준:
 * - 모든 기능이 키보드만으로 조작 가능
 * - 키보드 포커스 표시가 명확
 * - 포커스 순서가 논리적
 * - aria-current="page"로 현재 위치 표시
 */
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";

// next/navigation 모킹
let mockPathname = "/dashboard";
vi.mock("next/navigation", () => ({
  usePathname: () => mockPathname,
}));

// next/link 모킹
vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    ...props
  }: {
    children: React.ReactNode;
    href: string;
    [key: string]: unknown;
  }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

import { Navigation } from "@/components/layout/Navigation";

describe("Navigation 접근성", () => {
  beforeEach(() => {
    mockPathname = "/dashboard";
  });

  it("nav 요소에 aria-label이 있음", () => {
    render(<Navigation />);
    expect(screen.getByRole("navigation")).toHaveAttribute(
      "aria-label",
      "주요 탐색"
    );
  });

  it("메뉴 역할(role='menubar')이 설정됨", () => {
    render(<Navigation />);
    expect(screen.getByRole("menubar")).toBeInTheDocument();
  });

  it("메뉴 아이템에 role='menuitem'이 설정됨", () => {
    render(<Navigation />);
    const menuItems = screen.getAllByRole("menuitem");
    expect(menuItems).toHaveLength(3);
  });

  it("현재 페이지에 aria-current='page'가 설정됨", () => {
    mockPathname = "/dashboard";
    render(<Navigation />);
    const dashboardLink = screen.getByRole("menuitem", { name: /대시보드/ });
    expect(dashboardLink).toHaveAttribute("aria-current", "page");
  });

  it("비활성 페이지에는 aria-current가 없음", () => {
    mockPathname = "/dashboard";
    render(<Navigation />);
    const writeLink = screen.getByRole("menuitem", { name: "글쓰기" });
    expect(writeLink).not.toHaveAttribute("aria-current");
  });

  it("현재 페이지에 스크린리더용 '(현재 페이지)' 텍스트가 있음", () => {
    mockPathname = "/write";
    render(<Navigation />);
    expect(screen.getByText("(현재 페이지)")).toBeInTheDocument();
  });

  it("포커스 링 스타일이 적용됨", () => {
    render(<Navigation />);
    const menuItems = screen.getAllByRole("menuitem");
    menuItems.forEach((item) => {
      expect(item.className).toContain("focus-visible:ring-4");
      expect(item.className).toContain("focus-visible:ring-primary-600");
    });
  });

  it("최소 터치 타겟 44px (min-h-touch)", () => {
    render(<Navigation />);
    const menuItems = screen.getAllByRole("menuitem");
    menuItems.forEach((item) => {
      expect(item.className).toContain("min-h-touch");
    });
  });

  it("오른쪽 방향키로 다음 메뉴 아이템으로 이동", () => {
    render(<Navigation />);
    const nav = screen.getByRole("navigation");
    const menuItems = screen.getAllByRole("menuitem");

    // 첫 번째 아이템에 포커스
    menuItems[0].focus();
    expect(document.activeElement).toBe(menuItems[0]);

    // ArrowRight
    fireEvent.keyDown(nav, { key: "ArrowRight" });
    expect(document.activeElement).toBe(menuItems[1]);
  });

  it("왼쪽 방향키로 이전 메뉴 아이템으로 이동", () => {
    render(<Navigation />);
    const nav = screen.getByRole("navigation");
    const menuItems = screen.getAllByRole("menuitem");

    menuItems[1].focus();
    fireEvent.keyDown(nav, { key: "ArrowLeft" });
    expect(document.activeElement).toBe(menuItems[0]);
  });

  it("Home 키로 첫 번째 아이템으로 이동", () => {
    render(<Navigation />);
    const nav = screen.getByRole("navigation");
    const menuItems = screen.getAllByRole("menuitem");

    menuItems[2].focus();
    fireEvent.keyDown(nav, { key: "Home" });
    expect(document.activeElement).toBe(menuItems[0]);
  });

  it("End 키로 마지막 아이템으로 이동", () => {
    render(<Navigation />);
    const nav = screen.getByRole("navigation");
    const menuItems = screen.getAllByRole("menuitem");

    menuItems[0].focus();
    fireEvent.keyDown(nav, { key: "End" });
    expect(document.activeElement).toBe(menuItems[2]);
  });

  it("마지막 아이템에서 오른쪽 방향키로 첫 번째 아이템으로 순환", () => {
    render(<Navigation />);
    const nav = screen.getByRole("navigation");
    const menuItems = screen.getAllByRole("menuitem");

    menuItems[2].focus();
    fireEvent.keyDown(nav, { key: "ArrowRight" });
    expect(document.activeElement).toBe(menuItems[0]);
  });
});
