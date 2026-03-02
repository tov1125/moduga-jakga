"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { useAnnouncer } from "@/hooks/useAnnouncer";
import { useSupabase } from "@/hooks/useSupabase";
import { books as booksApi } from "@/lib/api";
import { genreLabel, statusLabel, formatRelativeDate } from "@/lib/utils";
import type { Book } from "@/types/book";

/**
 * Dashboard page showing the user's books.
 */
export default function DashboardPage() {
  const { user, isLoading: authLoading } = useSupabase();
  const { announcePolite, announceAssertive } = useAnnouncer();

  const [bookList, setBookList] = useState<Book[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadBooks = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await booksApi.list();
      setBookList(response.data);
      announcePolite(`${response.data.length}개의 작품을 불러왔습니다`);
    } catch {
      setError("작품 목록을 불러올 수 없습니다");
      announceAssertive("작품 목록을 불러올 수 없습니다");
    } finally {
      setIsLoading(false);
    }
  }, [announcePolite, announceAssertive]);

  useEffect(() => {
    if (!authLoading && user) {
      loadBooks();
    } else if (!authLoading && !user) {
      setIsLoading(false);
    }
  }, [authLoading, user, loadBooks]);

  if (authLoading || isLoading) {
    return (
      <div className="flex items-center justify-center py-20" role="status" aria-live="polite">
        <p className="text-xl text-gray-500 dark:text-gray-400">
          불러오는 중...
        </p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex flex-col items-center gap-6 py-20">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
          로그인이 필요합니다
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          대시보드를 이용하려면 먼저 로그인해 주세요.
        </p>
        <Link
          href="/login"
          className="
            inline-flex items-center justify-center
            bg-primary-600 text-white
            px-6 py-3 rounded-xl
            text-lg font-bold
            no-underline
            hover:bg-primary-700
            focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-yellow-400
          "
        >
          로그인하기
        </Link>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
          내 작품
        </h1>
        <Link
          href="/write"
          className="
            inline-flex items-center justify-center
            bg-primary-600 text-white
            px-6 py-3 rounded-xl
            text-lg font-bold
            no-underline
            hover:bg-primary-700
            focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-yellow-400
            min-h-touch
          "
          aria-label="새 작품 만들기"
        >
          + 새 작품 만들기
        </Link>
      </div>

      {/* Error */}
      {error && (
        <div
          className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl"
          role="alert"
        >
          <p className="text-red-700 dark:text-red-300 text-base">
            {error}
          </p>
          <Button
            variant="ghost"
            size="sm"
            onClick={loadBooks}
            aria-label="다시 시도"
            className="mt-2"
          >
            다시 시도
          </Button>
        </div>
      )}

      {/* Book list */}
      {bookList.length === 0 ? (
        <div className="text-center py-16 bg-gray-50 dark:bg-gray-800 rounded-2xl">
          <p className="text-xl text-gray-500 dark:text-gray-400 mb-4">
            아직 작품이 없습니다
          </p>
          <p className="text-base text-gray-400 dark:text-gray-500 mb-6">
            첫 번째 작품을 만들어 보세요!
          </p>
          <Link
            href="/write"
            className="
              inline-flex items-center justify-center
              bg-primary-600 text-white
              px-6 py-3 rounded-xl
              text-lg font-bold
              no-underline
              hover:bg-primary-700
              focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-yellow-400
            "
          >
            작품 만들기
          </Link>
        </div>
      ) : (
        <ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" aria-label="작품 목록">
          {bookList.map((book) => (
            <li key={book.id}>
              <Link
                href={`/write/${book.id}`}
                className="
                  block p-6 rounded-2xl
                  bg-white dark:bg-gray-800
                  border-2 border-gray-200 dark:border-gray-700
                  hover:border-primary-300 dark:hover:border-primary-600
                  transition-colors duration-150
                  no-underline
                  focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-yellow-400
                  group
                "
                aria-label={`${book.title} - ${genreLabel(book.genre)}, ${statusLabel(book.status)}, ${formatRelativeDate(book.updatedAt)} 수정`}
              >
                <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400">
                  {book.title}
                </h2>
                <div className="flex items-center gap-3 mb-3">
                  <span className="inline-block px-2 py-0.5 rounded text-sm font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                    {genreLabel(book.genre)}
                  </span>
                  <span className="inline-block px-2 py-0.5 rounded text-sm font-medium bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300">
                    {statusLabel(book.status)}
                  </span>
                </div>
                {book.description && (
                  <p className="text-base text-gray-600 dark:text-gray-400 line-clamp-2 mb-3">
                    {book.description}
                  </p>
                )}
                <p className="text-sm text-gray-500 dark:text-gray-500">
                  {book.chapters.length}개 챕터 | {formatRelativeDate(book.updatedAt)} 수정
                </p>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
