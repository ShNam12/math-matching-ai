import { apiRequest } from "./apiClient";

export function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  return apiRequest("/documents/upload", {
    method: "POST",
    body: formData,
  });
}

export function listDocuments() {
  return apiRequest("/documents");
}

export function getDocument(documentId) {
  return apiRequest(`/documents/${documentId}`);
}

export function getDocumentStatus(documentId) {
  return apiRequest(`/documents/${documentId}/status`);
}

export function getDocumentMarkdown(documentId) {
  return apiRequest(`/documents/${documentId}/markdown`);
}

export function storeDocument(documentId) {
  return apiRequest(`/documents/${documentId}/store`, {
    method: "POST",
  });
}