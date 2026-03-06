"use client";

import { useCallback, useContext, useEffect, useRef, useState } from "react";
import { VoiceContext } from "@/providers/VoiceProvider";
import { useAnnouncer } from "./useAnnouncer";
import type { STTResult } from "@/types/voice";

const WS_URL =
  process.env.NEXT_PUBLIC_WS_URL ||
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

      // C-02: 핸드셰이크 상태 추적 (auth → config → streaming)
      let handshakePhase: "auth" | "config" | "streaming" = "auth";

      ws.onopen = () => {
        // 1단계: 인증 토큰 전송 (BE 프로토콜: { token })
        const token =
          typeof window !== "undefined"
            ? localStorage.getItem("access_token")
            : null;
        if (token) {
          ws.send(JSON.stringify({ token }));
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          // 핸드셰이크: 인증 응답 처리
          if (handshakePhase === "auth") {
            if (data.error) {
              setError("음성 인식 인증에 실패했습니다");
              voiceCtx?.setSttState("error");
              announceAssertive("음성 인식 인증에 실패했습니다");
              ws.close();
              return;
            }
            // 인증 성공 → 설정 전송 (C-02: 언어 코드 ko-KR 통일)
            handshakePhase = "config";
            ws.send(JSON.stringify({ language: "ko-KR" }));
            return;
          }

          if (handshakePhase === "config") {
            // 설정 확인 응답 → 스트리밍 시작
            handshakePhase = "streaming";
            voiceCtx?.setSttState("recording");
            announceAssertive("녹음을 시작합니다");

            // H-05: PCM 16bit 우선, 미지원 시 webm/opus 폴백
            let mediaRecorder: MediaRecorder;
            const pcmMime = "audio/webm;codecs=pcm";
            if (MediaRecorder.isTypeSupported(pcmMime)) {
              mediaRecorder = new MediaRecorder(stream, { mimeType: pcmMime });
            } else {
              mediaRecorder = new MediaRecorder(stream, {
                mimeType: "audio/webm;codecs=opus",
              });
            }
            mediaRecorderRef.current = mediaRecorder;

            mediaRecorder.ondataavailable = (ev) => {
              if (ev.data.size > 0 && ws.readyState === WebSocket.OPEN) {
                ws.send(ev.data);
              }
            };

            mediaRecorder.start(250);
            return;
          }

          // 스트리밍 단계: STT 결과 처리
          if (data.error) {
            setError(data.error);
            return;
          }

          // C-01: is_final (snake_case — BE와 통일)
          const result = data as STTResult;
          if (result.is_final) {
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
