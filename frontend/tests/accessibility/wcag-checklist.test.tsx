/**
 * A17 접근성 감사 에이전트 - WCAG 2.1 AA 종합 체크리스트 테스트
 *
 * 이 파일은 agent.md의 accessibility_checklist 전체 항목을 검증합니다.
 * 각 카테고리별: Perceivable, Operable, Understandable, Robust
 */
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";

// --- Mocks ---
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn() }),
  usePathname: () => "/",
}));

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

vi.mock("@/hooks/useAnnouncer", () => ({
  useAnnouncer: () => ({
    announce: vi.fn(),
    announcePolite: vi.fn(),
    announceAssertive: vi.fn(),
  }),
}));

vi.mock("@/hooks/useSupabase", () => ({
  useSupabase: () => ({
    user: null,
    session: null,
    isLoading: false,
    signOut: vi.fn(),
  }),
}));

import { Button } from "@/components/ui/Button";
import { SkipLink } from "@/components/ui/SkipLink";

// --- Perceivable ---
describe("WCAG Perceivable (인식 가능)", () => {
  it("비텍스트 콘텐츠에 대체 텍스트가 존재 (아이콘 버튼)", () => {
    render(<Button aria-label="설정 열기">⚙️</Button>);
    expect(screen.getByRole("button", { name: "설정 열기" })).toBeInTheDocument();
  });

  it("색상만으로 정보를 전달하지 않음 (위험 버튼은 텍스트도 제공)", () => {
    render(<Button variant="destructive">삭제</Button>);
    const button = screen.getByRole("button", { name: "삭제" });
    // 빨간색뿐 아니라 "삭제" 텍스트로도 의미를 전달
    expect(button).toHaveTextContent("삭제");
  });
});

// --- Operable ---
describe("WCAG Operable (운용 가능)", () => {
  it("건너뛰기 링크(Skip Link)가 존재", () => {
    render(<SkipLink />);
    const skipLink = screen.getByText(/본문으로 건너뛰기|메인 콘텐츠로 이동/i);
    expect(skipLink).toBeInTheDocument();
  });

  it("포커스 표시가 명확함 (노란색 링 4px)", () => {
    render(<Button>테스트</Button>);
    const button = screen.getByRole("button");
    expect(button.className).toContain("focus-visible:ring-4");
    expect(button.className).toContain("focus-visible:ring-yellow-400");
  });

  it("비활성 버튼은 클릭 불가", async () => {
    const onClick = vi.fn();
    render(
      <Button disabled onClick={onClick}>
        비활성
      </Button>
    );
    const button = screen.getByRole("button");
    button.click();
    expect(onClick).not.toHaveBeenCalled();
  });
});

// --- Understandable ---
describe("WCAG Understandable (이해 가능)", () => {
  it("한국어 UI 텍스트가 올바르게 표시됨", () => {
    render(<Button isLoading>저장</Button>);
    expect(screen.getByText("처리 중입니다")).toBeInTheDocument();
  });
});

// --- Robust ---
describe("WCAG Robust (견고함)", () => {
  it("ARIA 역할이 올바르게 사용됨 (button)", () => {
    render(<Button>확인</Button>);
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  it("aria-hidden이 장식 요소에만 사용됨", () => {
    render(
      <Button leftIcon={<span data-testid="icon">🔍</span>}>검색</Button>
    );
    const iconWrapper = screen.getByTestId("icon").parentElement;
    expect(iconWrapper).toHaveAttribute("aria-hidden", "true");
    // 버튼 자체는 aria-hidden이 아님
    const button = screen.getByRole("button");
    expect(button).not.toHaveAttribute("aria-hidden");
  });
});
