"use client";

import { Component } from "react";
import type { ErrorInfo, ReactNode } from "react";

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
}

export class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error("[ErrorBoundary]", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          role="alert"
          aria-live="assertive"
          className="flex flex-col items-center justify-center min-h-[50vh] px-6 text-center"
        >
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            오류가 발생했습니다
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 mb-6">
            예상치 못한 문제가 발생했습니다. 새로고침해 주세요.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-primary-500 text-white rounded-xl text-lg font-medium
              hover:bg-primary-600 focus-visible:outline-none focus-visible:ring-4
              focus-visible:ring-primary-600"
            aria-label="페이지 새로고침"
          >
            새로고침
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
