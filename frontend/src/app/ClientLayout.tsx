"use client";

import type { ReactNode } from "react";
import { SkipLink } from "@/components/ui/SkipLink";
import { AnnouncerProvider } from "@/providers/AnnouncerProvider";
import { SupabaseProvider } from "@/providers/SupabaseProvider";
import { ThemeProvider } from "@/providers/ThemeProvider";
import { VoiceProvider } from "@/providers/VoiceProvider";
import { Header } from "@/components/layout/Header";
import { Navigation } from "@/components/layout/Navigation";
import { Footer } from "@/components/layout/Footer";

interface ClientLayoutProps {
  children: ReactNode;
}

/**
 * Client-side layout wrapper.
 * Provides all context providers and layout shell (header, nav, footer).
 */
export function ClientLayout({ children }: ClientLayoutProps) {
  return (
    <ThemeProvider>
      <SupabaseProvider>
        <AnnouncerProvider>
          <VoiceProvider>
            <SkipLink />
            <Header />
            <Navigation />
            <main
              id="main-content"
              className="flex-1 w-full max-w-7xl mx-auto px-6 py-8"
              tabIndex={-1}
              role="main"
            >
              {children}
            </main>
            <Footer />
          </VoiceProvider>
        </AnnouncerProvider>
      </SupabaseProvider>
    </ThemeProvider>
  );
}
