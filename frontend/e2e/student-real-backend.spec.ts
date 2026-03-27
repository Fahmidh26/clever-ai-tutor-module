import { expect, test } from "@playwright/test";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8003";

test("real backend student flow covers class context, session, quiz, and dashboard", async ({ page, request }) => {
  test.setTimeout(60000);
  const healthResponse = await request.get(`${apiBase}/health`);
  test.skip(!healthResponse.ok(), `Real backend is unavailable at ${apiBase}`);
  const health = (await healthResponse.json()) as { db?: { status?: string } };
  test.skip(health.db?.status !== "ok", "Real backend database is not ready for the seeded student flow.");

  const loginRoute = await request.get(`${apiBase}/api/local-auth/accounts`);
  test.skip(!loginRoute.ok(), "Local-dev auth is unavailable; enable AUTH_MODE=local_dev for real-backend e2e.");

  await page.goto("/auth/local-login");

  await expect(page.getByRole("heading", { name: "Local Dev Login" })).toBeVisible();
  await page.getByLabel("Account").selectOption("student@local.dev");
  await page.getByLabel("Password").fill("devpass123");
  await page.getByRole("button", { name: "Sign In" }).click();

  await expect(page.getByRole("heading", { name: "Tutor Workspace" })).toBeVisible({ timeout: 20000 });

  const classContext = page.locator("section").filter({
    has: page.getByRole("heading", { name: "My Class Context" }),
  });
  await expect(page.getByRole("heading", { name: "My Class Context" })).toBeVisible();
  await expect(classContext.getByText("Class: Grade 8 Physics A")).toBeVisible({ timeout: 20000 });
  await expect(classContext.getByText("Teacher: Teacher Demo")).toBeVisible({ timeout: 20000 });
  await expect(classContext.getByText("Materials: 1")).toBeVisible({ timeout: 20000 });
  await expect(classContext.locator("option").filter({ hasText: "Newton Laws Unit" })).toHaveCount(1, { timeout: 20000 });

  await expect(page.getByText("Session History")).toBeVisible();
  const existingSession = page.locator("button").filter({ hasText: /^#\d+/ }).first();
  await expect(existingSession).toBeVisible();
  await existingSession.click();

  const workspace = page.locator("section").filter({
    has: page.getByRole("heading", { name: "Tutor Workspace" }),
  });
  const modeSelect = page.locator("select").nth(3);

  await modeSelect.evaluate((element) => {
    const select = element as HTMLSelectElement;
    select.selectedIndex = 0;
    select.dispatchEvent(new Event("change", { bubbles: true }));
  });
  await expect(modeSelect).toHaveValue("teach_me");

  await workspace.getByRole("button", { name: "New Session Draft" }).click();
  await workspace.getByPlaceholder("Ask your tutor...").fill("Help me understand Newton's second law.");
  await workspace.getByRole("button", { name: "Send Message" }).click();
  await expect(workspace.getByText(/Let's work through this carefully:/)).toBeVisible({ timeout: 15000 });
  await workspace.getByRole("button", { name: "New Session Draft" }).click();
  await modeSelect.evaluate((element) => {
    const select = element as HTMLSelectElement;
    select.selectedIndex = 1;
    select.dispatchEvent(new Event("change", { bubbles: true }));
  });
  await expect(modeSelect).toHaveValue("quiz_me");
  await workspace.getByPlaceholder("Ask your tutor...").fill("Quiz me on Newton's second law.");
  await workspace.getByRole("button", { name: "Generate Quiz Question" }).click();
  await expect(workspace.getByText(/Active quiz difficulty:/)).toBeVisible();
  await workspace.getByRole("button", { name: /^A\./ }).click();
  await expect(workspace.getByRole("button", { name: "Explain My Answer" })).toBeVisible();

  await page.getByRole("button", { name: "Refresh Student Dashboard" }).click();
  await expect(page.getByText("Student Summary")).toBeVisible();
  await expect(page.getByText(/Sessions:/)).toBeVisible();
  await expect(page.getByText(/Avg Mastery:/)).toBeVisible();
  await expect(page.getByText(/Active Misconceptions:/)).toBeVisible();

  const masterySection = page.locator("section").filter({
    has: page.getByRole("heading", { name: "Mastery Tracking" }),
  });
  const misconceptionSection = page.locator("section").filter({
    has: page.getByRole("heading", { name: "Misconception Detection" }),
  });
  await expect(page.getByRole("heading", { name: "Mastery Tracking" })).toBeVisible();
  await expect(masterySection.getByText("Physics - Newton's 2nd Law").first()).toBeVisible();
  await expect(page.getByRole("heading", { name: "Misconception Detection" })).toBeVisible();
  await expect(misconceptionSection.getByText(/formula-confusion/i)).toBeVisible();
});
