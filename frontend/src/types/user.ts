/** Types of visual disability */
export type DisabilityType =
  | "total_blindness"
  | "low_vision"
  | "color_blindness"
  | "other"
  | "none";

/** User profile */
export interface User {
  id: string;
  email: string;
  displayName: string;
  disabilityType: DisabilityType;
  voiceSpeed: number;
  voiceType: string;
  createdAt: string;
  updatedAt: string;
}

/** Data required for sign up */
export interface SignUpData {
  email: string;
  password: string;
  displayName: string;
  disabilityType: DisabilityType;
}

/** Data required for login */
export interface LoginData {
  email: string;
  password: string;
}

/** User settings update */
export interface UserSettingsUpdate {
  displayName?: string;
  disabilityType?: DisabilityType;
  voiceSpeed?: number;
  voiceType?: string;
}
