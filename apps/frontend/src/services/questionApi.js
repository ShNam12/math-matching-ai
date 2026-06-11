import { apiRequest } from "./apiClient";

export function getQuestion(questionId) {
  return apiRequest(`/questions/${questionId}`);
}

export function listDocumentQuestions(documentId) {
  return apiRequest(`/documents/${documentId}/questions`);
}