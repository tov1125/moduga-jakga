"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { EditingPanel } from "@/components/editing/EditingPanel";
import { QualityReport } from "@/components/editing/QualityReport";
import { VoicePlayer } from "@/components/voice/VoicePlayer";
import { Button } from "@/components/ui/Button";
import { useAnnouncer } from "@/hooks/useAnnouncer";
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

type EditingStage = "structure" | "content" | "proofread" | "copyedit";

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

  // Load book data
  useEffect(() => {
    async function load() {
      try {
        const [bookRes, chaptersRes] = await Promise.all([
          booksApi.get(bookId),
          chaptersApi.list(bookId),
        ]);
        setBook(bookRes.data);
        setChapters(chaptersRes.data);
        if (chaptersRes.data.length > 0) {
          setActiveChapter(chaptersRes.data[0]);
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
        let response;
        switch (stage) {
          case "structure":
            response = await editingApi.structureReview(bookId, activeChapter.id);
            break;
          case "content":
            response = await editingApi.styleCheck(bookId, activeChapter.id);
            break;
          case "proofread":
          case "copyedit":
            response = await editingApi.proofread(bookId, activeChapter.id);
            break;
        }
        setSuggestions(response.data.suggestions);
        announcePolite(`${response.data.suggestions.length}개의 제안이 있습니다`);
      } catch {
        announceAssertive("분석에 실패했습니다");
      } finally {
        setIsAnalyzing(false);
      }
    },
    [bookId, activeChapter, announcePolite, announceAssertive]
  );

  // Accept suggestion
  const handleAcceptSuggestion = useCallback((suggestionId: string) => {
    setSuggestions((prev) =>
      prev.map((s) => (s.id === suggestionId ? { ...s, accepted: true } : s))
    );
  }, []);

  // Reject suggestion
  const handleRejectSuggestion = useCallback((suggestionId: string) => {
    setSuggestions((prev) =>
      prev.map((s) => (s.id === suggestionId ? { ...s, accepted: false } : s))
    );
  }, []);

  // Accept all
  const handleAcceptAll = useCallback(() => {
    setSuggestions((prev) =>
      prev.map((s) => (s.accepted === null ? { ...s, accepted: true } : s))
    );
    announcePolite("모든 수정 사항이 적용되었습니다");
  }, [announcePolite]);

  // Load quality report
  const handleLoadReport = useCallback(async () => {
    setIsLoadingReport(true);
    try {
      const response = await editingApi.report(
        bookId,
        activeChapter?.id
      );
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
          <Link
            href={`/write/${bookId}`}
            className="
              inline-flex items-center
              text-primary-600 dark:text-primary-400
              font-medium no-underline
              hover:underline
              focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-yellow-400
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
              focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-yellow-400
            "
          >
            {chapters.map((chapter) => (
              <option key={chapter.id} value={chapter.id}>
                {chapter.chapterNumber}장: {chapter.title}
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
            size="md"
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
            bg-primary-600 text-white
            px-6 py-3 rounded-xl
            text-base font-semibold
            no-underline
            hover:bg-primary-700
            focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-yellow-400
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
