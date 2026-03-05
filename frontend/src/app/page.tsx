import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "모두가 작가 - AI 글쓰기 플랫폼",
};

/**
 * Landing page.
 * Introduces the service with a hero section and CTA.
 */
export default function HomePage() {
  return (
    <div className="flex flex-col items-center gap-12 py-12">
      {/* Hero Section */}
      <section className="text-center max-w-3xl" aria-label="서비스 소개">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-gray-100 mb-6">
          당신의 이야기를,
          <br />
          <span className="text-primary-700 dark:text-primary-400">목소리</span>로
          써보세요
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 leading-relaxed mb-8">
          모두가 작가는 시각 장애인을 위한 AI 기반 글쓰기 플랫폼입니다.
          <br />
          음성으로 이야기하면 AI가 아름다운 글로 완성해 드립니다.
        </p>
        <Link
          href="/signup"
          className="
            inline-flex items-center justify-center
            bg-primary-400 text-gray-900
            px-8 py-4 rounded-xl
            text-xl font-bold
            hover:bg-primary-500
            focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-600
            no-underline
            min-h-touch
            shadow-lg hover:shadow-xl
            transition-all duration-200
          "
          aria-label="시작하기 - 회원가입 페이지로 이동"
        >
          시작하기
        </Link>
      </section>

      {/* How it works */}
      <section className="w-full max-w-4xl" aria-label="이용 방법">
        <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-gray-100 mb-8">
          이렇게 사용해요
        </h2>
        <ol className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              step: 1,
              title: "말하기",
              description:
                "마이크 버튼을 누르고 당신의 이야기를 들려주세요. 음성 인식이 자동으로 텍스트로 변환합니다.",
            },
            {
              step: 2,
              title: "AI와 함께 쓰기",
              description:
                "AI가 당신의 이야기를 에세이, 소설, 시 등 원하는 형태로 아름답게 다듬어 줍니다.",
            },
            {
              step: 3,
              title: "출판하기",
              description:
                "AI 편집과 교정을 거쳐 완성된 작품을 PDF, 전자책 등으로 내보내세요.",
            },
          ].map((item) => (
            <li
              key={item.step}
              className="
                flex flex-col items-center text-center
                p-6 rounded-xl
                bg-gray-50 dark:bg-gray-800
                border border-gray-200 dark:border-gray-700
              "
            >
              <span
                className="
                  w-12 h-12 rounded-full
                  bg-primary-400 text-gray-900
                  flex items-center justify-center
                  text-xl font-bold mb-4
                "
                aria-hidden="true"
              >
                {item.step}
              </span>
              <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                {item.step}단계: {item.title}
              </h3>
              <p className="text-base text-gray-600 dark:text-gray-400 leading-relaxed">
                {item.description}
              </p>
            </li>
          ))}
        </ol>
      </section>

      {/* Accessibility info */}
      <section
        className="w-full max-w-3xl text-center py-8"
        aria-label="접근성 안내"
      >
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
          모든 사용자를 위한 설계
        </h2>
        <p className="text-base text-gray-600 dark:text-gray-400 leading-relaxed">
          모두가 작가는 WCAG 2.1 AA 접근성 지침을 준수합니다.
          <br />
          키보드만으로 모든 기능을 사용할 수 있으며,
          <br />
          스크린 리더와 완벽하게 호환됩니다.
        </p>
      </section>
    </div>
  );
}
