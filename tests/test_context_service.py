from app.services.context_service import build_context, build_sources


def _fake_results():
    return {
        "documents": [["first chunk text", "second chunk text"]],
        "metadatas": [[
            {"document_id": "doc-1", "filename": "paper.pdf", "chunk_index": 0},
            {"document_id": "doc-1", "filename": "paper.pdf", "chunk_index": 1},
        ]],
        "distances": [[0.1, 0.3]],
    }


def test_build_context_labels_each_chunk_with_source():
    context = build_context(_fake_results())

    assert "[Source 1: paper.pdf, chunk 0]" in context
    assert "[Source 2: paper.pdf, chunk 1]" in context
    assert "first chunk text" in context
    assert "second chunk text" in context


def test_build_context_empty_results_returns_empty_string():
    empty = {"documents": [[]], "metadatas": [[]]}
    assert build_context(empty) == ""


def test_build_sources_returns_expected_fields():
    sources = build_sources(_fake_results())

    assert len(sources) == 2
    assert sources[0]["document_id"] == "doc-1"
    assert sources[0]["filename"] == "paper.pdf"
    assert sources[0]["chunk_index"] == 0
    assert sources[0]["content"] == "first chunk text"
    # distance 0.1 -> similarity 0.9
    assert sources[0]["similarity"] == 0.9


def test_build_sources_clamps_similarity_between_zero_and_one():
    results = {
        "documents": [["a chunk"]],
        "metadatas": [[{"filename": "x.pdf", "chunk_index": 0}]],
        "distances": [[5.0]],  # distance > 1 shouldn't produce negative similarity
    }
    sources = build_sources(results)
    assert sources[0]["similarity"] == 0.0
