"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import PageHeader from "@/components/PageHeader";
import MetricCard from "@/components/MetricCard";
import Gauge from "@/components/Gauge";
import Spinner from "@/components/Spinner";
import EmptyState from "@/components/EmptyState";
import ErrorBanner from "@/components/ErrorBanner";
import { api, ApiError } from "@/lib/api";
import {
  formatCurrency,
  formatNumber,
  formatPercent,
  timeAgo,
} from "@/lib/format";
import type {
  ActivityEntry,
  Business,
  ExitReadiness,
  Metrics,
  Paginated,
} from "@/lib/types";

export default function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [business, setBusiness] = useState<Business | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [exit, setExit] = useState<ExitReadiness | null>(null);
  const [activity, setActivity] = useState<ActivityEntry[]>([]);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const list = await api.get<Paginated<Business>>("/businesses", {
        query: { limit: 1 },
      });
      const first = list.items[0] ?? null;
      setBusiness(first);

      if (!first) {
        setMetrics(null);
        setExit(null);
        setActivity([]);
        return;
      }

      const [m, e, a] = await Promise.allSettled([
        api.get<Metrics>(`/businesses/${first.id}/metrics`, {
          query: { period: "30d" },
        }),
        api.get<ExitReadiness>(`/businesses/${first.id}/exit-readiness`),
        api.get<Paginated<ActivityEntry>>(`/businesses/${first.id}/activity`, {
          query: { limit: 8 },
        }),
      ]);

      setMetrics(m.status === "fulfilled" ? m.value : null);
      setExit(e.status === "fulfilled" ? e.value : null);
      setActivity(a.status === "fulfilled" ? a.value.items : []);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Failed to load the dashboard.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Spinner label="Loading dashboard…" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard"
        description={
          business
            ? `Overview for ${business.name}`
            : "Your founder overview at a glance."
        }
      />

      {error ? <ErrorBanner message={error} onRetry={load} /> : null}

      {!business && !error ? (
        <EmptyState
          title="No businesses yet"
          description="Create your first business to start tracking metrics, decisions, and agent activity."
          action={
            <Link href="/businesses" className="btn-primary">
              Create a business
            </Link>
          }
        />
      ) : null}

      {business ? (
        <>
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
              hint="Monthly recurring revenue"
            />
            <MetricCard
              label="Churn"
              value={
                metrics ? `${(metrics.churn_rate_pct ?? 0).toFixed(1)}%` : "—"
              }
              hint="Monthly churn rate"
            />
            <MetricCard
              label="CAC"
              value={formatCurrency(metrics?.cac ?? 0)}
              hint="Customer acquisition cost"
            />
            <MetricCard
              label="LTV"
              value={formatCurrency(metrics?.ltv ?? 0)}
              hint={
                metrics
                  ? `LTV/CAC ${(metrics.ltv_cac_ratio ?? 0).toFixed(1)}×`
                  : "Lifetime value"
              }
            />
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <div className="card flex flex-col items-center justify-center lg:col-span-1">
              <h2 className="mb-2 self-start text-sm font-semibold text-slate-100">
                Exit Readiness
              </h2>
              {exit ? (
                <>
                  <Gauge value={exit.exit_readiness_score} />
                  <p className="mt-1 text-center text-xs text-muted">
                    {exit.recommendation}
                  </p>
                </>
              ) : (
                <div className="py-8">
                  <EmptyState
                    title="Not scored yet"
                    description="The ExitPlanningAgent will compute this as data accrues."
                  />
                </div>
              )}
            </div>

            <div className="card lg:col-span-2">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-sm font-semibold text-slate-100">
                  Recent activity
                </h2>
                <Link
                  href="/activity"
                  className="text-xs text-indigo-300 hover:underline"
                >
                  View all
                </Link>
              </div>
              {activity.length === 0 ? (
                <EmptyState
                  title="No activity yet"
                  description="Agent and human actions will appear here."
                />
              ) : (
                <ul className="divide-y divide-border/60">
                  {activity.map((entry) => (
                    <li key={entry.id} className="flex items-start gap-3 py-3">
                      <span
                        className={`mt-0.5 inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10px] font-semibold ${
                          entry.actor_type === "agent"
                            ? "bg-brand-soft/50 text-indigo-200"
                            : "bg-emerald-500/15 text-emerald-300"
                        }`}
                      >
                        {entry.actor_type === "agent" ? "AI" : "You"}
                      </span>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm text-slate-200">
                          {entry.summary}
                        </p>
                        <p className="text-[11px] text-muted">
                          {entry.action} · {timeAgo(entry.created_at)}
                        </p>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {metrics ? (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <MetricCard
                label="Signups"
                value={formatNumber(metrics.signups)}
                hint="New signups in period"
              />
              <MetricCard
                label="NPS"
                value={formatNumber(metrics.nps)}
                hint="Net promoter score"
              />
              <MetricCard
                label="LTV / CAC"
                value={`${(metrics.ltv_cac_ratio ?? 0).toFixed(1)}×`}
                hint="Unit economics health"
              />
            </div>
          ) : null}
        </>
      ) : null}
    </div>
  );
}
