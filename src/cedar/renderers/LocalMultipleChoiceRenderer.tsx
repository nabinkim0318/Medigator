// src/cedar/renderers/LocalMultipleChoiceRenderer.tsx
"use client";

import * as React from "react";
import {
  createMessageRenderer,
  type CustomMessage,
  type MessageRenderer,
  useCedarStore,
} from "cedar-os";
import { triageAnswers } from "@/cedar/triage/triageState";

type MCOption = { label: string; value: string };

type MultipleChoiceMsg = CustomMessage<
  "multiple_choice",
  {
    field?: string;          // e.g., "q1_when", "q2_where", ...
    required?: boolean;
    content?: string;        // question text (optional; we'll supply one)
    options: MCOption[];     // not strictly needed when we use our presets
  }
>;

// ----- Question presets -----
const QUESTIONS: Record<
  string,
  { title: string; options: MCOption[]; otherLabel?: string }
> = {
  q1_when: {
    title: "When did the pain start?",
    options: [
      { value: "just_now", label: "Just now (within the last hour)" },
      { value: "earlier_today", label: "Earlier today" },
      { value: "yesterday", label: "Yesterday" },
      { value: "several_days", label: "Several days ago" },
      { value: "other", label: "Other / describe" },
    ],
  },
  q2_where: {
    title: "Where do you feel the pain?",
    options: [
      { value: "mid_chest", label: "Middle of chest" },
      { value: "left_chest", label: "Left side of chest" },
      { value: "right_chest", label: "Right side of chest" },
      {
        value: "spreads",
        label: "Spreads to left arm / jaw / neck / back",
      },
      { value: "other", label: "Other / describe" },
    ],
  },
  q3_feel: {
    title: "What does the pain feel like?",
    options: [
      { value: "pressure", label: "Pressure or squeezing" },
      { value: "sharp", label: "Sharp or stabbing" },
      { value: "burning", label: "Burning" },
      { value: "tightness", label: "Tightness / heaviness" },
      { value: "other", label: "Other / describe" },
    ],
  },
  q4_worse: {
    title: "What makes it worse?",
    options: [
      { value: "activity", label: "Physical activity (walking, stairs, exercise)" },
      { value: "breathing_position", label: "Breathing deeply or changing position" },
      { value: "eating_drinking", label: "Eating or drinking" },
      { value: "stress_anxiety", label: "Stress or anxiety" },
      { value: "not_sure", label: "Not sure" },
      { value: "other", label: "Other / describe" },
    ],
  },
  q5_better: {
    title: "What makes it better?",
    options: [
      { value: "rest", label: "Rest" },
      { value: "stop_activity", label: "Stopping activity" },
      { value: "medicine", label: "Medicine (nitroglycerin, antacids, painkillers)" },
      { value: "nothing_helps", label: "Nothing helps" },
      { value: "not_sure", label: "Not sure" },
      { value: "other", label: "Other / describe" },
    ],
  },
  q6_sameTime: {
    title: "Do you have any of these at the same time?",
    options: [
      { value: "sob", label: "Shortness of breath" },
      { value: "sweating", label: "Sweating" },
      { value: "nausea_vomiting", label: "Nausea or vomiting" },
      { value: "dizziness_fainting", label: "Dizziness or fainting" },
      { value: "fast_irregular_heartbeat", label: "Fast or irregular heartbeat" },
      { value: "none", label: "No, none of these" },
      { value: "other", label: "Other / describe" },
    ],
  },
  q7_duration: {
    title: "Duration – How long does each episode last?",
    options: [
      { value: "seconds", label: "A few seconds" },
      { value: "1_5_min", label: "1–5 minutes" },
      { value: "5_30_min", label: "5–30 minutes" },
      { value: "more_than_30_min", label: "More than 30 minutes" },
      { value: "hours", label: "Hours" },
      { value: "other", label: "Other / describe" },
    ],
  },
  q8_frequency: {
    title: "Frequency – How often does it happen?",
    options: [
      { value: "once", label: "Only once" },
      { value: "few_times_day", label: "A few times a day" },
      { value: "daily", label: "Daily" },
      { value: "few_times_week", label: "A few times a week" },
      { value: "less_than_week", label: "Less than once a week" },
      { value: "other", label: "Other / describe" },
    ],
  },
  q9_severity: {
    title: "Severity – On a scale of 0–10, how bad is the pain?",
    options: [
      { value: "0_2", label: "0–2 (mild)" },
      { value: "3_5", label: "3–5 (moderate)" },
      { value: "6_7", label: "6–7 (severe)" },
      { value: "8_10", label: "8–10 (very severe / worst ever)" },
      { value: "other", label: "Other / describe" },
    ],
  },
};

