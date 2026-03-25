"use client";

import { useEffect, useMemo, useState } from "react";
import { useAuthContext } from "@/components/auth/auth-context";
import { MessageRenderer } from "@/components/chat/message-renderer";
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

type HintProgressionState = {
  id: number;
  current_level: number;
  can_request_next: boolean;
  problem_text: string;
};

type ActiveQuizState = {
  id: number;
  difficulty: number;
  question: string;
  options: string[];
};

type FlashcardDeck = {
  id: number;
  title: string;
  subject?: string | null;
  topic?: string | null;
  card_count?: number;
};

type DueFlashcard = {
  id: number;
  deck_id: number;
  deck_title?: string;
  front: string;
  back: string;
  interval_days?: number;
  review_count?: number;
};

type MasteryRecord = {
  id: number;
  subject: string;
  topic: string;
  mastery_level: number;
  reasoning_quality?: number | null;
  last_assessed_at?: string | null;
};

type MisconceptionRecord = {
  id: number;
  subject?: string | null;
  topic?: string | null;
  misconception_type: string;
  description: string;
  detected_at?: string | null;
  resolved_at?: string | null;
};

type StudentProgressSummary = {
  total_sessions: number;
  total_tokens: number;
  total_quiz: number;
  correct_quiz: number;
  quiz_accuracy: number;
  mastery_topics: number;
  avg_mastery: number;
  active_misconceptions: number;
  due_flashcards: number;
};

type TeacherProgressSummary = {
  student_count: number;
  avg_mastery: number;
  quiz_accuracy: number;
  active_misconceptions: number;
};

type GradeBand = "k2" | "g35" | "g68" | "g912";

function extractGradeLevel(user: Record<string, unknown> | null): number | null {
  if (!user || typeof user !== "object") return null;
  const tutorUser = user.tutor_user;
  if (!tutorUser || typeof tutorUser !== "object") return null;
  const raw = (tutorUser as Record<string, unknown>).grade_level;
  if (typeof raw === "number" && Number.isFinite(raw)) return raw;
  if (typeof raw === "string") {
    const n = Number(raw);
    if (Number.isFinite(n)) return n;
  }
  return null;
}

function resolveGradeBand(grade: number | null): GradeBand {
  if (grade !== null && grade <= 2) return "k2";
  if (grade !== null && grade <= 5) return "g35";
  if (grade !== null && grade <= 8) return "g68";
  return "g912";
}

function gradeBandLabel(band: GradeBand): string {
  if (band === "k2") return "K-2";
  if (band === "g35") return "3-5";
  if (band === "g68") return "6-8";
  return "9-12";
}

