"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { isLoggedIn, setTokens } from "@/lib/auth";
import type { RegisterResponse } from "@/lib/types";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [tenantName, setTenantName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isLoggedIn()) router.replace("/dashboard");
  }, [router]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await api.post<RegisterResponse>("/auth/register", {
        email,
        password,
        full_name: fullName,
        tenant_name: tenantName,
      });
      setTokens(res.access_token, res.refresh_token);
      router.replace("/dashboard");
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Something went wrong. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-brand text-lg font-bold text-white">
            U
          </div>
          <h1 className="text-2xl font-semibold text-slate-50">
            Create your account
          </h1>
          <p className="mt-1 text-sm text-muted">
            Your full virtual team — one console, idea to exit.
          </p>
        </div>

        <form onSubmit={onSubmit} className="card space-y-4">
          {error ? (
            <div className="rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-200">
              {error}
            </div>
          ) : null}

          <div>
            <label htmlFor="full_name" className="label">
              Full name
            </label>
            <input
              id="full_name"
              type="text"
              autoComplete="name"
              required
              className="input"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Pavel Ignatev"
            />
          </div>

          <div>
            <label htmlFor="tenant_name" className="label">
              Workspace name
            </label>
            <input
              id="tenant_name"
              type="text"
              required
              className="input"
              value={tenantName}
              onChange={(e) => setTenantName(e.target.value)}
              placeholder="Ignatev Ventures"
            />
          </div>

          <div>
            <label htmlFor="email" className="label">
              Email
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              required
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label htmlFor="password" className="label">
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="new-password"
              required
              minLength={8}
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters"
            />
          </div>

          <button
            type="submit"
            className="btn-primary w-full"
            disabled={loading}
          >
            {loading ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-muted">
          Already have an account?{" "}
          <Link href="/login" className="text-indigo-300 hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </main>
  );
}
