"use client";

const DEMO_SESSION_KEY = "medigator_demo_session_id";
const OPERATOR_SESSION_KEY = "medigator_operator_session";

export const API_BASE =
  (process.env.NEXT_PUBLIC_API_URL as string) || "http://localhost:8082";

export function getOrCreateDemoSessionId(): string {
  if (typeof window === "undefined") {
    return "";
  }
  let id = sessionStorage.getItem(DEMO_SESSION_KEY);
  if (!id) {
    id = crypto.randomUUID();
    sessionStorage.setItem(DEMO_SESSION_KEY, id);
  }
  return id;
}

export function getOperatorSession(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return sessionStorage.getItem(OPERATOR_SESSION_KEY);
}

export function setOperatorSession(token: string): void {
  sessionStorage.setItem(OPERATOR_SESSION_KEY, token);
}

export function clearOperatorSession(): void {
  sessionStorage.removeItem(OPERATOR_SESSION_KEY);
}

export function jsonHeaders(): HeadersInit {
  return { "Content-Type": "application/json" };
}

export function operatorHeaders(): HeadersInit {
  const token = getOperatorSession();
  return token
    ? { "Content-Type": "application/json", Authorization: `Bearer ${token}` }
    : jsonHeaders();
}
