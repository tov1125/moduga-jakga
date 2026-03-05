import { auth, books, ApiError } from "@/lib/api";

const mockFetch = vi.fn();
global.fetch = mockFetch;

// localStorage mock
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] ?? null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
  };
})();
Object.defineProperty(globalThis, "localStorage", { value: localStorageMock });

const API_BASE = "http://localhost:8000/api/v1";

function mockResponse(body: unknown, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    statusText: status === 200 ? "OK" : "Error",
    json: () => Promise.resolve(body),
  });
}

describe("ApiError", () => {
  it("인스턴스 생성 시 올바른 속성을 가짐", () => {
    const error = new ApiError("테스트 에러", 404, "NOT_FOUND");

    expect(error).toBeInstanceOf(Error);
    expect(error).toBeInstanceOf(ApiError);
    expect(error.message).toBe("테스트 에러");
    expect(error.status).toBe(404);
    expect(error.code).toBe("NOT_FOUND");
    expect(error.name).toBe("ApiError");
  });

  it("Error 상속으로 stack trace를 포함", () => {
    const error = new ApiError("서버 에러", 500, "INTERNAL");
    expect(error.stack).toBeDefined();
  });
});

describe("auth", () => {
  beforeEach(() => {
    mockFetch.mockReset();
    localStorageMock.clear();
  });

  it("login 성공 시 올바른 endpoint와 body로 fetch 호출", async () => {
    const responseData = {
      user: { id: "u1", email: "test@example.com" },
      access_token: "tok123",
      token_type: "bearer",
      expires_in: "3600",
    };
    mockFetch.mockReturnValueOnce(mockResponse(responseData));

    const result = await auth.login({
      email: "test@example.com",
      password: "password123",
    });

    expect(mockFetch).toHaveBeenCalledTimes(1);
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/auth/login`);
    expect(options.method).toBe("POST");
    expect(JSON.parse(options.body)).toEqual({
      email: "test@example.com",
      password: "password123",
    });
    expect(result).toEqual({ success: true, data: responseData });
  });

  it("login 실패 시 ApiError를 throw", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse(
        { error: { code: "INVALID_CREDENTIALS", message: "잘못된 인증 정보" } },
        401
      )
    );

    await expect(
      auth.login({ email: "bad@example.com", password: "wrong" })
    ).rejects.toThrow(ApiError);

    try {
      mockFetch.mockReturnValueOnce(
        mockResponse(
          { error: { code: "INVALID_CREDENTIALS", message: "잘못된 인증 정보" } },
          401
        )
      );
      await auth.login({ email: "bad@example.com", password: "wrong" });
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError);
      expect((e as ApiError).status).toBe(401);
      expect((e as ApiError).code).toBe("INVALID_CREDENTIALS");
    }
  });

  it("Authorization 헤더에 토큰이 포함됨", async () => {
    localStorageMock.setItem("access_token", "my-jwt-token");

    mockFetch.mockReturnValueOnce(
      mockResponse({ id: "u1", email: "test@example.com" })
    );

    await auth.me();

    const [, options] = mockFetch.mock.calls[0];
    expect(options.headers["Authorization"]).toBe("Bearer my-jwt-token");
  });

  it("토큰이 없으면 Authorization 헤더 없음", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ id: "u1", email: "test@example.com" })
    );

    await auth.me();

    const [, options] = mockFetch.mock.calls[0];
    expect(options.headers["Authorization"]).toBeUndefined();
  });
});

describe("books", () => {
  beforeEach(() => {
    mockFetch.mockReset();
    localStorageMock.clear();
  });

  it("list가 올바른 query param으로 호출", async () => {
    const responseData = {
      items: [],
      total: 0,
      page: 2,
      page_size: 5,
    };
    mockFetch.mockReturnValueOnce(mockResponse(responseData));

    await books.list(2, 5);

    const [url] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/books?page=2&page_size=5`);
  });

  it("list 기본 파라미터 (page=1, pageSize=10)", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));

    await books.list();

    const [url] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/books?page=1&page_size=10`);
  });

  it("create가 POST로 올바른 body 전송", async () => {
    const newBook = { title: "나의 첫 책", genre: "essay" };
    mockFetch.mockReturnValueOnce(
      mockResponse({ id: "b1", ...newBook })
    );

    await books.create(newBook as never);

    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/books`);
    expect(options.method).toBe("POST");
    expect(JSON.parse(options.body)).toEqual(newBook);
  });

  it("create 시 Authorization 헤더에 토큰 포함", async () => {
    localStorageMock.setItem("access_token", "book-token");

    mockFetch.mockReturnValueOnce(
      mockResponse({ id: "b1", title: "테스트" })
    );

    await books.create({ title: "테스트", genre: "novel" } as never);

    const [, options] = mockFetch.mock.calls[0];
    expect(options.headers["Authorization"]).toBe("Bearer book-token");
  });

  it("서버 에러 시 ApiError를 throw", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse(
        { error: { code: "SERVER_ERROR", message: "서버 오류" } },
        500
      )
    );

    await expect(books.list()).rejects.toThrow(ApiError);
  });

  it("get이 올바른 URL로 호출", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ id: "b1", title: "테스트" }));
    await books.get("b1");
    const [url] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/books/b1`);
  });

  it("update가 PATCH로 올바른 body 전송", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ id: "b1", title: "수정됨" }));
    await books.update("b1", { title: "수정됨" } as never);
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/books/b1`);
    expect(options.method).toBe("PATCH");
  });

  it("delete가 DELETE로 호출", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(null));
    await books.delete("b1");
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/books/b1`);
    expect(options.method).toBe("DELETE");
  });
});

import { chapters, editing, design, publishing, tts, writing } from "@/lib/api";

describe("chapters", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it("list가 올바른 URL로 호출", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ chapters: [], total: 0 }));
    await chapters.list("b1");
    const [url] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/books/b1/chapters`);
  });

  it("create가 POST로 호출", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ id: "ch1", title: "1장" }));
    await chapters.create("b1", { title: "1장" } as never);
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/books/b1/chapters`);
    expect(options.method).toBe("POST");
  });

  it("get이 올바른 URL로 호출", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ id: "ch1" }));
    await chapters.get("b1", "ch1");
    const [url] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/books/b1/chapters/ch1`);
  });

  it("update가 PATCH로 호출", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ id: "ch1" }));
    await chapters.update("b1", "ch1", { title: "수정됨" } as never);
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/books/b1/chapters/ch1`);
    expect(options.method).toBe("PATCH");
  });

  it("delete가 DELETE로 호출", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(null));
    await chapters.delete("b1", "ch1");
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/books/b1/chapters/ch1`);
    expect(options.method).toBe("DELETE");
  });
});

