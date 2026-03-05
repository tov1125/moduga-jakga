"use client";

import { useCallback, useRef, useState } from "react";
import { Button } from "@/components/ui/Button";
import { useAnnouncer } from "@/hooks/useAnnouncer";

interface WritingEditorProps {
  /** Current content */
  content: string;
  /** Callback when content changes */
  onChange: (content: string) => void;
  /** Callback when save is requested */
  onSave: () => void;
  /** Whether save is in progress */
  isSaving?: boolean;
  /** Chapter title for labeling */
  chapterTitle?: string;
  /** Additional CSS class */
  className?: string;
}

/**
 * Main writing editor component.
 * Provides a textarea for AI-generated content, integrated with STT input.
 * Fully accessible with aria labels and keyboard navigation.
 */
export function WritingEditor({
  content,
  onChange,
  onSave,
  isSaving = false,
  chapterTitle = "챕터",
  className = "",
}: WritingEditorProps) {
  const { announcePolite } = useAnnouncer();
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [wordCount, setWordCount] = useState(0);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const newContent = e.target.value;
      onChange(newContent);
      // Count Korean characters (or any characters)
      const count = newContent.replace(/\s/g, "").length;
      setWordCount(count);
    },
    [onChange]
  );

  const handleAppendText = useCallback(
    (text: string) => {
      const newContent = content ? `${content}\n${text}` : text;
      onChange(newContent);
      const count = newContent.replace(/\s/g, "").length;
      setWordCount(count);
      announcePolite("텍스트가 추가되었습니다");

      // Focus textarea and scroll to bottom
      if (textareaRef.current) {
        textareaRef.current.focus();
        textareaRef.current.scrollTop = textareaRef.current.scrollHeight;
      }
    },
    [content, onChange, announcePolite]
  );

  const handleSave = useCallback(() => {
    onSave();
    announcePolite("저장 중입니다");
  }, [onSave, announcePolite]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      // Ctrl+S or Cmd+S to save
      if ((e.ctrlKey || e.metaKey) && e.key === "s") {
        e.preventDefault();
        handleSave();
      }
    },
    [handleSave]
  );

  return (
    <div
      className={`flex flex-col gap-4 ${className}`}
      role="region"
      aria-label="글쓰기 편집기"
    >
      {/* Editor header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
          {chapterTitle}
        </h2>
        <div className="flex items-center gap-3">
          <span
            className="text-base text-gray-600 dark:text-gray-400"
            aria-label={`${wordCount}자 작성됨`}
          >
            {wordCount}자
          </span>
          <Button
            variant="primary"
            size="default"
            onClick={handleSave}
            isLoading={isSaving}
            aria-label="저장하기 (Ctrl+S)"
          >
            저장
          </Button>
        </div>
      </div>

      {/* Textarea */}
      <div className="relative">
        <label htmlFor="writing-editor" className="sr-only">
          {chapterTitle} 내용 편집
        </label>
        <textarea
          id="writing-editor"
          ref={textareaRef}
          value={content}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          aria-label={`${chapterTitle} 내용 편집`}
          aria-describedby="editor-hint"
          placeholder="여기에 글을 작성하거나, 음성 녹음으로 내용을 추가하세요..."
          className="
            w-full min-h-[400px] p-6
            text-lg leading-relaxed
            text-gray-900 dark:text-gray-100
            bg-white dark:bg-gray-800
            border-2 border-gray-300 dark:border-gray-600
            rounded-xl
            resize-y
            focus:border-primary-500 dark:focus:border-primary-400
            focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-600
            placeholder:text-gray-400 dark:placeholder:text-gray-500
          "
        />
        <p id="editor-hint" className="sr-only">
          Ctrl+S로 저장할 수 있습니다. 음성 녹음 결과가 자동으로 추가됩니다.
        </p>
      </div>

      {/* Expose appendText for parent components */}
      <input type="hidden" data-append-text={handleAppendText.toString()} />
    </div>
  );
}

// Export the append function type for parent components
export type WritingEditorHandle = {
  appendText: (text: string) => void;
};
