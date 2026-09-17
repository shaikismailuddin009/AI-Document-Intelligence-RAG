from pathlib import Path

from app.services.document_embedding_service import (
    process_document_embeddings
)


PDF_PATH = Path("app/data/uploads/base paper.pdf")


result = process_document_embeddings(PDF_PATH)

chunks = result["chunks"]
embeddings = result["embeddings"]


print("Number of chunks:", len(chunks))
print("Number of embeddings:", len(embeddings))
print("Embedding dimensions:", embeddings.shape[1])


print("\nFirst chunk:")
print(chunks[0][:500])


print("\nFirst embedding:")
print(embeddings[0][:10])