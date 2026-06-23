"use client";

import { useRouter } from "next/navigation";
import { clearTokens } from "@/lib/auth";
import type { CurrentUser } from "@/lib/types";

interface TopbarProps {
  user: CurrentUser | null;
}

export function Topbar({ user }: TopbarProps) {
  const router = useRouter();

  function logout() {
    clearTokens();
    router.replace("/login");
  }

  const initials = user?.full_name
    ? user.full_name
        .split(" ")
        .map((p) => p[0])
        .slice(0, 2)
        .join("")
        .toUpperCase()
    : "??";

  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-border bg-bg-subtle/60 px-6 backdrop-blur">
      <div className="text-sm text-muted">
        Welcome back
        {user?.full_name ? (
          <span className="text-slate-200">, {user.full_name}</span>
        ) : null}
      </div>

      <div className="flex items-center gap-3">
        <div className="hidden text-right sm:block">
          <div className="text-sm text-slate-100">
            {user?.email ?? "Account"}
          </div>
          <div className="text-[11px] capitalize text-muted">
            {user?.role ?? "—"}
          </div>
        </div>
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-soft text-xs font-semibold text-white">
          {initials}
        </div>
        <button
          onClick={logout}
          className="rounded-lg border border-border px-3 py-1.5 text-sm text-muted transition-colors hover:border-border-subtle hover:text-slate-100"
        >
          Log out
        </button>
      </div>
    </header>
  );
}

export default Topbar;
