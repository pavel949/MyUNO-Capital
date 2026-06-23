import type { ReactNode } from "react";

interface MetricCardProps {
  label: string;
  value: ReactNode;
  hint?: string;
  trend?: { value: string; positive?: boolean };
}

export function MetricCard({ label, value, hint, trend }: MetricCardProps) {
  return (
    <div className="rounded-xl border border-border bg-bg-card p-5 shadow-card">
      <div className="text-xs font-medium uppercase tracking-wide text-muted">
        {label}
      </div>
      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-2xl font-semibold text-slate-50">{value}</span>
        {trend ? (
          <span
            className={`text-xs font-medium ${
              trend.positive ? "text-emerald-400" : "text-rose-400"
            }`}
          >
            {trend.value}
          </span>
        ) : null}
      </div>
      {hint ? <div className="mt-1 text-xs text-muted">{hint}</div> : null}
    </div>
  );
}

export default MetricCard;
