import app.services.rag_service as rag_service


def test_answer_question_returns_answer_and_sources(monkeypatch):
    fake_results = {
        "documents": [["SVM and KNN are used for classification."]],
        "metadatas": [[{"document_id": "doc-1", "filename": "paper.pdf", "chunk_index": 0}]],
        "distances": [[0.05]],
    }

    monkeypatch.setattr(rag_service, "search_document", lambda **kwargs: fake_results)
    monkeypatch.setattr(rag_service, "generate_answer", lambda **kwargs: "SVM and KNN are used.")

    result = rag_service.answer_question("What methods are used?")

    assert result["answer"] == "SVM and KNN are used."
    assert len(result["sources"]) == 1
    assert result["sources"][0]["filename"] == "paper.pdf"
    assert "paper.pdf" in result["context"]


def test_answer_question_no_matches_skips_llm_call(monkeypatch):
    empty_results = {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    monkeypatch.setattr(rag_service, "search_document", lambda **kwargs: empty_results)

    def _should_not_be_called(**kwargs):
        raise AssertionError("generate_answer should not be called with no retrieved chunks")

    monkeypatch.setattr(rag_service, "generate_answer", _should_not_be_called)

    result = rag_service.answer_question("Anything about quantum computing?")

    assert result["sources"] == []
    assert "could not find" in result["answer"].lower()


def test_answer_question_below_relevance_threshold_skips_llm(monkeypatch):
    weak_results = {
        "documents": [["totally unrelated text"]],
        "metadatas": [[{"document_id": "doc-1", "filename": "paper.pdf", "chunk_index": 0}]],
        "distances": [[0.95]],  # similarity ~0.05, below the default 0.15 threshold
    }

    monkeypatch.setattr(rag_service, "search_document", lambda **kwargs: weak_results)

    def _should_not_be_called(**kwargs):
        raise AssertionError("generate_answer should not be called below the relevance threshold")

    monkeypatch.setattr(rag_service, "generate_answer", _should_not_be_called)

    result = rag_service.answer_question("What is quantum entanglement?")

    assert "don't appear to contain" in result["answer"]
    # Sources still surfaced for transparency, even though they weren't used
    assert len(result["sources"]) == 1


def test_answer_question_llm_failure_degrades_gracefully(monkeypatch):
    good_results = {
        "documents": [["SVM and KNN are used for classification."]],
        "metadatas": [[{"document_id": "doc-1", "filename": "paper.pdf", "chunk_index": 0}]],
        "distances": [[0.05]],
    }

    monkeypatch.setattr(rag_service, "search_document", lambda **kwargs: good_results)

    def _boom(**kwargs):
        raise RuntimeError("OpenAI is down")

    monkeypatch.setattr(rag_service, "generate_answer", _boom)

    result = rag_service.answer_question("What methods are used?")

    assert "generating an answer failed" in result["answer"]
    assert len(result["sources"]) == 1  # retrieval succeeded even though generation failed


def test_answer_question_passes_document_id_filter_through(monkeypatch):
    captured = {}

    def fake_search(**kwargs):
        captured.update(kwargs)
        return {"documents": [["a chunk"]], "metadatas": [[{"filename": "x.pdf", "chunk_index": 0}]], "distances": [[0.1]]}

    monkeypatch.setattr(rag_service, "search_document", fake_search)
    monkeypatch.setattr(rag_service, "generate_answer", lambda **kwargs: "answer")

    rag_service.answer_question("question", top_k=5, document_id="doc-99")

    assert captured["document_id"] == "doc-99"
    assert captured["top_k"] == 5
