import pytest
from fastapi.testclient import TestClient

import app.api.rag as rag_api
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_ask_question_happy_path(client, monkeypatch):
    monkeypatch.setattr(
        rag_api, "answer_question",
        lambda **kwargs: {
            "question": kwargs["question"],
            "answer": "SVM and KNN are used.",
            "context": "...",
            "sources": [
                {"filename": "paper.pdf", "chunk_index": 0, "similarity": 0.91, "content": "SVM and KNN..."}
            ],
        },
    )

    response = client.post("/rag/ask", json={"question": "What methods are used?"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "SVM and KNN are used."
    assert body["sources"][0]["filename"] == "paper.pdf"


def test_ask_question_rejects_empty_question(client):
    response = client.post("/rag/ask", json={"question": ""})
    assert response.status_code in (400, 422)


def test_ask_question_rejects_whitespace_only_question(client, monkeypatch):
    monkeypatch.setattr(
        rag_api, "answer_question",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("should not be called")),
    )
    response = client.post("/rag/ask", json={"question": "   "})
    assert response.status_code == 400


def test_ask_question_service_failure_returns_500(client, monkeypatch):
    def _boom(**kwargs):
        raise RuntimeError("chroma is down")

    monkeypatch.setattr(rag_api, "answer_question", _boom)

    response = client.post("/rag/ask", json={"question": "anything?"})
    assert response.status_code == 500


def test_ask_question_invalid_document_id_returns_404(client, monkeypatch):
    monkeypatch.setattr(rag_api.registry, "get_document", lambda document_id: None)

    def _should_not_be_called(**kwargs):
        raise AssertionError("answer_question should not run for an invalid document_id")

    monkeypatch.setattr(rag_api, "answer_question", _should_not_be_called)

    response = client.post("/rag/ask", json={"question": "hi", "document_id": "does-not-exist"})
    assert response.status_code == 404


def test_ask_question_valid_document_id_proceeds(client, monkeypatch):
    monkeypatch.setattr(rag_api.registry, "get_document", lambda document_id: {"document_id": document_id})
    monkeypatch.setattr(
        rag_api, "answer_question",
        lambda **kwargs: {"question": kwargs["question"], "answer": "ok", "context": "", "sources": []},
    )

    response = client.post("/rag/ask", json={"question": "hi", "document_id": "doc-1"})
    assert response.status_code == 200


def test_ask_question_rejects_top_k_out_of_range(client):
    response = client.post("/rag/ask", json={"question": "hi", "top_k": 50})
    assert response.status_code == 422
