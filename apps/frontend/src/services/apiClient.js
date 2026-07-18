import { clearStoredAuthSession, getAccessToken } from "../auth/session";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function apiRequest(path, options = {}) {
  const headers = new Headers(options.headers ?? {});
  const accessToken = getAccessToken();

  if (accessToken && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });
  const contentType = response.headers.get("content-type") ?? "";

  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    if (response.status === 401) {
      clearStoredAuthSession();
    }

    const detail =
      typeof data === "object" && data?.detail
        ? data.detail
        : data;

    const message =
      typeof detail === "string"
        ? detail
        : typeof detail?.message === "string"
          ? detail.message
          : JSON.stringify(detail);

    const error = new Error(message || "Request failed");
    error.status = response.status;
    error.detail = detail;
    throw error;
  }

  return data;
}
