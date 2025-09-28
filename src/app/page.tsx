"use client";

import { Sign } from "crypto";
import DoctorPatientView from "./pages/DoctorPatientView";
import OnboardingQuestionnaire from "./pages/OnboardingQuestionaire";
import OnboardingThankYou from "./pages/OnboardingThankYou";
import ProfileQuestionnaire from "./pages/ProfileQuestionnaire";
import SignIn from "./pages/SignIn";

export default function Home() {
  return (
    <SignIn />
  );
}
