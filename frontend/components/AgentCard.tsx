import { titleize } from "@/lib/format";
import type { Agent } from "@/lib/types";

interface AgentCardProps {
  agent: Agent;
  onRun?: (agent: Agent) => void;
  running?: boolean;
}

export function AgentCard({ agent, onRun, running }: AgentCardProps) {
  return (
    <div className="flex h-full flex-col rounded-xl border border-border bg-bg-card p-5 shadow-card">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-50">{agent.agent}</h3>
          <span className="mt-1 inline-block rounded-full bg-bg-elevated px-2 py-0.5 text-[11px] text-muted">
            {titleize(agent.category)}
          </span>
        </div>
        <span className="rounded-md bg-brand-soft/40 px-2 py-0.5 text-[11px] font-medium text-indigo-200">
          {titleize(agent.min_tier)}
        </span>
      </div>

      <p className="mt-3 flex-1 text-sm leading-relaxed text-muted">
        {agent.description}
      </p>

      {agent.required_integrations && agent.required_integrations.length > 0 ? (
        <div className="mt-3 flex flex-wrap gap-1">
          {agent.required_integrations.map((i) => (
            <span
              key={i}
              className="rounded bg-bg-elevated px-1.5 py-0.5 text-[10px] text-muted"
            >
              {titleize(i)}
            </span>
          ))}
        </div>
      ) : null}

      {onRun ? (
        <button
          onClick={() => onRun(agent)}
          disabled={running}
          className="mt-4 inline-flex items-center justify-center rounded-lg bg-brand px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-brand-hover disabled:cursor-not-allowed disabled:opacity-60"
        >
          {running ? "Starting…" : "Run agent"}
        </button>
      ) : null}
    </div>
  );
}

export default AgentCard;
