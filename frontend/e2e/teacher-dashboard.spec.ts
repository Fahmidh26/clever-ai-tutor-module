import { expect, test, type Page } from "@playwright/test";

const apiBase = "http://localhost:8003";

function json(body: unknown) {
  return {
    status: 200,
    contentType: "application/json",
    body: JSON.stringify(body),
    headers: { "access-control-allow-origin": "*" },
  };
}

async function mockJsonRoute(page: Page, path: string, body: unknown) {
  await page.context().route(`**${path}`, async (route) => {
    await route.fulfill(json(body));
  });
}

async function installTeacherApiMocks(page: Page) {
  await mockJsonRoute(page, "/api/me", {
    access_token: "teacher-token",
    role: "teacher",
    user: {
      tutor_user: {
        tutor_user_id: 41,
        role: "teacher",
        grade_level: 8,
      },
    },
  });

  await mockJsonRoute(page, "/api/experts?domain=expert-chat", {
    experts: [
      {
        id: 1,
        name: "Newton Tutor",
        tagline: "Physics-first explanations",
        teaching_style: "Socratic",
        subject_expertise: ["Physics"],
      },
    ],
  });

  await mockJsonRoute(page, "/api/tutor/modes", { modes: [{ id: "teach_me", label: "Teach Me" }] });
  await mockJsonRoute(page, "/api/tutor/sessions?limit=50", { sessions: [] });
  await mockJsonRoute(page, "/api/tutor/progress/student", {
    summary: {
      total_sessions: 2,
      total_tokens: 200,
      total_quiz: 4,
      correct_quiz: 3,
      quiz_accuracy: 0.75,
      mastery_topics: 2,
      avg_mastery: 3.5,
      active_misconceptions: 1,
      due_flashcards: 2,
    },
  });
  await mockJsonRoute(page, "/api/teacher/classes", {
    classes: [
      {
        id: 11,
        name: "Grade 8 Physics A",
        subject: "Physics",
        grade_level: 8,
        invite_code: "PHY8A",
        roster_count: 2,
      },
    ],
  });
  await mockJsonRoute(page, "/api/teacher/kb", {
    knowledge_bases: [
      {
        id: 21,
        name: "Newton Laws Unit",
        subject: "Physics",
        description: "Class notes and worked examples",
        document_count: 2,
      },
    ],
  });
  await mockJsonRoute(page, "/api/teacher/classes/11/roster", {
    roster: [
      {
        enrollment_id: 501,
        student_id: 77,
        display_name: "Student One",
        grade_level: 8,
        status: "active",
      },
    ],
  });
  await mockJsonRoute(page, "/api/tutor/progress/teacher?class_id=11", {
    summary: {
      student_count: 2,
      active_students: 1,
      avg_mastery: 3.8,
      quiz_accuracy: 0.82,
      active_misconceptions: 1,
      total_sessions: 6,
      total_messages: 18,
      kb_messages: 4,
      assigned_kb_count: 1,
    },
  });
}

test("teacher sees teacher dashboard metrics inside the single app shell", async ({ page }) => {
  await installTeacherApiMocks(page);

  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Clever AI Tutor" })).toBeVisible();
  await expect(page.getByText("These are tutor styles and subject tutors, not classroom teachers.")).toBeVisible();
  await expect(page.getByText("Teacher Class Summary")).toBeVisible();
  await expect(page.getByText("Students: 2")).toBeVisible();
  await expect(page.getByText("Messages: 18")).toBeVisible();
  await expect(page.getByText("KB-backed Messages: 4")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Knowledge Base Manager" })).toBeVisible();
  await expect(page.getByText("Grade 8 Physics A")).toBeVisible();
  await expect(page.getByText("Newton Laws Unit")).toBeVisible();
  await expect(page.getByText("My Class Context")).toHaveCount(0);
});
