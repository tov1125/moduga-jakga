import { renderHook, act } from "@testing-library/react";
import { useEditHistory } from "@/hooks/useEditHistory";

describe("useEditHistory", () => {
  it("초기 상태에서 canUndo와 canRedo가 false", () => {
    const { result } = renderHook(() => useEditHistory());

    expect(result.current.canUndo).toBe(false);
    expect(result.current.canRedo).toBe(false);
  });

  it("push 후 canUndo가 true, canRedo가 false", () => {
    const { result } = renderHook(() => useEditHistory());

    act(() => {
      result.current.push("첫 번째 스냅샷");
    });

    expect(result.current.canUndo).toBe(true);
    expect(result.current.canRedo).toBe(false);
  });

  it("push → undo 시 스냅샷을 반환하고 canRedo가 true", () => {
    const { result } = renderHook(() => useEditHistory());

    act(() => {
      result.current.push("스냅샷 A");
    });

    let snapshot: string | null = null;
    act(() => {
      snapshot = result.current.undo();
    });

    expect(snapshot).toBe("스냅샷 A");
    expect(result.current.canUndo).toBe(false);
    expect(result.current.canRedo).toBe(true);
  });

  it("undo → redo 시 스냅샷을 복원", () => {
    const { result } = renderHook(() => useEditHistory());

    act(() => {
      result.current.push("스냅샷 1");
      result.current.push("스냅샷 2");
    });

    act(() => {
      result.current.undo();
    });

    let restored: string | null = null;
    act(() => {
      restored = result.current.redo();
    });

    expect(restored).toBe("스냅샷 2");
    expect(result.current.canUndo).toBe(true);
  });

  it("빈 상태에서 undo 시 null 반환", () => {
    const { result } = renderHook(() => useEditHistory());

    let snapshot: string | null = "not null";
    act(() => {
      snapshot = result.current.undo();
    });

    expect(snapshot).toBeNull();
  });

  it("빈 상태에서 redo 시 null 반환", () => {
    const { result } = renderHook(() => useEditHistory());

    let snapshot: string | null = "not null";
    act(() => {
      snapshot = result.current.redo();
    });

    expect(snapshot).toBeNull();
  });

  it("push 후 redo 스택이 초기화됨", () => {
    const { result } = renderHook(() => useEditHistory());

    act(() => {
      result.current.push("A");
      result.current.push("B");
    });

    // undo로 redo 스택에 항목 추가
    act(() => {
      result.current.undo();
    });
    expect(result.current.canRedo).toBe(true);

    // 새 push로 redo 스택 초기화
    act(() => {
      result.current.push("C");
    });
    expect(result.current.canRedo).toBe(false);

    let redoResult: string | null = null;
    act(() => {
      redoResult = result.current.redo();
    });
    expect(redoResult).toBeNull();
  });

  it("MAX_HISTORY(50) 초과 시 오래된 항목이 제거됨", () => {
    const { result } = renderHook(() => useEditHistory());

    // 51개 push — 가장 오래된 "item-0"은 제거되어야 함
    act(() => {
      for (let i = 0; i <= 50; i++) {
        result.current.push(`item-${i}`);
      }
    });

    // 50번 undo하면 50개까지만 꺼낼 수 있음
    const undone: (string | null)[] = [];
    act(() => {
      for (let i = 0; i < 51; i++) {
        undone.push(result.current.undo());
      }
    });

    // 50개는 유효한 값, 51번째는 null
    const validItems = undone.filter((v) => v !== null);
    expect(validItems).toHaveLength(50);

    // "item-0"은 제거되었으므로 포함되지 않아야 함
    expect(validItems).not.toContain("item-0");
    // "item-1"은 가장 오래된 유효 항목
    expect(validItems).toContain("item-1");
    // "item-50"은 가장 최근 항목
    expect(validItems).toContain("item-50");
  });

  it("여러 번 undo/redo 왕복 시 올바르게 동작", () => {
    const { result } = renderHook(() => useEditHistory());

    act(() => {
      result.current.push("A");
      result.current.push("B");
      result.current.push("C");
    });

    // undo 2번
    let s1: string | null = null;
    let s2: string | null = null;
    act(() => {
      s1 = result.current.undo(); // C
      s2 = result.current.undo(); // B
    });
    expect(s1).toBe("C");
    expect(s2).toBe("B");
    expect(result.current.canUndo).toBe(true);
    expect(result.current.canRedo).toBe(true);

    // redo 1번
    let r1: string | null = null;
    act(() => {
      r1 = result.current.redo(); // B
    });
    expect(r1).toBe("B");
    expect(result.current.canRedo).toBe(true); // C 아직 redo 스택에 있음
  });
});
