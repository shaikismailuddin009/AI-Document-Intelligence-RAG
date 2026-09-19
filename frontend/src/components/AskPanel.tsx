import { useState, type FormEvent } from "react";
import { askQuestion, ApiError } from "../api/client";
import type { AnswerResponse, DocumentRecord } from "../types";
import SourceList from "./SourceList";

interface Props {
  documents: DocumentRecord[];
  selectedDocumentId: string | null;
}

export default function AskPanel({ documents, selectedDocumentId }: Props) {
  const [question, setQuestion] = useState("");
  const [isAsking, setIsAsking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnswerResponse | null>(null);

  const selectedDoc = documents.find((d) => d.document_id === selectedDocumentId) ?? null;
  const hasProcessedDocs = documents.some((d) => d.status === "processed");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();

    const trimmed = question.trim();
    if (!trimmed) {
      setError("Please enter a question.");
      return;
    }

    setError(null);
    setIsAsking(true);
    setResult(null);

    try {
      const response = await askQuestion({
        question: trimmed,
        document_id: selectedDocumentId,
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setIsAsking(false);
    }
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <h2 className="text-sm font-medium text-slate-700">
        Ask a question{selectedDoc ? ` about ${selectedDoc.filename}` : " (all documents)"}
      </h2>

      <form onSubmit={handleSubmit} className="mt-3 flex flex-col gap-2 sm:flex-row">
        <input
          type="text"
          aria-label="Question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. What machine learning methods are discussed?"
          disabled={!hasProcessedDocs}
          className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none disabled:bg-slate-50"
        />
        <button
          type="submit"
          disabled={isAsking || !hasProcessedDocs}
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
        >
          {isAsking ? "Asking…" : "Ask"}
        </button>
      </form>

      {!hasProcessedDocs && (
        <p className="mt-2 text-sm text-slate-500">Upload and process a document before asking questions.</p>
      )}

      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}

      {isAsking && (
        <div className="mt-4 flex items-center gap-2 text-sm text-slate-500">
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-indigo-600" />
          Retrieving relevant chunks and generating an answer…
        </div>
      )}

      {result && !isAsking && (
        <div className="mt-4">
          <h3 className="text-sm font-medium text-slate-700">Answer</h3>
          <p className="mt-1 whitespace-pre-wrap text-sm text-slate-800">{result.answer}</p>
          <SourceList sources={result.sources} />
        </div>
      )}
    </div>
  );
}
