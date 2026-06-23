import ScoreBadge from "./ScoreBadge";
import type { DecisionOption } from "@/lib/types";

interface OptionsTableProps {
  options: DecisionOption[];
  selectedOptionId?: string;
  onSelect?: (option: DecisionOption) => void;
  selecting?: string | null;
  readOnly?: boolean;
}

export function OptionsTable({
  options,
  selectedOptionId,
  onSelect,
  selecting,
  readOnly,
}: OptionsTableProps) {
  return (
    <div className="overflow-x-auto rounded-xl border border-border bg-bg-card shadow-card">
      <table className="w-full min-w-[760px] border-collapse text-sm">
        <thead>
          <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted">
            <th className="px-4 py-3 font-medium">Option</th>
            <th className="px-4 py-3 font-medium">Risk</th>
            <th className="px-4 py-3 font-medium">Complexity</th>
            <th className="px-4 py-3 font-medium">Potential</th>
            <th className="px-4 py-3 font-medium">Time to Impact</th>
            <th className="px-4 py-3 font-medium">Capital</th>
            <th className="px-4 py-3 font-medium">AI Recommendation</th>
            {!readOnly ? (
              <th className="px-4 py-3 font-medium">Your Choice</th>
            ) : null}
          </tr>
        </thead>
        <tbody>
          {options.map((opt) => {
            const chosen = opt.id === selectedOptionId;
            return (
              <tr
                key={opt.id}
                className={`border-b border-border/60 last:border-0 ${
                  chosen ? "bg-emerald-500/5" : ""
                }`}
              >
                <td className="px-4 py-3">
                  <div className="font-medium text-slate-100">{opt.name}</div>
                  {opt.overall_call ? (
                    <div className="mt-0.5 text-[11px] text-indigo-300">
                      {opt.overall_call}
                    </div>
                  ) : null}
                </td>
                <td className="px-4 py-3">
                  <ScoreBadge score={opt.risk} tone="bad" />
                </td>
                <td className="px-4 py-3">
                  <ScoreBadge score={opt.complexity} tone="bad" />
                </td>
                <td className="px-4 py-3">
                  <ScoreBadge score={opt.potential} tone="good" />
                </td>
                <td className="px-4 py-3 text-muted">
                  {opt.time_to_impact ?? "—"}
                </td>
                <td className="px-4 py-3 text-muted">
                  {opt.capital_required ?? "—"}
                </td>
                <td className="px-4 py-3 text-slate-200">
                  {opt.ai_recommendation ?? "—"}
                </td>
                {!readOnly ? (
                  <td className="px-4 py-3">
                    {chosen ? (
                      <span className="inline-flex items-center gap-1 rounded-md bg-emerald-500/15 px-2 py-1 text-xs font-medium text-emerald-300 ring-1 ring-emerald-500/30">
                        ✓ Selected
                      </span>
                    ) : (
                      <button
                        onClick={() => onSelect?.(opt)}
                        disabled={!!selecting}
                        className="rounded-md border border-brand/60 bg-brand/10 px-3 py-1 text-xs font-medium text-indigo-200 transition-colors hover:bg-brand/20 disabled:opacity-50"
                      >
                        {selecting === opt.id ? "Selecting…" : "Select"}
                      </button>
                    )}
                  </td>
                ) : null}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default OptionsTable;
