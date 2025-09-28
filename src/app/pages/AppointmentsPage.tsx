"use client";

import React, { useMemo, useState } from "react";
import { Search, Calendar, Plus, Maximize2, X } from "lucide-react";

type Gender = "Male" | "Female";

interface PatientRow {
  id: string;
  time: string;
  date: string; // DD/MM/YYYY
  patient: {
    name: string;
    age: number;
    gender: Gender;
    initials: string;
    avatar?: string;
  };
  doctor: string;
}

const data: PatientRow[] = [
  { id: "a1", time: "9:30 AM", date: "05/12/2022", patient: { name: "Elizabeth Polson", age: 32, gender: "Female", initials: "EP" }, doctor: "Dr. John" },
  { id: "a2", time: "9:30 AM", date: "05/12/2022", patient: { name: "John David", age: 28, gender: "Male", initials: "JD" }, doctor: "Dr. Joel" },
  { id: "a3", time: "10:30 AM", date: "05/12/2022", patient: { name: "Krishtav Rajan", age: 24, gender: "Male", initials: "KR" }, doctor: "Dr. Joel" },
  { id: "a4", time: "11:00 AM", date: "05/12/2022", patient: { name: "Sumanth Tinson", age: 26, gender: "Male", initials: "KR" }, doctor: "Dr. John" },
  { id: "a5", time: "11:30 AM", date: "05/12/2022", patient: { name: "EG Subramani", age: 77, gender: "Male", initials: "KR" }, doctor: "Dr. John" },
  { id: "a6", time: "11:00 AM", date: "05/12/2022", patient: { name: "Ranjan Maari", age: 77, gender: "Male", initials: "KR" }, doctor: "Dr. John" },
  { id: "a7", time: "11:00 AM", date: "05/12/2022", patient: { name: "Phillipie Gopal", age: 55, gender: "Male", initials: "KR" }, doctor: "Dr. John" },
];

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

const AppointmentsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"new" | "completed">("new");
  const [search, setSearch] = useState("");
  const [dateFilter, setDateFilter] = useState("");

  const rows = useMemo(() => {
    let r = data;
    if (search.trim()) {
      const q = search.toLowerCase();
      r = r.filter(
        (x) =>
          x.patient.name.toLowerCase().includes(q) ||
          x.doctor.toLowerCase().includes(q) ||
          x.time.toLowerCase().includes(q),
      );
    }
    if (dateFilter.trim()) {
      r = r.filter((x) => x.date.includes(dateFilter));
    }
    return r;
  }, [search, dateFilter]);

  return (
    // Let height come from the parent shell; contain overflow inside.
    <div style={{ height: "100%", minHeight: 0, display: "flex", flexDirection: "column", background: "#f8fafc" }}>
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
            <div
              title="Notifications"
              style={{
                width: 36,
                height: 36,
                borderRadius: 18,
                background: "white",
                boxShadow: "0 1px 2px rgba(0,0,0,.05)",
                position: "relative",
                overflow: "hidden",
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
                  overflow: "hidden",
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
                <div style={{ fontWeight: 700, color: "#334155" }}>Jonitha Cathrine</div>
                <div style={{ fontSize: 12, color: "#94a3b8" }}>Doctor</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content area (owns the remaining height). Hide outer overflow so only rows scroll. */}
      <section
        style={{
          padding: 24,
          display: "flex",
          flexDirection: "column",
          flex: 1,
          minHeight: 0,
          overflow: "hidden", // <-- important
        }}
      >
        <div
          style={{
            background: "white",
            borderRadius: 14,
            boxShadow: "0 1px 3px rgba(0,0,0,.08)",
            overflow: "hidden",
            display: "flex",
            flexDirection: "column",
            flex: 1,
            minHeight: 0,
          }}
        >
          {/* Tabs & Actions */}
          <div style={{ borderBottom: "1px solid #e5e7eb", padding: "0 18px" }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 12,
                flexWrap: "wrap", // allow wrap on small widths
                minWidth: 0,
              }}
            >
              <div style={{ minWidth: 0 }}>
                <TabButton active={activeTab === "new"} onClick={() => setActiveTab("new")}>
                  NEW APPOINTMENTS
                </TabButton>
                <TabButton active={activeTab === "completed"} onClick={() => setActiveTab("completed")}>
                  COMPLETED APPOINTMENTS
                </TabButton>
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: 10, minWidth: 0 }}>
                <button
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    background: "#f59e0b",
                    color: "white",
                    border: "none",
                    padding: "10px 14px",
                    borderRadius: 10,
                    fontWeight: 700,
                    cursor: "pointer",
                  }}
                >
                  <Plus style={{ width: 18, height: 18 }} />
                  New Appointment
                </button>

                <button
                  title="Expand"
                  style={{
                    border: "none",
                    background: "transparent",
                    padding: 8,
                    borderRadius: 8,
                    color: "#ea580c",
                    cursor: "pointer",
                  }}
                >
                  <Maximize2 style={{ width: 18, height: 18 }} />
                </button>
              </div>
            </div>

            {/* Filters */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                padding: "12px 0 18px 0",
              }}
            >
              <div style={{ position: "relative", width: 260 }}>
                <Search
                  style={{
                    width: 18,
                    height: 18,
                    color: "#9ca3af",
                    position: "absolute",
                    top: "50%",
                    left: 14,
                    transform: "translateY(-50%)",
                  }}
                />
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search"
                  style={{
                    width: "100%",
                    padding: "10px 12px 10px 40px",
                    background: "#fff7ed",
                    border: "1px solid #fde68a",
                    borderRadius: 24,
                    outline: "none",
                    fontSize: 14,
                    color: "#334155",
                  }}
                />
              </div>

              <div>
                <button
                  onClick={() => {
                    const v = prompt("Filter by Date (DD/MM/YYYY) contains…", dateFilter || "05/12/2022");
                    if (v !== null) setDateFilter(v);
                  }}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    padding: "10px 14px",
                    borderRadius: 24,
                    border: "1px solid #f59e0b",
                    background: "white",
                    color: "#334155",
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                >
                  Filter by Date
                  <Calendar style={{ width: 16, height: 16, color: "#f59e0b" }} />
                </button>
              </div>
            </div>
          </div>

          {/* Rows scroller */}
          <div style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>
            <div style={{ overflowY: "auto", flex: 1 }}>
              <table style={{ width: "100%", borderCollapse: "collapse", tableLayout: "fixed" }}>
                <thead style={{ background: "#f8fafc", position: "sticky", top: 0, zIndex: 1 }}>
                  <tr style={{ color: "#1f2937" }}>
                    {["Time", "Date", "Patient Name", "Patient Age", "Doctor", "User Action"].map((h) => (
                      <th
                        key={h}
                        style={{
                          textAlign: "left",
                          padding: "14px 20px",
                          fontWeight: 700,
                          fontSize: 13,
                          borderBottom: "1px solid #e5e7eb",
                          background: "#f8fafc",
                        }}
                      >
                        {h} <span style={{ color: "#cbd5e1" }}>▾</span>
                      </th>
                    ))}
                  </tr>
                </thead>

                <tbody>
                  {rows.map((r, idx) => (
                    <tr
                      key={r.id}
                      style={{
                        borderTop: idx === 0 ? "none" : "1px solid #f1f5f9",
                        transition: "background-color .2s",
                      }}
                      onMouseEnter={(e) =>
                        ((e.currentTarget as HTMLTableRowElement).style.backgroundColor = "#fafafa")
                      }
                      onMouseLeave={(e) =>
                        ((e.currentTarget as HTMLTableRowElement).style.backgroundColor = "transparent")
                      }
                    >
                      <td style={{ padding: "16px 20px", color: "#475569" }}>{r.time}</td>
                      <td style={{ padding: "16px 20px", color: "#475569" }}>{r.date}</td>
                      <td style={{ padding: "16px 20px" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                          <AvatarBadge initials={r.patient.initials} />
                          <span style={{ color: "#1f2937", fontWeight: 600 }}>{r.patient.name}</span>
                        </div>
                      </td>
                      <td style={{ padding: "16px 20px", color: "#475569" }}>{r.patient.age}</td>
                      <td style={{ padding: "16px 20px", color: "#475569" }}>{r.doctor}</td>
                      <td style={{ padding: "16px 20px" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                          <button
                            style={{
                              background: "transparent",
                              border: 0,
                              color: "#ea580c",
                              fontWeight: 700,
                              cursor: "pointer",
                            }}
                            onClick={() => alert(`Reschedule ${r.patient.name}`)}
                          >
                            Reschedule
                          </button>
                          <button
                            title="Cancel"
                            onClick={() => confirm("Cancel this appointment?") && alert("Canceled")}
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
                  ))}

                  {rows.length === 0 && (
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
