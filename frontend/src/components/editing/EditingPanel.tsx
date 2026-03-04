"use client";

import { useCallback, useState } from "react";
import type { EditSuggestion } from "@/types/book";
import { Button } from "@/components/ui/Button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { useAnnouncer } from "@/hooks/useAnnouncer";

type EditingStage = "structure" | "content" | "proofread" | "final";

interface EditingPanelProps {
  suggestions: EditSuggestion[];
  activeStage: EditingStage;
  onStageChange: (stage: EditingStage) => void;
  onAcceptSuggestion: (suggestionId: string) => void;
  onRejectSuggestion: (suggestionId: string) => void;
  onAcceptAll: () => void;
  isLoading?: boolean;
  onRunAnalysis: (stage: EditingStage) => void;
  className?: string;
}

const STAGE_LABELS: Record<EditingStage, string> = {
  structure: "구조 편집",
  content: "내용 편집",
  proofread: "교정",
  final: "최종 검토",
};

const STAGE_ORDER: EditingStage[] = ["structure", "content", "proofread", "final"];

/**
 * 4-stage editing interface with suggestions list.
 * Each stage shows AI suggestions that can be accepted or rejected.
 */
export function EditingPanel({
  suggestions,
  activeStage,
  onStageChange,
  onAcceptSuggestion,
  onRejectSuggestion,
  onAcceptAll,
  isLoading = false,
  onRunAnalysis,
  className = "",
}: EditingPanelProps) {
  const { announcePolite } = useAnnouncer();
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const handleStageChange = useCallback(
    (stage: EditingStage) => {
      onStageChange(stage);
      announcePolite(`${STAGE_LABELS[stage]} 단계로 전환합니다`);
    },
    [onStageChange, announcePolite]
  );

  const handleAccept = useCallback(
    (suggestion: EditSuggestion) => {
      onAcceptSuggestion(suggestion.id);
      announcePolite("수정 사항을 적용했습니다");
    },
    [onAcceptSuggestion, announcePolite]
  );

  const handleReject = useCallback(
    (suggestion: EditSuggestion) => {
      onRejectSuggestion(suggestion.id);
      announcePolite("수정 사항을 거절했습니다");
    },
    [onRejectSuggestion, announcePolite]
  );

  const pendingSuggestions = suggestions.filter((s) => s.accepted === null);
  const acceptedCount = suggestions.filter((s) => s.accepted === true).length;
  const rejectedCount = suggestions.filter((s) => s.accepted === false).length;

  return (
    <div
      className={`flex flex-col gap-4 ${className}`}
      role="region"
      aria-label="편집 패널"
    >
      {/* Stage tabs + Panel content */}
      <Tabs value={activeStage} onValueChange={(v) => handleStageChange(v as EditingStage)}>
        <TabsList className="flex flex-wrap gap-2" aria-label="편집 단계">
          {STAGE_ORDER.map((stage) => (
            <TabsTrigger key={stage} value={stage} className="min-h-touch">
              {STAGE_LABELS[stage]}
            </TabsTrigger>
          ))}
        </TabsList>

        <TabsContent value={activeStage} className="flex flex-col gap-4">
          {/* Actions */}
          <div className="flex items-center justify-between flex-wrap gap-3">
            <Button
              variant="secondary"
              size="default"
              onClick={() => onRunAnalysis(activeStage)}
              isLoading={isLoading}
              aria-label={`${STAGE_LABELS[activeStage]} 분석 실행`}
            >
              분석 실행
            </Button>

            {pendingSuggestions.length > 0 && (
              <Button
                variant="primary"
                size="sm"
                onClick={onAcceptAll}
                aria-label="모든 수정 사항 적용"
              >
                모두 적용 ({pendingSuggestions.length}건)
              </Button>
            )}
          </div>

          {/* Summary */}
          <p
            className="text-base text-gray-600 dark:text-gray-400"
            aria-live="polite"
          >
            총 {suggestions.length}건의 제안 | 적용: {acceptedCount}건 | 거절:{" "}
            {rejectedCount}건 | 대기: {pendingSuggestions.length}건
          </p>

          {/* Suggestions list */}
          {suggestions.length === 0 ? (
            <p className="text-base text-gray-500 dark:text-gray-400 p-6 text-center">
              분석 실행 버튼을 눌러 AI 편집 제안을 받아보세요.
            </p>
          ) : (
            <ul className="flex flex-col gap-3" aria-label="편집 제안 목록">
              {suggestions.map((suggestion, index) => (
                <li
                  key={suggestion.id}
                  className={`
                    p-4 rounded-xl border-2
                    ${
                      suggestion.accepted === true
                        ? "border-green-300 dark:border-green-700 bg-green-50 dark:bg-green-900/20"
                        : suggestion.accepted === false
                          ? "border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/20 opacity-60"
                          : "border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800"
                    }
                  `}
                >
                  {/* Suggestion header */}
                  <div className="flex items-start justify-between gap-3">
                    <button
                      onClick={() =>
                        setExpandedId(
                          expandedId === suggestion.id ? null : suggestion.id
                        )
                      }
                      aria-expanded={expandedId === suggestion.id}
                      aria-label={`제안 ${index + 1}: ${suggestion.explanation}. 자세히 보기`}
                      className="
                        flex-1 text-left
                        focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-yellow-400
                        rounded-lg p-1
                      "
                    >
                      <span className="flex items-center gap-2 mb-1">
                        {suggestion.type === "grammar" && (
                          <Badge variant="default" className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 border-transparent">문법</Badge>
                        )}
                        {suggestion.type === "style" && (
                          <Badge variant="secondary">문체</Badge>
                        )}
                        {suggestion.type === "structure" && (
                          <Badge variant="outline">구조</Badge>
                        )}
                        {suggestion.type === "content" && (
                          <Badge variant="default" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 border-transparent">내용</Badge>
                        )}
                        {suggestion.accepted === true && (
                          <Badge variant="default" className="bg-green-100 text-green-800 border-transparent">적용됨</Badge>
                        )}
                        {suggestion.accepted === false && (
                          <Badge variant="destructive">거절됨</Badge>
                        )}
                      </span>
                      <p className="text-base text-gray-900 dark:text-gray-100">
                        {suggestion.explanation}
                      </p>
                    </button>
                  </div>

                  {/* Expanded details */}
                  {expandedId === suggestion.id && (
                    <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                            원본:
                          </p>
                          <p className="text-base text-red-700 dark:text-red-300 bg-red-50 dark:bg-red-900/30 p-3 rounded-lg line-through">
                            {suggestion.original}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                            수정:
                          </p>
                          <p className="text-base text-green-700 dark:text-green-300 bg-green-50 dark:bg-green-900/30 p-3 rounded-lg">
                            {suggestion.suggested}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Action buttons */}
                  {suggestion.accepted === null && (
                    <div className="flex gap-2 mt-3">
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => handleAccept(suggestion)}
                        aria-label={`제안 ${index + 1} 적용: ${suggestion.explanation}`}
                      >
                        적용
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleReject(suggestion)}
                        aria-label={`제안 ${index + 1} 거절: ${suggestion.explanation}`}
                      >
                        거절
                      </Button>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
