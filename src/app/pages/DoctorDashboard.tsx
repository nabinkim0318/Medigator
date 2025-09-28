"use client";

import React, { useState } from "react";
import Sidebar from "./Sidebar";

// Your existing dashboard component + types
import DoctorDashboard, {
  AppointmentRow,
  ClinicalUpdate,
  PatientFeeItem,
} from "./DoctorPage";
import AppointmentsPage from "./AppointmentsPage";
import DoctorPatientView from "./DoctorPatientView";

// (Optional) bring in your standalone appointments component if you have it)
// import Appointments from "./Appointments";

const appointments: AppointmentRow[] = [
  {
    id: "a1",
    time: "9:30 AM",
    date: "05/12/2022",
    patient: { name: "Elizabeth Polson", initials: "EP", gender: "Female" },
    doctor: "Dr. John",
  },
  {
    id: "a2",
    time: "9:30 AM",
    date: "05/12/2022",
    patient: { name: "John David", initials: "JD", gender: "Male" },
    doctor: "Dr. Joel",
  },
  {
    id: "a3",
    time: "10:30 AM",
    date: "05/12/2022",
    patient: { name: "Krishtav Rajan", initials: "KR", gender: "Male" },
    doctor: "Dr. Joel",
  },
  {
    id: "a4",
    time: "11:00 AM",
    date: "05/12/2022",
    patient: { name: "Sumanth Tinson", initials: "ST", gender: "Male" },
    doctor: "Dr. John",
  },
  {
    id: "a5",
    time: "11:30 AM",
    date: "05/12/2022",
    patient: { name: "EG Subramani", initials: "ES", gender: "Male" },
    doctor: "Dr. John",
  },
];

const completedAppointments: AppointmentRow[] = [
  {
    id: "c1",
    time: "8:00 AM",
    date: "05/12/2022",
    patient: { name: "Mary Ann", initials: "MA", gender: "Female" },
    doctor: "Dr. John",
  },
  {
    id: "c2",
    time: "8:30 AM",
    date: "05/12/2022",
    patient: { name: "Peter Kim", initials: "PK", gender: "Male" },
    doctor: "Dr. Joel",
  },
  {
    id: "c3",
    time: "9:00 AM",
    date: "05/12/2022",
    patient: { name: "Liam Patel", initials: "LP", gender: "Male" },
    doctor: "Dr. Joel",
  },
  {
    id: "c4",
    time: "9:15 AM",
    date: "05/12/2022",
    patient: { name: "Sophia Lopez", initials: "SL", gender: "Female" },
    doctor: "Dr. John",
  },
];

const updates: ClinicalUpdate[] = [
  {
    id: "c1",
    title: "T2DM: New 130/80 BP Goal",
    author: "By Dr. K. Lee",
    thumb:
      "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&h=80&fit=crop&crop=faces",
    badge: "New",
  },
  {
    id: "c2",
    title: "SGLT2i for Non-Diabetic CKD",
    author: "By Dr. J. Chen",
    thumb:
      "https://images.unsplash.com/photo-1541534401786-2077eed87a72?w=80&h=80&fit=crop&crop=faces",
    badge: "New",
  },
  {
    id: "c3",
    title: "Updated PCP Anxiety Screening",
    author: "By Dr. M. Rodriguez",
    thumb:
      "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=80&h=80&fit=crop&crop=faces",
    badge: "New",
  },
  {
    id: "c4",
    title: "New Oral MDD Drug",
    author: "—",
    thumb:
      "https://images.unsplash.com/photo-1606207554193-62c61d9bf34a?w=80&h=80&fit=crop&crop=faces",
    badge: "Read",
  },
];

const fees: PatientFeeItem[] = [
  {
    id: "f1",
    name: "EG Subramani",
    status: "Doctor fee pending",
    initials: "KR",
  },
  {
    id: "f2",
    name: "Elizabeth Polson",
    status: "Doctor fee pending",
    initials: "KR",
  },
  {
    id: "f3",
    name: "Sumanth Tinson",
    status: "Doctor fee pending",
    initials: "KR",
  },
  {
    id: "f4",
    name: "Krishtav Rajan",
    status: "Doctor fee pending",
    initials: "KR",
  },
];

type Tab =
  | "Dashboard"
  | "Appointments"
  | "Patients"
  | "Doctors"
  | "Messages"
  | "Clinical Updates"
  | "Settings";

export default function DashboardShell() {
  const [active, setActive] = useState<Tab>("Dashboard");

  // Swap content here based on `active`
  const renderContent = () => {
    switch (active) {
      case "Dashboard":
        return (
          <DoctorDashboard
            newAppointments={appointments}
            completedAppointments={completedAppointments}
            clinicalUpdates={updates}
            feeItems={fees}
          />
        );

      case "Appointments":
        // If you have a dedicated Appointments component, render it here:
        return <AppointmentsPage />;

      case "Patients":
        return <DoctorPatientView />;
      case "Doctors":
        return <div></div>;
      case "Messages":
        return <div></div>;
      case "Clinical Updates":
        return <div></div>;
      case "Settings":
        return <div></div>;
      default:
        return null;
    }
  };

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#fef9f5" }}>
      <Sidebar active={active} onSelect={setActive} />
      {/* Main area swaps the component based on the selected tab */}
      <div style={{ flex: 1, display: "flex", minHeight: 0 }}>
        {renderContent()}
      </div>
    </div>
  );
}
