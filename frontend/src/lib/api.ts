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
  EditHistory,
  EditSuggestion,
  QualityReport,
  CoverTemplate,
  ExportFormat,
  ExportStatus,
  TTSVoice,
  User,
  SignUpData,
  LoginData,
  UserSettingsUpdate,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

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
    const errorBody = await response.json().catch(() => ({
      error: { code: "UNKNOWN", message: response.statusText },
    }));
    throw new ApiError(
      errorBody.error?.message || response.statusText,
      response.status,
      errorBody.error?.code || "UNKNOWN"
    );
  }

  return response.json();
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

  async login(data: LoginData): Promise<ApiResponse<{ user: User; accessToken: string }>> {
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
  async list(bookId: string): Promise<ApiResponse<Chapter[]>> {
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

// ─── Writing (AI generation) ─────────────────────────────────────────────────

export const writing = {
  /**
   * Stream AI-generated text via SSE.
   * Returns a ReadableStream that yields text chunks.
   */
  async generate(
    bookId: string,
    chapterId: string,
    prompt: string,
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
      body: JSON.stringify({ bookId, chapterId, prompt }),
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
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") {
              controller.close();
              return;
            }
            try {
              const parsed = JSON.parse(data);
              if (parsed.text) {
                controller.enqueue(parsed.text);
              }
            } catch {
              // Raw text chunk
              controller.enqueue(data);
            }
          }
        }
      },
    });
  },

  async rewrite(
    bookId: string,
    chapterId: string,
    content: string,
    instructions: string
  ): Promise<ApiResponse<{ rewritten: string }>> {
    return apiFetch("/writing/rewrite", {
      method: "POST",
      body: JSON.stringify({ bookId, chapterId, content, instructions }),
    });
  },

  async structure(
    bookId: string,
    description: string
  ): Promise<ApiResponse<{ chapters: Array<{ title: string; description: string }> }>> {
    return apiFetch("/writing/structure", {
      method: "POST",
      body: JSON.stringify({ bookId, description }),
    });
  },
};

// ─── Editing ─────────────────────────────────────────────────────────────────

export const editing = {
  async proofread(
    bookId: string,
    chapterId: string
  ): Promise<ApiResponse<{ suggestions: EditSuggestion[] }>> {
    return apiFetch(`/editing/proofread`, {
      method: "POST",
      body: JSON.stringify({ bookId, chapterId }),
    });
  },

  async styleCheck(
    bookId: string,
    chapterId: string
  ): Promise<ApiResponse<{ suggestions: EditSuggestion[] }>> {
    return apiFetch(`/editing/style-check`, {
      method: "POST",
      body: JSON.stringify({ bookId, chapterId }),
    });
  },

  async structureReview(
    bookId: string,
    chapterId: string
  ): Promise<ApiResponse<{ suggestions: EditSuggestion[] }>> {
    return apiFetch(`/editing/structure-review`, {
      method: "POST",
      body: JSON.stringify({ bookId, chapterId }),
    });
  },

  async fullReview(
    bookId: string
  ): Promise<ApiResponse<{ history: EditHistory[] }>> {
    return apiFetch(`/editing/full-review`, {
      method: "POST",
      body: JSON.stringify({ bookId }),
    });
  },

  async report(bookId: string, chapterId?: string): Promise<ApiResponse<QualityReport>> {
    const body: Record<string, string> = { bookId };
    if (chapterId) body.chapterId = chapterId;
    return apiFetch(`/editing/report`, {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
};

// ─── Design ──────────────────────────────────────────────────────────────────

export const design = {
  async generateCover(
    bookId: string,
    templateId?: string
  ): Promise<ApiResponse<{ coverUrl: string }>> {
    return apiFetch("/design/cover", {
      method: "POST",
      body: JSON.stringify({ bookId, templateId }),
    });
  },

  async templates(): Promise<ApiResponse<CoverTemplate[]>> {
    return apiFetch("/design/templates");
  },

  async layoutPreview(
    bookId: string,
    options: { fontSize?: number; fontFamily?: string }
  ): Promise<ApiResponse<{ previewUrl: string }>> {
    return apiFetch("/design/layout-preview", {
      method: "POST",
      body: JSON.stringify({ bookId, ...options }),
    });
  },
};

// ─── Publishing ──────────────────────────────────────────────────────────────

export const publishing = {
  async exportBook(
    bookId: string,
    format: ExportFormat
  ): Promise<ApiResponse<ExportStatus>> {
    return apiFetch("/publishing/export", {
      method: "POST",
      body: JSON.stringify({ bookId, format }),
    });
  },

  async status(exportId: string): Promise<ApiResponse<ExportStatus>> {
    return apiFetch(`/publishing/status/${exportId}`);
  },

  async download(exportId: string): Promise<string> {
    const result = await apiFetch<ApiResponse<{ downloadUrl: string }>>(
      `/publishing/download/${exportId}`
    );
    return result.data.downloadUrl;
  },
};

// ─── TTS ─────────────────────────────────────────────────────────────────────

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

    const response = await fetch(`${API_BASE}/tts/synthesize`, {
      method: "POST",
      headers,
      body: JSON.stringify({ text, voiceId, speed }),
    });

    if (!response.ok) {
      throw new ApiError("TTS 합성 오류", response.status, "TTS_ERROR");
    }

    return response.arrayBuffer();
  },

  async voices(): Promise<ApiResponse<TTSVoice[]>> {
    return apiFetch("/tts/voices");
  },
};
