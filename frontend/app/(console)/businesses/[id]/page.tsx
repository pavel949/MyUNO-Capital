"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import PageHeader from "@/components/PageHeader";
import MetricCard from "@/components/MetricCard";
import Gauge from "@/components/Gauge";
import Spinner from "@/components/Spinner";
import EmptyState from "@/components/EmptyState";
import ErrorBanner from "@/components/ErrorBanner";
import { api, ApiError } from "@/lib/api";
import {
  formatCurrency,
  formatDate,
  formatPercent,
  titleize,
} from "@/lib/format";
import type {
  Agent,
  Business,
  ExitReadiness,
  Goal,
  Metrics,
  Paginated,
} from "@/lib/types";

export default function BusinessDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [business, setBusiness] = useState<Business | null>(null);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [exit, setExit] = useState<ExitReadiness | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);

  // agent run state
  const [selectedAgent, setSelectedAgent] = useState("");
  const [objective, setObjective] = useState("");
  const [running, setRunning] = useState(false);
  const [runMessage, setRunMessage] = useState<string | null>(null);
  const [runError, setRunError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const biz = await api.get<Business>(`/businesses/${id}`);
      setBusiness(biz);

      const [g, m, e, ag] = await Promise.allSettled([
        api.get<Paginated<Goal>>(`/businesses/${id}/goals`),
        api.get<Metrics>(`/businesses/${id}/metrics`, {
          query: { period: "30d" },
        }),
        api.get<ExitReadiness>(`/businesses/${id}/exit-readiness`),
        api.get<Paginated<Agent>>("/agents", { query: { limit: 100 } }),
      ]);

      setGoals(g.status === "fulfilled" ? g.value.items : []);
      setMetrics(m.status === "fulfilled" ? m.value : null);
      setExit(e.status === "fulfilled" ? e.value : null);
      if (ag.status === "fulfilled") {
        setAgents(ag.value.items);
        if (ag.value.items[0]) setSelectedAgent(ag.value.items[0].agent);
      }
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Failed to load this business.",
      );
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  async function triggerRun(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedAgent) return;
    setRunning(true);
    setRunMessage(null);
    setRunError(null);
    try {
      const res = await api.post<{ run_id: string; status: string }>(
        `/businesses/${id}/agents/${selectedAgent}/run`,
        { objective },
        { idempotencyKey: "" },
      );
      setRunMessage(
        `Run queued (${selectedAgent}) — status: ${res.status}. Track it in the Activity log.`,
      );
      setObjective("");
    } catch (err) {
      setRunError(
        err instanceof ApiError
          ? err.message
          : "Could not start the agent run.",
      );
    } finally {
      setRunning(false);
    }
  }

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Spinner label="Loading business…" />
      </div>
    );
  }

  if (error && !business) {
    return (
      <div className="space-y-4">
        <Link href="/businesses" className="text-sm text-indigo-300">
          ← Back to businesses
        </Link>
        <ErrorBanner message={error} onRetry={load} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Link href="/businesses" className="text-sm text-indigo-300">
        ← Back to businesses
      </Link>

      <PageHeader
        title={business?.name ?? "Business"}
        description={
          business?.description ?? titleize(business?.model_template ?? "")
        }
        action={
          <div className="flex items-center gap-2">
            <span className="rounded-full bg-bg-elevated px-3 py-1 text-xs capitalize text-slate-200">
              Stage: {business?.stage}
            </span>
            <Link
              href={`/businesses/${id}/decisions`}
              className="btn-secondary"
            >
              Decision Hub
            </Link>
          </div>
        }
      />

      {error ? <ErrorBanner message={error} onRetry={load} /> : null}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="MRR"
          value={formatCurrency(metrics?.mrr ?? 0)}
          trend={
            metrics
              ? {
                  value: formatPercent(metrics.mrr_growth_pct),
                  positive: (metrics.mrr_growth_pct ?? 0) >= 0,
                }
              : undefined
          }
        />
        <MetricCard
          label="Churn"
          value={metrics ? `${(metrics.churn_rate_pct ?? 0).toFixed(1)}%` : "—"}
        />
        <MetricCard label="CAC" value={formatCurrency(metrics?.cac ?? 0)} />
        <MetricCard
          label="LTV"
          value={formatCurrency(metrics?.ltv ?? 0)}
          hint={
            metrics
              ? `LTV/CAC ${(metrics.ltv_cac_ratio ?? 0).toFixed(1)}×`
              : undefined
          }
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Goals */}
        <div className="card lg:col-span-2">
          <h2 className="mb-3 text-sm font-semibold text-slate-100">Goals</h2>
          {goals.length === 0 ? (
            <EmptyState
              title="No goals yet"
              description="Goals turn into OKRs and roadmaps via the StrategyAgent."
            />
          ) : (
            <ul className="space-y-3">
              {goals.map((goal) => (
                <li
                  key={goal.id}
                  className="flex items-start justify-between gap-4 rounded-lg border border-border bg-bg-subtle/40 p-3"
                >
                  <div>
                    <p className="text-sm font-medium text-slate-100">
                      {goal.title}
                    </p>
                    <p className="mt-0.5 text-[11px] text-muted">
                      {goal.metric.toUpperCase()} target{" "}
                      {goal.metric === "mrr"
                        ? formatCurrency(goal.target_value)
                        : goal.target_value}{" "}
                      · by {formatDate(goal.target_date)}
                    </p>
                  </div>
                  <span className="rounded-full bg-bg-elevated px-2 py-0.5 text-[11px] capitalize text-muted">
                    {goal.status}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Exit readiness */}
        <div className="card flex flex-col items-center">
          <h2 className="mb-2 self-start text-sm font-semibold text-slate-100">
            Exit Readiness
          </h2>
          {exit ? (
            <>
              <Gauge value={exit.exit_readiness_score} />
              <div className="mt-2 w-full space-y-1.5 text-xs">
                {Object.entries(exit.components).map(([k, v]) => (
                  <div key={k} className="flex items-center justify-between">
                    <span className="capitalize text-muted">{titleize(k)}</span>
                    <span className="text-slate-200">{v}</span>
                  </div>
                ))}
              </div>
              <p className="mt-3 text-center text-[11px] text-muted">
                {exit.recommendation}
              </p>
            </>
          ) : (
            <div className="py-6">
              <EmptyState title="Not scored yet" />
            </div>
          )}
        </div>
      </div>

      {/* Trigger agent run */}
      <div className="card">
        <h2 className="mb-3 text-sm font-semibold text-slate-100">
          Trigger an agent run
        </h2>
        {runMessage ? (
          <div className="mb-3 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 text-sm text-emerald-200">
            {runMessage}
          </div>
        ) : null}
        {runError ? (
          <div className="mb-3 rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-200">
            {runError}
          </div>
        ) : null}
        <form
          onSubmit={triggerRun}
          className="grid grid-cols-1 gap-4 md:grid-cols-[220px_1fr_auto] md:items-end"
        >
          <div>
            <label htmlFor="agent" className="label">
              Agent
            </label>
            <select
              id="agent"
              className="input"
              value={selectedAgent}
              onChange={(e) => setSelectedAgent(e.target.value)}
              disabled={agents.length === 0}
            >
              {agents.length === 0 ? (
                <option value="">No agents available</option>
              ) : (
                agents.map((a) => (
                  <option key={a.agent} value={a.agent}>
                    {a.agent}
                  </option>
                ))
              )}
            </select>
          </div>
          <div>
            <label htmlFor="objective" className="label">
              Objective
            </label>
            <input
              id="objective"
              required
              className="input"
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              placeholder="Validate demand with a landing page and $50/day ad test."
            />
          </div>
          <button
            type="submit"
            className="btn-primary"
            disabled={running || !selectedAgent}
          >
            {running ? "Starting…" : "Run"}
          </button>
        </form>
      </div>
    </div>
  );
}
