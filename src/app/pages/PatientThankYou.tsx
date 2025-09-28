"use client";

import React from "react";

export default function PatientThankYou() {

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
            Thank you for your time!
          </h1>
          <p className="text-gray-600 mb-6">
            Thank you for filling out this preliminary survey. <br /><br />Sit tight! A doctor will be with you shortly.
          </p>
        </div>

        <div className="text-xs text-gray-400 mt-8">
          © 2025 Medigator. All rights reserved.
        </div>
      </div>
    </div>
  );
}
