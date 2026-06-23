"use client";

import { useCallback, useEffect, useState } from "react";
import PageHeader from "@/components/PageHeader";
import Spinner from "@/components/Spinner";
import EmptyState from "@/components/EmptyState";
import ErrorBanner from "@/components/ErrorBanner";
import { api, ApiError } from "@/lib/api";
import { formatDate, titleize } from "@/lib/format";
import type {
  Business,
  ConnectIntegrationResponse,
  Integration,
  Paginated,
} from "@/lib/types";

const CATEGORY_ICON: Record<string, string> = {
  payments: "$",
  ads: "◎",
  source_control: "{ }",
  email: "✉",
  analytics: "▲",
};

export default function IntegrationsPage() {
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [businessId, setBusinessId] = useState("");
  const [items, setItems] = useState<Integration[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

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

  const loadIntegrations = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<Paginated<Integration>>(
        `/businesses/${id}/integrations`,
        { query: { limit: 100 } },
      );
      setItems(res.items);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Failed to load integrations.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadBusinesses();
  }, [loadBusinesses]);

  useEffect(() => {
    if (businessId) loadIntegrations(businessId);
  }, [businessId, loadIntegrations]);

  async function connect(provider: string) {
    setBusy(provider);
    setError(null);
    try {
      const res = await api.post<ConnectIntegrationResponse>(
        `/businesses/${businessId}/integrations/${provider}/connect`,
        {
          redirect_uri:
            typeof window !== "undefined"
              ? `${window.location.origin}/integrations`
              : undefined,
        },
      );
      if (res.authorization_url) {
        window.location.assign(res.authorization_url);
        return;
      }
      await loadIntegrations(businessId);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Could not start the connect flow.",
      );
    } finally {
      setBusy(null);
    }
  }

  async function disconnect(provider: string) {
    setBusy(provider);
    setError(null);
    try {
      await api.del(
        `/businesses/${businessId}/integrations/${provider}/disconnect`,
      );
      setItems((prev) =>
        prev.map((i) =>
          i.provider === provider
            ? { ...i, status: "available", connected_at: undefined }
            : i,
        ),
      );
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not disconnect.");
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Integrations"
        description="Connect the tools your agents act through — payments, ads, repos, email, and more."
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

      {error ? (
        <ErrorBanner
          message={error}
          onRetry={() => businessId && loadIntegrations(businessId)}
        />
      ) : null}

      {businesses.length === 0 && !loading ? (
        <EmptyState
          title="No businesses yet"
          description="Create a business first to manage its integrations."
        />
      ) : loading ? (
        <div className="flex h-40 items-center justify-center">
          <Spinner label="Loading integrations…" />
        </div>
      ) : items.length === 0 ? (
        <EmptyState
          title="No integrations available"
          description="Available connectors for this business will appear here."
        />
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {items.map((integration) => {
            const connected = integration.status === "connected";
            return (
              <div key={integration.provider} className="card flex flex-col">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-bg-elevated text-sm text-indigo-200">
                      {CATEGORY_ICON[integration.category] ?? "◆"}
                    </span>
                    <div>
                      <h3 className="text-sm font-semibold text-slate-50">
                        {titleize(integration.provider)}
                      </h3>
                      <p className="text-[11px] text-muted">
                        {titleize(integration.category)}
                      </p>
                    </div>
                  </div>
                  <span
                    className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${
                      connected
                        ? "bg-emerald-500/15 text-emerald-300"
                        : integration.status === "error"
                          ? "bg-rose-500/15 text-rose-300"
                          : "bg-slate-500/15 text-slate-300"
                    }`}
                  >
                    {titleize(integration.status)}
                  </span>
                </div>

                {connected && integration.connected_at ? (
                  <p className="mt-3 text-[11px] text-muted">
                    Connected {formatDate(integration.connected_at)}
                  </p>
                ) : null}

                <div className="mt-4">
                  {connected ? (
                    <button
                      className="btn-secondary w-full"
                      onClick={() => disconnect(integration.provider)}
                      disabled={busy === integration.provider}
                    >
                      {busy === integration.provider
                        ? "Disconnecting…"
                        : "Disconnect"}
                    </button>
                  ) : (
                    <button
                      className="btn-primary w-full"
                      onClick={() => connect(integration.provider)}
                      disabled={busy === integration.provider}
                    >
                      {busy === integration.provider
                        ? "Connecting…"
                        : "Connect"}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
