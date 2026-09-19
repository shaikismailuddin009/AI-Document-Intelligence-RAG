import { useState } from "react";
import type { DocumentRecord } from "../types";
import StatusBadge from "./StatusBadge";

interface Props {
  documents: DocumentRecord[];
  isLoading: boolean;
  selectedId: string | null;
  onSelect: (id: string | null) => void;
  onDelete: (id: string) => Promise<void>;
}

export default function DocumentList({ documents, isLoading, selectedId, onSelect, onDelete }: Props) {
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  async function confirmDelete(id: string) {
    setDeletingId(id);
    try {
      await onDelete(id);
    } finally {
      setDeletingId(null);
      setPendingDeleteId(null);
    }
  }

  if (isLoading) {
    return <p className="text-sm text-slate-500">Loading documents…</p>;
  }

  if (documents.length === 0) {
    return (
      <p className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-500">
        No documents yet — upload a PDF to get started.
      </p>
    );
  }

  return (
    <ul className="space-y-2">
      <li>
        <button
          onClick={() => onSelect(null)}
          className={`w-full rounded-lg border px-3 py-2 text-left text-sm transition ${
            selectedId === null
              ? "border-indigo-500 bg-indigo-50 text-indigo-700"
              : "border-slate-200 bg-white text-slate-600 hover:border-slate-300"
          }`}
        >
          Search across all documents
        </button>
      </li>

      {documents.map((doc) => (
        <li
          key={doc.document_id}
          className={`rounded-lg border px-3 py-2 transition ${
            selectedId === doc.document_id
              ? "border-indigo-500 bg-indigo-50"
              : "border-slate-200 bg-white hover:border-slate-300"
          }`}
        >
          <button
            onClick={() => onSelect(doc.document_id)}
            className="block w-full text-left"
            disabled={doc.status !== "processed"}
          >
            <div className="flex items-center justify-between gap-2">
              <span className="truncate text-sm font-medium text-slate-800">{doc.filename}</span>
              <StatusBadge status={doc.status} />
            </div>
            <div className="mt-1 text-xs text-slate-500">
              {doc.status === "processed" && `${doc.chunk_count} chunks`}
              {doc.status === "failed" && (doc.error ?? "Processing failed")}
              {doc.status === "processing" && "Processing…"}
            </div>
          </button>

          <div className="mt-2 flex justify-end">
            {pendingDeleteId === doc.document_id ? (
              <div className="flex items-center gap-2 text-xs">
                <span className="text-slate-500">Delete this document?</span>
                <button
                  onClick={() => confirmDelete(doc.document_id)}
                  disabled={deletingId === doc.document_id}
                  className="font-medium text-red-600 hover:text-red-700 disabled:opacity-50"
                >
                  {deletingId === doc.document_id ? "Deleting…" : "Confirm"}
                </button>
                <button
                  onClick={() => setPendingDeleteId(null)}
                  className="text-slate-500 hover:text-slate-700"
                >
                  Cancel
                </button>
              </div>
            ) : (
              <button
                onClick={() => setPendingDeleteId(doc.document_id)}
                className="text-xs text-slate-400 hover:text-red-600"
              >
                Delete
              </button>
            )}
          </div>
        </li>
      ))}
    </ul>
  );
}
