import { create } from "zustand";

export type SessionUser = Record<string, unknown> | null;

type SessionState = {
  user: SessionUser;
  loading: boolean;
  error: string;
  setSession: (user: SessionUser) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string) => void;
  clearSession: () => void;
};

export const useSessionStore = create<SessionState>((set) => ({
  user: null,
  loading: true,
  error: "",
  setSession: (user) => set({ user, error: "" }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  clearSession: () => set({ user: null, error: "", loading: false }),
}));
