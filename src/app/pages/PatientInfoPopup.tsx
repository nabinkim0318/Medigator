"use client";

import React, { useState } from "react";
import { X, User, Clock } from "lucide-react";
import { useToast } from "../components/ErrorToast";

export interface Patient {
  id: string;
  name: string;
  age?: number;
  gender?: string;
  bloodType?: string;
  phone?: string;
  email?: string;
  ai_summary_status?: string;
  createdAt?: string;
  token?: string;
}

interface PatientInfoPopupProps {
  isOpen: boolean;
  onClose: () => void;
  patient: Patient | null;
  summary?: string | null;
  evidence?: string | null;
}

const PatientInfoPopup: React.FC<PatientInfoPopupProps> = ({
  isOpen,
  onClose,
  patient,
  summary,
  evidence,
}) => {
  const [selectedQuestion, setSelectedQuestion] = useState<string>("");
  const { showToast, ToastContainer } = useToast();

  if (!isOpen || !patient) return null;

  const InfoSection: React.FC<{ title: string; children: React.ReactNode }> = ({
    title,
    children,
  }) => (
    <div style={{ marginBottom: "24px" }}>
      <h3
        style={{
          color: "#f59e0b", // amber-500
          fontSize: "16px",
          fontWeight: "600",
          marginBottom: "12px",
          borderBottom: "1px solid #f59e0b",
          paddingBottom: "4px",
        }}
      >
        {title}
      </h3>
      {children}
    </div>
  );

  const DataRow: React.FC<{ label: string; value: string }> = ({
    label,
    value,
  }) => (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "8px 0",
        borderBottom: "1px solid #f3f4f6",
      }}
    >
      <span style={{ color: "#6b7280", fontSize: "14px" }}>{label}</span>
      <span style={{ color: "#1f2937", fontSize: "14px", fontWeight: "500" }}>
        {value}
      </span>
    </div>
  );

  return (
    <>
      <ToastContainer />
      <div
        style={{
          position: "fixed",
          inset: 0,
          backgroundColor: "rgba(0, 0, 0, 0.5)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1000,
          padding: "20px",
        }}
      >
        <div
          style={{
            backgroundColor: "white",
            borderRadius: "12px",
            width: "100%",
            maxWidth: "800px",
            maxHeight: "90vh",
            overflow: "hidden",
            display: "flex",
            flexDirection: "column",
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: "24px 24px 16px 24px",
              borderBottom: "1px solid #e5e7eb",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <div>
              <h2
                style={{
                  fontSize: "24px",
                  fontWeight: "600",
                  color: "#1f2937",
                  margin: "0 0 4px 0",
                }}
              >
                Patient Details
              </h2>
              <p
                style={{
                  fontSize: "16px",
                  color: "#f59e0b", // amber-500
                  margin: "0",
                  fontWeight: "500",
                }}
              >
                {patient.name}
              </p>
            </div>
            <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
              <button
                style={{
                  backgroundColor: "#f59e0b", // amber-500
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  padding: "8px 16px",
                  fontSize: "14px",
                  fontWeight: "500",
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLElement).style.backgroundColor =
                    "#d97706"; // amber-600
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLElement).style.backgroundColor =
                    "#f59e0b"; // amber-500
                }}
              >
                View Diagnosis History
              </button>
              <button
                onClick={onClose}
                style={{
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  padding: "8px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "#9ca3af",
                }}
              >
                <X size={24} />
              </button>
            </div>
          </div>

          {/* Content */}
          <div
            style={{
              padding: "24px",
              overflowY: "auto",
              flex: 1,
            }}
          >
            {/* Patient Information */}
            <InfoSection title="Patient Information">
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "16px",
                }}
              >
                <DataRow label="Name" value={patient.name} />
                <DataRow label="Age" value={patient.age?.toString() || "N/A"} />
                <DataRow label="Gender" value={patient.gender || "N/A"} />
                <DataRow
                  label="Blood Type"
                  value={patient.bloodType || "N/A"}
                />
                <DataRow label="Phone" value={patient.phone || "N/A"} />
                <DataRow label="Email" value={patient.email || "N/A"} />
                <DataRow
                  label="AI Summary Status"
                  value={patient.ai_summary_status || "pending"}
                />
              </div>
            </InfoSection>

            {/* Patient Summary */}
            {summary && (
              <InfoSection title="Patient Summary">
                <div
                  style={{
                    backgroundColor: "#fef3c7", // amber-100
                    border: "1px solid #f59e0b", // amber-500
                    borderRadius: "8px",
                    padding: "16px",
                    fontSize: "14px",
                    lineHeight: "1.6",
                    color: "#1f2937",
                  }}
                >
                  {summary}
                </div>
              </InfoSection>
            )}

            {/* Likely ICD-10 and CPT Codes */}
            <InfoSection title="Likely ICD-10 and CPT Codes">
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                <span
                  style={{
                    backgroundColor: "#f59e0b", // amber-500
                    color: "white",
                    padding: "4px 12px",
                    borderRadius: "16px",
                    fontSize: "12px",
                    fontWeight: "500",
                  }}
                >
                  ICD-10: R06.02
                </span>
                <span
                  style={{
                    backgroundColor: "#f59e0b", // amber-500
                    color: "white",
                    padding: "4px 12px",
                    borderRadius: "16px",
                    fontSize: "12px",
                    fontWeight: "500",
                  }}
                >
                  CPT: 99213
                </span>
              </div>
            </InfoSection>

            {/* Suspected Conditions */}
            <InfoSection title="Suspected Conditions">
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                <span
                  style={{
                    backgroundColor: "#f59e0b", // amber-500
                    color: "white",
                    padding: "4px 12px",
                    borderRadius: "16px",
                    fontSize: "12px",
                    fontWeight: "500",
                  }}
                >
                  Acute Chest Pain
                </span>
                <span
                  style={{
                    backgroundColor: "#f59e0b", // amber-500
                    color: "white",
                    padding: "4px 12px",
                    borderRadius: "16px",
                    fontSize: "12px",
                    fontWeight: "500",
                  }}
                >
                  Possible MI
                </span>
              </div>
            </InfoSection>

            {/* Recommended Research */}
            <InfoSection title="Recommended Research">
              <div
                style={{
                  backgroundColor: "#fef3c7", // amber-100
                  border: "1px solid #f59e0b", // amber-500
                  borderRadius: "8px",
                  padding: "16px",
                  fontSize: "14px",
                  lineHeight: "1.6",
                  color: "#1f2937",
                }}
              >
                <p style={{ margin: "0 0 12px 0" }}>
                  <strong>Immediate Actions:</strong>
                </p>
                <ul style={{ margin: "0", paddingLeft: "20px" }}>
                  <li>ECG within 10 minutes</li>
                  <li>Cardiac enzymes (troponin)</li>
                  <li>Chest X-ray</li>
                  <li>Vital signs monitoring</li>
                </ul>
              </div>
            </InfoSection>

            {/* Supporting Medical Evidence */}
            {evidence && (
              <InfoSection title="Supporting Medical Evidence">
                <div
                  style={{
                    backgroundColor: "#fef3c7", // amber-100
                    border: "1px solid #f59e0b", // amber-500
                    borderRadius: "8px",
                    padding: "16px",
                    fontSize: "14px",
                    lineHeight: "1.6",
                    color: "#1f2937",
                  }}
                >
                  {evidence}
                </div>
              </InfoSection>
            )}

            {/* Add Questions Button */}
            <InfoSection title="">
              <button
                style={{
                  backgroundColor: "#f59e0b", // amber-500
                  color: "white",
                  border: "none",
                  borderRadius: "8px",
                  padding: "12px 24px",
                  fontSize: "14px",
                  fontWeight: "500",
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLElement).style.backgroundColor =
                    "#d97706"; // amber-600
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLElement).style.backgroundColor =
                    "#f59e0b"; // amber-500
                }}
              >
                Add Questions
              </button>
            </InfoSection>
          </div>
        </div>
      </div>
    </>
  );
};

export default PatientInfoPopup;
