"use client";

import React, { useState } from "react";
import DoctorDashboard from "./pages/DoctorDashboard";

import OnboardingQuestionnaire from "./pages/OnboardingQuestionaire";
import OnboardingThankYou from "./pages/OnboardingThankYou";
import ProfileQuestionnaire from "./pages/ProfileQuestionnaire";
import SignIn from "./pages/SignIn";

export default function Home() {
  const [activeApp, setActiveApp] = useState<"patient" | "doctor">("patient");

  return <SignIn />;
}
