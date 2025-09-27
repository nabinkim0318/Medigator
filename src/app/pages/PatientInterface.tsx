// app/pages/PatientInterface.tsx
"use client";

import React, { useEffect, useRef, useState } from "react";
import { useCedarStore } from "cedar-os";
import { FloatingCedarChat } from "@/cedar/components/chatComponents/FloatingCedarChat";
import { AnimatePresence } from "framer-motion";

export default function PatientInterface() {
  const store = useCedarStore();
  const seeded = useRef(false);

  // 👇 Will flip to true after long-answer is submitted
  const [docked, setDocked] = useState(false);

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

  // 🔊 Listen for the "dock me" event from the long-answer renderer
  useEffect(() => {
    const handler = () => setDocked(true);
    window.addEventListener("triage:move-bottom-right", handler);
    return () => window.removeEventListener("triage:move-bottom-right", handler);
  }, []);

  // Optionally shrink the chat when docked
  const dockedDimensions = docked
    ? { height: 700 }      // smaller when docked
    : { height: 600 };     // larger before docking

  return (
    <div>
      <FloatingCedarChat stream={false} side={docked ? "right" : "center"} dimensions={dockedDimensions} />
      {docked ? <div>
        INSERT GENERATED PDF HERE
      </div> : <></>}
    </div>
  );
}
