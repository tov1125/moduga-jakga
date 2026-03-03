"use client";

import type { QualityReport as QualityReportType } from "@/types/book";

interface QualityReportProps {
  report: QualityReportType;
  className?: string;
}

const STAGE_LABELS: Record<string, string> = {
  structure: "구조 편집",
  content: "내용 편집",
  proofread: "교정/교열",
  final: "최종 검토",
};

/**
 * Quality report display component.
 * Shows overall score, stage results, summary, and recommendations.
 */
export function QualityReport({ report, className = "" }: QualityReportProps) {
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

      {/* Overall score */}
      <div
        className={`p-4 rounded-xl text-center ${
          report.overall_score >= 80
            ? "bg-green-100 dark:bg-green-900/30"
            : report.overall_score >= 60
              ? "bg-yellow-100 dark:bg-yellow-900/30"
              : "bg-red-100 dark:bg-red-900/30"
        }`}
        role="status"
        aria-label={`종합 점수: 100점 만점에 ${report.overall_score}점`}
      >
        <span className={`text-3xl font-bold ${getScoreColor(report.overall_score)}`}>
          {report.overall_score}점
        </span>
        <p className="text-base text-gray-600 dark:text-gray-400 mt-1">
          종합 품질 점수 (발견 문제: {report.total_issues}건)
        </p>
      </div>

      {/* Stage results */}
      {report.stage_results.length > 0 && (
        <div className="flex flex-col gap-4" aria-label="단계별 점수">
          {report.stage_results.map((stage) => (
            <div key={stage.stage} className="flex flex-col gap-1">
              <div className="flex items-center justify-between">
                <span className="text-base font-medium text-gray-700 dark:text-gray-300">
                  {STAGE_LABELS[stage.stage] || stage.stage}
                  <span className="text-sm text-gray-500 ml-2">
                    ({stage.issues_count}건)
                  </span>
                </span>
                <span
                  className={`text-lg font-bold ${getScoreColor(stage.score)}`}
                  aria-label={`${STAGE_LABELS[stage.stage]}: 100점 만점에 ${stage.score}점`}
                >
                  {stage.score}점
                </span>
              </div>
              <div
                className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden"
                aria-hidden="true"
              >
                <div
                  className={`h-full rounded-full transition-all duration-500 ${getBarColor(stage.score)}`}
                  style={{ width: `${stage.score}%` }}
                />
              </div>
              {stage.feedback && (
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  {stage.feedback}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Summary */}
      {report.summary && (
        <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-xl">
          <h4 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-2">
            종합 평가
          </h4>
          <p className="text-base text-gray-700 dark:text-gray-300">
            {report.summary}
          </p>
        </div>
      )}

      {/* Recommendations */}
      {report.recommendations.length > 0 && (
        <div>
          <h4 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-3">
            권장 사항 ({report.recommendations.length}건)
          </h4>
          <ul className="flex flex-col gap-2" aria-label="권장 사항 목록">
            {report.recommendations.map((rec, index) => (
              <li
                key={index}
                className="flex items-start gap-3 p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20"
              >
                <span className="inline-block px-2 py-0.5 rounded text-sm font-medium shrink-0 bg-blue-200 text-blue-800 dark:bg-blue-800 dark:text-blue-200">
                  권장
                </span>
                <p className="text-base text-gray-900 dark:text-gray-100">
                  {rec}
                </p>
              </li>
            ))}
          </ul>
        </div>
      )}

      {report.recommendations.length === 0 && report.total_issues === 0 && (
        <p className="text-base text-gray-600 dark:text-gray-400 text-center p-4">
          발견된 문제가 없습니다.
        </p>
      )}
    </div>
  );
}
