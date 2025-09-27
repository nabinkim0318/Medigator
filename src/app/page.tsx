"use client";

import { CedarCopilot } from "cedar-os";
import AppointmentsPage from "./pages/AppointmentsPage";
import PatientInterface from "./pages/PatientInterface";
import OnboardingQuestionnaire from "./pages/OnboardingQuestionaire";

export default function Home() {
  return (
    <OnboardingQuestionnaire />
  );
}
