import { apiRequest } from "./apiClient";

export function searchQuestions({
  query,
  limit = 10,
  subject = null,
  chapter = null,
  difficulty = null,
}) {
  return apiRequest("/search/questions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query,
      limit,
      subject,
      chapter,
      difficulty,
    }),
  });
}

export function searchFormulas({ latex, limit = 10, source = null }) {
  return apiRequest("/search/formulas", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      latex,
      limit,
      source,
    }),
  });
}