"use client";

import React from "react";

export default function SignIn() {
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

          <form className="flex flex-col gap-4 text-left">
            <input
              type="text"
              placeholder="Username"
              className="w-full rounded-xl border border-gray-200 px-4 py-3 outline-none focus:ring-2 focus:ring-orange-200"
            />
            <input
              type="password"
              placeholder="Password"
              className="w-full rounded-xl border border-gray-200 px-4 py-3 outline-none focus:ring-2 focus:ring-orange-200"
            />
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
