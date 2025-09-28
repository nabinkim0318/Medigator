"use client";

import React, { useEffect, useState } from "react";
import { Search, Calendar, Bell, Plus, Edit, X, Eye } from "lucide-react";
import PatientInfoPopup, { Patient } from "./PatientInfoPopup";

const DoctorPatientView: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterDate, setFilterDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // popup state
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);

  const [patients, setPatients] = useState<Patient[]>([]);

  useEffect(() => {
    const API_BASE = (process.env.NEXT_PUBLIC_API_URL as string) || "http://localhost:8082";
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
      borderRadius: "50%",
      transition: "all 0.2s",
      border: "none",
      cursor: "pointer",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      ...(t === "edit" && { color: "#ea580c", backgroundColor: "transparent" }),
      ...(t === "delete" && {
        color: "#dc2626",
        backgroundColor: "transparent",
      }),
      ...(t === "view" && { color: "#6b7280", backgroundColor: "transparent" }),
    });

    return (
      <button
        type="button"
        aria-label={type}
        style={getButtonStyle(type)}
        onClick={onClick}
        onMouseEnter={(e) => {
          const el = e.currentTarget;
          if (type === "edit") el.style.backgroundColor = "#fff7ed";
          if (type === "delete") el.style.backgroundColor = "#fef2f2";
          if (type === "view") el.style.backgroundColor = "#f9fafb";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = "transparent";
        }}
      >
        {icons[type]}
      </button>
    );
  };

  const Avatar: React.FC<{ patient: Patient }> = ({ patient }) =>
    patient.avatar ? (
      <img
        src={patient.avatar}
        alt={patient.name}
        style={{
          width: "40px",
          height: "40px",
          borderRadius: "50%",
          objectFit: "cover",
        }}
      />
    ) : (
      <div
        style={{
          width: "40px",
          height: "40px",
          borderRadius: "50%",
          backgroundColor: "#3b82f6",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "white",
          fontSize: "14px",
          fontWeight: 500,
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
    <div style={{ display: "flex", height: "100vh", backgroundColor: "#f9fafb", width: "100%" }}>
      {/* Main */}
      <div style={{display: "flex", flexDirection: "column", width: "100%", flex: 1}}>
      {/* Top bar */}
      <div
        style={{
          padding: "18px 28px",
          background: "linear-gradient(180deg,#fff7ed, #fff)",
          borderBottom: "1px solid #f1f5f9",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <h1 style={{ margin: 0, fontSize: 28, fontWeight: 700, color: "#374151" }}>Patients</h1>
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
                <div style={{ fontWeight: 700, color: "#334155" }}>Jonitha Cathrine</div>
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
                  color: "#ea580c",
                  borderBottom: "2px solid #ea580c",
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
            <div style={{ padding: "24px", borderBottom: "1px solid #e5e7eb" }}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <div
                  style={{ display: "flex", alignItems: "center", gap: "16px" }}
                >
                  <div style={{ position: "relative" }}>
                    <Search
                      style={{
                        width: 20,
                        height: 20,
                        color: "#9ca3af",
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
                        border: "1px solid #d1d5db",
                        borderRadius: "8px",
                        outline: "none",
                        fontSize: "14px",
                      }}
                      onFocus={(e) => {
                        e.currentTarget.style.borderColor = "#f97316";
                        e.currentTarget.style.boxShadow =
                          "0 0 0 2px rgba(249, 115, 22, 0.2)";
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
                    backgroundColor: "#f97316",
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
                    ).style.backgroundColor = "#ea580c";
                  }}
                  onMouseLeave={(e) => {
                    (
                      e.currentTarget as HTMLButtonElement
                    ).style.backgroundColor = "#f97316";
                  }}
                >
                  <Plus style={{ width: 16, height: 16 }} />
                  New Patient
                </button>
              </div>
            </div>

            {/* Table */}
            
            <div style={{ flex: 1, overflow: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead style={{ backgroundColor: "#f9fafb" }}>
                  <tr>
                    <th
                      style={{
                        textAlign: "left",
                        padding: "16px",
                        fontWeight: 500,
                        color: "#374151",
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
                      }}
                    >
                      User Action
                    </th>
                  </tr>
                </thead>
                
                <tbody>
                  {filteredPatients.map((patient, index) => (
                    <tr
                      key={patient.id}
                      onClick={() => openPatient(patient)}
                      style={{
                        borderTop: index > 0 ? "1px solid #e5e7eb" : "none",
                        transition: "background-color 0.2s",
                        cursor: "pointer",
                      }}
                      onMouseEnter={(e) => {
                        (
                          e.currentTarget as HTMLTableRowElement
                        ).style.backgroundColor = "#f9fafb";
                      }}
                      onMouseLeave={(e) => {
                        (
                          e.currentTarget as HTMLTableRowElement
                        ).style.backgroundColor = "transparent";
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
                                if (!confirm(`Are you sure you want to delete ${patient.name}?`)) return;

                                try {
                                  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8082";
                                  const res = await fetch(`${API_BASE}/api/v1/patient/profile/${patient.id}`, {
                                    method: "DELETE",
                                  });
                                  if (!res.ok) {
                                    const t = await res.text();
                                    throw new Error(`Delete failed: ${res.status} ${t}`);
                                  }

                                  // remove from state
                                  setPatients((prev) => prev.filter((p) => p.id !== patient.id));
                                } catch (err: any) {
                                  alert(`Error deleting: ${err.message}`);
                                }
                      
                            }}
                          />
                          <ActionButton
                            type="edit"
                            onClick={async (e) => {
                              alert(`Edit Placeholder`);
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
                  style={{
                    color: "#9ca3af",
                    fontSize: "14px",
                    backgroundColor: "transparent",
                    border: "none",
                    cursor: "pointer",
                  }}
                >
                  Previous
                </button>
                <div
                  style={{ display: "flex", alignItems: "center", gap: "8px" }}
                >
                  <button
                    style={{
                      width: "32px",
                      height: "32px",
                      backgroundColor: "#f97316",
                      color: "white",
                      borderRadius: "8px",
                      fontSize: "14px",
                      border: "none",
                      cursor: "pointer",
                    }}
                  >
                    1
                  </button>
                  {["2", "3", "4"].map((p) => (
                    <button
                      key={p}
                      style={{
                        width: "32px",
                        height: "32px",
                        color: "#6b7280",
                        backgroundColor: "transparent",
                        borderRadius: "8px",
                        fontSize: "14px",
                        border: "none",
                        cursor: "pointer",
                        transition: "background-color 0.2s",
                      }}
                      onMouseEnter={(e) => {
                        (
                          e.currentTarget as HTMLButtonElement
                        ).style.backgroundColor = "#f3f4f6";
                      }}
                      onMouseLeave={(e) => {
                        (
                          e.currentTarget as HTMLButtonElement
                        ).style.backgroundColor = "transparent";
                      }}
                    >
                      {p}
                    </button>
                  ))}
                </div>
                <button
                  style={{
                    color: "#6b7280",
                    fontSize: "14px",
                    backgroundColor: "transparent",
                    border: "none",
                    cursor: "pointer",
                    transition: "color 0.2s",
                  }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLButtonElement).style.color =
                      "#ea580c";
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLButtonElement).style.color =
                      "#6b7280";
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
      />
    </div>
  );
};

export default DoctorPatientView;