function promptSuggestionsForBand(band: GradeBand): string[] {
  if (band === "k2") {
    return [
      "Can you explain with a short story?",
      "Give me one tiny step first.",
      "Use easy words and one example.",
    ];
  }
  if (band === "g35") {
    return [
      "Quiz me with one medium question.",
      "Give me two hints before the answer.",
      "Show me an easy visual way.",
    ];
  }
  if (band === "g68") {
    return [
      "Teach this like exam prep.",
      "Give me a challenge after explanation.",
      "Find my likely misconception.",
    ];
  }
  return [
    "Give me a rigorous explanation.",
    "Compare two solution strategies.",
    "Challenge my assumptions here.",
  ];
}

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
  const [hintState, setHintState] = useState<HintProgressionState | null>(null);
  const [activeQuiz, setActiveQuiz] = useState<ActiveQuizState | null>(null);
  const [lastSubmittedQuizId, setLastSubmittedQuizId] = useState<number | null>(null);
  const [explainReasoningInput, setExplainReasoningInput] = useState("");
  const [flashDecks, setFlashDecks] = useState<FlashcardDeck[]>([]);
  const [selectedFlashDeckId, setSelectedFlashDeckId] = useState<number | null>(null);
  const [dueFlashcards, setDueFlashcards] = useState<DueFlashcard[]>([]);
  const [flashcardsLoading, setFlashcardsLoading] = useState(false);
  const [flashcardsError, setFlashcardsError] = useState("");
  const [flashDeckTitleInput, setFlashDeckTitleInput] = useState("");
  const [flashcardPromptInput, setFlashcardPromptInput] = useState("");
  const [masteryRecords, setMasteryRecords] = useState<MasteryRecord[]>([]);
  const [masteryLoading, setMasteryLoading] = useState(false);
  const [masteryError, setMasteryError] = useState("");
  const [misconceptions, setMisconceptions] = useState<MisconceptionRecord[]>([]);
  const [misconceptionsLoading, setMisconceptionsLoading] = useState(false);
  const [misconceptionsError, setMisconceptionsError] = useState("");
  const [studentProgress, setStudentProgress] = useState<StudentProgressSummary | null>(null);
  const [teacherProgress, setTeacherProgress] = useState<TeacherProgressSummary | null>(null);
  const [progressLoading, setProgressLoading] = useState(false);
  const [progressError, setProgressError] = useState("");
  const [isOnline, setIsOnline] = useState(true);
  const [subjectInput, setSubjectInput] = useState("");
  const [topicInput, setTopicInput] = useState("");

  const { user, role, isAuthenticated, loading, error, startLogin, logout, authMode } = useAuthContext();

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
  const gradeBand = resolveGradeBand(extractGradeLevel(user));
  const gradeSuggestions = promptSuggestionsForBand(gradeBand);

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

  const loadFlashcardDecks = async () => {
    try {
      setFlashcardsLoading(true);
      setFlashcardsError("");
      const data = await apiClient.get<{ decks?: FlashcardDeck[] }>("/api/tutor/flashcards/decks");
      const decks = Array.isArray(data.decks) ? data.decks : [];
      setFlashDecks(decks);
      if (decks.length > 0 && (selectedFlashDeckId === null || !decks.some((d) => d.id === selectedFlashDeckId))) {
        setSelectedFlashDeckId(decks[0].id);
      }
    } catch (err) {
      setFlashcardsError(err instanceof Error ? err.message : "Could not load flashcard decks");
      setFlashDecks([]);
      setSelectedFlashDeckId(null);
    } finally {
      setFlashcardsLoading(false);
    }
  };

  const loadDueFlashcards = async () => {
    try {
      setFlashcardsLoading(true);
      setFlashcardsError("");
      const data = await apiClient.get<{ cards?: DueFlashcard[] }>("/api/tutor/flashcards/review?limit=20");
      setDueFlashcards(Array.isArray(data.cards) ? data.cards : []);
    } catch (err) {
      setFlashcardsError(err instanceof Error ? err.message : "Could not load due flashcards");
      setDueFlashcards([]);
    } finally {
      setFlashcardsLoading(false);
    }
  };

  const loadMasteryRecords = async () => {
    try {
      setMasteryLoading(true);
      setMasteryError("");
      const data = await apiClient.get<{ mastery?: MasteryRecord[] }>("/api/tutor/mastery?limit=50");
      setMasteryRecords(Array.isArray(data.mastery) ? data.mastery : []);
    } catch (err) {
      setMasteryError(err instanceof Error ? err.message : "Could not load mastery data");
      setMasteryRecords([]);
    } finally {
      setMasteryLoading(false);
    }
  };

  const recomputeMasteryFromSelection = async () => {
    const subject = subjectInput.trim();
    const topic = topicInput.trim();
    if (!subject || !topic) {
      setMasteryError("Enter subject and topic to recompute mastery");
      return;
    }
    try {
      setMasteryLoading(true);
      setMasteryError("");
      await apiClient.post("/api/tutor/mastery/recompute", { subject, topic });
      await loadMasteryRecords();
    } catch (err) {
      setMasteryError(err instanceof Error ? err.message : "Failed to recompute mastery");
    } finally {
      setMasteryLoading(false);
    }
  };

  const loadMisconceptions = async () => {
    try {
      setMisconceptionsLoading(true);
      setMisconceptionsError("");
      const data = await apiClient.get<{ misconceptions?: MisconceptionRecord[] }>(
        "/api/tutor/misconceptions?include_resolved=false&limit=50"
      );
      setMisconceptions(Array.isArray(data.misconceptions) ? data.misconceptions : []);
    } catch (err) {
      setMisconceptionsError(err instanceof Error ? err.message : "Could not load misconceptions");
      setMisconceptions([]);
    } finally {
      setMisconceptionsLoading(false);
    }
  };

  const resolveMisconception = async (misconceptionId: number) => {
    try {
      setMisconceptionsLoading(true);
      setMisconceptionsError("");
      await apiClient.post(`/api/tutor/misconceptions/${misconceptionId}/resolve`);
      await loadMisconceptions();
    } catch (err) {
      setMisconceptionsError(err instanceof Error ? err.message : "Failed to resolve misconception");
    } finally {
      setMisconceptionsLoading(false);
    }
  };

  const loadStudentProgress = async () => {
    try {
      setProgressLoading(true);
      setProgressError("");
      const data = await apiClient.get<{ summary?: StudentProgressSummary }>("/api/tutor/progress/student");
      setStudentProgress(data.summary ?? null);
    } catch (err) {
      setProgressError(err instanceof Error ? err.message : "Could not load student progress");
      setStudentProgress(null);
    } finally {
      setProgressLoading(false);
    }
  };

  const loadTeacherProgress = async (classId: number) => {
    try {
      setProgressLoading(true);
      setProgressError("");
      const data = await apiClient.get<{ summary?: TeacherProgressSummary }>(
        `/api/tutor/progress/teacher?class_id=${classId}`
      );
      setTeacherProgress(data.summary ?? null);
    } catch (err) {
      setProgressError(err instanceof Error ? err.message : "Could not load teacher progress");
      setTeacherProgress(null);
    } finally {
      setProgressLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      void loadExperts();
      void loadModes();
      void loadSessions();
      void loadFlashcardDecks();
      void loadDueFlashcards();
      void loadMasteryRecords();
      void loadMisconceptions();
      void loadStudentProgress();
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
    setFlashDecks([]);
    setSelectedFlashDeckId(null);
    setDueFlashcards([]);
    setMasteryRecords([]);
    setMisconceptions([]);
    setStudentProgress(null);
    setTeacherProgress(null);
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
      void loadTeacherProgress(selectedClassId);
      return;
    }
    setTeacherProgress(null);
    setRoster([]);
  }, [selectedClassId, isAuthenticated, isTeacherRole]);

  useEffect(() => {
    if (!isAuthenticated || selectedSessionId === null) {
      return;
    }
    setHintState(null);
    setLastSubmittedQuizId(null);
    setExplainReasoningInput("");
    void loadSessionDetail(selectedSessionId);
  }, [selectedSessionId, isAuthenticated]);

  useEffect(() => {
    if (selectedMode !== "hint") {
      setHintState(null);
    }
    if (selectedMode !== "quiz_me") {
      setActiveQuiz(null);
      setLastSubmittedQuizId(null);
      setExplainReasoningInput("");
    }
  }, [selectedMode]);

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

    if (selectedMode === "hint") {
      setChatLoading(true);
      setChatError("");
      setChatResult("");
      const userContent = chatPrompt.trim();
      setChatMessages((prev) => [...prev, { role: "user", content: userContent }]);
      const sessionId = await startSessionIfNeeded();
      if (sessionId === null) {
        setChatLoading(false);
        return;
      }
      try {
        const data = await apiClient.post<{
          progression?: { id?: number; current_level?: number; problem_text?: string };
          hint?: string;
          can_request_next?: boolean;
        }>("/api/tutor/hints/start", {
          session_id: sessionId,
          subject: subjectInput.trim() || undefined,
          topic: topicInput.trim() || undefined,
          problem_text: userContent,
        });
        const hint = String(data.hint || "").trim();
        if (hint) {
          setChatMessages((prev) => [...prev, { role: "assistant", content: hint, mode: "hint" }]);
          setChatResult(hint);
        }
        const progressionId = Number(data.progression?.id);
        const currentLevel = Number(data.progression?.current_level ?? 1);
        setHintState(
          Number.isInteger(progressionId) && progressionId > 0
            ? {
                id: progressionId,
                current_level: Number.isFinite(currentLevel) ? currentLevel : 1,
                can_request_next: Boolean(data.can_request_next),
                problem_text: String(data.progression?.problem_text || userContent),
              }
            : null
        );
        setChatPrompt("");
        await loadSessions();
      } catch (err) {
        setChatError(err instanceof Error ? err.message : "Hint request failed");
        setChatResult("");
      } finally {
        setChatLoading(false);
      }
      return;
    }

    if (selectedMode === "quiz_me") {
      setChatLoading(true);
      setChatError("");
      setChatResult("");
      const userContent = chatPrompt.trim();
      const sessionId = await startSessionIfNeeded();
      if (sessionId === null) {
        setChatLoading(false);
        return;
      }

      const renderQuizQuestion = (question: string, options: string[]) =>
        [question, ...options.map((opt, idx) => `${String.fromCharCode(65 + idx)}. ${opt}`)].join("\n");

      try {
        if (activeQuiz) {
          const normalizedAnswer = userContent.toUpperCase();
          setChatMessages((prev) => [...prev, { role: "user", content: userContent, mode: "quiz_me" }]);
          const submitted = await apiClient.post<{
            result?: {
              is_correct?: boolean;
              selected_answer?: string;
              correct_answer?: string;
              feedback?: string;
              explanation?: string;
              next_recommended_difficulty?: number;
            };
          }>(`/api/tutor/quiz/${activeQuiz.id}/submit`, { answer: normalizedAnswer });
          const result = submitted.result;
          const feedbackText = [
            result?.is_correct ? "Correct." : "Not correct.",
            result?.feedback || "",
            result?.explanation ? `Explanation: ${result.explanation}` : "",
            Number.isFinite(Number(result?.next_recommended_difficulty))
              ? `Next difficulty suggestion: ${result?.next_recommended_difficulty}/3`
              : "",
          ]
            .filter(Boolean)
            .join("\n");
          setChatMessages((prev) => [...prev, { role: "assistant", content: feedbackText, mode: "quiz_me" }]);
          setChatResult(feedbackText);
          setLastSubmittedQuizId(activeQuiz.id);
          setActiveQuiz(null);
        } else {
          setChatMessages((prev) => [...prev, { role: "user", content: userContent, mode: "quiz_me" }]);
          const generated = await apiClient.post<{
            quiz?: { id?: number; difficulty?: number; question?: string; options?: string[] };
          }>("/api/tutor/quiz/generate", {
            session_id: sessionId,
            subject: subjectInput.trim() || undefined,
            topic: topicInput.trim() || undefined,
            prompt_context: userContent,
          });
          const quiz = generated.quiz;
          const quizId = Number(quiz?.id);
          const options = Array.isArray(quiz?.options) ? quiz.options.map((v) => String(v)) : [];
          const question = String(quiz?.question || "").trim();
          const difficulty = Number(quiz?.difficulty || 2);
          if (!Number.isInteger(quizId) || quizId <= 0 || !question || options.length === 0) {
            throw new Error("Quiz generation returned invalid payload");
          }
          setActiveQuiz({ id: quizId, difficulty, question, options });
          const quizMessage = renderQuizQuestion(question, options);
          setChatMessages((prev) => [...prev, { role: "assistant", content: quizMessage, mode: "quiz_me" }]);
          setChatResult(quizMessage);
        }

        setChatPrompt("");
        await loadSessions();
      } catch (err) {
        setChatError(err instanceof Error ? err.message : "Quiz request failed");
        setChatResult("");
      } finally {
        setChatLoading(false);
      }
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

  const requestNextHintLevel = async () => {
    if (!hintState || !hintState.can_request_next) {
      return;
    }
    if (!isOnline) {
      setChatError("You are offline. Reconnect and try again.");
      return;
    }
    setChatLoading(true);
    setChatError("");
    try {
      const data = await apiClient.post<{
        progression?: { id?: number; current_level?: number; problem_text?: string };
        hint?: string;
        can_request_next?: boolean;
      }>(`/api/tutor/hints/${hintState.id}/next`);
      const hint = String(data.hint || "").trim();
      if (hint) {
        setChatMessages((prev) => [...prev, { role: "assistant", content: hint, mode: "hint" }]);
        setChatResult(hint);
      }
      const currentLevel = Number(data.progression?.current_level ?? hintState.current_level);
      setHintState({
        id: hintState.id,
        current_level: Number.isFinite(currentLevel) ? currentLevel : hintState.current_level,
        can_request_next: Boolean(data.can_request_next),
        problem_text: String(data.progression?.problem_text || hintState.problem_text),
      });
      await loadSessions();
    } catch (err) {
      setChatError(err instanceof Error ? err.message : "Failed to request next hint");
    } finally {
      setChatLoading(false);
    }
  };

  const submitActiveQuizChoice = async (choice: "A" | "B" | "C" | "D") => {
    if (!activeQuiz || selectedMode !== "quiz_me") {
      return;
    }
    setChatPrompt(choice);
    setChatLoading(true);
    setChatError("");
    try {
      setChatMessages((prev) => [...prev, { role: "user", content: choice, mode: "quiz_me" }]);
      const submitted = await apiClient.post<{
        result?: {
          is_correct?: boolean;
          feedback?: string;
          explanation?: string;
          next_recommended_difficulty?: number;
        };
      }>(`/api/tutor/quiz/${activeQuiz.id}/submit`, { answer: choice });
      const result = submitted.result;
      const feedbackText = [
        result?.is_correct ? "Correct." : "Not correct.",
        result?.feedback || "",
        result?.explanation ? `Explanation: ${result.explanation}` : "",
        Number.isFinite(Number(result?.next_recommended_difficulty))
          ? `Next difficulty suggestion: ${result?.next_recommended_difficulty}/3`
          : "",
      ]
        .filter(Boolean)
        .join("\n");
      setChatMessages((prev) => [...prev, { role: "assistant", content: feedbackText, mode: "quiz_me" }]);
      setChatResult(feedbackText);
      setLastSubmittedQuizId(activeQuiz.id);
      setActiveQuiz(null);
      setChatPrompt("");
      await loadSessions();
    } catch (err) {
      setChatError(err instanceof Error ? err.message : "Failed to submit quiz answer");
    } finally {
      setChatLoading(false);
    }
  };

  const runExplainMyAnswer = async () => {
    if (!lastSubmittedQuizId || !explainReasoningInput.trim()) {
      return;
    }
    if (!isOnline) {
      setChatError("You are offline. Reconnect and try again.");
      return;
    }
    setChatLoading(true);
    setChatError("");
    try {
      setChatMessages((prev) => [
        ...prev,
        { role: "user", content: `Why I chose my answer: ${explainReasoningInput.trim()}`, mode: "quiz_me" },
      ]);
      const data = await apiClient.post<{ explanation?: string }>(
        `/api/tutor/quiz/${lastSubmittedQuizId}/explain-my-answer`,
        { student_reasoning: explainReasoningInput.trim() }
      );
      const explanation = String(data.explanation || "").trim();
      if (explanation) {
        setChatMessages((prev) => [...prev, { role: "assistant", content: explanation, mode: "quiz_me" }]);
        setChatResult(explanation);
      }
      setExplainReasoningInput("");
    } catch (err) {
      setChatError(err instanceof Error ? err.message : "Explain-my-answer failed");
    } finally {
      setChatLoading(false);
    }
  };

  const createFlashcardDeck = async () => {
    if (!flashDeckTitleInput.trim()) {
      setFlashcardsError("Deck title is required");
      return;
    }
    try {
      setFlashcardsLoading(true);
      setFlashcardsError("");
      const data = await apiClient.post<{ deck?: { id?: number } }>("/api/tutor/flashcards/decks", {
        title: flashDeckTitleInput.trim(),
        subject: subjectInput.trim() || undefined,
        topic: topicInput.trim() || undefined,
      });
      setFlashDeckTitleInput("");
      await loadFlashcardDecks();
      const id = Number(data.deck?.id);
      if (Number.isInteger(id) && id > 0) {
        setSelectedFlashDeckId(id);
      }
    } catch (err) {
      setFlashcardsError(err instanceof Error ? err.message : "Failed to create deck");
    } finally {
      setFlashcardsLoading(false);
    }
  };

  const generateFlashcardsFromPrompt = async () => {
    if (!flashcardPromptInput.trim()) {
      setFlashcardsError("Prompt is required to generate flashcards");
      return;
    }
    try {
      setFlashcardsLoading(true);
      setFlashcardsError("");
      await apiClient.post("/api/tutor/flashcards/generate", {
        deck_id: selectedFlashDeckId ?? undefined,
        title: selectedFlashDeckId ? undefined : "Generated Deck",
        prompt: flashcardPromptInput.trim(),
        subject: subjectInput.trim() || undefined,
        topic: topicInput.trim() || undefined,
        session_id: selectedSessionId ?? undefined,
        count: 5,
      });
      setFlashcardPromptInput("");
      await Promise.all([loadFlashcardDecks(), loadDueFlashcards()]);
    } catch (err) {
      setFlashcardsError(err instanceof Error ? err.message : "Failed to generate flashcards");
    } finally {
      setFlashcardsLoading(false);
    }
  };

  const reviewDueFlashcard = async (cardId: number, quality: number) => {
    try {
      setFlashcardsLoading(true);
      setFlashcardsError("");
      await apiClient.post(`/api/tutor/flashcards/${cardId}/review`, { quality });
      await loadDueFlashcards();
    } catch (err) {
      setFlashcardsError(err instanceof Error ? err.message : "Failed to review flashcard");
    } finally {
      setFlashcardsLoading(false);
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

  const refreshDashboard = async () => {
    await Promise.allSettled([
      loadExperts(),
      loadModes(),
      loadSessions(),
      loadFlashcardDecks(),
      loadDueFlashcards(),
      loadMasteryRecords(),
      loadMisconceptions(),
      loadStudentProgress(),
      selectedClassId && isTeacherRole ? loadTeacherProgress(selectedClassId) : Promise.resolve(),
      isTeacherRole ? loadKnowledgeBases() : Promise.resolve(),
      isTeacherRole ? loadClasses() : Promise.resolve(),
      selectedKbId ? loadDocuments(selectedKbId) : Promise.resolve(),
      selectedClassId ? loadRoster(selectedClassId) : Promise.resolve(),
    ]);
  };

  const loadingFlags = {
    chatLoading,
    sessionLoading,
    kbLoading,
    docsLoading,
    classBusy,
    flashcardsLoading,
    masteryLoading,
    misconceptionsLoading,
    progressLoading,
  };
  const anyLoading = Object.values(loadingFlags).some(Boolean);
  const activeErrors = [error, expertsError, chatError, kbError, docsError, classesError].filter(Boolean);
  const primaryError = activeErrors.length > 0 ? activeErrors[0] : "";

  return (
    <main className={`page age-band-${gradeBand}`}>
      <aside className="shell-sidebar">
        <div className="shell-brand">Clever AI Tutor</div>
        <div className="band-chip">Band {gradeBandLabel(gradeBand)}</div>
        <nav className="shell-nav">
          <button className="shell-nav-item" type="button">
            {gradeBand === "k2" ? "Home" : "Dashboard"}
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
            {isAuthenticated ? <Button onClick={handleLogout}>Logout</Button> : <Button onClick={startLogin}>{authMode === "local_dev" ? "Login with Local Dev Account" : "Login with Main Site"}</Button>}
          </div>
        </header>

        <div className="shell-content">
          <ProtectedRoute>
            <section className="card">
              <h2>System Status</h2>
              <p>
                Connection: <strong>{isOnline ? "Online" : "Offline"}</strong>
              </p>
              {anyLoading ? <p>Background activity: syncing data...</p> : <p>Background activity: idle</p>}
              {primaryError ? <p className="error">Current issue: {primaryError}</p> : null}
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                <Button variant="outline" onClick={() => void refreshDashboard()} disabled={anyLoading}>
                  Refresh Data
                </Button>
                {!isOnline ? (
                  <Button variant="secondary" onClick={() => window.location.reload()}>
                    Reload Page
                  </Button>
                ) : null}
              </div>
            </section>

            <header className="header">
              <div>
                <h1>Clever AI Tutor</h1>
                <p>
                  {gradeBand === "k2"
                    ? "Friendly tutoring with short, clear steps."
                    : "Next.js + FastAPI. Auth via main site; experts and chat run locally. See ARCHITECTURE.md."}
                </p>
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
                      setHintState(null);
                      setActiveQuiz(null);
                      setLastSubmittedQuizId(null);
                      setExplainReasoningInput("");
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
                        <div style={{ marginTop: "6px" }}>
                          <MessageRenderer content={message.content} />
                        </div>
                      </div>
                    ))}
                  </div>
                  <textarea
                    value={chatPrompt}
                    onChange={(event) => setChatPrompt(event.target.value)}
                    rows={3}
                    placeholder={gradeBand === "k2" ? "Ask your tutor in simple words..." : "Ask your tutor..."}
                    disabled={!isAuthenticated || chatLoading}
                  />
                  <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginBottom: "8px" }}>
                    {gradeSuggestions.map((suggestion) => (
                      <button
                        key={suggestion}
                        type="button"
                        className="chip"
                        onClick={() => setChatPrompt(suggestion)}
                        disabled={chatLoading}
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                  <Button onClick={sendStreamChat} disabled={!isAuthenticated || chatLoading || !chatPrompt.trim()}>
                    {chatLoading
                      ? selectedMode === "hint"
                        ? "Getting Hint..."
                        : selectedMode === "quiz_me"
                          ? activeQuiz
                            ? "Submitting..."
                            : "Generating Quiz..."
                          : "Streaming..."
                      : selectedMode === "hint"
                        ? "Get Hint (Level 1)"
                        : selectedMode === "quiz_me"
                          ? activeQuiz
                            ? "Submit Typed Answer"
                            : "Generate Quiz Question"
                        : "Send Message"}
                  </Button>
                  {selectedMode === "quiz_me" && activeQuiz ? (
                    <div style={{ marginTop: "8px", display: "flex", gap: "6px", flexWrap: "wrap" }}>
                      {(activeQuiz.options.slice(0, 4) as string[]).map((option, idx) => {
                        const label = String.fromCharCode(65 + idx) as "A" | "B" | "C" | "D";
                        return (
                          <Button
                            key={`${activeQuiz.id}-${label}`}
                            variant="secondary"
                            onClick={() => submitActiveQuizChoice(label)}
                            disabled={chatLoading}
                          >
                            {label}. {option}
                          </Button>
                        );
                      })}
                    </div>
                  ) : null}
                  {selectedMode === "hint" && hintState && hintState.can_request_next ? (
                    <Button
                      variant="secondary"
                      onClick={requestNextHintLevel}
                      disabled={!isAuthenticated || chatLoading}
                      style={{ marginLeft: "8px" }}
                    >
                      {chatLoading ? "Loading..." : `Next Hint (Level ${Math.min(3, hintState.current_level + 1)})`}
                    </Button>
                  ) : null}
                  {chatError ? <p className="error">Error: {chatError}</p> : null}
                  {chatResult ? <p style={{ marginTop: "6px", fontSize: "12px", opacity: 0.8 }}>Latest response captured.</p> : null}
                  {selectedMode === "hint" && hintState ? (
                    <p style={{ marginTop: "6px", fontSize: "12px", opacity: 0.8 }}>
                      Hint progression active: level {hintState.current_level}/3
                    </p>
                  ) : null}
                  {selectedMode === "quiz_me" && activeQuiz ? (
                    <p style={{ marginTop: "6px", fontSize: "12px", opacity: 0.8 }}>
                      Active quiz difficulty: {activeQuiz.difficulty}/3
                    </p>
                  ) : null}
                  {selectedMode === "quiz_me" && !activeQuiz && lastSubmittedQuizId ? (
                    <div style={{ marginTop: "8px", display: "grid", gap: "6px" }}>
                      <textarea
                        rows={2}
                        value={explainReasoningInput}
                        onChange={(event) => setExplainReasoningInput(event.target.value)}
                        placeholder="Explain why you chose your answer..."
                        disabled={chatLoading}
                      />
                      <Button
                        variant="secondary"
                        onClick={runExplainMyAnswer}
                        disabled={chatLoading || !explainReasoningInput.trim()}
                      >
                        {chatLoading ? "Explaining..." : "Explain My Answer"}
                      </Button>
                    </div>
                  ) : null}
                </div>
              </div>
            </section>

            <section className="card">
              <h2>Flashcards & Spaced Review</h2>
              <div style={{ display: "grid", gap: "8px", marginBottom: "10px" }}>
                <input
                  value={flashDeckTitleInput}
                  onChange={(event) => setFlashDeckTitleInput(event.target.value)}
                  placeholder="New deck title"
                />
                <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                  <Button onClick={createFlashcardDeck} disabled={flashcardsLoading || !flashDeckTitleInput.trim()}>
                    {flashcardsLoading ? "Working..." : "Create Deck"}
                  </Button>
                  <Button variant="secondary" onClick={loadFlashcardDecks} disabled={flashcardsLoading}>
                    Refresh Decks
                  </Button>
                </div>
              </div>

              {flashDecks.length > 0 ? (
                <select
                  value={selectedFlashDeckId ?? ""}
                  onChange={(event) => setSelectedFlashDeckId(Number(event.target.value))}
                  style={{ width: "100%", padding: "8px", marginBottom: "10px" }}
                >
                  {flashDecks.map((deck) => (
                    <option key={deck.id} value={deck.id}>
                      {deck.title} ({deck.card_count ?? 0} cards)
                    </option>
                  ))}
                </select>
              ) : (
                <p>No decks yet.</p>
              )}

              <div style={{ display: "grid", gap: "8px", marginBottom: "10px" }}>
                <textarea
                  rows={2}
                  value={flashcardPromptInput}
                  onChange={(event) => setFlashcardPromptInput(event.target.value)}
                  placeholder="Paste notes or topic summary to auto-generate flashcards..."
                />
                <Button
                  variant="secondary"
                  onClick={generateFlashcardsFromPrompt}
                  disabled={flashcardsLoading || !flashcardPromptInput.trim()}
                >
                  {flashcardsLoading ? "Generating..." : "Generate 5 Flashcards"}
                </Button>
              </div>

              <div>
                <strong>Due For Review</strong>
                <div style={{ marginTop: "8px", display: "grid", gap: "8px" }}>
                  {dueFlashcards.length === 0 ? <p>No cards due right now.</p> : null}
                  {dueFlashcards.map((card) => (
                    <div
                      key={card.id}
                      style={{
                        border: "1px solid var(--border)",
                        borderRadius: "8px",
                        padding: "10px",
                        display: "grid",
                        gap: "6px",
                      }}
                    >
                      <div style={{ fontSize: "12px", opacity: 0.8 }}>{card.deck_title || `Deck #${card.deck_id}`}</div>
                      <div><strong>Front:</strong> {card.front}</div>
                      <div><strong>Back:</strong> {card.back}</div>
                      <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
                        <Button variant="outline" onClick={() => reviewDueFlashcard(card.id, 1)} disabled={flashcardsLoading}>
                          Again
                        </Button>
                        <Button variant="outline" onClick={() => reviewDueFlashcard(card.id, 3)} disabled={flashcardsLoading}>
                          Hard
                        </Button>
                        <Button variant="secondary" onClick={() => reviewDueFlashcard(card.id, 4)} disabled={flashcardsLoading}>
                          Good
                        </Button>
                        <Button onClick={() => reviewDueFlashcard(card.id, 5)} disabled={flashcardsLoading}>
                          Easy
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              {flashcardsError ? <p className="error">Error: {flashcardsError}</p> : null}
            </section>

            <section className="card">
              <h2>Mastery Tracking</h2>
              <p style={{ marginBottom: "8px" }}>Topic mastery is tracked on a 0-5 scale.</p>
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginBottom: "8px" }}>
                <Button variant="secondary" onClick={loadMasteryRecords} disabled={masteryLoading}>
                  {masteryLoading ? "Loading..." : "Refresh Mastery"}
                </Button>
                <Button onClick={recomputeMasteryFromSelection} disabled={masteryLoading}>
                  Recompute From Subject/Topic
                </Button>
              </div>
              {masteryError ? <p className="error">Error: {masteryError}</p> : null}
              {masteryRecords.length === 0 ? <p>No mastery records yet.</p> : null}
              {masteryRecords.length > 0 ? (
                <div style={{ display: "grid", gap: "8px" }}>
                  {masteryRecords.map((record) => (
                    <div
                      key={record.id}
                      style={{
                        border: "1px solid var(--border)",
                        borderRadius: "8px",
                        padding: "10px",
                        display: "grid",
                        gap: "4px",
                      }}
                    >
                      <strong>
                        {record.subject} - {record.topic}
                      </strong>
                      <div>Mastery: {record.mastery_level}/5</div>
                      <div>Reasoning quality: {record.reasoning_quality ?? "-"}/5</div>
                    </div>
                  ))}
                </div>
              ) : null}
            </section>

            <section className="card">
              <h2>Misconception Detection</h2>
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginBottom: "8px" }}>
                <Button variant="secondary" onClick={loadMisconceptions} disabled={misconceptionsLoading}>
                  {misconceptionsLoading ? "Loading..." : "Refresh Misconceptions"}
                </Button>
              </div>
              {misconceptionsError ? <p className="error">Error: {misconceptionsError}</p> : null}
              {misconceptions.length === 0 ? <p>No active misconceptions detected.</p> : null}
              {misconceptions.length > 0 ? (
                <div style={{ display: "grid", gap: "8px" }}>
                  {misconceptions.map((item) => (
                    <div
                      key={item.id}
                      style={{
                        border: "1px solid var(--border)",
                        borderRadius: "8px",
                        padding: "10px",
                        display: "grid",
                        gap: "6px",
                      }}
                    >
                      <strong>
                        {item.subject || "General"} {item.topic ? `- ${item.topic}` : ""}
                      </strong>
                      <div style={{ fontSize: "12px", opacity: 0.85 }}>
                        Type: {item.misconception_type}
                      </div>
                      <div>{item.description}</div>
                      <div>
                        <Button variant="outline" onClick={() => resolveMisconception(item.id)} disabled={misconceptionsLoading}>
                          Mark Resolved
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : null}
            </section>

            <section className="card">
              <h2>Progress Dashboards</h2>
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginBottom: "8px" }}>
                <Button variant="secondary" onClick={loadStudentProgress} disabled={progressLoading}>
                  {progressLoading ? "Loading..." : "Refresh Student Dashboard"}
                </Button>
                {isTeacherRole && selectedClassId ? (
                  <Button variant="secondary" onClick={() => loadTeacherProgress(selectedClassId)} disabled={progressLoading}>
                    {progressLoading ? "Loading..." : "Refresh Teacher Dashboard"}
                  </Button>
                ) : null}
              </div>
              {progressError ? <p className="error">Error: {progressError}</p> : null}

              <div style={{ display: "grid", gap: "8px", marginBottom: "10px" }}>
                <strong>Student Summary</strong>
                {!studentProgress ? <p>No student summary yet.</p> : null}
                {studentProgress ? (
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(140px,1fr))", gap: "8px" }}>
                    <div className="chip">Sessions: {studentProgress.total_sessions}</div>
                    <div className="chip">Quiz Accuracy: {(studentProgress.quiz_accuracy * 100).toFixed(1)}%</div>
                    <div className="chip">Avg Mastery: {studentProgress.avg_mastery}/5</div>
                    <div className="chip">Due Cards: {studentProgress.due_flashcards}</div>
                    <div className="chip">Active Misconceptions: {studentProgress.active_misconceptions}</div>
                  </div>
                ) : null}
              </div>

              {isTeacherRole ? (
                <div style={{ display: "grid", gap: "8px" }}>
                  <strong>Teacher Class Summary</strong>
                  {!teacherProgress ? <p>Select a class to view teacher dashboard.</p> : null}
                  {teacherProgress ? (
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(140px,1fr))", gap: "8px" }}>
                      <div className="chip">Students: {teacherProgress.student_count}</div>
                      <div className="chip">Class Avg Mastery: {teacherProgress.avg_mastery}/5</div>
                      <div className="chip">Class Quiz Accuracy: {(teacherProgress.quiz_accuracy * 100).toFixed(1)}%</div>
                      <div className="chip">Class Misconceptions: {teacherProgress.active_misconceptions}</div>
                    </div>
                  ) : null}
                </div>
              ) : null}
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
