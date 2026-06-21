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

export function previewConvertToMCQ(questionId, payload) {
  return apiRequest(`/generation/questions/${questionId}/convert-to-mcq/preview`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export function saveConvertToMCQ(questionId, payload) {
  return apiRequest(`/generation/questions/${questionId}/convert-to-mcq/save`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export function listSymbolicMCQSolvers() {
  return apiRequest("/generation/mcq/solvers");
}

export function previewSymbolicMCQ(payload) {
  return apiRequest("/generation/mcq/symbolic/preview", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export function saveSymbolicMCQ(payload) {
  return apiRequest("/generation/mcq/symbolic/save", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}
