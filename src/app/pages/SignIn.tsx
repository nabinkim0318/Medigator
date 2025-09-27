"use client";

import React from "react";
import { useRouter } from "next/navigation";

// Small utility to generate a RFC4122 v4 UUID-ish token (not cryptographically secure - fine for mock)
function generateToken() {
  // quick UUID v4
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

export default function SignIn() {
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const formData = new FormData(form);
    const username = (formData.get("username") as string) ?? "";

    // Request token for this username from backend (creates persistent token per username)
    try {
      const API_BASE = (process.env.NEXT_PUBLIC_API_URL as string) || "http://localhost:8082";
      const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username }),
      });
      if (!res.ok) {
        // eslint-disable-next-line no-alert
        alert("Login failed");
        return;
      }
      const data = await res.json();
      const token = data.token;
      router.push(`/OnboardingQuestionaire?token=${encodeURIComponent(token)}`);
    } catch (err) {
      // eslint-disable-next-line no-alert
      alert("Unable to contact auth server");
    }
  };

  return (
    <div className="min-h-screen w-full bg-orange-50 flex items-center justify-center px-4">
      <div className="mx-auto w-full max-w-md text-center">
        {/* Logo / Brand */}
        <div className="flex items-center justify-center gap-2 mb-6">
          <div className="h-6 w-6 rounded-md bg-orange-400" />
          <div className="font-semibold text-orange-600">Medigator</div>
        </div>

        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-6 sm:p-8">
          <h1 className="text-2xl font-semibold text-gray-900 mb-6">Sign In</h1>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4 text-left">
            <input
              name="username"
              type="text"
              placeholder="Username"
              className="w-full rounded-xl border border-gray-200 px-4 py-3 outline-none focus:ring-2 focus:ring-orange-200"
            />
            <input
              name="password"
              type="password"
              placeholder="Password"
              className="w-full rounded-xl border border-gray-200 px-4 py-3 outline-none focus:ring-2 focus:ring-orange-200"
            />
            <button
              type="submit"
              className="w-full px-6 py-3 rounded-xl bg-orange-500 text-white font-medium hover:bg-orange-600 transition"
            >
              Sign In (Mock SMART)
            </button>
          </form>
        </div>

        <div className="text-xs text-gray-400 mt-8">
          © 2025 Medigator. All rights reserved.
        </div>
      </div>
    </div>
  );
}
