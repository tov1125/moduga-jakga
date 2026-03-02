"use client";

import { useCallback, useState } from "react";
import { Button } from "@/components/ui/Button";
import { useAnnouncer } from "@/hooks/useAnnouncer";
import { design } from "@/lib/api";
import type { CoverTemplate } from "@/types/book";

interface CoverDesignerProps {
  bookId: string;
  bookTitle: string;
  currentCoverUrl?: string | null;
  className?: string;
}

/**
 * Cover design interface.
 * Allows generating AI covers, selecting templates,
 * and viewing cover descriptions via TTS.
 */
export function CoverDesigner({
  bookId,
  bookTitle,
  currentCoverUrl,
  className = "",
}: CoverDesignerProps) {
  const { announcePolite, announceAssertive } = useAnnouncer();
  const [coverUrl, setCoverUrl] = useState(currentCoverUrl || "");
  const [templates, setTemplates] = useState<CoverTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLoadingTemplates, setIsLoadingTemplates] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLoadTemplates = useCallback(async () => {
    setIsLoadingTemplates(true);
    setError(null);
    try {
      const response = await design.templates();
      setTemplates(response.data);
      announcePolite(`${response.data.length}개의 템플릿을 불러왔습니다`);
    } catch {
      setError("템플릿을 불러올 수 없습니다");
      announceAssertive("템플릿을 불러올 수 없습니다");
    } finally {
      setIsLoadingTemplates(false);
    }
  }, [announcePolite, announceAssertive]);

  const handleGenerateCover = useCallback(async () => {
    setIsGenerating(true);
    setError(null);
    announcePolite("표지를 생성하고 있습니다. 잠시 기다려 주세요.");

    try {
      const response = await design.generateCover(
        bookId,
        selectedTemplate || undefined
      );
      setCoverUrl(response.data.coverUrl);
      announcePolite("새 표지가 생성되었습니다");
    } catch {
      setError("표지 생성에 실패했습니다. 다시 시도해 주세요.");
      announceAssertive("표지 생성에 실패했습니다");
    } finally {
      setIsGenerating(false);
    }
  }, [bookId, selectedTemplate, announcePolite, announceAssertive]);

  return (
    <div
      className={`flex flex-col gap-6 ${className}`}
      role="region"
      aria-label="표지 디자이너"
    >
      <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
        표지 디자인
      </h2>

      {/* Current cover preview */}
      <div className="flex flex-col items-center gap-4">
        {coverUrl ? (
          <div className="relative w-64 h-80 bg-gray-100 dark:bg-gray-800 rounded-xl overflow-hidden shadow-lg">
            <img
              src={coverUrl}
              alt={`${bookTitle} 표지 이미지`}
              className="w-full h-full object-cover"
            />
          </div>
        ) : (
          <div className="w-64 h-80 bg-gray-100 dark:bg-gray-800 rounded-xl flex items-center justify-center shadow-lg">
            <p className="text-gray-500 dark:text-gray-400 text-center px-4">
              아직 표지가 없습니다.
              <br />
              아래 버튼으로 생성해 보세요.
            </p>
          </div>
        )}
      </div>

      {/* Generate button */}
      <div className="flex flex-col gap-3 items-center">
        <Button
          variant="primary"
          size="lg"
          onClick={handleGenerateCover}
          isLoading={isGenerating}
          aria-label={coverUrl ? "표지 다시 생성" : "AI 표지 생성"}
        >
          {coverUrl ? "표지 다시 생성" : "AI 표지 생성"}
        </Button>
      </div>

      {/* Template selection */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            템플릿 선택
          </h3>
          <Button
            variant="secondary"
            size="sm"
            onClick={handleLoadTemplates}
            isLoading={isLoadingTemplates}
            aria-label="템플릿 불러오기"
          >
            템플릿 불러오기
          </Button>
        </div>

        {templates.length > 0 && (
          <div
            role="radiogroup"
            aria-label="표지 템플릿 선택"
            className="grid grid-cols-2 md:grid-cols-3 gap-3"
          >
            {templates.map((template) => (
              <button
                key={template.id}
                role="radio"
                aria-checked={selectedTemplate === template.id}
                onClick={() => {
                  setSelectedTemplate(template.id);
                  announcePolite(`${template.name} 템플릿 선택됨`);
                }}
                className={`
                  flex flex-col items-center gap-2 p-3 rounded-xl
                  min-h-touch
                  transition-colors duration-150
                  focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-yellow-400
                  ${
                    selectedTemplate === template.id
                      ? "border-2 border-primary-500 bg-primary-50 dark:bg-primary-900/20"
                      : "border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-gray-300"
                  }
                `}
              >
                <div className="w-full h-24 bg-gray-200 dark:bg-gray-700 rounded-lg overflow-hidden">
                  {template.previewUrl && (
                    <img
                      src={template.previewUrl}
                      alt={`${template.name} 템플릿 미리보기`}
                      className="w-full h-full object-cover"
                    />
                  )}
                </div>
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {template.name}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {template.description}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <p
          className="text-red-600 dark:text-red-400 text-base font-medium text-center"
          role="alert"
        >
          {error}
        </p>
      )}
    </div>
  );
}
