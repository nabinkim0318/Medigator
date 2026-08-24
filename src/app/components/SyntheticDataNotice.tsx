"use client";

import React from "react";

export default function SyntheticDataNotice() {
  return (
    <div className="mb-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-left text-sm text-amber-900">
      <p className="font-medium">Synthetic / demo data only</p>
      <p className="mt-1 text-amber-800">
        Research prototype — not for diagnosis, treatment, or clinical use. Do
        not enter real patient names, phones, emails, or other identifiers. Demo
        mode does not make real information safe. Use{" "}
        <code className="rounded bg-white px-1">@example.com</code> emails and
        phone numbers starting with{" "}
        <code className="rounded bg-white px-1">555</code>.
      </p>
    </div>
  );
}
