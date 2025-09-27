"use client";

import React, { useMemo, useState } from "react";
import {
  Bell,
  Maximize2,
  ChevronDown,
  Users,
  ClipboardList,
  Pill,
  FlaskConical,
} from "lucide-react";

type Gender = "Male" | "Female";

interface AppointmentRow {
  id: string;
  time: string;
  date: string; // DD/MM/YYYY
  patient: { name: string; initials: string; gender: Gender };
  doctor: string;
}

interface ClinicalUpdate {
  id: string;
  title: string;
  author: string;
  thumb: string;
  badge?: "New" | "Read";
}

interface PatientFeeItem {
  id: string;
  name: string;
  status: "Doctor fee pending" | "Doctor fee pending (reminder)";
  initials: string;
}

const appointments: AppointmentRow[] = [
  { id: "a1", time: "9:30 AM", date: "05/12/2022", patient: { name: "Elizabeth Polson", initials: "JD", gender: "Female" }, doctor: "Dr. John" },
  { id: "a2", time: "9:30 AM", date: "05/12/2022", patient: { name: "John David", initials: "JD", gender: "Male" }, doctor: "Dr. Joel" },
  { id: "a3", time: "10:30 AM", date: "05/12/2022", patient: { name: "Krishtav Rajan", initials: "KR", gender: "Male" }, doctor: "Dr. Joel" },
  { id: "a4", time: "11:00 AM", date: "05/12/2022", patient: { name: "Sumanth Tinson", initials: "JD", gender: "Male" }, doctor: "Dr. John" },
  { id: "a5", time: "11:30 AM", date: "05/12/2022", patient: { name: "EG Subramani", initials: "JD", gender: "Male" }, doctor: "Dr. John" },
];

const clinicalUpdates: ClinicalUpdate[] = [
  {
    id: "c1",
    title: "T2DM: New 130/80 BP Goal",
    author: "By Dr. K. Lee",
    thumb: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&h=80&fit=crop&crop=faces",
    badge: "New",
  },
  {
    id: "c2",
    title: "SGLT2i for Non-Diabetic CKD",
    author: "By Dr. J. Chen",
    thumb: "https://images.unsplash.com/photo-1541534401786-2077eed87a72?w=80&h=80&fit=crop&crop=faces",
    badge: "New",
  },
  {
    id: "c3",
    title: "Updated PCP Anxiety Screening",
    author: "By Dr. M. Rodriguez",
    thumb: "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=80&h=80&fit=crop&crop=faces",
    badge: "New",
  },
  {
    id: "c4",
    title: "New Oral MDD Drug",
    author: "—",
    thumb: "https://images.unsplash.com/photo-1606207554193-62c61d9bf34a?w=80&h=80&fit=crop&crop=faces",
    badge: "Read",
  },
];

const feeItems: PatientFeeItem[] = [
  { id: "f1", name: "EG Subramani", status: "Doctor fee pending", initials: "KR" },
  { id: "f2", name: "Elizabeth Polson", status: "Doctor fee pending", initials: "KR" },
  { id: "f3", name: "Sumanth Tinson", status: "Doctor fee pending", initials: "KR" },
  { id: "f4", name: "Krishtav Rajan", status: "Doctor fee pending", initials: "KR" },
];

