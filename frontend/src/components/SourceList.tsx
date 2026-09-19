import type { SourceItem } from "../types";

export default function SourceList({ sources }: { sources: SourceItem[] }) {
  if (sources.length === 0) return null;

  return (
    <div className="mt-4">
      <h3 className="text-sm font-medium text-slate-700">Sources</h3>
      <ul className="mt-2 space-y-2">
        {sources.map((source, index) => (
          <li key={`${source.filename}-${source.chunk_index}-${index}`}>
            <details className="rounded-lg border border-slate-200 bg-white p-3">
              <summary className="cursor-pointer text-sm text-slate-700">
                <span className="font-medium">{source.filename}</span>
                {source.chunk_index !== null && (
                  <span className="text-slate-400"> · chunk {source.chunk_index}</span>
                )}
                <span className="ml-2 text-xs text-slate-400">
                  {Math.round(source.similarity * 100)}% match
                </span>
              </summary>
              <p className="mt-2 whitespace-pre-wrap text-sm text-slate-600">{source.content}</p>
            </details>
          </li>
        ))}
      </ul>
    </div>
  );
}
