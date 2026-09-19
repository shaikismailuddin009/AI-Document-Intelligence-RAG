import uuid

import chromadb
import numpy as np
import pytest

import app.services.vector_store_service as vector_store_service


@pytest.fixture
def isolated_collection(monkeypatch):
    test_client = chromadb.EphemeralClient()

    # Generate a genuinely unique collection name for every test.
    collection_name = f"test-documents-{uuid.uuid4().hex}"

    test_collection = test_client.get_or_create_collection(
        name=collection_name
    )

    monkeypatch.setattr(
        vector_store_service,
        "collection",
        test_collection,
    )

    return test_collection


def _fake_embeddings(n: int, dim: int = 8):
    return np.random.rand(n, dim)


def test_store_document_chunks_returns_chunk_count(isolated_collection):
    chunks = [
        "chunk one",
        "chunk two",
        "chunk three",
    ]

    embeddings = _fake_embeddings(3)

    count = vector_store_service.store_document_chunks(
        chunks=chunks,
        embeddings=embeddings,
        document_id="doc-1",
        filename="file.pdf",
    )

    assert count == 3
    assert isolated_collection.count() == 3


def test_store_document_chunks_empty_list_is_noop(isolated_collection):
    count = vector_store_service.store_document_chunks(
        chunks=[],
        embeddings=_fake_embeddings(0),
        document_id="doc-1",
        filename="file.pdf",
    )

    assert count == 0
    assert isolated_collection.count() == 0


def test_store_document_chunks_sets_metadata(isolated_collection):
    vector_store_service.store_document_chunks(
        chunks=["only chunk"],
        embeddings=_fake_embeddings(1),
        document_id="doc-42",
        filename="report.pdf",
    )

    result = isolated_collection.get(ids=["doc-42-0"])

    metadata = result["metadatas"][0]

    assert metadata["document_id"] == "doc-42"
    assert metadata["filename"] == "report.pdf"
    assert metadata["chunk_index"] == 0


def test_search_document_filters_by_document_id(
    isolated_collection,
    monkeypatch,
):
    vector_store_service.store_document_chunks(
        chunks=["alpha content"],
        embeddings=_fake_embeddings(1),
        document_id="doc-a",
        filename="a.pdf",
    )

    vector_store_service.store_document_chunks(
        chunks=["beta content"],
        embeddings=_fake_embeddings(1),
        document_id="doc-b",
        filename="b.pdf",
    )

    # search_document imports generate_embeddings from the
    # embedding service, so patch it at its source module.
    import app.services.embedding_service as embedding_service

    monkeypatch.setattr(
        embedding_service,
        "generate_embeddings",
        lambda texts: _fake_embeddings(len(texts)),
    )

    results = vector_store_service.search_document(
        query="anything",
        top_k=5,
        document_id="doc-a",
    )

    metadatas = results["metadatas"][0]

    assert len(metadatas) == 1
    assert metadatas[0]["document_id"] == "doc-a"


def test_delete_document_chunks_removes_only_that_document(
    isolated_collection,
):
    vector_store_service.store_document_chunks(
        chunks=["a", "b"],
        embeddings=_fake_embeddings(2),
        document_id="doc-a",
        filename="a.pdf",
    )

    vector_store_service.store_document_chunks(
        chunks=["c"],
        embeddings=_fake_embeddings(1),
        document_id="doc-b",
        filename="b.pdf",
    )

    vector_store_service.delete_document_chunks("doc-a")

    assert isolated_collection.count() == 1

    remaining = isolated_collection.get()

    assert remaining["metadatas"][0]["document_id"] == "doc-b"