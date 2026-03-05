"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ExportPanel } from "@/components/book/ExportPanel";
import { useAnnouncer } from "@/hooks/useAnnouncer";
import { books as booksApi } from "@/lib/api";
import type { Book } from "@/types/book";
import Link from "next/link";

/**
 * Publishing page for exporting and downloading the finished book.
 */
export default function PublishPage() {
  const params = useParams();
  const bookId = params.bookId as string;
  const { announcePolite, announceAssertive } = useAnnouncer();

  const [book, setBook] = useState<Book | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const response = await booksApi.get(bookId);
        setBook(response.data);
        announcePolite("출판 페이지가 열렸습니다");
      } catch {
        announceAssertive("데이터를 불러올 수 없습니다");
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, [bookId, announcePolite, announceAssertive]);

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
          {book?.title} - 출판
        </h1>
        <Link
          href={`/design/${bookId}`}
          className="
            inline-flex items-center
            text-primary-700 dark:text-primary-400
            font-medium no-underline hover:underline
            focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-600
            rounded-lg px-3 py-2 min-h-touch
          "
          aria-label="디자인으로 돌아가기"
        >
          디자인으로 돌아가기
        </Link>
      </div>

      {/* Book info summary */}
      <section
        className="p-6 bg-green-50 dark:bg-green-900/20 rounded-xl border border-green-200 dark:border-green-800"
        aria-label="출판 준비 완료"
      >
        <h2 className="text-xl font-bold text-green-800 dark:text-green-200 mb-2">
          출판 준비가 완료되었습니다!
        </h2>
        <p className="text-base text-green-700 dark:text-green-300">
          아래에서 원하는 형식을 선택하여 작품을 내보내세요.
        </p>
      </section>

      {/* Export panel */}
      <section className="bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-200 dark:border-gray-700">
        <ExportPanel bookId={bookId} bookTitle={book?.title} />
      </section>

      {/* Back to dashboard */}
      <div className="flex justify-center pt-4">
        <Link
          href="/dashboard"
          className="
            inline-flex items-center justify-center
            text-primary-700 dark:text-primary-400
            font-medium no-underline hover:underline
            focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-600
            rounded-lg px-3 py-2 min-h-touch
          "
          aria-label="대시보드로 돌아가기"
        >
          대시보드로 돌아가기
        </Link>
      </div>
    </div>
  );
}
