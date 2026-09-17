import numpy as np

from app.services.embedding_service import generate_embeddings


def search_similar_chunks(
    query: str,
    chunks: list[str],
    embeddings,
    top_k: int = 3
):
    # Generate an embedding for the user's question
    query_embedding = generate_embeddings([query])[0]

    # Calculate similarity between the question and every chunk
    similarities = np.dot(embeddings, query_embedding)

    # Get indexes of the most similar chunks
    top_indexes = np.argsort(similarities)[::-1][:top_k]

    results = []

    for index in top_indexes:
        results.append({
            "chunk": chunks[index],
            "similarity": float(similarities[index])
        })

    return results