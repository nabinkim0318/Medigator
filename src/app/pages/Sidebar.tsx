"use client";

import React from "react";

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

const NAV_ITEMS: { icon: string; label: NavItem }[] = [
  { icon: "🧭", label: "Dashboard" },
  { icon: "👥", label: "Patients" },
  { icon: "📝", label: "Appointments" },
  { icon: "👨‍⚕️", label: "Doctors" },
  { icon: "💬", label: "Messages" },
  { icon: "🏥", label: "Clinical Updates" },
  { icon: "⚙️", label: "Settings" },
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
            <span style={{ fontSize: 18 }}>{item.icon}</span>
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
          <span>🚪</span>
          <span style={{ fontWeight: 700 }}>Logout</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
