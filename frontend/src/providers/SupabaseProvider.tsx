"use client";

import React, {
  createContext,
  useCallback,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import type { Session } from "@supabase/supabase-js";
import { createClient } from "@/lib/supabase/client";
import type { User } from "@/types/user";

interface SupabaseContextValue {
  session: Session | null;
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
 * Provides Supabase session state and user information to the app.
 */
export function SupabaseProvider({ children }: SupabaseProviderProps) {
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const supabase = createClient();

  const refreshUser = useCallback(async () => {
    try {
      const { data: { session: currentSession } } = await supabase.auth.getSession();
      setSession(currentSession);

      if (currentSession?.user) {
        // Map Supabase user to our User type
        const supabaseUser = currentSession.user;
        setUser({
          id: supabaseUser.id,
          email: supabaseUser.email || "",
          displayName: supabaseUser.user_metadata?.display_name || "",
          disabilityType: supabaseUser.user_metadata?.disability_type || "none",
          voiceSpeed: supabaseUser.user_metadata?.voice_speed || 1.0,
          voiceType: supabaseUser.user_metadata?.voice_type || "default",
          createdAt: supabaseUser.created_at,
          updatedAt: supabaseUser.updated_at || supabaseUser.created_at,
        });
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error("Failed to refresh user:", error);
    } finally {
      setIsLoading(false);
    }
  }, [supabase.auth]);

  useEffect(() => {
    refreshUser();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      if (session?.user) {
        const supabaseUser = session.user;
        setUser({
          id: supabaseUser.id,
          email: supabaseUser.email || "",
          displayName: supabaseUser.user_metadata?.display_name || "",
          disabilityType: supabaseUser.user_metadata?.disability_type || "none",
          voiceSpeed: supabaseUser.user_metadata?.voice_speed || 1.0,
          voiceType: supabaseUser.user_metadata?.voice_type || "default",
          createdAt: supabaseUser.created_at,
          updatedAt: supabaseUser.updated_at || supabaseUser.created_at,
        });
      } else {
        setUser(null);
      }
      setIsLoading(false);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [refreshUser, supabase.auth]);

  const signOut = useCallback(async () => {
    await supabase.auth.signOut();
    setSession(null);
    setUser(null);
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
    }
  }, [supabase.auth]);

  return (
    <SupabaseContext.Provider
      value={{ session, user, isLoading, signOut, refreshUser }}
    >
      {children}
    </SupabaseContext.Provider>
  );
}
