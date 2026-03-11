"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { ApiError, createApiClient } from "@/lib/api-client";
import { useAuthStore } from "@/stores/auth-store";
import { useSessionStore } from "@/stores/session-store";

type SessionPayload = {
  user: Record<string, unknown> | null;
  access_token: string;
};

type AuthContextValue = {
  user: Record<string, unknown> | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string;
  apiBaseUrl: string;
  startLogin: () => void;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8003";
const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(null);

  const user = useSessionStore((state) => state.user);
  const loading = useSessionStore((state) => state.loading);
  const error = useSessionStore((state) => state.error);
  const setSessionUser = useSessionStore((state) => state.setSession);
  const setSessionLoading = useSessionStore((state) => state.setLoading);
  const setSessionError = useSessionStore((state) => state.setError);
  const clearSessionStore = useSessionStore((state) => state.clearSession);

  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const setAuthenticated = useAuthStore((state) => state.setAuthenticated);
  const clearAuth = useAuthStore((state) => state.clearAuth);

  const clearAuthState = useCallback(() => {
    setAccessToken(null);
    clearAuth();
    clearSessionStore();
  }, [clearAuth, clearSessionStore]);

  const apiClient = useMemo(
    () =>
      createApiClient({
        baseUrl: apiBaseUrl,
        onUnauthorized: clearAuthState,
      }),
    [clearAuthState]
  );

  const refreshSession = useCallback(async () => {
    try {
      setSessionLoading(true);
      setSessionError("");
      const data = await apiClient.get<SessionPayload>("/api/me");
      setAccessToken(data.access_token);
      setAuthenticated(data.access_token);
      setSessionUser(data.user);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        clearAuthState();
        return;
      }
      setSessionError(err instanceof Error ? err.message : "Unexpected error while loading session");
    } finally {
      setSessionLoading(false);
    }
  }, [apiClient, clearAuthState, setAuthenticated, setSessionError, setSessionLoading, setSessionUser]);

  useEffect(() => {
    void refreshSession();
  }, [refreshSession]);

  const startLogin = useCallback(() => {
    window.location.href = `${apiBaseUrl}/oauth/login`;
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiClient.post<{ ok: boolean }>("/api/logout");
    } finally {
      clearAuthState();
    }
  }, [apiClient, clearAuthState]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      accessToken,
      isAuthenticated,
      loading,
      error,
      apiBaseUrl,
      startLogin,
      logout,
      refreshSession,
    }),
    [accessToken, error, isAuthenticated, loading, logout, refreshSession, startLogin, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuthContext must be used inside AuthProvider");
  }
  return context;
}

