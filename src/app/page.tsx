"use client";

import { CedarCopilot } from "cedar-os";
import PatientInterface from "./pages/PatientInterface";
import LocalMultipleChoiceRenderer from "@/cedar/renderers/LocalMultipleChoiceRenderer";
import LocalLongAnswerRenderer from "@/cedar/renderers/LocalLongAnswerRenderer";
import SignIn from "./pages/SignIn";

export default function Home() {
  return (
    <CedarCopilot
      // Omit llmProvider so the first questions never call an LLM.
      // Add it later when you want AI for the rest of the flow.
      // llmProvider={{ provider: "openai", apiKey: process.env.NEXT_PUBLIC_OPENAI_API_KEY ?? "" }}

      messageRenderers={[LocalLongAnswerRenderer, LocalMultipleChoiceRenderer]}
      messageStorage={{ type: "local" }} // or { type: "none" } to avoid persistence
      // userId="user-123"   // recommended if you want per-user persistence
      // threadId="thread-abc"
    >
      <SignIn />
    </CedarCopilot>
  );
}
