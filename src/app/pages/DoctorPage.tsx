"use client";

import React, { useMemo, useState } from "react";
import { Maximize2, ChevronDown, Users, ClipboardList, Pill, FlaskConical } from "lucide-react";

export type Gender = "Male" | "Female";

export interface AppointmentRow {
  id: string;
  time: string;
  date: string; // DD/MM/YYYY
  patient: { name: string; initials: string; gender: Gender };
  doctor: string;
}

export interface ClinicalUpdate {
  id: string;
  title: string;
  author: string;
  thumb: string;
  badge?: "New" | "Read";
}

export interface PatientFeeItem {
  id: string;
  name: string;
  status: "Doctor fee pending" | "Doctor fee pending (reminder)";
  initials: string;
}

export interface DoctorDashboardProps {
  newAppointments: AppointmentRow[];
  completedAppointments: AppointmentRow[];
  clinicalUpdates: ClinicalUpdate[];
  feeItems: PatientFeeItem[];
}

const StatTile: React.FC<{ icon: React.ReactNode; value: number | string; label: string }> = ({
  icon,
  value,
  label,
}) => (
  <div
    style={{
      background: "white",
      borderRadius: 12,
      boxShadow: "0 1px 3px rgba(0,0,0,.08)",
      padding: 18,
      display: "flex",
      alignItems: "center",
      gap: 14,
      maxHeight: 70,
    }}
  >
    <div
      style={{
        width: 46,
        height: 46,
        borderRadius: 10,
        background: "#fff7ed",
        color: "#ea580c",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {icon}
    </div>
    <div>
      <div style={{ fontSize: 22, fontWeight: 800, color: "#1f2937", lineHeight: 1 }}>{value}</div>
      <div style={{ fontSize: 13, color: "#64748b" }}>{label}</div>
    </div>
  </div>
);

const AvatarBadge: React.FC<{ initials: string; size?: number }> = ({ initials, size = 30 }) => (
  <div
    style={{
      width: size,
      height: size,
      borderRadius: 999,
      background: "#cbd5e1",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      color: "#334155",
      fontWeight: 700,
      fontSize: 12,
    }}
  >
    {initials}
  </div>
);

const DoctorDashboard: React.FC<DoctorDashboardProps> = ({
  newAppointments,
  completedAppointments,
  clinicalUpdates,
  feeItems,
}) => {
  const [apptTab, setApptTab] = useState<"new" | "completed">("new");

  // kept for parity with original (future chart/legend etc.)
  useMemo(
    () => [
      { pct: 55, label: "Hypertension (I10)", color: "#f97316" },
      { pct: 25, label: "URI (J06/J20)", color: "#8b5cf6" },
      { pct: 12, label: "Diabetes (E11)", color: "#22c55e" },
      { pct: 8, label: "Others", color: "#f59e0b" },
    ],
    []
  );

  const rows = apptTab === "new" ? newAppointments : completedAppointments;

  return (
    <main style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0, height: "100vh" }}>
      {/* Top Bar */}
      <div
        style={{
          padding: "18px 28px",
          background: "linear-gradient(180deg, #fff7ed, #ffffff)",
          borderBottom: "1px solid #f1f5f9",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <h1 style={{ margin: 0, fontSize: 28, fontWeight: 800, color: "#374151" }}>Dashboard</h1>
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div
              title="Notifications"
              style={{
                width: 36,
                height: 36,
                borderRadius: 18,
                background: "white",
                boxShadow: "0 1px 2px rgba(0,0,0,.05)",
                position: "relative",
              }}
            >
              <div
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: 8,
                  background: "#ef4444",
                  position: "absolute",
                  right: 8,
                  top: 8,
                }}
              />
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <img
                src="https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=40&h=40&fit=crop&crop=face"
                style={{ width: 40, height: 40, borderRadius: 999 }}
                alt="Doctor"
              />
              <div>
                <div style={{ fontWeight: 800, color: "#334155" }}>Jonitha Cathrine</div>
                <div style={{ fontSize: 12, color: "#94a3b8" }}>Doctor</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content Grid */}
      <div
        style={{
          padding: 24,
          display: "grid",
          gridTemplateColumns: "1.2fr 1.8fr",
          gap: 24,
          flex: 1,
          minHeight: 0,
          overflow: "hidden",
          background: "#fef9f5",
        }}
      >
        {/* Left column */}
        <div style={{ display: "grid", gap: 24, gridTemplateRows: "1fr 1fr", minHeight: 0 }}>
          {/* Activity Overview */}
          <div
            style={{
              background: "white",
              borderRadius: 14,
              boxShadow: "0 1px 3px rgba(0,0,0,.08)",
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
              height: "100%",
              minHeight: 0,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: 18 }}>
              <h3 style={{ margin: 0, color: "#111827", fontSize: 16, fontWeight: 800 }}>Activity Overview</h3>
              <button
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  border: "none",
                  background: "transparent",
                  color: "#64748b",
                  cursor: "pointer",
                  fontWeight: 700,
                }}
              >
                Weekly <ChevronDown size={16} />
              </button>
            </div>

            <div style={{ padding: 18, overflowY: "auto", minHeight: 0 }}>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 14 }}>
                <StatTile icon={<ClipboardList size={22} />} value={100} label="Appointments" />
                <StatTile icon={<Users size={22} />} value={50} label="New Patients" />
                <StatTile icon={<Pill size={22} />} value={500} label="Medicines Sold" />
                <StatTile icon={<FlaskConical size={22} />} value={100} label="Lab Tests" />
              </div>
            </div>
          </div>

          {/* Clinical Updates */}
          <div
            style={{
              background: "white",
              borderRadius: 14,
              boxShadow: "0 1px 3px rgba(0,0,0,.08)",
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
              height: "100%",
              minHeight: 0,
            }}
          >
            <div
              style={{
                padding: "14px 16px",
                borderBottom: "1px solid #e5e7eb",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              <h3 style={{ margin: 0, color: "#111827", fontSize: 16, fontWeight: 800 }}>Clinical Updates</h3>
              <button
                style={{
                  border: "none",
                  background: "transparent",
                  color: "#ea580c",
                  cursor: "pointer",
                  padding: 6,
                  borderRadius: 8,
                }}
              >
                <Maximize2 size={16} />
              </button>
            </div>

            <div
              style={{
                padding: 12,
                display: "flex",
                flexDirection: "column",
                gap: 12,
                overflowY: "auto",
                minHeight: 0,
                flex: 1,
              }}
            >
              {clinicalUpdates.map((u) => (
                <div
                  key={u.id}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 12,
                    padding: 10,
                    background: "#f8fafc",
                    borderRadius: 10,
                  }}
                >
                  <img
                    src={u.thumb}
                    alt={u.title}
                    style={{ width: 36, height: 36, borderRadius: 999, objectFit: "cover" }}
                  />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 700, color: "#111827", fontSize: 14 }}>{u.title}</div>
                    <div style={{ fontSize: 12, color: "#64748b" }}>{u.author}</div>
                  </div>
                  <button
                    style={{
                      border: "none",
                      background: u.badge === "New" ? "#f59e0b" : "#e2e8f0",
                      color: u.badge === "New" ? "white" : "#334155",
                      fontWeight: 800,
                      padding: "8px 12px",
                      borderRadius: 10,
                      cursor: "pointer",
                    }}
                  >
                    {u.badge}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right column */}
        <div style={{ display: "grid", gap: 24, gridTemplateRows: "1fr 1fr", minHeight: 0 }}>
          {/* Appointments */}
          <div
            style={{
              background: "white",
              borderRadius: 14,
              boxShadow: "0 1px 3px rgba(0,0,0,.08)",
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
              height: "100%",
              minHeight: 0,
            }}
          >
            <div
              style={{
                padding: "12px 16px",
                borderBottom: "1px solid #e5e7eb",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              <div>
                <button
                  onClick={() => setApptTab("new")}
                  style={{
                    padding: "8px 10px",
                    border: "none",
                    background: "transparent",
                    color: apptTab === "new" ? "#ea580c" : "#64748b",
                    borderBottom: apptTab === "new" ? "2px solid #ea580c" : "2px solid transparent",
                    fontWeight: 800,
                    cursor: "pointer",
                    marginRight: 8,
                  }}
                >
                  NEW APPOINTMENTS
                </button>
                <button
                  onClick={() => setApptTab("completed")}
                  style={{
                    padding: "8px 10px",
                    border: "none",
                    background: "transparent",
                    color: apptTab === "completed" ? "#ea580c" : "#64748b",
                    borderBottom: apptTab === "completed" ? "2px solid #ea580c" : "2px solid transparent",
                    fontWeight: 800,
                    cursor: "pointer",
                  }}
                >
                  COMPLETED APPOINTMENTS
                </button>
              </div>
              <button
                style={{
                  border: "none",
                  background: "transparent",
                  color: "#ea580c",
                  cursor: "pointer",
                  padding: 6,
                  borderRadius: 8,
                }}
              >
                <Maximize2 size={16} />
              </button>
            </div>

            <div style={{ flex: 1, minHeight: 0, overflowY: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead style={{ background: "#f9fafb", position: "sticky", top: 0, zIndex: 1 }}>
                  <tr>
                    {["Time", "Date", "Patient Name", "Doctor"].map((h) => (
                      <th
                        key={h}
                        style={{
                          textAlign: "left",
                          padding: "12px 16px",
                          color: "#111827",
                          fontWeight: 800,
                          fontSize: 12,
                          borderBottom: "1px solid #e5e7eb",
                          background: "#f9fafb",
                        }}
                      >
                        {h} <span style={{ color: "#cbd5e1" }}>▾</span>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((r, i) => (
                    <tr
                      key={r.id}
                      style={{
                        borderTop: i === 0 ? "none" : "1px solid #f1f5f9",
                        transition: "background-color .2s",
                      }}
                      onMouseEnter={(e) =>
                        ((e.currentTarget as HTMLTableRowElement).style.backgroundColor = "#fafafa")
                      }
                      onMouseLeave={(e) =>
                        ((e.currentTarget as HTMLTableRowElement).style.backgroundColor = "transparent")
                      }
                    >
                      <td style={{ padding: "12px 16px", color: "#475569" }}>{r.time}</td>
                      <td style={{ padding: "12px 16px", color: "#475569" }}>{r.date}</td>
                      <td style={{ padding: "12px 16px" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                          <AvatarBadge initials={r.patient.initials} />
                          <span style={{ color: "#111827", fontWeight: 700, fontSize: 14 }}>{r.patient.name}</span>
                        </div>
                      </td>
                      <td style={{ padding: "12px 16px", color: "#475569" }}>{r.doctor}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Patient Fee */}
          <div
            style={{
              background: "white",
              borderRadius: 14,
              boxShadow: "0 1px 3px rgba(0,0,0,.08)",
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
              height: "100%",
              minHeight: 0,
            }}
          >
            <div
              style={{
                padding: "12px 16px",
                borderBottom: "1px solid #e5e7eb",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              <h3 style={{ margin: 0, color: "#111827", fontSize: 16, fontWeight: 800 }}>Patient Fee</h3>
              <button
                style={{
                  border: "none",
                  background: "transparent",
                  color: "#ea580c",
                  cursor: "pointer",
                }}
              >
                <Maximize2 size={16} />
              </button>
            </div>

            <div
              style={{
                padding: 12,
                display: "flex",
                flexDirection: "column",
                gap: 12,
                overflowY: "auto",
                minHeight: 0,
                flex: 1,
              }}
            >
              {feeItems.map((p) => (
                <div
                  key={p.id}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 12,
                    padding: 10,
                    background: "#f8fafc",
                    borderRadius: 10,
                  }}
                >
                  <AvatarBadge initials={p.initials} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 800, color: "#111827", fontSize: 14 }}>{p.name}</div>
                    <div style={{ fontSize: 12, color: "#f97316", fontWeight: 700 }}>{p.status}</div>
                  </div>
                  <button
                    style={{
                      border: "none",
                      background: "#f59e0b",
                      color: "white",
                      fontWeight: 800,
                      padding: "8px 12px",
                      borderRadius: 10,
                      cursor: "pointer",
                    }}
                    onClick={() => alert(`Requested fee from ${p.name}`)}
                  >
                    Request Fee
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div style={{ textAlign: "center", color: "#cbd5e1", fontSize: 12, paddingBottom: 16 }}>
        © 2025 Medigator. All rights reserved.
      </div>
    </main>
  );
};

export default DoctorDashboard;
