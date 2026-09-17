from pathlib import Path

from app.services.document_embedding_service import (
    process_document_embeddings
)

from app.services.search_service import search_similar_chunks


PDF_PATH = Path("app/data/uploads/base paper.pdf")


# Process the PDF
result = process_document_embeddings(PDF_PATH)

chunks = result["chunks"]
embeddings = result["embeddings"]


# Ask a question about the document
query = "What machine learning method is used for skin disease detection?"


# Search for the most relevant chunks
results = search_similar_chunks(
    query=query,
    chunks=chunks,
    embeddings=embeddings,
    top_k=3
)


print("\nQuery:")
print(query)

print("\nTop relevant chunks:\n")


for i, result in enumerate(results, start=1):

    print(f"--- Result {i} ---")
    print("Similarity:", result["similarity"])
    print("Chunk:")
    print(result["chunk"][:1000])
    print()