describe("auth 추가", () => {
  beforeEach(() => {
    mockFetch.mockReset();
    localStorageMock.clear();
  });

  it("signup이 POST로 호출", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ id: "u1" }));
    await auth.signup({ email: "a@b.com", password: "p", display_name: "작가" } as never);
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/auth/signup`);
    expect(options.method).toBe("POST");
  });

  it("logout이 POST로 호출", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(null));
    await auth.logout();
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/auth/logout`);
    expect(options.method).toBe("POST");
  });

  it("updateSettings가 PATCH로 호출", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ id: "u1" }));
    await auth.updateSettings({ display_name: "새이름" } as never);
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/auth/settings`);
    expect(options.method).toBe("PATCH");
  });
});

describe("editing", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it("proofread가 POST로 올바른 body 전송", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ corrected_text: "수정됨", corrections: [], total_corrections: 0, accuracy_score: 100 }));
    await editing.proofread("테스트 텍스트", { check_spelling: true, check_grammar: false });
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/editing/proofread`);
    expect(options.method).toBe("POST");
    const body = JSON.parse(options.body);
    expect(body.text).toBe("테스트 텍스트");
    expect(body.check_spelling).toBe(true);
    expect(body.check_grammar).toBe(false);
    expect(body.check_punctuation).toBe(true); // default
  });

  it("styleCheck이 POST로 호출", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ issues: [], consistency_score: 95, overall_feedback: "좋음" }));
    await editing.styleCheck("텍스트", "문어체", "essay");
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/editing/style-check`);
    const body = JSON.parse(options.body);
    expect(body.reference_style).toBe("문어체");
    expect(body.genre).toBe("essay");
  });

  it("structureReview가 POST로 호출", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ flow_score: 80, organization_score: 85, feedback: [], suggestions: [] }));
    await editing.structureReview("b1", ["ch1", "ch2"]);
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/editing/structure-review`);
    const body = JSON.parse(options.body);
    expect(body.book_id).toBe("b1");
    expect(body.chapters).toEqual(["ch1", "ch2"]);
  });

  it("fullReview가 POST로 호출 (기본 stages)", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ overall_score: 90 }));
    await editing.fullReview("b1");
    const [, options] = mockFetch.mock.calls[0];
    const body = JSON.parse(options.body);
    expect(body.include_stages).toEqual(["structure", "content", "proofread", "final"]);
  });

  it("report가 GET으로 호출", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ overall_score: 85 }));
    await editing.report("b1");
    const [url] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/editing/report/b1`);
  });
});

describe("design", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it("generateCover가 POST로 올바른 body 전송", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ image_url: "http://img", prompt_used: "p", style: "modern" }));
    await design.generateCover({ book_title: "제목", author_name: "작가", genre: "essay" });
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/design/cover/generate`);
    expect(options.method).toBe("POST");
    const body = JSON.parse(options.body);
    expect(body.book_title).toBe("제목");
  });

  it("templates가 GET으로 호출", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ templates: [], total: 0 }));
    await design.templates();
    const [url] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/design/cover/templates`);
  });

  it("layoutPreview가 POST로 호출", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ preview_url: "http://p", total_pages: 10, page_size: "A5" }));
    await design.layoutPreview({ book_id: "b1", page_size: "A5" });
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/design/layout/preview`);
    expect(options.method).toBe("POST");
  });
});

