"use client";

import React, { useState } from "react";
import { Search, Calendar, Bell, Plus, Edit, X, Eye } from "lucide-react";
import PatientInfoPopup, { Patient } from "./PatientInfoPopup";

const DoctorPatientView: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterDate, setFilterDate] = useState("");

  // popup state
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);

  const patients: Patient[] = [
    {
      id: "1",
      name: "Elizabeth Polsan",
      age: 24,
      gender: "Female",
      bloodGroup: "B+ve",
      phone: "+91 12345 67890",
      email: "elisabethpolsan@hotmail.com",
      avatar:
        "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=40&h=40&fit=crop&crop=face",
      initials: "EP",
    },
    {
      id: "2",
      name: "John David",
      age: 28,
      gender: "Male",
      bloodGroup: "B+ve",
      phone: "+91 12345 67890",
      email: "davidjohn22@gmail.com",
      avatar: "",
      initials: "JD",
    },
    {
      id: "3",
      name: "Krishtav Rajan",
      age: 24,
      gender: "Male",
      bloodGroup: "AB+ve",
      phone: "+91 12345 67890",
      email: "krishnrajan23@gmail.com",
      avatar: "",
      initials: "KR",
    },
    {
      id: "4",
      name: "Sumanth Tinson",
      age: 26,
      gender: "Male",
      bloodGroup: "O+ve",
      phone: "+91 12345 67890",
      email: "tintintn@gmail.com",
      avatar:
        "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=40&h=40&fit=crop&crop=face",
      initials: "ST",
    },
    {
      id: "5",
      name: "EG Subramani",
      age: 77,
      gender: "Male",
      bloodGroup: "AB+ve",
      phone: "+91 12345 67890",
      email: "egs3122@gmail.com",
      avatar:
        "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=40&h=40&fit=crop&crop=face",
      initials: "ES",
    },
    {
      id: "6",
      name: "Ranjan Maari",
      age: 77,
      gender: "Male",
      bloodGroup: "O+ve",
      phone: "+91 12345 67890",
      email: "ranjanmaari@yahoo.com",
      avatar:
        "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=40&h=40&fit=crop&crop=face",
      initials: "RM",
    },
    {
      id: "7",
      name: "Philipile Gopal",
      age: 55,
      gender: "Male",
      bloodGroup: "O-ve",
      phone: "+91 12345 67890",
      email: "gopal22@gmail.com",
      avatar:
        "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=40&h=40&fit=crop&crop=face",
      initials: "PG",
    },
  ];

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
      ...(t === "delete" && { color: "#dc2626", backgroundColor: "transparent" }),
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

  return (
    <div style={{ display: "flex", height: "100vh", backgroundColor: "#f9fafb" }}>
      {/* Sidebar */}
      <div
        style={{
          width: "256px",
          backgroundColor: "white",
          boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
          position: "relative",
        }}
      >
        <div style={{ padding: "24px", borderBottom: "1px solid #e5e7eb" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <div
              style={{
                width: "32px",
                height: "32px",
                backgroundColor: "#f97316",
                borderRadius: "8px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <span style={{ color: "white", fontWeight: "bold" }}>+</span>
            </div>
            <span style={{ fontSize: "20px", fontWeight: 600, color: "#1f2937" }}>
              Medigator
            </span>
          </div>
        </div>

        <nav style={{ padding: "16px" }}>
          {sidebarItems.map((item, index) => (
            <div
              key={index}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "12px",
                padding: "12px",
                borderRadius: "8px",
                marginBottom: "4px",
                cursor: "pointer",
                transition: "all 0.2s",
                ...(item.active
                  ? {
                      backgroundColor: "#fff7ed",
                      color: "#ea580c",
                      borderRight: "2px solid #ea580c",
                    }
                  : { color: "#6b7280" }),
              }}
              onMouseEnter={(e) => {
                if (!item.active) {
                  (e.currentTarget as HTMLElement).style.backgroundColor = "#f9fafb";
                }
              }}
              onMouseLeave={(e) => {
                if (!item.active) {
                  (e.currentTarget as HTMLElement).style.backgroundColor = "transparent";
                }
              }}
            >
              <span style={{ fontSize: "18px" }}>{item.icon}</span>
              <span style={{ fontWeight: 500 }}>{item.label}</span>
            </div>
          ))}
        </nav>

        <div style={{ position: "absolute", bottom: "16px", left: "16px", right: "16px" }}>
          <button
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              padding: "12px",
              width: "100%",
              color: "#6b7280",
              backgroundColor: "transparent",
              border: "none",
              borderRadius: "8px",
              transition: "all 0.2s",
              cursor: "pointer",
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#f9fafb";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLButtonElement).style.backgroundColor = "transparent";
            }}
          >
            <span style={{ fontSize: "18px" }}>🚪</span>
            <span style={{ fontWeight: 500 }}>Logout</span>
          </button>
        </div>
      </div>

      {/* Main */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        <div
          style={{
            backgroundColor: "white",
            borderBottom: "1px solid #e5e7eb",
            padding: "16px 24px",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <h1 style={{ fontSize: "24px", fontWeight: 600, color: "#1f2937", margin: 0 }}>
              Patient Details
            </h1>
            <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
              <button
                style={{
                  position: "relative",
                  padding: "8px",
                  color: "#6b7280",
                  backgroundColor: "transparent",
                  border: "none",
                  borderRadius: "50%",
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#f3f4f6";
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.backgroundColor = "transparent";
                }}
              >
                <Bell style={{ width: 20, height: 20 }} />
                <span
                  style={{
                    position: "absolute",
                    top: "-4px",
                    right: "-4px",
                    width: "12px",
                    height: "12px",
                    backgroundColor: "#ef4444",
                    borderRadius: "50%",
                  }}
                />
              </button>
              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                <img
                  src="https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=40&h=40&fit=crop&crop=face"
                  alt="Doctor"
                  style={{
                    width: "40px",
                    height: "40px",
                    borderRadius: "50%",
                    objectFit: "cover",
                  }}
                />
                <div>
                  <div style={{ fontSize: "14px", fontWeight: 500, color: "#1f2937" }}>
                    Jonitha Cathrine
                  </div>
                  <div style={{ fontSize: "12px", color: "#6b7280" }}>Doctor</div>
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
                <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
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
                  <div style={{ position: "relative" }}>
                    <Calendar
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
                      placeholder="Filter by Date"
                      value={filterDate}
                      onChange={(e) => setFilterDate(e.target.value)}
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
                    (e.currentTarget as HTMLButtonElement).style.backgroundColor =
                      "#ea580c";
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLButtonElement).style.backgroundColor =
                      "#f97316";
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
                    <th style={{ textAlign: "left", padding: "16px", fontWeight: 500, color: "#374151" }}>
                      Patient Name
                    </th>
                    <th style={{ textAlign: "left", padding: "16px", fontWeight: 500, color: "#374151" }}>
                      Age
                    </th>
                    <th style={{ textAlign: "left", padding: "16px", fontWeight: 500, color: "#374151" }}>
                      Gender
                    </th>
                    <th style={{ textAlign: "left", padding: "16px", fontWeight: 500, color: "#374151" }}>
                      Blood Group
                    </th>
                    <th style={{ textAlign: "left", padding: "16px", fontWeight: 500, color: "#374151" }}>
                      Phone Number
                    </th>
                    <th style={{ textAlign: "left", padding: "16px", fontWeight: 500, color: "#374151" }}>
                      Email ID
                    </th>
                    <th style={{ textAlign: "left", padding: "16px", fontWeight: 500, color: "#374151" }}>
                      User Action
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {patients.map((patient, index) => (
                    <tr
                      key={patient.id}
                      onClick={() => openPatient(patient)}
                      style={{
                        borderTop: index > 0 ? "1px solid #e5e7eb" : "none",
                        transition: "background-color 0.2s",
                        cursor: "pointer",
                      }}
                      onMouseEnter={(e) => {
                        (e.currentTarget as HTMLTableRowElement).style.backgroundColor = "#f9fafb";
                      }}
                      onMouseLeave={(e) => {
                        (e.currentTarget as HTMLTableRowElement).style.backgroundColor = "transparent";
                      }}
                    >
                      <td style={{ padding: "16px" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                          <Avatar patient={patient} />
                          <span style={{ fontWeight: 500, color: "#1f2937" }}>
                            {patient.name}
                          </span>
                        </div>
                      </td>
                      <td style={{ padding: "16px", color: "#6b7280" }}>{patient.age}</td>
                      <td style={{ padding: "16px", color: "#6b7280" }}>{patient.gender}</td>
                      <td style={{ padding: "16px", color: "#6b7280" }}>{patient.bloodGroup}</td>
                      <td style={{ padding: "16px", color: "#6b7280" }}>{patient.phone}</td>
                      <td style={{ padding: "16px", color: "#6b7280" }}>{patient.email}</td>
                      <td style={{ padding: "16px" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
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
                            onClick={(e) => {
                              e.stopPropagation();
                              // delete logic here...
                              alert(`Delete ${patient.name}`);
                            }}
                          />
                          <ActionButton
                            type="edit"
                            onClick={(e) => {
                              e.stopPropagation();
                              // edit logic here...
                              alert(`Edit ${patient.name}`);
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
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
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
                        (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#f3f4f6";
                      }}
                      onMouseLeave={(e) => {
                        (e.currentTarget as HTMLButtonElement).style.backgroundColor = "transparent";
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
                    (e.currentTarget as HTMLButtonElement).style.color = "#ea580c";
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLButtonElement).style.color = "#6b7280";
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
