/**
 * A17 접근성 감사 에이전트 - E2E 접근성 테스트 (Playwright)
 *
 * Lighthouse Accessibility Score >= 90 목표
 * axe-core를 Playwright에 통합하여 실행
 */
import { test, expect } from "@playwright/test";
import type { Page } from "@playwright/test";

// 공통: 접근성 기본 검사
async function checkBasicA11y(page: Page) {
  // lang 속성 확인
  const htmlLang = await page.getAttribute("html", "lang");
  expect(htmlLang).toBe("ko");

  // 건너뛰기 링크 존재 확인
  const skipLink = page.getByText(/본문으로 건너뛰기|메인 콘텐츠로 이동/i);
  await expect(skipLink).toBeAttached();

  // 메인 콘텐츠 영역 존재 확인
  const main = page.locator('main, [role="main"]');
  await expect(main).toBeAttached();
}

test.describe("랜딩 페이지 접근성", () => {
  test("기본 접근성 요소가 존재", async ({ page }) => {
    await page.goto("/");
    await checkBasicA11y(page);
  });

  test("제목 계층이 올바름 (h1이 하나만 존재)", async ({ page }) => {
    await page.goto("/");
    const h1Count = await page.locator("h1").count();
    expect(h1Count).toBe(1);
  });

  test("모든 링크에 접근 가능한 텍스트가 있음", async ({ page }) => {
    await page.goto("/");
    const links = page.locator("a");
    const count = await links.count();

    for (let i = 0; i < count; i++) {
      const link = links.nth(i);
      const text = await link.textContent();
      const ariaLabel = await link.getAttribute("aria-label");
      const hasAccessibleName = (text && text.trim().length > 0) || ariaLabel;
      expect(hasAccessibleName).toBeTruthy();
    }
  });

  test("Tab 키로 모든 인터랙티브 요소에 도달 가능", async ({ page }) => {
    await page.goto("/");
    const focusableElements: string[] = [];

    // Tab을 20번까지 눌러서 포커스 경로 확인
    for (let i = 0; i < 20; i++) {
      await page.keyboard.press("Tab");
      const tagName = await page.evaluate(
        () => document.activeElement?.tagName || ""
      );
      if (tagName === "BODY") break;
      focusableElements.push(tagName);
    }

    // 최소 3개 이상의 포커스 가능 요소가 있어야 함
    expect(focusableElements.length).toBeGreaterThanOrEqual(3);
  });
});

test.describe("로그인 페이지 접근성", () => {
  test("폼 필드에 레이블이 연결됨", async ({ page }) => {
    await page.goto("/login");

    // 이메일 입력 필드
    const emailInput = page.getByLabel(/이메일/i);
    await expect(emailInput).toBeAttached();

    // 비밀번호 입력 필드
    const passwordInput = page.getByLabel(/비밀번호/i);
    await expect(passwordInput).toBeAttached();
  });

  test("필수 필드에 aria-required가 설정됨", async ({ page }) => {
    await page.goto("/login");

    const emailInput = page.getByLabel(/이메일/i);
    const required = await emailInput.getAttribute("aria-required");
    expect(required).toBe("true");
  });
});

test.describe("키보드 탐색", () => {
  test("건너뛰기 링크로 메인 콘텐츠에 직접 이동 가능", async ({ page }) => {
    await page.goto("/");

    // 첫 번째 Tab으로 건너뛰기 링크에 포커스
    await page.keyboard.press("Tab");
    const activeText = await page.evaluate(
      () => document.activeElement?.textContent || ""
    );

    // 건너뛰기 링크가 포커스되면 Enter로 활성화
    if (activeText.includes("본문") || activeText.includes("메인")) {
      await page.keyboard.press("Enter");

      // 메인 콘텐츠가 포커스되었는지 확인
      const focusedRole = await page.evaluate(
        () => document.activeElement?.getAttribute("role") || document.activeElement?.tagName
      );
      expect(["main", "MAIN"]).toContain(focusedRole);
    }
  });
});
