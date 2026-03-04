"use client";

import { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";
import { useAnnouncer } from "@/hooks/useAnnouncer";
import { publishing } from "@/lib/api";
import type { ExportFormat, ExportStatus } from "@/types/book";

interface ExportPanelProps {
  bookId: string;
  bookTitle?: string;
  className?: string;
}

const FORMAT_LABELS: Record<ExportFormat, string> = {
  docx: "Word 문서 (DOCX)",
  pdf: "PDF 문서",
  epub: "전자책 (EPUB)",
};

const FORMAT_DESCRIPTIONS: Record<ExportFormat, string> = {
  docx: "Microsoft Word에서 편집할 수 있는 문서 형식입니다.",
  pdf: "인쇄 및 배포에 적합한 고정 레이아웃 문서입니다.",
  epub: "전자책 리더에서 읽을 수 있는 전자책 형식입니다.",
};

/**
 * Export/download panel for books.
 * Supports DOCX, PDF, EPUB formats with progress tracking.
 */
export function ExportPanel({ bookId, bookTitle, className = "" }: ExportPanelProps) {
  const { announcePolite, announceAssertive } = useAnnouncer();
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>("pdf");
  const [includeCover, setIncludeCover] = useState(true);
  const [includeToc, setIncludeToc] = useState(true);
  const [exportStatus, setExportStatus] = useState<ExportStatus | null>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExport = useCallback(async () => {
    setIsExporting(true);
    setError(null);
    announcePolite(`${FORMAT_LABELS[selectedFormat]} 형식으로 내보내기를 시작합니다`);

    try {
      const response = await publishing.exportBook({
        book_id: bookId,
        format: selectedFormat,
        include_cover: includeCover,
        include_toc: includeToc,
      });
      setExportStatus({
        export_id: response.data.export_id,
        book_id: response.data.book_id,
        format: response.data.format,
        status: response.data.status,
        progress: 0,
        error_message: null,
        created_at: response.data.created_at,
      });
      announcePolite("내보내기가 시작되었습니다. 진행 상황을 확인 중입니다.");
    } catch {
      setError("내보내기를 시작할 수 없습니다. 다시 시도해 주세요.");
      announceAssertive("내보내기 실패");
      setIsExporting(false);
    }
  }, [bookId, selectedFormat, includeCover, includeToc, announcePolite, announceAssertive]);

  // Poll export status
  useEffect(() => {
    if (!exportStatus || exportStatus.status === "completed" || exportStatus.status === "failed") {
      setIsExporting(false);
      return;
    }

    const interval = setInterval(async () => {
      try {
        const response = await publishing.status(exportStatus.export_id);
        setExportStatus(response.data);

        if (response.data.status === "completed") {
          announceAssertive("내보내기가 완료되었습니다. 다운로드할 수 있습니다.");
          setIsExporting(false);
        } else if (response.data.status === "failed") {
          setError(response.data.error_message || "내보내기에 실패했습니다");
          announceAssertive("내보내기에 실패했습니다");
          setIsExporting(false);
        }
      } catch {
        // Silently retry
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [exportStatus, announceAssertive]);

  const handleDownload = useCallback(async () => {
    if (!exportStatus?.export_id) return;

    try {
      const blob = await publishing.download(exportStatus.export_id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const fileName = bookTitle ? `${bookTitle}.${exportStatus.format}` : `export.${exportStatus.format}`;
      a.download = fileName;
      a.click();
      URL.revokeObjectURL(url);
      announcePolite("다운로드가 시작되었습니다");
    } catch {
      setError("다운로드에 실패했습니다");
      announceAssertive("다운로드 실패");
    }
  }, [exportStatus, bookTitle, announcePolite, announceAssertive]);

  return (
    <div
      className={`flex flex-col gap-6 ${className}`}
      role="region"
      aria-label="내보내기 및 다운로드"
    >
      <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
        작품 내보내기
      </h2>

      {/* Format selection */}
      <fieldset>
        <legend className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
          파일 형식 선택
        </legend>
        <div className="flex flex-col gap-3" role="radiogroup">
          {(Object.keys(FORMAT_LABELS) as ExportFormat[]).map((format) => (
            <label
              key={format}
              className={`
                flex items-start gap-4 p-4 rounded-xl cursor-pointer
                min-h-touch
                transition-colors duration-150
                focus-within:ring-4 focus-within:ring-yellow-400
                ${
                  selectedFormat === format
                    ? "border-2 border-primary-500 bg-primary-50 dark:bg-primary-900/20"
                    : "border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-gray-300"
                }
              `}
            >
              <input
                type="radio"
                name="export-format"
                value={format}
                checked={selectedFormat === format}
                onChange={() => setSelectedFormat(format)}
                className="mt-1 w-5 h-5 text-primary-600 focus:ring-primary-500"
                aria-describedby={`format-desc-${format}`}
              />
              <div>
                <span className="text-base font-medium text-gray-900 dark:text-gray-100">
                  {FORMAT_LABELS[format]}
                </span>
                <p
                  id={`format-desc-${format}`}
                  className="text-sm text-gray-500 dark:text-gray-400 mt-0.5"
                >
                  {FORMAT_DESCRIPTIONS[format]}
                </p>
              </div>
            </label>
          ))}
        </div>
      </fieldset>

      {/* Export options */}
      <div className="flex flex-col gap-3">
        <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          포함 항목
        </p>
        <label className="flex items-center gap-3 cursor-pointer min-h-touch">
          <input
            type="checkbox"
            checked={includeCover}
            onChange={(e) => setIncludeCover(e.target.checked)}
            className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
          />
          <span className="text-base text-gray-900 dark:text-gray-100">
            표지 포함
          </span>
        </label>
        <label className="flex items-center gap-3 cursor-pointer min-h-touch">
          <input
            type="checkbox"
            checked={includeToc}
            onChange={(e) => setIncludeToc(e.target.checked)}
            className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
          />
          <span className="text-base text-gray-900 dark:text-gray-100">
            목차 포함
          </span>
        </label>
      </div>

      {/* Export button */}
      <Button
        variant="primary"
        size="lg"
        onClick={handleExport}
        isLoading={isExporting}
        disabled={isExporting}
        aria-label={`${FORMAT_LABELS[selectedFormat]}로 내보내기`}
      >
        내보내기 시작
      </Button>

      {/* Export status */}
      {exportStatus && (
        <div
          className={`
            p-4 rounded-xl
            ${
              exportStatus.status === "completed"
                ? "bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800"
                : exportStatus.status === "failed"
                  ? "bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800"
                  : "bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800"
            }
          `}
          role="status"
          aria-live="polite"
        >
          <p className="text-base font-medium text-gray-900 dark:text-gray-100">
            {exportStatus.status === "pending" && "내보내기 준비 중..."}
            {exportStatus.status === "processing" && "내보내기 진행 중..."}
            {exportStatus.status === "completed" && "내보내기가 완료되었습니다!"}
            {exportStatus.status === "failed" && "내보내기에 실패했습니다."}
          </p>

          {/* Progress bar for processing */}
          {(exportStatus.status === "pending" || exportStatus.status === "processing") && (
            <div
              className="mt-3 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden"
              role="progressbar"
              aria-label="내보내기 진행률"
              aria-valuemin={0}
              aria-valuemax={100}
              aria-valuenow={exportStatus.status === "processing" ? 50 : 10}
            >
              <div
                className="h-full bg-primary-500 rounded-full animate-pulse"
                style={{
                  width: exportStatus.status === "processing" ? "60%" : "10%",
                }}
              />
            </div>
          )}

          {/* Download button */}
          {exportStatus.status === "completed" && (
            <Button
              variant="primary"
              size="default"
              onClick={handleDownload}
              aria-label="파일 다운로드"
              className="mt-3"
            >
              다운로드
            </Button>
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <p
          className="text-red-600 dark:text-red-400 text-base font-medium"
          role="alert"
        >
          {error}
        </p>
      )}
    </div>
  );
}
