import { create } from "zustand";

type AuthState = {
  isAuthenticated: boolean;
  accessToken: string | null;
  setAuthenticated: (accessToken: string) => void;
  clearAuth: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  accessToken: null,
  setAuthenticated: (accessToken) => set({ isAuthenticated: true, accessToken }),
  clearAuth: () => set({ isAuthenticated: false, accessToken: null }),
}));
