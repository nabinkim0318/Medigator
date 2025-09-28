"use client";

import React, { useState, useEffect } from "react";
import DoctorDashboard from "./DoctorDashboard";

// API base URL
const API_BASE =
  (process.env.NEXT_PUBLIC_API_URL as string) || "http://localhost:8082";

// Enhanced appointment interface with LLM summary
export interface EnhancedAppointmentRow {
  id: string;
  time: string;
  date: string;
  patient: { name: string; initials: string; gender: "Male" | "Female" };
  doctor: string;
  token?: string;
  summary?: {
    hpi?: string;
    ros?: any;
    pmh?: string;
    meds?: string;
    flags?: any;
    codes?: any;
  };
  evidence?: any[];
}

// Mock data with some appointments having LLM summaries
const mockAppointments: EnhancedAppointmentRow[] = [
  {
    id: "a1",
    time: "9:30 AM",
    date: "05/12/2022",
    patient: { name: "Elizabeth Polson", initials: "EP", gender: "Female" },
    doctor: "Dr. John",
    token: "token123",
    summary: {
      hpi: "55-year-old female presents with chest pain radiating to left arm, duration 2 hours",
      ros: {
        cardiovascular: { positive: ["chest pain"], negative: [] },
        respiratory: { positive: [], negative: [] },
      },
      pmh: "Hypertension, Diabetes",
      meds: "Lisinopril, Metformin",
      flags: { ischemic_features: true, dm_followup: false },
    },
    evidence: [
      {
        title: "Chest Pain Evaluation Guidelines",
        content: "Acute chest pain requires immediate ECG and cardiac enzymes",
        year: "2023",
        section: "Emergency Medicine",
      },
    ],
  },
  {
    id: "a2",
    time: "10:00 AM",
    date: "05/12/2022",
    patient: { name: "John David", initials: "JD", gender: "Male" },
    doctor: "Dr. Joel",
    token: "token456",
  },
  {
    id: "a3",
    time: "10:30 AM",
    date: "05/12/2022",
    patient: { name: "Krishtav Rajan", initials: "KR", gender: "Male" },
    doctor: "Dr. Joel",
    token: "token789",
  },
];

export default function DoctorDashboardWithData() {
  const [appointments, setAppointments] =
    useState<EnhancedAppointmentRow[]>(mockAppointments);
  const [loading, setLoading] = useState(false);

  // Load patient data with LLM summaries
  const loadPatientData = async () => {
    setLoading(true);
    try {
      // In a real implementation, you would fetch from your API
      // For now, we'll use mock data that simulates the structure
      const updatedAppointments = await Promise.all(
        mockAppointments.map(async (appointment) => {
          if (appointment.token) {
            try {
              // Fetch appointment summary from API
              const response = await fetch(
                `${API_BASE}/api/v1/patient/appointment/${appointment.token}/summary`,
              );
              if (response.ok) {
                const data = await response.json();

                // Generate LLM summary
                const summaryResponse = await fetch(
                  `${API_BASE}/api/v1/summary`,
                  {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data),
                  },
                );

                if (summaryResponse.ok) {
                  const summaryData = await summaryResponse.json();

                  // Generate RAG evidence
                  const evidenceResponse = await fetch(
                    `${API_BASE}/api/v1/evidence`,
                    {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify(summaryData.summary),
                    },
                  );

                  let evidence = [];
                  if (evidenceResponse.ok) {
                    const evidenceData = await evidenceResponse.json();
                    evidence = evidenceData;
                  }

                  return {
                    ...appointment,
                    summary: summaryData.summary,
                    evidence: evidence,
                  };
                }
              }
            } catch (error) {
              console.warn(
                `Failed to load data for patient ${appointment.patient.name}:`,
                error,
              );
            }
          }
          return appointment;
        }),
      );

      setAppointments(updatedAppointments);
    } catch (error) {
      console.error("Failed to load patient data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPatientData();
  }, []);

  return (
    <div>
      <div
        style={{
          padding: "16px",
          background: "#f8fafc",
          borderBottom: "1px solid #e2e8f0",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <h1
            style={{ fontSize: "24px", fontWeight: "bold", color: "#1e293b" }}
          >
            Doctor Dashboard
          </h1>
          <button
            onClick={loadPatientData}
            disabled={loading}
            style={{
              padding: "8px 16px",
              background: "#3b82f6",
              color: "white",
              border: "none",
              borderRadius: "6px",
              cursor: loading ? "not-allowed" : "pointer",
              opacity: loading ? 0.6 : 1,
            }}
          >
            {loading ? "Loading..." : "Refresh Patient Data"}
          </button>
        </div>
      </div>

      <DoctorDashboard appointments={appointments} loading={loading} />
    </div>
  );
}