const StatTile: React.FC<{
  icon: React.ReactNode;
  value: number | string;
  label: string;
}> = ({ icon, value, label }) => (
  <div
    style={{
      background: "white",
      borderRadius: 12,
      boxShadow: "0 1px 3px rgba(0,0,0,.08)",
      padding: 18,
      display: "flex",
      alignItems: "center",
      gap: 14,
      minHeight: 88,
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

// Simple SVG donut chart
const Donut: React.FC<{
  segments: { pct: number; label: string; color: string }[];
  size?: number;
  thickness?: number;
}> = ({ segments, size = 220, thickness = 38 }) => {
  const R = size / 2;
  const r = R - thickness;
  let cum = 0;
  const c = 2 * Math.PI * r;

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <g transform={`translate(${R}, ${R}) rotate(-90)`}>
        {segments.map((s, i) => {
          const dash = (s.pct / 100) * c;
          const gap = c - dash;
          const strokeDasharray = `${dash} ${gap}`;
          const rotate = (cum / 100) * 360;
          cum += s.pct;
          return (
            <circle
              key={i}
              r={r}
              cx={0}
              cy={0}
              fill="transparent"
              stroke={s.color}
              strokeWidth={thickness}
              strokeDasharray={strokeDasharray}
              transform={`rotate(${rotate})`}
              strokeLinecap="butt"
            />
          );
        })}
      </g>
      <circle cx={R} cy={R} r={r - 10} fill="white" />
      <text x={R} y={R - 4} textAnchor="middle" fontWeight={800} fontSize={22} fill="#0f172a">
        55%
      </text>
      <text x={R} y={R + 16} textAnchor="middle" fontSize={12} fill="#64748b">
        Hypertension
      </text>
    </svg>
  );
};

const DashboardPage: React.FC = () => {
  const [apptTab] = useState<"new" | "completed">("new");
  const morbiditySegments = useMemo(
    () => [
      { pct: 55, label: "Hypertension (I10)", color: "#f97316" },
      { pct: 25, label: "URI (J06/J20)", color: "#8b5cf6" },
      { pct: 12, label: "Diabetes (E11)", color: "#22c55e" },
      { pct: 8, label: "Others", color: "#f59e0b" },
    ],
    []
  );

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#fef9f5" }}>
      {/* Sidebar */}
      <aside
        style={{
          width: 256,
          background: "white",
          borderRight: "1px solid #f1f5f9",
          display: "flex",
          flexDirection: "column",
          position: "relative",
        }}
      >
        {/* Brand */}
        <div style={{ padding: 24, borderBottom: "1px solid #f1f5f9" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div
              style={{
                width: 36,
                height: 36,
                background: "#f59e0b",
                color: "white",
                borderRadius: 10,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 900,
                fontSize: 18,
              }}
            >
              +
            </div>
            <div style={{ color: "#ef6c00", fontWeight: 800, fontSize: 18 }}>Medigator</div>
          </div>
        </div>

        {[
          { icon: "🧭", label: "Dashboard", active: true },
          { icon: "👥", label: "Patients" },
          { icon: "📝", label: "Appointments" },
          { icon: "👨‍⚕️", label: "Doctors" },
          { icon: "💬", label: "Messages" },
          { icon: "🏥", label: "Clinical Updates" },
          { icon: "⚙️", label: "Settings" },
        ].map((item) => (
          <div
            key={item.label}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              padding: "12px 16px",
              color: item.active ? "#ea580c" : "#475569",
              background: item.active ? "#fff7ed" : "transparent",
              borderRight: item.active ? "3px solid #ea580c" : "3px solid transparent",
              cursor: "pointer",
            }}
          >
            <span style={{ fontSize: 18 }}>{item.icon}</span>
            <span style={{ fontWeight: 700 }}>{item.label}</span>
          </div>
        ))}

        <div style={{ marginTop: "auto", padding: 16 }}>
          <button
            style={{
              width: "100%",
              display: "flex",
              alignItems: "center",
              gap: 10,
              padding: 12,
              borderRadius: 10,
              border: "none",
              background: "transparent",
              color: "#64748b",
              cursor: "pointer",
            }}
          >
            <span>🚪</span>
            <span style={{ fontWeight: 700 }}>Logout</span>
          </button>
          <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 8 }}>
            Demo only — Not diagnostic • No PHI.
          </div>
        </div>
      </aside>

      {/* Main */}
      <main style={{ flex: 1, display: "flex", flexDirection: "column" }}>
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
        <div style={{ padding: 24, display: "grid", gridTemplateColumns: "1.2fr 1.8fr", gap: 24 }}>
          {/* Left column */}
          <div style={{ display: "grid", gap: 24 }}>
            {/* Activity Overview (2x2 grid) */}
            <div
              style={{
                background: "white",
                borderRadius: 14,
                boxShadow: "0 1px 3px rgba(0,0,0,.08)",
                padding: 18,
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
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

              {/* 2 x 2 grid */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(2, 1fr)",
                  gap: 14,
                  marginTop: 14,
                }}
              >
                <StatTile icon={<ClipboardList size={22} />} value={100} label="Appointments" />
                <StatTile icon={<Users size={22} />} value={50} label="New Patients" />
                <StatTile icon={<Pill size={22} />} value={500} label="Medicines Sold" />
                <StatTile icon={<FlaskConical size={22} />} value={100} label="Lab Tests" />
              </div>
            </div>

            {/* Clinical Updates */}
            <div
              style={{
                background: "white",
                borderRadius: 14,
                boxShadow: "0 1px 3px rgba(0,0,0,.08)",
                overflow: "hidden",
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

              <div style={{ padding: 12, display: "flex", flexDirection: "column", gap: 12 }}>
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
          <div style={{ display: "grid", gap: 24 }}>
            {/* New Appointments table */}
            <div
              style={{
                background: "white",
                borderRadius: 14,
                boxShadow: "0 1px 3px rgba(0,0,0,.08)",
                overflow: "hidden",
                display: "flex",
                flexDirection: "column",
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
                    style={{
                      padding: "8px 10px",
                      border: "none",
                      background: "transparent",
                      color: "#ea580c",
                      borderBottom: "2px solid #ea580c",
                      fontWeight: 800,
                      cursor: "pointer",
                    }}
                  >
                    NEW APPOINTMENTS
                  </button>
                  <button
                    style={{
                      padding: "8px 10px",
                      border: "none",
                      background: "transparent",
                      color: "#64748b",
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

              <div style={{ maxHeight: 270, overflowY: "auto" }}>
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
                    {appointments.map((r, i) => (
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
                            <span style={{ color: "#111827", fontWeight: 700, fontSize: 14 }}>
                              {r.patient.name}
                            </span>
                          </div>
                        </td>
                        <td style={{ padding: "12px 16px", color: "#475569" }}>{r.doctor}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Patient Morbidity */}
            <div
              style={{
                background: "white",
                borderRadius: 14,
                boxShadow: "0 1px 3px rgba(0,0,0,.08)",
                padding: 14,
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: 10,
                alignItems: "center",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gridColumn: "1 / -1",
                }}
              >
                <h3 style={{ margin: 0, color: "#111827", fontSize: 16, fontWeight: 800 }}>
                  Patient Morbidity
                </h3>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <button
                    style={{
                      border: "none",
                      background: "transparent",
                      display: "flex",
                      alignItems: "center",
                      gap: 6,
                      color: "#64748b",
                      fontWeight: 700,
                      cursor: "pointer",
                    }}
                  >
                    Weekly <ChevronDown size={16} />
                  </button>
                  <button
                    style={{
                      border: "none",
                      background: "transparent",
                      color: "#ea580c",
                      cursor: "pointer",
                    }}
                    title="Expand"
                  >
                    <Maximize2 size={16} />
                  </button>
                </div>
              </div>

              <div style={{ display: "flex", justifyContent: "center" }}>
                <Donut segments={morbiditySegments} />
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {morbiditySegments.map((s, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span
                      style={{
                        width: 10,
                        height: 10,
                        background: s.color,
                        borderRadius: 999,
                        display: "inline-block",
                      }}
                    />
                    <span style={{ color: "#334155", fontWeight: 700, fontSize: 13 }}>{s.label}</span>
                    <span style={{ marginLeft: "auto", color: "#64748b", fontWeight: 700 }}>{s.pct}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Patient Fee */}
            <div
              style={{
                background: "white",
                borderRadius: 14,
                boxShadow: "0 1px 3px rgba(0,0,0,.08)",
                overflow: "hidden",
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

              <div style={{ padding: 12, display: "flex", flexDirection: "column", gap: 12 }}>
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
    </div>
  );
};

export default DashboardPage;
