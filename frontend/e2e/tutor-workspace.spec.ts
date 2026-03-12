import { expect, test } from "@playwright/test";

test("authenticated user can stream a tutor response", async ({ page }) => {
  let createdSessionId = 101;

  await page.route("http://localhost:8003/api/me", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        access_token: "mock-token",
        role: "student",
        user: {
          tutor_user: {
            tutor_user_id: 77,
            role: "student",
            grade_level: 7,
          },
        },
      }),
      headers: { "access-control-allow-origin": "*" },
    });
  });

  await page.route("http://localhost:8003/api/experts?domain=expert-chat", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        experts: [{ id: 1, name: "Newton Tutor" }],
      }),
      headers: { "access-control-allow-origin": "*" },
    });
  });

  await page.route("http://localhost:8003/api/tutor/modes", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        modes: [{ id: "teach_me", label: "Teach Me" }],
      }),
      headers: { "access-control-allow-origin": "*" },
    });
  });

  await page.route("http://localhost:8003/api/tutor/sessions?limit=50", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        sessions: [{ id: createdSessionId, persona_id: 1, persona_name: "Newton Tutor", mode: "teach_me" }],
      }),
      headers: { "access-control-allow-origin": "*" },
    });
  });

  await page.route("http://localhost:8003/api/tutor/sessions/101", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        session: { id: 101, persona_id: 1, mode: "teach_me" },
        messages: [],
      }),
      headers: { "access-control-allow-origin": "*" },
    });
  });

  await page.route("http://localhost:8003/api/tutor/sessions", async (route) => {
    if (route.request().method() === "POST") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ session: { id: createdSessionId } }),
        headers: { "access-control-allow-origin": "*" },
      });
      return;
    }
    await route.fallback();
  });

  await page.route("http://localhost:8003/api/expert-chat/stream", async (route) => {
    const sseBody = [
      'event: stream_start\ndata: {"session_id":101}\n\n',
      "event: token\ndata: {\"content\":\"Newton's second law says force equals mass times acceleration.\"}\n\n",
      'event: stream_end\ndata: {"session_id":101,"tokens_used":25}\n\n',
    ].join("");
    await route.fulfill({
      status: 200,
      contentType: "text/event-stream",
      body: sseBody,
      headers: {
        "cache-control": "no-cache",
        "access-control-allow-origin": "*",
      },
    });
  });

  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Tutor Workspace" })).toBeVisible();

  await page.getByPlaceholder("Ask your tutor...").fill("Explain Newton second law");
  await page.getByRole("button", { name: "Send Message" }).click();

  await expect(page.getByText("Newton's second law says force equals mass times acceleration.")).toBeVisible();
});
