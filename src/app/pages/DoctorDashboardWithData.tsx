"use client";

import React from "react";
import DoctorDashboard from "./DoctorDashboard";

export interface EnhancedAppointmentRow {
  id: string;
  time: string;
  date: string;
  patient: { name: string; initials: string; gender: "Male" | "Female" };
  doctor: string;
  token?: string;
  summary?: {
    hpi?: string;
    ros?: unknown;
    pmh?: string;
    meds?: string;
    flags?: unknown;
    codes?: unknown;
  };
  evidence?: unknown[];
}

/** Shell with local demo appointments. Not a live clinical feed. */
export default function DoctorDashboardWithData() {
  return <DoctorDashboard />;
}
