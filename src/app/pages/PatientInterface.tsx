"use client";

import React, { useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

// --- Types
type Choice = {
  id: string;
  label: string;
  // marks this as an "Other" choice that reveals a text input
  isOther?: boolean;
  // when selected, all other choices are cleared (e.g., "None")
  isExclusive?: boolean;
};

type MultiAnswer = { selected: string[]; otherText?: string };
type SingleAnswer = { selected?: string; otherText?: string };

// --- Small UI atoms
const PageShell: React.FC<{ step: number; total: number; title: string; subtitle?: string; children: React.ReactNode; onBack?: () => void; onNext?: () => void; nextDisabled?: boolean; }> = ({ step, total, title, subtitle, children, onBack, onNext, nextDisabled }) => {
  return (
    <div className="min-h-screen w-full bg-orange-50 flex items-center justify-center px-4">
      <div className="mx-auto w-full max-w-3xl text-center">
        <div className="mb-8 text-gray-400 text-xs">Demo only — Not diagnostic • No PHI</div>

        {/* Logo / Brand */}
        <div className="flex items-center justify-center gap-2 mb-6">
          <div className="h-6 w-6 rounded-md bg-orange-400" />
          <div className="font-semibold text-orange-600">Medigator</div>
        </div>

        {/* Progress */}
        <div className="text-gray-500 text-sm mb-2">{step} / {total}</div>

        <h1 className="text-3xl font-semibold text-gray-900 mb-2">{title}</h1>
        {subtitle && <p className="text-gray-500 mb-6">{subtitle}</p>}

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
              className={`px-6 py-3 rounded-xl text-white ${nextDisabled ? "bg-orange-300 cursor-not-allowed" : "bg-orange-500 hover:bg-orange-600"}`}
              onClick={onNext}
              disabled={nextDisabled}
            >
              Next
            </button>
          )}
        </div>

        <div className="text-xs text-gray-400 mt-8">© 2025 Medigator. All rights reserved.</div>
      </div>
    </div>
  );
};

const SelectBox: React.FC<{
  selected: boolean;
  onToggle: () => void;
  label: string;
  radio?: boolean;
}> = ({ selected, onToggle, label, radio }) => {
  return (
    <button
      type="button"
      onClick={onToggle}
      className={`w-full text-left rounded-xl border transition py-4 px-5 mb-3
        ${selected ? "border-green-500 ring-2 ring-green-100 bg-green-50" : "border-gray-200 hover:bg-gray-50"}
      `}
    >
      <div className="flex items-center gap-3">
        <span
          className={`inline-flex h-5 w-5 items-center justify-center rounded-full border ${selected ? "border-green-500 bg-green-500 text-white" : "border-gray-300 bg-white text-transparent"}`}
        >
          {radio ? "●" : "✓"}
        </span>
        <span className="text-gray-800">{label}</span>
      </div>
    </button>
  );
};

// --- Multi-select block with optional "Other" free text
const MultiSelectQuestion: React.FC<{
  choices: Choice[];
  value: MultiAnswer;
  onChange: (v: MultiAnswer) => void;
  scrollable?: boolean;
}> = ({ choices, value, onChange, scrollable }) => {
  const toggle = (c: Choice) => {
    const has = value.selected.includes(c.id);
    let next = value.selected;

    if (has) {
      next = value.selected.filter((x) => x !== c.id);
    } else {
      // If exclusive option selected, clear others
      if (c.isExclusive) {
        next = [c.id];
      } else {
        // If clicking a non-exclusive option and exclusive is selected, remove exclusive
        next = value.selected.filter((id) => !choices.find((x) => x.id === id)?.isExclusive);
        next = [...next, c.id];
      }
    }

    // If "Other" was de-selected, remove text
    const otherId = choices.find((x) => x.isOther)?.id;
    const otherDeselected = otherId && !next.includes(otherId) && value.selected.includes(otherId);
    onChange({ selected: next, otherText: otherDeselected ? "" : value.otherText });
  };

  const other = choices.find((c) => c.isOther);
  const otherSelected = !!(other && value.selected.includes(other.id));

  return (
    <div className={`${scrollable ? "max-h-[22rem] overflow-auto pr-1" : ""}`}>
      {choices.map((c) => (
        <SelectBox
          key={c.id}
          selected={value.selected.includes(c.id)}
          onToggle={() => toggle(c)}
          label={c.label}
        />
      ))}
      {other && otherSelected && (
        <div className="mt-2">
          <input
            className="w-full rounded-xl border border-gray-300 px-4 py-3 outline-none focus:ring-2 focus:ring-orange-200"
            placeholder="Please describe…"
            value={value.otherText ?? ""}
            onChange={(e) => onChange({ ...value, otherText: e.target.value })}
          />
        </div>
      )}
    </div>
  );
};

