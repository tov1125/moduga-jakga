"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import { EditingPanel } from "@/components/editing/EditingPanel";
import { QualityReport } from "@/components/editing/QualityReport";
import { VoicePlayer } from "@/components/voice/VoicePlayer";
import { Button } from "@/components/ui/Button";
import { useAnnouncer } from "@/hooks/useAnnouncer";
import { useEditHistory } from "@/hooks/useEditHistory";
import {
  books as booksApi,
  chapters as chaptersApi,
  editing as editingApi,
} from "@/lib/api";
import type {
  Book,
  Chapter,
  EditSuggestion,
  QualityReport as QualityReportType,
} from "@/types/book";
import Link from "next/link";

type EditingStage = "structure" | "content" | "proofread" | "final";

/**
 * Apply a single suggestion to the chapter text.
 * Returns the updated text, or null if no change was made.
 */
function applySuggestion(
  text: string,
  suggestion: EditSuggestion
): string | null {
  // Structure suggestions are advisory — no text replacement
  if (suggestion.type === "structure") return null;

  // Position-based replacement (proofread/final with valid positions)
  if (suggestion.position.start > 0 || suggestion.position.end > 0) {
    const { start, end } = suggestion.position;
    if (start >= 0 && end > start && end <= text.length) {
      return text.slice(0, start) + suggestion.suggested + text.slice(end);
    }
  }

  // String-search replacement (style/content with original text)
  if (suggestion.original && text.includes(suggestion.original)) {
    return text.replace(suggestion.original, suggestion.suggested);
  }

  return null;
}

/**
 * Editing page with 4-stage editing interface.
 */
