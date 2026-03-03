/** Book genre options (synced with BE Genre enum) */
export type BookGenre = "essay" | "novel" | "poem" | "autobiography" | "children" | "non_fiction" | "other";

/** Book status in the writing pipeline (synced with BE BookStatus enum) */
export type BookStatus =
  | "draft"
  | "writing"
  | "editing"
  | "designing"
  | "completed"
  | "published";

/** Chapter editing status (synced with BE ChapterStatus enum) */
export type ChapterStatus = "draft" | "writing" | "completed" | "editing" | "finalized";

/** Main book model (matches BE BookResponse — snake_case keys) */
export interface Book {
  id: string;
  user_id: string;
  title: string;
  genre: BookGenre;
  status: BookStatus;
  description: string;
  target_audience: string;
  chapter_count: number;
  word_count: number;
  created_at: string;
  updated_at: string;
}

/** Chapter within a book (matches BE ChapterResponse — snake_case keys) */
export interface Chapter {
  id: string;
  book_id: string;
  title: string;
  content: string;
  order: number;
  status: ChapterStatus;
  word_count: number;
  created_at: string;
  updated_at: string;
}

/** Create book request */
export interface CreateBookData {
  title: string;
  genre: BookGenre;
  description?: string;
}

/** Update book request */
export interface UpdateBookData {
  title?: string;
  genre?: BookGenre;
  description?: string;
  status?: BookStatus;
}

/** Create chapter request */
export interface CreateChapterData {
  title: string;
  order: number;
}

/** Update chapter request */
export interface UpdateChapterData {
  title?: string;
  content?: string;
  order?: number;
  status?: ChapterStatus;
}

/** Editing suggestion from AI */
export interface EditSuggestion {
  id: string;
  type: "grammar" | "style" | "structure" | "content";
  original: string;
  suggested: string;
  explanation: string;
  position: {
    start: number;
    end: number;
  };
  accepted: boolean | null;
}

/** Edit history entry (FE view model — 편집 기록) */
export interface EditHistory {
  id: string;
  chapter_id: string;
  stage: "structure" | "content" | "proofread" | "final";
  suggestions: EditSuggestion[];
  applied_at: string | null;
  created_at: string;
}

/** Stage result from BE QualityReport */
export interface StageResult {
  stage: "structure" | "content" | "proofread" | "final";
  score: number;
  issues_count: number;
  feedback: string;
}

/** Quality report (matches BE QualityReport — snake_case keys) */
export interface QualityReport {
  book_id: string;
  overall_score: number;
  stage_results: StageResult[];
  total_issues: number;
  summary: string;
  recommendations: string[];
  created_at: string;
}

/** Cover design template (matches BE CoverTemplate — snake_case keys) */
export interface CoverTemplate {
  id: string;
  name: string;
  genre: BookGenre;
  style: string;
  preview_url: string;
  description: string;
}

/** Export format options */
export type ExportFormat = "docx" | "pdf" | "epub";

/** Export status (matches BE ExportStatus — snake_case keys) */
export interface ExportStatus {
  export_id: string;
  book_id: string;
  format: ExportFormat;
  status: "pending" | "processing" | "completed" | "failed";
  progress: number;
  error_message: string | null;
  created_at: string;
}

/** Export response (matches BE ExportResponse — snake_case keys) */
export interface ExportResponse {
  export_id: string;
  book_id: string;
  format: ExportFormat;
  status: "pending" | "processing" | "completed" | "failed";
  download_url: string | null;
  file_size_bytes: string | null;
  created_at: string;
}
