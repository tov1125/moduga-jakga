"use client";

import { useCallback, useContext, useEffect, useRef, useState } from "react";
import { VoiceContext } from "@/providers/VoiceProvider";
import { useAnnouncer } from "./useAnnouncer";
import type { STTResult } from "@/types/voice";

const WS_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/^http/, "ws") ||
  "ws://localhost:8000/api/v1";

interface UseSTTReturn {
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  isRecording: boolean;
  transcript: string;
  interimTranscript: string;
  error: string | null;
  clearTranscript: () => void;
}

/**
 * Hook for Speech-to-Text via WebSocket.
 * Connects to the backend STT streaming endpoint,
 * records audio from the microphone, and sends chunks.
 */
export function useSTT(): UseSTTReturn {
  const voiceCtx = useContext(VoiceContext);
  const { announceAssertive, announcePolite } = useAnnouncer();

  const [transcript, setTranscript] = useState("");
  const [interimTranscript, setInterimTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const isRecording = voiceCtx?.sttState === "recording";

  const clearTranscript = useCallback(() => {
    setTranscript("");
    setInterimTranscript("");
  }, []);

  const stopRecording = useCallback(() => {
    // Stop media recorder
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
    mediaRecorderRef.current = null;

    // Stop media stream tracks
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    // Close WebSocket
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    voiceCtx?.setSttState("idle");
    voiceCtx?.resumeTtsAfterStt();
    announcePolite("녹음을 중지합니다");
  }, [voiceCtx, announcePolite]);

  const startRecording = useCallback(async () => {
    setError(null);

    // Pause TTS if playing
    voiceCtx?.pauseTtsForStt();

    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000,
        },
      });
      streamRef.current = stream;

      // Open WebSocket connection
      const ws = new WebSocket(`${WS_URL}/stt/stream`);
      wsRef.current = ws;

      ws.onopen = () => {
        // Send auth token if available
        const token =
          typeof window !== "undefined"
            ? localStorage.getItem("access_token")
            : null;
        if (token) {
          ws.send(JSON.stringify({ type: "auth", token }));
        }

        // Send config (language)
        ws.send(JSON.stringify({ type: "config", language: "ko" }));

        voiceCtx?.setSttState("recording");
        announceAssertive("녹음을 시작합니다");

        // Start recording
        const mediaRecorder = new MediaRecorder(stream, {
          mimeType: "audio/webm;codecs=opus",
        });
        mediaRecorderRef.current = mediaRecorder;

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0 && ws.readyState === WebSocket.OPEN) {
            ws.send(event.data);
          }
        };

        mediaRecorder.start(250); // Send chunks every 250ms
      };

      ws.onmessage = (event) => {
        try {
          const result: STTResult = JSON.parse(event.data);
          if (result.isFinal) {
            setTranscript((prev) => {
              const updated = prev ? `${prev} ${result.text}` : result.text;
              voiceCtx?.setTranscript(updated);
              return updated;
            });
            setInterimTranscript("");
          } else {
            setInterimTranscript(result.text);
          }
        } catch {
          // Non-JSON message, treat as raw text
          setInterimTranscript(event.data);
        }
      };

      ws.onerror = () => {
        setError("음성 인식 연결에 실패했습니다");
        voiceCtx?.setSttState("error");
        announceAssertive("음성 인식 연결에 실패했습니다");
        stopRecording();
      };

      ws.onclose = () => {
        if (voiceCtx?.sttState === "recording") {
          voiceCtx?.setSttState("idle");
        }
      };
    } catch (err) {
      const message =
        err instanceof DOMException && err.name === "NotAllowedError"
          ? "마이크 사용 권한이 필요합니다. 브라우저 설정에서 마이크를 허용해주세요."
          : "마이크를 사용할 수 없습니다";
      setError(message);
      voiceCtx?.setSttState("error");
      announceAssertive(message);
    }
  }, [voiceCtx, announceAssertive, stopRecording]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
        mediaRecorderRef.current.stop();
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return {
    startRecording,
    stopRecording,
    isRecording,
    transcript,
    interimTranscript,
    error,
    clearTranscript,
  };
}
