"use client";

import { useCallback, useEffect, useState, useRef } from "react";
import { useParams } from "next/navigation";
import { VoiceRecorder } from "@/components/voice/VoiceRecorder";
import { VoicePlayer } from "@/components/voice/VoicePlayer";
import { VoiceCommandIndicator } from "@/components/voice/VoiceCommand";
import { WritingEditor } from "@/components/writing/WritingEditor";
import { ChapterList } from "@/components/writing/ChapterList";
import { StreamingText } from "@/components/writing/StreamingText";
import { Button } from "@/components/ui/Button";
import { useAnnouncer } from "@/hooks/useAnnouncer";
import {
  books as booksApi,
  chapters as chaptersApi,
  writing as writingApi,
} from "@/lib/api";
import type { Book, Chapter } from "@/types/book";
import type { VoiceCommandType } from "@/types/voice";

/**
 * Writing workspace page.
 * Combines voice recording, AI generation, text editing, and TTS.
 */
export default function WritingWorkspacePage() {
  const params = useParams();
  const bookId = params.bookId as string;
  const { announcePolite, announceAssertive } = useAnnouncer();

  const [book, setBook] = useState<Book | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [activeChapter, setActiveChapter] = useState<Chapter | null>(null);
  const [content, setContent] = useState("");
  const [transcript, setTranscript] = useState("");
  const [streamedText, setStreamedText] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  // Load book and chapters
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
          setContent(chapterList[0].content);
        }
        announcePolite(`${bookRes.data.title} 작업 공간이 열렸습니다`);
      } catch {
        setError("작품을 불러올 수 없습니다");
        announceAssertive("작품을 불러올 수 없습니다");
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, [bookId, announcePolite, announceAssertive]);

  // Select chapter
  const handleSelectChapter = useCallback(
    (chapter: Chapter) => {
      setActiveChapter(chapter);
      setContent(chapter.content);
      setStreamedText("");
      announcePolite(`${chapter.title} 챕터가 선택되었습니다`);
    },
    [announcePolite]
  );

  // Add chapter
  const handleAddChapter = useCallback(async () => {
    try {
      const newNumber = chapters.length + 1;
      const response = await chaptersApi.create(bookId, {
        title: `제${newNumber}장`,
        order: newNumber,
      });
      setChapters((prev) => [...prev, response.data]);
      setActiveChapter(response.data);
      setContent("");
      announcePolite(`새 챕터 제${newNumber}장이 추가되었습니다`);
    } catch {
      announceAssertive("챕터 추가에 실패했습니다");
    }
  }, [bookId, chapters.length, announcePolite, announceAssertive]);

  // Remove chapter
  const handleRemoveChapter = useCallback(
    async (chapterId: string) => {
      try {
        await chaptersApi.delete(bookId, chapterId);
        setChapters((prev) => prev.filter((c) => c.id !== chapterId));
        if (activeChapter?.id === chapterId) {
          setActiveChapter(null);
          setContent("");
        }
        announcePolite("챕터가 삭제되었습니다");
      } catch {
        announceAssertive("챕터 삭제에 실패했습니다");
      }
    },
    [bookId, activeChapter, announcePolite, announceAssertive]
  );

  // Save content
  const handleSave = useCallback(async () => {
    if (!activeChapter) return;
    setIsSaving(true);
    try {
      await chaptersApi.update(bookId, activeChapter.id, {
        content,
      });
      announcePolite("저장되었습니다");
    } catch {
      announceAssertive("저장에 실패했습니다");
    } finally {
      setIsSaving(false);
    }
  }, [bookId, activeChapter, content, transcript, announcePolite, announceAssertive]);

  // Handle STT transcript
  const handleTranscript = useCallback(
    (text: string) => {
      setTranscript(text);
      setContent((prev) => (prev ? `${prev}\n${text}` : text));
      announcePolite("음성 인식 결과가 편집기에 추가되었습니다");
    },
    [announcePolite]
  );

  // AI text generation
  const handleGenerate = useCallback(async () => {
    if (!activeChapter) return;

    // M-02: 빈 prompt 방지
    if (!transcript.trim() && !content.trim()) {
      announceAssertive("AI 생성을 위해 먼저 음성 녹음이나 텍스트를 입력해 주세요.");
      return;
    }

    setIsStreaming(true);
    setStreamedText("");
    announcePolite("AI가 글을 생성하고 있습니다");

    abortControllerRef.current = new AbortController();

    try {
      const stream = await writingApi.generate(
        {
          genre: book?.genre || "essay",
          prompt: transcript || content,
          context: content,
          chapter_title: activeChapter.title,
        },
        { signal: abortControllerRef.current.signal }
      );

      const reader = stream.getReader();
      let fullText = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        fullText += value;
        setStreamedText(fullText);
      }

      // Append generated text to content
      setContent((prev) => (prev ? `${prev}\n\n${fullText}` : fullText));
      announcePolite("AI 글 생성이 완료되었습니다");
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") {
        announcePolite("AI 생성이 중단되었습니다");
      } else {
        announceAssertive("AI 글 생성에 실패했습니다");
      }
    } finally {
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  }, [bookId, activeChapter, transcript, content, announcePolite, announceAssertive]);

  const handleStopGeneration = useCallback(() => {
    abortControllerRef.current?.abort();
  }, []);

  // Voice command handler
  const handleVoiceCommand = useCallback(
    (command: VoiceCommandType) => {
      switch (command) {
        case "save":
          handleSave();
          break;
        case "read":
          // TTS will be triggered by the VoicePlayer
          break;
        case "stop":
          handleStopGeneration();
          break;
        default:
          break;
      }
    },
    [handleSave, handleStopGeneration]
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20" role="status" aria-live="polite">
        <p className="text-xl text-gray-500 dark:text-gray-400">불러오는 중...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center gap-4 py-20" role="alert">
        <p className="text-xl text-red-600 dark:text-red-400">{error}</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Page heading */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
          {book?.title || "글쓰기"}
        </h1>
        <div className="flex items-center gap-3">
          <VoiceCommandIndicator
            transcript={transcript}
            onCommand={handleVoiceCommand}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar: Chapter list */}
        <aside className="lg:col-span-1">
          <ChapterList
            chapters={chapters}
            activeChapterId={activeChapter?.id}
            onSelectChapter={handleSelectChapter}
            onAddChapter={handleAddChapter}
            onRemoveChapter={handleRemoveChapter}
          />
        </aside>

        {/* Main content area */}
        <div className="lg:col-span-3 flex flex-col gap-6">
          {/* Voice recorder */}
          <section aria-label="음성 녹음">
            <VoiceRecorder onTranscript={handleTranscript} />
          </section>

          {/* AI generation controls */}
          <div className="flex items-center gap-3 flex-wrap">
            <Button
              variant="primary"
              size="default"
              onClick={handleGenerate}
              disabled={isStreaming || !activeChapter}
              isLoading={isStreaming}
              aria-label="AI 글 생성 시작"
            >
              AI로 글 생성
            </Button>
            {isStreaming && (
              <Button
                variant="destructive"
                size="default"
                onClick={handleStopGeneration}
                aria-label="AI 글 생성 중단"
              >
                생성 중단
              </Button>
            )}
          </div>

          {/* Streaming text display */}
          {(isStreaming || streamedText) && (
            <StreamingText text={streamedText} isStreaming={isStreaming} />
          )}

          {/* Writing editor */}
          {activeChapter ? (
            <WritingEditor
              content={content}
              onChange={setContent}
              onSave={handleSave}
              isSaving={isSaving}
              chapterTitle={activeChapter.title}
            />
          ) : (
            <div className="text-center py-12 bg-gray-50 dark:bg-gray-800 rounded-xl">
              <p className="text-lg text-gray-500 dark:text-gray-400">
                왼쪽에서 챕터를 선택하거나 새 챕터를 추가하세요.
              </p>
            </div>
          )}

          {/* TTS Player */}
          {content && (
            <section aria-label="음성 낭독">
              <VoicePlayer text={content} />
            </section>
          )}

          {/* Navigation to editing */}
          {activeChapter && content && (
            <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <a
                href={`/write/${bookId}/edit`}
                className="
                  inline-flex items-center justify-center
                  bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100
                  px-6 py-3 rounded-xl
                  text-base font-semibold
                  no-underline
                  hover:bg-gray-300 dark:hover:bg-gray-600
                  focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-600
                  min-h-touch
                "
                aria-label="편집 단계로 이동"
              >
                편집하기
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
