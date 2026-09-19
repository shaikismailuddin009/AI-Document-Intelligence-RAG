import chromadb

CHROMA_PATH = "app/data/chroma"


client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


collection = client.get_or_create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"},
)

def store_document_chunks(
    chunks: list[str],
    embeddings,
    document_id: str,
    filename: str,
):
    if not chunks:
        return 0

    ids = [
        f"{document_id}-{index}"
        for index in range(len(chunks))
    ]

    metadata = [
        {
            "document_id": document_id,
            "filename": filename,
            "chunk_index": index,
        }
        for index in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=metadata,
    )

    return len(chunks)


def search_document(
    query: str,
    top_k: int = 3,
    document_id: str | None = None,
):
    from app.services.embedding_service import generate_embeddings

    query_embedding = generate_embeddings([query])[0]

    where = {"document_id": document_id} if document_id else None

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k,
        where=where,
    )

    return results


def delete_document_chunks(document_id: str) -> None:
    collection.delete(where={"document_id": document_id})
