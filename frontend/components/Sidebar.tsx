"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

interface NavItem {
  href: string;
  label: string;
  icon: string;
}

const NAV: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: "▦" },
  { href: "/businesses", label: "Businesses", icon: "◧" },
  { href: "/businesses?view=decisions", label: "Decision Hub", icon: "⚖" },
  { href: "/agents", label: "Agents", icon: "✦" },
  { href: "/integrations", label: "Integrations", icon: "⇄" },
  { href: "/activity", label: "Activity", icon: "≣" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-60 shrink-0 flex-col border-r border-border bg-bg-subtle">
      <div className="flex h-16 items-center gap-2 border-b border-border px-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand text-sm font-bold text-white">
          U
        </div>
        <div className="leading-tight">
          <div className="text-sm font-semibold text-slate-50">MyUNO</div>
          <div className="text-[11px] text-muted">Founder Console</div>
        </div>
      </div>

      <nav className="flex-1 space-y-1 p-3">
        {NAV.map((item) => {
          const base = item.href.split("?")[0];
          const active =
            pathname === base ||
            (base !== "/dashboard" && pathname.startsWith(base));
          return (
            <Link
              key={item.label}
              href={item.href}
              className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                active
                  ? "bg-brand-soft/60 text-white"
                  : "text-muted hover:bg-bg-card hover:text-slate-100"
              }`}
            >
              <span className="w-4 text-center text-base" aria-hidden="true">
                {item.icon}
              </span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-border p-4 text-[11px] leading-relaxed text-muted">
        Autonomous AI OS for solo founders.
      </div>
    </aside>
  );
}

export default Sidebar;
