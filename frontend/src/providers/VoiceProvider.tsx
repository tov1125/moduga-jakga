"use client";

import React, {
  createContext,
  useCallback,
  useState,
  type ReactNode,
} from "react";
import type { STTState, TTSState } from "@/types/voice";

interface VoiceContextValue {
  // STT state
  sttState: STTState;
  setSttState: (state: STTState) => void;
  isRecording: boolean;
  transcript: string;
  setTranscript: (text: string) => void;

  // TTS state
  ttsState: TTSState;
  setTtsState: (state: TTSState) => void;
  isPlaying: boolean;
  isPaused: boolean;
  ttsSpeed: number;
  setTtsSpeed: (speed: number) => void;

  // Conflict prevention
  pauseTtsForStt: () => void;
  resumeTtsAfterStt: () => void;
}

export const VoiceContext = createContext<VoiceContextValue | null>(null);

interface VoiceProviderProps {
  children: ReactNode;
}

/**
 * Provides global voice state (STT + TTS) and handles conflicts
 * (e.g., pausing TTS when STT recording starts).
 */
export function VoiceProvider({ children }: VoiceProviderProps) {
  const [sttState, setSttState] = useState<STTState>("idle");
  const [ttsState, setTtsState] = useState<TTSState>("idle");
  const [transcript, setTranscript] = useState("");
  const [ttsSpeed, setTtsSpeed] = useState(1.0);
  const [wasTtsPlaying, setWasTtsPlaying] = useState(false);

  const isRecording = sttState === "recording";
  const isPlaying = ttsState === "playing";
  const isPaused = ttsState === "paused";

  const pauseTtsForStt = useCallback(() => {
    if (ttsState === "playing") {
      setWasTtsPlaying(true);
      setTtsState("paused");
    }
  }, [ttsState]);

  const resumeTtsAfterStt = useCallback(() => {
    if (wasTtsPlaying) {
      setTtsState("playing");
      setWasTtsPlaying(false);
    }
  }, [wasTtsPlaying]);

  return (
    <VoiceContext.Provider
      value={{
        sttState,
        setSttState,
        isRecording,
        transcript,
        setTranscript,
        ttsState,
        setTtsState,
        isPlaying,
        isPaused,
        ttsSpeed,
        setTtsSpeed,
        pauseTtsForStt,
        resumeTtsAfterStt,
      }}
    >
      {children}
    </VoiceContext.Provider>
  );
}
