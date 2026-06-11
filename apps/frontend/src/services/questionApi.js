import { apiRequest } from "./apiClient";

export function getQuestion(questionId) {
  return apiRequest(`/questions/${questionId}`);
}

export function listDocumentQuestions(documentId) {
  return apiRequest(`/documents/${documentId}/questions`);
}

export function updateQuestion(questionId, payload) {
  return apiRequest(`/questions/${questionId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

