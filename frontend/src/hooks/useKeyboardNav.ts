"use client";

import { useCallback, useEffect, useRef } from "react";

interface KeyboardNavOptions {
  /** List of focusable element selectors within the container */
  selector?: string;
  /** Enable arrow key navigation */
  arrowKeys?: boolean;
  /** Enable Home/End navigation */
  homeEnd?: boolean;
  /** Navigate in a loop (wrap around) */
  loop?: boolean;
  /** Orientation: vertical = up/down, horizontal = left/right, both = all arrows */
  orientation?: "vertical" | "horizontal" | "both";
  /** Callback when Escape is pressed */
  onEscape?: () => void;
  /** Callback when Enter or Space is pressed on a focused item */
  onActivate?: (element: HTMLElement, index: number) => void;
}

/**
 * Hook to handle keyboard navigation within a container.
 * Supports arrow key navigation, Home/End, Enter/Space activation.
 */
export function useKeyboardNav(options: KeyboardNavOptions = {}) {
  const {
    selector = '[tabindex], a, button, input, select, textarea, [role="option"], [role="tab"]',
    arrowKeys = true,
    homeEnd = true,
    loop = true,
    orientation = "vertical",
    onEscape,
    onActivate,
  } = options;

  const containerRef = useRef<HTMLElement | null>(null);

  const getFocusableElements = useCallback((): HTMLElement[] => {
    if (!containerRef.current) return [];
    const elements = containerRef.current.querySelectorAll<HTMLElement>(selector);
    return Array.from(elements).filter(
      (el) => !el.hasAttribute("disabled") && el.getAttribute("aria-disabled") !== "true"
    );
  }, [selector]);

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      const elements = getFocusableElements();
      if (elements.length === 0) return;

      const currentIndex = elements.findIndex((el) => el === document.activeElement);

      let nextIndex: number | null = null;

      if (arrowKeys) {
        const isVertical = orientation === "vertical" || orientation === "both";
        const isHorizontal = orientation === "horizontal" || orientation === "both";

        if (
          (event.key === "ArrowDown" && isVertical) ||
          (event.key === "ArrowRight" && isHorizontal)
        ) {
          event.preventDefault();
          if (currentIndex === -1) {
            nextIndex = 0;
          } else if (currentIndex < elements.length - 1) {
            nextIndex = currentIndex + 1;
          } else if (loop) {
            nextIndex = 0;
          }
        }

        if (
          (event.key === "ArrowUp" && isVertical) ||
          (event.key === "ArrowLeft" && isHorizontal)
        ) {
          event.preventDefault();
          if (currentIndex === -1) {
            nextIndex = elements.length - 1;
          } else if (currentIndex > 0) {
            nextIndex = currentIndex - 1;
          } else if (loop) {
            nextIndex = elements.length - 1;
          }
        }
      }

      if (homeEnd) {
        if (event.key === "Home") {
          event.preventDefault();
          nextIndex = 0;
        }
        if (event.key === "End") {
          event.preventDefault();
          nextIndex = elements.length - 1;
        }
      }

      if (nextIndex !== null && nextIndex >= 0 && nextIndex < elements.length) {
        elements[nextIndex].focus();
      }

      // Enter/Space activation
      if (
        (event.key === "Enter" || event.key === " ") &&
        currentIndex >= 0 &&
        onActivate
      ) {
        event.preventDefault();
        onActivate(elements[currentIndex], currentIndex);
      }

      // Escape
      if (event.key === "Escape" && onEscape) {
        event.preventDefault();
        onEscape();
      }
    },
    [getFocusableElements, arrowKeys, homeEnd, loop, orientation, onEscape, onActivate]
  );

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    container.addEventListener("keydown", handleKeyDown);
    return () => {
      container.removeEventListener("keydown", handleKeyDown);
    };
  }, [handleKeyDown]);

  return { containerRef };
}
