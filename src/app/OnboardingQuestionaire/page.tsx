"use client";

import React, { Suspense } from "react";
import OnboardingQuestionnaire from "../pages/OnboardingQuestionaire";

export default function OnboardingPageRoute() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <OnboardingQuestionnaire />
    </Suspense>
  );
}
