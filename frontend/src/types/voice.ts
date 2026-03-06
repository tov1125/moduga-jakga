/** State of the Speech-to-Text engine */
export type STTState = "idle" | "recording" | "processing" | "error";

/** State of the Text-to-Speech engine */
export type TTSState = "idle" | "playing" | "paused" | "error";

/** Voice commands recognized by the app */
export type VoiceCommandType =
  | "next"        // 다음
  | "previous"    // 이전
  | "edit"        // 수정
  | "stop"        // 멈춰
  | "read"        // 읽어줘
  | "save"        // 저장
  | "delete"      // 삭제
  | "confirm"     // 확인
  | "cancel"      // 취소
  | "help"        // 도움말
  | "unknown";

/** Parsed voice command */
export interface VoiceCommand {
  type: VoiceCommandType;
  rawText: string;
  params?: string;
  confidence: number;
}

/** STT transcription result (matches BE snake_case: is_final) */
export interface STTResult {
  text: string;
  is_final: boolean;
  segments?: Array<{ start: number; end: number; text: string }>;
}

/** TTS configuration */
export interface TTSConfig {
  voiceId: string;
  speed: number;
  pitch: number;
  volume: number;
  language: string;
}

/** Available TTS voice */
export interface TTSVoice {
  id: string;
  name: string;
  language: string;
  gender: "male" | "female" | "neutral";
  previewUrl?: string;
}
