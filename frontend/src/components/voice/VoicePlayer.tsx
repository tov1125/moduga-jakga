"use client";

import { useTTS } from "@/hooks/useTTS";
import { Button } from "@/components/ui/Button";

interface VoicePlayerProps {
  /** Text to be read aloud */
  text: string;
  /** Additional CSS class */
  className?: string;
}

/**
 * TTS playback component with play/pause, speed control,
 * and sentence navigation. All controls are keyboard accessible.
 */
export function VoicePlayer({ text, className = "" }: VoicePlayerProps) {
  const {
    speak,
    pause,
    resume,
    stop,
    isPlaying,
    isPaused,
    speed,
    setSpeed,
    currentSentence,
    totalSentences,
    skipForward,
    skipBackward,
    error,
  } = useTTS();

  const handlePlayPause = () => {
    if (isPlaying) {
      pause();
    } else if (isPaused) {
      resume();
    } else {
      speak(text);
    }
  };

  const speedOptions = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0];

  return (
    <div
      className={`flex flex-col gap-4 ${className}`}
      role="region"
      aria-label="음성 낭독 컨트롤"
    >
      {/* Main controls */}
      <div className="flex items-center gap-3 flex-wrap">
        {/* Skip backward */}
        <Button
          variant="secondary"
          size="md"
          onClick={skipBackward}
          disabled={!isPlaying && !isPaused}
          aria-label="이전 문장으로 이동"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5"
            viewBox="0 0 24 24"
            fill="currentColor"
            aria-hidden="true"
          >
            <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z" />
          </svg>
        </Button>

        {/* Play / Pause */}
        <Button
          variant="primary"
          size="lg"
          onClick={handlePlayPause}
          aria-label={
            isPlaying ? "일시정지" : isPaused ? "낭독 재개" : "낭독 시작"
          }
          aria-pressed={isPlaying}
        >
          {isPlaying ? (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              viewBox="0 0 24 24"
              fill="currentColor"
              aria-hidden="true"
            >
              <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
            </svg>
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              viewBox="0 0 24 24"
              fill="currentColor"
              aria-hidden="true"
            >
              <path d="M8 5v14l11-7z" />
            </svg>
          )}
          <span className="ml-1">
            {isPlaying ? "일시정지" : isPaused ? "재개" : "낭독"}
          </span>
        </Button>

        {/* Skip forward */}
        <Button
          variant="secondary"
          size="md"
          onClick={skipForward}
          disabled={!isPlaying && !isPaused}
          aria-label="다음 문장으로 이동"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5"
            viewBox="0 0 24 24"
            fill="currentColor"
            aria-hidden="true"
          >
            <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z" />
          </svg>
        </Button>

        {/* Stop */}
        {(isPlaying || isPaused) && (
          <Button
            variant="ghost"
            size="md"
            onClick={stop}
            aria-label="낭독 중지"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              viewBox="0 0 24 24"
              fill="currentColor"
              aria-hidden="true"
            >
              <rect x="6" y="6" width="12" height="12" />
            </svg>
            <span className="ml-1">중지</span>
          </Button>
        )}
      </div>

      {/* Speed control */}
      <div className="flex items-center gap-3" role="group" aria-label="낭독 속도 조절">
        <span className="text-base text-gray-700 dark:text-gray-300 font-medium">
          속도:
        </span>
        {speedOptions.map((s) => (
          <Button
            key={s}
            variant={speed === s ? "primary" : "secondary"}
            size="sm"
            onClick={() => setSpeed(s)}
            aria-label={`속도 ${s}배`}
            aria-pressed={speed === s}
          >
            {s}x
          </Button>
        ))}
      </div>

      {/* Progress indicator */}
      {totalSentences > 0 && (
        <p
          className="text-base text-gray-600 dark:text-gray-400"
          aria-live="polite"
        >
          {totalSentences}개 문장 중 {currentSentence + 1}번째 문장
          {isPlaying && " 낭독 중"}
          {isPaused && " 일시정지"}
        </p>
      )}

      {/* Error message */}
      {error && (
        <p
          className="text-red-600 dark:text-red-400 text-base font-medium"
          role="alert"
        >
          {error}
        </p>
      )}
    </div>
  );
}
