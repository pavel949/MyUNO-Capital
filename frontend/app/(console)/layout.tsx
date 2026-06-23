"use client";

import { useEffect, useState, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import Topbar from "@/components/Topbar";
import Spinner from "@/components/Spinner";
import { api, ApiError } from "@/lib/api";
import { isLoggedIn } from "@/lib/auth";
import type { CurrentUser } from "@/lib/types";

export default function ConsoleLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [user, setUser] = useState<CurrentUser | null>(null);

  useEffect(() => {
    if (!isLoggedIn()) {
      router.replace("/login");
      return;
    }
    let cancelled = false;
    // Best-effort fetch of the current user; the api wrapper already
    // redirects to /login on 401. Render the shell regardless so other
    // failures (e.g. backend down) don't trap the user on a blank screen.
    api
      .get<CurrentUser>("/auth/me")
      .then((u) => {
        if (!cancelled) setUser(u);
      })
      .catch((err) => {
        if (!(err instanceof ApiError) || err.status !== 401) {
          // Non-auth error: keep the shell usable.
        }
      })
      .finally(() => {
        if (!cancelled) setReady(true);
      });
    return () => {
      cancelled = true;
    };
  }, [router]);

  if (!ready) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Spinner label="Loading your console…" />
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Topbar user={user} />
        <main className="flex-1 overflow-y-auto p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
