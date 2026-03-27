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

async function installRoleMocks(page: Page, role: "student" | "admin") {
  await mockJsonRoute(page, "/api/me", {
    access_token: `${role}-token`,
    role,
    user: {
      tutor_user: {
        tutor_user_id: role === "student" ? 77 : 1,
        role,
        grade_level: role === "student" ? 7 : 12,
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
      total_sessions: 1,
      total_tokens: 80,
      total_quiz: 1,
      correct_quiz: 1,
      quiz_accuracy: 1,
      mastery_topics: 1,
      avg_mastery: 4,
      active_misconceptions: 0,
      due_flashcards: 1,
    },
  });

  if (role === "student") {
    await mockJsonRoute(page, "/api/tutor/classes", {
      classes: [
        {
          id: 15,
          name: "Grade 7 Science",
          subject: "Science",
          grade_level: 7,
          teacher_name: "Ms. Rivera",
          assigned_kb_count: 1,
          assigned_kbs: [{ id: 99, name: "Forces Basics", document_count: 1 }],
        },
      ],
    });
    return;
  }

  await mockJsonRoute(page, "/api/teacher/classes", {
    classes: [
      {
        id: 11,
        name: "Admin Oversight Class",
        subject: "Physics",
        grade_level: 8,
        invite_code: "ADM11",
        roster_count: 3,
      },
    ],
  });
  await mockJsonRoute(page, "/api/teacher/kb", {
    knowledge_bases: [{ id: 21, name: "Admin KB", subject: "Physics", document_count: 2 }],
  });
  await mockJsonRoute(page, "/api/teacher/classes/11/roster", { roster: [] });
  await mockJsonRoute(page, "/api/tutor/progress/teacher?class_id=11", {
    summary: {
      student_count: 3,
      active_students: 2,
      avg_mastery: 4,
      quiz_accuracy: 0.9,
      active_misconceptions: 1,
      total_sessions: 7,
      total_messages: 20,
      kb_messages: 5,
      assigned_kb_count: 1,
    },
  });
}

test("student stays in student-facing class context and does not see teacher dashboard controls", async ({ page }) => {
  await installRoleMocks(page, "student");

  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Tutor Workspace" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "My Class Context" })).toBeVisible();
  await expect(page.getByText("Teacher: Ms. Rivera")).toBeVisible();
  await expect(page.getByText("Materials: 1")).toBeVisible();
  await expect(page.getByText("Teacher Class Summary")).toHaveCount(0);
});

test("admin remains in the same shell and can see teacher-capable summaries", async ({ page }) => {
  await installRoleMocks(page, "admin");

  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Tutor Workspace" })).toBeVisible();
  await expect(page.getByText("Teacher Class Summary")).toBeVisible();
  await expect(page.getByText("Students: 3")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Knowledge Base Manager" })).toBeVisible();
});
