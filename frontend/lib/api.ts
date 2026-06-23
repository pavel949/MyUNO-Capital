"use client";

import { clearTokens, getToken, redirectToLogin } from "./auth";
import type { ApiErrorBody } from "./types";

// Base URL of the FastAPI backend. All calls hit `${API_BASE}/api/v1/...`.
const API_ROOT =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ||
  "http://localhost:8000";
const API_BASE = `${API_ROOT}/api/v1`;

export class ApiError extends Error {
  status: number;
  code: string;
  details?: { field: string; issue: string }[];
  requestId?: string;

  constructor(
    status: number,
    code: string,
    message: string,
    details?: { field: string; issue: string }[],
    requestId?: string,
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
    this.requestId = requestId;
  }
}

interface RequestOptions {
  /** Extra query parameters appended to the URL. */
  query?: Record<string, string | number | boolean | undefined>;
  /** Send an Idempotency-Key (for unsafe POSTs). */
  idempotencyKey?: string;
  /** Additional headers. */
  headers?: Record<string, string>;
  signal?: AbortSignal;
}

function buildUrl(path: string, query?: RequestOptions["query"]): string {
  const url = new URL(`${API_BASE}${path.startsWith("/") ? path : `/${path}`}`);
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined && value !== null) {
        url.searchParams.set(key, String(value));
      }
    }
  }
  return url.toString();
}

function uuid(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  // Fallback for environments without crypto.randomUUID.
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  options: RequestOptions = {},
): Promise<T> {
  const headers: Record<string, string> = {
    Accept: "application/json",
    ...(options.headers ?? {}),
  };

  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let payload: BodyInit | undefined;
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }

  if (options.idempotencyKey !== undefined) {
    headers["Idempotency-Key"] = options.idempotencyKey || uuid();
  }

  let res: Response;
  try {
    res = await fetch(buildUrl(path, options.query), {
      method,
      headers,
      body: payload,
      signal: options.signal,
      cache: "no-store",
    });
  } catch (err) {
    // Network failure / backend unreachable.
    throw new ApiError(
      0,
      "network_error",
      "Could not reach the MyUNO Capital API. Is the backend running?",
    );
  }

  // 401 → clear token and bounce to login.
  if (res.status === 401) {
    clearTokens();
    redirectToLogin();
    throw new ApiError(401, "unauthorized", "Your session has expired.");
  }

  if (res.status === 204) {
    return undefined as T;
  }

  let data: unknown = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!res.ok) {
    const errBody = data as ApiErrorBody | null;
    const code = errBody?.error?.code ?? "error";
    const message =
      errBody?.error?.message ??
      (typeof data === "string" && data
        ? data
        : `Request failed with status ${res.status}`);
    throw new ApiError(
      res.status,
      code,
      message,
      errBody?.error?.details,
      errBody?.error?.request_id,
    );
  }

  return data as T;
}

export const api = {
  get: <T>(path: string, options?: RequestOptions) =>
    request<T>("GET", path, undefined, options),
  post: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>("POST", path, body, options),
  patch: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>("PATCH", path, body, options),
  del: <T>(path: string, options?: RequestOptions) =>
    request<T>("DELETE", path, undefined, options),
};

export { API_BASE, API_ROOT };