// --- Single-select block with optional "Other" free text
const SingleSelectQuestion: React.FC<{
  choices: Choice[];
  value: SingleAnswer;
  onChange: (v: SingleAnswer) => void;
}> = ({ choices, value, onChange }) => {
  const select = (c: Choice) => {
    // toggle off if clicking same one
    const selected = value.selected === c.id ? undefined : c.id;
    const otherId = choices.find((x) => x.isOther)?.id;
    const otherDeselected = otherId && selected !== otherId && value.selected === otherId;
    onChange({ selected, otherText: otherDeselected ? "" : value.otherText });
  };

  const other = choices.find((c) => c.isOther);
  const otherSelected = value.selected === other?.id;

  return (
    <>
      {choices.map((c) => (
        <SelectBox
          key={c.id}
          radio
          selected={value.selected === c.id}
          onToggle={() => select(c)}
          label={c.label}
        />
      ))}
      {other && otherSelected && (
        <div className="mt-2">
          <input
            className="w-full rounded-xl border border-gray-300 px-4 py-3 outline-none focus:ring-2 focus:ring-orange-200"
            placeholder="Please describe…"
            value={value.otherText ?? ""}
            onChange={(e) => onChange({ ...value, otherText: e.target.value })}
          />
        </div>
      )}
    </>
  );
};

// --- Full Questionnaire
const TOTAL_STEPS = 9;