// Order → next question
const FLOW: string[] = [
  "q1_when",
  "q2_where",
  "q3_feel",
  "q4_worse",
  "q5_better",
  "q6_sameTime",
  "q7_duration",
  "q8_frequency",
  "q9_severity",
];

// Map each question field to where we store it in triageAnswers
const STORE_KEY: Record<string, keyof typeof triageAnswers> = {
  q1_when: "whenStart" as any,
  q2_where: "painLocation" as any,
  q3_feel: "painQuality" as any,
  q4_worse: "worseWith" as any,
  q5_better: "betterWith" as any,
  q6_sameTime: "concurrentSymptoms" as any,
  q7_duration: "duration" as any,
  q8_frequency: "frequency" as any,
  q9_severity: "severity" as any,
};

// ----- Helpers -----
function nextField(current?: string): string | null {
  if (!current) return FLOW[0];
  const i = FLOW.indexOf(current);
  return i >= 0 && i < FLOW.length - 1 ? FLOW[i + 1] : null;
}

function ask(storeAdd: (msg: any) => void, field: string) {
  const spec = QUESTIONS[field];
  if (!spec) return;
  storeAdd({
    role: "assistant",
    type: "multiple_choice",
    field,
    required: true,
    content: spec.title,
    options: spec.options,
  } as any);
}

// ----- Renderer -----
const LocalMultipleChoiceRenderer: MessageRenderer =
  createMessageRenderer<MultipleChoiceMsg>({
    type: "multiple_choice",
    namespace: "patient-ui",
    validateMessage: (m): m is MultipleChoiceMsg =>
      m.type === "multiple_choice",

    render: (message) => {
      const addMessage = useCedarStore((s) => s.addMessage);
      const [picked, setPicked] = React.useState<string | null>(null);

      // Ensure we always render with our presets if the message came without them
      const field = (message as any).field ?? FLOW[0];
      const preset = QUESTIONS[field] ?? QUESTIONS[FLOW[0]];
      const options = preset.options;

      const onPick = (opt: MCOption) => {
        if (picked) return;
        setPicked(opt.value);

        // 1) Save local answer
        const storeKey = STORE_KEY[field];
        if (storeKey) {
          // If "other", record sentinel; long text will be saved by long_answer renderer under `${storeKey}Other`
          (triageAnswers as any)[storeKey] = opt.value;
        }

        // 2) Confirm
        addMessage({
          role: "assistant",
          type: "text",
          content: `Thanks, recorded your answer: ${opt.label}.`,
        } as any);

        // 3) If "other", ask for typed details
        if (opt.value === "other") {
          addMessage({
            role: "assistant",
            type: "long_answer",
            field: `${field}_other`, // your long_answer renderer can store this e.g. triageAnswers[`${storeKey}Other`]
            content: `Please briefly describe for: ${preset.title}`,
            placeholder: "Type a brief description…",
            rows: 3,
            buttonLabel: "Submit",
          } as any);
        }

        // 4) Ask next question (if any)
        const nf = nextField(field);
        if (nf) {
          ask(addMessage, nf);
        } else {
          // Done
          addMessage({
            role: "assistant",
            type: "text",
            content: "Thanks — that’s everything for now.",
          } as any);
          
          window.dispatchEvent(new CustomEvent("triage:move-bottom-right"));
        }
      };

      return (
        <div className="space-y-2">
          <div className="font-medium">
            {preset.title}
          </div>
          <div className="flex flex-wrap gap-2">
            {options.map((opt) => (
              <button
                key={`${opt.label}-${opt.value}`}
                onClick={() => onPick(opt)}
                disabled={!!picked}
                className="px-3 py-1 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50"
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      );
    },
  });

export default LocalMultipleChoiceRenderer;