"use client";

import { Button } from "@/components/ui/button";
import { useAuthContext } from "@/components/auth/auth-context";

type ProtectedRouteProps = {
  children: React.ReactNode;
  allowedRoles?: string[];
};

export function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { isAuthenticated, role, loading, error, startLogin } = useAuthContext();

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

  if (allowedRoles && allowedRoles.length > 0) {
    const normalizedRole = (role || "").toLowerCase();
    const normalizedAllowedRoles = allowedRoles.map((allowedRole) => allowedRole.toLowerCase());
    if (!normalizedRole || !normalizedAllowedRoles.includes(normalizedRole)) {
      return (
        <section className="card">
          <h2>Access Restricted</h2>
          <p>You do not have permission to access this section.</p>
          <p className="error">Required role: {allowedRoles.join(", ")}</p>
        </section>
      );
    }
  }

  return <>{children}</>;
}

