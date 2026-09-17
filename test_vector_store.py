from pathlib import Path

from app.services.document_embedding_service import (
    process_document_embeddings
)

from app.services.vector_store_service import (
    store_document_chunks
)


PDF_PATH = Path("app/data/uploads/base paper.pdf")


# Process PDF
result = process_document_embeddings(PDF_PATH)

chunks = result["chunks"]
embeddings = result["embeddings"]


# Store chunks and embeddings
count = store_document_chunks(
    chunks=chunks,
    embeddings=embeddings,
    filename=PDF_PATH.name
)


print("Chunks stored:", count)
print("Vector store created successfully.")