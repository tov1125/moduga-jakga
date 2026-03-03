/** Types of visual disability (synced with BE DisabilityType enum) */
export type DisabilityType =
  | "visual"
  | "low_vision"
  | "none"
  | "other";

/** User profile (matches BE UserResponse — snake_case keys) */
export interface User {
  id: string;
  email: string;
  display_name: string;
  disability_type: DisabilityType;
  voice_speed: number;
  voice_type: string;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

/** Data required for sign up (matches BE SignUpRequest — snake_case keys) */
export interface SignUpData {
  email: string;
  password: string;
  display_name: string;
  disability_type: DisabilityType;
}

/** Data required for login */
export interface LoginData {
  email: string;
  password: string;
}

/** User settings update (matches BE UserSettingsUpdate — snake_case keys) */
export interface UserSettingsUpdate {
  display_name?: string;
  disability_type?: DisabilityType;
  voice_speed?: number;
  voice_type?: string;
}
