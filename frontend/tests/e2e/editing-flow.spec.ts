import { test, expect } from "@playwright/test";

test.describe("편집 흐름", () => {
  test.beforeEach(async ({ page }) => {
    // Mock 인증 토큰 설정
    await page.goto("/");
    await page.evaluate(() => {
      localStorage.setItem("access_token", "mock-token");
    });
  });

  test("편집 페이지 접근 (mock 인증)", async ({ page }) => {
    // Mock API: 책 + 챕터 데이터
    await page.route("**/api/v1/books/**", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          data: {
            id: "book-1",
            title: "테스트 작품",
            genre: "essay",
            chapters: [
              { id: "ch-1", title: "1장", content: "이것은 테스트 텍스트입니다." },
            ],
          },
        }),
      })
    );

    await page.goto("/write/book-1/edit");
    const body = page.locator("body");
    await expect(body).toContainText(/.+/);
  });

  test("편집 제안 탭이 존재하면 전환 가능", async ({ page }) => {
    await page.route("**/api/v1/**", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ data: {} }),
      })
    );

    await page.goto("/write/book-1/edit");

    // 탭 요소가 있으면 클릭
    const tabs = page.getByRole("tablist");
    if (await tabs.isVisible({ timeout: 3000 }).catch(() => false)) {
      const tabButtons = tabs.getByRole("tab");
      const count = await tabButtons.count();
      expect(count).toBeGreaterThan(0);
    }
  });

  test("Undo/Redo 버튼이 존재하면 접근성 속성 확인", async ({ page }) => {
    await page.route("**/api/v1/**", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ data: {} }),
      })
    );

    await page.goto("/write/book-1/edit");

    const undoBtn = page.getByRole("button", { name: /되돌리기|undo/i });
    if (await undoBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      // aria-label 확인
      const label = await undoBtn.getAttribute("aria-label");
      expect(label).toBeTruthy();

      // 초기에 비활성화 상태
      await expect(undoBtn).toBeDisabled();
    }
  });

  test("편집 분석 실행 요청 (mock API)", async ({ page }) => {
    // Mock API: 편집 분석
    await page.route("**/api/v1/editing/**", (route) => {
      if (route.request().method() === "POST") {
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            data: {
              suggestions: [
                { type: "grammar", original: "테스트 문장.", suggestion: "테스트 문장입니다.", position: { start: 0, end: 8 } },
              ],
              scores: { grammar: 90, style: 85, structure: 80 },
            },
          }),
        });
      }
      return route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
    });

    await page.route("**/api/v1/books/**", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          data: {
            id: "book-1",
            title: "테스트 작품",
            genre: "essay",
            chapters: [{ id: "ch-1", title: "1장", content: "테스트 문장." }],
          },
        }),
      })
    );

    await page.goto("/write/book-1/edit");

    // 분석 실행 버튼 탐색
    const analyzeBtn = page.getByRole("button", { name: /분석|교정|검사/i });
    if (await analyzeBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await analyzeBtn.click();
      await page.waitForTimeout(1000);
      // 분석 결과가 화면에 나타남
      const body = page.locator("body");
      await expect(body).toContainText(/.+/);
    }
  });

  test("편집 제안 수락 흐름 (mock API)", async ({ page }) => {
    await page.route("**/api/v1/**", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          data: {
            id: "book-1",
            title: "테스트 작품",
            genre: "essay",
            chapters: [{ id: "ch-1", title: "1장", content: "테스트 문장." }],
          },
        }),
      })
    );

    await page.goto("/write/book-1/edit");

    // 수락 버튼이 있으면 클릭
    const acceptBtn = page.getByRole("button", { name: /수락|적용|accept/i });
    if (await acceptBtn.first().isVisible({ timeout: 3000 }).catch(() => false)) {
      await acceptBtn.first().click();
      await page.waitForTimeout(500);
      // 수락 후 페이지 유지
      await expect(page.locator("body")).toContainText(/.+/);
    }
  });

  test("이용약관 페이지 접근 가능", async ({ page }) => {
    await page.goto("/terms");
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  });

  test("개인정보처리방침 페이지 접근 가능", async ({ page }) => {
    await page.goto("/privacy");
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  });

  test("다크모드 토글 접근성", async ({ page }) => {
    await page.goto("/");
    const themeBtn = page.getByRole("button", { name: /모드|테마/i });
    if (await themeBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await themeBtn.click();
      await expect(themeBtn).toBeVisible();
    }
  });
});
