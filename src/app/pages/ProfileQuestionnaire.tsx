"use client";

import React, { useMemo, useState } from "react";
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
  const [touched, setTouched] = useState<{ [k: string]: boolean }>({});

  const ageOptions = useMemo(
    () => Array.from({ length: 130 }, (_, i) => String(i + 1)),
    [],
  );
  const bloodGroups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"];

  const errors = useMemo(() => {
    const e: { [k: string]: string } = {};
    if (!name.trim()) e.name = "Name is required";
    const ageNum = Number(age);
    if (!age || Number.isNaN(ageNum) || ageNum < 1 || ageNum > 130)
      e.age = "Select a valid age";
    if (!gender.trim()) e.gender = "Gender is required";
    if (!bloodGroup) e.bloodGroup = "Select blood group";
    if (!/^\d{10}$/.test(phone)) e.phone = "Phone must be 10 digits";
    if (!(email.includes("@") && email.includes(".com")))
      e.email = "Email not valid";
    return e;
  }, [name, age, gender, bloodGroup, phone, email]);

  const isValid = Object.keys(errors).length === 0;

  const handleBlur = (field: string) => {
    setTouched((t) => ({ ...t, [field]: true }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      token,
      profile: { name, age, gender, bloodGroup, phone, email },
    };
    const API_BASE =
      (process.env.NEXT_PUBLIC_API_URL as string) || "http://localhost:8082";
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
        router.push(
          `/OnboardingQuestionaire?token=${encodeURIComponent(token)}`,
        );
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
          <h1 className="text-2xl font-semibold text-gray-900 mb-4">
            Personal Profile Details
          </h1>
          <form
            onSubmit={handleSubmit}
            className="flex flex-col gap-3 text-left"
          >
            <div>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                onBlur={() => handleBlur("name")}
                name="name"
                placeholder="Full name"
                className="w-full rounded-xl border border-gray-200 px-4 py-3"
              />
              {touched.name && errors.name && (
                <div className="text-red-500 text-sm mt-1">{errors.name}</div>
              )}
            </div>

            <div>
              <select
                value={age}
                onChange={(e) => setAge(e.target.value)}
                onBlur={() => handleBlur("age")}
                name="age"
                className="w-full rounded-xl border border-gray-200 px-4 py-3 bg-white"
              >
                <option value="">Select age</option>
                {ageOptions.map((a) => (
                  <option key={a} value={a}>
                    {a}
                  </option>
                ))}
              </select>
              {touched.age && errors.age && (
                <div className="text-red-500 text-sm mt-1">{errors.age}</div>
              )}
            </div>

            <div>
              <select
                value={gender}
                onChange={(e) => setGender(e.target.value)}
                onBlur={() => handleBlur("gender")}
                name="gender"
                className="w-full rounded-xl border border-gray-200 px-4 py-3 bg-white"
              >
                <option value="">Select Gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
              {touched.gender && errors.gender && (
                <div className="text-red-500 text-sm mt-1">{errors.gender}</div>
              )}
            </div>

            <div>
              <select
                value={bloodGroup}
                onChange={(e) => setBloodGroup(e.target.value)}
                onBlur={() => handleBlur("bloodGroup")}
                name="bloodGroup"
                className="w-full rounded-xl border border-gray-200 px-4 py-3 bg-white"
              >
                <option value="">Select Blood Group</option>
                {bloodGroups.map((bg) => (
                  <option key={bg} value={bg}>
                    {bg}
                  </option>
                ))}
              </select>
              {touched.bloodGroup && errors.bloodGroup && (
                <div className="text-red-500 text-sm mt-1">
                  {errors.bloodGroup}
                </div>
              )}
            </div>

            <div>
              <input
                value={phone}
                onChange={(e) =>
                  setPhone(e.target.value.replace(/[^0-9]/g, ""))
                }
                onBlur={() => handleBlur("phone")}
                name="phone"
                placeholder="Phone number (10 digits)"
                className="w-full rounded-xl border border-gray-200 px-4 py-3"
                maxLength={10}
              />
              {touched.phone && errors.phone && (
                <div className="text-red-500 text-sm mt-1">{errors.phone}</div>
              )}
            </div>

            <div>
              <input
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onBlur={() => handleBlur("email")}
                name="email"
                placeholder="Email"
                className="w-full rounded-xl border border-gray-200 px-4 py-3"
              />
              {touched.email && errors.email && (
                <div className="text-red-500 text-sm mt-1">{errors.email}</div>
              )}
            </div>

            <button
              type="submit"
              className={`w-full px-6 py-3 rounded-xl ${isValid ? "bg-orange-500 text-white" : "bg-gray-300 text-gray-600 cursor-not-allowed"}`}
              disabled={!isValid}
            >
              Continue
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
