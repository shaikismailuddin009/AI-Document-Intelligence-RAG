import chromadb


CHROMA_PATH = "app/data/chroma"


client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


collection = client.get_or_create_collection(
    name="documents"
)


def store_document_chunks(
    chunks: list[str],
    embeddings,
    filename: str
):
    ids = [
        f"{filename}-{index}"
        for index in range(len(chunks))
    ]

    metadata = [
        {
            "filename": filename,
            "chunk_index": index
        }
        for index in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=metadata
    )

    return len(chunks)
def search_document(
    query: str,
    top_k: int = 3
):
    from app.services.embedding_service import generate_embeddings

    query_embedding = generate_embeddings([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k
    )

    return results