"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAuthContext } from "@/components/auth/auth-context";

export default function AuthCallbackPage() {
  const router = useRouter();
  const { refreshSession } = useAuthContext();
  const called = useRef(false);

  useEffect(() => {
    if (called.current) return;
    called.current = true;

    refreshSession().then(() => {
      router.replace("/");
    });
  }, [refreshSession, router]);

  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
      <p>Signing you in…</p>
    </div>
  );
}
