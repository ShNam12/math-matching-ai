import { apiRequest } from "./apiClient";

export function searchQuestions({
  query,
  limit = 10,
  subject = null,
  chapter = null,
  chapter_code = null,
  topic_code = null,
  problem_type_code = null,
  difficulty = null,
  skill = null,
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
      chapter_code,
      topic_code,
      problem_type_code,
      difficulty,
      skill
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