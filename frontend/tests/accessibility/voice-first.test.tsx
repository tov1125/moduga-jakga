/**
 * A17 접근성 감사 에이전트 - Voice-First 접근성 테스트
 *
 * agent.md의 voice_first_specific 체크리스트:
 * - 모든 상태 변화에 TTS 피드백 존재
 * - 음성 명령으로 모든 핵심 기능 수행 가능
 * - STT/TTS 동시 사용 시 충돌 없음
 * - 오류 발생 시 음성으로 원인과 해결 방법 안내
 */
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

// --- Mock useSTT ---
const mockStartRecording = vi.fn();
const mockStopRecording = vi.fn();
const mockClearTranscript = vi.fn();
let mockSTTState = {
  isRecording: false,
  transcript: "",
  interimTranscript: "",
  error: null as string | null,
};

vi.mock("@/hooks/useSTT", () => ({
  useSTT: () => ({
    startRecording: mockStartRecording,
    stopRecording: mockStopRecording,
    clearTranscript: mockClearTranscript,
    ...mockSTTState,
  }),
}));

import { VoiceRecorder } from "@/components/voice/VoiceRecorder";

describe("VoiceRecorder 접근성 (Voice-First)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockSTTState = {
      isRecording: false,
      transcript: "",
      interimTranscript: "",
      error: null,
    };
  });

  it("녹음 버튼에 명확한 aria-label이 있음", () => {
    render(<VoiceRecorder />);
    expect(
      screen.getByRole("button", { name: "녹음 시작" })
    ).toBeInTheDocument();
  });

  it("녹음 중일 때 aria-label이 '녹음 중지'로 변경됨", () => {
    mockSTTState.isRecording = true;
    render(<VoiceRecorder />);
    expect(
      screen.getByRole("button", { name: "녹음 중지" })
    ).toBeInTheDocument();
  });

  it("녹음 중일 때 aria-pressed='true'가 설정됨", () => {
    mockSTTState.isRecording = true;
    render(<VoiceRecorder />);
    const btn = screen.getByRole("button", { name: "녹음 중지" });
    expect(btn).toHaveAttribute("aria-pressed", "true");
  });

  it("녹음 상태가 aria-live 영역으로 실시간 알림됨", () => {
    render(<VoiceRecorder />);
    const statusText = screen.getByText("마이크 버튼을 눌러 녹음을 시작하세요");
    expect(statusText).toHaveAttribute("aria-live", "polite");
  });

  it("녹음 중일 때 상태 텍스트가 '녹음 중...'으로 변경됨", () => {
    mockSTTState.isRecording = true;
    render(<VoiceRecorder />);
    const statusText = screen.getByText("녹음 중...");
    expect(statusText).toHaveAttribute("aria-live", "polite");
  });

  it("오류 발생 시 role='alert'로 즉시 알림됨", () => {
    mockSTTState.error = "마이크 접근 권한이 필요합니다";
    render(<VoiceRecorder />);
    const errorMsg = screen.getByRole("alert");
    expect(errorMsg).toHaveTextContent("마이크 접근 권한이 필요합니다");
  });

  it("인식 결과 영역에 aria-label과 aria-live가 있음", () => {
    mockSTTState.transcript = "안녕하세요";
    render(<VoiceRecorder />);
    const resultArea = screen.getByLabelText("음성 인식 결과");
    expect(resultArea).toHaveAttribute("aria-live", "polite");
  });

  it("결과 지우기 버튼에 접근성 레이블이 있음", () => {
    mockSTTState.transcript = "테스트 텍스트";
    mockSTTState.isRecording = false;
    render(<VoiceRecorder />);
    expect(
      screen.getByRole("button", { name: "음성 인식 결과 지우기" })
    ).toBeInTheDocument();
  });

  it("SVG 아이콘이 aria-hidden으로 스크린리더에서 숨겨짐", () => {
    render(<VoiceRecorder />);
    const svgs = document.querySelectorAll("svg");
    svgs.forEach((svg) => {
      expect(svg).toHaveAttribute("aria-hidden", "true");
    });
  });
});
