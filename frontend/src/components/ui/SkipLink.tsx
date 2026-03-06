"use client";

/**
 * Skip to main content link.
 * Hidden until focused via Tab, allowing keyboard users to bypass navigation.
 */
export function SkipLink() {
  return (
    <a
      href="#main-content"
      className="
        sr-only focus:not-sr-only
        focus:fixed focus:top-4 focus:left-4 focus:z-[9999]
        focus:block focus:px-6 focus:py-3
        focus:bg-primary-500 focus:text-white
        focus:text-lg focus:font-bold focus:rounded-lg
        focus:ring-4 focus:ring-primary-600
        focus:outline-none
        focus:shadow-lg
      "
      aria-label="본문으로 건너뛰기"
    >
      본문으로 건너뛰기
    </a>
  );
}
