from app.services.document_service import (
    extract_text_from_pdf,
    clean_text,
    chunk_text
) 
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

UPLOAD_DIR = Path("app/data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    filename = file.filename

    if not filename or not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    file_path = UPLOAD_DIR / filename

    contents = await file.read()

    with open(file_path, "wb") as f:
        f.write(contents)

    return {
        "message": "Document uploaded successfully",
        "filename": filename
    }
@router.post("/extract")
async def extract_document_text(file: UploadFile = File(...)):

    filename = file.filename

    if not filename or not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    file_path = UPLOAD_DIR / filename

    contents = await file.read()

    with open(file_path, "wb") as f:
        f.write(contents)

    text = extract_text_from_pdf(file_path)

    return {
        "filename": filename,
        "text": text
    }
@router.post("/process")
async def process_document(file: UploadFile = File(...)):

    filename = file.filename

    if not filename or not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    file_path = UPLOAD_DIR / filename

    contents = await file.read()

    with open(file_path, "wb") as f:
        f.write(contents)

    extracted_text = extract_text_from_pdf(file_path)

    cleaned_text = clean_text(extracted_text)

    chunks = chunk_text(cleaned_text)

    return {
        "filename": filename,
        "character_count": len(cleaned_text),
        "chunk_count": len(chunks),
        "chunks": chunks
    }