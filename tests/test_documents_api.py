import io

import numpy as np
import pytest
from fastapi.testclient import TestClient

import app.services.document_registry_service as registry
import app.api.documents as documents_api
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Isolate the JSON metadata registry to a temp file per test.
    monkeypatch.setattr(registry, "REGISTRY_PATH", tmp_path / "documents.json")

    # Isolate uploaded files to a temp directory.
    monkeypatch.setattr(documents_api, "UPLOAD_DIR", tmp_path / "uploads")
    documents_api.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Avoid loading the real embedding model / touching the real vector store.
    monkeypatch.setattr(
        documents_api, "generate_embeddings",
        lambda chunks: np.random.rand(len(chunks), 8),
    )
    monkeypatch.setattr(
        documents_api, "store_document_chunks",
        lambda **kwargs: len(kwargs["chunks"]),
    )
    monkeypatch.setattr(documents_api, "delete_document_chunks", lambda document_id: None)

    return TestClient(app)


def _minimal_pdf_bytes() -> bytes:
    from pypdf import PdfWriter
    import io as _io

    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buf = _io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_upload_rejects_non_pdf(client):
    response = client.post(
        "/documents/upload",
        files={"file": ("notes.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 400


def test_upload_rejects_empty_file(client):
    response = client.post(
        "/documents/upload",
        files={"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")},
    )
    assert response.status_code == 400


def test_upload_rejects_fake_pdf_with_correct_extension(client):
    # .pdf extension but not actually PDF bytes — should be caught by the
    # magic-byte check, not just the extension check.
    response = client.post(
        "/documents/upload",
        files={"file": ("fake.pdf", io.BytesIO(b"this is not a real pdf"), "application/pdf")},
    )
    assert response.status_code == 400


def test_upload_blank_pdf_has_no_extractable_text_returns_422(client):
    response = client.post(
        "/documents/upload",
        files={"file": ("blank.pdf", io.BytesIO(_minimal_pdf_bytes()), "application/pdf")},
    )
    assert response.status_code == 422


def test_list_documents_starts_empty(client):
    response = client.get("/documents")
    assert response.status_code == 200
    assert response.json() == []


def test_get_nonexistent_document_returns_404(client):
    response = client.get("/documents/does-not-exist")
    assert response.status_code == 404


def test_delete_nonexistent_document_returns_404(client):
    response = client.delete("/documents/does-not-exist")
    assert response.status_code == 404
