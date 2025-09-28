"use client";

import React, { Suspense } from "react";
import OnboardingThankYou from "../pages/OnboardingThankYou";

export default function OnboardingTYPageRoute() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <OnboardingThankYou />
    </Suspense>
  );
}
