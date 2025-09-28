import React, { useState } from "react";

export default function OnboardingQuestionnaire() {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState({
    medicalHistory: "",
    familyHistory: "",
    allergies: "",
  });

  const questions = [
    {
      id: "medicalHistory",
      question:
        "Have you ever been diagnosed with or treated for any illnesses? (including surgeries or hospitalizations)",
      type: "textarea",
    },
    {
      id: "familyHistory",
      question:
        "Does anyone in your family have similar conditions or major illnesses (e.g., hypertension, diabetes, heart disease, cancer)?",
      type: "textarea",
    },
    {
      id: "allergies",
      question: "Do you have any allergies to medications or food?",
      type: "textarea",
    },
  ];

  const handleInputChange = (value: string) => {
    const currentQuestionId = questions[currentStep].id;
    setAnswers((prev) => ({
      ...prev,
      [currentQuestionId]: value,
    }));
  };

  const handleNext = () => {
    if (currentStep < questions.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // Handle form completion
      alert(
        "Questionnaire completed! Answers: " + JSON.stringify(answers, null, 2),
      );
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const currentQuestion = questions[currentStep];
  const currentAnswer =
    answers[currentQuestion.id as keyof typeof answers] || "";
=======
"use client";

import React, { useMemo, useState } from "react";

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
>>>>>>> e3a4d472791ca3e73dd25c1bbb7e4423947a1f5b

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
<<<<<<< HEAD
    <div
      style={{
        padding: "40px 20px",
        maxWidth: "600px",
        margin: "0 auto",
        fontFamily: "Arial, sans-serif",
      }}
    >
      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: "40px" }}>
        <h1 style={{ fontSize: "24px", marginBottom: "8px" }}>
          Medical History Questionnaire
        </h1>
        <p style={{ color: "#666", margin: 0 }}>
          Step {currentStep + 1} of {questions.length}
        </p>
      </div>

      {/* Question */}
      <div style={{ marginBottom: "40px" }}>
        <h2
          style={{ fontSize: "18px", marginBottom: "20px", lineHeight: "1.4" }}
        >
          {currentQuestion.question}
        </h2>

        <textarea
          value={currentAnswer}
          onChange={(e) => handleInputChange(e.target.value)}
          placeholder="Please provide details or write 'None' if not applicable"
          style={{
            width: "100%",
            minHeight: "120px",
            padding: "12px",
            border: "1px solid #ccc",
            borderRadius: "4px",
            fontSize: "14px",
            fontFamily: "Arial, sans-serif",
            resize: "vertical",
            boxSizing: "border-box",
          }}
        />
      </div>

      {/* Navigation Buttons */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "40px",
        }}
      >
        <button
          onClick={handleBack}
          disabled={currentStep === 0}
          style={{
            padding: "10px 20px",
            border: "1px solid #ccc",
            backgroundColor: currentStep === 0 ? "#f5f5f5" : "white",
            color: currentStep === 0 ? "#999" : "#333",
            borderRadius: "4px",
            cursor: currentStep === 0 ? "not-allowed" : "pointer",
            fontSize: "14px",
          }}
        >
          Back
        </button>

        <button
          onClick={handleNext}
          style={{
            padding: "10px 20px",
            border: "none",
            backgroundColor: "#007bff",
            color: "white",
            borderRadius: "4px",
            cursor: "pointer",
            fontSize: "14px",
          }}
        >
          {currentStep === questions.length - 1 ? "Complete" : "Next"}
        </button>
      </div>

      {/* Progress Dots */}
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: "8px",
        }}
      >
        {questions.map((_, index) => (
          <div
            key={index}
            style={{
              width: "12px",
              height: "12px",
              borderRadius: "50%",
              backgroundColor:
                index === currentStep
                  ? "#007bff"
                  : index < currentStep
                    ? "#28a745"
                    : "#dee2e6",
              cursor: "pointer",
            }}
            onClick={() => setCurrentStep(index)}
          />
        ))}
=======
    <div className="min-h-screen w-full bg-orange-50 flex items-center justify-center px-4">
      <div className="mx-auto w-full max-w-3xl text-center">

        {/* Logo / Brand */}
        <div className="flex items-center justify-center gap-2 mb-6">
          <div className="h-6 w-6" >
            <img src="/logo.png" alt="Medigator Logo" />
          </div>
          <div className="font-semibold text-orange-600">Medigator</div>
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
>>>>>>> e3a4d472791ca3e73dd25c1bbb7e4423947a1f5b
      </div>
    </div>
  );
};

export default function OnboardingQuestionnaire() {
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
      // Final submit
      console.log("Onboarding answers:", answers);
      alert("Thanks! Your responses were captured in the console.");
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
