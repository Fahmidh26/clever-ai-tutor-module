"use client";

import { useEffect, useMemo, useState } from "react";

import { useAuthContext } from "@/components/auth/auth-context";
import { Button } from "@/components/ui/button";
import { createApiClient } from "@/lib/api-client";

type TeacherClass = {
  id: number;
  name: string;
  subject?: string | null;
  grade_level?: number | null;
  invite_code?: string | null;
};

type LinkedStudent = {
  link_id: number;
  student_id: number;
  display_name?: string | null;
  grade_level?: number | null;
  class_count: number;
  source?: string;
};

type JoinCode = {
  id: number;
  code: string;
  status: string;
  expires_at?: string | null;
};

type JoinRequest = {
  id: number;
  student_id: number;
  display_name?: string | null;
  grade_level?: number | null;
  class_id?: number | null;
  class_name?: string | null;
  join_code?: string | null;
  request_message?: string | null;
  requested_at?: string | null;
};

type Persona = {
  id: number;
  name: string;
  tagline?: string | null;
  teaching_style?: string | null;
};

type ClassPersonaPolicy = {
  persona_id?: number | null;
  persona_name?: string | null;
  overlay_instructions?: string | null;
  effective_prompt_preview?: string | null;
};

type ClassAnalyticsStudent = {
  student_id: number;
  display_name?: string | null;
  avg_mastery: number;
  quiz_accuracy: number;
  active_misconceptions: number;
  total_sessions: number;
  total_messages: number;
  last_activity_at?: string | null;
};

type ClassAnalytics = {
  class?: TeacherClass;
  summary?: {
    student_count: number;
    active_students: number;
    avg_mastery: number;
    quiz_accuracy: number;
    active_misconceptions: number;
    total_sessions: number;
    total_messages: number;
    kb_messages: number;
    assigned_kb_count: number;
  };
  students?: ClassAnalyticsStudent[];
};

type StrugglingStudent = {
  student_id: number;
  display_name?: string | null;
  class_name?: string | null;
  avg_mastery: number;
  quiz_accuracy: number;
  active_misconceptions: number;
  flags: string[];
};

type StudentAnalytics = {
  student?: {
    id: number;
    display_name?: string | null;
    grade_level?: number | null;
  };
  summary?: {
    class_count: number;
    mastery_count: number;
    active_misconceptions: number;
    quiz_accuracy: number;
    session_count: number;
  };
  recent_sessions?: Array<{
    id: number;
    subject?: string | null;
    topic?: string | null;
    mode?: string | null;
    persona_name?: string | null;
    created_at?: string | null;
  }>;
};

type SessionReplay = {
  session?: {
    id: number;
    student_name?: string | null;
    class_name?: string | null;
    subject?: string | null;
    topic?: string | null;
    persona_name?: string | null;
  };
  messages?: Array<{
    id: number;
    role: string;
    content: string;
  }>;
};

type ReportDraft = {
  id: number;
  report_type: string;
  title: string;
  class_name?: string | null;
  student_name?: string | null;
  body_json?: {
    suggestions?: string[];
  };
};

type Assessment = {
  id: number;
  title: string;
  type?: string | null;
  subject?: string | null;
  question_count?: number;
};

type AssessmentDetail = {
  assessment?: Assessment;
  questions?: Array<{
    id: number;
    content: string;
    question_type?: string | null;
  }>;
};

const shellCard = "rounded-2xl border border-border/70 bg-background/70 p-4 shadow-sm";
const sectionTitle = "text-lg font-semibold tracking-tight";
const muted = "text-sm text-muted-foreground";
const grid2 = "grid gap-4 lg:grid-cols-2";

