"use client";

import { useCallback, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { useAnnouncer } from "@/hooks/useAnnouncer";
import { useSupabase } from "@/hooks/useSupabase";
import { auth } from "@/lib/api";

/**
 * Login page with accessible form.
 */
export default function LoginPage() {
  const router = useRouter();
  const { announceAssertive, announcePolite } = useAnnouncer();
  const { refreshUser } = useSupabase();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setError(null);
      setIsLoading(true);

      if (!email || !password) {
        setError("이메일과 비밀번호를 모두 입력해 주세요.");
        announceAssertive("이메일과 비밀번호를 모두 입력해 주세요.");
        setIsLoading(false);
        return;
      }

      try {
        const response = await auth.login({ email, password });
        if (response.data.access_token) {
          localStorage.setItem("access_token", response.data.access_token);
        }
        await refreshUser();
        announcePolite("로그인되었습니다. 대시보드로 이동합니다.");
        router.push("/dashboard");
      } catch (err) {
        const message =
          err instanceof Error
            ? err.message
            : "로그인에 실패했습니다. 이메일과 비밀번호를 확인해 주세요.";
        setError(message);
        announceAssertive(message);
      } finally {
        setIsLoading(false);
      }
    },
    [email, password, router, announceAssertive, announcePolite, refreshUser]
  );

  return (
    <div className="flex flex-col items-center py-12">
      <div className="w-full max-w-md">
        <h1 className="text-3xl font-bold text-center text-gray-900 dark:text-gray-100 mb-8">
          로그인
        </h1>

        <form
          onSubmit={handleSubmit}
          noValidate
          className="flex flex-col gap-6"
          aria-label="로그인 양식"
        >
          {/* Error message */}
          {error && (
            <div
              className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl"
              role="alert"
              aria-live="assertive"
            >
              <p className="text-red-700 dark:text-red-300 text-base font-medium">
                {error}
              </p>
            </div>
          )}

          {/* Email */}
          <div className="flex flex-col gap-2">
            <label
              htmlFor="login-email"
              className="text-base font-medium text-gray-900 dark:text-gray-100"
            >
              이메일
            </label>
            <input
              id="login-email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              aria-required="true"
              aria-describedby={error ? "login-error" : undefined}
              className="
                w-full px-4 py-3 min-h-touch
                text-lg text-gray-900 dark:text-gray-100
                bg-white dark:bg-gray-800
                border-2 border-gray-300 dark:border-gray-600
                rounded-xl
                focus:border-primary-500 dark:focus:border-primary-400
                focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-600
                placeholder:text-gray-400
              "
              placeholder="example@email.com"
            />
          </div>

          {/* Password */}
          <div className="flex flex-col gap-2">
            <label
              htmlFor="login-password"
              className="text-base font-medium text-gray-900 dark:text-gray-100"
            >
              비밀번호
            </label>
            <input
              id="login-password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              aria-required="true"
              className="
                w-full px-4 py-3 min-h-touch
                text-lg text-gray-900 dark:text-gray-100
                bg-white dark:bg-gray-800
                border-2 border-gray-300 dark:border-gray-600
                rounded-xl
                focus:border-primary-500 dark:focus:border-primary-400
                focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-600
                placeholder:text-gray-400
              "
              placeholder="비밀번호를 입력하세요"
            />
          </div>

          {/* Submit button */}
          <Button
            type="submit"
            variant="primary"
            size="lg"
            isLoading={isLoading}
            aria-label="로그인"
            className="w-full"
          >
            로그인
          </Button>

          {/* Sign up link */}
          <p className="text-center text-base text-gray-600 dark:text-gray-400">
            아직 계정이 없으신가요?{" "}
            <Link
              href="/signup"
              className="text-primary-700 dark:text-primary-400 font-medium"
            >
              회원가입
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
