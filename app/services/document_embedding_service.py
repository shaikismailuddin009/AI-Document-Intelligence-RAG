from pathlib import Path

from app.services.document_service import (
    extract_text_from_pdf,
    clean_text,
    chunk_text
)

from app.services.embedding_service import generate_embeddings


def process_document_embeddings(file_path: Path):
    # 1. Extract text from PDF
    extracted_text = extract_text_from_pdf(file_path)

    # 2. Clean extracted text
    cleaned_text = clean_text(extracted_text)

    # 3. Split text into chunks
    chunks = chunk_text(cleaned_text)

    # 4. Generate embeddings for every chunk
    embeddings = generate_embeddings(chunks)

    return {
        "chunks": chunks,
        "embeddings": embeddings
    }