"use client";

import { useEffect, useMemo, useState } from "react";
import { useAuthContext } from "@/components/auth/auth-context";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { Button } from "@/components/ui/button";
import { createApiClient } from "@/lib/api-client";
import { useChatStore } from "@/stores/chat-store";
import { useUIStore } from "@/stores/ui-store";

type Expert = {
  id?: string | number;
  name?: string;
  expert_name?: string;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8003";
export default function HomePage() {
  const [experts, setExperts] = useState<Expert[]>([]);
  const [expertsError, setExpertsError] = useState("");

  const { user, isAuthenticated, loading, error, startLogin, logout } = useAuthContext();

  const chatPrompt = useChatStore((state) => state.prompt);
  const chatResult = useChatStore((state) => state.result);
  const chatError = useChatStore((state) => state.error);
  const chatLoading = useChatStore((state) => state.loading);
  const setChatPrompt = useChatStore((state) => state.setPrompt);
  const setChatResult = useChatStore((state) => state.setResult);
  const setChatError = useChatStore((state) => state.setError);
  const setChatLoading = useChatStore((state) => state.setLoading);
  const resetChat = useChatStore((state) => state.resetChat);

  const theme = useUIStore((state) => state.theme);
  const toggleTheme = useUIStore((state) => state.toggleTheme);

  const apiClient = useMemo(() => createApiClient({ baseUrl: apiBaseUrl }), []);

  const loadExperts = async () => {
    try {
      setExpertsError("");
      const data = await apiClient.get<{ experts?: Expert[] } | Expert[]>(
        "/api/main-site/api/experts?domain=expert-chat"
      );
      const list = Array.isArray((data as { experts?: Expert[] }).experts)
        ? (data as { experts: Expert[] }).experts
        : Array.isArray(data)
          ? data
          : [];
      setExperts(list);
    } catch (err) {
      setExpertsError(err instanceof Error ? err.message : "Could not fetch experts");
      setExperts([]);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      void loadExperts();
      return;
    }
    setExperts([]);
  }, [isAuthenticated]);

  useEffect(() => {
    if (typeof document !== "undefined") {
      document.documentElement.classList.toggle("dark", theme === "dark");
    }
  }, [theme]);

  const handleLogout = async () => {
    await logout();
    setExperts([]);
    resetChat();
  };

  const sendDemoChat = async () => {
    if (!chatPrompt.trim()) {
      return;
    }
    setChatLoading(true);
    setChatError("");

    try {
      const expertId = experts[0]?.id ?? null;
      const data = await apiClient.post<{
        message?: string;
        error?: string;
        response?: string;
      }>("/api/main-site/api/expert-chat", {
        message: chatPrompt.trim(),
        expert_id: expertId,
        domain: "expert-chat",
        conversation: [],
      });
      setChatResult(data.response || data.message || JSON.stringify(data));
    } catch (err) {
      setChatError(err instanceof Error ? err.message : "Chat request failed");
      setChatResult("");
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <main className="page">
      <aside className="shell-sidebar">
        <div className="shell-brand">Clever AI Tutor</div>
        <nav className="shell-nav">
          <button className="shell-nav-item" type="button">
            Dashboard
          </button>
          <button className="shell-nav-item" type="button">
            Sessions
          </button>
          <button className="shell-nav-item" type="button">
            Tutors
          </button>
          <button className="shell-nav-item" type="button">
            Knowledge Base
          </button>
        </nav>
      </aside>

      <section className="shell-main">
        <header className="shell-topbar">
          <div className="actions" style={{ display: "flex", gap: "8px", justifyContent: "flex-end" }}>
            <Button variant="secondary" onClick={toggleTheme}>
              {theme === "dark" ? "Light mode" : "Dark mode"}
            </Button>
            {isAuthenticated ? <Button onClick={handleLogout}>Logout</Button> : <Button onClick={startLogin}>Login with Main Site</Button>}
          </div>
        </header>

        <div className="shell-content">
          <ProtectedRoute>
            <header className="header">
              <div>
                <h1>Clever AI Tutor</h1>
                <p>Next.js + FastAPI. Auth via main site; experts and chat run locally. See ARCHITECTURE.md.</p>
              </div>
            </header>

            <section className="card">
              <h2>Session</h2>
              {loading ? <p>Loading session...</p> : null}
              {error ? <p className="error">Error: {error}</p> : null}
              {!loading && !user ? <p>Not logged in.</p> : null}
              {user ? <pre>{JSON.stringify({ user }, null, 2)}</pre> : null}
            </section>

            <section className="card">
              <h2>Experts (local API)</h2>
              {expertsError ? <p className="error">Error: {expertsError}</p> : null}
              {!expertsError ? <p>Loaded experts: {experts.length}</p> : null}
              {experts.length > 0 ? (
                <ul>
                  {experts.slice(0, 5).map((expert) => (
                    <li key={String(expert.id ?? expert.name ?? expert.expert_name)}>
                      {expert.name || expert.expert_name || "Unnamed expert"}
                    </li>
                  ))}
                </ul>
              ) : null}
            </section>

            <section className="card">
              <h2>Demo Expert Chat</h2>
              <textarea
                value={chatPrompt}
                onChange={(event) => setChatPrompt(event.target.value)}
                rows={3}
                placeholder="Ask a question..."
                disabled={!isAuthenticated || chatLoading}
              />
              <Button onClick={sendDemoChat} disabled={!isAuthenticated || chatLoading || !chatPrompt.trim()}>
                {chatLoading ? "Sending..." : "Send Prompt"}
              </Button>
              {chatError ? <p className="error">Error: {chatError}</p> : null}
              {chatResult ? <pre>{chatResult}</pre> : null}
            </section>
          </ProtectedRoute>
        </div>
      </section>
    </main>
  );
}
