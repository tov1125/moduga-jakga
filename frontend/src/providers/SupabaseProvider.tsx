"use client";

import React, {
  createContext,
  useCallback,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import type { User } from "@/types/user";
import { auth } from "@/lib/api";

interface SupabaseContextValue {
  session: null;
  user: User | null;
  isLoading: boolean;
  signOut: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

export const SupabaseContext = createContext<SupabaseContextValue | null>(null);

interface SupabaseProviderProps {
  children: ReactNode;
}

/**
 * Provides auth state and user information to the app.
 * Uses Backend JWT stored in localStorage + /auth/me endpoint.
 */
export function SupabaseProvider({ children }: SupabaseProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    if (typeof window === "undefined") {
      setIsLoading(false);
      return;
    }

    const token = localStorage.getItem("access_token");
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    try {
      const response = await auth.me();
      setUser(response.data);
    } catch {
      localStorage.removeItem("access_token");
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const signOut = useCallback(async () => {
    try {
      await auth.logout();
    } catch {
      // logout 실패해도 로컬 상태는 정리
    }
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
    }
    setUser(null);
  }, []);

  return (
    <SupabaseContext.Provider
      value={{ session: null, user, isLoading, signOut, refreshUser }}
    >
      {children}
    </SupabaseContext.Provider>
  );
}
