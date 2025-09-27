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
    field?: string;                // e.g., "painScore" or "symptom"
    required?: boolean;
    content?: string;              // question text
    options: MCOption[];           // [{ label, value }]
  }
>;

/**
 * Overrides the built-in "multiple_choice" so a click:
 *  - records the answer locally (triageAnswers),
 *  - shows a confirmation,
 *  - and posts the *next* question in the flow.
 * No LLM calls, no extra "answer:" bubbles.
 */
const LocalMultipleChoiceRenderer: MessageRenderer =
  createMessageRenderer<MultipleChoiceMsg>({
    type: "multiple_choice",
    namespace: "patient-ui",
    validateMessage: (m): m is MultipleChoiceMsg =>
      m.type === "multiple_choice" && Array.isArray((m as any).options),

    render: (message) => {
      const addMessage = useCedarStore((s) => s.addMessage);
      const [picked, setPicked] = React.useState<string | null>(null);

      const onPick = (opt: MCOption) => {
        if (picked) return; // prevent double-clicks
        setPicked(opt.value);

        const field = (message as any).field ?? "choice";

        // 1) Record locally
        if (field === "painScore") triageAnswers.painScore = opt.value;
        if (field === "symptom") triageAnswers.symptom = opt.value;

        // 2) Local confirmation
        const label = opt.label ?? opt.value;
        addMessage({
          role: "assistant",
          type: "text",
          content: `Thanks, recorded your ${field} as ${label}.`,
        } as any);

        // 3) Post NEXT question in the flow
        if (field === "painScore") {
          // Next: symptoms (MC with Other)
          addMessage({
            role: "assistant",
            type: "multiple_choice",
            field: "symptom",
            required: true,
            content: "Which of the following symptoms are you experiencing?",
            options: [
              { value: "abdominal_pain", label: "Abdominal pain" },
              { value: "cough", label: "Cough" },
              { value: "headache", label: "Headache" },
              { value: "other", label: "Other" },
            ],
          } as any);
        } else if (field === "symptom") {
          // Next: long-answer text prompt
          addMessage({
            role: "assistant",
            type: "text",
            // marker so we know the next user message is the long answer
            field: "detailsPrompt",
            content:
              "Please briefly describe any specific symptoms or your current condition.",
          } as any);
        }
      };

      return (
        <div className="space-y-2">
          <div className="font-medium">
            {message.content ?? "Please choose one:"}
          </div>
          <div className="flex flex-wrap gap-2">
            {message.options.map((opt) => (
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
