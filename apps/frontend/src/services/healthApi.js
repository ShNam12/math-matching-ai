import { apiRequest } from "./apiClient";

export function getRootStatus() {
  return apiRequest("/");
}

export function getHealth() {
  return apiRequest("/health");
}

export function getReadiness() {
  return apiRequest("/ready");
}