export default function PatientChestPainQuestionnairePage() {
  const router = useRouter();
  const search = new URLSearchParams(window.location.search);
  const token = search.get("token") ?? "";
  // Answers
  const [q1, setQ1] = useState<SingleAnswer>({}); // When did the pain start? (single)
  const [q2, setQ2] = useState<MultiAnswer>({ selected: [] });
  const [q3, setQ3] = useState<MultiAnswer>({ selected: [] });
  const [q4, setQ4] = useState<MultiAnswer>({ selected: [] });
  const [q5, setQ5] = useState<MultiAnswer>({ selected: [] });
  const [q6, setQ6] = useState<MultiAnswer>({ selected: [] });
  const [q7, setQ7] = useState<SingleAnswer>({});
  const [q8, setQ8] = useState<SingleAnswer>({});
  const [q9, setQ9] = useState<SingleAnswer>({});

  const [step, setStep] = useState(1);

  // --- Choice lists
  const Q1_CHOICES: Choice[] = [
    { id: "now", label: "Just now (within the last hour)" },
    { id: "today", label: "Earlier today" },
    { id: "yesterday", label: "Yesterday" },
    { id: "several-days", label: "Several days ago" },
    { id: "other", label: "Other / describe", isOther: true },
  ];

  const Q2_CHOICES: Choice[] = [
    { id: "mid-chest", label: "Middle of chest" },
    { id: "left-chest", label: "Left side of chest" },
    { id: "right-chest", label: "Right side of chest" },
    { id: "spreads", label: "Spreads to left arm / jaw / neck / back" },
    { id: "other", label: "Other / describe", isOther: true },
  ];

  const Q3_CHOICES: Choice[] = [
    { id: "pressure", label: "Pressure or squeezing" },
    { id: "sharp", label: "Sharp or stabbing" },
    { id: "burning", label: "Burning" },
    { id: "tight", label: "Tightness / heaviness" },
    { id: "other", label: "Other / describe", isOther: true },
  ];

  const Q4_CHOICES: Choice[] = [
    { id: "activity", label: "Physical activity (walking, climbing stairs, exercise)" },
    { id: "breathing", label: "Breathing deeply or changing position" },
    { id: "eating", label: "Eating or drinking" },
    { id: "stress", label: "Stress or anxiety" },
    { id: "not-sure", label: "Not sure" },
    { id: "other", label: "Other / describe", isOther: true },
  ];

  const Q5_CHOICES: Choice[] = [
    { id: "rest", label: "Rest" },
    { id: "stop", label: "Stopping activity" },
    { id: "medicine", label: "Medicine (nitroglycerin, antacids, painkillers)" },
    { id: "nothing", label: "Nothing helps" },
    { id: "not-sure", label: "Not sure" },
    { id: "other", label: "Other / describe", isOther: true },
  ];

  const Q6_CHOICES: Choice[] = [
    { id: "sob", label: "Shortness of breath" },
    { id: "sweating", label: "Sweating" },
    { id: "nausea", label: "Nausea or vomiting" },
    { id: "dizziness", label: "Dizziness or fainting" },
    { id: "heartbeat", label: "Fast or irregular heartbeat" },
    { id: "none", label: "No, none of these", isExclusive: true },
    { id: "other", label: "Other / describe", isOther: true },
  ];

  const Q7_CHOICES: Choice[] = [
    { id: "seconds", label: "A few seconds" },
    { id: "1-5", label: "1–5 minutes" },
    { id: "5-30", label: "5–30 minutes" },
    { id: "30+", label: "More than 30 minutes" },
    { id: "hours", label: "Hours" },
    { id: "other", label: "Other / describe", isOther: true },
  ];

  const Q8_CHOICES: Choice[] = [
    { id: "once", label: "Only once" },
    { id: "few-day", label: "A few times a day" },
    { id: "daily", label: "Daily" },
    { id: "few-week", label: "A few times a week" },
    { id: "lt-week", label: "Less than once a week" },
    { id: "other", label: "Other / describe", isOther: true },
  ];

  const Q9_CHOICES: Choice[] = [
    { id: "0-2", label: "0–2 (mild)" },
    { id: "3-5", label: "3–5 (moderate)" },
    { id: "6-7", label: "6–7 (severe)" },
    { id: "8-10", label: "8–10 (very severe / worst ever)" },
    { id: "other", label: "Other / describe", isOther: true },
  ];

  // --- Step guards (disable Next until valid)
  const nextDisabled = useMemo(() => {
    switch (step) {
      case 1: {
        if (!q1.selected) return true;
        if (q1.selected === "other" && !q1.otherText?.trim()) return true;
        return false;
      }
      case 2: {
        if (!q2.selected.length) return true;
        if (q2.selected.includes("other") && !q2.otherText?.trim()) return true;
        return false;
      }
      case 3: {
        if (!q3.selected.length) return true;
        if (q3.selected.includes("other") && !q3.otherText?.trim()) return true;
        return false;
      }
      case 4: {
        if (!q4.selected.length) return true;
        if (q4.selected.includes("other") && !q4.otherText?.trim()) return true;
        return false;
      }
      case 5: {
        if (!q5.selected.length) return true;
        if (q5.selected.includes("other") && !q5.otherText?.trim()) return true;
        return false;
      }
      case 6: {
        if (!q6.selected.length) return true;
        if (q6.selected.includes("other") && !q6.otherText?.trim()) return true;
        return false;
      }
      case 7: {
        if (!q7.selected) return true;
        if (q7.selected === "other" && !q7.otherText?.trim()) return true;
        return false;
      }
      case 8: {
        if (!q8.selected) return true;
        if (q8.selected === "other" && !q8.otherText?.trim()) return true;
        return false;
      }
      case 9: {
        if (!q9.selected) return true;
        if (q9.selected === "other" && !q9.otherText?.trim()) return true;
        return false;
      }
      default:
        return true;
    }
  }, [step, q1, q2, q3, q4, q5, q6, q7, q8, q9]);

  // --- Submit
  const submit = () => {
    const payload = {
      q1,
      q2,
      q3,
      q4,
      q5,
      q6,
      q7,
      q8,
      q9,
    };
    // POST appointment payload to backend under the user's token
    const API_BASE = (process.env.NEXT_PUBLIC_API_URL as string) || "http://localhost:8082";

    const body = { token, appointmentData: payload };

    fetch(`${API_BASE}/api/v1/patient/appointment`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
      .then(async (res) => {
        if (!res.ok) {
          const t = await res.text();
          throw new Error(`save failed: ${res.status} ${t}`);
        }
        return res.json();
      })
      .then((data) => {
        // show user the key so they can reference or copy it
        // eslint-disable-next-line no-alert
        router.push(`/PatientThankYou?token=${encodeURIComponent(token)}`)
        console.log(`Saved appointment data as ${data.key}`);
      })
      .catch((err) => {
        // eslint-disable-next-line no-alert
        alert(`Failed to save appointment: ${err.message}`);
      });
  };

  // --- Render per step
  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <PageShell
            step={step}
            total={TOTAL_STEPS}
            title="Symptom Onset"
            subtitle="When did the pain start?"
            onNext={() => setStep(step + 1)}
            nextDisabled={nextDisabled}
          >
            <SingleSelectQuestion choices={Q1_CHOICES} value={q1} onChange={setQ1} />
          </PageShell>
        );

      case 2:
        return (
          <PageShell
            step={step}
            total={TOTAL_STEPS}
            title="Pain Location"
            subtitle="Where do you feel the pain?"
            onBack={() => setStep(step - 1)}
            onNext={() => setStep(step + 1)}
            nextDisabled={nextDisabled}
          >
            <MultiSelectQuestion choices={Q2_CHOICES} value={q2} onChange={setQ2} />
          </PageShell>
        );

      case 3:
        return (
          <PageShell
            step={step}
            total={TOTAL_STEPS}
            title="Pain Quality"
            subtitle="What does the pain feel like?"
            onBack={() => setStep(step - 1)}
            onNext={() => setStep(step + 1)}
            nextDisabled={nextDisabled}
          >
            <MultiSelectQuestion choices={Q3_CHOICES} value={q3} onChange={setQ3} />
          </PageShell>
        );

      case 4:
        return (
          <PageShell
            step={step}
            total={TOTAL_STEPS}
            title="Triggers"
            subtitle="What makes it worse?"
            onBack={() => setStep(step - 1)}
            onNext={() => setStep(step + 1)}
            nextDisabled={nextDisabled}
          >
            <MultiSelectQuestion choices={Q4_CHOICES} value={q4} onChange={setQ4} />
          </PageShell>
        );

      case 5:
        return (
          <PageShell
            step={step}
            total={TOTAL_STEPS}
            title="Relief"
            subtitle="What makes it better?"
            onBack={() => setStep(step - 1)}
            onNext={() => setStep(step + 1)}
            nextDisabled={nextDisabled}
          >
            <MultiSelectQuestion choices={Q5_CHOICES} value={q5} onChange={setQ5} />
          </PageShell>
        );

      case 6:
        return (
          <PageShell
            step={step}
            total={TOTAL_STEPS}
            title="Associated Symptoms"
            subtitle="Do you have any of these at the same time?"
            onBack={() => setStep(step - 1)}
            onNext={() => setStep(step + 1)}
            nextDisabled={nextDisabled}
          >
            {/* Scrollable box like your mock (rows scroll, page doesn't) */}
            <MultiSelectQuestion choices={Q6_CHOICES} value={q6} onChange={setQ6} scrollable />
          </PageShell>
        );

      case 7:
        return (
          <PageShell
            step={step}
            total={TOTAL_STEPS}
            title="Duration"
            subtitle="How long does each episode last?"
            onBack={() => setStep(step - 1)}
            onNext={() => setStep(step + 1)}
            nextDisabled={nextDisabled}
          >
            <SingleSelectQuestion choices={Q7_CHOICES} value={q7} onChange={setQ7} />
          </PageShell>
        );

      case 8:
        return (
          <PageShell
            step={step}
            total={TOTAL_STEPS}
            title="Frequency"
            subtitle="How often does it happen?"
            onBack={() => setStep(step - 1)}
            onNext={() => setStep(step + 1)}
            nextDisabled={nextDisabled}
          >
            <SingleSelectQuestion choices={Q8_CHOICES} value={q8} onChange={setQ8} />
          </PageShell>
        );

      case 9:
        return (
          <PageShell
            step={step}
            total={TOTAL_STEPS}
            title="Pain/Discomfort Level"
            subtitle="Severity – On a scale of 0–10, how bad is the pain?"
            onBack={() => setStep(step - 1)}
            onNext={submit}
            nextDisabled={nextDisabled}
          >
            <SingleSelectQuestion choices={Q9_CHOICES} value={q9} onChange={setQ9} />
          </PageShell>
        );

      default:
        return null;
    }
  };

  return renderStep();
}
