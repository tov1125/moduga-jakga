"use client";

import React, {
  createContext,
  useCallback,
  useRef,
  useState,
  type ReactNode,
} from "react";

type AnnouncementPriority = "polite" | "assertive";

interface AnnouncerContextValue {
  announce: (message: string, priority?: AnnouncementPriority) => void;
  announcePolite: (message: string) => void;
  announceAssertive: (message: string) => void;
}

export const AnnouncerContext = createContext<AnnouncerContextValue | null>(null);

interface AnnouncerProviderProps {
  children: ReactNode;
}

/**
 * Provides a global announcement mechanism for screen readers.
 * Uses an aria-live region to broadcast messages.
 */
export function AnnouncerProvider({ children }: AnnouncerProviderProps) {
  const [politeMessage, setPoliteMessage] = useState("");
  const [assertiveMessage, setAssertiveMessage] = useState("");
  const politeTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const assertiveTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const announce = useCallback(
    (message: string, priority: AnnouncementPriority = "polite") => {
      if (priority === "assertive") {
        // Clear and re-set to force re-announcement
        setAssertiveMessage("");
        if (assertiveTimeoutRef.current) {
          clearTimeout(assertiveTimeoutRef.current);
        }
        assertiveTimeoutRef.current = setTimeout(() => {
          setAssertiveMessage(message);
        }, 100);
      } else {
        setPoliteMessage("");
        if (politeTimeoutRef.current) {
          clearTimeout(politeTimeoutRef.current);
        }
        politeTimeoutRef.current = setTimeout(() => {
          setPoliteMessage(message);
        }, 100);
      }
    },
    []
  );

  const announcePolite = useCallback(
    (message: string) => announce(message, "polite"),
    [announce]
  );

  const announceAssertive = useCallback(
    (message: string) => announce(message, "assertive"),
    [announce]
  );

  return (
    <AnnouncerContext.Provider value={{ announce, announcePolite, announceAssertive }}>
      {children}
      {/* Visually hidden aria-live regions */}
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      >
        {politeMessage}
      </div>
      <div
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
        className="sr-only"
      >
        {assertiveMessage}
      </div>
    </AnnouncerContext.Provider>
  );
}
