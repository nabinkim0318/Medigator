"use client";

import React, { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function PatientThankYou() {
  const router = useRouter();
  const sp = useSearchParams();
  const token = sp?.get("token") ?? "";

  const handleContinue = () => {
    router.push(`/PatientInterface?token=${encodeURIComponent(token)}`);
  };

  return (
    <div className="min-h-screen w-full bg-orange-50 flex items-center justify-center px-4">
      <div className="mx-auto w-full max-w-2xl text-center">
        {/* Logo / Brand */}
        <div className="flex items-center justify-center gap-2 mb-6">
          <div className="h-6 w-6">
            <img src="/logo.png" alt="Medigator Logo" />
          </div>
          <div className="font-semibold text-orange-600">Medigator</div>
        </div>

        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-6 sm:p-10">
          <h1 className="text-3xl font-semibold text-gray-900 mb-2">
            Thank you!
          </h1>
          <p className="text-gray-600 mb-6">
            Your appointment data has been saved successfully.
          </p>

          <div className="flex gap-3 justify-center">
            <button
              onClick={handleContinue}
              className="px-6 py-3 rounded-xl bg-gray-100 text-gray-700 font-medium hover:bg-gray-200 transition"
            >
              Back to Symptoms
            </button>
          </div>
        </div>

        <div className="text-xs text-gray-400 mt-8">
          © 2025 Medigator. All rights reserved.
        </div>
      </div>
    </div>
  );
}
