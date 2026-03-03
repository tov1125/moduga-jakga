/**
 * useVoiceCommand 훅 테스트
 * 한국어 음성 명령 파싱 및 자동 클리어 기능 검증
 */
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useVoiceCommand } from "@/hooks/useVoiceCommand";

describe("useVoiceCommand", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("초기 상태는 command가 null이다", () => {
    const { result } = renderHook(() => useVoiceCommand());
    expect(result.current.command).toBeNull();
  });

  it("'다음' 명령을 인식한다", () => {
    const { result } = renderHook(() => useVoiceCommand());

    act(() => {
      result.current.processTranscript("다음");
    });

    expect(result.current.command).not.toBeNull();
    expect(result.current.command?.type).toBe("next");
  });

  it("'이전' 명령을 인식한다", () => {
    const { result } = renderHook(() => useVoiceCommand());

    act(() => {
      result.current.processTranscript("이전");
    });

    expect(result.current.command?.type).toBe("previous");
  });

  it("'수정' 명령을 인식한다", () => {
    const { result } = renderHook(() => useVoiceCommand());

    act(() => {
      result.current.processTranscript("수정");
    });

    expect(result.current.command?.type).toBe("edit");
  });

  it("'중지' 명령을 인식한다", () => {
    const { result } = renderHook(() => useVoiceCommand());

    act(() => {
      result.current.processTranscript("중지");
    });

    expect(result.current.command?.type).toBe("stop");
  });

  it("'읽어줘' 명령을 인식한다", () => {
    const { result } = renderHook(() => useVoiceCommand());

    act(() => {
      result.current.processTranscript("읽어줘");
    });

    expect(result.current.command?.type).toBe("read");
  });

  it("'저장' 명령을 인식한다", () => {
    const { result } = renderHook(() => useVoiceCommand());

    act(() => {
      result.current.processTranscript("저장");
    });

    expect(result.current.command?.type).toBe("save");
  });

  it("'도움말' 명령을 인식한다", () => {
    const { result } = renderHook(() => useVoiceCommand());

    act(() => {
      result.current.processTranscript("도움말");
    });

    expect(result.current.command?.type).toBe("help");
  });

  it("clearCommand로 명령을 초기화할 수 있다", () => {
    const { result } = renderHook(() => useVoiceCommand());

    act(() => {
      result.current.processTranscript("다음");
    });

    expect(result.current.command).not.toBeNull();

    act(() => {
      result.current.clearCommand();
    });

    expect(result.current.command).toBeNull();
  });

  it("3초 후 명령이 자동으로 클리어된다", () => {
    const { result } = renderHook(() => useVoiceCommand());

    act(() => {
      result.current.processTranscript("다음");
    });

    expect(result.current.command).not.toBeNull();

    act(() => {
      vi.advanceTimersByTime(3000);
    });

    expect(result.current.command).toBeNull();
  });

  it("인식되지 않는 텍스트는 null을 반환한다", () => {
    const { result } = renderHook(() => useVoiceCommand());

    const cmd = result.current.processTranscript("안녕하세요 반갑습니다");

    expect(cmd).toBeNull();
  });
});
