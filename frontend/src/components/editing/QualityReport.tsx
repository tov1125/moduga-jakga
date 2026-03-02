"use client";

import type { QualityReport as QualityReportType } from "@/types/book";

interface QualityReportProps {
  report: QualityReportType;
  className?: string;
}

/** Korean labels for score categories */
const SCORE_LABELS: Record<string, string> = {
  overall: "종합 점수",
  grammar: "문법",
  style: "문체",
  structure: "구조",
  readability: "가독성",
};

/** Verdict labels */
const VERDICT_LABELS: Record<string, string> = {
  pass: "통과",
  needs_revision: "수정 필요",
  major_revision: "대폭 수정 필요",
};

/** Severity labels */
const SEVERITY_LABELS: Record<string, string> = {
  info: "참고",
  warning: "주의",
  error: "오류",
};

/**
 * Quality report display component.
 * Shows scores with accessible text (not just visual bars),
 * issue list, and overall verdict.
 */
export function QualityReport({ report, className = "" }: QualityReportProps) {
  const scores = [
    { key: "overall", value: report.overallScore },
    { key: "grammar", value: report.grammarScore },
    { key: "style", value: report.styleScore },
    { key: "structure", value: report.structureScore },
    { key: "readability", value: report.readabilityScore },
  ];

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600 dark:text-green-400";
    if (score >= 60) return "text-yellow-600 dark:text-yellow-400";
    return "text-red-600 dark:text-red-400";
  };

  const getBarColor = (score: number) => {
    if (score >= 80) return "bg-green-500";
    if (score >= 60) return "bg-yellow-500";
    return "bg-red-500";
  };

  return (
    <div
      className={`flex flex-col gap-6 ${className}`}
      role="region"
      aria-label="품질 보고서"
    >
      <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">
        품질 보고서
      </h3>

      {/* Verdict */}
      <div
        className={`
          p-4 rounded-xl text-center text-lg font-bold
          ${
            report.verdict === "pass"
              ? "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200"
              : report.verdict === "needs_revision"
                ? "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200"
                : "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200"
          }
        `}
        role="status"
        aria-label={`판정 결과: ${VERDICT_LABELS[report.verdict]}`}
      >
        판정: {VERDICT_LABELS[report.verdict]}
      </div>

      {/* Scores */}
      <div className="flex flex-col gap-4" aria-label="점수 상세">
        {scores.map(({ key, value }) => (
          <div key={key} className="flex flex-col gap-1">
            <div className="flex items-center justify-between">
              <span className="text-base font-medium text-gray-700 dark:text-gray-300">
                {SCORE_LABELS[key]}
              </span>
              <span
                className={`text-lg font-bold ${getScoreColor(value)}`}
                aria-label={`${SCORE_LABELS[key]}: 100점 만점에 ${value}점`}
              >
                {value}점
              </span>
            </div>
            {/* Visual bar (decorative, score is announced textually) */}
            <div
              className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden"
              aria-hidden="true"
            >
              <div
                className={`h-full rounded-full transition-all duration-500 ${getBarColor(value)}`}
                style={{ width: `${value}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Issues list */}
      {report.issues.length > 0 && (
        <div>
          <h4 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-3">
            발견된 문제 ({report.issues.length}건)
          </h4>
          <ul className="flex flex-col gap-2" aria-label="문제 목록">
            {report.issues.map((issue, index) => (
              <li
                key={index}
                className={`
                  flex items-start gap-3 p-3 rounded-lg
                  ${
                    issue.severity === "error"
                      ? "bg-red-50 dark:bg-red-900/20"
                      : issue.severity === "warning"
                        ? "bg-yellow-50 dark:bg-yellow-900/20"
                        : "bg-blue-50 dark:bg-blue-900/20"
                  }
                `}
              >
                <span
                  className={`
                    inline-block px-2 py-0.5 rounded text-sm font-medium shrink-0
                    ${
                      issue.severity === "error"
                        ? "bg-red-200 text-red-800 dark:bg-red-800 dark:text-red-200"
                        : issue.severity === "warning"
                          ? "bg-yellow-200 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-200"
                          : "bg-blue-200 text-blue-800 dark:bg-blue-800 dark:text-blue-200"
                    }
                  `}
                  aria-label={SEVERITY_LABELS[issue.severity]}
                >
                  {SEVERITY_LABELS[issue.severity]}
                </span>
                <div className="flex-1">
                  <p className="text-base text-gray-900 dark:text-gray-100">
                    {issue.message}
                  </p>
                  {issue.location && (
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      위치: {issue.location}
                    </p>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {report.issues.length === 0 && (
        <p className="text-base text-gray-600 dark:text-gray-400 text-center p-4">
          발견된 문제가 없습니다.
        </p>
      )}
    </div>
  );
}
