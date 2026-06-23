"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import PageHeader from "@/components/PageHeader";
import AgentCard from "@/components/AgentCard";
import Spinner from "@/components/Spinner";
import EmptyState from "@/components/EmptyState";
import ErrorBanner from "@/components/ErrorBanner";
import { api, ApiError } from "@/lib/api";
import { titleize } from "@/lib/format";
import type { Agent, Business, Paginated } from "@/lib/types";

export default function AgentsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [businessId, setBusinessId] = useState("");

  // run dialog state
  const [runAgent, setRunAgent] = useState<Agent | null>(null);
  const [objective, setObjective] = useState("");
  const [running, setRunning] = useState(false);
  const [runResult, setRunResult] = useState<string | null>(null);
  const [runError, setRunError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [a, b] = await Promise.allSettled([
        api.get<Paginated<Agent>>("/agents", { query: { limit: 100 } }),
        api.get<Paginated<Business>>("/businesses", { query: { limit: 100 } }),
      ]);
      if (a.status === "fulfilled") setAgents(a.value.items);
      else
        setError(
          a.reason instanceof ApiError
            ? a.reason.message
            : "Failed to load agents.",
        );
      if (b.status === "fulfilled") {
        setBusinesses(b.value.items);
        if (b.value.items[0]) setBusinessId(b.value.items[0].id);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const grouped = useMemo(() => {
    const map = new Map<string, Agent[]>();
    for (const a of agents) {
      const list = map.get(a.category) ?? [];
      list.push(a);
      map.set(a.category, list);
    }
    return Array.from(map.entries());
  }, [agents]);

  function openRun(agent: Agent) {
    setRunAgent(agent);
    setObjective("");
    setRunResult(null);
    setRunError(null);
  }

  async function submitRun(e: React.FormEvent) {
    e.preventDefault();
    if (!runAgent || !businessId) return;
    setRunning(true);
    setRunResult(null);
    setRunError(null);
    try {
      const res = await api.post<{ run_id: string; status: string }>(
        `/businesses/${businessId}/agents/${runAgent.agent}/run`,
        { objective },
        { idempotencyKey: "" },
      );
      setRunResult(`Run queued — status: ${res.status}.`);
    } catch (err) {
      setRunError(
        err instanceof ApiError ? err.message : "Could not start the run.",
      );
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Agents"
        description="Your virtual team. Trigger any agent to run against one of your businesses."
      />

      {error ? <ErrorBanner message={error} onRetry={load} /> : null}

      {loading ? (
        <div className="flex h-40 items-center justify-center">
          <Spinner label="Loading agents…" />
        </div>
      ) : agents.length === 0 && !error ? (
        <EmptyState
          title="No agents available"
          description="Your plan's agent catalog will appear here."
        />
      ) : (
        <div className="space-y-8">
          {grouped.map(([category, list]) => (
            <section key={category}>
              <h2 className="mb-3 text-sm font-semibold text-slate-100">
                {titleize(category)}
              </h2>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
                {list.map((agent) => (
                  <AgentCard
                    key={agent.agent}
                    agent={agent}
                    onRun={businesses.length > 0 ? openRun : undefined}
                  />
                ))}
              </div>
            </section>
          ))}
        </div>
      )}

      {businesses.length === 0 && agents.length > 0 ? (
        <p className="text-sm text-muted">
          Create a business to run agents against it.
        </p>
      ) : null}

      {/* Run modal */}
      {runAgent ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
          onClick={() => !running && setRunAgent(null)}
        >
          <div
            className="w-full max-w-lg rounded-xl border border-border bg-bg-card p-6 shadow-card"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="text-base font-semibold text-slate-50">
              Run {runAgent.agent}
            </h2>
            <p className="mt-1 text-sm text-muted">{runAgent.description}</p>

            {runResult ? (
              <div className="mt-4 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 text-sm text-emerald-200">
                {runResult}
              </div>
            ) : null}
            {runError ? (
              <div className="mt-4 rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-200">
                {runError}
              </div>
            ) : null}

            <form onSubmit={submitRun} className="mt-4 space-y-4">
              <div>
                <label htmlFor="run-business" className="label">
                  Business
                </label>
                <select
                  id="run-business"
                  className="input"
                  value={businessId}
                  onChange={(e) => setBusinessId(e.target.value)}
                >
                  {businesses.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="run-objective" className="label">
                  Objective
                </label>
                <textarea
                  id="run-objective"
                  required
                  className="input min-h-[80px]"
                  value={objective}
                  onChange={(e) => setObjective(e.target.value)}
                  placeholder="Validate demand with a landing page and $50/day ad test."
                />
              </div>
              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setRunAgent(null)}
                  disabled={running}
                >
                  Close
                </button>
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={running || !businessId}
                >
                  {running ? "Starting…" : "Run agent"}
                </button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </div>
  );
}
