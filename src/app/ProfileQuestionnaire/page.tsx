"use client";

import React, { Suspense } from "react";
import ProfileQuestionnaire from "../pages/ProfileQuestionnaire";

export default function ProfileQuestionnaireRoute() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ProfileQuestionnaire />
    </Suspense>
  );
}
