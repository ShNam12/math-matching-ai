import { apiRequest } from "./apiClient";

export function searchQuestions(payload) {
  return apiRequest("/search/questions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export function searchFormulas(payload) {
  return apiRequest("/search/formulas", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}