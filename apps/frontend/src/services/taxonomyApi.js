import { apiRequest } from "./apiClient";

export function getTaxonomy() {
  return apiRequest("/taxonomy");
}

export function getTaxonomyStats() {
  return apiRequest("/taxonomy/stats");
}