"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

// Small utility to generate a RFC4122 v4 UUID-ish token (not cryptographically secure - fine for mock)
function generateToken() {
  // quick UUID v4
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

export default function SignIn() {
  const router = useRouter();
  const [errors, setErrors] = useState<{ username?: string; password?: string }>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const formData = new FormData(form);
    const username = (formData.get("username") as string)?.trim() ?? "";
    const password = (formData.get("password") as string) ?? "";

    // Quick local doctor shortcut
    if (username === "doc" && password === "pass") {
      router.push(`/DoctorDashboard`);
      return;
    }

    // Validation for regular users
    const newErrors: { username?: string; password?: string } = {};
    if (username.length < 8) {
      newErrors.username = "Username must be at least 8 characters.";
    }
    if (!/^(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$/.test(password)) {
      newErrors.password = "Password must be at least 8 characters and include a special character.";
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    } else {
      setErrors({});
    }

    // Request token for this username from backend
    try {
      const API_BASE =
        (process.env.NEXT_PUBLIC_API_URL as string) || "http://localhost:8082";
      const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username }),
      });
      if (!res.ok) {
        alert("Login failed");
        return;
      }
      const data = await res.json();
      const token = data.token;
      const existing = !!data.existing;
      if (existing) {
        router.push(`/PatientInterface?token=${encodeURIComponent(token)}`);
      } else {
        router.push(`/ProfileQuestionnaire?token=${encodeURIComponent(token)}`);
      }
    } catch (err) {
      alert("Unable to contact auth server");
    }
  };

  return (
    <div className="min-h-screen w-full bg-orange-50 flex items-center justify-center px-4">
      <div className="mx-auto w-full max-w-md text-center">
        {/* Logo / Brand */}
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

          <form
            onSubmit={handleSubmit}
            className="flex flex-col gap-4 text-left"
          >
            <input
              name="username"
              type="text"
              placeholder="Username"
              className={`w-full rounded-xl border px-4 py-3 outline-none focus:ring-2 ${
                errors.username ? "border-red-500 focus:ring-red-200" : "border-gray-200 focus:ring-orange-200"
              }`}
            />
            {errors.username && <p className="text-red-500 text-sm">{errors.username}</p>}

            <input
              name="password"
              type="password"
              placeholder="Password"
              className={`w-full rounded-xl border px-4 py-3 outline-none focus:ring-2 ${
                errors.password ? "border-red-500 focus:ring-red-200" : "border-gray-200 focus:ring-orange-200"
              }`}
            />
            {errors.password && <p className="text-red-500 text-sm">{errors.password}</p>}

            <button
              type="submit"
              className="w-full px-6 py-3 rounded-xl bg-orange-500 text-white font-medium hover:bg-orange-600 transition"
            >
              Sign In
            </button>
          </form>
        </div>

        <div className="text-xs text-gray-400 mt-8">© 2025 Medigator. All rights reserved.</div>
      </div>
    </div>
  );
}
