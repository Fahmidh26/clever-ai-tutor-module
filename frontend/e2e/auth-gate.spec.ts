import { expect, test } from "@playwright/test";

test("shows auth gate when /api/me is unauthorized", async ({ page }) => {
  await page.route("http://localhost:8003/api/me", async (route) => {
    await route.fulfill({
      status: 401,
      contentType: "application/json",
      body: JSON.stringify({ error: "Not authenticated" }),
      headers: {
        "access-control-allow-origin": "*",
      },
    });
  });

  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Authentication Required" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Login with Main Site" })).toBeVisible();
});

