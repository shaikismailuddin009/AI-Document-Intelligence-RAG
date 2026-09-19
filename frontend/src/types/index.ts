export type DocumentStatus = "uploaded" | "processing" | "processed" | "failed";

export interface DocumentRecord {
  document_id: string;
  filename: string;
  upload_time: string;
  status: DocumentStatus;
  chunk_count: number;
  error: string | null;
}

export interface SourceItem {
  document_id: string | null;
  filename: string;
  chunk_index: number | null;
  similarity: number;
  content: string;
}

export interface AnswerResponse {
  question: string;
  answer: string;
  sources: SourceItem[];
}
