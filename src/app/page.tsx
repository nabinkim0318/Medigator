"use client";

import { CedarCopilot } from "cedar-os";
import AppointmentsPage from "./pages/AppointmentsPage";
import PatientInterface from "./pages/PatientInterface";
import OnboardingQuestionnaire from "./pages/OnboardingQuestionaire";
import SignIn from "./pages/SignIn";
import DoctorDashboard from "./pages/DoctorDashboard";
import DoctorPatientView from "./pages/DoctorPatientView";
import OnboardingThankYou from "./pages/OnboardingThankYou";
import PatientThankYou from "./pages/PatientThankYou";

export default function Home() {
  return (
    <SignIn />
  );
}