export default function EditingPage() {
  const params = useParams();
  const bookId = params.bookId as string;
  const { announcePolite, announceAssertive } = useAnnouncer();

  const [book, setBook] = useState<Book | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [activeChapter, setActiveChapter] = useState<Chapter | null>(null);
  const [suggestions, setSuggestions] = useState<EditSuggestion[]>([]);
  const [activeStage, setActiveStage] = useState<EditingStage>("structure");
  const [report, setReport] = useState<QualityReportType | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLoadingReport, setIsLoadingReport] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const { push: pushHistory, undo, redo, canUndo, canRedo } = useEditHistory();

  /** Debounced save — 500ms delay to avoid request storms on rapid accepts */
  const debouncedSave = useCallback(
    (chapterId: string, content: string) => {
      if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
      saveTimerRef.current = setTimeout(async () => {
        setIsSaving(true);
        try {
          await chaptersApi.update(bookId, chapterId, { content });
          announcePolite("저장되었습니다");
        } catch {
          announceAssertive("저장에 실패했습니다. 다시 시도해주세요.");
        } finally {
          setIsSaving(false);
        }
      }, 500);
    },
    [bookId, announcePolite, announceAssertive]
  );

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    };
  }, []);

  // Load book data
  useEffect(() => {
    async function load() {
      try {
        const [bookRes, chaptersRes] = await Promise.all([
          booksApi.get(bookId),
          chaptersApi.list(bookId),
        ]);
        setBook(bookRes.data);
        const chapterList = chaptersRes.data.chapters;
        setChapters(chapterList);
        if (chapterList.length > 0) {
          setActiveChapter(chapterList[0]);
        }
      } catch {
        announceAssertive("편집 데이터를 불러올 수 없습니다");
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, [bookId, announceAssertive]);

  // Run analysis for current stage
  const handleRunAnalysis = useCallback(
    async (stage: EditingStage) => {
      if (!activeChapter) return;
      setIsAnalyzing(true);
      setSuggestions([]);
      announcePolite("분석을 진행하고 있습니다. 잠시 기다려 주세요.");

      try {
        let mapped: EditSuggestion[] = [];
        switch (stage) {
          case "structure": {
            const structRes = await editingApi.structureReview(
              bookId,
              chapters.map((c) => c.content)
            );
            mapped = structRes.data.suggestions.map((s, i) => ({
              id: `struct-${i}`,
              type: "structure" as const,
              original: "",
              suggested: s,
              explanation: structRes.data.feedback[i] || "",
              position: { start: 0, end: 0 },
              accepted: null,
            }));
            break;
          }
          case "content": {
            const styleRes = await editingApi.styleCheck(activeChapter.content);
            mapped = styleRes.data.issues.map((issue, i) => ({
              id: `style-${i}`,
              type: "style" as const,
              original: issue.text_excerpt,
              suggested: issue.suggestion,
              explanation: issue.issue,
              position: { start: 0, end: 0 },
              accepted: null,
            }));
            break;
          }
          case "proofread":
          case "final": {
            const proofRes = await editingApi.proofread(activeChapter.content);
            mapped = proofRes.data.corrections.map((c, i) => ({
              id: `proof-${i}`,
              type: "grammar" as const,
              original: c.original,
              suggested: c.corrected,
              explanation: c.reason,
              position: { start: c.position_start, end: c.position_end },
              accepted: null,
            }));
            break;
          }
        }
        setSuggestions(mapped);
        announcePolite(`${mapped.length}개의 제안이 있습니다`);
      } catch {
        announceAssertive("분석에 실패했습니다");
      } finally {
        setIsAnalyzing(false);
      }
    },
    [bookId, activeChapter, chapters, announcePolite, announceAssertive]
  );

  // Undo handler
  const handleUndo = useCallback(() => {
    if (!activeChapter) return;
    const prev = undo();
    if (prev !== null) {
      const newChapter = { ...activeChapter, content: prev };
      setActiveChapter(newChapter);
      setChapters((cs) =>
        cs.map((c) => (c.id === newChapter.id ? newChapter : c))
      );
      debouncedSave(activeChapter.id, prev);
      announcePolite("되돌리기 완료");
    }
  }, [activeChapter, undo, debouncedSave, announcePolite]);

  // Redo handler
  const handleRedo = useCallback(() => {
    if (!activeChapter) return;
    const next = redo();
    if (next !== null) {
      const newChapter = { ...activeChapter, content: next };
      setActiveChapter(newChapter);
      setChapters((cs) =>
        cs.map((c) => (c.id === newChapter.id ? newChapter : c))
      );
      debouncedSave(activeChapter.id, next);
      announcePolite("다시 실행 완료");
    }
  }, [activeChapter, redo, debouncedSave, announcePolite]);

  // Keyboard shortcuts: Ctrl+Z / Ctrl+Shift+Z
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      const mod = e.metaKey || e.ctrlKey;
      if (mod && e.key === "z" && !e.shiftKey) {
        e.preventDefault();
        handleUndo();
      } else if (mod && e.key === "z" && e.shiftKey) {
        e.preventDefault();
        handleRedo();
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleUndo, handleRedo]);

  // Accept suggestion — apply text change + save
  const handleAcceptSuggestion = useCallback(
    (suggestionId: string) => {
      if (!activeChapter) return;

      const suggestion = suggestions.find((s) => s.id === suggestionId);
      if (!suggestion) return;

      // Save current content to history before applying
      pushHistory(activeChapter.content);

      const updated = applySuggestion(activeChapter.content, suggestion);

      if (updated !== null) {
        // Update local chapter content
        const newChapter = { ...activeChapter, content: updated };
        setActiveChapter(newChapter);
        setChapters((prev) =>
          prev.map((c) => (c.id === newChapter.id ? newChapter : c))
        );

        // Adjust positions for remaining suggestions (shift by length delta)
        const delta =
          suggestion.suggested.length -
          (suggestion.position.end - suggestion.position.start ||
            suggestion.original.length);
        setSuggestions((prev) =>
          prev.map((s) => {
            if (s.id === suggestionId) return { ...s, accepted: true };
            if (
              s.accepted === null &&
              s.position.start > suggestion.position.start &&
              s.position.end > 0
            ) {
              return {
                ...s,
                position: {
                  start: s.position.start + delta,
                  end: s.position.end + delta,
                },
              };
            }
            return s;
          })
        );

        // Save to backend
        debouncedSave(activeChapter.id, updated);
        announcePolite("수정이 적용되었습니다");
      } else {
        // Structure suggestions or no-match — mark as accepted without text change
        setSuggestions((prev) =>
          prev.map((s) =>
            s.id === suggestionId ? { ...s, accepted: true } : s
          )
        );
        if (suggestion.type === "structure") {
          announcePolite("구조 제안을 확인했습니다");
        }
      }
    },
    [activeChapter, suggestions, debouncedSave, announcePolite, pushHistory]
  );

  // Reject suggestion
  const handleRejectSuggestion = useCallback((suggestionId: string) => {
    setSuggestions((prev) =>
      prev.map((s) => (s.id === suggestionId ? { ...s, accepted: false } : s))
    );
  }, []);

  // Accept all — apply in reverse position order to avoid offset shifts
  const handleAcceptAll = useCallback(() => {
    if (!activeChapter) return;

    // Save current content to history before applying all
    pushHistory(activeChapter.content);

    const pending = suggestions.filter(
      (s) => s.accepted === null && s.type !== "structure"
    );

    if (pending.length === 0) {
      // Only structure suggestions remain — mark all accepted
      setSuggestions((prev) =>
        prev.map((s) => (s.accepted === null ? { ...s, accepted: true } : s))
      );
      announcePolite("모든 구조 제안을 확인했습니다");
      return;
    }

    // Sort by position descending (apply from end to start)
    const sorted = [...pending].sort(
      (a, b) => b.position.start - a.position.start
    );

    let content = activeChapter.content;
    let appliedCount = 0;

    for (const s of sorted) {
      if (s.position.start > 0 || s.position.end > 0) {
        const { start, end } = s.position;
        if (start >= 0 && end > start && end <= content.length) {
          content = content.slice(0, start) + s.suggested + content.slice(end);
          appliedCount++;
        }
      } else if (s.original && content.includes(s.original)) {
        content = content.replace(s.original, s.suggested);
        appliedCount++;
      }
    }

    // Update local state
    const newChapter = { ...activeChapter, content };
    setActiveChapter(newChapter);
    setChapters((prev) =>
      prev.map((c) => (c.id === newChapter.id ? newChapter : c))
    );

    // Mark all as accepted
    setSuggestions((prev) =>
      prev.map((s) => (s.accepted === null ? { ...s, accepted: true } : s))
    );

    // Save to backend
    if (appliedCount > 0) {
      debouncedSave(activeChapter.id, content);
    }

    announcePolite(`${appliedCount}개 수정이 모두 적용되었습니다`);
  }, [activeChapter, suggestions, debouncedSave, announcePolite, pushHistory]);

  // Load quality report
  const handleLoadReport = useCallback(async () => {
    setIsLoadingReport(true);
    try {
      const response = await editingApi.report(bookId);
      setReport(response.data);
      announcePolite("품질 보고서가 준비되었습니다");
    } catch {
      announceAssertive("품질 보고서를 불러올 수 없습니다");
    } finally {
      setIsLoadingReport(false);
    }
  }, [bookId, activeChapter, announcePolite, announceAssertive]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20" role="status" aria-live="polite">
        <p className="text-xl text-gray-500 dark:text-gray-400">불러오는 중...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
          {book?.title} - 편집
        </h1>
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleUndo}
            disabled={!canUndo}
            aria-label="되돌리기 (Ctrl+Z)"
          >
            되돌리기
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRedo}
            disabled={!canRedo}
            aria-label="다시 실행 (Ctrl+Shift+Z)"
          >
            다시 실행
          </Button>
          {isSaving && (
            <span className="text-sm text-gray-500 dark:text-gray-400" role="status">
              저장 중...
            </span>
          )}
          <Link
            href={`/write/${bookId}`}
            className="
              inline-flex items-center
              text-primary-700 dark:text-primary-400
              font-medium no-underline
              hover:underline
              focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-600
              rounded-lg px-3 py-2 min-h-touch
            "
            aria-label="글쓰기로 돌아가기"
          >
            글쓰기로 돌아가기
          </Link>
        </div>
      </div>

      {/* Chapter selector */}
      {chapters.length > 1 && (
        <div className="flex items-center gap-3 flex-wrap">
          <label
            htmlFor="edit-chapter-select"
            className="text-base font-medium text-gray-900 dark:text-gray-100"
          >
            챕터 선택:
          </label>
          <select
            id="edit-chapter-select"
            value={activeChapter?.id || ""}
            onChange={(e) => {
              const chapter = chapters.find((c) => c.id === e.target.value);
              if (chapter) {
                setActiveChapter(chapter);
                setSuggestions([]);
                setReport(null);
              }
            }}
            className="
              px-4 py-2 min-h-touch
              text-base text-gray-900 dark:text-gray-100
              bg-white dark:bg-gray-800
              border-2 border-gray-300 dark:border-gray-600
              rounded-xl
              focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-600
            "
          >
            {chapters.map((chapter) => (
              <option key={chapter.id} value={chapter.id}>
                {chapter.order}장: {chapter.title}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Editing panel */}
      <EditingPanel
        suggestions={suggestions}
        activeStage={activeStage}
        onStageChange={(stage) => {
          setActiveStage(stage);
          setSuggestions([]);
        }}
        onAcceptSuggestion={handleAcceptSuggestion}
        onRejectSuggestion={handleRejectSuggestion}
        onAcceptAll={handleAcceptAll}
        isLoading={isAnalyzing}
        onRunAnalysis={handleRunAnalysis}
      />

      {/* TTS for reading suggestions */}
      {suggestions.length > 0 && (
        <section aria-label="수정 사항 낭독">
          <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-3">
            수정 사항 듣기
          </h2>
          <VoicePlayer
            text={suggestions
              .filter((s) => s.accepted === null)
              .map(
                (s) =>
                  `${s.explanation}. 원본: ${s.original}. 수정안: ${s.suggested}.`
              )
              .join(" ")}
          />
        </section>
      )}

      {/* Quality report */}
      <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            품질 보고서
          </h2>
          <Button
            variant="secondary"
            size="default"
            onClick={handleLoadReport}
            isLoading={isLoadingReport}
            aria-label="품질 보고서 생성"
          >
            보고서 생성
          </Button>
        </div>
        {report && <QualityReport report={report} />}
      </div>

      {/* Next step */}
      <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
        <Link
          href={`/write/${bookId}/review`}
          className="
            inline-flex items-center justify-center
            bg-primary-400 text-gray-900
            px-6 py-3 rounded-xl
            text-base font-semibold
            no-underline
            hover:bg-primary-500
            focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-600
            min-h-touch
          "
          aria-label="검토 단계로 이동"
        >
          검토하기
        </Link>
      </div>
    </div>
  );
}
