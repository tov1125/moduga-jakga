/**
 * useTTS Hook 테스트
 * TTS 음성 재생/일시정지/중지, 속도 조절, 문장 탐색을 검증합니다.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import React from "react";

// --- Hoisted Mocks ---
const {
  mockSetTtsState,
  mockAnnouncePolite,
  mockAnnounceAssertive,
  mockSynthesize,
  mockTtsSpeedRef,
} = vi.hoisted(() => {
  const speedRef = { value: 1.0 };
  return {
    mockSetTtsState: vi.fn(),
    mockAnnouncePolite: vi.fn(),
    mockAnnounceAssertive: vi.fn(),
    mockSynthesize: vi.fn().mockResolvedValue(new ArrayBuffer(100)),
    mockTtsSpeedRef: speedRef,
  };
});

vi.mock("@/providers/VoiceProvider", () => ({
  VoiceContext: React.createContext({
    sttState: "idle",
    setSttState: vi.fn(),
    isRecording: false,
    transcript: "",
    setTranscript: vi.fn(),
    ttsState: "idle",
    setTtsState: mockSetTtsState,
    isPlaying: false,
    isPaused: false,
    ttsSpeed: 1.0,
    setTtsSpeed: (s: number) => {
      mockTtsSpeedRef.value = s;
    },
    pauseTtsForStt: vi.fn(),
    resumeTtsAfterStt: vi.fn(),
  }),
}));

vi.mock("@/hooks/useAnnouncer", () => ({
  useAnnouncer: () => ({
    announcePolite: mockAnnouncePolite,
    announceAssertive: mockAnnounceAssertive,
  }),
}));

// Mock TTS API
vi.mock("@/lib/api", () => ({
  tts: {
    synthesize: (...args: unknown[]) => mockSynthesize(...args),
  },
}));

// Mock clamp
vi.mock("@/lib/utils", () => ({
  clamp: (val: number, min: number, max: number) =>
    Math.min(Math.max(val, min), max),
}));

// setup.ts에서 AudioContext가 이미 글로벌 mock됨

import { useTTS } from "@/hooks/useTTS";

describe("useTTS", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockTtsSpeedRef.value = 1.0;
  });

  it("초기 상태: isPlaying=false, isPaused=false, speed=1.0", () => {
    const { result } = renderHook(() => useTTS());
    expect(result.current.isPlaying).toBe(false);
    expect(result.current.isPaused).toBe(false);
    expect(result.current.speed).toBe(1.0);
    expect(result.current.error).toBeNull();
  });

  it("setSpeed로 속도 변경 시 clamp(0.5~2.0) 적용", () => {
    const { result } = renderHook(() => useTTS());

    act(() => {
      result.current.setSpeed(3.0);
    });
    // clamp(3.0, 0.5, 2.0) = 2.0
    expect(mockTtsSpeedRef.value).toBeLessThanOrEqual(2.0);
  });

  it("stop 호출 시 announcePolite('낭독을 중지합니다') 호출", () => {
    const { result } = renderHook(() => useTTS());

    act(() => {
      result.current.stop();
    });

    expect(mockSetTtsState).toHaveBeenCalledWith("idle");
    expect(mockAnnouncePolite).toHaveBeenCalledWith("낭독을 중지합니다");
  });

  it("totalSentences가 초기 0", () => {
    const { result } = renderHook(() => useTTS());
    expect(result.current.totalSentences).toBe(0);
    expect(result.current.currentSentence).toBe(0);
  });

  it("반환 인터페이스가 올바른 타입을 가진다", () => {
    const { result } = renderHook(() => useTTS());

    expect(typeof result.current.speak).toBe("function");
    expect(typeof result.current.pause).toBe("function");
    expect(typeof result.current.resume).toBe("function");
    expect(typeof result.current.stop).toBe("function");
    expect(typeof result.current.skipForward).toBe("function");
    expect(typeof result.current.skipBackward).toBe("function");
    expect(typeof result.current.setSpeed).toBe("function");
    expect(typeof result.current.isPlaying).toBe("boolean");
    expect(typeof result.current.isPaused).toBe("boolean");
    expect(typeof result.current.speed).toBe("number");
    expect(typeof result.current.currentSentence).toBe("number");
    expect(typeof result.current.totalSentences).toBe("number");
  });

  it("speak 호출 시 문장 분할 및 TTS API 호출", async () => {
    const { result } = renderHook(() => useTTS());

    await act(async () => {
      await result.current.speak("첫 번째 문장. 두 번째 문장.");
    });

    expect(mockAnnouncePolite).toHaveBeenCalledWith("낭독을 시작합니다");
    expect(mockSynthesize).toHaveBeenCalled();
  });

  it("빈 텍스트로 speak 호출 시 아무 동작 없음", async () => {
    const { result } = renderHook(() => useTTS());

    await act(async () => {
      await result.current.speak("");
    });

    expect(mockSynthesize).not.toHaveBeenCalled();
  });

  it("speak 중 API 에러 시 에러 메시지 설정", async () => {
    mockSynthesize.mockRejectedValueOnce(new Error("TTS API error"));

    const { result } = renderHook(() => useTTS());

    await act(async () => {
      await result.current.speak("테스트 문장.");
    });

    expect(result.current.error).toBe("음성 합성 중 오류가 발생했습니다");
    expect(mockAnnounceAssertive).toHaveBeenCalled();
  });
});
