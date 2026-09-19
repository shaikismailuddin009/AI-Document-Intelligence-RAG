import { useCallback, useEffect, useState } from "react";
import { deleteDocument, listDocuments, ApiError } from "./api/client";
import type { DocumentRecord } from "./types";
import UploadPanel from "./components/UploadPanel";
import DocumentList from "./components/DocumentList";
import AskPanel from "./components/AskPanel";

export default function App() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [isLoadingDocs, setIsLoadingDocs] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const refreshDocuments = useCallback(async () => {
    try {
      const docs = await listDocuments();
      setDocuments(docs);
      setLoadError(null);
    } catch (err) {
      setLoadError(
        err instanceof ApiError
          ? err.message
          : "Could not load documents. Is the backend running?",
      );
    } finally {
      setIsLoadingDocs(false);
    }
  }, []);

  useEffect(() => {
    refreshDocuments();
  }, [refreshDocuments]);

  function handleUploaded(doc: DocumentRecord) {
    setDocuments((prev) => [doc, ...prev]);
  }

  async function handleDelete(id: string) {
    await deleteDocument(id);
    setDocuments((prev) => prev.filter((d) => d.document_id !== id));
    if (selectedId === id) setSelectedId(null);
  }

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-5xl px-4 py-4">
          <h1 className="text-lg font-semibold text-slate-900">AI Document Intelligence</h1>
          <p className="text-sm text-slate-500">
            Upload PDFs, then ask grounded questions with cited sources.
          </p>
        </div>
      </header>

      <main className="mx-auto grid max-w-5xl grid-cols-1 gap-6 px-4 py-6 md:grid-cols-[320px_1fr]">
        <section className="space-y-4">
          <UploadPanel onUploaded={handleUploaded} />

          {loadError && (
            <p className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-600">
              {loadError}
            </p>
          )}

          <DocumentList
            documents={documents}
            isLoading={isLoadingDocs}
            selectedId={selectedId}
            onSelect={setSelectedId}
            onDelete={handleDelete}
          />
        </section>

        <section>
          <AskPanel documents={documents} selectedDocumentId={selectedId} />
        </section>
      </main>
    </div>
  );
}
