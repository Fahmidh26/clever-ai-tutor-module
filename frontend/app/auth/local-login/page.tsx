"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ApiError, createApiClient } from "@/lib/api-client";
import { useAuthContext } from "@/components/auth/auth-context";

type LocalAccount = {
  email?: string;
  display_name?: string;
  role?: string;
  grade_level?: number | null;
};

type LocalAccountsPayload = {
  auth_mode?: string;
  password_hint?: string;
  accounts?: LocalAccount[];
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8003";

export default function LocalLoginPage() {
  const router = useRouter();
  const { authMode, refreshSession } = useAuthContext();
  const apiClient = useMemo(() => createApiClient({ baseUrl: apiBaseUrl }), []);

  const [accounts, setAccounts] = useState<LocalAccount[]>([]);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("devpass123");
  const [passwordHint, setPasswordHint] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (authMode !== "local_dev") {
      router.replace("/");
      return;
    }

    let active = true;
    const loadAccounts = async () => {
      try {
        setLoading(true);
        setError("");
        const data = await apiClient.get<LocalAccountsPayload>("/api/local-auth/accounts");
        if (!active) return;
        const list = Array.isArray(data.accounts) ? data.accounts : [];
        setAccounts(list);
        setPasswordHint(typeof data.password_hint === "string" ? data.password_hint : "");
        if (!email && list.length > 0 && typeof list[0].email === "string") {
          setEmail(list[0].email);
        }
      } catch (err) {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Failed to load local dev accounts");
      } finally {
        if (active) setLoading(false);
      }
    };

    void loadAccounts();
    return () => {
      active = false;
    };
  }, [apiClient, authMode, email, router]);

  const submitLogin = async () => {
    try {
      setSubmitting(true);
      setError("");
      await apiClient.post("/api/local-auth/login", { email, password });
      await refreshSession();
      router.replace("/");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError(err instanceof Error ? err.message : "Login failed");
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (authMode !== "local_dev") {
    return null;
  }

  return (
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: "24px" }}>
      <section style={{ width: "100%", maxWidth: "720px", display: "grid", gap: "16px" }}>
        <div>
          <h1>Local Dev Login</h1>
          <p>Use a temporary tutor account so development can continue without the main-site API.</p>
          {passwordHint ? <p>{passwordHint}</p> : null}
        </div>

        <div style={{ border: "1px solid var(--border)", borderRadius: "12px", padding: "16px", display: "grid", gap: "12px" }}>
          <label style={{ display: "grid", gap: "6px" }}>
            <span>Account</span>
            <select value={email} onChange={(event) => setEmail(event.target.value)} disabled={loading || submitting}>
              <option value="">Select a local account</option>
              {accounts.map((account) => {
                const accountEmail = typeof account.email === "string" ? account.email : "";
                const displayName = typeof account.display_name === "string" ? account.display_name : accountEmail;
                const role = typeof account.role === "string" ? account.role : "user";
                return (
                  <option key={accountEmail} value={accountEmail}>
                    {displayName} ({role})
                  </option>
                );
              })}
            </select>
          </label>

          <label style={{ display: "grid", gap: "6px" }}>
            <span>Password</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter local dev password"
              disabled={submitting}
            />
          </label>

          {loading ? <p>Loading local accounts...</p> : null}
          {error ? <p className="error">Error: {error}</p> : null}

          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
            <Button onClick={submitLogin} disabled={submitting || !email || !password}>
              {submitting ? "Signing In..." : "Sign In"}
            </Button>
            <Button variant="secondary" onClick={() => router.replace("/")} disabled={submitting}>
              Back
            </Button>
          </div>
        </div>

        {accounts.length > 0 ? (
          <section style={{ border: "1px solid var(--border)", borderRadius: "12px", padding: "16px", display: "grid", gap: "8px" }}>
            <h2>Seeded Accounts</h2>
            {accounts.map((account) => {
              const accountEmail = typeof account.email === "string" ? account.email : "";
              const displayName = typeof account.display_name === "string" ? account.display_name : accountEmail;
              const role = typeof account.role === "string" ? account.role : "user";
              const grade = typeof account.grade_level === "number" ? `, grade ${account.grade_level}` : "";
              return (
                <div key={accountEmail}>
                  <strong>{displayName}</strong> - {role} - {accountEmail}
                  {grade}
                </div>
              );
            })}
          </section>
        ) : null}
      </section>
    </main>
  );
}
