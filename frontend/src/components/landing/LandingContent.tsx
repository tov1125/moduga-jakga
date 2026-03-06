"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Mic,
  PenTool,
  BookOpen,
  ShieldCheck,
  Keyboard,
  Volume2,
  ChevronLeft,
  ChevronRight,
  ArrowRight,
} from "lucide-react";

const PHRASES = [
  "말하다...",
  "글이 되다...",
  "책이 되다...",
  "작가가 되다",
];

const QUOTES = [
  {
    text: "나의 목소리가 한 줄의 문장이 되는 순간,\n나는 비로소 작가가 되었다.",
    author: "첫 번째 이야기",
  },
  {
    text: "보이지 않아도 느낄 수 있고,\n느낀 것을 글로 남길 수 있다.",
    author: "두 번째 이야기",
  },
  {
    text: "AI가 나의 손이 되어주었고,\n세상이 나의 독자가 되었다.",
    author: "세 번째 이야기",
  },
];

const STEPS = [
  {
    icon: Mic,
    step: 1,
    title: "말하기",
    description:
      "마이크 버튼을 누르고 이야기를 들려주세요. 음성 인식이 자동으로 텍스트로 변환합니다.",
  },
  {
    icon: PenTool,
    step: 2,
    title: "AI와 함께 쓰기",
    description:
      "AI가 이야기를 에세이, 소설, 시 등 원하는 형태로 아름답게 다듬어 줍니다.",
  },
  {
    icon: BookOpen,
    step: 3,
    title: "출판하기",
    description:
      "편집과 교정을 거쳐 완성된 작품을 PDF, 전자책으로 출판하세요.",
  },
];

const BADGES = [
  {
    icon: ShieldCheck,
    title: "WCAG 2.1 AA",
    description:
      "국제 웹 접근성 지침을 준수하여 모든 사용자가 동등하게 이용할 수 있습니다.",
  },
  {
    icon: Keyboard,
    title: "키보드 내비게이션",
    description:
      "마우스 없이 키보드만으로 모든 기능을 완벽하게 사용할 수 있습니다.",
  },
  {
    icon: Volume2,
    title: "스크린 리더 호환",
    description:
      "VoiceOver, NVDA 등 스크린 리더와 완벽하게 호환됩니다.",
  },
];

