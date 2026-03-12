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
  tagline?: string;
  subject_expertise?: unknown;
};

type KnowledgeBase = {
  id: number;
  name: string;
  description?: string | null;
  subject?: string | null;
  grade_level?: number | null;
  visibility?: string;
  status?: string;
  document_count?: number;
};

type KBDocument = {
  id: number;
  kb_id: number;
  filename: string;
  file_type?: string | null;
  file_size?: number;
  status?: string;
  error_message?: string | null;
  created_at?: string | null;
};

type TeacherClass = {
  id: number;
  name: string;
  subject?: string | null;
  grade_level?: number | null;
  invite_code?: string | null;
  roster_count?: number;
};

type RosterEntry = {
  enrollment_id: number;
  student_id: number;
  display_name?: string | null;
  grade_level?: number | null;
  status?: string;
};

type TutorMode = {
  id: string;
  label: string;
};

type TutorSessionSummary = {
  id: number;
  persona_id: number;
  persona_name?: string;
  subject?: string | null;
  topic?: string | null;
  mode?: string;
  created_at?: string | null;
};

type TutorSessionMessage = {
  id?: number;
  role: "user" | "assistant";
  content: string;
  mode?: string;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8003";
export default function HomePage() {
  const [experts, setExperts] = useState<Expert[]>([]);
  const [expertsError, setExpertsError] = useState("");
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [kbLoading, setKbLoading] = useState(false);
  const [kbError, setKbError] = useState("");
  const [kbName, setKbName] = useState("");
  const [kbSubject, setKbSubject] = useState("");
  const [kbDescription, setKbDescription] = useState("");
  const [selectedKbId, setSelectedKbId] = useState<number | null>(null);
  const [documents, setDocuments] = useState<KBDocument[]>([]);
  const [docsLoading, setDocsLoading] = useState(false);
  const [docsError, setDocsError] = useState("");
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [processingQueued, setProcessingQueued] = useState(false);
  const [previewDocId, setPreviewDocId] = useState<number | null>(null);
  const [previewText, setPreviewText] = useState("");
  const [classes, setClasses] = useState<TeacherClass[]>([]);
  const [classesError, setClassesError] = useState("");
  const [className, setClassName] = useState("");
  const [classSubject, setClassSubject] = useState("");
  const [selectedClassId, setSelectedClassId] = useState<number | null>(null);
  const [roster, setRoster] = useState<RosterEntry[]>([]);
  const [studentIdInput, setStudentIdInput] = useState("");
  const [classBusy, setClassBusy] = useState(false);
  const [modes, setModes] = useState<TutorMode[]>([]);
  const [selectedMode, setSelectedMode] = useState("teach_me");
  const [selectedExpertId, setSelectedExpertId] = useState<number | null>(null);
  const [sessions, setSessions] = useState<TutorSessionSummary[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<number | null>(null);
  const [chatMessages, setChatMessages] = useState<TutorSessionMessage[]>([]);
  const [sessionLoading, setSessionLoading] = useState(false);
  const [isOnline, setIsOnline] = useState(true);
  const [subjectInput, setSubjectInput] = useState("");
  const [topicInput, setTopicInput] = useState("");

  const { user, role, isAuthenticated, loading, error, startLogin, logout } = useAuthContext();

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
  const isTeacherRole = role === "teacher" || role === "admin";

  const loadExperts = async () => {
    try {
      setExpertsError("");
      const data = await apiClient.get<{ experts?: Expert[] } | Expert[]>(
        "/api/experts?domain=expert-chat"
      );
      const list = Array.isArray((data as { experts?: Expert[] }).experts)
        ? (data as { experts: Expert[] }).experts
        : Array.isArray(data)
          ? data
          : [];
      setExperts(list);
      if (!selectedExpertId && list.length > 0) {
        const firstId = Number(list[0].id);
        if (Number.isInteger(firstId)) {
          setSelectedExpertId(firstId);
        }
      }
    } catch (err) {
      setExpertsError(err instanceof Error ? err.message : "Could not fetch experts");
      setExperts([]);
    }
  };

  const loadModes = async () => {
    try {
      const data = await apiClient.get<{ modes?: TutorMode[] }>("/api/tutor/modes");
      const list = Array.isArray(data.modes) ? data.modes : [];
      setModes(list);
      if (list.length > 0 && !list.some((m) => m.id === selectedMode)) {
        setSelectedMode(list[0].id);
      }
    } catch {
      setModes([]);
    }
  };

  const loadSessions = async () => {
    try {
      setSessionLoading(true);
      const data = await apiClient.get<{ sessions?: TutorSessionSummary[] }>("/api/tutor/sessions?limit=50");
      const list = Array.isArray(data.sessions) ? data.sessions : [];
      setSessions(list);
      if (list.length > 0 && selectedSessionId === null) {
        setSelectedSessionId(list[0].id);
      }
    } catch (err) {
      setChatError(err instanceof Error ? err.message : "Could not load sessions");
      setSessions([]);
    } finally {
      setSessionLoading(false);
    }
  };

  const loadSessionDetail = async (sessionId: number) => {
    try {
      setSessionLoading(true);
      const data = await apiClient.get<{ session?: TutorSessionSummary; messages?: TutorSessionMessage[] }>(
        `/api/tutor/sessions/${sessionId}`
      );
      const messages = Array.isArray(data.messages) ? data.messages : [];
      setChatMessages(
        messages.map((m) => ({
          id: m.id,
          role: m.role === "assistant" ? "assistant" : "user",
          content: String(m.content || ""),
          mode: m.mode,
        }))
      );
      if (data.session?.persona_id) {
        setSelectedExpertId(Number(data.session.persona_id));
      }
      if (data.session?.mode) {
        setSelectedMode(data.session.mode);
      }
    } catch (err) {
      setChatError(err instanceof Error ? err.message : "Could not load session messages");
      setChatMessages([]);
    } finally {
      setSessionLoading(false);
    }
  };

  const loadKnowledgeBases = async () => {
    if (!isTeacherRole) {
      setKnowledgeBases([]);
      setSelectedKbId(null);
      return;
    }
    try {
      setKbLoading(true);
      setKbError("");
      const data = await apiClient.get<{ knowledge_bases?: KnowledgeBase[] }>("/api/teacher/kb");
      const list = Array.isArray(data.knowledge_bases) ? data.knowledge_bases : [];
      setKnowledgeBases(list);
      if (!selectedKbId && list.length > 0) {
        setSelectedKbId(list[0].id);
      }
      if (selectedKbId && !list.some((kb) => kb.id === selectedKbId)) {
        setSelectedKbId(list.length > 0 ? list[0].id : null);
      }
    } catch (err) {
      setKbError(err instanceof Error ? err.message : "Could not fetch knowledge bases");
      setKnowledgeBases([]);
    } finally {
      setKbLoading(false);
    }
  };

  const loadClasses = async () => {
    if (!isTeacherRole) {
      setClasses([]);
      setSelectedClassId(null);
      return;
    }
    try {
      setClassesError("");
      const data = await apiClient.get<{ classes?: TeacherClass[] }>("/api/teacher/classes");
      const list = Array.isArray(data.classes) ? data.classes : [];
      setClasses(list);
      if (!selectedClassId && list.length > 0) {
        setSelectedClassId(list[0].id);
      }
      if (selectedClassId && !list.some((cls) => cls.id === selectedClassId)) {
        setSelectedClassId(list.length > 0 ? list[0].id : null);
      }
    } catch (err) {
      setClassesError(err instanceof Error ? err.message : "Could not load classes");
      setClasses([]);
    }
  };

  const loadRoster = async (classId: number) => {
    try {
      setClassesError("");
      const data = await apiClient.get<{ roster?: RosterEntry[] }>(`/api/teacher/classes/${classId}`);
      setRoster(Array.isArray(data.roster) ? data.roster : []);
    } catch (err) {
      setClassesError(err instanceof Error ? err.message : "Could not load roster");
      setRoster([]);
    }
  };

  const loadDocuments = async (kbId: number) => {
    try {
      setDocsLoading(true);
      setDocsError("");
      const data = await apiClient.get<{ documents?: KBDocument[] }>(`/api/teacher/kb/${kbId}/documents`);
      setDocuments(Array.isArray(data.documents) ? data.documents : []);
    } catch (err) {
      setDocsError(err instanceof Error ? err.message : "Could not fetch documents");
      setDocuments([]);
    } finally {
      setDocsLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      void loadExperts();
      void loadModes();
      void loadSessions();
      void loadKnowledgeBases();
      void loadClasses();
      return;
    }
    setExperts([]);
    setKnowledgeBases([]);
    setSelectedKbId(null);
    setClasses([]);
    setSelectedClassId(null);
    setRoster([]);
    setSessions([]);
    setSelectedSessionId(null);
    setChatMessages([]);
  }, [isAuthenticated]);

  useEffect(() => {
    if (isAuthenticated && isTeacherRole) {
      void loadKnowledgeBases();
      void loadClasses();
    }
  }, [isAuthenticated, isTeacherRole]);

  useEffect(() => {
    if (selectedKbId && isAuthenticated && isTeacherRole) {
      void loadDocuments(selectedKbId);
      setPreviewDocId(null);
      setPreviewText("");
      return;
    }
    setDocuments([]);
  }, [selectedKbId, isAuthenticated, isTeacherRole]);

  useEffect(() => {
    if (selectedClassId && isAuthenticated && isTeacherRole) {
      void loadRoster(selectedClassId);
      return;
    }
    setRoster([]);
  }, [selectedClassId, isAuthenticated, isTeacherRole]);

  useEffect(() => {
    if (!isAuthenticated || selectedSessionId === null) {
      return;
    }
    void loadSessionDetail(selectedSessionId);
  }, [selectedSessionId, isAuthenticated]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    const setOnline = () => setIsOnline(navigator.onLine);
    setOnline();
    window.addEventListener("online", setOnline);
    window.addEventListener("offline", setOnline);
    return () => {
      window.removeEventListener("online", setOnline);
      window.removeEventListener("offline", setOnline);
    };
  }, []);

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

  const startSessionIfNeeded = async (): Promise<number | null> => {
    if (selectedSessionId !== null) {
      return selectedSessionId;
    }
    if (!selectedExpertId) {
      setChatError("Select a tutor first");
      return null;
    }
    try {
      const created = await apiClient.post<{ session?: { id: number } }>("/api/tutor/sessions", {
        persona_id: selectedExpertId,
        subject: subjectInput.trim() || undefined,
        topic: topicInput.trim() || undefined,
        mode: selectedMode,
      });
      const id = created.session?.id ?? null;
      if (id !== null) {
        setSelectedSessionId(id);
        await loadSessions();
      }
      return id;
    } catch (err) {
      setChatError(err instanceof Error ? err.message : "Failed to create session");
      return null;
    }
  };

  const sendStreamChat = async () => {
    if (!chatPrompt.trim()) {
      return;
    }
    if (!isOnline) {
      setChatError("You are offline. Reconnect and try again.");
      return;
    }
    setChatLoading(true);
    setChatError("");
    setChatResult("");
    const userContent = chatPrompt.trim();
    const nextMessages = [...chatMessages, { role: "user" as const, content: userContent }];
    setChatMessages([...nextMessages, { role: "assistant" as const, content: "" }]);

    const sessionId = await startSessionIfNeeded();
    if (sessionId === null) {
      setChatLoading(false);
      return;
    }
    try {
      const response = await fetch(`${apiBaseUrl}/api/expert-chat/stream`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
        body: JSON.stringify({
          message: userContent,
          expert_id: selectedExpertId,
          session_id: sessionId,
          mode: selectedMode,
          conversation: nextMessages.map((m) => ({ role: m.role, content: m.content })),
          kb_id: selectedKbId ?? undefined,
        }),
      });
      if (!response.ok || !response.body) {
        const text = await response.text();
        throw new Error(text || `Chat request failed (${response.status})`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          break;
        }
        buffer += decoder.decode(value, { stream: true });

        let boundary = buffer.indexOf("\n\n");
        while (boundary >= 0) {
          const block = buffer.slice(0, boundary);
          buffer = buffer.slice(boundary + 2);
          boundary = buffer.indexOf("\n\n");

          const lines = block.split("\n");
          const eventLine = lines.find((l) => l.startsWith("event: "));
          const dataLine = lines.find((l) => l.startsWith("data: "));
          const event = eventLine ? eventLine.replace("event: ", "").trim() : "message";
          const dataRaw = dataLine ? dataLine.replace("data: ", "") : "";
          let payload: Record<string, unknown> = {};
          try {
            payload = dataRaw ? (JSON.parse(dataRaw) as Record<string, unknown>) : {};
          } catch {
            payload = {};
          }

          if (event === "token") {
            const token = String(payload.content || "");
            setChatMessages((prev) => {
              if (prev.length === 0) {
                return [{ role: "assistant", content: token }];
              }
              const copy = [...prev];
              const lastIdx = copy.length - 1;
              const last = copy[lastIdx];
              if (last.role !== "assistant") {
                copy.push({ role: "assistant", content: token });
                return copy;
              }
              copy[lastIdx] = { ...last, content: `${last.content}${token}` };
              return copy;
            });
          } else if (event === "error") {
            const message = String(payload.message || "Streaming error");
            throw new Error(message);
          } else if (event === "stream_end") {
            const assistantText = String(
              (chatMessages.length > 0 ? chatMessages[chatMessages.length - 1]?.content : "") || ""
            );
            if (assistantText) {
              setChatResult(assistantText);
            }
          }
        }
      }
      setChatPrompt("");
      await loadSessions();
    } catch (err) {
      setChatError(err instanceof Error ? err.message : "Chat request failed");
      setChatResult("");
    } finally {
      setChatLoading(false);
    }
  };

  const createKnowledgeBase = async () => {
    if (!kbName.trim()) {
      setKbError("KB name is required");
      return;
    }
    try {
      setKbError("");
      await apiClient.post("/api/teacher/kb", {
        name: kbName.trim(),
        subject: kbSubject.trim() || undefined,
        description: kbDescription.trim() || undefined,
        visibility: "private",
      });
      setKbName("");
      setKbSubject("");
      setKbDescription("");
      await loadKnowledgeBases();
    } catch (err) {
      setKbError(err instanceof Error ? err.message : "Failed to create knowledge base");
    }
  };

  const uploadDocument = async () => {
    if (!selectedKbId || !uploadFile) {
      setDocsError("Select a KB and file first");
      return;
    }
    try {
      setUploading(true);
      setDocsError("");
      const form = new FormData();
      form.append("file", uploadFile);
      const response = await fetch(`${apiBaseUrl}/api/teacher/kb/${selectedKbId}/documents/upload`, {
        method: "POST",
        credentials: "include",
        body: form,
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(payload?.error || payload?.message || `Upload failed (${response.status})`);
      }
      setUploadFile(null);
      await loadDocuments(selectedKbId);
      await loadKnowledgeBases();
    } catch (err) {
      setDocsError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const processQueuedDocuments = async () => {
    if (!selectedKbId) {
      return;
    }
    try {
      setProcessingQueued(true);
      setDocsError("");
      await apiClient.post(`/api/teacher/kb/${selectedKbId}/documents/process-queued?limit=10`);
      await loadDocuments(selectedKbId);
      await loadKnowledgeBases();
    } catch (err) {
      setDocsError(err instanceof Error ? err.message : "Failed to process queued documents");
    } finally {
      setProcessingQueued(false);
    }
  };

  const previewDocument = async (docId: number) => {
    if (!selectedKbId) {
      return;
    }
    try {
      setPreviewDocId(docId);
      const data = await apiClient.get<{ document?: { preview?: string | null } }>(
        `/api/teacher/kb/${selectedKbId}/documents/${docId}/preview`
      );
      setPreviewText(data.document?.preview || "No preview available.");
    } catch (err) {
      setPreviewText(err instanceof Error ? err.message : "Failed to load preview");
    }
  };

  const deleteDocument = async (docId: number) => {
    if (!selectedKbId) {
      return;
    }
    try {
      await apiClient.del(`/api/teacher/kb/${selectedKbId}/documents/${docId}`);
      if (previewDocId === docId) {
        setPreviewDocId(null);
        setPreviewText("");
      }
      await loadDocuments(selectedKbId);
      await loadKnowledgeBases();
    } catch (err) {
      setDocsError(err instanceof Error ? err.message : "Failed to delete document");
    }
  };

  const createClass = async () => {
    if (!className.trim()) {
      setClassesError("Class name is required");
      return;
    }
    try {
      setClassBusy(true);
      setClassesError("");
      await apiClient.post("/api/teacher/classes", {
        name: className.trim(),
        subject: classSubject.trim() || undefined,
      });
      setClassName("");
      setClassSubject("");
      await loadClasses();
    } catch (err) {
      setClassesError(err instanceof Error ? err.message : "Failed to create class");
    } finally {
      setClassBusy(false);
    }
  };

  const enrollStudent = async () => {
    if (!selectedClassId) {
      return;
    }
    const sid = Number(studentIdInput);
    if (!Number.isInteger(sid) || sid <= 0) {
      setClassesError("Enter a valid student ID");
      return;
    }
    try {
      setClassBusy(true);
      setClassesError("");
      await apiClient.post(`/api/teacher/classes/${selectedClassId}/enroll`, { student_id: sid });
      setStudentIdInput("");
      await loadRoster(selectedClassId);
      await loadClasses();
    } catch (err) {
      setClassesError(err instanceof Error ? err.message : "Failed to enroll student");
    } finally {
      setClassBusy(false);
    }
  };

  const removeEnrollment = async (enrollmentId: number) => {
    if (!selectedClassId) {
      return;
    }
    try {
      setClassBusy(true);
      setClassesError("");
      await apiClient.del(`/api/teacher/classes/${selectedClassId}/enrollments/${enrollmentId}`);
      await loadRoster(selectedClassId);
      await loadClasses();
    } catch (err) {
      setClassesError(err instanceof Error ? err.message : "Failed to remove enrollment");
    } finally {
      setClassBusy(false);
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
              <h2>Tutor Workspace</h2>
              {!isOnline ? <p className="error">Offline mode: connect to send messages.</p> : null}
              <div style={{ display: "grid", gap: "8px", marginBottom: "10px" }}>
                <select
                  value={selectedExpertId ?? ""}
                  onChange={(event) => setSelectedExpertId(Number(event.target.value))}
                  disabled={experts.length === 0}
                >
                  {experts.map((expert) => (
                    <option key={String(expert.id)} value={Number(expert.id)}>
                      {expert.name || expert.expert_name || "Unnamed tutor"}
                    </option>
                  ))}
                </select>
                <select value={selectedMode} onChange={(event) => setSelectedMode(event.target.value)}>
                  {modes.map((mode) => (
                    <option key={mode.id} value={mode.id}>
                      {mode.label}
                    </option>
                  ))}
                </select>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
                  <input
                    value={subjectInput}
                    onChange={(event) => setSubjectInput(event.target.value)}
                    placeholder="Subject (optional)"
                  />
                  <input
                    value={topicInput}
                    onChange={(event) => setTopicInput(event.target.value)}
                    placeholder="Topic (optional)"
                  />
                </div>
                <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                  <Button
                    variant="secondary"
                    onClick={async () => {
                      const id = await startSessionIfNeeded();
                      if (id !== null) {
                        setSelectedSessionId(id);
                      }
                    }}
                    disabled={chatLoading || !selectedExpertId}
                  >
                    Start Session
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setSelectedSessionId(null);
                      setChatMessages([]);
                      setChatError("");
                    }}
                    disabled={chatLoading}
                  >
                    New Session Draft
                  </Button>
                </div>
              </div>

              <div className="workspace-grid">
                <div style={{ border: "1px solid var(--border)", borderRadius: "8px", padding: "8px" }}>
                  <strong>Session History</strong>
                  {sessionLoading ? <p>Loading...</p> : null}
                  {sessions.length === 0 ? <p>No sessions yet.</p> : null}
                  <div style={{ display: "grid", gap: "6px", marginTop: "8px", maxHeight: "340px", overflow: "auto" }}>
                    {sessions.map((session) => (
                      <button
                        key={session.id}
                        type="button"
                        className="shell-nav-item"
                        style={{
                          background:
                            selectedSessionId === session.id ? "var(--secondary)" : "var(--background)",
                        }}
                        onClick={() => setSelectedSessionId(session.id)}
                      >
                        <div>#{session.id} {session.persona_name || "Tutor"}</div>
                        <div style={{ fontSize: "12px", opacity: 0.8 }}>
                          {session.subject || "General"} {session.topic ? `· ${session.topic}` : ""}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                <div style={{ border: "1px solid var(--border)", borderRadius: "8px", padding: "10px" }}>
                  <div style={{ maxHeight: "340px", overflow: "auto", display: "grid", gap: "8px", marginBottom: "10px" }}>
                    {chatMessages.length === 0 ? <p>Start a conversation.</p> : null}
                    {chatMessages.map((message, index) => (
                      <div
                        key={`${message.role}-${index}`}
                        style={{
                          border: "1px solid var(--border)",
                          borderRadius: "8px",
                          padding: "10px",
                          background: message.role === "assistant" ? "var(--card)" : "var(--secondary)",
                        }}
                      >
                        <strong>{message.role === "assistant" ? "Tutor" : "You"}</strong>
                        <pre style={{ marginTop: "6px", whiteSpace: "pre-wrap" }}>{message.content}</pre>
                      </div>
                    ))}
                  </div>
                  <textarea
                    value={chatPrompt}
                    onChange={(event) => setChatPrompt(event.target.value)}
                    rows={3}
                    placeholder="Ask your tutor..."
                    disabled={!isAuthenticated || chatLoading}
                  />
                  <Button onClick={sendStreamChat} disabled={!isAuthenticated || chatLoading || !chatPrompt.trim()}>
                    {chatLoading ? "Streaming..." : "Send Message"}
                  </Button>
                  {chatError ? <p className="error">Error: {chatError}</p> : null}
                  {chatResult ? <p style={{ marginTop: "6px", fontSize: "12px", opacity: 0.8 }}>Latest response captured.</p> : null}
                </div>
              </div>
            </section>

            <section className="card">
              <h2>Knowledge Base Manager</h2>
              {!isTeacherRole ? <p>Teacher/admin role required for KB management.</p> : null}
              {isTeacherRole ? (
                <>
                  <div style={{ display: "grid", gap: "8px", marginBottom: "12px" }}>
                    <input
                      value={kbName}
                      onChange={(event) => setKbName(event.target.value)}
                      placeholder="Knowledge base name"
                    />
                    <input
                      value={kbSubject}
                      onChange={(event) => setKbSubject(event.target.value)}
                      placeholder="Subject (optional)"
                    />
                    <textarea
                      value={kbDescription}
                      onChange={(event) => setKbDescription(event.target.value)}
                      rows={2}
                      placeholder="Description (optional)"
                    />
                    <Button onClick={createKnowledgeBase} disabled={!kbName.trim() || kbLoading}>
                      {kbLoading ? "Working..." : "Create Knowledge Base"}
                    </Button>
                  </div>

                  {kbError ? <p className="error">Error: {kbError}</p> : null}
                  <p>My KBs: {knowledgeBases.length}</p>
                  {knowledgeBases.length > 0 ? (
                    <select
                      value={selectedKbId ?? ""}
                      onChange={(event) => setSelectedKbId(Number(event.target.value))}
                      style={{ width: "100%", padding: "8px", marginBottom: "10px" }}
                    >
                      {knowledgeBases.map((kb) => (
                        <option key={kb.id} value={kb.id}>
                          {kb.name} ({kb.document_count ?? 0} docs)
                        </option>
                      ))}
                    </select>
                  ) : null}

                  <div style={{ display: "flex", gap: "8px", marginBottom: "10px", flexWrap: "wrap" }}>
                    <input
                      type="file"
                      accept=".pdf,.docx,.pptx,.txt,.md"
                      onChange={(event) => setUploadFile(event.target.files?.[0] ?? null)}
                    />
                    <Button onClick={uploadDocument} disabled={!selectedKbId || !uploadFile || uploading}>
                      {uploading ? "Uploading..." : "Upload Document"}
                    </Button>
                    <Button
                      variant="secondary"
                      onClick={processQueuedDocuments}
                      disabled={!selectedKbId || processingQueued}
                    >
                      {processingQueued ? "Processing..." : "Process Queued"}
                    </Button>
                  </div>

                  {docsError ? <p className="error">Error: {docsError}</p> : null}
                  {docsLoading ? <p>Loading documents...</p> : null}
                  {!docsLoading && documents.length === 0 ? <p>No documents yet.</p> : null}
                  {documents.length > 0 ? (
                    <div style={{ display: "grid", gap: "8px" }}>
                      {documents.map((doc) => (
                        <div
                          key={doc.id}
                          style={{
                            border: "1px solid var(--border)",
                            borderRadius: "8px",
                            padding: "10px",
                            display: "grid",
                            gap: "8px",
                          }}
                        >
                          <div>
                            <strong>{doc.filename}</strong> - {doc.status ?? "unknown"}
                            {doc.error_message ? <p className="error">Error: {doc.error_message}</p> : null}
                          </div>
                          <div style={{ display: "flex", gap: "8px" }}>
                            <Button variant="secondary" onClick={() => previewDocument(doc.id)}>
                              Preview
                            </Button>
                            <Button variant="outline" onClick={() => deleteDocument(doc.id)}>
                              Delete
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : null}

                  {previewDocId ? (
                    <div style={{ marginTop: "12px" }}>
                      <h3>Preview (Doc #{previewDocId})</h3>
                      <pre>{previewText || "Loading preview..."}</pre>
                    </div>
                  ) : null}
                </>
              ) : null}
            </section>

            <section className="card">
              <h2>Class & Roster Basics</h2>
              {!isTeacherRole ? <p>Teacher/admin role required for class management.</p> : null}
              {isTeacherRole ? (
                <>
                  <div style={{ display: "grid", gap: "8px", marginBottom: "10px" }}>
                    <input
                      value={className}
                      onChange={(event) => setClassName(event.target.value)}
                      placeholder="Class name"
                    />
                    <input
                      value={classSubject}
                      onChange={(event) => setClassSubject(event.target.value)}
                      placeholder="Subject (optional)"
                    />
                    <Button onClick={createClass} disabled={!className.trim() || classBusy}>
                      {classBusy ? "Working..." : "Create Class"}
                    </Button>
                  </div>

                  {classesError ? <p className="error">Error: {classesError}</p> : null}
                  {classes.length > 0 ? (
                    <select
                      value={selectedClassId ?? ""}
                      onChange={(event) => setSelectedClassId(Number(event.target.value))}
                      style={{ width: "100%", padding: "8px", marginBottom: "10px" }}
                    >
                      {classes.map((cls) => (
                        <option key={cls.id} value={cls.id}>
                          {cls.name} ({cls.roster_count ?? 0} students)
                        </option>
                      ))}
                    </select>
                  ) : (
                    <p>No classes yet.</p>
                  )}

                  {selectedClassId ? (
                    <>
                      <div style={{ display: "flex", gap: "8px", marginBottom: "8px", flexWrap: "wrap" }}>
                        <input
                          value={studentIdInput}
                          onChange={(event) => setStudentIdInput(event.target.value)}
                          placeholder="Student tutor_user ID"
                        />
                        <Button onClick={enrollStudent} disabled={classBusy || !studentIdInput.trim()}>
                          Enroll Student
                        </Button>
                      </div>

                      {roster.length === 0 ? <p>No students enrolled.</p> : null}
                      {roster.length > 0 ? (
                        <div style={{ display: "grid", gap: "8px" }}>
                          {roster.map((entry) => (
                            <div
                              key={entry.enrollment_id}
                              style={{
                                border: "1px solid var(--border)",
                                borderRadius: "8px",
                                padding: "10px",
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center",
                                gap: "8px",
                              }}
                            >
                              <div>
                                <strong>{entry.display_name || `Student #${entry.student_id}`}</strong>
                                <div>ID: {entry.student_id}</div>
                              </div>
                              <Button variant="outline" onClick={() => removeEnrollment(entry.enrollment_id)}>
                                Remove
                              </Button>
                            </div>
                          ))}
                        </div>
                      ) : null}
                    </>
                  ) : null}
                </>
              ) : null}
            </section>
          </ProtectedRoute>
        </div>
      </section>
    </main>
  );
}