export function TeacherControlCenter() {
  const { apiBaseUrl, role } = useAuthContext();
  const apiClient = useMemo(() => createApiClient({ baseUrl: apiBaseUrl }), [apiBaseUrl]);
  const isTeacherRole = role === "teacher" || role === "admin";

  const [classes, setClasses] = useState<TeacherClass[]>([]);
  const [selectedClassId, setSelectedClassId] = useState<number | null>(null);
  const [roster, setRoster] = useState<LinkedStudent[]>([]);
  const [unassigned, setUnassigned] = useState<LinkedStudent[]>([]);
  const [joinCodes, setJoinCodes] = useState<JoinCode[]>([]);
  const [joinRequests, setJoinRequests] = useState<JoinRequest[]>([]);
  const [manualStudentId, setManualStudentId] = useState("");
  const [rosterError, setRosterError] = useState("");

  const [personas, setPersonas] = useState<Persona[]>([]);
  const [selectedPersonaId, setSelectedPersonaId] = useState<number | null>(null);
  const [personaOverlay, setPersonaOverlay] = useState("");
  const [classPolicy, setClassPolicy] = useState<ClassPersonaPolicy | null>(null);
  const [personaPreview, setPersonaPreview] = useState("");
  const [personaError, setPersonaError] = useState("");

  const [classAnalytics, setClassAnalytics] = useState<ClassAnalytics | null>(null);
  const [struggling, setStruggling] = useState<StrugglingStudent[]>([]);
  const [selectedStudentId, setSelectedStudentId] = useState<number | null>(null);
  const [studentAnalytics, setStudentAnalytics] = useState<StudentAnalytics | null>(null);
  const [selectedReplaySessionId, setSelectedReplaySessionId] = useState<number | null>(null);
  const [sessionReplay, setSessionReplay] = useState<SessionReplay | null>(null);
  const [monitoringError, setMonitoringError] = useState("");

  const [copilotTopic, setCopilotTopic] = useState("");
  const [copilotSuggestions, setCopilotSuggestions] = useState<string[]>([]);
  const [worksheetDraft, setWorksheetDraft] = useState<string[]>([]);
  const [reports, setReports] = useState<ReportDraft[]>([]);
  const [reportError, setReportError] = useState("");

  const [assessmentTitle, setAssessmentTitle] = useState("");
  const [assessmentSubject, setAssessmentSubject] = useState("");
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [selectedAssessmentId, setSelectedAssessmentId] = useState<number | null>(null);
  const [assessmentDetail, setAssessmentDetail] = useState<AssessmentDetail | null>(null);
  const [questionContent, setQuestionContent] = useState("");
  const [assessmentError, setAssessmentError] = useState("");

  const refreshClasses = async () => {
    if (!isTeacherRole) return;
    const data = await apiClient.get<{ classes?: TeacherClass[] }>("/api/teacher/classes");
    const items = Array.isArray(data.classes) ? data.classes : [];
    setClasses(items);
    setSelectedClassId((current) => current ?? items[0]?.id ?? null);
  };

  const refreshRoster = async () => {
    if (!isTeacherRole) return;
    try {
      setRosterError("");
      const data = await apiClient.get<{
        linked_students?: LinkedStudent[];
        unassigned_students?: LinkedStudent[];
        pending_requests?: JoinRequest[];
        join_codes?: JoinCode[];
      }>("/api/teacher/roster");
      setRoster(Array.isArray(data.linked_students) ? data.linked_students : []);
      setUnassigned(Array.isArray(data.unassigned_students) ? data.unassigned_students : []);
      setJoinRequests(Array.isArray(data.pending_requests) ? data.pending_requests : []);
      setJoinCodes(Array.isArray(data.join_codes) ? data.join_codes : []);
    } catch (error) {
      setRosterError(error instanceof Error ? error.message : "Failed to load teacher roster");
    }
  };

  const refreshPersonas = async () => {
    if (!isTeacherRole) return;
    try {
      setPersonaError("");
      const [personaData, policyData] = await Promise.all([
        apiClient.get<{ personas?: Persona[] }>("/api/teacher/personas"),
        selectedClassId
          ? apiClient.get<{ policy?: ClassPersonaPolicy }>(`/api/teacher/personas/classes/${selectedClassId}`)
          : Promise.resolve({ policy: undefined }),
      ]);
      const items = Array.isArray(personaData.personas) ? personaData.personas : [];
      setPersonas(items);
      setSelectedPersonaId((current) => current ?? policyData.policy?.persona_id ?? items[0]?.id ?? null);
      setClassPolicy(policyData.policy ?? null);
      setPersonaOverlay(policyData.policy?.overlay_instructions ?? "");
      setPersonaPreview(policyData.policy?.effective_prompt_preview ?? "");
    } catch (error) {
      setPersonaError(error instanceof Error ? error.message : "Failed to load persona policy");
    }
  };

  const refreshMonitoring = async () => {
    if (!isTeacherRole || !selectedClassId) return;
    try {
      setMonitoringError("");
      const [classData, strugglingData] = await Promise.all([
        apiClient.get<ClassAnalytics>(`/api/teacher/analytics/class/${selectedClassId}`),
        apiClient.get<{ students?: StrugglingStudent[] }>("/api/teacher/analytics/struggling"),
      ]);
      setClassAnalytics(classData);
      setStruggling(Array.isArray(strugglingData.students) ? strugglingData.students : []);
    } catch (error) {
      setMonitoringError(error instanceof Error ? error.message : "Failed to load monitoring data");
    }
  };

  const refreshStudentAnalytics = async (studentId: number) => {
    try {
      setMonitoringError("");
      const data = await apiClient.get<StudentAnalytics>(`/api/teacher/analytics/students/${studentId}`);
      setSelectedStudentId(studentId);
      setStudentAnalytics(data);
      const firstSessionId = data.recent_sessions?.[0]?.id ?? null;
      setSelectedReplaySessionId(firstSessionId);
      if (firstSessionId) {
        const replay = await apiClient.get<SessionReplay>(`/api/teacher/session-replay/${firstSessionId}`);
        setSessionReplay(replay);
      } else {
        setSessionReplay(null);
      }
    } catch (error) {
      setMonitoringError(error instanceof Error ? error.message : "Failed to load student analytics");
    }
  };

  const refreshReports = async () => {
    if (!isTeacherRole) return;
    try {
      setReportError("");
      const data = await apiClient.get<{ reports?: ReportDraft[] }>("/api/teacher/reports");
      setReports(Array.isArray(data.reports) ? data.reports : []);
    } catch (error) {
      setReportError(error instanceof Error ? error.message : "Failed to load teacher reports");
    }
  };

  const refreshAssessments = async () => {
    if (!isTeacherRole) return;
    try {
      setAssessmentError("");
      const data = await apiClient.get<{ assessments?: Assessment[] }>("/api/teacher/assessments");
      const items = Array.isArray(data.assessments) ? data.assessments : [];
      setAssessments(items);
      setSelectedAssessmentId((current) => current ?? items[0]?.id ?? null);
    } catch (error) {
      setAssessmentError(error instanceof Error ? error.message : "Failed to load assessments");
    }
  };

  const refreshAssessmentDetail = async (assessmentId: number | null) => {
    if (!assessmentId) {
      setAssessmentDetail(null);
      return;
    }
    try {
      const data = await apiClient.get<AssessmentDetail>(`/api/teacher/assessments/${assessmentId}`);
      setAssessmentDetail(data);
    } catch (error) {
      setAssessmentError(error instanceof Error ? error.message : "Failed to load assessment detail");
    }
  };

  useEffect(() => {
    if (!isTeacherRole) return;
    void refreshClasses();
    void refreshRoster();
    void refreshReports();
    void refreshAssessments();
  }, [isTeacherRole]);

  useEffect(() => {
    if (!isTeacherRole || !selectedClassId) return;
    void refreshPersonas();
    void refreshMonitoring();
  }, [isTeacherRole, selectedClassId]);

  useEffect(() => {
    if (!selectedAssessmentId) return;
    void refreshAssessmentDetail(selectedAssessmentId);
  }, [selectedAssessmentId]);

  if (!isTeacherRole) {
    return null;
  }

  return (
    <section className="grid gap-6">
      <div className={shellCard}>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className={sectionTitle}>Teacher Control Center</h2>
            <p className={muted}>Roster, class policy, monitoring, reports, and assessments stay in the same app shell.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <select
              className="min-w-56 rounded-md border border-border bg-background px-3 py-2 text-sm"
              value={selectedClassId ?? ""}
              onChange={(event) => setSelectedClassId(Number(event.target.value))}
            >
              {classes.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
            <Button variant="secondary" onClick={() => void Promise.all([refreshRoster(), refreshMonitoring(), refreshReports()])}>
              Refresh Teacher Data
            </Button>
          </div>
        </div>
      </div>

      <div className={grid2}>
        <section className={shellCard}>
          <h3 className={sectionTitle}>Roster And Join Flow</h3>
          <p className={`${muted} mb-3`}>Generate teacher join codes, approve requests, and keep an unassigned linked-student queue.</p>
          <div className="mb-3 flex flex-wrap gap-2">
            <input
              className="min-w-44 rounded-md border border-border bg-background px-3 py-2 text-sm"
              placeholder="Student tutor_user ID"
              value={manualStudentId}
              onChange={(event) => setManualStudentId(event.target.value)}
            />
            <Button
              onClick={async () => {
                try {
                  await apiClient.post("/api/teacher/roster/link", { student_id: Number(manualStudentId) });
                  setManualStudentId("");
                  await refreshRoster();
                } catch (error) {
                  setRosterError(error instanceof Error ? error.message : "Failed to link student");
                }
              }}
              disabled={!manualStudentId.trim()}
            >
              Link Student
            </Button>
            <Button
              variant="secondary"
              onClick={async () => {
                try {
                  await apiClient.post("/api/teacher/join-codes", { expires_in_days: 14 });
                  await refreshRoster();
                } catch (error) {
                  setRosterError(error instanceof Error ? error.message : "Failed to create join code");
                }
              }}
            >
              Generate Join Code
            </Button>
          </div>
          {rosterError ? <p className="mb-3 text-sm text-destructive">{rosterError}</p> : null}
          <div className="grid gap-3">
            <div>
              <div className="mb-2 text-sm font-medium">Active join codes</div>
              <div className="flex flex-wrap gap-2">
                {joinCodes.length === 0 ? <span className={muted}>No join codes yet.</span> : null}
                {joinCodes.map((item) => (
                  <span key={item.id} className="rounded-full border border-border px-3 py-1 text-xs">
                    {item.code}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <div className="mb-2 text-sm font-medium">Pending requests</div>
              <div className="grid gap-2">
                {joinRequests.length === 0 ? <span className={muted}>No pending join requests.</span> : null}
                {joinRequests.map((item) => (
                  <div key={item.id} className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-border/70 p-3">
                    <div className="text-sm">
                      <div className="font-medium">{item.display_name || `Student #${item.student_id}`}</div>
                      <div className={muted}>
                        {item.class_name ? `Requested class: ${item.class_name}` : "Teacher-level roster request"}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="secondary"
                        onClick={async () => {
                          await apiClient.post(`/api/teacher/join-requests/${item.id}/approve`);
                          await Promise.all([refreshRoster(), refreshClasses(), refreshMonitoring()]);
                        }}
                      >
                        Approve
                      </Button>
                      <Button
                        variant="outline"
                        onClick={async () => {
                          await apiClient.post(`/api/teacher/join-requests/${item.id}/reject`);
                          await refreshRoster();
                        }}
                      >
                        Reject
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="grid gap-2 md:grid-cols-2">
              <div>
                <div className="mb-2 text-sm font-medium">Linked students</div>
                <div className="grid gap-2">
                  {roster.length === 0 ? <span className={muted}>No linked students yet.</span> : null}
                  {roster.map((item) => (
                    <button
                      key={item.link_id}
                      className="rounded-xl border border-border/70 p-3 text-left text-sm transition hover:border-foreground/30"
                      onClick={() => void refreshStudentAnalytics(item.student_id)}
                    >
                      <div className="font-medium">{item.display_name || `Student #${item.student_id}`}</div>
                      <div className={muted}>Classes: {item.class_count} • Source: {item.source || "manual"}</div>
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <div className="mb-2 text-sm font-medium">Unassigned queue</div>
                <div className="grid gap-2">
                  {unassigned.length === 0 ? <span className={muted}>No linked students waiting for class placement.</span> : null}
                  {unassigned.map((item) => (
                    <div key={`unassigned-${item.link_id}`} className="rounded-xl border border-dashed border-border p-3 text-sm">
                      <div className="font-medium">{item.display_name || `Student #${item.student_id}`}</div>
                      <div className={muted}>Linked but not enrolled in any class yet.</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className={shellCard}>
          <h3 className={sectionTitle}>Class Persona Policy</h3>
          <p className={`${muted} mb-3`}>Assign a default tutor style per class and optionally layer teacher instructions on top.</p>
          {personaError ? <p className="mb-3 text-sm text-destructive">{personaError}</p> : null}
          <div className="grid gap-3">
            <select
              className="rounded-md border border-border bg-background px-3 py-2 text-sm"
              value={selectedPersonaId ?? ""}
              onChange={(event) => setSelectedPersonaId(Number(event.target.value))}
            >
              {personas.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name} • {item.teaching_style}
                </option>
              ))}
            </select>
            <textarea
              className="min-h-28 rounded-md border border-border bg-background px-3 py-2 text-sm"
              value={personaOverlay}
              onChange={(event) => setPersonaOverlay(event.target.value)}
              placeholder="Optional teacher overlay, for example: emphasize evidence-based explanations and short retrieval checks."
            />
            <div className="flex flex-wrap gap-2">
              <Button
                variant="secondary"
                onClick={async () => {
                  if (!selectedPersonaId) return;
                  const data = await apiClient.post<{ preview?: { effective_prompt_preview?: string } }>(
                    "/api/teacher/personas/preview",
                    {
                      persona_id: selectedPersonaId,
                      overlay_instructions: personaOverlay,
                    }
                  );
                  setPersonaPreview(data.preview?.effective_prompt_preview ?? "");
                }}
              >
                Preview Policy
              </Button>
              <Button
                onClick={async () => {
                  if (!selectedClassId || !selectedPersonaId) return;
                  const data = await apiClient.post<{ policy?: ClassPersonaPolicy }>(
                    `/api/teacher/personas/classes/${selectedClassId}`,
                    {
                      persona_id: selectedPersonaId,
                      overlay_instructions: personaOverlay,
                    }
                  );
                  setClassPolicy(data.policy ?? null);
                  setPersonaPreview(data.policy?.effective_prompt_preview ?? "");
                  await refreshClasses();
                }}
                disabled={!selectedClassId || !selectedPersonaId}
              >
                Save Class Persona
              </Button>
            </div>
            <div className="rounded-xl border border-border/70 bg-muted/20 p-3 text-sm">
              <div className="mb-2 font-medium">Current class policy</div>
              <div className={muted}>{classPolicy?.persona_name || "No class persona assigned yet."}</div>
              {personaPreview ? <pre className="mt-3 whitespace-pre-wrap text-xs">{personaPreview}</pre> : null}
            </div>
          </div>
        </section>
      </div>

      <div className={grid2}>
        <section className={shellCard}>
          <h3 className={sectionTitle}>Monitoring And Session Replay</h3>
          <p className={`${muted} mb-3`}>Class analytics, struggling student flags, student drill-down, and read-only session replay.</p>
          {monitoringError ? <p className="mb-3 text-sm text-destructive">{monitoringError}</p> : null}
          {classAnalytics?.summary ? (
            <div className="mb-4 grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
              <div className="rounded-xl border border-border/70 p-3 text-sm">Students: {classAnalytics.summary.student_count}</div>
              <div className="rounded-xl border border-border/70 p-3 text-sm">Active: {classAnalytics.summary.active_students}</div>
              <div className="rounded-xl border border-border/70 p-3 text-sm">Avg Mastery: {classAnalytics.summary.avg_mastery}</div>
              <div className="rounded-xl border border-border/70 p-3 text-sm">Quiz Accuracy: {(classAnalytics.summary.quiz_accuracy * 100).toFixed(1)}%</div>
            </div>
          ) : null}
          <div className="grid gap-3 lg:grid-cols-[1.2fr_0.8fr]">
            <div className="grid gap-2">
              <div className="text-sm font-medium">Students in selected class</div>
              {classAnalytics?.students?.map((item) => (
                <button
                  key={item.student_id}
                  className="rounded-xl border border-border/70 p-3 text-left text-sm transition hover:border-foreground/30"
                  onClick={() => void refreshStudentAnalytics(item.student_id)}
                >
                  <div className="font-medium">{item.display_name || `Student #${item.student_id}`}</div>
                  <div className={muted}>
                    Mastery {item.avg_mastery} • Quiz {(item.quiz_accuracy * 100).toFixed(0)}% • Misconceptions {item.active_misconceptions}
                  </div>
                </button>
              ))}
            </div>
            <div className="grid gap-2">
              <div className="text-sm font-medium">Struggling queue</div>
              {struggling.length === 0 ? <span className={muted}>No flagged students right now.</span> : null}
              {struggling.map((item) => (
                <div key={`${item.class_name}-${item.student_id}`} className="rounded-xl border border-dashed border-border p-3 text-sm">
                  <div className="font-medium">{item.display_name}</div>
                  <div className={muted}>{item.class_name}</div>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {item.flags.map((flag) => (
                      <span key={flag} className="rounded-full bg-muted px-2 py-1 text-xs">
                        {flag}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
          {studentAnalytics?.student ? (
            <div className="mt-4 grid gap-3 rounded-2xl border border-border/70 p-4">
              <div>
                <div className="font-medium">{studentAnalytics.student.display_name}</div>
                <div className={muted}>
                  Classes: {studentAnalytics.summary?.class_count ?? 0} • Sessions: {studentAnalytics.summary?.session_count ?? 0}
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                <select
                  className="min-w-56 rounded-md border border-border bg-background px-3 py-2 text-sm"
                  value={selectedReplaySessionId ?? ""}
                  onChange={async (event) => {
                    const id = Number(event.target.value);
                    setSelectedReplaySessionId(id);
                    const replay = await apiClient.get<SessionReplay>(`/api/teacher/session-replay/${id}`);
                    setSessionReplay(replay);
                  }}
                >
                  {(studentAnalytics.recent_sessions || []).map((session) => (
                    <option key={session.id} value={session.id}>
                      {session.subject || "General"} {session.topic ? `• ${session.topic}` : ""}
                    </option>
                  ))}
                </select>
              </div>
              {sessionReplay?.messages?.length ? (
                <div className="grid gap-2">
                  {sessionReplay.messages.map((message) => (
                    <div key={message.id} className="rounded-xl border border-border/70 p-3 text-sm">
                      <div className="mb-1 text-xs uppercase tracking-wide text-muted-foreground">{message.role}</div>
                      <div className="whitespace-pre-wrap">{message.content}</div>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}
        </section>

        <section className={shellCard}>
          <h3 className={sectionTitle}>Reports And Co-Pilot Drafts</h3>
          <p className={`${muted} mb-3`}>Draft-only intervention suggestions, worksheet ideas, and parent-ready summaries.</p>
          {reportError ? <p className="mb-3 text-sm text-destructive">{reportError}</p> : null}
          <div className="mb-3 grid gap-2">
            <input
              className="rounded-md border border-border bg-background px-3 py-2 text-sm"
              value={copilotTopic}
              onChange={(event) => setCopilotTopic(event.target.value)}
              placeholder="Worksheet topic, for example: Newton's 2nd law"
            />
            <div className="flex flex-wrap gap-2">
              <Button
                variant="secondary"
                onClick={async () => {
                  const data = await apiClient.post<{ draft?: { suggestions?: string[] } }>("/api/teacher/copilot/suggest", {
                    class_id: selectedClassId,
                    student_id: selectedStudentId,
                  });
                  setCopilotSuggestions(data.draft?.suggestions ?? []);
                }}
              >
                Generate Suggestions
              </Button>
              <Button
                variant="secondary"
                onClick={async () => {
                  const data = await apiClient.post<{ draft?: { items?: string[] } }>("/api/teacher/copilot/worksheet", {
                    class_id: selectedClassId,
                    student_id: selectedStudentId,
                    topic: copilotTopic,
                  });
                  setWorksheetDraft(data.draft?.items ?? []);
                }}
              >
                Draft Worksheet
              </Button>
              <Button
                onClick={async () => {
                  await apiClient.post("/api/teacher/reports", {
                    report_type: selectedStudentId ? "parent-summary" : "summary",
                    class_id: selectedClassId,
                    student_id: selectedStudentId,
                    title: selectedStudentId ? "Parent Summary Draft" : "Class Summary Draft",
                  });
                  await refreshReports();
                }}
              >
                Save Draft Report
              </Button>
            </div>
          </div>
          <div className="grid gap-3">
            {copilotSuggestions.length > 0 ? (
              <div className="rounded-xl border border-border/70 p-3 text-sm">
                <div className="mb-2 font-medium">Intervention suggestions</div>
                <ul className="list-disc space-y-1 pl-5">
                  {copilotSuggestions.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            ) : null}
            {worksheetDraft.length > 0 ? (
              <div className="rounded-xl border border-border/70 p-3 text-sm">
                <div className="mb-2 font-medium">Worksheet draft</div>
                <ol className="list-decimal space-y-1 pl-5">
                  {worksheetDraft.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ol>
              </div>
            ) : null}
            <div className="grid gap-2">
              <div className="text-sm font-medium">Saved draft reports</div>
              {reports.length === 0 ? <span className={muted}>No saved reports yet.</span> : null}
              {reports.map((item) => (
                <div key={item.id} className="rounded-xl border border-border/70 p-3 text-sm">
                  <div className="font-medium">{item.title}</div>
                  <div className={muted}>
                    {item.report_type} {item.class_name ? `• ${item.class_name}` : ""} {item.student_name ? `• ${item.student_name}` : ""}
                  </div>
                  {item.body_json?.suggestions?.length ? (
                    <ul className="mt-2 list-disc space-y-1 pl-5">
                      {item.body_json.suggestions.map((suggestion) => (
                        <li key={suggestion}>{suggestion}</li>
                      ))}
                    </ul>
                  ) : null}
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>

      <section className={shellCard}>
        <h3 className={sectionTitle}>Assessments</h3>
        <p className={`${muted} mb-3`}>Create teacher-owned assessments and attach simple question banks.</p>
        {assessmentError ? <p className="mb-3 text-sm text-destructive">{assessmentError}</p> : null}
        <div className="mb-4 grid gap-2 md:grid-cols-[1fr_1fr_auto]">
          <input
            className="rounded-md border border-border bg-background px-3 py-2 text-sm"
            value={assessmentTitle}
            onChange={(event) => setAssessmentTitle(event.target.value)}
            placeholder="Assessment title"
          />
          <input
            className="rounded-md border border-border bg-background px-3 py-2 text-sm"
            value={assessmentSubject}
            onChange={(event) => setAssessmentSubject(event.target.value)}
            placeholder="Subject"
          />
          <Button
            onClick={async () => {
              await apiClient.post("/api/teacher/assessments", {
                title: assessmentTitle,
                subject: assessmentSubject,
                type: "quiz",
              });
              setAssessmentTitle("");
              setAssessmentSubject("");
              await refreshAssessments();
            }}
            disabled={!assessmentTitle.trim()}
          >
            Create Assessment
          </Button>
        </div>
        <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="grid gap-2">
            {assessments.map((item) => (
              <button
                key={item.id}
                className="rounded-xl border border-border/70 p-3 text-left text-sm transition hover:border-foreground/30"
                onClick={() => setSelectedAssessmentId(item.id)}
              >
                <div className="font-medium">{item.title}</div>
                <div className={muted}>
                  {item.subject || "General"} • {item.question_count ?? 0} questions
                </div>
              </button>
            ))}
          </div>
          <div className="grid gap-3">
            <div className="rounded-xl border border-border/70 p-3 text-sm">
              <div className="mb-2 font-medium">{assessmentDetail?.assessment?.title || "Select an assessment"}</div>
              {assessmentDetail?.questions?.map((question) => (
                <div key={question.id} className="mt-2 rounded-lg border border-border/60 p-3">
                  <div className="text-xs uppercase tracking-wide text-muted-foreground">{question.question_type}</div>
                  <div>{question.content}</div>
                </div>
              ))}
            </div>
            {selectedAssessmentId ? (
              <div className="grid gap-2 rounded-xl border border-dashed border-border p-3">
                <textarea
                  className="min-h-24 rounded-md border border-border bg-background px-3 py-2 text-sm"
                  value={questionContent}
                  onChange={(event) => setQuestionContent(event.target.value)}
                  placeholder="Question content"
                />
                <Button
                  variant="secondary"
                  onClick={async () => {
                    if (!selectedAssessmentId) return;
                    await apiClient.post(`/api/teacher/assessments/${selectedAssessmentId}/questions`, {
                      content: questionContent,
                      question_type: "short-answer",
                    });
                    setQuestionContent("");
                    await refreshAssessmentDetail(selectedAssessmentId);
                    await refreshAssessments();
                  }}
                  disabled={!questionContent.trim()}
                >
                  Add Question
                </Button>
              </div>
            ) : null}
          </div>
        </div>
      </section>
    </section>
  );
}
