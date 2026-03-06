"use client";

import { useCallback, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Checkbox } from "@/components/ui/checkbox";
import { useAnnouncer } from "@/hooks/useAnnouncer";
import { auth } from "@/lib/api";
import type { DisabilityType } from "@/types/user";

const DISABILITY_OPTIONS: { value: DisabilityType; label: string }[] = [
  { value: "visual", label: "시각장애" },
  { value: "low_vision", label: "저시력" },
  { value: "other", label: "기타 시각 장애" },
  { value: "none", label: "해당 없음" },
];

/**
 * Signup page with accessible form.
 */
export default function SignupPage() {
  const router = useRouter();
  const { announceAssertive, announcePolite } = useAnnouncer();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [disabilityType, setDisabilityType] = useState<DisabilityType>("none");
  const [agreeTerms, setAgreeTerms] = useState(false);
  const [agreePrivacy, setAgreePrivacy] = useState(false);
  const [agreeCopyright, setAgreeCopyright] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  const allAgreed = agreeTerms && agreePrivacy && agreeCopyright;

  const validate = useCallback((): boolean => {
    const errors: Record<string, string> = {};

    if (!email) errors.email = "이메일을 입력해 주세요.";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
      errors.email = "올바른 이메일 형식이 아닙니다.";

    if (!password) errors.password = "비밀번호를 입력해 주세요.";
    else if (password.length < 8)
      errors.password = "비밀번호는 8자 이상이어야 합니다.";

    if (password !== passwordConfirm)
      errors.passwordConfirm = "비밀번호가 일치하지 않습니다.";

    if (!displayName) errors.displayName = "이름을 입력해 주세요.";

    setFieldErrors(errors);

    if (Object.keys(errors).length > 0) {
      const firstError = Object.values(errors)[0];
      announceAssertive(firstError);
      return false;
    }

    return true;
  }, [email, password, passwordConfirm, displayName, announceAssertive]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setError(null);

      if (!validate()) return;

      setIsLoading(true);

      try {
        await auth.signup({
          email,
          password,
          display_name: displayName,
          disability_type: disabilityType,
        });
        announcePolite(
          "회원가입이 완료되었습니다. 로그인 페이지로 이동합니다."
        );
        router.push("/login");
      } catch (err) {
        const message =
          err instanceof Error
            ? err.message
            : "회원가입에 실패했습니다. 다시 시도해 주세요.";
        setError(message);
        announceAssertive(message);
        window.scrollTo({ top: 0, behavior: "smooth" });
      } finally {
        setIsLoading(false);
      }
    },
    [
      email,
      password,
      displayName,
      disabilityType,
      validate,
      router,
      announceAssertive,
      announcePolite,
    ]
  );

  return (
    <div className="flex flex-col items-center py-12">
      <div className="w-full max-w-md">
        <h1 className="text-3xl font-bold text-center text-gray-900 dark:text-gray-100 mb-8">
          회원가입
        </h1>

        <form
          onSubmit={handleSubmit}
          noValidate
          className="flex flex-col gap-6"
          aria-label="회원가입 양식"
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
              htmlFor="signup-email"
              className="text-base font-medium text-gray-900 dark:text-gray-100"
            >
              이메일 <span aria-hidden="true">*</span>
            </label>
            <input
              id="signup-email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              aria-required="true"
              aria-invalid={!!fieldErrors.email}
              aria-describedby={
                fieldErrors.email ? "signup-email-error" : "signup-email-hint"
              }
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
            <p
              id="signup-email-hint"
              className="text-sm text-gray-500 dark:text-gray-400"
            >
              로그인에 사용할 이메일을 입력하세요.
            </p>
            {fieldErrors.email && (
              <p
                id="signup-email-error"
                className="text-sm text-red-600 dark:text-red-400 font-medium"
                role="alert"
              >
                {fieldErrors.email}
              </p>
            )}
          </div>

          {/* Display name */}
          <div className="flex flex-col gap-2">
            <label
              htmlFor="signup-name"
              className="text-base font-medium text-gray-900 dark:text-gray-100"
            >
              이름 (필명) <span aria-hidden="true">*</span>
            </label>
            <input
              id="signup-name"
              type="text"
              autoComplete="name"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              required
              aria-required="true"
              aria-invalid={!!fieldErrors.displayName}
              aria-describedby={
                fieldErrors.displayName ? "signup-name-error" : undefined
              }
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
              placeholder="작가 이름을 입력하세요"
            />
            {fieldErrors.displayName && (
              <p
                id="signup-name-error"
                className="text-sm text-red-600 dark:text-red-400 font-medium"
                role="alert"
              >
                {fieldErrors.displayName}
              </p>
            )}
          </div>

          {/* Password */}
          <div className="flex flex-col gap-2">
            <label
              htmlFor="signup-password"
              className="text-base font-medium text-gray-900 dark:text-gray-100"
            >
              비밀번호 <span aria-hidden="true">*</span>
            </label>
            <input
              id="signup-password"
              type="password"
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              aria-required="true"
              aria-invalid={!!fieldErrors.password}
              aria-describedby="signup-password-hint"
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
            <p
              id="signup-password-hint"
              className="text-sm text-gray-500 dark:text-gray-400"
            >
              8자 이상의 비밀번호를 입력하세요.
            </p>
            {fieldErrors.password && (
              <p
                className="text-sm text-red-600 dark:text-red-400 font-medium"
                role="alert"
              >
                {fieldErrors.password}
              </p>
            )}
          </div>

          {/* Password confirm */}
          <div className="flex flex-col gap-2">
            <label
              htmlFor="signup-password-confirm"
              className="text-base font-medium text-gray-900 dark:text-gray-100"
            >
              비밀번호 확인 <span aria-hidden="true">*</span>
            </label>
            <input
              id="signup-password-confirm"
              type="password"
              autoComplete="new-password"
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              required
              aria-required="true"
              aria-invalid={!!fieldErrors.passwordConfirm}
              aria-describedby={
                fieldErrors.passwordConfirm
                  ? "signup-password-confirm-error"
                  : undefined
              }
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
              placeholder="비밀번호를 다시 입력하세요"
            />
            {fieldErrors.passwordConfirm && (
              <p
                id="signup-password-confirm-error"
                className="text-sm text-red-600 dark:text-red-400 font-medium"
                role="alert"
              >
                {fieldErrors.passwordConfirm}
              </p>
            )}
          </div>

          {/* Disability type */}
          <div className="flex flex-col gap-2">
            <label
              htmlFor="signup-disability"
              className="text-base font-medium text-gray-900 dark:text-gray-100"
            >
              시각 장애 유형
            </label>
            <select
              id="signup-disability"
              value={disabilityType}
              onChange={(e) =>
                setDisabilityType(e.target.value as DisabilityType)
              }
              aria-describedby="signup-disability-hint"
              className="
                w-full px-4 py-3 min-h-touch
                text-lg text-gray-900 dark:text-gray-100
                bg-white dark:bg-gray-800
                border-2 border-gray-300 dark:border-gray-600
                rounded-xl
                focus:border-primary-500 dark:focus:border-primary-400
                focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-600
              "
            >
              {DISABILITY_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <p
              id="signup-disability-hint"
              className="text-sm text-gray-500 dark:text-gray-400"
            >
              서비스 최적화를 위해 선택해 주세요. 언제든 설정에서 변경할 수
              있습니다.
            </p>
          </div>

          {/* Consent checkboxes */}
          <fieldset className="flex flex-col gap-4">
            <legend className="text-base font-medium text-gray-900 dark:text-gray-100 mb-2">
              약관 동의 <span aria-hidden="true">*</span>
            </legend>

            <div className="flex items-start gap-3">
              <Checkbox
                id="agree-terms"
                checked={agreeTerms}
                onCheckedChange={(checked) => setAgreeTerms(checked === true)}
                aria-required="true"
              />
              <label
                htmlFor="agree-terms"
                className="text-base text-gray-700 dark:text-gray-300 leading-snug"
              >
                <Link
                  href="/terms"
                  target="_blank"
                  className="text-primary-700 dark:text-primary-400 underline"
                >
                  이용약관
                </Link>
                에 동의합니다 (필수)
              </label>
            </div>

            <div className="flex items-start gap-3">
              <Checkbox
                id="agree-privacy"
                checked={agreePrivacy}
                onCheckedChange={(checked) => setAgreePrivacy(checked === true)}
                aria-required="true"
              />
              <label
                htmlFor="agree-privacy"
                className="text-base text-gray-700 dark:text-gray-300 leading-snug"
              >
                <Link
                  href="/privacy"
                  target="_blank"
                  className="text-primary-700 dark:text-primary-400 underline"
                >
                  개인정보처리방침
                </Link>
                에 동의합니다 (필수)
              </label>
            </div>

            <div className="flex items-start gap-3">
              <Checkbox
                id="agree-copyright"
                checked={agreeCopyright}
                onCheckedChange={(checked) =>
                  setAgreeCopyright(checked === true)
                }
                aria-required="true"
              />
              <label
                htmlFor="agree-copyright"
                className="text-base text-gray-700 dark:text-gray-300 leading-snug"
              >
                AI 생성 글의 저작권 정책에 동의합니다 (필수)
              </label>
            </div>
          </fieldset>

          {/* Submit */}
          <Button
            type="submit"
            variant="primary"
            size="lg"
            isLoading={isLoading}
            disabled={!allAgreed}
            aria-label="회원가입"
            aria-disabled={!allAgreed}
            className="w-full"
          >
            회원가입
          </Button>

          {/* Login link */}
          <p className="text-center text-base text-gray-600 dark:text-gray-400">
            이미 계정이 있으신가요?{" "}
            <Link
              href="/login"
              className="text-primary-700 dark:text-primary-400 font-medium"
            >
              로그인
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
