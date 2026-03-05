"use client";

import { useCallback, useRef, useState } from "react";

const MAX_HISTORY = 50;

interface UseEditHistoryReturn {
  push: (content: string) => void;
  undo: () => string | null;
  redo: () => string | null;
  canUndo: boolean;
  canRedo: boolean;
}

/**
 * Undo/Redo history stack for text editing.
 * Stores up to 50 snapshots. Each push clears the redo stack.
 */
export function useEditHistory(): UseEditHistoryReturn {
  const undoStack = useRef<string[]>([]);
  const redoStack = useRef<string[]>([]);
  const [canUndo, setCanUndo] = useState(false);
  const [canRedo, setCanRedo] = useState(false);

  const push = useCallback((content: string) => {
    undoStack.current.push(content);
    if (undoStack.current.length > MAX_HISTORY) {
      undoStack.current.shift();
    }
    redoStack.current = [];
    setCanUndo(true);
    setCanRedo(false);
  }, []);

  const undo = useCallback((): string | null => {
    const snapshot = undoStack.current.pop();
    if (snapshot === undefined) return null;
    redoStack.current.push(snapshot);
    setCanUndo(undoStack.current.length > 0);
    setCanRedo(true);
    return snapshot;
  }, []);

  const redo = useCallback((): string | null => {
    const snapshot = redoStack.current.pop();
    if (snapshot === undefined) return null;
    undoStack.current.push(snapshot);
    setCanUndo(true);
    setCanRedo(redoStack.current.length > 0);
    return snapshot;
  }, []);

  return { push, undo, redo, canUndo, canRedo };
}
