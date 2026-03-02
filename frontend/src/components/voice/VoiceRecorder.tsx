"use client";

import { useCallback } from "react";
import { useSTT } from "@/hooks/useSTT";
import { Button } from "@/components/ui/Button";

interface VoiceRecorderProps {
  /** Called when final transcript is available */
  onTranscript?: (text: string) => void;
  /** Additional CSS class */
  className?: string;
}

/**
 * STT recording component with a large record button,
 * visual feedback for recording state, and real-time transcript display.
 */
export function VoiceRecorder({ onTranscript, className = "" }: VoiceRecorderProps) {
  const {
    startRecording,
    stopRecording,
    isRecording,
    transcript,
    interimTranscript,
    error,
    clearTranscript,
  } = useSTT();

  const handleToggleRecording = useCallback(async () => {
    if (isRecording) {
      stopRecording();
      if (transcript && onTranscript) {
        onTranscript(transcript);
      }
    } else {
      clearTranscript();
      await startRecording();
    }
  }, [isRecording, stopRecording, startRecording, transcript, onTranscript, clearTranscript]);

  return (
    <div className={`flex flex-col items-center gap-4 ${className}`}>
      {/* Record button */}
      <Button
        variant={isRecording ? "danger" : "primary"}
        size="lg"
        onClick={handleToggleRecording}
        aria-label={isRecording ? "녹음 중지" : "녹음 시작"}
        aria-pressed={isRecording}
        className={`
          w-24 h-24 rounded-full text-2xl
          ${isRecording ? "animate-pulse" : ""}
        `}
      >
        {isRecording ? (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-10 w-10"
            viewBox="0 0 24 24"
            fill="currentColor"
            aria-hidden="true"
          >
            <rect x="6" y="6" width="12" height="12" rx="2" />
          </svg>
        ) : (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-10 w-10"
            viewBox="0 0 24 24"
            fill="currentColor"
            aria-hidden="true"
          >
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
            <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
          </svg>
        )}
      </Button>

      {/* Recording state text */}
      <p
        className="text-lg font-medium text-gray-700 dark:text-gray-300"
        aria-live="polite"
      >
        {isRecording ? "녹음 중..." : "마이크 버튼을 눌러 녹음을 시작하세요"}
      </p>

      {/* Error message */}
      {error && (
        <p
          className="text-red-600 dark:text-red-400 text-base font-medium"
          role="alert"
        >
          {error}
        </p>
      )}

      {/* Transcript display */}
      {(transcript || interimTranscript) && (
        <div
          className="
            w-full max-w-2xl p-4 mt-2
            bg-gray-50 dark:bg-gray-800
            border border-gray-200 dark:border-gray-700
            rounded-lg
          "
          aria-label="음성 인식 결과"
          aria-live="polite"
        >
          <p className="text-base text-gray-900 dark:text-gray-100">
            {transcript}
            {interimTranscript && (
              <span className="text-gray-500 dark:text-gray-400 italic">
                {" "}
                {interimTranscript}
              </span>
            )}
          </p>
        </div>
      )}

      {/* Clear button */}
      {transcript && !isRecording && (
        <Button
          variant="ghost"
          size="sm"
          onClick={clearTranscript}
          aria-label="음성 인식 결과 지우기"
        >
          결과 지우기
        </Button>
      )}
    </div>
  );
}
