"use client";

import { useCallback, useEffect, useState } from "react";
import PageHeader from "@/components/PageHeader";
import Spinner from "@/components/Spinner";
import EmptyState from "@/components/EmptyState";
import ErrorBanner from "@/components/ErrorBanner";
import { api, ApiError } from "@/lib/api";
import { formatDateTime, timeAgo } from "@/lib/format";
import type {
  ActivityEntry,
  ActorType,
  Business,
  Paginated,
} from "@/lib/types";

type ActorFilter = "all" | ActorType;

export default function ActivityPage() {
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [businessId, setBusinessId] = useState("");
  const [entries, setEntries] = useState<ActivityEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<ActorFilter>("all");

  const loadBusinesses = useCallback(async () => {
    try {
      const res = await api.get<Paginated<Business>>("/businesses", {
        query: { limit: 100 },
      });
      setBusinesses(res.items);
      if (res.items[0]) setBusinessId(res.items[0].id);
      else setLoading(false);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Failed to load businesses.",
      );
      setLoading(false);
    }
  }, []);

  const loadActivity = useCallback(async (id: string, actor: ActorFilter) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<Paginated<ActivityEntry>>(
        `/businesses/${id}/activity`,
        {
          query: {
            limit: 50,
            actor_type: actor === "all" ? undefined : actor,
          },
        },
      );
      setEntries(res.items);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Failed to load the activity log.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadBusinesses();
  }, [loadBusinesses]);

  useEffect(() => {
    if (businessId) loadActivity(businessId, filter);
  }, [businessId, filter, loadActivity]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Activity"
        description="Every significant agent and human action — your audit trail for trust and due diligence."
        action={
          businesses.length > 0 ? (
            <select
              className="input w-56"
              value={businessId}
              onChange={(e) => setBusinessId(e.target.value)}
            >
              {businesses.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          ) : undefined
        }
      />

      {businesses.length > 0 ? (
        <div className="flex gap-2">
          {(["all", "agent", "human"] as ActorFilter[]).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`rounded-full px-3 py-1 text-xs font-medium capitalize transition-colors ${
                filter === f
                  ? "bg-brand text-white"
                  : "bg-bg-card text-muted hover:text-slate-200"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      ) : null}

      {error ? (
        <ErrorBanner
          message={error}
          onRetry={() => businessId && loadActivity(businessId, filter)}
        />
      ) : null}

      {businesses.length === 0 && !loading ? (
        <EmptyState
          title="No businesses yet"
          description="Create a business to start building its activity log."
        />
      ) : loading ? (
        <div className="flex h-40 items-center justify-center">
          <Spinner label="Loading activity…" />
        </div>
      ) : entries.length === 0 ? (
        <EmptyState
          title="No activity yet"
          description="Agent and human actions for this business will appear here."
        />
      ) : (
        <div className="card">
          <ol className="relative space-y-5 border-l border-border pl-5">
            {entries.map((entry) => (
              <li key={entry.id} className="relative">
                <span
                  className={`absolute -left-[27px] top-1 flex h-5 w-5 items-center justify-center rounded-full text-[9px] font-bold ${
                    entry.actor_type === "agent"
                      ? "bg-brand-soft text-indigo-100"
                      : "bg-emerald-500/30 text-emerald-200"
                  }`}
                >
                  {entry.actor_type === "agent" ? "AI" : "Y"}
                </span>
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <p className="text-sm text-slate-100">{entry.summary}</p>
                  <span
                    className="text-[11px] text-muted"
                    title={formatDateTime(entry.created_at)}
                  >
                    {timeAgo(entry.created_at)}
                  </span>
                </div>
                <p className="mt-0.5 text-[11px] text-muted">
                  <span className="font-mono">{entry.action}</span>
                  {" · "}
                  <span>{entry.actor_id}</span>
                  {" · "}
                  <span>{entry.target}</span>
                </p>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
