"use client";

import { useCallback, useContext, useEffect, useRef, useState } from "react";
import { VoiceContext } from "@/providers/VoiceProvider";
import { useAnnouncer } from "./useAnnouncer";
import { tts as ttsApi } from "@/lib/api";
import { clamp } from "@/lib/utils";

interface UseTTSReturn {
  speak: (text: string) => Promise<void>;
  pause: () => void;
  resume: () => void;
  stop: () => void;
  isPlaying: boolean;
  isPaused: boolean;
  speed: number;
  setSpeed: (speed: number) => void;
  currentSentence: number;
  totalSentences: number;
  skipForward: () => void;
  skipBackward: () => void;
  error: string | null;
}

/**
 * Hook for Text-to-Speech playback.
 * Calls the backend TTS API and plays audio in the browser.
 */
export function useTTS(): UseTTSReturn {
  const voiceCtx = useContext(VoiceContext);
  const { announcePolite, announceAssertive } = useAnnouncer();

  const [error, setError] = useState<string | null>(null);
  const [sentences, setSentences] = useState<string[]>([]);
  const [currentSentence, setCurrentSentence] = useState(0);

  const audioContextRef = useRef<AudioContext | null>(null);
  const sourceRef = useRef<AudioBufferSourceNode | null>(null);
  const audioBuffersRef = useRef<AudioBuffer[]>([]);
  const isPlayingRef = useRef(false);

  const isPlaying = voiceCtx?.ttsState === "playing";
  const isPaused = voiceCtx?.ttsState === "paused";
  const speed = voiceCtx?.ttsSpeed ?? 1.0;

  const setSpeed = useCallback(
    (newSpeed: number) => {
      const clamped = clamp(newSpeed, 0.5, 2.0);
      voiceCtx?.setTtsSpeed(clamped);
    },
    [voiceCtx]
  );

  /** Split text into sentences for navigation */
  const splitSentences = useCallback((text: string): string[] => {
    return text
      .split(/(?<=[.!?。！？])\s+/)
      .filter((s) => s.trim().length > 0);
  }, []);

  /** Play a specific sentence */
  const playSentence = useCallback(
    async (sentenceIndex: number, sentenceList: string[]) => {
      if (sentenceIndex < 0 || sentenceIndex >= sentenceList.length) {
        voiceCtx?.setTtsState("idle");
        isPlayingRef.current = false;
        return;
      }

      setError(null);
      isPlayingRef.current = true;

      try {
        // Get audio from backend
        const audioData = await ttsApi.synthesize(
          sentenceList[sentenceIndex],
          undefined,
          speed
        );

        // Create AudioContext if needed
        if (!audioContextRef.current) {
          audioContextRef.current = new AudioContext();
        }
        const ctx = audioContextRef.current;

        // Decode audio
        const audioBuffer = await ctx.decodeAudioData(audioData);
        audioBuffersRef.current[sentenceIndex] = audioBuffer;

        // Play audio
        const source = ctx.createBufferSource();
        source.buffer = audioBuffer;
        source.playbackRate.value = speed;
        source.connect(ctx.destination);
        sourceRef.current = source;

        source.onended = () => {
          if (isPlayingRef.current) {
            const next = sentenceIndex + 1;
            setCurrentSentence(next);
            if (next < sentenceList.length) {
              playSentence(next, sentenceList);
            } else {
              voiceCtx?.setTtsState("idle");
              isPlayingRef.current = false;
              announcePolite("낭독이 끝났습니다");
            }
          }
        };

        source.start();
        voiceCtx?.setTtsState("playing");
      } catch (err) {
        console.error("TTS error:", err);
        setError("음성 합성 중 오류가 발생했습니다");
        voiceCtx?.setTtsState("error");
        announceAssertive("음성 합성 중 오류가 발생했습니다");
        isPlayingRef.current = false;
      }
    },
    [speed, voiceCtx, announcePolite, announceAssertive]
  );

  const speak = useCallback(
    async (text: string) => {
      // Stop any current playback
      if (sourceRef.current) {
        try {
          sourceRef.current.stop();
        } catch {
          // Already stopped
        }
      }

      const sentenceList = splitSentences(text);
      if (sentenceList.length === 0) return;

      setSentences(sentenceList);
      setCurrentSentence(0);
      audioBuffersRef.current = [];
      announcePolite("낭독을 시작합니다");

      await playSentence(0, sentenceList);
    },
    [splitSentences, playSentence, announcePolite]
  );

  const pause = useCallback(() => {
    if (audioContextRef.current && audioContextRef.current.state === "running") {
      audioContextRef.current.suspend();
      voiceCtx?.setTtsState("paused");
      isPlayingRef.current = false;
      announcePolite("일시정지합니다");
    }
  }, [voiceCtx, announcePolite]);

  const resume = useCallback(() => {
    if (audioContextRef.current && audioContextRef.current.state === "suspended") {
      audioContextRef.current.resume();
      voiceCtx?.setTtsState("playing");
      isPlayingRef.current = true;
      announcePolite("낭독을 재개합니다");
    }
  }, [voiceCtx, announcePolite]);

  const stop = useCallback(() => {
    if (sourceRef.current) {
      try {
        sourceRef.current.stop();
      } catch {
        // Already stopped
      }
    }
    isPlayingRef.current = false;
    voiceCtx?.setTtsState("idle");
    setCurrentSentence(0);
    announcePolite("낭독을 중지합니다");
  }, [voiceCtx, announcePolite]);

  const skipForward = useCallback(() => {
    if (currentSentence < sentences.length - 1) {
      if (sourceRef.current) {
        try {
          sourceRef.current.stop();
        } catch {
          // Already stopped
        }
      }
      const next = currentSentence + 1;
      setCurrentSentence(next);
      announcePolite(`다음 문장, ${sentences.length}개 중 ${next + 1}번째`);
      playSentence(next, sentences);
    }
  }, [currentSentence, sentences, playSentence, announcePolite]);

  const skipBackward = useCallback(() => {
    if (currentSentence > 0) {
      if (sourceRef.current) {
        try {
          sourceRef.current.stop();
        } catch {
          // Already stopped
        }
      }
      const prev = currentSentence - 1;
      setCurrentSentence(prev);
      announcePolite(`이전 문장, ${sentences.length}개 중 ${prev + 1}번째`);
      playSentence(prev, sentences);
    }
  }, [currentSentence, sentences, playSentence, announcePolite]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isPlayingRef.current = false;
      if (sourceRef.current) {
        try {
          sourceRef.current.stop();
        } catch {
          // Already stopped
        }
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  return {
    speak,
    pause,
    resume,
    stop,
    isPlaying,
    isPaused,
    speed,
    setSpeed,
    currentSentence,
    totalSentences: sentences.length,
    skipForward,
    skipBackward,
    error,
  };
}
