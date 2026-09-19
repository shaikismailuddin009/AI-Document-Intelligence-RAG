def build_context(results) -> str:
    """Build the text block sent to the LLM, labelling each chunk with
    its source filename and chunk index so citations stay traceable."""

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[{}] * len(documents)])[0]

    context_parts = []

    for index, (document, metadata) in enumerate(
        zip(documents, metadatas), start=1
    ):
        filename = metadata.get("filename", "unknown document")
        chunk_index = metadata.get("chunk_index", "?")

        context_parts.append(
            f"[Source {index}: {filename}, chunk {chunk_index}]\n{document}"
        )

    return "\n\n".join(context_parts)


def build_sources(results) -> list[dict]:
    """Turn a ChromaDB query result into the source list returned to the
    frontend: filename, chunk index, an approximate similarity score, and
    the chunk content itself."""

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[{}] * len(documents)])[0]
    distances = results.get("distances", [[0.0] * len(documents)])[0]

    sources = []

    for document, metadata, distance in zip(documents, metadatas, distances):
        # The collection is explicitly configured with hnsw:space="cosine"
        # (see vector_store_service), so Chroma's distance IS cosine
        # distance and (1 - distance) is exactly cosine similarity, not an
        # approximation. Still clamped defensively in case of float drift.
        similarity = max(0.0, min(1.0, 1 - distance))

        sources.append({
            "document_id": metadata.get("document_id"),
            "filename": metadata.get("filename", "unknown document"),
            "chunk_index": metadata.get("chunk_index"),
            "similarity": round(float(similarity), 4),
            "content": document,
        })

    return sources
