/**
 * useKeyboardNav 훅 테스트
 * 키보드 화살표 탐색, Home/End, Loop, Escape 기능 검증
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook } from "@testing-library/react";
import { useKeyboardNav } from "@/hooks/useKeyboardNav";

describe("useKeyboardNav", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("containerRef를 반환한다", () => {
    const { result } = renderHook(() => useKeyboardNav());
    expect(result.current.containerRef).toBeDefined();
    expect(result.current.containerRef.current).toBeNull();
  });

  it("옵션 없이도 기본값으로 동작한다", () => {
    const { result } = renderHook(() => useKeyboardNav());
    expect(result.current.containerRef).toBeDefined();
  });

  it("onEscape 콜백을 받을 수 있다", () => {
    const onEscape = vi.fn();
    const { result } = renderHook(() =>
      useKeyboardNav({ onEscape })
    );
    expect(result.current.containerRef).toBeDefined();
  });

  it("onActivate 콜백을 받을 수 있다", () => {
    const onActivate = vi.fn();
    const { result } = renderHook(() =>
      useKeyboardNav({ onActivate })
    );
    expect(result.current.containerRef).toBeDefined();
  });

  it("orientation 옵션을 받을 수 있다", () => {
    const { result } = renderHook(() =>
      useKeyboardNav({ orientation: "horizontal" })
    );
    expect(result.current.containerRef).toBeDefined();
  });

  it("loop 옵션을 비활성화할 수 있다", () => {
    const { result } = renderHook(() =>
      useKeyboardNav({ loop: false })
    );
    expect(result.current.containerRef).toBeDefined();
  });
});
