// Simple in-memory store for this session.
// Import { triageAnswers } anywhere to read results.
export type TriageAnswers = {
  painScore?: string;
  symptom?: string;
  details?: string;
};

export const triageAnswers: TriageAnswers = {};
