from app.services.embedding_service import generate_embeddings


def test_embedding_generation():

    texts = [
        "Machine learning allows computers to learn from data.",
        "Artificial intelligence can learn patterns from examples."
    ]

    embeddings = generate_embeddings(texts)

    assert len(embeddings) == 2
    assert embeddings.shape[1] > 0