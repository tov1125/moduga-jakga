import { describe, it, expect } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useAnnouncer } from "@/hooks/useAnnouncer";
import { AnnouncerProvider } from "@/providers/AnnouncerProvider";
import type { ReactNode } from "react";

const wrapper = ({ children }: { children: ReactNode }) => (
  <AnnouncerProvider>{children}</AnnouncerProvider>
);

describe("useAnnouncer", () => {
  it("Provider 내에서 context를 반환한다", () => {
    const { result } = renderHook(() => useAnnouncer(), { wrapper });
    expect(result.current.announce).toBeDefined();
    expect(result.current.announcePolite).toBeDefined();
    expect(result.current.announceAssertive).toBeDefined();
  });

  it("Provider 없이 사용 시 에러를 throw한다", () => {
    expect(() => {
      renderHook(() => useAnnouncer());
    }).toThrow("useAnnouncer must be used within an AnnouncerProvider");
  });

  it("announcePolite가 호출 가능하다", () => {
    const { result } = renderHook(() => useAnnouncer(), { wrapper });
    expect(() => {
      act(() => {
        result.current.announcePolite("테스트 메시지");
      });
    }).not.toThrow();
  });

  it("announceAssertive가 호출 가능하다", () => {
    const { result } = renderHook(() => useAnnouncer(), { wrapper });
    expect(() => {
      act(() => {
        result.current.announceAssertive("긴급 메시지");
      });
    }).not.toThrow();
  });

  it("announce가 기본 polite 우선순위로 호출된다", () => {
    const { result } = renderHook(() => useAnnouncer(), { wrapper });
    expect(() => {
      act(() => {
        result.current.announce("일반 메시지");
      });
    }).not.toThrow();
  });
});
