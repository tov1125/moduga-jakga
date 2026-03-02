"use client";

import { useEffect } from "react";
import { useVoiceCommand } from "@/hooks/useVoiceCommand";
import { useAnnouncer } from "@/hooks/useAnnouncer";
import type { VoiceCommandType } from "@/types/voice";

/** Korean labels for voice commands */
const COMMAND_LABELS: Record<VoiceCommandType, string> = {
  next: "다음",
  previous: "이전",
  edit: "수정",
  stop: "멈춤",
  read: "읽기",
  save: "저장",
  delete: "삭제",
  confirm: "확인",
  cancel: "취소",
  help: "도움말",
  unknown: "알 수 없음",
};

interface VoiceCommandProps {
  /** Current STT transcript to process */
  transcript: string;
  /** Callback when a command is detected */
  onCommand?: (command: VoiceCommandType, params?: string) => void;
  /** Additional CSS class */
  className?: string;
}

/**
 * Voice command indicator component.
 * Shows detected voice commands and confirms actions via announcements.
 */
export function VoiceCommandIndicator({
  transcript,
  onCommand,
  className = "",
}: VoiceCommandProps) {
  const { command, processTranscript, clearCommand } = useVoiceCommand();
  const { announceAssertive } = useAnnouncer();

  // Process transcript whenever it changes
  useEffect(() => {
    if (transcript) {
      const detected = processTranscript(transcript);
      if (detected && detected.type !== "unknown") {
        announceAssertive(`음성 명령 감지: ${COMMAND_LABELS[detected.type]}`);
        onCommand?.(detected.type, detected.params);
      }
    }
  }, [transcript, processTranscript, announceAssertive, onCommand]);

  if (!command || command.type === "unknown") return null;

  return (
    <div
      className={`
        inline-flex items-center gap-2
        px-4 py-2 rounded-full
        bg-primary-100 dark:bg-primary-900
        text-primary-800 dark:text-primary-200
        text-base font-medium
        animate-pulse
        ${className}
      `}
      role="status"
      aria-live="assertive"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-5 w-5"
        viewBox="0 0 24 24"
        fill="currentColor"
        aria-hidden="true"
      >
        <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
        <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
      </svg>
      <span>명령: {COMMAND_LABELS[command.type]}</span>
      <button
        onClick={clearCommand}
        aria-label="명령 표시 닫기"
        className="
          ml-1 p-1 rounded-full
          hover:bg-primary-200 dark:hover:bg-primary-800
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-yellow-400
          min-h-touch min-w-touch flex items-center justify-center
        "
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-4 w-4"
          viewBox="0 0 24 24"
          fill="currentColor"
          aria-hidden="true"
        >
          <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
        </svg>
      </button>
    </div>
  );
}
