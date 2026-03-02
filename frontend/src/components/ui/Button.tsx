"use client";

import React, { forwardRef, type ButtonHTMLAttributes, type ReactNode } from "react";

type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";
type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  /** aria-label for accessibility (required when button has no text content) */
  "aria-label"?: string;
  /** For toggle buttons */
  "aria-pressed"?: boolean;
  /** Loading state */
  isLoading?: boolean;
  /** Icon to show before text */
  leftIcon?: ReactNode;
  /** Icon to show after text */
  rightIcon?: ReactNode;
  children?: ReactNode;
}

const variantStyles: Record<ButtonVariant, string> = {
  primary:
    "bg-primary-600 text-white hover:bg-primary-700 active:bg-primary-800 dark:bg-primary-500 dark:hover:bg-primary-600",
  secondary:
    "bg-gray-200 text-gray-900 hover:bg-gray-300 active:bg-gray-400 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600",
  danger:
    "bg-red-600 text-white hover:bg-red-700 active:bg-red-800 dark:bg-red-500 dark:hover:bg-red-600",
  ghost:
    "bg-transparent text-gray-700 hover:bg-gray-100 active:bg-gray-200 dark:text-gray-300 dark:hover:bg-gray-800",
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: "px-3 py-1.5 text-sm min-h-touch min-w-touch",
  md: "px-5 py-2.5 text-base min-h-touch min-w-touch",
  lg: "px-7 py-3.5 text-lg min-h-[3.25rem] min-w-[3.25rem]",
};

/**
 * Accessible button component with variants, sizes, and loading state.
 * All buttons have minimum 44x44px touch target for accessibility.
 */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  {
    variant = "primary",
    size = "md",
    isLoading = false,
    leftIcon,
    rightIcon,
    disabled,
    children,
    className = "",
    ...props
  },
  ref
) {
  const isDisabled = disabled || isLoading;

  return (
    <button
      ref={ref}
      disabled={isDisabled}
      aria-disabled={isDisabled || undefined}
      aria-busy={isLoading || undefined}
      className={`
        inline-flex items-center justify-center gap-2
        font-semibold rounded-lg
        transition-colors duration-150
        focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-yellow-400
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variantStyles[variant]}
        ${sizeStyles[size]}
        ${className}
      `.trim()}
      {...props}
    >
      {isLoading ? (
        <>
          <span
            className="inline-block w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin"
            aria-hidden="true"
          />
          <span className="sr-only">처리 중입니다</span>
          {children}
        </>
      ) : (
        <>
          {leftIcon && <span aria-hidden="true">{leftIcon}</span>}
          {children}
          {rightIcon && <span aria-hidden="true">{rightIcon}</span>}
        </>
      )}
    </button>
  );
});
