import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import type { BookGenre, BookStatus, ChapterStatus } from "@/types/book";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format a date string to a Korean-friendly format.
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(date);
}

/**
 * Format a date string to a relative time (e.g., "3일 전").
 */
export function formatRelativeDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMinutes = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMinutes < 1) return "방금 전";
  if (diffMinutes < 60) return `${diffMinutes}분 전`;
  if (diffHours < 24) return `${diffHours}시간 전`;
  if (diffDays < 30) return `${diffDays}일 전`;
  return formatDate(dateString);
}

/**
 * Format word count with Korean unit.
 */
export function formatWordCount(count: number): string {
  if (count >= 10000) {
    return `${(count / 10000).toFixed(1)}만 자`;
  }
  if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}천 자`;
  }
  return `${count}자`;
}

/**
 * Korean labels for book genres.
 */
export function genreLabel(genre: BookGenre): string {
  const labels: Record<BookGenre, string> = {
    essay: "에세이",
    novel: "소설",
    poem: "시",
    autobiography: "자서전",
    children: "동화",
    non_fiction: "논픽션",
    other: "기타",
  };
  return labels[genre];
}

/**
 * Korean labels for book statuses.
 */
export function statusLabel(status: BookStatus): string {
  const labels: Record<BookStatus, string> = {
    draft: "초안",
    writing: "집필 중",
    editing: "편집 중",
    designing: "디자인 중",
    completed: "완성됨",
    published: "출판 완료",
  };
  return labels[status];
}

/**
 * Korean labels for chapter statuses.
 */
export function chapterStatusLabel(status: ChapterStatus): string {
  const labels: Record<ChapterStatus, string> = {
    draft: "초안",
    writing: "작성 중",
    completed: "완료",
    editing: "편집 중",
    finalized: "최종 확인",
  };
  return labels[status];
}

/**
 * Generate a unique ID (for client-side temporary IDs).
 */
export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

/**
 * Clamp a number between min and max.
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}
