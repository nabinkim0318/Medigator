"use client";

import React, { useState } from "react";
import DoctorDashboard from "./pages/DoctorDashboard";
import PatientInterface from "./pages/PatientInterface";

export default function Home() {
  const [activeApp, setActiveApp] = useState<"patient" | "doctor">("patient");

  return (
    <div className="min-h-screen bg-gray-50">
      {/* App Selector */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <h1 className="text-2xl font-bold text-gray-900">
              🏥 BBB Medical System
            </h1>
            <div className="flex space-x-4">
              <a
                href="/patient"
                className="px-4 py-2 rounded-md font-medium transition-colors bg-blue-600 text-white hover:bg-blue-700"
              >
                👤 Patient Interface
              </a>
              <a
                href="/doctor"
                className="px-4 py-2 rounded-md font-medium transition-colors bg-green-600 text-white hover:bg-green-700"
              >
                👨‍⚕️ Doctor Dashboard
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Landing Content */}
      <div className="flex-1 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-4xl font-bold text-gray-900 mb-8">
              AI-Powered Medical System
            </h2>
            <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto">
              Advanced medical report generation with RAG capabilities, HIPAA
              compliance, and intelligent symptom analysis for both patients and
              healthcare providers.
            </p>

            <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
              <div className="bg-white p-8 rounded-lg shadow-lg">
                <div className="text-6xl mb-4">👤</div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">
                  Patient Interface
                </h3>
                <p className="text-gray-600 mb-6">
                  Interactive symptom questionnaire with AI-powered analysis and
                  personalized medical insights.
                </p>
                <a
                  href="/patient"
                  className="inline-block bg-blue-600 text-white px-6 py-3 rounded-md font-medium hover:bg-blue-700 transition-colors"
                >
                  Start Patient Assessment
                </a>
              </div>

              <div className="bg-white p-8 rounded-lg shadow-lg">
                <div className="text-6xl mb-4">👨‍⚕️</div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">
                  Doctor Dashboard
                </h3>
                <p className="text-gray-600 mb-6">
                  Comprehensive patient management with AI-generated reports,
                  evidence retrieval, and clinical decision support.
                </p>
                <a
                  href="/doctor"
                  className="inline-block bg-green-600 text-white px-6 py-3 rounded-md font-medium hover:bg-green-700 transition-colors"
                >
                  Access Doctor Dashboard
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
