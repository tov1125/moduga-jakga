"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { CoverDesigner } from "@/components/book/CoverDesigner";
import { Button } from "@/components/ui/Button";
import { useAnnouncer } from "@/hooks/useAnnouncer";
import { useSupabase } from "@/hooks/useSupabase";
import { books as booksApi, design as designApi } from "@/lib/api";
import type { Book } from "@/types/book";
import Link from "next/link";

/**
 * Design page for cover design and interior layout.
 */
export default function DesignPage() {
  const params = useParams();
  const bookId = params.bookId as string;
  const { announcePolite, announceAssertive } = useAnnouncer();
  const { user } = useSupabase();

  const [book, setBook] = useState<Book | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [fontSize, setFontSize] = useState(16);
  const [fontFamily, setFontFamily] = useState("default");
  const [pageSize, setPageSize] = useState("B5");
  const [lineSpacing, setLineSpacing] = useState(1.6);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const response = await booksApi.get(bookId);
        setBook(response.data);
        announcePolite("디자인 페이지가 열렸습니다");
      } catch {
        announceAssertive("데이터를 불러올 수 없습니다");
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, [bookId, announcePolite, announceAssertive]);

  const handlePreviewLayout = useCallback(async () => {
    setIsPreviewLoading(true);
    try {
      const response = await designApi.layoutPreview({
        book_id: bookId,
        page_size: pageSize,
        font_size: fontSize,
        line_spacing: lineSpacing,
      });
      setPreviewUrl(response.data.preview_url);
      announcePolite("레이아웃 미리보기가 준비되었습니다");
    } catch {
      announceAssertive("레이아웃 미리보기를 생성할 수 없습니다");
    } finally {
      setIsPreviewLoading(false);
    }
  }, [bookId, pageSize, fontSize, lineSpacing, announcePolite, announceAssertive]);

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
          {book?.title} - 디자인
        </h1>
        <Link
          href={`/write/${bookId}/review`}
          className="
            inline-flex items-center
            text-primary-700 dark:text-primary-400
            font-medium no-underline hover:underline
            focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-600
            rounded-lg px-3 py-2 min-h-touch
          "
          aria-label="검토로 돌아가기"
        >
          검토로 돌아가기
        </Link>
      </div>

      {/* Cover Design */}
      <section className="bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-200 dark:border-gray-700">
        <CoverDesigner
          bookTitle={book?.title || ""}
          authorName={user?.display_name || ""}
          bookGenre={book?.genre}
          currentCoverUrl={undefined}
        />
      </section>

      {/* Interior Layout */}
      <section
        className="bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-200 dark:border-gray-700"
        aria-label="내지 레이아웃 설정"
      >
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">
          내지 레이아웃
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Page size */}
          <div className="flex flex-col gap-2">
            <label
              htmlFor="page-size"
              className="text-base font-medium text-gray-900 dark:text-gray-100"
            >
              판형
            </label>
            <select
              id="page-size"
              value={pageSize}
              onChange={(e) => setPageSize(e.target.value)}
              className="
                w-full px-4 py-3 min-h-touch
                text-base text-gray-900 dark:text-gray-100
                bg-white dark:bg-gray-800
                border-2 border-gray-300 dark:border-gray-600
                rounded-xl
                focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-600
              "
            >
              <option value="A5">A5 (148×210mm)</option>
              <option value="B5">신국판 B5 (152×225mm)</option>
              <option value="A4">A4 (210×297mm)</option>
              <option value="paperback">46판 (127×188mm)</option>
            </select>
          </div>

          {/* Font family */}
          <div className="flex flex-col gap-2">
            <label
              htmlFor="font-family"
              className="text-base font-medium text-gray-900 dark:text-gray-100"
            >
              글꼴 선택
            </label>
            <select
              id="font-family"
              value={fontFamily}
              onChange={(e) => setFontFamily(e.target.value)}
              className="
                w-full px-4 py-3 min-h-touch
                text-base text-gray-900 dark:text-gray-100
                bg-white dark:bg-gray-800
                border-2 border-gray-300 dark:border-gray-600
                rounded-xl
                focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-600
              "
            >
              <option value="default">기본 글꼴</option>
              <option value="nanum-myeongjo">나눔명조</option>
              <option value="nanum-gothic">나눔고딕</option>
              <option value="noto-serif">Noto Serif Korean</option>
            </select>
          </div>

          {/* Font size */}
          <div className="flex flex-col gap-2">
            <label
              htmlFor="font-size"
              className="text-base font-medium text-gray-900 dark:text-gray-100"
            >
              글자 크기: {fontSize}pt
            </label>
            <input
              id="font-size"
              type="range"
              min={12}
              max={24}
              value={fontSize}
              onChange={(e) => setFontSize(Number(e.target.value))}
              aria-valuenow={fontSize}
              aria-valuemin={12}
              aria-valuemax={24}
              aria-label={`글자 크기: ${fontSize}포인트`}
              className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-sm text-gray-500 dark:text-gray-400">
              <span>12pt</span>
              <span>24pt</span>
            </div>
          </div>

          {/* Line spacing */}
          <div className="flex flex-col gap-2">
            <label
              htmlFor="line-spacing"
              className="text-base font-medium text-gray-900 dark:text-gray-100"
            >
              줄 간격: {lineSpacing.toFixed(1)}
            </label>
            <input
              id="line-spacing"
              type="range"
              min={1.0}
              max={2.5}
              step={0.1}
              value={lineSpacing}
              onChange={(e) => setLineSpacing(Number(e.target.value))}
              aria-valuenow={lineSpacing}
              aria-valuemin={1.0}
              aria-valuemax={2.5}
              aria-label={`줄 간격: ${lineSpacing.toFixed(1)}배`}
              className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-sm text-gray-500 dark:text-gray-400">
              <span>1.0</span>
              <span>2.5</span>
            </div>
          </div>
        </div>

        {/* Preview button */}
        <div className="mt-6">
          <Button
            variant="secondary"
            size="default"
            onClick={handlePreviewLayout}
            isLoading={isPreviewLoading}
            aria-label="레이아웃 미리보기"
          >
            미리보기
          </Button>
        </div>

        {/* Preview */}
        {previewUrl && (
          <div className="mt-6" aria-label="레이아웃 미리보기">
            <img
              src={previewUrl}
              alt="내지 레이아웃 미리보기 이미지"
              className="w-full max-w-lg mx-auto rounded-xl shadow-lg"
            />
          </div>
        )}
      </section>

      {/* Next step */}
      <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
        <Link
          href={`/publish/${bookId}`}
          className="
            inline-flex items-center justify-center
            bg-primary-500 text-white
            px-6 py-3 rounded-xl
            text-base font-semibold
            no-underline
            hover:bg-primary-600
            focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-600
            min-h-touch
          "
          aria-label="출판 단계로 이동"
        >
          출판하기
        </Link>
      </div>
    </div>
  );
}