export function LandingContent() {
  const [phraseIndex, setPhraseIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);
  const [quoteIndex, setQuoteIndex] = useState(0);
  const [isCarouselPaused, setIsCarouselPaused] = useState(false);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mql = window.matchMedia("(prefers-reduced-motion: reduce)");
    setPrefersReducedMotion(mql.matches);
    const handler = (e: MediaQueryListEvent) =>
      setPrefersReducedMotion(e.matches);
    mql.addEventListener("change", handler);
    return () => mql.removeEventListener("change", handler);
  }, []);

  // Typing animation
  useEffect(() => {
    if (prefersReducedMotion) {
      setCharIndex(PHRASES[phraseIndex].length);
      return;
    }

    const currentPhrase = PHRASES[phraseIndex];

    if (!isDeleting && charIndex < currentPhrase.length) {
      const timeout = setTimeout(() => setCharIndex((c) => c + 1), 100);
      return () => clearTimeout(timeout);
    }

    if (!isDeleting && charIndex === currentPhrase.length) {
      // Last phrase stays
      if (phraseIndex === PHRASES.length - 1) return;
      const timeout = setTimeout(() => setIsDeleting(true), 2000);
      return () => clearTimeout(timeout);
    }

    if (isDeleting && charIndex > 0) {
      const timeout = setTimeout(() => setCharIndex((c) => c - 1), 50);
      return () => clearTimeout(timeout);
    }

    if (isDeleting && charIndex === 0) {
      setIsDeleting(false);
      setPhraseIndex((i) => i + 1);
    }
  }, [charIndex, isDeleting, phraseIndex, prefersReducedMotion]);

  // Reduced motion: cycle phrases without typing
  useEffect(() => {
    if (!prefersReducedMotion) return;
    const interval = setInterval(() => {
      setPhraseIndex((i) => (i + 1) % PHRASES.length);
    }, 3000);
    return () => clearInterval(interval);
  }, [prefersReducedMotion]);

  // Carousel auto-rotate
  useEffect(() => {
    if (isCarouselPaused || prefersReducedMotion) return;
    const interval = setInterval(() => {
      setQuoteIndex((i) => (i + 1) % QUOTES.length);
    }, 5000);
    return () => clearInterval(interval);
  }, [isCarouselPaused, prefersReducedMotion]);

  const displayText = PHRASES[phraseIndex].slice(0, charIndex);

  return (
    <div className="flex flex-col items-center">
      {/* Section 1: Hero */}
      <section
        className="w-full py-20 md:py-32 text-center"
        aria-label="서비스 소개"
      >
        <div className="max-w-4xl mx-auto px-6">
          <p className="text-lg text-primary-600 dark:text-primary-400 font-medium mb-4">
            AI 글쓰기 플랫폼
          </p>
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-gray-100 mb-6 min-h-[4rem] md:min-h-[5rem]">
            <span aria-live="polite" aria-atomic="true">
              {displayText}
            </span>
            <span
              className="animate-blink text-accent-400"
              aria-hidden="true"
            >
              |
            </span>
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 leading-relaxed mb-10 max-w-2xl mx-auto">
            시각 장애인을 위한 AI 글쓰기 플랫폼.
            <br />
            음성으로 이야기하면, AI가 아름다운 글로 완성합니다.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/signup"
              className="
                inline-flex items-center justify-center
                bg-primary-500 text-white
                px-8 py-4 rounded-xl
                text-xl font-bold
                hover:bg-primary-600
                focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-600
                no-underline min-h-touch
                shadow-lg hover:shadow-xl
                transition-all duration-200
              "
              aria-label="시작하기 - 회원가입 페이지로 이동"
            >
              시작하기
            </Link>
            <Link
              href="/login"
              className="
                inline-flex items-center justify-center
                border-2 border-gray-300 dark:border-gray-600
                text-gray-700 dark:text-gray-300
                px-8 py-4 rounded-xl
                text-xl font-bold
                hover:border-primary-400 hover:text-primary-700
                dark:hover:text-primary-400
                no-underline min-h-touch
                transition-all duration-200
              "
              aria-label="로그인 페이지로 이동"
            >
              로그인
            </Link>
          </div>
        </div>
      </section>

      {/* Section 2: Quotes Carousel */}
      <section
        className="w-full py-16 bg-gray-50 dark:bg-gray-800/50"
        aria-label="작품 샘플"
      >
        <div className="max-w-3xl mx-auto px-6">
          <div
            className="
              relative bg-white dark:bg-gray-800
              rounded-2xl shadow-lg
              p-8 md:p-12
              border border-gray-200 dark:border-gray-700
            "
            onMouseEnter={() => setIsCarouselPaused(true)}
            onMouseLeave={() => setIsCarouselPaused(false)}
            role="region"
            aria-roledescription="carousel"
            aria-label="작품 샘플 캐러셀"
          >
            <span
              className="absolute top-4 left-6 text-6xl text-accent-200 dark:text-accent-800 font-serif leading-none select-none"
              aria-hidden="true"
            >
              &ldquo;
            </span>
            <div
              className="min-h-[120px] flex items-center justify-center"
              aria-live="polite"
            >
              <blockquote className="text-center">
                <p className="text-xl md:text-2xl text-gray-800 dark:text-gray-200 leading-relaxed whitespace-pre-line font-medium">
                  {QUOTES[quoteIndex].text}
                </p>
                <footer className="mt-6 text-base text-accent-600 dark:text-accent-400">
                  &mdash; {QUOTES[quoteIndex].author}
                </footer>
              </blockquote>
            </div>
            <span
              className="absolute bottom-12 right-6 text-6xl text-accent-200 dark:text-accent-800 font-serif leading-none rotate-180 select-none"
              aria-hidden="true"
            >
              &ldquo;
            </span>

            {/* Carousel Nav */}
            <div className="flex items-center justify-center gap-4 mt-6">
              <button
                onClick={() =>
                  setQuoteIndex(
                    (i) => (i - 1 + QUOTES.length) % QUOTES.length,
                  )
                }
                className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                aria-label="이전 글"
              >
                <ChevronLeft className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              </button>
              <div className="flex gap-2" role="tablist" aria-label="글 선택">
                {QUOTES.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setQuoteIndex(i)}
                    className={`w-2.5 h-2.5 rounded-full transition-colors ${
                      i === quoteIndex
                        ? "bg-accent-400"
                        : "bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500"
                    }`}
                    role="tab"
                    aria-selected={i === quoteIndex}
                    aria-label={`${i + 1}번째 글`}
                  />
                ))}
              </div>
              <button
                onClick={() =>
                  setQuoteIndex((i) => (i + 1) % QUOTES.length)
                }
                className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                aria-label="다음 글"
              >
                <ChevronRight className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Section 3: How It Works */}
      <section
        className="w-full py-16 md:py-20"
        aria-label="이용 방법"
      >
        <div className="max-w-5xl mx-auto px-6">
          <h2 className="text-3xl md:text-4xl font-bold text-center text-gray-900 dark:text-gray-100 mb-12">
            이렇게 사용해요
          </h2>
          <ol className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-4">
            {STEPS.map((item, index) => (
              <li
                key={item.step}
                className="relative flex flex-col items-center text-center"
              >
                {index < STEPS.length - 1 && (
                  <div
                    className="hidden md:block absolute top-10 -right-4 z-10"
                    aria-hidden="true"
                  >
                    <ArrowRight className="w-8 h-8 text-accent-300 dark:text-accent-700" />
                  </div>
                )}
                <div className="w-20 h-20 rounded-2xl bg-accent-50 dark:bg-accent-950/50 flex items-center justify-center mb-5">
                  <item.icon
                    className="w-10 h-10 text-accent-600 dark:text-accent-400"
                    aria-hidden="true"
                  />
                </div>
                <span className="text-sm font-medium text-accent-600 dark:text-accent-400 mb-1">
                  Step {item.step}
                </span>
                <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-3">
                  {item.title}
                </h3>
                <p className="text-base text-gray-600 dark:text-gray-400 leading-relaxed max-w-xs">
                  {item.description}
                </p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {/* Section 4: Accessibility Trust */}
      <section
        className="w-full py-16 bg-gray-50 dark:bg-gray-800/50"
        aria-label="접근성 안내"
      >
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-gray-100 mb-10">
            모든 사용자를 위한 설계
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {BADGES.map((item) => (
              <div
                key={item.title}
                className="
                  flex flex-col items-center text-center
                  p-6 rounded-xl
                  bg-white dark:bg-gray-800
                  border border-gray-200 dark:border-gray-700
                  shadow-sm
                "
              >
                <div className="w-14 h-14 rounded-full bg-primary-100 dark:bg-primary-900/50 flex items-center justify-center mb-4">
                  <item.icon
                    className="w-7 h-7 text-primary-600 dark:text-primary-400"
                    aria-hidden="true"
                  />
                </div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-2">
                  {item.title}
                </h3>
                <p className="text-base text-gray-600 dark:text-gray-400 leading-relaxed">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Section 5: Final CTA */}
      <section className="w-full py-20 text-center" aria-label="시작하기">
        <div className="max-w-2xl mx-auto px-6">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            당신의 이야기를 시작하세요
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
            목소리가 글이 되고, 글이 책이 되는 경험.
          </p>
          <Link
            href="/signup"
            className="
              inline-flex items-center justify-center
              bg-primary-500 text-white
              px-10 py-4 rounded-xl
              text-xl font-bold
              hover:bg-primary-600
              focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-600
              no-underline min-h-touch
              shadow-lg hover:shadow-xl
              transition-all duration-200
            "
            aria-label="무료로 시작하기 - 회원가입 페이지로 이동"
          >
            무료로 시작하기
          </Link>
        </div>
      </section>
    </div>
  );
}
