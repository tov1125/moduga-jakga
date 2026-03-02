"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { VoiceCommand, VoiceCommandType } from "@/types/voice";

/** Map of Korean voice commands to command types */
const COMMAND_MAP: Record<string, VoiceCommandType> = {
  다음: "next",
  "다음으로": "next",
  이전: "previous",
  "이전으로": "previous",
  수정: "edit",
  "수정해줘": "edit",
  멈춰: "stop",
  "중지": "stop",
  "그만": "stop",
  읽어줘: "read",
  "읽어": "read",
  "낭독": "read",
  저장: "save",
  "저장해줘": "save",
  삭제: "delete",
  "삭제해줘": "delete",
  확인: "confirm",
  "네": "confirm",
  "예": "confirm",
  취소: "cancel",
  "아니요": "cancel",
  "아니": "cancel",
  도움말: "help",
  "도움": "help",
};

interface UseVoiceCommandReturn {
  command: VoiceCommand | null;
  processTranscript: (text: string) => VoiceCommand | null;
  clearCommand: () => void;
}

/**
 * Hook to process voice commands from STT transcript.
 * Listens for specific Korean command words and maps them to actions.
 */
export function useVoiceCommand(): UseVoiceCommandReturn {
  const [command, setCommand] = useState<VoiceCommand | null>(null);
  const lastProcessedRef = useRef<string>("");

  const processTranscript = useCallback((text: string): VoiceCommand | null => {
    if (!text || text === lastProcessedRef.current) return null;

    const trimmed = text.trim();
    lastProcessedRef.current = trimmed;

    // Check the last segment of the transcript for commands
    const words = trimmed.split(/\s+/);
    const lastWords = words.slice(-3); // Check last 3 words

    for (const word of lastWords) {
      const cleanWord = word.replace(/[.,!?。！？]/g, "");
      const commandType = COMMAND_MAP[cleanWord];

      if (commandType) {
        const voiceCommand: VoiceCommand = {
          type: commandType,
          rawText: trimmed,
          confidence: 1.0,
          params: words.slice(0, -1).join(" "), // Everything before the command
        };
        setCommand(voiceCommand);
        return voiceCommand;
      }
    }

    return null;
  }, []);

  const clearCommand = useCallback(() => {
    setCommand(null);
  }, []);

  // Auto-clear command after 3 seconds
  useEffect(() => {
    if (command) {
      const timer = setTimeout(() => {
        setCommand(null);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [command]);

  return {
    command,
    processTranscript,
    clearCommand,
  };
}
