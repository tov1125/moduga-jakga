"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useRef, useCallback } from "react";

interface NavItem {
  href: string;
  label: string;
}

const navItems: NavItem[] = [
  { href: "/dashboard", label: "대시보드" },
  { href: "/write", label: "글쓰기" },
  { href: "/settings", label: "설정" },
];

/**
 * Main navigation component.
 * Uses arrow key navigation and aria-current for the active page.
 */
export function Navigation() {
  const pathname = usePathname();
  const navRef = useRef<HTMLElement>(null);

  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLElement>) => {
      if (!navRef.current) return;

      const links = navRef.current.querySelectorAll<HTMLAnchorElement>("a");
      const linkArray = Array.from(links);
      const currentIndex = linkArray.findIndex((link) => link === document.activeElement);

      let nextIndex: number | null = null;

      if (event.key === "ArrowRight" || event.key === "ArrowDown") {
        event.preventDefault();
        nextIndex = currentIndex < linkArray.length - 1 ? currentIndex + 1 : 0;
      }

      if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
        event.preventDefault();
        nextIndex = currentIndex > 0 ? currentIndex - 1 : linkArray.length - 1;
      }

      if (event.key === "Home") {
        event.preventDefault();
        nextIndex = 0;
      }

      if (event.key === "End") {
        event.preventDefault();
        nextIndex = linkArray.length - 1;
      }

      if (nextIndex !== null) {
        linkArray[nextIndex].focus();
      }
    },
    []
  );

  return (
    <nav
      ref={navRef}
      aria-label="주요 탐색"
      className="
        w-full bg-gray-50 dark:bg-gray-800
        border-b border-gray-200 dark:border-gray-700
        px-6 py-2
      "
      onKeyDown={handleKeyDown}
    >
      <div className="max-w-7xl mx-auto">
        <ul className="flex items-center gap-2" role="menubar">
          {navItems.map((item) => {
            const isActive =
              pathname === item.href || pathname.startsWith(item.href + "/");

            return (
              <li key={item.href} role="none">
                <Link
                  href={item.href}
                  role="menuitem"
                  aria-current={isActive ? "page" : undefined}
                  className={`
                    inline-flex items-center
                    px-4 py-2.5 min-h-touch
                    rounded-lg text-base font-medium
                    transition-colors duration-150
                    focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-yellow-400
                    ${
                      isActive
                        ? "bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200"
                        : "text-gray-700 hover:bg-gray-200 dark:text-gray-300 dark:hover:bg-gray-700"
                    }
                  `}
                >
                  {item.label}
                  {isActive && <span className="sr-only"> (현재 페이지)</span>}
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
    </nav>
  );
}
