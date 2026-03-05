"use client";

import { useCallback, useRef } from "react";
import type { Chapter } from "@/types/book";
import { chapterStatusLabel } from "@/lib/utils";
import { Button } from "@/components/ui/Button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useAnnouncer } from "@/hooks/useAnnouncer";

interface ChapterListProps {
  chapters: Chapter[];
  activeChapterId?: string;
  onSelectChapter: (chapter: Chapter) => void;
  onAddChapter: () => void;
  onRemoveChapter?: (chapterId: string) => void;
  className?: string;
}

/**
 * Chapter list/navigation sidebar.
 * Ordered list of chapters with keyboard navigation,
 * add/remove capabilities.
 */
export function ChapterList({
  chapters,
  activeChapterId,
  onSelectChapter,
  onAddChapter,
  onRemoveChapter,
  className = "",
}: ChapterListProps) {
  const { announcePolite } = useAnnouncer();
  const listRef = useRef<HTMLOListElement>(null);

  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLOListElement>) => {
      if (!listRef.current) return;

      const items = listRef.current.querySelectorAll<HTMLButtonElement>(
        '[role="option"]'
      );
      const itemArray = Array.from(items);
      const currentIndex = itemArray.findIndex(
        (item) => item === document.activeElement
      );

      let nextIndex: number | null = null;

      if (event.key === "ArrowDown") {
        event.preventDefault();
        nextIndex =
          currentIndex < itemArray.length - 1 ? currentIndex + 1 : 0;
      }
      if (event.key === "ArrowUp") {
        event.preventDefault();
        nextIndex =
          currentIndex > 0 ? currentIndex - 1 : itemArray.length - 1;
      }
      if (event.key === "Home") {
        event.preventDefault();
        nextIndex = 0;
      }
      if (event.key === "End") {
        event.preventDefault();
        nextIndex = itemArray.length - 1;
      }

      if (nextIndex !== null && nextIndex >= 0 && nextIndex < itemArray.length) {
        itemArray[nextIndex].focus();
      }
    },
    []
  );

  const handleSelectChapter = useCallback(
    (chapter: Chapter) => {
      onSelectChapter(chapter);
      announcePolite(
        `${chapter.order}장 ${chapter.title} 선택됨`
      );
    },
    [onSelectChapter, announcePolite]
  );

  return (
    <nav
      className={`flex flex-col gap-3 ${className}`}
      aria-label="챕터 목록"
    >
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
          챕터 목록
        </h3>
        <Button
          variant="secondary"
          size="sm"
          onClick={onAddChapter}
          aria-label="새 챕터 추가"
        >
          + 추가
        </Button>
      </div>

      <ScrollArea className="max-h-96">
      <ol
        ref={listRef}
        role="listbox"
        aria-label="챕터 선택"
        onKeyDown={handleKeyDown}
        className="flex flex-col gap-1"
      >
        {chapters.length === 0 ? (
          <li className="text-base text-gray-500 dark:text-gray-400 p-4 text-center">
            아직 챕터가 없습니다. 새 챕터를 추가하세요.
          </li>
        ) : (
          chapters.map((chapter) => {
            const isActive = chapter.id === activeChapterId;
            return (
              <li key={chapter.id}>
                <button
                  role="option"
                  aria-selected={isActive}
                  onClick={() => handleSelectChapter(chapter)}
                  tabIndex={isActive ? 0 : -1}
                  className={`
                    w-full text-left p-3 rounded-lg
                    flex items-center justify-between
                    min-h-touch
                    transition-colors duration-150
                    focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-600
                    ${
                      isActive
                        ? "bg-primary-100 dark:bg-primary-900 text-primary-900 dark:text-primary-100 font-semibold"
                        : "bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
                    }
                  `}
                >
                  <span className="flex items-center gap-2">
                    <span className="text-sm text-gray-500 dark:text-gray-400 font-mono">
                      {chapter.order}.
                    </span>
                    <span className="text-base">{chapter.title}</span>
                  </span>
                  <span className="flex items-center gap-2">
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {chapterStatusLabel(chapter.status)}
                    </span>
                    {onRemoveChapter && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onRemoveChapter(chapter.id);
                        }}
                        aria-label={`${chapter.title} 챕터 삭제`}
                        className="
                          p-1 rounded
                          text-gray-400 hover:text-red-600
                          dark:text-gray-500 dark:hover:text-red-400
                          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-600
                          min-h-touch min-w-touch flex items-center justify-center
                        "
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          className="h-4 w-4"
                          viewBox="0 0 24 24"
                          fill="currentColor"
                          aria-hidden="true"
                        >
                          <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
                        </svg>
                      </button>
                    )}
                  </span>
                </button>
              </li>
            );
          })
        )}
      </ol>
      </ScrollArea>
    </nav>
  );
}
