"use client";

interface AnnouncerProps {
  message: string;
  mode?: "polite" | "assertive";
}

/**
 * Visually hidden aria-live region for screen reader announcements.
 * Content changes are automatically announced by assistive technology.
 */
export function Announcer({ message, mode = "polite" }: AnnouncerProps) {
  return (
    <div
      role={mode === "assertive" ? "alert" : "status"}
      aria-live={mode}
      aria-atomic="true"
      className="sr-only"
    >
      {message}
    </div>
  );
}
