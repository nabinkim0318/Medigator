"use client";

import React, { useState } from "react";
import { X, User, Clock } from "lucide-react";

export interface Patient {
  id: string;
  name: string;
  age: number;
  gender: "Male" | "Female";
  bloodGroup: string;
  phone: string;
  email: string;
  avatar: string;
  initials: string;
}

interface PatientInfoPopupProps {
  isOpen: boolean;
  onClose: () => void;
  patient?: Patient | null;
}

const PatientInfoPopup: React.FC<PatientInfoPopupProps> = ({
  isOpen,
  onClose,
  patient,
}) => {
  const [selectedQuestion, setSelectedQuestion] = useState<string>("");
  if (!isOpen || !patient) return null;

  // You can augment these with real fields from your store/API
  const patientData = {
    name: patient.name,
    mrn: "RCC22279",
    lastAppointment: "11-10-2024",
    ageGender: `${patient.age} ${patient.gender}`,
    dateOfBirth: "11-11-2000",
    age: patient.age,
    gender: patient.gender,
    nationality: "AUS",
    recentTravel: "Student",
    nationalId: "XXXX",
    email: patient.email,
    heartRate: "88 bpm",
    bloodPressure: "120/78 mmHg",
    temperature: "98.6 °F [37.0 °C]",
    oxygenSaturation: "97%",
  };

  const medicalHistory = ["Hypertension, Hyperlipidemia"];
  const recentTravel = "Long Int'l Flight 3 Weeks Ago";
  const hpiSymptoms = [
    "Substernal chest pressure radiating to left arm",
    "Started 2 hours ago, worsened in exertion",
    "Alleviating with rest",
  ];
  const rosSymptoms = [
    "Shortness of breath, diaphoresis",
    "Denies fever, cough, or leg swelling",
  ];
  const dangerousSymptoms = "Shortness of breath, Diaphoresis";
  const painScale = "9/10";
  const smokingAlcohol = "Non-smoker, Social drinker";
  const medications = "Aspirin, Lisinopril, Atorvastatin";
  const allergies = "No known drug allergies";
  const familyHistory = "No significant history";
  const icdCodes = [
    { code: "R07.9", description: "Chest pain, unspecified" },
    { code: "93000", description: "Electrocardiogram, routine ECG" },
  ];
  const suspectedConditions = ["Myocardial Infarction"];
  const recommendedResearch = [
    {
      title: "MI Biomarkers",
      subtitle: "Reflex to high-LI vs old, drugs and biomarkers",
      rank: "Rank 1",
      author: "Author Name",
      avatar:
        "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=40&h=40&fit=crop&crop=face",
      summary:
        "High-sensitivity troponin detected myocardial infarction 3–6 hours earlier than standard methods.\nEarly detection improved patient outcomes by reducing time to treatment initiation.",
    },
    {
      title: "PCI Outcomes in STEMI Patients",
      subtitle: "By Carla Chen",
      rank: "Rank 2",
      author: "Carla Chen",
      avatar:
        "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=40&h=40&fit=crop&crop=face",
      summary:
        "ECG within 10 minutes of chest pain onset remains the gold standard for MI diagnosis.\nCombining ECG with biomarker testing reduces false negatives in early-stage infarction.",
    },
  ];
  const similarPatients = [
    {
      id: "Patient A",
      condition: "Ischemic Heart Disease Attack",
      details: "Similar chief and clinical factors, symptoms and vital signs",
      status: "Correct Diag",
    },
    {
      id: "Patient B",
      condition: "Diagnosed as a STEMI MI",
      details: "Different chest pain symptoms and medical history",
      status: "Incorrect Diag",
    },
  ];
  const questions = ["How long does each episode of chest pain last?"];

  const InfoSection: React.FC<{ title: string; children: React.ReactNode }> = ({
    title,
    children,
  }) => (
    <div style={{ marginBottom: "24px" }}>
      <h3
        style={{
          fontSize: "16px",
          fontWeight: "600",
          color: "#1f2937",
          margin: "0 0 12px 0",
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
          borderRadius: "16px",
          width: "95%",
          maxWidth: "1400px",
          maxHeight: "90vh",
          overflow: "hidden",
          boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: "24px 32px",
            borderBottom: "1px solid #e5e7eb",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <h2
            style={{
              fontSize: "24px",
              fontWeight: "600",
              color: "#1f2937",
              margin: 0,
            }}
          >
            Patient Details
          </h2>
          <button
            onClick={onClose}
            style={{
              padding: "8px",
              backgroundColor: "transparent",
              border: "none",
              borderRadius: "8px",
              cursor: "pointer",
              color: "#6b7280",
              transition: "all 0.2s",
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.backgroundColor =
                "#f3f4f6";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.backgroundColor =
                "transparent";
            }}
          >
            <X style={{ width: "24px", height: "24px" }} />
          </button>
        </div>

        {/* Content */}
        <div
          style={{
            display: "flex",
            height: "calc(90vh - 100px)",
            overflow: "hidden",
          }}
        >
          {/* Left Column */}
          <div
            style={{
              width: "300px",
              padding: "32px",
              borderRight: "1px solid #e5e7eb",
              overflow: "auto",
            }}
          >
            {/* Patient Header */}
            <div style={{ marginBottom: "32px" }}>
              <h3
                style={{
                  fontSize: "20px",
                  fontWeight: "600",
                  color: "#1f2937",
                  margin: "0 0 4px 0",
                }}
              >
                {patientData.name}
              </h3>
              <p
                style={{
                  color: "#6b7280",
                  fontSize: "14px",
                  margin: "0 0 16px 0",
                }}
              >
                MRN: {patientData.mrn}
              </p>

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "16px",
                  marginBottom: "16px",
                }}
              >
                <div
                  style={{ display: "flex", alignItems: "center", gap: "6px" }}
                >
                  <Clock
                    style={{ width: "16px", height: "16px", color: "#6b7280" }}
                  />
                  <span style={{ fontSize: "12px", color: "#6b7280" }}>
                    Last Appointment
                  </span>
                </div>
                <div
                  style={{ display: "flex", alignItems: "center", gap: "6px" }}
                >
                  <User
                    style={{ width: "16px", height: "16px", color: "#6b7280" }}
                  />
                  <span style={{ fontSize: "12px", color: "#6b7280" }}>
                    Age & Gender
                  </span>
                </div>
              </div>

              <div
                style={{ display: "flex", alignItems: "center", gap: "16px" }}
              >
                <span
                  style={{
                    fontSize: "12px",
                    color: "#1f2937",
                    fontWeight: "500",
                  }}
                >
                  {patientData.lastAppointment}
                </span>
                <span
                  style={{
                    fontSize: "12px",
                    color: "#1f2937",
                    fontWeight: "500",
                  }}
                >
                  {patientData.ageGender}
                </span>
              </div>

              <button
                style={{
                  marginTop: "16px",
                  padding: "8px 16px",
                  backgroundColor: "#f97316",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  fontSize: "12px",
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLElement).style.backgroundColor =
                    "#ea580c";
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLElement).style.backgroundColor =
                    "#f97316";
                }}
              >
                View Diagnosis History
              </button>
            </div>

            {/* Patient Information */}
            <InfoSection title="Patient Information">
              <DataRow label="Patient Name" value={patientData.name} />
              <DataRow label="Date of Birth" value={patientData.dateOfBirth} />
              <DataRow label="Age" value={String(patientData.age)} />
              <DataRow label="Gender" value={patientData.gender} />
              <DataRow label="Nationality" value={patientData.nationality} />
              <DataRow label="Recent Travel" value={patientData.recentTravel} />
              <DataRow label="National ID" value={patientData.nationalId} />
              <DataRow label="Email ID" value={patientData.email} />
            </InfoSection>

            {/* Patient Data */}
            <InfoSection title="Patient Data">
              <DataRow label="Heart Rate (HR)" value={patientData.heartRate} />
              <DataRow
                label="Blood Pressure (BP)"
                value={patientData.bloodPressure}
              />
              <DataRow label="Temperature" value={patientData.temperature} />
              <DataRow
                label="Oxygen Saturation"
                value={patientData.oxygenSaturation}
              />
            </InfoSection>
          </div>

          {/* Middle Column */}
          <div style={{ flex: 1, padding: "32px", overflow: "auto" }}>
            {/* HPI and ROS */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "24px",
                marginBottom: "32px",
              }}
            >
              <div
                style={{
                  backgroundColor: "#fefce8",
                  border: "1px solid #fde047",
                  borderRadius: "12px",
                  padding: "20px",
                }}
              >
                <h4
                  style={{
                    color: "#f59e0b",
                    fontSize: "14px",
                    fontWeight: "600",
                    margin: "0 0 12px 0",
                  }}
                >
                  HPI
                </h4>
                <ul style={{ margin: 0, paddingLeft: "16px" }}>
                  {hpiSymptoms.map((symptom, index) => (
                    <li
                      key={index}
                      style={{
                        fontSize: "14px",
                        color: "#1f2937",
                        marginBottom: "8px",
                      }}
                    >
                      {symptom}
                    </li>
                  ))}
                </ul>
              </div>

              <div
                style={{
                  backgroundColor: "#fefce8",
                  border: "1px solid #fde047",
                  borderRadius: "12px",
                  padding: "20px",
                }}
              >
                <h4
                  style={{
                    color: "#f59e0b",
                    fontSize: "14px",
                    fontWeight: "600",
                    margin: "0 0 12px 0",
                  }}
                >
                  ROS
                </h4>
                <ul style={{ margin: 0, paddingLeft: "16px" }}>
                  {rosSymptoms.map((symptom, index) => (
                    <li
                      key={index}
                      style={{
                        fontSize: "14px",
                        color: "#1f2937",
                        marginBottom: "8px",
                      }}
                    >
                      {symptom}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Medical Information Grid */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(3, 1fr)",
                gap: "20px",
                marginBottom: "32px",
              }}
            >
              <div>
                <h4
                  style={{
                    fontSize: "14px",
                    fontWeight: "600",
                    color: "#1f2937",
                    margin: "0 0 8px 0",
                  }}
                >
                  Past Medical History
                </h4>
                <p style={{ fontSize: "14px", color: "#6b7280", margin: 0 }}>
                  {medicalHistory[0]}
                </p>
              </div>

              <div>
                <h4
                  style={{
                    fontSize: "14px",
                    fontWeight: "600",
                    color: "#1f2937",
                    margin: "0 0 8px 0",
                  }}
                >
                  Dangerous Symptoms
                </h4>
                <p style={{ fontSize: "14px", color: "#6b7280", margin: 0 }}>
                  {dangerousSymptoms}
                </p>
              </div>

              <div>
                <h4
                  style={{
                    fontSize: "14px",
                    fontWeight: "600",
                    color: "#1f2937",
                    margin: "0 0 8px 0",
                  }}
                >
                  Pain Scale
                </h4>
                <p style={{ fontSize: "14px", color: "#6b7280", margin: 0 }}>
                  {painScale}
                </p>
              </div>

              <div>
                <h4
                  style={{
                    fontSize: "14px",
                    fontWeight: "600",
                    color: "#1f2937",
                    margin: "0 0 8px 0",
                  }}
                >
                  Recent Travel
                </h4>
                <p style={{ fontSize: "14px", color: "#6b7280", margin: 0 }}>
                  {recentTravel}
                </p>
              </div>

              <div>
                <h4
                  style={{
                    fontSize: "14px",
                    fontWeight: "600",
                    color: "#1f2937",
                    margin: "0 0 8px 0",
                  }}
                >
                  Smoking, Alcohol
                </h4>
                <p style={{ fontSize: "14px", color: "#6b7280", margin: 0 }}>
                  {smokingAlcohol}
                </p>
              </div>

              <div>
                <h4
                  style={{
                    fontSize: "14px",
                    fontWeight: "600",
                    color: "#1f2937",
                    margin: "0 0 8px 0",
                  }}
                >
                  Medications
                </h4>
                <p style={{ fontSize: "14px", color: "#6b7280", margin: 0 }}>
                  {medications}
                </p>
              </div>

              <div>
                <h4
                  style={{
                    fontSize: "14px",
                    fontWeight: "600",
                    color: "#1f2937",
                    margin: "0 0 8px 0",
                  }}
                >
                  Pregnancy
                </h4>
                <p style={{ fontSize: "14px", color: "#6b7280", margin: 0 }}>
                  Not applicable
                </p>
              </div>

              <div>
                <h4
                  style={{
                    fontSize: "14px",
                    fontWeight: "600",
                    color: "#1f2937",
                    margin: "0 0 8px 0",
                  }}
                >
                  Allergies
                </h4>
                <p style={{ fontSize: "14px", color: "#6b7280", margin: 0 }}>
                  {allergies}
                </p>
              </div>

              <div>
                <h4
                  style={{
                    fontSize: "14px",
                    fontWeight: "600",
                    color: "#1f2937",
                    margin: "0 0 8px 0",
                  }}
                >
                  Family History
                </h4>
                <p style={{ fontSize: "14px", color: "#6b7280", margin: 0 }}>
                  {familyHistory}
                </p>
              </div>
            </div>

            {/* ICD Codes and Suspected Conditions */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 2fr",
                gap: "24px",
              }}
            >
              <div>
                <h4
                  style={{
                    fontSize: "16px",
                    fontWeight: "600",
                    color: "#f59e0b",
                    margin: "0 0 16px 0",
                  }}
                >
                  Suspected Condition(s)
                </h4>
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "8px",
                  }}
                >
                  {suspectedConditions.map((condition, index) => (
                    <div
                      key={index}
                      style={{
                        padding: "8px 12px",
                        backgroundColor: "#f9fafb",
                        borderRadius: "6px",
                        fontSize: "14px",
                        color: "#1f2937",
                      }}
                    >
                      {condition}
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h4
                  style={{
                    fontSize: "16px",
                    fontWeight: "600",
                    color: "#f59e0b",
                    margin: "0 0 16px 0",
                  }}
                >
                  Likely ICD-10 and CPT Codes
                </h4>
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "12px",
                  }}
                >
                  {icdCodes.map((code, index) => (
                    <div
                      key={index}
                      style={{
                        backgroundColor: "#f97316",
                        color: "white",
                        padding: "12px 16px",
                        borderRadius: "8px",
                      }}
                    >
                      <div style={{ fontWeight: "600", fontSize: "14px" }}>
                        {code.code}: {code.description}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div
            style={{
              width: "350px",
              padding: "32px",
              borderLeft: "1px solid #e5e7eb",
              overflow: "auto",
            }}
          >
            {/* Similar Patient Cases */}
            <InfoSection title="Similar Patient Cases">
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "16px",
                }}
              >
                {similarPatients.map((sp, index) => (
                  <div
                    key={index}
                    style={{
                      padding: "16px",
                      backgroundColor: "#f9fafb",
                      borderRadius: "8px",
                    }}
                  >
                    <h5
                      style={{
                        fontSize: "14px",
                        fontWeight: "600",
                        color: "#1f2937",
                        margin: "0 0 8px 0",
                      }}
                    >
                      {sp.id}
                    </h5>
                    <p
                      style={{
                        fontSize: "13px",
                        fontWeight: "500",
                        color: "#1f2937",
                        margin: "0 0 8px 0",
                      }}
                    >
                      {sp.condition}
                    </p>
                    <p
                      style={{
                        fontSize: "12px",
                        color: "#6b7280",
                        margin: "0 0 12px 0",
                      }}
                    >
                      {sp.details}
                    </p>
                    <span
                      style={{
                        fontSize: "11px",
                        fontWeight: "600",
                        color: "white",
                        backgroundColor:
                          sp.status === "Correct Diag" ? "#10b981" : "#f59e0b",
                        padding: "4px 8px",
                        borderRadius: "4px",
                      }}
                    >
                      {sp.status}
                    </span>
                  </div>
                ))}
              </div>
            </InfoSection>

            {/* Recommended Research */}
            <InfoSection title="Recommended Research">
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "16px",
                }}
              >
                {recommendedResearch.map((item, index) => (
                  <div
                    key={index}
                    style={{
                      display: "flex",
                      alignItems: "flex-start",
                      gap: "12px",
                      padding: "12px",
                      backgroundColor: "#f9fafb",
                      borderRadius: "8px",
                    }}
                  >
                    <img
                      src={item.avatar}
                      alt={item.author}
                      style={{
                        width: "32px",
                        height: "32px",
                        borderRadius: "50%",
                        objectFit: "cover",
                      }}
                    />
                    <div style={{ flex: 1 }}>
                      <h5
                        style={{
                          fontSize: "14px",
                          fontWeight: "600",
                          color: "#1f2937",
                          margin: "0 0 4px 0",
                        }}
                      >
                        {item.title}
                      </h5>
                      <p
                        style={{
                          fontSize: "12px",
                          color: "#6b7280",
                          margin: "0 0 8px 0",
                        }}
                      >
                        {item.subtitle}
                      </p>
                      <span
                        style={{
                          fontSize: "10px",
                          fontWeight: "600",
                          color: "#1f2937",
                          backgroundColor: "#f59e0b",
                          padding: "2px 6px",
                          borderRadius: "4px",
                        }}
                      >
                        {item.rank}
                      </span>
                      <p
                        style={{
                          fontSize: "12px",
                          color: "#1f2937",
                          margin: "8px 0 8px 0",
                        }}
                      >
                        {item.summary}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </InfoSection>

            {/* Suggested Questions */}
            <InfoSection title="Suggested Questions">
              <div style={{ marginBottom: "16px" }}>
                {questions.map((question, index) => (
                  <div key={index} style={{ marginBottom: "12px" }}>
                    <div
                      style={{
                        padding: "12px",
                        backgroundColor: "#f9fafb",
                        borderRadius: "8px",
                        fontSize: "14px",
                        color: "#1f2937",
                        marginBottom: "8px",
                      }}
                    >
                      {question}
                    </div>
                    <div style={{ display: "flex", gap: "8px" }}>
                      <textarea
                        className="w-full min-h-[160px] rounded-2xl border border-gray-200 px-4 py-3 outline-none focus:ring-2 focus:ring-orange-200 resize-y"
                        value={
                          selectedQuestion === question ? selectedQuestion : ""
                        }
                        onChange={(e) => setSelectedQuestion(e.target.value)}
                      />
                    </div>
                  </div>
                ))}
              </div>
              <button
                style={{
                  width: "100%",
                  padding: "10px",
                  backgroundColor: "#f97316",
                  color: "white",
                  border: "none",
                  borderRadius: "8px",
                  fontSize: "14px",
                  fontWeight: "500",
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLElement).style.backgroundColor =
                    "#ea580c";
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLElement).style.backgroundColor =
                    "#f97316";
                }}
              >
                Add Questions
              </button>
            </InfoSection>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientInfoPopup;
