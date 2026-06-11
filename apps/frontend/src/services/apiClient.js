const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  const contentType = response.headers.get("content-type") ?? "";

  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail =
      typeof data === "object" && data?.detail
        ? data.detail
        : data;

    const message =
      typeof detail === "string"
        ? detail
        : JSON.stringify(detail);

    throw new Error(message || "Request failed");
  }

  return data;
}