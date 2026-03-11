"use client";

import { Button } from "@/components/ui/button";
import { useAuthContext } from "@/components/auth/auth-context";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading, error, startLogin } = useAuthContext();

  if (loading) {
    return <p>Loading session...</p>;
  }

  if (!isAuthenticated) {
    return (
      <section className="card">
        <h2>Authentication Required</h2>
        <p>Login with the main site to access this page.</p>
        {error ? <p className="error">Error: {error}</p> : null}
        <Button onClick={startLogin}>Login with Main Site</Button>
      </section>
    );
  }

  return <>{children}</>;
}

