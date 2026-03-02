"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
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
  QualityReport as QualityReportType,
} from "@/types/book";
import Link from "next/link";

/**
 * Review page for final manuscript review before design/publishing.
 */
export default function ReviewPage() {
  const params = useParams();
  const router = useRouter();
  const bookId = params.bookId as string;
  const { announcePolite, announceAssertive } = useAnnouncer();

  const [book, setBook] = useState<Book | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [report, setReport] = useState<QualityReportType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isReviewing, setIsReviewing] = useState(false);
  const [isApproving, setIsApproving] = useState(false);

  // Load data
  useEffect(() => {
    async function load() {
      try {
        const [bookRes, chaptersRes] = await Promise.all([
          booksApi.get(bookId),
          chaptersApi.list(bookId),
        ]);
        setBook(bookRes.data);
        setChapters(chaptersRes.data);
      } catch {
        announceAssertive("데이터를 불러올 수 없습니다");
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, [bookId, announceAssertive]);

  // Run full review
  const handleFullReview = useCallback(async () => {
    setIsReviewing(true);
    announcePolite("전체 검토를 진행하고 있습니다. 시간이 걸릴 수 있습니다.");

    try {
      const response = await editingApi.report(bookId);
      setReport(response.data);
      announcePolite("검토가 완료되었습니다");
    } catch {
      announceAssertive("검토에 실패했습니다");
    } finally {
      setIsReviewing(false);
    }
  }, [bookId, announcePolite, announceAssertive]);

  // Approve and move to design
  const handleApprove = useCallback(async () => {
    setIsApproving(true);
    try {
      await booksApi.update(bookId, { status: "designing" });
      announcePolite("검토가 승인되었습니다. 디자인 페이지로 이동합니다.");
      router.push(`/design/${bookId}`);
    } catch {
      announceAssertive("상태 업데이트에 실패했습니다");
    } finally {
      setIsApproving(false);
    }
  }, [bookId, router, announcePolite, announceAssertive]);

  const fullText = chapters.map((c) => c.content).join("\n\n");
  const totalWords = fullText.replace(/\s/g, "").length;

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
          {book?.title} - 최종 검토
        </h1>
        <Link
          href={`/write/${bookId}/edit`}
          className="
            inline-flex items-center
            text-primary-600 dark:text-primary-400
            font-medium no-underline hover:underline
            focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-yellow-400
            rounded-lg px-3 py-2 min-h-touch
          "
          aria-label="편집으로 돌아가기"
        >
          편집으로 돌아가기
        </Link>
      </div>

      {/* Manuscript summary */}
      <section
        className="p-6 bg-gray-50 dark:bg-gray-800 rounded-xl"
        aria-label="원고 요약"
      >
        <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">
          원고 요약
        </h2>
        <dl className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <dt className="text-sm text-gray-500 dark:text-gray-400">총 챕터</dt>
            <dd className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {chapters.length}개
            </dd>
          </div>
          <div>
            <dt className="text-sm text-gray-500 dark:text-gray-400">총 글자 수</dt>
            <dd className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {totalWords.toLocaleString()}자
            </dd>
          </div>
          <div>
            <dt className="text-sm text-gray-500 dark:text-gray-400">장르</dt>
            <dd className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {book?.genre === "essay"
                ? "에세이"
                : book?.genre === "novel"
                  ? "소설"
                  : book?.genre === "poem"
                    ? "시"
                    : "자서전"}
            </dd>
          </div>
          <div>
            <dt className="text-sm text-gray-500 dark:text-gray-400">상태</dt>
            <dd className="text-2xl font-bold text-primary-600 dark:text-primary-400">
              검토 중
            </dd>
          </div>
        </dl>
      </section>

      {/* Full review */}
      <section aria-label="전체 검토">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            품질 검토
          </h2>
          <Button
            variant="secondary"
            size="md"
            onClick={handleFullReview}
            isLoading={isReviewing}
            aria-label="전체 검토 실행"
          >
            전체 검토 실행
          </Button>
        </div>

        {report ? (
          <QualityReport report={report} />
        ) : (
          <p className="text-base text-gray-500 dark:text-gray-400 text-center p-8 bg-gray-50 dark:bg-gray-800 rounded-xl">
            전체 검토 실행 버튼을 눌러 품질 보고서를 확인하세요.
          </p>
        )}
      </section>

      {/* TTS for full text */}
      {fullText && (
        <section aria-label="전체 원고 낭독">
          <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-3">
            전체 원고 듣기
          </h2>
          <VoicePlayer text={fullText} />
        </section>
      )}

      {/* Actions */}
      <div className="flex justify-between items-center pt-6 border-t border-gray-200 dark:border-gray-700">
        <Link
          href={`/write/${bookId}/edit`}
          className="
            inline-flex items-center justify-center
            bg-gray-200 dark:bg-gray-700
            text-gray-900 dark:text-gray-100
            px-6 py-3 rounded-xl
            text-base font-semibold
            no-underline
            hover:bg-gray-300 dark:hover:bg-gray-600
            focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-yellow-400
            min-h-touch
          "
          aria-label="수정 사항 요청 - 편집으로 돌아가기"
        >
          수정 요청
        </Link>
        <Button
          variant="primary"
          size="lg"
          onClick={handleApprove}
          isLoading={isApproving}
          disabled={!report || report.verdict === "major_revision"}
          aria-label="승인하고 디자인 단계로 이동"
        >
          승인 및 디자인
        </Button>
      </div>
    </div>
  );
}
