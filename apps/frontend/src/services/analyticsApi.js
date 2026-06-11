import { apiRequest } from "./apiClient";

export function getAnalyticsSummary() {
  return apiRequest("/analytics/summary");
}