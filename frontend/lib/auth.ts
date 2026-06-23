"use client";

// Token storage helpers. JWT access/refresh tokens live in localStorage.

const ACCESS_KEY = "myuno_access_token";
const REFRESH_KEY = "myuno_refresh_token";

function isBrowser(): boolean {
  return typeof window !== "undefined";
}

export function getToken(): string | null {
  if (!isBrowser()) return null;
  return window.localStorage.getItem(ACCESS_KEY);
}

export function getRefreshToken(): string | null {
  if (!isBrowser()) return null;
  return window.localStorage.getItem(REFRESH_KEY);
}

export function setTokens(accessToken: string, refreshToken?: string): void {
  if (!isBrowser()) return;
  window.localStorage.setItem(ACCESS_KEY, accessToken);
  if (refreshToken) {
    window.localStorage.setItem(REFRESH_KEY, refreshToken);
  }
}

export function clearTokens(): void {
  if (!isBrowser()) return;
  window.localStorage.removeItem(ACCESS_KEY);
  window.localStorage.removeItem(REFRESH_KEY);
}

export function isLoggedIn(): boolean {
  return !!getToken();
}

/**
 * Redirect helper used after clearing tokens on a 401. Uses a hard
 * navigation so any in-flight client state is discarded.
 */
export function redirectToLogin(): void {
  if (!isBrowser()) return;
  if (window.location.pathname !== "/login") {
    window.location.assign("/login");
  }
}
