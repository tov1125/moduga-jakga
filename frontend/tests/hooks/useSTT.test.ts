/**
 * useSTT Hook 테스트
 * WebSocket 기반 STT 녹음 시작/중지, 인증/설정 메시지, 에러 처리를 검증합니다.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import React from "react";

// --- Hoisted Mocks ---
const {
  mockSetSttState,
  mockPauseTtsForStt,
  mockResumeTtsAfterStt,
  mockSetTranscript,
  mockAnnounceAssertive,
  mockAnnouncePolite,
} = vi.hoisted(() => ({
  mockSetSttState: vi.fn(),
  mockPauseTtsForStt: vi.fn(),
  mockResumeTtsAfterStt: vi.fn(),
  mockSetTranscript: vi.fn(),
  mockAnnounceAssertive: vi.fn(),
  mockAnnouncePolite: vi.fn(),
}));

vi.mock("@/providers/VoiceProvider", () => ({
  VoiceContext: React.createContext({
    sttState: "idle",
    setSttState: mockSetSttState,
    isRecording: false,
    transcript: "",
    setTranscript: mockSetTranscript,
    ttsState: "idle",
    setTtsState: vi.fn(),
    isPlaying: false,
    isPaused: false,
    ttsSpeed: 1.0,
    setTtsSpeed: vi.fn(),
    pauseTtsForStt: mockPauseTtsForStt,
    resumeTtsAfterStt: mockResumeTtsAfterStt,
  }),
}));

vi.mock("@/hooks/useAnnouncer", () => ({
  useAnnouncer: () => ({
    announceAssertive: mockAnnounceAssertive,
    announcePolite: mockAnnouncePolite,
  }),
}));

// setup.ts에서 MediaRecorder, AudioContext, navigator.mediaDevices가 이미 글로벌 mock됨
// getUserMedia mock을 테스트별로 제어하기 위해 참조
const mockGetUserMedia = globalThis.navigator.mediaDevices
  .getUserMedia as ReturnType<typeof vi.fn>;

// Mock localStorage
const mockLocalStorage: Record<string, string> = {};
vi.stubGlobal("localStorage", {
  getItem: (key: string) => mockLocalStorage[key] ?? null,
  setItem: (key: string, val: string) => {
    mockLocalStorage[key] = val;
  },
});

import { useSTT } from "@/hooks/useSTT";

describe("useSTT", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    delete mockLocalStorage["access_token"];
    mockGetUserMedia.mockResolvedValue({
      getTracks: () => [{ stop: vi.fn() }],
    });
  });

  it("초기 상태: isRecording=false, transcript=빈문자열, error=null", () => {
    const { result } = renderHook(() => useSTT());
    expect(result.current.isRecording).toBe(false);
    expect(result.current.transcript).toBe("");
    expect(result.current.error).toBeNull();
  });

  it("startRecording 호출 시 getUserMedia를 요청한다", async () => {
    const { result } = renderHook(() => useSTT());

    await act(async () => {
      await result.current.startRecording();
    });

    expect(mockGetUserMedia).toHaveBeenCalledWith({
      audio: expect.objectContaining({
        echoCancellation: true,
        noiseSuppression: true,
      }),
    });
  });

  it("startRecording 시 TTS를 일시정지한다", async () => {
    const { result } = renderHook(() => useSTT());

    await act(async () => {
      await result.current.startRecording();
    });

    expect(mockPauseTtsForStt).toHaveBeenCalled();
  });

  it("stopRecording 호출 시 TTS를 재개하고 announcePolite 호출", () => {
    const { result } = renderHook(() => useSTT());

    act(() => {
      result.current.stopRecording();
    });

    expect(mockResumeTtsAfterStt).toHaveBeenCalled();
    expect(mockAnnouncePolite).toHaveBeenCalledWith("녹음을 중지합니다");
  });

  it("clearTranscript 호출 시 transcript가 초기화된다", () => {
    const { result } = renderHook(() => useSTT());

    act(() => {
      result.current.clearTranscript();
    });

    expect(result.current.transcript).toBe("");
    expect(result.current.interimTranscript).toBe("");
  });

  it("마이크 권한 거부 시 에러 메시지 설정", async () => {
    mockGetUserMedia.mockRejectedValueOnce(
      Object.assign(new DOMException("Not allowed", "NotAllowedError"))
    );

    const { result } = renderHook(() => useSTT());

    await act(async () => {
      await result.current.startRecording();
    });

    expect(result.current.error).toContain("마이크 사용 권한");
    expect(mockAnnounceAssertive).toHaveBeenCalled();
  });

  it("마이크 일반 에러 시 일반 에러 메시지 설정", async () => {
    mockGetUserMedia.mockRejectedValueOnce(new Error("Device not found"));

    const { result } = renderHook(() => useSTT());

    await act(async () => {
      await result.current.startRecording();
    });

    expect(result.current.error).toBe("마이크를 사용할 수 없습니다");
  });

  it("반환 인터페이스가 올바른 타입을 가진다", () => {
    const { result } = renderHook(() => useSTT());

    expect(typeof result.current.startRecording).toBe("function");
    expect(typeof result.current.stopRecording).toBe("function");
    expect(typeof result.current.clearTranscript).toBe("function");
    expect(typeof result.current.isRecording).toBe("boolean");
    expect(typeof result.current.transcript).toBe("string");
    expect(typeof result.current.interimTranscript).toBe("string");
  });
});
