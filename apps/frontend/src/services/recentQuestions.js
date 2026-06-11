const STORAGE_KEY = "recent_viewed_question_ids";
const MAX_RECENT = 5;

export function getRecentQuestionIds() {
  try {
    const rawValue = localStorage.getItem(STORAGE_KEY);
    const ids = JSON.parse(rawValue || "[]");

    return Array.isArray(ids) ? ids : [];
  } catch {
    return [];
  }
}

export function rememberRecentQuestion(questionId) {
  if (!questionId) {
    return;
  }

  const currentIds = getRecentQuestionIds();
  const nextIds = [
    questionId,
    ...currentIds.filter((id) => id !== questionId),
  ].slice(0, MAX_RECENT);

  localStorage.setItem(STORAGE_KEY, JSON.stringify(nextIds));
}