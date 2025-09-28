"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Search, Calendar, Bell, Plus, Edit, X, Eye } from "lucide-react";
import PatientInfoPopup, { Patient } from "./PatientInfoPopup";
import { useToast } from "../components/ErrorToast";

const DoctorPatientView: React.FC = () => {
  const router = useRouter();
  const { showToast, ToastContainer } = useToast();
  const [searchTerm, setSearchTerm] = useState("");
  const [filterDate, setFilterDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // popup state
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);

  const [patients, setPatients] = useState<Patient[]>([]);
  const [patientSummaries, setPatientSummaries] = useState<{
    [key: string]: any;
  }>({});
  const [currentPage, setCurrentPage] = useState(1);
  const [patientsPerPage] = useState(10);

  // Calculate pagination
  const totalPages = Math.ceil(patients.length / patientsPerPage);
  const startIndex = (currentPage - 1) * patientsPerPage;
  const endIndex = startIndex + patientsPerPage;
  const currentPatients = patients.slice(startIndex, endIndex);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  useEffect(() => {
    const API_BASE =
      (process.env.NEXT_PUBLIC_API_URL as string) || "http://localhost:8082";

    const fetchPatients = () => {
      setLoading(true);
      fetch(`${API_BASE}/api/v1/patient/profile`)
        .then(async (res) => {
          if (!res.ok) {
            const t = await res.text();
            throw new Error(`fetch failed: ${res.status} ${t}`);
          }
          return res.json();
        })
        .then((data) => {
          // data.profiles: [{ token, profile: { name, age, gender, ... } }]
          if (Array.isArray(data.profiles)) {
            const mapped: Patient[] = data.profiles
              .map((p: any, idx: number) => {
                if (!p.profile) return null;
                const prof = p.profile;
                const initials = prof.name
                  ? prof.name
                      .split(" ")
                      .map((s: string) => s[0])
                      .join("")
                      .slice(0, 2)
                      .toUpperCase()
                  : "??";
                return {
                  id: p.token || String(idx + 1),
                  name: prof.name || "Unknown",
                  age: Number(prof.age) || 0,
                  gender: prof.gender || (prof.sex as any) || "Male",
                  bloodGroup: prof.bloodGroup || "",
                  phone: prof.phone || "",
                  email: prof.email || "",
                  avatar: prof.avatar || "",
                  initials,
                  token: p.token, // Add token field
                  ai_summary_status: p.ai_summary_status || "pending", // Add AI summary status
                } as Patient;
              })
              .filter(Boolean) as Patient[];
            setPatients(mapped);
          } else {
            setPatients([]);
          }
          setLoading(false);
        })
        .catch((err) => {
          setError(err.message);
          setLoading(false);
        });
    };

    // Initial data load
    fetchPatients();

    // Auto refresh: update data every 3 seconds
    const interval = setInterval(fetchPatients, 3000);

    return () => clearInterval(interval);
  }, []);

  const sidebarItems = [
    { icon: "📊", label: "Dashboard", active: false },
    { icon: "👥", label: "Patients", active: true },
    { icon: "📅", label: "Appointments", active: false },
    { icon: "👨‍⚕️", label: "Doctors", active: false },
    { icon: "💬", label: "Messages", active: false },
    { icon: "🏥", label: "Clinical Updates", active: false },
    { icon: "⚙️", label: "Settings", active: false },
  ];

  const ActionButton: React.FC<{
    type: "edit" | "delete" | "view";
    onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
  }> = ({ type, onClick }) => {
    const icons = {
      edit: <Edit style={{ width: 16, height: 16 }} />,
      delete: <X style={{ width: 16, height: 16 }} />,
      view: <Eye style={{ width: 16, height: 16 }} />,
    };

    const getButtonStyle = (t: string) => ({
      padding: "6px",
      borderRadius: "8px",
      transition: "all 0.2s",
      border: "1px solid #e5e7eb",
      backgroundColor: "white",
      cursor: "pointer",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      ...(t === "edit" && { color: "#f59e0b" }),
      ...(t === "delete" && { color: "#dc2626" }),
      ...(t === "view" && { color: "#6b7280" }),
    });

    return (
      <button
        type="button"
        aria-label={type}
        style={getButtonStyle(type)}
        onClick={onClick}
        onMouseEnter={(e) => {
          e.currentTarget.style.borderColor = "#d1d5db";
          e.currentTarget.style.backgroundColor = "#f9fafb";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.borderColor = "#e5e7eb";
          e.currentTarget.style.backgroundColor = "white";
        }}
      >
        {icons[type]}
      </button>
    );
  };

  const Avatar: React.FC<{ patient: Patient }> = ({ patient }) => (
    <div
      style={{
        width: "40px",
        height: "40px",
        borderRadius: "50%",
        backgroundColor: "#f59e0b",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: "white",
        fontSize: "14px",
        fontWeight: 600,
      }}
    >
      {patient.initials}
    </div>
  );

  const openPatient = (p: Patient) => {
    setSelectedPatient(p);
    setIsPopupOpen(true);
  };

  const filteredPatients = patients.filter((p) => {
  const matchesName = p.name.toLowerCase().includes(searchTerm.toLowerCase());
  return matchesName;
});


  return (
    <>
      <ToastContainer />
      <div
        style={{
          display: "flex",
          height: "100vh",
          backgroundColor: "#fff7ed",
          width: "100%",
          fontFamily:
            "'Poppins', system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
        }}
      >
        {/* Sidebar */}
        <div
          style={{
            width: 208,
            backgroundColor: "white",
            padding: "24px 0",
            boxShadow: "0 2px 4px rgba(0,0,0,0.05)",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
          }}
        >
          <div>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                padding: "0 24px",
                marginBottom: 24,
                gap: 8,
              }}
            >
              <div
                style={{
                  width: 36,
                  height: 36,
                  backgroundColor: "#f59e0b",
                  borderRadius: 8,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "white",
                  fontWeight: 700,
                }}
              >
                M
              </div>
              <span style={{ fontSize: 18, fontWeight: 700, color: "#f59e0b" }}>
                Medigator
              </span>
            </div>

            <nav>
              {sidebarItems.map((item) => (
                <div
                  key={item.label}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    padding: "12px 24px",
                    color: item.active ? "#f59e0b" : "#6b7280",
                    backgroundColor: item.active
                      ? "rgba(245,158,11,0.08)"
                      : "transparent",
                    borderLeft: item.active
                      ? "3px solid #f59e0b"
                      : "3px solid transparent",
                    fontWeight: item.active ? 600 : 400,
                    cursor: "pointer",
                    transition: "all 0.2s",
                    gap: 12,
                  }}
                  onMouseEnter={(e) => {
                    if (!item.active) {
                      e.currentTarget.style.backgroundColor =
                        "rgba(245,158,11,0.04)";
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!item.active) {
                      e.currentTarget.style.backgroundColor = "transparent";
                    }
                  }}
                >
                  <span>{item.icon}</span>
                  {item.label}
                </div>
              ))}
            </nav>
          </div>

          <div
            style={{
              padding: "12px 24px",
              color: "#4b5563",
              fontSize: 14,
              display: "flex",
              alignItems: "center",
              cursor: "pointer",
            }}
            onClick={() => router.push("/")}
          >
            <span style={{ marginRight: 12 }}>🚪</span>
            Logout
          </div>
        </div>

        {/* Main */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            width: "100%",
            flex: 1,
          }}
        >
          {/* Top bar */}
          <div
            style={{
              padding: "18px 28px",
              background: "linear-gradient(180deg,#fff, #fff7ed)",
              borderBottom: "1px solid #f1f5f9",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              <h1
                style={{
                  margin: 0,
                  fontSize: 28,
                  fontWeight: 700,
                  color: "#374151",
                }}
              >
                Patients
              </h1>
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
                    <div style={{ fontWeight: 700, color: "#334155" }}>
                      Jonitha Cathrine
                    </div>
                    <div style={{ fontSize: 12, color: "#94a3b8" }}>Doctor</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Content */}
          <div
            style={{
              padding: "24px",
              flex: 1,
              display: "flex",
              flexDirection: "column",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                backgroundColor: "white",
                borderRadius: "8px",
                boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
                flex: 1,
                display: "flex",
                flexDirection: "column",
                overflow: "hidden",
              }}
            >
              <div style={{ borderBottom: "1px solid #e5e7eb" }}>
                <button
                  style={{
                    padding: "16px 24px",
                    color: "#f59e0b",
                    borderBottom: "2px solid #f59e0b",
                    fontWeight: 500,
                    backgroundColor: "transparent",
                    border: "none",
                    cursor: "pointer",
                  }}
                >
                  Patient Info
                </button>
              </div>

              {/* Controls */}
              <div
                style={{
                  padding: "24px",
                  borderBottom: "1px solid #e5e7eb",
                  position: "relative",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "16px",
                    }}
                  >
                    <div style={{ position: "relative" }}>
                      <Search
                        style={{
                          width: 18,
                          height: 18,
                          color: "#f59e0b",
                          position: "absolute",
                          left: "12px",
                          top: "50%",
                          transform: "translateY(-50%)",
                        }}
                      />
                      <input
                        type="text"
                        placeholder="Search"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        style={{
                          paddingLeft: "40px",
                          paddingRight: "16px",
                          paddingTop: "8px",
                          paddingBottom: "8px",
                          border: "1px solid #e5e7eb",
                          borderRadius: "8px",
                          outline: "none",
                          fontSize: "14px",
                          backgroundColor: "#fff7ed",
                        }}
                        onFocus={(e) => {
                          e.currentTarget.style.borderColor = "#f59e0b";
                          e.currentTarget.style.boxShadow =
                            "0 0 0 2px rgba(245, 158, 11, 0.2)";
                        }}
                        onBlur={(e) => {
                          e.currentTarget.style.borderColor = "#d1d5db";
                          e.currentTarget.style.boxShadow = "none";
                        }}
                      />
                    </div>
                    <div style={{ position: "relative" }}>
                      <Calendar
                        style={{
                          width: 18,
                          height: 18,
                          color: "#f59e0b",
                          position: "absolute",
                          left: "12px",
                          top: "50%",
                          transform: "translateY(-50%)",
                        }}
                      />
                      <input
                        type="text"
                        placeholder="Filter by Date"
                        value={filterDate}
                        onChange={(e) => setFilterDate(e.target.value)}
                        style={{
                          paddingLeft: "40px",
                          paddingRight: "16px",
                          paddingTop: "8px",
                          paddingBottom: "8px",
                          border: "1px solid #e5e7eb",
                          borderRadius: "8px",
                          outline: "none",
                          fontSize: "14px",
                          backgroundColor: "#fff7ed",
                        }}
                        onFocus={(e) => {
                          e.currentTarget.style.borderColor = "#f59e0b";
                          e.currentTarget.style.boxShadow =
                            "0 0 0 2px rgba(245, 158, 11, 0.2)";
                        }}
                        onBlur={(e) => {
                          e.currentTarget.style.borderColor = "#d1d5db";
                          e.currentTarget.style.boxShadow = "none";
                        }}
                      />
                    </div>
                  </div>
                  <button
                    style={{
                      backgroundColor: "#f59e0b",
                      color: "white",
                      padding: "8px 16px",
                      borderRadius: "8px",
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      transition: "all 0.2s",
                      border: "none",
                      cursor: "pointer",
                      fontSize: "14px",
                      fontWeight: 500,
                    }}
                    onMouseEnter={(e) => {
                      (
                        e.currentTarget as HTMLButtonElement
                      ).style.backgroundColor = "#d97706";
                    }}
                    onMouseLeave={(e) => {
                      (
                        e.currentTarget as HTMLButtonElement
                      ).style.backgroundColor = "#f59e0b";
                    }}
                  >
                    <Plus style={{ width: 16, height: 16 }} />
                    New Patient
                  </button>
                </div>
                {/* Amber highlight bar */}
                <div
                  style={{
                    position: "absolute",
                    bottom: -1,
                    left: 24,
                    width: 144,
                    height: 2,
                    backgroundColor: "#f59e0b",
                  }}
                />
              </div>

              {/* Table */}
              <div style={{ flex: 1, overflow: "auto" }}>
                <table
                  style={{
                    width: "100%",
                    borderCollapse: "separate",
                    borderSpacing: 0,
                  }}
                >
                  <thead
                    style={{
                      position: "sticky",
                      top: 0,
                      backgroundColor: "#fff",
                      zIndex: 1,
                      boxShadow: "0 1px 0 rgba(0,0,0,0.06)",
                    }}
                  >
                    <tr>
                      <th
                        style={{
                          textAlign: "left",
                          padding: "16px",
                          fontWeight: 500,
                          color: "#374151",
                          position: "sticky",
                          top: 0,
                          backgroundColor: "#fff",
                        }}
                      >
                        Patient Name
                      </th>
                      <th
                        style={{
                          textAlign: "left",
                          padding: "16px",
                          fontWeight: 500,
                          color: "#374151",
                          position: "sticky",
                          top: 0,
                          backgroundColor: "#fff",
                        }}
                      >
                        Age
                      </th>
                      <th
                        style={{
                          textAlign: "left",
                          padding: "16px",
                          fontWeight: 500,
                          color: "#374151",
                          position: "sticky",
                          top: 0,
                          backgroundColor: "#fff",
                        }}
                      >
                        Gender
                      </th>
                      <th
                        style={{
                          textAlign: "left",
                          padding: "16px",
                          fontWeight: 500,
                          color: "#374151",
                          position: "sticky",
                          top: 0,
                          backgroundColor: "#fff",
                        }}
                      >
                        Blood Group
                      </th>
                      <th
                        style={{
                          textAlign: "left",
                          padding: "16px",
                          fontWeight: 500,
                          color: "#374151",
                          position: "sticky",
                          top: 0,
                          backgroundColor: "#fff",
                        }}
                      >
                        Phone Number
                      </th>
                      <th
                        style={{
                          textAlign: "left",
                          padding: "16px",
                          fontWeight: 500,
                          color: "#374151",
                          position: "sticky",
                          top: 0,
                          backgroundColor: "#fff",
                        }}
                      >
                        Email ID
                      </th>
                      <th
                        style={{
                          textAlign: "left",
                          padding: "16px",
                          fontWeight: 500,
                          color: "#374151",
                          position: "sticky",
                          top: 0,
                          backgroundColor: "#fff",
                        }}
                      >
                        AI Summary
                      </th>
                      <th
                        style={{
                          textAlign: "left",
                          padding: "16px",
                          fontWeight: 500,
                          color: "#374151",
                          position: "sticky",
                          top: 0,
                          backgroundColor: "#fff",
                        }}
                      >
                        User Action
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {currentPatients.map((patient, index) => (
                      <tr
                        key={patient.id}
                        onClick={() => openPatient(patient)}
                        style={{
                          borderTop: index > 0 ? "1px solid #e5e7eb" : "none",
                          transition: "background-color 0.2s, box-shadow 0.2s",
                          cursor: "pointer",
                          backgroundColor: index % 2 === 0 ? "#fff" : "#fffaf0",
                          borderRadius: 8,
                        }}
                        onMouseEnter={(e) => {
                          (
                            e.currentTarget as HTMLTableRowElement
                          ).style.backgroundColor = "#fff7ed";
                          (
                            e.currentTarget as HTMLTableRowElement
                          ).style.boxShadow =
                            "inset 0 0 0 1px rgba(245,158,11,0.15)";
                        }}
                        onMouseLeave={(e) => {
                          (
                            e.currentTarget as HTMLTableRowElement
                          ).style.backgroundColor = "transparent";
                          (
                            e.currentTarget as HTMLTableRowElement
                          ).style.boxShadow = "none";
                        }}
                      >
                        <td style={{ padding: "16px" }}>
                          <div
                            style={{
                              display: "flex",
                              alignItems: "center",
                              gap: "12px",
                            }}
                          >
                            <Avatar patient={patient} />
                            <span style={{ fontWeight: 500, color: "#1f2937" }}>
                              {patient.name}
                            </span>
                          </div>
                        </td>
                        <td style={{ padding: "16px", color: "#6b7280" }}>
                          {patient.age}
                        </td>
                        <td style={{ padding: "16px", color: "#6b7280" }}>
                          {patient.gender}
                        </td>
                        <td style={{ padding: "16px", color: "#6b7280" }}>
                          {patient.bloodGroup}
                        </td>
                        <td style={{ padding: "16px", color: "#6b7280" }}>
                          {patient.phone}
                        </td>
                        <td style={{ padding: "16px", color: "#6b7280" }}>
                          {patient.email}
                        </td>
                        <td style={{ padding: "16px" }}>
                          {patient.ai_summary_status === "done" ? (
                            <span
                              style={{
                                display: "inline-flex",
                                alignItems: "center",
                                gap: 6,
                                backgroundColor: "#10b981",
                                color: "white",
                                borderRadius: 999,
                                padding: "4px 10px",
                                fontSize: 12,
                                fontWeight: 600,
                                letterSpacing: 0.2,
                              }}
                            >
                              Done
                            </span>
                          ) : (
                            <span
                              style={{
                                display: "inline-flex",
                                alignItems: "center",
                                gap: 6,
                                backgroundColor: "#f59e0b",
                                color: "white",
                                borderRadius: 999,
                                padding: "4px 10px",
                                fontSize: 12,
                                fontWeight: 600,
                                letterSpacing: 0.2,
                              }}
                            >
                              Pending
                            </span>
                          )}
                        </td>
                        <td style={{ padding: "16px" }}>
                          <div
                            style={{
                              display: "flex",
                              alignItems: "center",
                              gap: "4px",
                            }}
                          >
                            {/* VIEW button with its own onClick */}
                            <ActionButton
                              type="view"
                              onClick={(e) => {
                                e.stopPropagation();
                                openPatient(patient);
                              }}
                            />
                            <ActionButton
                              type="delete"
                              onClick={async (e) => {
                                e.stopPropagation();
                                if (
                                  !confirm(
                                    `Are you sure you want to delete ${patient.name}?`,
                                  )
                                )
                                  return;

                                try {
                                  const API_BASE =
                                    process.env.NEXT_PUBLIC_API_URL ||
                                    "http://localhost:8082";
                                  const res = await fetch(
                                    `${API_BASE}/api/v1/patient/profile/${patient.token || patient.id}`,
                                    {
                                      method: "DELETE",
                                    },
                                  );
                                  if (!res.ok) {
                                    const t = await res.text();
                                    throw new Error(
                                      `Delete failed: ${res.status} ${t}`,
                                    );
                                  }

                                  // remove from state
                                  setPatients((prev) =>
                                    prev.filter((p) => p.id !== patient.id),
                                  );
                                } catch (err: any) {
                                  showToast(
                                    `Error deleting: ${err.message}`,
                                    "error",
                                  );
                                }
                              }}
                            />
                            <ActionButton
                              type="edit"
                              onClick={async (e) => {
                                showToast(
                                  "Edit functionality coming soon",
                                  "info",
                                );
                              }}
                            />
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div style={{ padding: "16px", borderTop: "1px solid #e5e7eb" }}>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                  }}
                >
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    style={{
                      color: currentPage === 1 ? "#9ca3af" : "#6b7280",
                      fontSize: "14px",
                      backgroundColor: "transparent",
                      border: "none",
                      cursor: currentPage === 1 ? "not-allowed" : "pointer",
                      transition: "color 0.2s",
                    }}
                    onMouseEnter={(e) => {
                      if (currentPage > 1) {
                        (e.currentTarget as HTMLButtonElement).style.color =
                          "#ea580c";
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (currentPage > 1) {
                        (e.currentTarget as HTMLButtonElement).style.color =
                          "#6b7280";
                      }
                    }}
                  >
                    Previous
                  </button>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                    }}
                  >
                    <button
                      onClick={() => handlePageChange(1)}
                      style={{
                        width: "32px",
                        height: "32px",
                        color: currentPage === 1 ? "#ffffff" : "#fb923c",
                        backgroundColor:
                          currentPage === 1 ? "#f59e0b" : "white",
                        borderRadius: "8px",
                        fontSize: "14px",
                        border:
                          currentPage === 1 ? "none" : "1px solid #e5e7eb",
                        cursor: "pointer",
                        boxShadow:
                          currentPage === 1
                            ? "0 0 0 2px rgba(245,158,11,0.25)"
                            : "none",
                        transition: "background-color 0.2s, box-shadow 0.2s",
                      }}
                      onMouseEnter={(e) => {
                        if (currentPage !== 1) {
                          (
                            e.currentTarget as HTMLButtonElement
                          ).style.backgroundColor = "#f3f4f6";
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (currentPage !== 1) {
                          (
                            e.currentTarget as HTMLButtonElement
                          ).style.backgroundColor = "transparent";
                        }
                      }}
                    >
                      1
                    </button>
                    {Array.from({ length: totalPages }, (_, i) => i + 1)
                      .slice(1)
                      .map((p) => (
                        <button
                          key={p}
                          onClick={() => handlePageChange(p)}
                          style={{
                            width: "32px",
                            height: "32px",
                            color: currentPage === p ? "#ffffff" : "#fb923c",
                            backgroundColor:
                              currentPage === p ? "#f59e0b" : "white",
                            borderRadius: "8px",
                            fontSize: "14px",
                            border:
                              currentPage === p ? "none" : "1px solid #e5e7eb",
                            cursor: "pointer",
                            boxShadow:
                              currentPage === p
                                ? "0 0 0 2px rgba(245,158,11,0.25)"
                                : "none",
                            transition:
                              "background-color 0.2s, box-shadow 0.2s",
                          }}
                          onMouseEnter={(e) => {
                            if (currentPage !== p) {
                              (
                                e.currentTarget as HTMLButtonElement
                              ).style.backgroundColor = "#f3f4f6";
                            }
                          }}
                          onMouseLeave={(e) => {
                            if (currentPage !== p) {
                              (
                                e.currentTarget as HTMLButtonElement
                              ).style.backgroundColor = "transparent";
                            }
                          }}
                        >
                          {p}
                        </button>
                      ))}
                  </div>
                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    style={{
                      color: currentPage === totalPages ? "#9ca3af" : "#6b7280",
                      fontSize: "14px",
                      backgroundColor: "transparent",
                      border: "none",
                      cursor:
                        currentPage === totalPages ? "not-allowed" : "pointer",
                      transition: "color 0.2s",
                    }}
                    onMouseEnter={(e) => {
                      if (currentPage < totalPages) {
                        (e.currentTarget as HTMLButtonElement).style.color =
                          "#ea580c";
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (currentPage < totalPages) {
                        (e.currentTarget as HTMLButtonElement).style.color =
                          "#6b7280";
                      }
                    }}
                  >
                    Next
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Popup */}
        <PatientInfoPopup
          isOpen={isPopupOpen}
          onClose={() => setIsPopupOpen(false)}
          patient={selectedPatient}
          summary={
            selectedPatient
              ? patientSummaries[selectedPatient.id]?.summary
              : null
          }
          evidence={
            selectedPatient
              ? patientSummaries[selectedPatient.id]?.evidence
              : null
          }
        />
      </div>
    </>
  );
};

export default DoctorPatientView;
