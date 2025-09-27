"use client";

import * as React from "react";
import {
  createMessageRenderer,
  type CustomMessage,
  type MessageRenderer,
  useCedarStore,
} from "cedar-os";
import { triageAnswers } from "@/cedar/triage/triageState"; // or your own store

type LongAnswerMsg = CustomMessage<
  "long_answer",
  { field: string; content?: string; placeholder?: string; rows?: number; buttonLabel?: string }
>;

const LocalLongAnswerRenderer: MessageRenderer = createMessageRenderer<LongAnswerMsg>({
  type: "long_answer",
  namespace: "patient-ui",
  validateMessage: (m): m is LongAnswerMsg =>
    m.type === "long_answer" && typeof (m as any).field === "string",

  render: (message) => {
    const addMessage = useCedarStore((s) => s.addMessage);
    const [text, setText] = React.useState("");
    const [submitted, setSubmitted] = React.useState(false);

    const onSubmit = () => {
      if (!text.trim() || submitted) return;
      setSubmitted(true);

      // save locally
      triageAnswers[message.field as keyof typeof triageAnswers] = text.trim();

      // local confirmation (no agent call)
      addMessage({
        role: "assistant",
        type: "text",
        content: "Thanks — your description has been recorded.",
      } as any);
    };

    return (
      <div className="space-y-2">
        {message.content && <div className="font-medium">{message.content}</div>}
        <textarea
          rows={message.rows ?? 3}
          placeholder={message.placeholder ?? "Type your response…"}
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={submitted}
          className="w-full border rounded-lg p-2 disabled:opacity-50"
        />
        <button
          onClick={onSubmit}
          disabled={submitted || !text.trim()}
          className="px-3 py-1 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50"
        >
          {message.buttonLabel ?? "Submit"}
        </button>
      </div>
    );
  },
});

export default LocalLongAnswerRenderer;
