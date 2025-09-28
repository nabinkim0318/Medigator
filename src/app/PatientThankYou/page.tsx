"use client";

import React, { Suspense } from "react";
import PatientThankYou from "../pages/PatientThankYou";

export default function PatientThankYouRoute() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <PatientThankYou />
    </Suspense>
  );
}
