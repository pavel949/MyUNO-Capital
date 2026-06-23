"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import PageHeader from "@/components/PageHeader";
import OptionsTable from "@/components/OptionsTable";
import ScoreBadge from "@/components/ScoreBadge";
import Spinner from "@/components/Spinner";
import EmptyState from "@/components/EmptyState";
import ErrorBanner from "@/components/ErrorBanner";
import { api, ApiError } from "@/lib/api";
import { titleize } from "@/lib/format";
import type {
  Decision,
  DecisionOption,
  DecisionType,
  Paginated,
} from "@/lib/types";

const ADVISOR_LABELS: Record<string, string> = {
  yc_pmf: "YC PMF",
  tech_feasibility: "Tech Feasibility",
  moonshot_potential: "Moonshot",
  global_scale_ease: "Global Scale",
  monetization_strength: "Monetization",
};

const DECISION_TYPES: { value: DecisionType; label: string }[] = [
  { value: "idea", label: "Idea" },
  { value: "feature", label: "Feature" },
  { value: "channel", label: "Channel" },
  { value: "pricing", label: "Pricing" },
  { value: "tech_stack", label: "Tech Stack" },
];

export default function DecisionsPage() {
  const params = useParams<{ id: string }>();
  const businessId = params.id;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [active, setActive] = useState<Decision | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [selecting, setSelecting] = useState<string | null>(null);

  // create form
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState("");
  const [type, setType] = useState<DecisionType>("idea");
  const [optionNames, setOptionNames] = useState("");
  const [creating, setCreating] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const loadDecisions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<Paginated<Decision>>(
        `/businesses/${businessId}/decisions`,
        { query: { limit: 100 } },
      );
      setDecisions(res.items);
    } catch (err) {
      // The list endpoint may not exist in every deployment; surface a
      // gentle empty state rather than crashing.
      if (err instanceof ApiError && err.status === 404) {
        setDecisions([]);
      } else {
        setError(
          err instanceof ApiError ? err.message : "Failed to load decisions.",
        );
      }
    } finally {
      setLoading(false);
    }
  }, [businessId]);

  useEffect(() => {
    loadDecisions();
  }, [loadDecisions]);

  const openDecision = useCallback(
    async (decisionId: string) => {
      setDetailLoading(true);
      setError(null);
      try {
        const detail = await api.get<Decision>(
          `/businesses/${businessId}/decisions/${decisionId}`,
        );
        // If options weren't included, fetch them separately.
        if (!detail.options || detail.options.length === 0) {
          try {
            const opts = await api.get<Paginated<DecisionOption>>(
              `/businesses/${businessId}/decisions/${decisionId}/options`,
            );
            detail.options = opts.items;
          } catch {
            // ignore — render whatever we have
          }
        }
        setActive(detail);
      } catch (err) {
        setError(
          err instanceof ApiError
            ? err.message
            : "Failed to load that decision.",
        );
      } finally {
        setDetailLoading(false);
      }
    },
    [businessId],
  );

  async function createDecision(e: React.FormEvent) {
    e.preventDefault();
    setCreating(true);
    setFormError(null);
    try {
      const options = optionNames
        .split("\n")
        .map((s) => s.trim())
        .filter(Boolean)
        .map((name) => ({ name }));
      if (options.length < 2) {
        setFormError("Add at least two options (one per line).");
        setCreating(false);
        return;
      }
      const created = await api.post<Decision>(
        `/businesses/${businessId}/decisions`,
        { title, type, options },
        { idempotencyKey: "" },
      );
      setDecisions((prev) => [created, ...prev]);
      setShowForm(false);
      setTitle("");
      setOptionNames("");
      setType("idea");
      openDecision(created.id);
    } catch (err) {
      setFormError(
        err instanceof ApiError ? err.message : "Could not create decision.",
      );
    } finally {
      setCreating(false);
    }
  }

  async function selectOption(option: DecisionOption) {
    if (!active) return;
    setSelecting(option.id);
    setError(null);
    try {
      await api.post(
        `/businesses/${businessId}/decisions/${active.id}/select`,
        { option_id: option.id },
      );
      setActive({
        ...active,
        status: "decided",
        selected_option_id: option.id,
      });
      setDecisions((prev) =>
        prev.map((d) =>
          d.id === active.id
            ? { ...d, status: "decided", selected_option_id: option.id }
            : d,
        ),
      );
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not select that option.",
      );
    } finally {
      setSelecting(null);
    }
  }

  return (
    <div className="space-y-6">
      <Link
        href={`/businesses/${businessId}`}
        className="text-sm text-indigo-300"
      >
        ← Back to business
      </Link>

      <PageHeader
        title="Decision Hub"
        description="Compare options with Risk / Complexity / Potential scores and advisor input — then choose."
        action={
          <button
            className="btn-primary"
            onClick={() => setShowForm((s) => !s)}
          >
            {showForm ? "Close" : "New decision"}
          </button>
        }
      />

      {showForm ? (
        <form onSubmit={createDecision} className="card space-y-4">
          <h2 className="text-sm font-semibold text-slate-100">
            Frame a new decision
          </h2>
          {formError ? (
            <div className="rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-200">
              {formError}
            </div>
          ) : null}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label htmlFor="title" className="label">
                Title
              </label>
              <input
                id="title"
                required
                className="input"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Which idea to build first?"
              />
            </div>
            <div>
              <label htmlFor="type" className="label">
                Type
              </label>
              <select
                id="type"
                className="input"
                value={type}
                onChange={(e) => setType(e.target.value as DecisionType)}
              >
                {DECISION_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <label htmlFor="options" className="label">
              Options (one per line)
            </label>
            <textarea
              id="options"
              className="input min-h-[96px]"
              value={optionNames}
              onChange={(e) => setOptionNames(e.target.value)}
              placeholder={"SaaS A\nInfo Product B\nMarketplace C"}
            />
          </div>
          <button type="submit" className="btn-primary" disabled={creating}>
            {creating ? "Creating…" : "Create & score"}
          </button>
        </form>
      ) : null}

      {error ? <ErrorBanner message={error} onRetry={loadDecisions} /> : null}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[280px_1fr]">
        {/* Decision list */}
        <div className="space-y-2">
          <h2 className="text-xs font-medium uppercase tracking-wide text-muted">
            Decisions
          </h2>
          {loading ? (
            <div className="py-6">
              <Spinner label="Loading…" />
            </div>
          ) : decisions.length === 0 ? (
            <EmptyState
              title="No decisions yet"
              description="Create one to start comparing options."
            />
          ) : (
            <ul className="space-y-2">
              {decisions.map((d) => (
                <li key={d.id}>
                  <button
                    onClick={() => openDecision(d.id)}
                    className={`w-full rounded-lg border px-3 py-2 text-left text-sm transition-colors ${
                      active?.id === d.id
                        ? "border-brand bg-brand-soft/30 text-white"
                        : "border-border bg-bg-card text-slate-200 hover:border-border-subtle"
                    }`}
                  >
                    <div className="font-medium">{d.title}</div>
                    <div className="mt-0.5 text-[11px] capitalize text-muted">
                      {titleize(d.type ?? "decision")} · {d.status}
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Decision detail */}
        <div className="space-y-4">
          {detailLoading ? (
            <div className="flex h-40 items-center justify-center">
              <Spinner label="Loading decision…" />
            </div>
          ) : !active ? (
            <EmptyState
              title="Select a decision"
              description="Pick a decision on the left to see its scored options."
            />
          ) : (
            <>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <h2 className="text-lg font-semibold text-slate-50">
                    {active.title}
                  </h2>
                  <p className="text-xs capitalize text-muted">
                    Status: {active.status}
                  </p>
                </div>
                {active.status === "scoring" ? (
                  <span className="inline-flex items-center gap-2 rounded-full bg-amber-500/15 px-3 py-1 text-xs text-amber-300">
                    <span className="h-2 w-2 animate-pulse rounded-full bg-amber-400" />
                    Agents are still scoring…
                  </span>
                ) : null}
              </div>

              {!active.options || active.options.length === 0 ? (
                <EmptyState
                  title="No options scored yet"
                  description="The IdeaValidationAgent and advisor panel will populate scores shortly."
                />
              ) : (
                <>
                  <OptionsTable
                    options={active.options}
                    selectedOptionId={active.selected_option_id}
                    onSelect={selectOption}
                    selecting={selecting}
                  />

                  {/* Advisor scores + justifications */}
                  <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                    {active.options.map((opt) => (
                      <div key={opt.id} className="card">
                        <div className="flex items-center justify-between">
                          <h3 className="font-semibold text-slate-100">
                            {opt.name}
                          </h3>
                          {opt.overall_call ? (
                            <span className="rounded-md bg-brand-soft/40 px-2 py-0.5 text-[11px] text-indigo-200">
                              {opt.overall_call}
                            </span>
                          ) : null}
                        </div>

                        <div className="mt-3 flex flex-wrap gap-2">
                          <ScoreBadge
                            score={opt.risk}
                            tone="bad"
                            label="Risk"
                          />
                          <ScoreBadge
                            score={opt.complexity}
                            tone="bad"
                            label="Complexity"
                          />
                          <ScoreBadge
                            score={opt.potential}
                            tone="good"
                            label="Potential"
                          />
                        </div>

                        {opt.advisor_scores ? (
                          <div className="mt-3 grid grid-cols-1 gap-1.5 text-xs">
                            {Object.entries(opt.advisor_scores).map(
                              ([k, v]) => (
                                <div
                                  key={k}
                                  className="flex items-center justify-between"
                                >
                                  <span className="text-muted">
                                    {ADVISOR_LABELS[k] ?? titleize(k)}
                                  </span>
                                  <ScoreBadge score={v} tone="good" />
                                </div>
                              ),
                            )}
                          </div>
                        ) : null}

                        {opt.justification ? (
                          <p className="mt-3 text-xs leading-relaxed text-muted">
                            {opt.justification}
                          </p>
                        ) : null}
                      </div>
                    ))}
                  </div>
                </>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
