"use client";

import React from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function OnboardingThankYou({
  onContinue,
}: {
  onContinue?: () => void;
}) {
  const router = useRouter();
  const sp = useSearchParams();
  const token = sp?.get("token") ?? "";
  const handleContinue = () => {
    if (onContinue) return onContinue();
    // Fallback: replace with your router navigation (e.g., router.push("/symptoms"))
    router.push(`/PatientInterface?token=${encodeURIComponent(token)}`);
  };

  return (
    <div className="min-h-screen w-full bg-orange-50 flex items-center justify-center px-4">
      <div className="mx-auto w-full max-w-2xl text-center">
        <div className="mb-8 text-gray-400 text-xs">
          Demo only — Not diagnostic • No PHI
        </div>

        {/* Logo / Brand */}
        <div className="flex items-center justify-center gap-2 mb-6">
          <div className="h-6 w-6 rounded-md bg-orange-400" />
          <div className="font-semibold text-orange-600">Medigator</div>
        </div>

        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-6 sm:p-10">
          <h1 className="text-3xl font-semibold text-gray-900 mb-2">
            Thank you!
          </h1>
          <p className="text-gray-600 mb-6">
            Your medical history has been saved — you won’t need to fill it out
            again.
          </p>

          <div className="text-left bg-orange-50/50 border border-orange-100 rounded-2xl p-5 sm:p-6 mb-6">
            <h2 className="text-lg font-medium text-gray-900 mb-3">
              What happens next
            </h2>
            <ul className="space-y-2 text-gray-700">
              <li>• Tell us about your current symptoms.</li>
              <li>• You’ll see an estimated cost for your appointment.</li>
              <li>• Your doctor will receive a clear summary of your answers.</li>
            </ul>
          </div>

          <button
            onClick={handleContinue}
            className="w-full sm:w-auto px-6 py-3 rounded-xl bg-orange-500 text-white font-medium hover:bg-orange-600 transition"
          >
            Start symptom check
          </button>
        </div>

        <div className="text-xs text-gray-400 mt-8">
          © 2025 Medigator. All rights reserved.
        </div>
      </div>
    </div>
  );
}
