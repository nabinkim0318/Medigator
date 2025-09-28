"use client";

import React, { Suspense } from "react";
import PatientInterface from "../pages/PatientInterface";

export default function PatientPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <PatientInterface />
    </Suspense>
  );
}
