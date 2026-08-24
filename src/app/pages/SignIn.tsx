"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import SyntheticDataNotice from "../components/SyntheticDataNotice";
import {
  API_BASE,
  getOrCreateDemoSessionId,
  jsonHeaders,
  setOperatorSession,
} from "@/lib/demoSession";

export default function SignIn() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="min-h-screen w-full bg-orange-50 flex items-center justify-center px-4">
        <div className="mx-auto w-full max-w-md text-center">
          <div className="flex items-center justify-center gap-2 mb-6">
            <div className="h-6 w-6">
              <img src="/logo.png" alt="Medigator Logo" />
            </div>
            <div className="font-semibold text-orange-600">Medigator</div>
          </div>
          <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-6 sm:p-8">
            <div className="text-center">Loading...</div>
          </div>
        </div>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    const form = e.target as HTMLFormElement;
    const formData = new FormData(form);
    const password = (formData.get("password") as string) ?? "";

    if (password.trim()) {
      try {
        const res = await fetch(`${API_BASE}/api/v1/auth/demo-operator`, {
          method: "POST",
          headers: jsonHeaders(),
          body: JSON.stringify({ access_code: password }),
        });
        if (res.ok) {
          const data = await res.json();
          if (data.operator_session) {
            setOperatorSession(data.operator_session);
            router.push(`/DoctorPatientView`);
            return;
          }
        }
      } catch {
        setError("Unable to contact the demo API");
        return;
      }
    }

    getOrCreateDemoSessionId();
    router.push(`/ProfileQuestionnaire`);
  };

  return (
    <div className="min-h-screen w-full bg-orange-50 flex items-center justify-center px-4">
      <div className="mx-auto w-full max-w-md text-center">
        <div className="flex items-center justify-center gap-2 mb-6">
          <div className="h-6 w-6">
            <img src="/logo.png" alt="Medigator Logo" />
          </div>
          <div className="font-semibold text-orange-600">Medigator</div>
        </div>

        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-6 sm:p-8">
          <h1 className="text-2xl font-semibold text-gray-900 mb-6">
            Please Enter Your Credentials
          </h1>

          <SyntheticDataNotice />

          <form
            onSubmit={handleSubmit}
            className="flex flex-col gap-4 text-left"
          >
            <input
              name="username"
              type="text"
              placeholder="Display name (synthetic only)"
              className="w-full rounded-xl border border-gray-200 px-4 py-3 outline-none focus:ring-2 focus:ring-orange-200"
            />
            <input
              name="password"
              type="password"
              placeholder="Demo access code (doctor view only)"
              className="w-full rounded-xl border border-gray-200 px-4 py-3 outline-none focus:ring-2 focus:ring-orange-200"
            />
            {error && <div className="text-sm text-red-600">{error}</div>}
            <p className="text-xs text-gray-500">
              Patient demo: leave the access code blank. Doctor demo: enter
              DEMO_ACCESS_CODE. Client-side routing is not authorization.
            </p>
            <button
              type="submit"
              className="w-full px-6 py-3 rounded-xl bg-orange-500 text-white font-medium hover:bg-orange-600 transition"
            >
              Sign In
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
