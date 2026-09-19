import { useRef, useState } from "react";
import { uploadDocument, ApiError } from "../api/client";
import type { DocumentRecord } from "../types";

interface Props {
  onUploaded: (doc: DocumentRecord) => void;
}

export default function UploadPanel({ onUploaded }: Props) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File | undefined) {
    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are supported.");
      return;
    }

    setError(null);
    setIsUploading(true);

    try {
      const doc = await uploadDocument(file);
      onUploaded(doc);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div className="rounded-lg border border-dashed border-slate-300 bg-white p-4">
      <label htmlFor="pdf-upload-input" className="block text-sm font-medium text-slate-700">
        Upload a PDF
      </label>
      <p className="mt-1 text-xs text-slate-500">
        The document is extracted, chunked, embedded, and indexed automatically.
      </p>

      <div className="mt-3 flex items-center gap-3">
        <input
          id="pdf-upload-input"
          ref={inputRef}
          type="file"
          accept="application/pdf"
          disabled={isUploading}
          onChange={(e) => handleFile(e.target.files?.[0])}
          className="block w-full text-sm text-slate-600 file:mr-3 file:rounded-md file:border-0 file:bg-indigo-600 file:px-3 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-indigo-500 disabled:opacity-50"
        />
        {isUploading && (
          <span className="flex items-center gap-2 text-sm text-indigo-600">
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-indigo-300 border-t-indigo-600" />
            Processing…
          </span>
        )}
      </div>

      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </div>
  );
}