describe("publishing", () => {
  beforeEach(() => {
    mockFetch.mockReset();
    localStorageMock.clear();
  });

  it("exportBook이 POST로 올바른 body 전송", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ export_id: "e1", status: "processing" }));
    await publishing.exportBook({ book_id: "b1", format: "pdf" as never });
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/publishing/export`);
    expect(options.method).toBe("POST");
    const body = JSON.parse(options.body);
    expect(body.book_id).toBe("b1");
    expect(body.format).toBe("pdf");
  });

  it("status가 GET으로 호출", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ export_id: "e1", status: "completed" }));
    await publishing.status("e1");
    const [url] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/publishing/export/e1`);
  });

  it("download가 blob을 반환", async () => {
    const mockBlob = new Blob(["test"], { type: "application/pdf" });
    mockFetch.mockReturnValueOnce(
      Promise.resolve({
        ok: true,
        status: 200,
        blob: () => Promise.resolve(mockBlob),
      })
    );
    const result = await publishing.download("e1");
    expect(result).toBeInstanceOf(Blob);
    const [url] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/publishing/download/e1`);
  });

  it("download 실패 시 ApiError throw", async () => {
    mockFetch.mockReturnValueOnce(
      Promise.resolve({ ok: false, status: 404 })
    );
    await expect(publishing.download("e1")).rejects.toThrow(ApiError);
  });
});

describe("tts", () => {
  beforeEach(() => {
    mockFetch.mockReset();
    localStorageMock.clear();
  });

  it("synthesize가 POST로 올바른 body 전송", async () => {
    const mockBuffer = new ArrayBuffer(8);
    mockFetch.mockReturnValueOnce(
      Promise.resolve({
        ok: true,
        status: 200,
        arrayBuffer: () => Promise.resolve(mockBuffer),
      })
    );
    const result = await tts.synthesize("안녕하세요", "nara", 1.0);
    expect(result).toBeInstanceOf(ArrayBuffer);
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/tts/synthesize`);
    expect(options.method).toBe("POST");
    const body = JSON.parse(options.body);
    expect(body.text).toBe("안녕하세요");
    expect(body.voice_id).toBe("nara");
    expect(body.speed).toBe(0); // 1.0 → 0 (normal)
  });

  it("synthesize 속도 변환이 올바름", async () => {
    mockFetch.mockReturnValueOnce(
      Promise.resolve({
        ok: true,
        status: 200,
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(8)),
      })
    );
    await tts.synthesize("텍스트", "nara", 2.0);
    const body = JSON.parse(mockFetch.mock.calls[0][1].body);
    expect(body.speed).toBe(5); // 2.0 → 5
  });

  it("synthesize 실패 시 ApiError throw", async () => {
    mockFetch.mockReturnValueOnce(
      Promise.resolve({ ok: false, status: 500 })
    );
    await expect(tts.synthesize("텍스트")).rejects.toThrow(ApiError);
  });

  it("voices가 GET으로 호출", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ voices: [], total: 0 }));
    await tts.voices();
    const [url] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/tts/voices`);
  });
});

describe("writing", () => {
  beforeEach(() => {
    mockFetch.mockReset();
    localStorageMock.clear();
  });

  it("rewrite가 POST로 올바른 body 전송", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ rewritten_text: "수정됨", changes_summary: "요약" }));
    await writing.rewrite("원본", "명료하게", "essay", "문어체");
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/writing/rewrite`);
    expect(options.method).toBe("POST");
    const body = JSON.parse(options.body);
    expect(body.original_text).toBe("원본");
    expect(body.instruction).toBe("명료하게");
    expect(body.genre).toBe("essay");
    expect(body.style_guide).toBe("문어체");
  });

  it("structure가 POST로 올바른 body 전송", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ chapters: [], overall_summary: "요약" }));
    await writing.structure("제목", "novel", "설명", 12);
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/writing/structure`);
    const body = JSON.parse(options.body);
    expect(body.book_title).toBe("제목");
    expect(body.target_chapters).toBe(12);
  });

  it("generate가 SSE 스트림을 반환", async () => {
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode('data: {"text":"안녕"}\n\n'));
        controller.enqueue(encoder.encode("data: [DONE]\n\n"));
        controller.close();
      },
    });
    mockFetch.mockReturnValueOnce(
      Promise.resolve({ ok: true, status: 200, body: stream })
    );
    const result = await writing.generate({ genre: "essay", prompt: "테스트" });
    const reader = result.getReader();
    const { value } = await reader.read();
    expect(value).toBe("안녕");
  });

  it("generate 실패 시 ApiError throw", async () => {
    mockFetch.mockReturnValueOnce(
      Promise.resolve({ ok: false, status: 500 })
    );
    await expect(writing.generate({ genre: "essay", prompt: "테스트" })).rejects.toThrow(ApiError);
  });
});
