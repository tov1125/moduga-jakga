import type {
  ApiResponse,
  PaginatedResponse,
  RequestOptions,
  Book,
  CreateBookData,
  UpdateBookData,
  Chapter,
  CreateChapterData,
  UpdateChapterData,
  QualityReport,
  CoverTemplate,
  ExportFormat,
  ExportStatus,
  ExportResponse,
  TTSVoice,
  User,
  SignUpData,
  LoginData,
  UserSettingsUpdate,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

/**
 * Base fetch wrapper that injects auth headers and handles errors.
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit & RequestOptions = {}
): Promise<T> {
  const { headers: customHeaders, signal, ...rest } = options;

  // Retrieve token from localStorage (set during login)
  let token: string | null = null;
  if (typeof window !== "undefined") {
    token = localStorage.getItem("access_token");
  }

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(customHeaders as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...rest,
    headers,
    signal,
  });

  if (!response.ok) {
    // H-01: 401 → 세션 만료 처리 (로그인 페이지로 리다이렉트)
    if (response.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      // 로그인 페이지가 아닌 경우에만 리다이렉트
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login?expired=1";
      }
    }

    const errorBody = await response.json().catch(() => ({
      error: { code: "UNKNOWN", message: response.statusText },
    }));
    const message =
      response.status === 401
        ? "세션이 만료되었습니다. 다시 로그인해 주세요."
        : errorBody.detail ||
          errorBody.error?.message ||
          errorBody.message ||
          response.statusText ||
          "요청 처리에 실패했습니다.";
    throw new ApiError(
      message,
      response.status,
      errorBody.error?.code || "UNKNOWN"
    );
  }

  const json = await response.json();

  // BE returns raw Pydantic objects; wrap to match FE ApiResponse format
  if (typeof json === "object" && json !== null && !("success" in json)) {
    return { success: true, data: json } as unknown as T;
  }
  return json as T;
}

/** Custom error class for API errors */
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// ─── Auth ────────────────────────────────────────────────────────────────────

export const auth = {
  async signup(data: SignUpData): Promise<ApiResponse<User>> {
    return apiFetch("/auth/signup", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async login(data: LoginData): Promise<ApiResponse<{ user: User; access_token: string; token_type: string; expires_in: string }>> {
    return apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async logout(): Promise<ApiResponse<null>> {
    return apiFetch("/auth/logout", { method: "POST" });
  },

  async me(): Promise<ApiResponse<User>> {
    return apiFetch("/auth/me");
  },

  async updateSettings(data: UserSettingsUpdate): Promise<ApiResponse<User>> {
    return apiFetch("/auth/settings", {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },
};

// ─── Books ───────────────────────────────────────────────────────────────────

export const books = {
  async list(page = 1, pageSize = 10): Promise<PaginatedResponse<Book>> {
    return apiFetch(`/books?page=${page}&page_size=${pageSize}`);
  },

  async create(data: CreateBookData): Promise<ApiResponse<Book>> {
    return apiFetch("/books", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async get(bookId: string): Promise<ApiResponse<Book>> {
    return apiFetch(`/books/${bookId}`);
  },

  async update(bookId: string, data: UpdateBookData): Promise<ApiResponse<Book>> {
    return apiFetch(`/books/${bookId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },

  async delete(bookId: string): Promise<ApiResponse<null>> {
    return apiFetch(`/books/${bookId}`, { method: "DELETE" });
  },
};

// ─── Chapters ────────────────────────────────────────────────────────────────

export const chapters = {
  async list(bookId: string): Promise<ApiResponse<{ chapters: Chapter[]; total: number }>> {
    return apiFetch(`/books/${bookId}/chapters`);
  },

  async create(bookId: string, data: CreateChapterData): Promise<ApiResponse<Chapter>> {
    return apiFetch(`/books/${bookId}/chapters`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async get(bookId: string, chapterId: string): Promise<ApiResponse<Chapter>> {
    return apiFetch(`/books/${bookId}/chapters/${chapterId}`);
  },

  async update(
    bookId: string,
    chapterId: string,
    data: UpdateChapterData
  ): Promise<ApiResponse<Chapter>> {
    return apiFetch(`/books/${bookId}/chapters/${chapterId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },

  async delete(bookId: string, chapterId: string): Promise<ApiResponse<null>> {
    return apiFetch(`/books/${bookId}/chapters/${chapterId}`, { method: "DELETE" });
  },
};

// ─── Writing (AI generation — matches BE GenerateRequest) ───────────────────

export const writing = {
  /**
   * Stream AI-generated text via SSE.
   * Body matches BE GenerateRequest: { genre, prompt, context, chapter_title, max_tokens, temperature }
   */
  async generate(
    params: {
      genre: string;
      prompt: string;
      context?: string;
      chapter_title?: string;
      max_tokens?: number;
      temperature?: number;
    },
    options?: RequestOptions
  ): Promise<ReadableStream<string>> {
    let token: string | null = null;
    if (typeof window !== "undefined") {
      token = localStorage.getItem("access_token");
    }

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}/writing/generate`, {
      method: "POST",
      headers,
      body: JSON.stringify(params),
      signal: options?.signal,
    });

    if (!response.ok) {
      throw new ApiError("AI 생성 중 오류가 발생했습니다", response.status, "GENERATION_ERROR");
    }

    const reader = response.body!.getReader();
    const decoder = new TextDecoder();

    return new ReadableStream<string>({
      async pull(controller) {
        const { done, value } = await reader.read();
        if (done) {
          controller.close();
          return;
        }
        const text = decoder.decode(value, { stream: true });
        // Parse SSE events
        const lines = text.split("\n");
        for (const line of lines) {
          // M-01: SSE 에러 이벤트 감지 — 텍스트 삽입 대신 에러 throw
          if (line.startsWith("event: error")) {
            continue; // 다음 data 라인에서 에러 메시지 처리
          }
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") {
              controller.close();
              return;
            }
            try {
              const parsed = JSON.parse(data);
              // 에러 응답 감지
              if (parsed.error) {
                controller.error(new ApiError(parsed.error, 500, "SSE_ERROR"));
                return;
              }
              if (parsed.text) {
                controller.enqueue(parsed.text);
              }
            } catch {
              // 에러 메시지가 아닌 경우만 텍스트로 처리
              if (data.trim() && !data.includes("error")) {
                controller.enqueue(data);
              }
            }
          }
        }
      },
    });
  },

  async rewrite(
    originalText: string,
    instruction: string,
    genre: string,
    styleGuide?: string
  ): Promise<ApiResponse<{ rewritten_text: string; changes_summary: string }>> {
    return apiFetch("/writing/rewrite", {
      method: "POST",
      body: JSON.stringify({
        original_text: originalText,
        instruction,
        genre,
        style_guide: styleGuide ?? "",
      }),
    });
  },

  async structure(
    bookTitle: string,
    genre: string,
    description: string,
    targetChapters?: number
  ): Promise<ApiResponse<{ chapters: Array<{ order: number; title: string; description: string; estimated_pages: number }>; overall_summary: string }>> {
    return apiFetch("/writing/structure", {
      method: "POST",
      body: JSON.stringify({
        book_title: bookTitle,
        genre,
        description,
        target_chapters: targetChapters ?? 10,
      }),
    });
  },
};

// ─── Editing (matches BE ProofreadRequest, StyleCheckRequest, etc.) ─────────

export const editing = {
  /** POST /editing/proofread — BE ProofreadRequest { text, check_spelling, check_grammar, check_punctuation } */
  async proofread(
    text: string,
    options?: {
      check_spelling?: boolean;
      check_grammar?: boolean;
      check_punctuation?: boolean;
    }
  ): Promise<ApiResponse<{
    corrected_text: string;
    corrections: Array<{
      original: string;
      corrected: string;
      reason: string;
      position_start: number;
      position_end: number;
      severity: string;
    }>;
    total_corrections: number;
    accuracy_score: number;
  }>> {
    return apiFetch("/editing/proofread", {
      method: "POST",
      body: JSON.stringify({
        text,
        check_spelling: options?.check_spelling ?? true,
        check_grammar: options?.check_grammar ?? true,
        check_punctuation: options?.check_punctuation ?? true,
      }),
    });
  },

  /** POST /editing/style-check — BE StyleCheckRequest { text, reference_style, genre } */
  async styleCheck(
    text: string,
    referenceStyle?: string,
    genre?: string
  ): Promise<ApiResponse<{
    issues: Array<{
      text_excerpt: string;
      issue: string;
      suggestion: string;
      severity: string;
    }>;
    consistency_score: number;
    overall_feedback: string;
  }>> {
    return apiFetch("/editing/style-check", {
      method: "POST",
      body: JSON.stringify({
        text,
        reference_style: referenceStyle ?? "",
        genre: genre ?? "",
      }),
    });
  },

  /** POST /editing/structure-review — BE StructureReviewRequest { book_id, chapters[] } */
  async structureReview(
    bookId: string,
    chapters: string[]
  ): Promise<ApiResponse<{
    flow_score: number;
    organization_score: number;
    feedback: string[];
    suggestions: string[];
  }>> {
    return apiFetch("/editing/structure-review", {
      method: "POST",
      body: JSON.stringify({ book_id: bookId, chapters }),
    });
  },

  /** POST /editing/full-review — BE FullReviewRequest { book_id, include_stages[] } */
  async fullReview(
    bookId: string,
    includeStages?: string[]
  ): Promise<ApiResponse<QualityReport>> {
    return apiFetch("/editing/full-review", {
      method: "POST",
      body: JSON.stringify({
        book_id: bookId,
        include_stages: includeStages ?? ["structure", "content", "proofread", "final"],
      }),
    });
  },

  /** GET /editing/report/{book_id} — returns QualityReport */
  async report(bookId: string): Promise<ApiResponse<QualityReport>> {
    return apiFetch(`/editing/report/${bookId}`);
  },
};

// ─── Design (matches BE CoverGenerateRequest, LayoutPreviewRequest) ─────────

export const design = {
  /** POST /design/cover/generate — BE CoverGenerateRequest */
  async generateCover(params: {
    book_title: string;
    author_name: string;
    genre: string;
    style?: string;
    description?: string;
    color_scheme?: string;
  }): Promise<ApiResponse<{ image_url: string; prompt_used: string; style: string }>> {
    return apiFetch("/design/cover/generate", {
      method: "POST",
      body: JSON.stringify(params),
    });
  },

  /** GET /design/cover/templates — BE CoverTemplateListResponse */
  async templates(): Promise<ApiResponse<{ templates: CoverTemplate[]; total: number }>> {
    return apiFetch("/design/cover/templates");
  },

  /** POST /design/layout/preview — BE LayoutPreviewRequest */
  async layoutPreview(params: {
    book_id: string;
    page_size?: string;
    font_size?: number;
    line_spacing?: number;
  }): Promise<ApiResponse<{ preview_url: string; total_pages: number; page_size: string }>> {
    return apiFetch("/design/layout/preview", {
      method: "POST",
      body: JSON.stringify(params),
    });
  },
};

// ─── Publishing (matches BE ExportRequest, ExportStatus, ExportResponse) ────

export const publishing = {
  /** POST /publishing/export — BE ExportRequest { book_id, format, ... } */
  async exportBook(params: {
    book_id: string;
    format: ExportFormat;
    include_cover?: boolean;
    include_toc?: boolean;
    accessibility_tags?: boolean;
  }): Promise<ApiResponse<ExportResponse>> {
    return apiFetch("/publishing/export", {
      method: "POST",
      body: JSON.stringify(params),
    });
  },

  /** GET /publishing/export/{export_id} — BE ExportStatus */
  async status(exportId: string): Promise<ApiResponse<ExportStatus>> {
    return apiFetch(`/publishing/export/${exportId}`);
  },

  /** GET /publishing/download/{export_id} — returns file (Blob) */
  async download(exportId: string): Promise<Blob> {
    let token: string | null = null;
    if (typeof window !== "undefined") {
      token = localStorage.getItem("access_token");
    }

    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}/publishing/download/${exportId}`, {
      headers,
    });

    if (!response.ok) {
      throw new ApiError("다운로드 오류", response.status, "DOWNLOAD_ERROR");
    }

    return response.blob();
  },
};

// ─── TTS (matches BE TTSSynthesizeRequest { text, voice_id, speed, ... }) ───

export const tts = {
  async synthesize(
    text: string,
    voiceId?: string,
    speed?: number
  ): Promise<ArrayBuffer> {
    let token: string | null = null;
    if (typeof window !== "undefined") {
      token = localStorage.getItem("access_token");
    }

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    // Convert FE speed (0.5~2.0, 1.0=normal) to BE CLOVA speed (-5~5, 0=normal)
    const feSpeed = speed ?? 1.0;
    const beSpeed = Math.max(-5, Math.min(5, (feSpeed - 1.0) * 5.0));

    const response = await fetch(`${API_BASE}/tts/synthesize`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        text,
        voice_id: voiceId ?? "nara",
        speed: beSpeed,
      }),
    });

    if (!response.ok) {
      throw new ApiError("TTS 합성 오류", response.status, "TTS_ERROR");
    }

    return response.arrayBuffer();
  },

  /** GET /tts/voices — BE TTSVoiceListResponse { voices, total } */
  async voices(): Promise<ApiResponse<{ voices: TTSVoice[]; total: number }>> {
    return apiFetch("/tts/voices");
  },
};
