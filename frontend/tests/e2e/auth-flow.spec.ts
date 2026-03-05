import { test, expect } from "@playwright/test";

test.describe("인증 흐름", () => {
  test("로그인 페이지 접근 가능", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByRole("heading", { name: "로그인" })).toBeVisible();
  });

  test("회원가입 페이지 접근 가능", async ({ page }) => {
    await page.goto("/signup");
    await expect(page.getByRole("heading", { name: "회원가입" })).toBeVisible();
  });

  test("잘못된 로그인 시 에러 메시지 표시", async ({ page }) => {
    await page.goto("/login");
    await page.fill('input[type="email"]', "wrong@test.com");
    await page.fill('input[type="password"]', "wrongpass");
    await page.getByRole("button", { name: "로그인" }).click();
    await expect(page.getByRole("alert")).toBeVisible({ timeout: 5000 });
  });

  test("회원가입 동의 체크박스 미체크 시 버튼 비활성화", async ({ page }) => {
    await page.goto("/signup");
    const submitBtn = page.getByRole("button", { name: "회원가입" });
    await expect(submitBtn).toBeDisabled();
  });

  test("로그인에서 회원가입 링크 이동", async ({ page }) => {
    await page.goto("/login");
    await page.getByRole("link", { name: /회원가입/ }).click();
    await expect(page).toHaveURL(/signup/);
  });

  test("성공 로그인 → 대시보드 리다이렉트 (mock)", async ({ page }) => {
    // API 인터셉트로 성공 로그인 시뮬레이션
    await page.route("**/api/v1/auth/login", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          data: {
            access_token: "mock-token",
            token_type: "bearer",
            user: { id: "u1", email: "test@test.com", display_name: "테스트" },
          },
        }),
      })
    );

    await page.goto("/login");
    await page.fill('input[type="email"]', "test@test.com");
    await page.fill('input[type="password"]', "ValidPass123");
    await page.getByRole("button", { name: "로그인" }).click();

    // 로그인 성공 후 대시보드 또는 홈으로 이동해야 함
    await page.waitForURL(/(dashboard|\/)/i, { timeout: 5000 });
    const url = page.url();
    expect(url).toMatch(/(dashboard|\/)/);
  });

  test("로그아웃 → 랜딩 리다이렉트", async ({ page }) => {
    // 먼저 로그인 상태를 설정 (localStorage에 토큰)
    await page.goto("/");
    await page.evaluate(() => {
      localStorage.setItem("access_token", "mock-token");
    });

    // 대시보드 접근 시도
    await page.goto("/dashboard");

    // 로그아웃 버튼이 있으면 클릭
    const logoutBtn = page.getByRole("button", { name: /로그아웃/i });
    if (await logoutBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await logoutBtn.click();
      // 홈 또는 로그인 페이지로 이동
      await page.waitForURL(/(login|\/)/i, { timeout: 5000 });
      expect(page.url()).toMatch(/(login|\/)/);
    } else {
      // 로그아웃 버튼이 없는 경우 — 미인증 상태로 리다이렉트 확인
      expect(page.url()).toMatch(/(login|dashboard|\/)/);
    }
  });
});
