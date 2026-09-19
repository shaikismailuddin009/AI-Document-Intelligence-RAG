from pathlib import Path
from typing import Literal, Optional

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.services.document_service import (
    extract_text_from_pdf,
    clean_text,
    chunk_text,
    sanitize_filename,
)
from app.services.embedding_service import generate_embeddings
from app.services.vector_store_service import (
    store_document_chunks,
    delete_document_chunks,
)
from app.services import document_registry_service as registry


router = APIRouter(prefix="/documents", tags=["Documents"])


class DocumentRecord(BaseModel):
    document_id: str
    filename: str
    upload_time: str
    status: Literal["uploaded", "processing", "processed", "failed"]
    chunk_count: int
    error: Optional[str] = None


class DeleteResponse(BaseModel):
    message: str
    document_id: str

UPLOAD_DIR = Path("app/data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


def _validate_pdf(file: UploadFile) -> None:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported",
        )


def _validate_pdf_contents(contents: bytes) -> None:
    # Extension checks alone trust the client-supplied filename. A quick
    # magic-byte check catches a renamed non-PDF file without needing a
    # full parse.
    if not contents.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="File does not appear to be a valid PDF",
        )


@router.post(
    "/upload",
    response_model=DocumentRecord,
    summary="Upload and process a PDF",
    description=(
        "Extracts, cleans, chunks, embeds, and stores a PDF in one call. "
        "Returns the document's metadata record, including its generated "
        "document_id and final processing status."
    ),
    responses={
        400: {"description": "Not a PDF, empty file, or over the 20MB limit"},
        422: {"description": "PDF has no extractable text (e.g. scanned/image-only)"},
        500: {"description": "Processing failed unexpectedly"},
    },
)
async def upload_document(file: UploadFile = File(...)):

    _validate_pdf(file)

    contents = await file.read()

    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail="File exceeds the 20MB size limit",
        )

    _validate_pdf_contents(contents)

    original_filename = sanitize_filename(file.filename)
    record = registry.create_document(original_filename)
    document_id = record["document_id"]

    # Store on disk under the document_id, never the original filename —
    # avoids collisions and path-unsafe names entirely.
    stored_path = UPLOAD_DIR / f"{document_id}.pdf"

    with open(stored_path, "wb") as f:
        f.write(contents)

    registry.update_document(document_id, status="processing")

    try:
        extracted_text = extract_text_from_pdf(stored_path)
        cleaned_text = clean_text(extracted_text)
        chunks = chunk_text(cleaned_text)

        if not chunks:
            registry.update_document(
                document_id,
                status="failed",
                error="No extractable text found in this PDF",
            )
            raise HTTPException(
                status_code=422,
                detail="No extractable text found in this PDF (it may be scanned/image-only)",
            )

        embeddings = generate_embeddings(chunks)

        store_document_chunks(
            chunks=chunks,
            embeddings=embeddings,
            document_id=document_id,
            filename=original_filename,
        )

        record = registry.update_document(
            document_id,
            status="processed",
            chunk_count=len(chunks),
        )

    except HTTPException:
        raise
    except Exception as exc:
        registry.update_document(document_id, status="failed", error=str(exc))
        raise HTTPException(
            status_code=500,
            detail="Failed to process document",
        ) from exc

    return record


@router.get(
    "",
    response_model=list[DocumentRecord],
    summary="List all documents",
    description="Returns every uploaded document's metadata, most recently uploaded first.",
)
def list_documents():
    return registry.list_documents()


@router.get(
    "/{document_id}",
    response_model=DocumentRecord,
    summary="Get one document's metadata",
    responses={404: {"description": "No document with this ID"}},
)
def get_document(document_id: str):
    record = registry.get_document(document_id)

    if not record:
        raise HTTPException(status_code=404, detail="Document not found")

    return record


@router.delete(
    "/{document_id}",
    response_model=DeleteResponse,
    summary="Delete a document",
    description="Removes the document's file, its vector chunks, and its metadata. Does not affect other documents.",
    responses={404: {"description": "No document with this ID"}},
)
def delete_document(document_id: str):
    record = registry.get_document(document_id)

    if not record:
        raise HTTPException(status_code=404, detail="Document not found")

    delete_document_chunks(document_id)

    stored_path = UPLOAD_DIR / f"{document_id}.pdf"
    if stored_path.exists():
        stored_path.unlink()

    registry.delete_document(document_id)

    return {"message": "Document deleted", "document_id": document_id}


@router.post(
    "/extract",
    summary="Preview PDF text extraction (no storage)",
    description=(
        "Extracts raw text from a PDF without chunking, embedding, or "
        "storing it — useful for inspecting a file before committing it "
        "via /documents/upload."
    ),
    responses={400: {"description": "Not a PDF or empty file"}},
)
async def extract_document_text(file: UploadFile = File(...)):

    _validate_pdf(file)

    contents = await file.read()

    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    _validate_pdf_contents(contents)

    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(contents)
        tmp_path = Path(tmp.name)

    try:
        text = extract_text_from_pdf(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    return {
        "filename": sanitize_filename(file.filename),
        "text": text,
    }
