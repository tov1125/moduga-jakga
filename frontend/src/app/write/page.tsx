"use client";

import { useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { useAnnouncer } from "@/hooks/useAnnouncer";
import { books as booksApi } from "@/lib/api";
import type { BookGenre } from "@/types/book";

const GENRE_OPTIONS: { value: BookGenre; label: string; description: string }[] = [
  {
    value: "essay",
    label: "에세이",
    description: "일상의 이야기와 생각을 자유롭게 풀어내는 글",
  },
  {
    value: "novel",
    label: "소설",
    description: "상상력을 발휘한 이야기와 등장인물의 세계",
  },
  {
    value: "poem",
    label: "시",
    description: "감성과 리듬이 어우러진 짧은 글",
  },
  {
    value: "autobiography",
    label: "자서전",
    description: "나의 인생 이야기를 기록하는 글",
  },
];

/**
 * New writing page - create a new book.
 */
export default function NewWritePage() {
  const router = useRouter();
  const { announcePolite, announceAssertive } = useAnnouncer();

  const [title, setTitle] = useState("");
  const [genre, setGenre] = useState<BookGenre>("essay");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setError(null);

      if (!title.trim()) {
        setError("작품 제목을 입력해 주세요.");
        announceAssertive("작품 제목을 입력해 주세요.");
        return;
      }

      setIsLoading(true);

      try {
        const response = await booksApi.create({
          title: title.trim(),
          genre,
          description: description.trim() || undefined,
        });
        announcePolite("새 작품이 만들어졌습니다. 글쓰기 페이지로 이동합니다.");
        router.push(`/write/${response.data.id}`);
      } catch {
        setError("작품 생성에 실패했습니다. 다시 시도해 주세요.");
        announceAssertive("작품 생성에 실패했습니다");
      } finally {
        setIsLoading(false);
      }
    },
    [title, genre, description, router, announcePolite, announceAssertive]
  );

  return (
    <div className="flex flex-col items-center py-8">
      <div className="w-full max-w-lg">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-8 text-center">
          새 작품 만들기
        </h1>

        <form
          onSubmit={handleSubmit}
          className="flex flex-col gap-6"
          aria-label="새 작품 만들기 양식"
        >
          {/* Error */}
          {error && (
            <div
              className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl"
              role="alert"
            >
              <p className="text-red-700 dark:text-red-300 text-base font-medium">
                {error}
              </p>
            </div>
          )}

          {/* Title */}
          <div className="flex flex-col gap-2">
            <label
              htmlFor="book-title"
              className="text-base font-medium text-gray-900 dark:text-gray-100"
            >
              작품 제목 <span aria-hidden="true">*</span>
            </label>
            <input
              id="book-title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              aria-required="true"
              className="
                w-full px-4 py-3 min-h-touch
                text-lg text-gray-900 dark:text-gray-100
                bg-white dark:bg-gray-800
                border-2 border-gray-300 dark:border-gray-600
                rounded-xl
                focus:border-primary-500 dark:focus:border-primary-400
                focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-600
                placeholder:text-gray-400
              "
              placeholder="작품 제목을 입력하세요"
            />
          </div>

          {/* Genre selection */}
          <fieldset>
            <legend className="text-base font-medium text-gray-900 dark:text-gray-100 mb-3">
              장르 선택 <span aria-hidden="true">*</span>
            </legend>
            <div
              role="radiogroup"
              aria-label="장르 선택"
              className="grid grid-cols-1 sm:grid-cols-2 gap-3"
            >
              {GENRE_OPTIONS.map((option) => (
                <label
                  key={option.value}
                  className={`
                    flex flex-col p-4 rounded-xl cursor-pointer
                    min-h-touch
                    transition-colors duration-150
                    focus-within:ring-4 focus-within:ring-primary-600
                    ${
                      genre === option.value
                        ? "border-2 border-primary-500 bg-primary-50 dark:bg-primary-900/20"
                        : "border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-gray-300"
                    }
                  `}
                >
                  <div className="flex items-center gap-3">
                    <input
                      type="radio"
                      name="genre"
                      value={option.value}
                      checked={genre === option.value}
                      onChange={() => setGenre(option.value)}
                      className="w-5 h-5 text-primary-700"
                    />
                    <span className="text-base font-semibold text-gray-900 dark:text-gray-100">
                      {option.label}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 ml-8">
                    {option.description}
                  </p>
                </label>
              ))}
            </div>
          </fieldset>

          {/* Description */}
          <div className="flex flex-col gap-2">
            <label
              htmlFor="book-description"
              className="text-base font-medium text-gray-900 dark:text-gray-100"
            >
              간단한 설명 (선택)
            </label>
            <textarea
              id="book-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              aria-describedby="book-desc-hint"
              className="
                w-full px-4 py-3
                text-lg text-gray-900 dark:text-gray-100
                bg-white dark:bg-gray-800
                border-2 border-gray-300 dark:border-gray-600
                rounded-xl resize-y
                focus:border-primary-500 dark:focus:border-primary-400
                focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-600
                placeholder:text-gray-400
              "
              placeholder="작품에 대해 간단히 설명해 주세요"
            />
            <p
              id="book-desc-hint"
              className="text-sm text-gray-500 dark:text-gray-400"
            >
              나중에 수정할 수 있습니다.
            </p>
          </div>

          {/* Submit */}
          <Button
            type="submit"
            variant="primary"
            size="lg"
            isLoading={isLoading}
            aria-label="글쓰기 시작"
            className="w-full"
          >
            글쓰기 시작
          </Button>
        </form>
      </div>
    </div>
  );
}
