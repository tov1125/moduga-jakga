"use client";

import { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";
import { useAnnouncer } from "@/hooks/useAnnouncer";
import { useSupabase } from "@/hooks/useSupabase";
import { auth as authApi, tts as ttsApi } from "@/lib/api";
import type { DisabilityType } from "@/types/user";
import type { TTSVoice } from "@/types/voice";

const DISABILITY_OPTIONS: { value: DisabilityType; label: string }[] = [
  { value: "total_blindness", label: "전맹" },
  { value: "low_vision", label: "저시력" },
  { value: "color_blindness", label: "색각 이상" },
  { value: "other", label: "기타 시각 장애" },
  { value: "none", label: "해당 없음" },
];

/**
 * Settings page for TTS, accessibility, and profile preferences.
 */
export default function SettingsPage() {
  const { user, refreshUser, isLoading: authLoading } = useSupabase();
  const { announcePolite, announceAssertive } = useAnnouncer();

  const [displayName, setDisplayName] = useState("");
  const [disabilityType, setDisabilityType] = useState<DisabilityType>("none");
  const [voiceSpeed, setVoiceSpeed] = useState(1.0);
  const [voiceType, setVoiceType] = useState("default");
  const [availableVoices, setAvailableVoices] = useState<TTSVoice[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoadingVoices, setIsLoadingVoices] = useState(false);
  const [message, setMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  // Initialize form from user data
  useEffect(() => {
    if (user) {
      setDisplayName(user.displayName);
      setDisabilityType(user.disabilityType);
      setVoiceSpeed(user.voiceSpeed);
      setVoiceType(user.voiceType);
    }
  }, [user]);

  // Load available voices
  useEffect(() => {
    async function loadVoices() {
      setIsLoadingVoices(true);
      try {
        const response = await ttsApi.voices();
        setAvailableVoices(response.data);
      } catch {
        // Silently fail - use default voice
      } finally {
        setIsLoadingVoices(false);
      }
    }
    loadVoices();
  }, []);

  const handleSave = useCallback(async () => {
    setIsSaving(true);
    setMessage(null);

    try {
      await authApi.updateSettings({
        displayName,
        disabilityType,
        voiceSpeed,
        voiceType,
      });
      await refreshUser();
      setMessage({ type: "success", text: "설정이 저장되었습니다." });
      announcePolite("설정이 저장되었습니다");
    } catch {
      setMessage({
        type: "error",
        text: "설정 저장에 실패했습니다. 다시 시도해 주세요.",
      });
      announceAssertive("설정 저장에 실패했습니다");
    } finally {
      setIsSaving(false);
    }
  }, [
    displayName,
    disabilityType,
    voiceSpeed,
    voiceType,
    refreshUser,
    announcePolite,
    announceAssertive,
  ]);

  if (authLoading) {
    return (
      <div className="flex items-center justify-center py-20" role="status" aria-live="polite">
        <p className="text-xl text-gray-500 dark:text-gray-400">불러오는 중...</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex flex-col items-center gap-4 py-20">
        <p className="text-xl text-gray-600 dark:text-gray-400">
          설정을 변경하려면 로그인해 주세요.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
        설정
      </h1>

      {/* Status message */}
      {message && (
        <div
          className={`
            p-4 rounded-xl
            ${
              message.type === "success"
                ? "bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800"
                : "bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800"
            }
          `}
          role="alert"
          aria-live="polite"
        >
          <p
            className={
              message.type === "success"
                ? "text-green-700 dark:text-green-300"
                : "text-red-700 dark:text-red-300"
            }
          >
            {message.text}
          </p>
        </div>
      )}

      {/* Profile settings */}
      <section
        className="bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-200 dark:border-gray-700"
        aria-label="프로필 설정"
      >
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">
          프로필
        </h2>

        <div className="flex flex-col gap-6">
          {/* Display name */}
          <div className="flex flex-col gap-2">
            <label
              htmlFor="settings-name"
              className="text-base font-medium text-gray-900 dark:text-gray-100"
            >
              이름 (필명)
            </label>
            <input
              id="settings-name"
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              className="
                w-full px-4 py-3 min-h-touch
                text-lg text-gray-900 dark:text-gray-100
                bg-white dark:bg-gray-800
                border-2 border-gray-300 dark:border-gray-600
                rounded-xl
                focus:border-primary-500 dark:focus:border-primary-400
                focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-yellow-400
              "
            />
          </div>

          {/* Disability type */}
          <div className="flex flex-col gap-2">
            <label
              htmlFor="settings-disability"
              className="text-base font-medium text-gray-900 dark:text-gray-100"
            >
              시각 장애 유형
            </label>
            <select
              id="settings-disability"
              value={disabilityType}
              onChange={(e) =>
                setDisabilityType(e.target.value as DisabilityType)
              }
              className="
                w-full px-4 py-3 min-h-touch
                text-lg text-gray-900 dark:text-gray-100
                bg-white dark:bg-gray-800
                border-2 border-gray-300 dark:border-gray-600
                rounded-xl
                focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-yellow-400
              "
            >
              {DISABILITY_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </section>

      {/* TTS settings */}
      <section
        className="bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-200 dark:border-gray-700"
        aria-label="음성 설정"
      >
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">
          음성 설정 (TTS)
        </h2>

        <div className="flex flex-col gap-6">
          {/* Voice selection */}
          <div className="flex flex-col gap-2">
            <label
              htmlFor="settings-voice"
              className="text-base font-medium text-gray-900 dark:text-gray-100"
            >
              음성 선택
            </label>
            <select
              id="settings-voice"
              value={voiceType}
              onChange={(e) => setVoiceType(e.target.value)}
              disabled={isLoadingVoices}
              className="
                w-full px-4 py-3 min-h-touch
                text-lg text-gray-900 dark:text-gray-100
                bg-white dark:bg-gray-800
                border-2 border-gray-300 dark:border-gray-600
                rounded-xl
                focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-yellow-400
                disabled:opacity-50
              "
            >
              <option value="default">기본 음성</option>
              {availableVoices.map((voice) => (
                <option key={voice.id} value={voice.id}>
                  {voice.name} ({voice.gender === "male" ? "남성" : voice.gender === "female" ? "여성" : "중성"})
                </option>
              ))}
            </select>
          </div>

          {/* Speed slider */}
          <div className="flex flex-col gap-2">
            <label
              htmlFor="settings-speed"
              className="text-base font-medium text-gray-900 dark:text-gray-100"
            >
              낭독 속도: {voiceSpeed.toFixed(1)}배
            </label>
            <input
              id="settings-speed"
              type="range"
              min={0.5}
              max={2.0}
              step={0.1}
              value={voiceSpeed}
              onChange={(e) => setVoiceSpeed(Number(e.target.value))}
              aria-valuenow={voiceSpeed}
              aria-valuemin={0.5}
              aria-valuemax={2.0}
              aria-label={`낭독 속도: ${voiceSpeed.toFixed(1)}배`}
              className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-sm text-gray-500 dark:text-gray-400">
              <span>0.5x (느리게)</span>
              <span>1.0x (보통)</span>
              <span>2.0x (빠르게)</span>
            </div>
          </div>
        </div>
      </section>

      {/* Save button */}
      <div className="flex justify-end">
        <Button
          variant="primary"
          size="lg"
          onClick={handleSave}
          isLoading={isSaving}
          aria-label="설정 저장"
        >
          설정 저장
        </Button>
      </div>
    </div>
  );
}
