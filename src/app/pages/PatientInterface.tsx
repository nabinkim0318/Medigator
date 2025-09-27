"use client";

import React, { useEffect, useRef } from "react";
import { useCedarStore, useThreadMessages } from "cedar-os";
import { FloatingCedarChat } from "@/cedar/components/chatComponents/FloatingCedarChat";
import { triageAnswers } from "@/cedar/triage/triageState";

export default function PatientInterface() {
  const store = useCedarStore();
  const { messages } = useThreadMessages();

  // Seed Q1 (pain scale) immediately
  const seeded = useRef(false);
  useEffect(() => {
    if (seeded.current) return;
    seeded.current = true;

    store.addMessage({
      role: "assistant",
      type: "multiple_choice",
      field: "painScore",
      required: true,
      content: "On a scale from 1–10, how bad is the pain right now?",
      options: Array.from({ length: 10 }, (_, i) => {
        const v = String(i + 1);
        return { value: v, label: v };
      }),
    } as any);
  }, [store]);

  // Helper to read user input payloads
  const getUserValue = (m: any) => m?.value ?? m?.selection?.value ?? m?.content;

  // Handle the long-answer step (the MC steps are handled by the custom renderer)
  useEffect(() => {
    if (!messages.length) return;
    const last = messages[messages.length - 1];
    if (last.role !== "user") return;

    const prevAssistant = [...messages]
      .slice(0, -1)
      .reverse()
      .find((m) => m.role === "assistant");

    const prevWasDetailsPrompt =
      (prevAssistant?.type === "text" &&
        (prevAssistant as any).field === "detailsPrompt") ||
      (typeof prevAssistant?.content === "string" &&
        prevAssistant.content.startsWith(
          "Please briefly describe any specific symptoms"
        ));

    if (prevWasDetailsPrompt) {
      const details = String(getUserValue(last) ?? "");
      triageAnswers.details = details;

      store.addMessage({
        role: "assistant",
        type: "text",
        content: "Thanks — your description has been recorded.",
      } as any);

      // Example: you now have all three answers in triageAnswers
      // console.log("Collected triage answers:", triageAnswers);
    }
  }, [messages, store]);

  return (
    <div>
      <button
        style={{
          position: "fixed",
          top: 10,
          right: 10,
          zIndex: 1000,
          color: "black",
          backgroundColor: "white",
          padding: "5px 10px",
          borderRadius: "5px",
          boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
        }}
        onClick={() => {
          window.location.href = "/signin";
        }}
      >
        Sign in
      </button>

      <FloatingCedarChat stream={false} />
    </div>
  );
}
