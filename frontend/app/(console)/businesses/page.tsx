"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import PageHeader from "@/components/PageHeader";
import Spinner from "@/components/Spinner";
import EmptyState from "@/components/EmptyState";
import ErrorBanner from "@/components/ErrorBanner";
import { api, ApiError } from "@/lib/api";
import { formatDate, titleize } from "@/lib/format";
import type {
  AutonomyProfile,
  Business,
  CreateBusinessInput,
  Paginated,
} from "@/lib/types";

const MODEL_TEMPLATES = [
  { value: "b2b_saas_micro", label: "B2B SaaS micro-product" },
  { value: "niche_ecommerce", label: "Niche e-commerce" },
  { value: "productized_service", label: "Productized service" },
  { value: "info_product", label: "Info product" },
  { value: "consulting", label: "Consulting" },
];

const AUTONOMY: { value: AutonomyProfile; label: string }[] = [
  { value: "ask_me_first", label: "Ask me first" },
  { value: "guided", label: "Guided autonomy" },
  { value: "autonomous_within_limits", label: "Autonomous within limits" },
];

const STAGE_COLORS: Record<string, string> = {
  ideation: "bg-slate-500/15 text-slate-300",
  validate: "bg-sky-500/15 text-sky-300",
  build: "bg-indigo-500/15 text-indigo-300",
  launch: "bg-violet-500/15 text-violet-300",
  grow: "bg-emerald-500/15 text-emerald-300",
  scale: "bg-teal-500/15 text-teal-300",
  exitprep: "bg-amber-500/15 text-amber-300",
  exit: "bg-rose-500/15 text-rose-300",
};

export default function BusinessesPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [items, setItems] = useState<Business[]>([]);
  const [showForm, setShowForm] = useState(false);

  // form state
  const [name, setName] = useState("");
  const [template, setTemplate] = useState(MODEL_TEMPLATES[0].value);
  const [description, setDescription] = useState("");
  const [autonomy, setAutonomy] = useState<AutonomyProfile>("guided");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<Paginated<Business>>("/businesses", {
        query: { limit: 100 },
      });
      setItems(res.items);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Failed to load businesses.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function createBusiness(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setFormError(null);
    try {
      const body: CreateBusinessInput = {
        name,
        model_template: template,
        description: description || undefined,
        autonomy_profile: autonomy,
      };
      const created = await api.post<Business>("/businesses", body, {
        idempotencyKey: "",
      });
      setItems((prev) => [created, ...prev]);
      setName("");
      setDescription("");
      setAutonomy("guided");
      setTemplate(MODEL_TEMPLATES[0].value);
      setShowForm(false);
    } catch (err) {
      setFormError(
        err instanceof ApiError ? err.message : "Could not create business.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Businesses"
        description="Each business runs its own goals, agents, decisions, and metrics."
        action={
          <button
            className="btn-primary"
            onClick={() => setShowForm((s) => !s)}
          >
            {showForm ? "Close" : "New business"}
          </button>
        }
      />

      {showForm ? (
        <form onSubmit={createBusiness} className="card space-y-4">
          <h2 className="text-sm font-semibold text-slate-100">
            Create a new business
          </h2>
          {formError ? (
            <div className="rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-200">
              {formError}
            </div>
          ) : null}

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label htmlFor="name" className="label">
                Name
              </label>
              <input
                id="name"
                required
                className="input"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="InboxZero SaaS"
              />
            </div>
            <div>
              <label htmlFor="template" className="label">
                Model template
              </label>
              <select
                id="template"
                className="input"
                value={template}
                onChange={(e) => setTemplate(e.target.value)}
              >
                {MODEL_TEMPLATES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label htmlFor="description" className="label">
              Description
            </label>
            <textarea
              id="description"
              className="input min-h-[72px]"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="AI inbox triage for solo consultants."
            />
          </div>

          <div>
            <label htmlFor="autonomy" className="label">
              Autonomy profile
            </label>
            <select
              id="autonomy"
              className="input"
              value={autonomy}
              onChange={(e) => setAutonomy(e.target.value as AutonomyProfile)}
            >
              {AUTONOMY.map((a) => (
                <option key={a.value} value={a.value}>
                  {a.label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex gap-2">
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? "Creating…" : "Create business"}
            </button>
            <button
              type="button"
              className="btn-secondary"
              onClick={() => setShowForm(false)}
            >
              Cancel
            </button>
          </div>
        </form>
      ) : null}

      {error ? <ErrorBanner message={error} onRetry={load} /> : null}

      {loading ? (
        <div className="flex h-40 items-center justify-center">
          <Spinner label="Loading businesses…" />
        </div>
      ) : items.length === 0 && !error ? (
        <EmptyState
          title="No businesses yet"
          description="Create your first business to assemble its virtual team."
          action={
            <button className="btn-primary" onClick={() => setShowForm(true)}>
              New business
            </button>
          }
        />
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {items.map((b) => (
            <Link
              key={b.id}
              href={`/businesses/${b.id}`}
              className="card group transition-colors hover:border-border-subtle"
            >
              <div className="flex items-start justify-between gap-2">
                <h3 className="font-semibold text-slate-50 group-hover:text-white">
                  {b.name}
                </h3>
                <span
                  className={`rounded-full px-2 py-0.5 text-[11px] font-medium capitalize ${
                    STAGE_COLORS[b.stage] ?? "bg-slate-500/15 text-slate-300"
                  }`}
                >
                  {b.stage}
                </span>
              </div>
              {b.description ? (
                <p className="mt-2 line-clamp-2 text-sm text-muted">
                  {b.description}
                </p>
              ) : null}
              <div className="mt-4 flex items-center justify-between text-[11px] text-muted">
                <span>{titleize(b.model_template)}</span>
                <span>Created {formatDate(b.created_at)}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
