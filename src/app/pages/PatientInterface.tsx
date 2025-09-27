// app/pages/PatientInterface.tsx
"use client";

import React, { useEffect, useRef } from "react";
import { useCedarStore } from "cedar-os";
import { FloatingCedarChat } from "@/cedar/components/chatComponents/FloatingCedarChat";

export default function PatientInterface() {
  const store = useCedarStore();
  const seeded = useRef(false);

  // Seed Q1 (pain 1–10) immediately
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

  return (
    <div>
      <FloatingCedarChat stream={false} />
    </div>
  );
}
