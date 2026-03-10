import { create } from "zustand";

type ThemeMode = "light" | "dark";

type UIState = {
  theme: ThemeMode;
  toggleTheme: () => void;
  setTheme: (theme: ThemeMode) => void;
};

export const useUIStore = create<UIState>((set, get) => ({
  theme: "light",
  toggleTheme: () => {
    const nextTheme = get().theme === "light" ? "dark" : "light";
    set({ theme: nextTheme });
  },
  setTheme: (theme) => set({ theme }),
}));
