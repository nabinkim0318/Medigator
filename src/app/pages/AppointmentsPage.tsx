"use client";

import React, { useEffect, useState } from "react";
import { Search, Calendar, Plus, Maximize2, X } from "lucide-react";

type Gender = "Male" | "Female";

const AvatarBadge: React.FC<{ initials: string; size?: number }> = ({
  initials,
  size = 32,
}) => (
  <div
    style={{
      width: size,
      height: size,
      borderRadius: "9999px",
      background: "#cbd5e1",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      color: "#334155",
      fontWeight: 600,
      fontSize: 12,
    }}
  >
    {initials}
  </div>
);

const TabButton: React.FC<{
  active?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}> = ({ active, onClick, children }) => (
  <button
    onClick={onClick}
    style={{
      padding: "16px 18px",
      border: 0,
      background: "transparent",
      cursor: "pointer",
      fontWeight: 600,
      color: active ? "#ea580c" : "#374151",
      borderBottomWidth: 2,
      borderBottomStyle: "solid",
      borderBottomColor: active ? "#ea580c" : "transparent",
    }}
  >
    {children}
  </button>
);

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8082";

interface Appointment {
  token: string;
  key: string;
  appointmentData: any;
  createdAt: string;
}

interface PatientProfile {
  token: string;
  name: string;
}

const AppointmentsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"new" | "completed">("new");
  const [search, setSearch] = useState("");
  const [dateFilter, setDateFilter] = useState("");
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [tokenMap, setTokenMap] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch appointments
  useEffect(() => {
  Promise.all([
    fetch(`${API_BASE}/api/v1/patient/appointment`).then((res) => res.json()),
    fetch(`${API_BASE}/api/v1/patient/profile`).then((res) => res.json()),
  ])
    .then(([apptData, profileData]) => {
      setAppointments(apptData.appointments || []);

      // Store full profile object keyed by token
      const map: Record<string, any> = {};
      (profileData.profiles || []).forEach((p: any) => {
        map[p.token] = p.profile || {};
      });
      setTokenMap(map);

      setLoading(false);
    })
    .catch((err) => {
      console.error(err);
      setError("Failed to load appointments or profiles");
      setLoading(false);
    });
  }, []);

  if (loading) return <p>Loading appointments…</p>;
  if (error) return <p className="text-red-500">{error}</p>;
  const filteredAppointments = appointments.filter((r) => {
  const appt = r.appointmentData || {};
  const profile = tokenMap[r.token] || {};
  const displayName = appt.patient?.name || profile.name || "";

  // Check search term
  const matchesSearch = displayName.toLowerCase().includes(search.toLowerCase());

  // Check date filter
  let matchesDate = true;
  if (dateFilter && r.createdAt) {
    const d = new Date(r.createdAt);
    const dateStr = d.toLocaleDateString("en-GB");
    matchesDate = dateStr.includes(dateFilter);
  }

  return matchesSearch && matchesDate;
});

  return (
    <div
      style={{
        height: "100%",
        minHeight: 0,
        display: "flex",
        flexDirection: "column",
        background: "#f8fafc",
      }}
    >
      {/* Top bar */}
      <div
        style={{
          padding: "18px 28px",
          background: "linear-gradient(180deg,#fff7ed, #fff)",
          borderBottom: "1px solid #f1f5f9",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <h1 style={{ margin: 0, fontSize: 28, fontWeight: 700, color: "#374151" }}>Appointments</h1>
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div title="Notifications" style={{ width: 36, height: 36, borderRadius: 18, background: "white", boxShadow: "0 1px 2px rgba(0,0,0,.05)", position: "relative" }}>
              <div style={{ width: 8, height: 8, borderRadius: 8, background: "#ef4444", position: "absolute", right: 8, top: 8 }} />
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <div
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: 999,
                  backgroundColor: "#f59e0b",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "white",
                  fontSize: "16px",
                  fontWeight: "600",
                }}
              >
                Dr
              </div>
              <div>
                <div style={{ fontWeight: 700, color: "#334155" }}>Jonitha Cathrine</div>
                <div style={{ fontSize: 12, color: "#94a3b8" }}>Doctor</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <section style={{ padding: 24, display: "flex", flexDirection: "column", flex: 1, minHeight: 0, overflow: "hidden" }}>
        <div style={{ background: "white", borderRadius: 14, boxShadow: "0 1px 3px rgba(0,0,0,.08)", overflow: "hidden", display: "flex", flexDirection: "column", flex: 1, minHeight: 0 }}>
          {/* Tabs & Actions */}
          <div style={{ borderBottom: "1px solid #e5e7eb", padding: "0 18px" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12, flexWrap: "wrap", minWidth: 0 }}>
              <div style={{ minWidth: 0 }}>
                <TabButton active={activeTab === "new"} onClick={() => setActiveTab("new")}>NEW APPOINTMENTS</TabButton>
                <TabButton active={activeTab === "completed"} onClick={() => setActiveTab("completed")}>COMPLETED APPOINTMENTS</TabButton>
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: 10, minWidth: 0 }}>
                <button style={{ display: "flex", alignItems: "center", gap: 8, background: "#f59e0b", color: "white", border: "none", padding: "10px 14px", borderRadius: 10, fontWeight: 700, cursor: "pointer" }}>
                  <Plus style={{ width: 18, height: 18 }} /> New Appointment
                </button>
                <button title="Expand" style={{ border: "none", background: "transparent", padding: 8, borderRadius: 8, color: "#ea580c", cursor: "pointer" }}>
                  <Maximize2 style={{ width: 18, height: 18 }} />
                </button>
              </div>
            </div>

            {/* Filters */}
            <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 0 18px 0" }}>
              <div style={{ position: "relative", width: 260 }}>
                <Search style={{ width: 18, height: 18, color: "#9ca3af", position: "absolute", top: "50%", left: 14, transform: "translateY(-50%)" }} />
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search"
                  style={{ width: "100%", padding: "10px 12px 10px 40px", background: "#fff7ed", border: "1px solid #fde68a", borderRadius: 24, outline: "none", fontSize: 14, color: "#334155" }}
                />
              </div>

              <div>
                <button
                  onClick={() => {
                    const v = prompt("Filter by Date (DD/MM/YYYY) contains…", dateFilter || "");
                    if (v !== null) setDateFilter(v);
                  }}
                  style={{ display: "flex", alignItems: "center", gap: 8, padding: "10px 14px", borderRadius: 24, border: "1px solid #f59e0b", background: "white", color: "#334155", fontWeight: 600, cursor: "pointer" }}
                >
                  Filter by Date
                  <Calendar style={{ width: 16, height: 16, color: "#f59e0b" }} />
                </button>
              </div>
            </div>
          </div>

          {/* Table */}
          <div style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>
            <div style={{ overflowY: "auto", flex: 1 }}>
              <table style={{ width: "100%", borderCollapse: "collapse", tableLayout: "fixed" }}>
                <thead style={{ background: "#f8fafc", position: "sticky", top: 0, zIndex: 1 }}>
                  <tr style={{ color: "#1f2937" }}>
                    {["Time", "Date", "Patient Name", "Patient Age", "Doctor", "User Action"].map((h) => (
                      <th key={h} style={{ textAlign: "left", padding: "14px 20px", fontWeight: 700, fontSize: 13, borderBottom: "1px solid #e5e7eb", background: "#f8fafc" }}>
                        {h} <span style={{ color: "#cbd5e1" }}>▾</span>
                      </th>
                    ))}
                  </tr>
                </thead>

                <tbody>
                  {filteredAppointments.map((r, idx) => {
                    const appt = r.appointmentData || {};
                    const patient = appt.patient || {};

                    // parse date & time from createdBy
                    let dateStr = "—";
                    let timeStr = "—";
                    if (r.createdAt) {
                      const d = new Date(r.createdAt);
                      dateStr = d.toLocaleDateString("en-GB");
                      timeStr = d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
                    }

                    // token → name mapping
                    const profile = tokenMap[r.token] || {};
                    const displayName = appt.patient?.name || profile.name || r.token;
                    const initials =
                      appt.patient?.initials ||
                      displayName
                        .split(" ")
                        .map((n) => n[0])
                        .join("")
                        .slice(0, 2)
                        .toUpperCase();
                    const age = appt.patient?.age || profile.age || "—";

                    

                    return (
                      <tr
                        key={r.key}
                        style={{ borderTop: idx === 0 ? "none" : "1px solid #f1f5f9", transition: "background-color .2s" }}
                        onMouseEnter={(e) => ((e.currentTarget as HTMLTableRowElement).style.backgroundColor = "#fafafa")}
                        onMouseLeave={(e) => ((e.currentTarget as HTMLTableRowElement).style.backgroundColor = "transparent")}
                      >
                        <td style={{ padding: "16px 20px", color: "#475569" }}>{timeStr}</td>
                        <td style={{ padding: "16px 20px", color: "#475569" }}>{dateStr}</td>
                        <td style={{ padding: "16px 20px" }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                            <AvatarBadge initials={initials} />
                            <span style={{ color: "#1f2937", fontWeight: 600 }}>{displayName}</span>
                          </div>
                        </td>
                        <td style={{ padding: "16px 20px", color: "#475569" }}>{age || "—"}</td>
                        <td style={{ padding: "16px 20px", color: "#475569" }}>{appt.doctor || "Dr. John"}</td>
                        <td style={{ padding: "16px 20px" }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                            <button
                              style={{ background: "transparent", border: 0, color: "#ea580c", fontWeight: 700, cursor: "pointer" }}
                              onClick={() => alert(`Reschedule ${displayName}`)}
                            >
                              Reschedule
                            </button>
                            <button
                              title="Cancel"
                              onClick={() => confirm("Cancel this appointment?") &&
                                alert(`Canceled ${patient.name || r.key}`)
                              }
                              style={{
                                width: 28,
                                height: 28,
                                borderRadius: 8,
                                border: 0,
                                background: "#fde2e2",
                                color: "#e11d48",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                cursor: "pointer",
                              }}
                            >
                              <X style={{ width: 14, height: 14 }} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}

                  {appointments.length === 0 && (
                    <tr>
                      <td colSpan={6} style={{ padding: 28, textAlign: "center", color: "#94a3b8" }}>
                        No appointments match your filters.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div
              style={{
                padding: "16px 20px",
                borderTop: "1px solid #e5e7eb",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              <span style={{ color: "#94a3b8", fontSize: 14 }}>Previous</span>
              <div style={{ display: "flex", gap: 8 }}>
                {["1", "2", "3", "4"].map((p, i) => (
                  <button
                    key={p}
                    style={{
                      width: 30,
                      height: 30,
                      borderRadius: 8,
                      border: 0,
                      cursor: "pointer",
                      background: i === 0 ? "#f59e0b" : "transparent",
                      color: i === 0 ? "white" : "#64748b",
                      fontWeight: 700,
                    }}
                  >
                    {p}
                  </button>
                ))}
              </div>
              <span style={{ color: "#94a3b8", fontSize: 14 }}>Next</span>
            </div>
          </div>
        </div>

        {/* Footer lives outside the card; section contains overflow so it won't push content off-screen */}
        <div style={{ textAlign: "center", color: "#cbd5e1", fontSize: 12, marginTop: 12 }}>
          © 2025 Medigator. All rights reserved.
        </div>
      </section>
    </div>
  );
};

export default AppointmentsPage;
