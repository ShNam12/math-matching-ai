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

export function classifyQuestion(questionId) {
  return apiRequest(`/questions/${questionId}/classify`, {
    method: "POST",
  });
}

export function listQuestionsByTaxonomy({
  chapter_code = null,
  topic_code = null,
  problem_type_code = null,
  limit = 50,
  offset = 0,
}) {
  const params = new URLSearchParams();

  if (chapter_code) params.set("chapter_code", chapter_code);
  if (topic_code) params.set("topic_code", topic_code);
  if (problem_type_code) {
    params.set("problem_type_code", problem_type_code);
  }

  params.set("limit", String(limit));
  params.set("offset", String(offset));

  return apiRequest(`/questions?${params.toString()}`);
}

export function getQuestionTaxonomyQuality(questionId) {
  return apiRequest(`/questions/${questionId}/taxonomy-quality`);
}