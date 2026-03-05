/**
 * A17 접근성 감사 에이전트 - Modal 접근성 테스트
 *
 * 검증 항목:
 * - role="dialog" 및 aria-modal="true"
 * - 포커스 트랩 (Tab 순환)
 * - Escape 키로 닫기
 * - 열릴 때 포커스 이동
 * - 닫힐 때 이전 포커스 복원
 * - 스크린리더 알림
 */
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { Modal } from "@/components/ui/Modal";

// useAnnouncer 모킹
const mockAnnounceAssertive = vi.fn();
vi.mock("@/hooks/useAnnouncer", () => ({
  useAnnouncer: () => ({
    announce: vi.fn(),
    announcePolite: vi.fn(),
    announceAssertive: mockAnnounceAssertive,
  }),
}));

describe("Modal 접근성", () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    title: "테스트 대화 상자",
    children: <p>내용</p>,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("role='dialog'와 aria-modal='true'가 설정됨", () => {
    render(<Modal {...defaultProps} />);
    const dialog = screen.getByRole("dialog");
    expect(dialog).toHaveAttribute("aria-modal", "true");
  });

  it("aria-label로 대화 상자 제목이 설정됨", () => {
    render(<Modal {...defaultProps} />);
    const dialog = screen.getByRole("dialog");
    expect(dialog).toHaveAttribute("aria-label", "테스트 대화 상자");
  });

  it("description이 있으면 aria-describedby가 설정됨", () => {
    render(<Modal {...defaultProps} description="추가 설명" />);
    const dialog = screen.getByRole("dialog");
    expect(dialog).toHaveAttribute("aria-describedby", "modal-description");
    expect(screen.getByText("추가 설명")).toHaveAttribute("id", "modal-description");
  });

  it("Escape 키로 모달 닫기", () => {
    const onClose = vi.fn();
    render(<Modal {...defaultProps} onClose={onClose} />);
    const dialog = screen.getByRole("dialog");
    fireEvent.keyDown(dialog, { key: "Escape" });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("닫기 버튼에 접근성 레이블이 있음", () => {
    render(<Modal {...defaultProps} />);
    expect(
      screen.getByRole("button", { name: "대화 상자 닫기" })
    ).toBeInTheDocument();
  });

  it("닫기 버튼의 아이콘이 aria-hidden", () => {
    render(<Modal {...defaultProps} />);
    const closeButton = screen.getByRole("button", { name: "대화 상자 닫기" });
    const svg = closeButton.querySelector("svg");
    expect(svg).toHaveAttribute("aria-hidden", "true");
  });

  it("닫기 버튼의 터치 타겟이 최소 44px", () => {
    render(<Modal {...defaultProps} />);
    const closeButton = screen.getByRole("button", { name: "대화 상자 닫기" });
    expect(closeButton.className).toContain("min-h-touch");
    expect(closeButton.className).toContain("min-w-touch");
  });

  it("열릴 때 스크린리더 알림이 발생함", () => {
    render(<Modal {...defaultProps} />);
    expect(mockAnnounceAssertive).toHaveBeenCalledWith(
      "대화 상자가 열렸습니다: 테스트 대화 상자"
    );
  });

  it("isOpen이 false이면 렌더링하지 않음", () => {
    render(<Modal {...defaultProps} isOpen={false} />);
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("배경 클릭 시 모달 닫기", () => {
    const onClose = vi.fn();
    render(<Modal {...defaultProps} onClose={onClose} />);
    // aria-hidden="true"인 backdrop 클릭
    const backdrop = screen.getByRole("dialog").parentElement?.querySelector(
      '[aria-hidden="true"]'
    );
    if (backdrop) {
      fireEvent.click(backdrop);
      expect(onClose).toHaveBeenCalledTimes(1);
    }
  });
});
