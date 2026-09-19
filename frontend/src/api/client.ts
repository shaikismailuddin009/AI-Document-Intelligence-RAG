import type { AnswerResponse, DocumentRecord } from "../types";

// Centralized backend URL — set VITE_API_BASE_URL in frontend/.env for a
// non-default backend. Every request in this file goes through here so the
// base URL is never duplicated across components.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, options);
  } catch {
    throw new ApiError(
      "Could not reach the backend. Make sure the API is running.",
      0,
    );
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;

    try {
      const body = await response.json();
      if (body?.detail) {
        detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
      }
    } catch {
      // response wasn't JSON — keep the generic message
    }

    throw new ApiError(detail, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export function listDocuments(): Promise<DocumentRecord[]> {
  return request<DocumentRecord[]>("/documents");
}

export function deleteDocument(documentId: string): Promise<{ message: string; document_id: string }> {
  return request(`/documents/${documentId}`, { method: "DELETE" });
}

export function uploadDocument(file: File): Promise<DocumentRecord> {
  const formData = new FormData();
  formData.append("file", file);

  return request<DocumentRecord>("/documents/upload", {
    method: "POST",
    body: formData,
  });
}

export function askQuestion(payload: {
  question: string;
  top_k?: number;
  document_id?: string | null;
}): Promise<AnswerResponse> {
  return request<AnswerResponse>("/rag/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
