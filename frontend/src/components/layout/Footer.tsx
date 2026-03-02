"use client";

/**
 * App footer with accessibility information and links.
 */
export function Footer() {
  return (
    <footer
      className="
        w-full border-t border-gray-200 dark:border-gray-700
        bg-white dark:bg-gray-900
        px-6 py-6 mt-auto
      "
      role="contentinfo"
    >
      <div className="max-w-7xl mx-auto text-center">
        <p className="text-gray-600 dark:text-gray-400 text-base">
          모두가 작가 - 시각 장애인을 위한 AI 글쓰기 플랫폼
        </p>
        <p className="text-gray-500 dark:text-gray-500 text-sm mt-2">
          이 서비스는 웹 접근성 지침(WCAG 2.1 AA)을 준수합니다.
        </p>
        <p className="text-gray-500 dark:text-gray-500 text-sm mt-1">
          문의: support@modugajakga.kr | 접근성 관련 의견 환영합니다.
        </p>
      </div>
    </footer>
  );
}
