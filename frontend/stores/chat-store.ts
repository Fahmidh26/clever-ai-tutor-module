import { create } from "zustand";

type ChatState = {
  prompt: string;
  result: string;
  error: string;
  loading: boolean;
  setPrompt: (prompt: string) => void;
  setResult: (result: string) => void;
  setError: (error: string) => void;
  setLoading: (loading: boolean) => void;
  resetChat: () => void;
};

export const useChatStore = create<ChatState>((set) => ({
  prompt: "Explain Newton second law with a real-world example.",
  result: "",
  error: "",
  loading: false,
  setPrompt: (prompt) => set({ prompt }),
  setResult: (result) => set({ result }),
  setError: (error) => set({ error }),
  setLoading: (loading) => set({ loading }),
  resetChat: () => set({ result: "", error: "", loading: false }),
}));
