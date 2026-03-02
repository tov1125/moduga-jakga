/** Book genre options */
export type BookGenre = "essay" | "novel" | "poem" | "autobiography";

/** Book status in the writing pipeline */
export type BookStatus =
  | "draft"
  | "writing"
  | "editing"
  | "reviewing"
  | "designing"
  | "publishing"
  | "published";

/** Chapter editing status */
export type ChapterStatus = "draft" | "written" | "edited" | "reviewed" | "finalized";

/** Main book model */
export interface Book {
  id: string;
  userId: string;
  title: string;
  genre: BookGenre;
  status: BookStatus;
  description: string;
  coverImageUrl: string | null;
  chapters: Chapter[];
  createdAt: string;
  updatedAt: string;
}

/** Chapter within a book */
export interface Chapter {
  id: string;
  bookId: string;
  chapterNumber: number;
  title: string;
  content: string;
  rawTranscript: string;
  aiGenerated: boolean;
  status: ChapterStatus;
  wordCount: number;
  createdAt: string;
  updatedAt: string;
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
  chapterNumber: number;
}

/** Update chapter request */
export interface UpdateChapterData {
  title?: string;
  content?: string;
  rawTranscript?: string;
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

/** Edit history entry */
export interface EditHistory {
  id: string;
  chapterId: string;
  stage: "structure" | "content" | "proofread" | "copyedit";
  suggestions: EditSuggestion[];
  appliedAt: string | null;
  createdAt: string;
}

/** Quality report for a chapter or book */
export interface QualityReport {
  id: string;
  bookId: string;
  chapterId?: string;
  overallScore: number;
  grammarScore: number;
  styleScore: number;
  structureScore: number;
  readabilityScore: number;
  issues: QualityIssue[];
  verdict: "pass" | "needs_revision" | "major_revision";
  createdAt: string;
}

/** Individual quality issue */
export interface QualityIssue {
  type: "grammar" | "style" | "structure" | "readability";
  severity: "info" | "warning" | "error";
  message: string;
  location?: string;
}

/** Cover design template */
export interface CoverTemplate {
  id: string;
  name: string;
  description: string;
  previewUrl: string;
}

/** Export format options */
export type ExportFormat = "docx" | "pdf" | "epub";

/** Export status */
export interface ExportStatus {
  id: string;
  bookId: string;
  format: ExportFormat;
  status: "pending" | "processing" | "completed" | "failed";
  downloadUrl: string | null;
  error?: string;
  createdAt: string;
}
