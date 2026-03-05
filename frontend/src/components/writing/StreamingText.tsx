"use client";

import { useEffect, useRef, useState } from "react";

interface StreamingTextProps {
  /** The text to display, growing as it streams in */
  text: string;
  /** Whether text is currently streaming */
  isStreaming: boolean;
  /** Additional CSS class */
  className?: string;
}

/**
 * Real-time AI text generation display.
 * Shows text as it streams in via SSE with a cursor animation.
 * Uses aria-live="polite" so screen readers announce new text.
 */
export function StreamingText({
  text,
  isStreaming,
  className = "",
}: StreamingTextProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [displayedText, setDisplayedText] = useState("");

  // Update displayed text
  useEffect(() => {
    setDisplayedText(text);
  }, [text]);

  // Auto-scroll to bottom as text streams in
  useEffect(() => {
    if (containerRef.current && isStreaming) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [displayedText, isStreaming]);

  if (!displayedText && !isStreaming) return null;

  return (
    <div
      ref={containerRef}
      className={`
        relative p-6
        bg-gray-50 dark:bg-gray-800
        border border-gray-200 dark:border-gray-700
        rounded-xl
        max-h-[300px] overflow-y-auto
        ${className}
      `}
      role="region"
      aria-label="AI 생성 텍스트"
    >
      {/* Streaming indicator */}
      {isStreaming && (
        <div
          className="flex items-center gap-2 mb-3"
          role="status"
          aria-live="polite"
        >
          <span className="flex gap-1">
            <span
              className="w-2 h-2 bg-primary-500 rounded-full animate-bounce"
              style={{ animationDelay: "0ms" }}
              aria-hidden="true"
            />
            <span
              className="w-2 h-2 bg-primary-500 rounded-full animate-bounce"
              style={{ animationDelay: "150ms" }}
              aria-hidden="true"
            />
            <span
              className="w-2 h-2 bg-primary-500 rounded-full animate-bounce"
              style={{ animationDelay: "300ms" }}
              aria-hidden="true"
            />
          </span>
          <span className="text-sm text-primary-700 dark:text-primary-400 font-medium">
            AI가 글을 생성하고 있습니다...
          </span>
        </div>
      )}

      {/* Text content */}
      <div aria-live="polite" aria-atomic="false">
        <p className="text-lg leading-relaxed text-gray-900 dark:text-gray-100 whitespace-pre-wrap">
          {displayedText}
          {isStreaming && (
            <span
              className="inline-block w-0.5 h-5 bg-primary-600 dark:bg-primary-400 animate-pulse ml-0.5 align-text-bottom"
              aria-hidden="true"
            />
          )}
        </p>
      </div>
    </div>
  );
}
