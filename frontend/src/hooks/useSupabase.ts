"use client";

import { useContext } from "react";
import { SupabaseContext } from "@/providers/SupabaseProvider";

/**
 * Hook to access Supabase auth state and client.
 *
 * @example
 * const { user, session, isLoading, signOut } = useSupabase();
 */
export function useSupabase() {
  const context = useContext(SupabaseContext);
  if (!context) {
    throw new Error("useSupabase must be used within a SupabaseProvider");
  }
  return context;
}
