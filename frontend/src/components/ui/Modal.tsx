"use client";

import React, { useCallback, useEffect, useRef, type ReactNode } from "react";
import { useAnnouncer } from "@/hooks/useAnnouncer";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  /** aria-describedby content */
  description?: string;
  children: ReactNode;
}

/**
 * Accessible modal dialog with focus trap, Escape to close,
 * and screen reader announcements.
 */
export function Modal({ isOpen, onClose, title, description, children }: ModalProps) {
  const { announceAssertive } = useAnnouncer();
  const dialogRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  // Save and restore focus
  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement as HTMLElement;
      announceAssertive(`대화 상자가 열렸습니다: ${title}`);

      // Focus the dialog
      requestAnimationFrame(() => {
        dialogRef.current?.focus();
      });
    }

    return () => {
      if (previousFocusRef.current && !isOpen) {
        previousFocusRef.current.focus();
      }
    };
  }, [isOpen, title, announceAssertive]);

  // Focus trap
  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        return;
      }

      if (event.key === "Tab") {
        const dialog = dialogRef.current;
        if (!dialog) return;

        const focusableElements = dialog.querySelectorAll<HTMLElement>(
          'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
        );

        if (focusableElements.length === 0) {
          event.preventDefault();
          return;
        }

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (event.shiftKey) {
          if (document.activeElement === firstElement) {
            event.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            event.preventDefault();
            firstElement.focus();
          }
        }
      }
    },
    [onClose]
  );

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      role="presentation"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Dialog */}
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-label={title}
        aria-describedby={description ? "modal-description" : undefined}
        tabIndex={-1}
        onKeyDown={handleKeyDown}
        className="
          relative z-10
          w-full max-w-lg mx-4
          bg-white dark:bg-gray-900
          rounded-2xl shadow-2xl
          p-8
          focus:outline-none
          max-h-[90vh] overflow-y-auto
        "
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {title}
          </h2>
          <button
            onClick={onClose}
            aria-label="대화 상자 닫기"
            className="
              p-2 min-h-touch min-w-touch
              flex items-center justify-center
              text-gray-500 hover:text-gray-700
              dark:text-gray-400 dark:hover:text-gray-200
              rounded-lg
              focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-yellow-400
            "
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Description */}
        {description && (
          <p id="modal-description" className="text-gray-600 dark:text-gray-400 mb-4">
            {description}
          </p>
        )}

        {/* Content */}
        {children}
      </div>
    </div>
  );
}
