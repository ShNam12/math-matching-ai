import { apiRequest } from "./apiClient";

export function previewGeneratedQuestions(payload) {
  return apiRequest("/generation/questions/preview", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export function assessGeneratedQuestionQuality(payload) {
  return apiRequest("/generation/questions/quality", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export function saveGeneratedQuestion(payload) {
  return apiRequest("/generation/questions/save", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}