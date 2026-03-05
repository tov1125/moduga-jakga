"use client";

import Link from "next/link";
import { useSupabase } from "@/hooks/useSupabase";
import { Button } from "@/components/ui/Button";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { useRouter } from "next/navigation";
import { useCallback } from "react";

/**
 * App header with logo, navigation links, and user menu.
 * Fully keyboard navigable.
 */
export function Header() {
  const { user, signOut, isLoading } = useSupabase();
  const router = useRouter();

  const handleSignOut = useCallback(async () => {
    await signOut();
    router.push("/");
  }, [signOut, router]);

  return (
    <header
      className="
        w-full border-b border-gray-200 dark:border-gray-700
        bg-white dark:bg-gray-900
        px-6 py-4
      "
      role="banner"
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <Link
          href="/"
          className="
            text-2xl font-bold text-primary-700 dark:text-primary-400
            focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-yellow-400
            rounded-lg px-2 py-1
          "
          aria-label="모두가 작가 - 홈으로 이동"
        >
          모두가 작가
        </Link>

        {/* Theme toggle + User actions */}
        <div className="flex items-center gap-4">
          <ThemeToggle />
          {!isLoading && (
            <>
              {user ? (
                <>
                  <span
                    className="text-gray-700 dark:text-gray-300 text-base"
                    aria-label={`${user.display_name}님으로 로그인됨`}
                  >
                    {user.display_name}님
                  </span>
                  <Link
                    href="/settings"
                    className="
                      text-gray-600 dark:text-gray-400
                      hover:text-primary-600 dark:hover:text-primary-400
                      focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-yellow-400
                      rounded-lg px-3 py-2 min-h-touch min-w-touch
                      inline-flex items-center
                    "
                    aria-label="설정"
                  >
                    설정
                  </Link>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleSignOut}
                    aria-label="로그아웃"
                  >
                    로그아웃
                  </Button>
                </>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="
                      text-gray-600 dark:text-gray-400
                      hover:text-primary-600 dark:hover:text-primary-400
                      focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-yellow-400
                      rounded-lg px-3 py-2 min-h-touch min-w-touch
                      inline-flex items-center
                    "
                    aria-label="로그인"
                  >
                    로그인
                  </Link>
                  <Link
                    href="/signup"
                    className="
                      bg-primary-600 text-white px-5 py-2.5
                      rounded-lg font-semibold
                      hover:bg-primary-700
                      focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-yellow-400
                      min-h-touch inline-flex items-center
                    "
                    aria-label="회원가입"
                  >
                    회원가입
                  </Link>
                </>
              )}
            </>
          )}
        </div>
      </div>
    </header>
  );
}
