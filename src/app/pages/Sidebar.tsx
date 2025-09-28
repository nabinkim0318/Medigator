"use client";

import React from "react";
import { useRouter } from "next/navigation";
import dashboard from "../assets/dashboard.svg";
import patients from "../assets/patients.svg";
import appointments from "../assets/appointments.svg";
import doctors from "../assets/doctors.svg";
import messages from "../assets/messages.svg";
import clinical_updates from "../assets/clinical_updates.svg";
import settings from "../assets/settings.svg";
import logout from "../assets/logout.svg";

type NavItem =
  | "Dashboard"
  | "Patients"
  | "Appointments"
  | "Doctors"
  | "Messages"
  | "Clinical Updates"
  | "Settings";

export interface SidebarProps {
  active?: NavItem;
  onSelect?: (item: NavItem) => void;
}

// Turbopack/Next may import SVGs as objects with a `src` field
const getIconSrc = (value: unknown): string => {
  if (typeof value === "string") return value;
  if (value && typeof value === "object" && "src" in (value as any)) {
    return (value as any).src as string;
  }
  return "";
};

const NAV_ITEMS: { icon: any; label: NavItem }[] = [
  { icon: dashboard as any, label: "Dashboard" },
  { icon: patients as any, label: "Patients" },
  { icon: appointments as any, label: "Appointments" },
  { icon: doctors as any, label: "Doctors" },
  { icon: messages as any, label: "Messages" },
  { icon: clinical_updates as any, label: "Clinical Updates" },
  { icon: settings as any, label: "Settings" },
];

const Sidebar: React.FC<SidebarProps> = ({
  active = "Dashboard",
  onSelect,
}) => {
  return (
    <aside
      style={{
        width: 256,
        height: "100vh",
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
              color: "white",
              borderRadius: 10,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: 900,
              fontSize: 18,
            }}
          >
            <img
              src="/logo.png"
              alt="Medigator Logo"
              style={{ width: 24, height: 24 }}
            />
          </div>
          <div style={{ color: "#ef6c00", fontWeight: 800, fontSize: 18 }}>
            Medigator
          </div>
        </div>
      </div>

      {/* Nav */}
      {NAV_ITEMS.map((item) => {
        const isActive = item.label === active;
        return (
          <button
            key={item.label}
            onClick={() => onSelect?.(item.label)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              padding: "12px 16px",
              color: isActive ? "#ea580c" : "#475569",
              background: isActive ? "#fff7ed" : "transparent",
              borderRight: isActive
                ? "3px solid #ea580c"
                : "3px solid transparent",
              cursor: "pointer",
              border: "none",
              textAlign: "left",
            }}
          >
            <img
              src={getIconSrc(item.icon)}
              alt={item.label}
              style={{ width: 18, height: 18 }}
            />
            <span style={{ fontWeight: 700 }}>{item.label}</span>
          </button>
        );
      })}

      {/* Footer */}
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
          <img
            src={getIconSrc(logout)}
            alt="Logout"
            style={{ width: 18, height: 18 }}
          />
          <span style={{ fontWeight: 700 }}>Logout</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
