import { apiRequest } from "./apiClient";

export function login({ username, password }) {
  return apiRequest("/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });
}

export function getCurrentUser() {
  return apiRequest("/auth/me");
}

