"use client";

import React, { useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

type QId = "medicalHistory" | "familyHistory" | "allergies";

type QA = Record<QId, string>;

type Q = {
  id: QId;
  question: string;
  type: "textarea";
  placeholder?: string;
};

const QUESTIONS: Q[] = [
  {
    id: "medicalHistory",
    question:
      "Have you ever been diagnosed with or treated for any illnesses? (including surgeries or hospitalizations)",
    type: "textarea",
    placeholder: "Please include condition, year, and any treatments..."
  },
  {
    id: "familyHistory",
    question:
      "Does anyone in your family have similar conditions or major illnesses (e.g., hypertension, diabetes, heart disease, cancer)?",
    type: "textarea",
    placeholder: "List relatives and conditions, if known…"
  },
  {
    id: "allergies",
    question: "Do you have any allergies to medications or food?",
    type: "textarea",
    placeholder: "E.g., penicillin (rash), peanuts (anaphylaxis)…"
  }
];

const PageShell: React.FC<{
  step: number;
  total: number;
  title: string;
  children: React.ReactNode;
  onBack?: () => void;
  onNext?: () => void;
  nextDisabled?: boolean;
}> = ({ step, total, title, children, onBack, onNext, nextDisabled }) => {
  return (
    <div className="min-h-screen w-full bg-orange-50 flex items-center justify-center px-4">
      <div className="mx-auto w-full max-w-3xl text-center">
        <div className="mb-8 text-gray-400 text-xs">
          Demo only — Not diagnostic • No PHI
        </div>

        {/* Logo / Brand */}
        <div className="flex items-center justify-center gap-2 mb-6">
          <div className="h-6 w-6 rounded-md bg-orange-400" />
          <div className="font-semibold text-orange-600">Medigator</div>
        </div>

        {/* Progress */}
        <div className="text-gray-500 text-sm mb-2">
          {step} / {total}
        </div>

        <h1 className="text-3xl font-semibold text-gray-900 mb-6">
          {title}
        </h1>

        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-6 sm:p-8">
          {children}
        </div>

        <div className="mt-8 flex items-center justify-center gap-3">
          {onBack && (
            <button
              className="px-5 py-3 rounded-xl border border-gray-200 bg-white text-gray-700 hover:bg-gray-50"
              onClick={onBack}
            >
              Back
            </button>
          )}
          {onNext && (
            <button
              className={`px-6 py-3 rounded-xl text-white ${
                nextDisabled
                  ? "bg-orange-300 cursor-not-allowed"
                  : "bg-orange-500 hover:bg-orange-600"
              }`}
              onClick={onNext}
              disabled={nextDisabled}
            >
              {step === total ? "Complete" : "Next"}
            </button>
          )}
        </div>

        <div className="text-xs text-gray-400 mt-8">
          © 2025 Medigator. All rights reserved.
        </div>
      </div>
    </div>
  );
};

export default function OnboardingQuestionnaire() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams?.get("token") ?? null;

  const copyToken = async () => {
    if (!token) return;
    try {
      await navigator.clipboard.writeText(token);
      // quick user feedback
      // eslint-disable-next-line no-alert
      alert("Token copied to clipboard");
    } catch (e) {
      // fallback
      // eslint-disable-next-line no-alert
      alert("Unable to copy token to clipboard");
    }
  };
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<QA>({
    medicalHistory: "",
    familyHistory: "",
    allergies: ""
  });

  const current = QUESTIONS[currentStep];

  const handleInputChange = (value: string) => {
    setAnswers((prev) => ({ ...prev, [current.id]: value }));
  };

  const canProceed = useMemo(() => {
    const val = answers[current.id]?.trim() ?? "";
    return val.length > 0;
  }, [answers, current.id]);

  const goNext = () => {
    if (currentStep < QUESTIONS.length - 1) {
      setCurrentStep((s) => s + 1);
    } else {
      // Final submit — POST medicalHistory to backend then navigate to PatientInterface
      const payload = {
        token,
        medicalHistory: answers,
      };

      const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8082";
      fetch(`${API_BASE}/api/v1/patient/patientData`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })
        .then(async (res) => {
          if (!res.ok) {
            const txt = await res.text();
            throw new Error(`save failed: ${res.status} ${txt}`);
          }
          return res.json();
        })
        .then(() => {
          // navigate to patient interface with token
          router.push(`/PatientInterface?token=${encodeURIComponent(token ?? "")}`);
        })
        .catch((err) => {
          // basic error feedback
          // eslint-disable-next-line no-alert
          alert(`Failed to save onboarding: ${err.message}`);
        });
    }
  };

  const goBack = () => setCurrentStep((s) => Math.max(0, s - 1));

  return (
    <PageShell
      step={currentStep + 1}
      total={QUESTIONS.length}
      title="Medical History Questionnaire"
      onBack={currentStep > 0 ? goBack : undefined}
      onNext={goNext}
      nextDisabled={!canProceed}
    >
      {/* Display token (if present) */}
      {token && (
        <div className="mb-4 flex items-center justify-end gap-2">
          <div className="text-xs text-gray-500">Auth token:</div>
          <div className="px-2 py-1 rounded-md bg-gray-100 text-xs font-mono text-gray-700 truncate max-w-xs">
            {token}
          </div>
          <button
            onClick={copyToken}
            className="px-2 py-1 rounded-md bg-orange-100 text-orange-700 text-xs"
          >
            Copy
          </button>
        </div>
      )}
      {/* Question text */}
      <h2 className="text-xl font-medium text-gray-900 text-left mb-3">
        {current.question}
      </h2>
      <p className="text-sm text-gray-500 text-left mb-5">
        Please provide details or write “None” if not applicable.
      </p>

      {/* Textarea */}
      <textarea
        value={answers[current.id]}
        onChange={(e) => handleInputChange(e.target.value)}
        placeholder={current.placeholder ?? "Type your answer…"}
        className="w-full min-h-[160px] rounded-2xl border border-gray-200 px-4 py-3 outline-none focus:ring-2 focus:ring-orange-200 resize-y"
      />

      {/* Progress dots */}
      <div className="mt-6 flex items-center justify-center gap-2">
        {QUESTIONS.map((_, i) => {
          const isActive = i === currentStep;
          const isDone = i < currentStep;
          return (
            <button
              key={i}
              onClick={() => setCurrentStep(i)}
              className={`h-3 w-3 rounded-full transition ${
                isActive
                  ? "bg-orange-500"
                  : isDone
                  ? "bg-green-500"
                  : "bg-gray-300"
              }`}
              aria-label={`Go to step ${i + 1}`}
            />
          );
        })}
      </div>
    </PageShell>
  );
}
