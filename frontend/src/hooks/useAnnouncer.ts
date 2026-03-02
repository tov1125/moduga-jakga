"use client";

import { useContext } from "react";
import { AnnouncerContext } from "@/providers/AnnouncerProvider";

/**
 * Hook to access the screen reader announcer.
 *
 * @example
 * const { announce, announcePolite, announceAssertive } = useAnnouncer();
 * announce("녹음을 시작합니다");
 * announceAssertive("오류가 발생했습니다");
 */
export function useAnnouncer() {
  const context = useContext(AnnouncerContext);
  if (!context) {
    throw new Error("useAnnouncer must be used within an AnnouncerProvider");
  }
  return context;
}
