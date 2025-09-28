"use client";

import React, { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function ProfileQuestionnaire() {
  const router = useRouter();
  const sp = useSearchParams();
  const token = sp?.get("token") ?? "";

  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");
  const [bloodGroup, setBloodGroup] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      token,
      profile: { name, age, gender, bloodGroup, phone, email },
    };
    const API_BASE = (process.env.NEXT_PUBLIC_API_URL as string) || "http://localhost:8082";
    fetch(`${API_BASE}/api/v1/patient/profile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(async (res) => {
        if (!res.ok) {
          const t = await res.text();
          throw new Error(`save failed: ${res.status} ${t}`);
        }
        return res.json();
      })
      .then(() => {
        router.push(`/OnboardingQuestionaire?token=${encodeURIComponent(token)}`);
      })
      .catch((err) => {
        // eslint-disable-next-line no-alert
        alert(`Failed to save profile: ${err.message}`);
      });
  };

  return (
    <div className="min-h-screen w-full bg-orange-50 flex items-center justify-center px-4">
      <div className="mx-auto w-full max-w-md text-center">
        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-6 sm:p-8">
          <h1 className="text-2xl font-semibold text-gray-900 mb-4">Personal Profile Details</h1>
          <form onSubmit={handleSubmit} className="flex flex-col gap-3 text-left">
            <input value={name} onChange={(e) => setName(e.target.value)} name="name" placeholder="Full name" className="w-full rounded-xl border border-gray-200 px-4 py-3" />
            <input value={age} onChange={(e) => setAge(e.target.value)} name="age" placeholder="Age" className="w-full rounded-xl border border-gray-200 px-4 py-3" />
            <input value={gender} onChange={(e) => setGender(e.target.value)} name="gender" placeholder="Gender" className="w-full rounded-xl border border-gray-200 px-4 py-3" />
            <input value={bloodGroup} onChange={(e) => setBloodGroup(e.target.value)} name="bloodGroup" placeholder="Blood Group" className="w-full rounded-xl border border-gray-200 px-4 py-3" />
            <input value={phone} onChange={(e) => setPhone(e.target.value)} name="phone" placeholder="Phone number" className="w-full rounded-xl border border-gray-200 px-4 py-3" />
            <input value={email} onChange={(e) => setEmail(e.target.value)} name="email" placeholder="Email" className="w-full rounded-xl border border-gray-200 px-4 py-3" />

            <button type="submit" className="w-full px-6 py-3 rounded-xl bg-orange-500 text-white">Continue</button>
          </form>
        </div>
      </div>
    </div>
  );
}
