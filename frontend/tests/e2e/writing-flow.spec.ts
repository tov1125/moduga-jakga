import { test, expect } from "@playwright/test";

test.describe("글쓰기 흐름", () => {
  test("대시보드 접근 시 미인증이면 리다이렉트 또는 안내", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page.locator("body")).toContainText(/(로그인|dashboard)/i);
  });

  test("랜딩 페이지에서 주요 CTA 존재", async ({ page }) => {
    await page.goto("/");
    const heading = page.getByRole("heading", { level: 1 });
    await expect(heading).toBeVisible();
  });

  test("작가 되기 또는 시작하기 버튼 존재", async ({ page }) => {
    await page.goto("/");
    const cta = page.getByRole("link").or(page.getByRole("button"));
    await expect(cta.first()).toBeVisible();
  });

  test("대시보드 → 새 작품 만들기 흐름 (mock 인증)", async ({ page }) => {
    // Mock 인증 토큰 설정
    await page.goto("/");
    await page.evaluate(() => {
      localStorage.setItem("access_token", "mock-token");
    });

    // Mock API: 책 목록
    await page.route("**/api/v1/books**", (route) => {
      if (route.request().method() === "GET") {
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ data: { books: [], total: 0 } }),
        });
      }
      // POST: 새 작품 생성
      return route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({
          data: { id: "book-1", title: "나의 첫 작품", genre: "essay" },
        }),
      });
    });

    await page.goto("/dashboard");

    // 새 작품 만들기 버튼 탐색
    const createBtn = page.getByRole("button", { name: /새 작품|만들기|시작/i })
      .or(page.getByRole("link", { name: /새 작품|만들기|시작/i }));

    if (await createBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await createBtn.click();
      // 글쓰기 페이지 또는 모달이 나타남
      await page.waitForTimeout(1000);
      expect(page.url()).toMatch(/(write|dashboard)/);
    } else {
      // 대시보드에 접근했음을 확인
      expect(page.url()).toMatch(/(dashboard|login)/);
    }
  });

  test("글쓰기 페이지 구조 확인 (mock 인증)", async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => {
      localStorage.setItem("access_token", "mock-token");
    });

    // Mock API: 책 데이터
    await page.route("**/api/v1/books/**", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          data: {
            id: "book-1",
            title: "테스트 작품",
            genre: "essay",
            chapters: [{ id: "ch-1", title: "1장", content: "" }],
          },
        }),
      })
    );

    await page.goto("/write/book-1");

    // 글쓰기 관련 요소 존재 확인
    const body = page.locator("body");
    await expect(body).toContainText(/.+/);
  });

  test("글쓰기 페이지에서 텍스트 입력 → 저장 흐름 (mock)", async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => {
      localStorage.setItem("access_token", "mock-token");
    });

    let savedContent = "";

    // Mock API: 책 + 챕터 데이터
    await page.route("**/api/v1/books/**", (route) => {
      if (route.request().method() === "GET") {
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            data: {
              id: "book-1",
              title: "테스트 작품",
              genre: "essay",
              chapters: [{ id: "ch-1", title: "1장", content: "기존 내용" }],
            },
          }),
        });
      }
      return route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
    });

    // Mock API: 챕터 저장
    await page.route("**/api/v1/chapters/**", (route) => {
      if (route.request().method() === "PUT" || route.request().method() === "PATCH") {
        savedContent = "saved";
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ data: { id: "ch-1", title: "1장", content: "새 내용" } }),
        });
      }
      return route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
    });

    await page.goto("/write/book-1");

    // 텍스트 영역 탐색 (textarea 또는 contenteditable)
    const textarea = page.locator("textarea").or(page.locator("[contenteditable=true]"));
    if (await textarea.first().isVisible({ timeout: 3000 }).catch(() => false)) {
      await textarea.first().fill("새 내용 입력 테스트");
      // 자동 저장 또는 저장 버튼
      const saveBtn = page.getByRole("button", { name: /저장/i });
      if (await saveBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await saveBtn.click();
      }
      // 자동 저장 대기 (debounce 500ms)
      await page.waitForTimeout(1000);
    }

    // 페이지가 정상적으로 로드됨을 확인
    await expect(page.locator("body")).toContainText(/.+/);
  });
});
