from app.services.vector_store_service import search_document


query = "What machine learning method is used for skin disease detection?"


results = search_document(
    query=query,
    top_k=3
)


print("\nQuery:")
print(query)

print("\nTop relevant chunks:\n")


documents = results["documents"][0]
distances = results["distances"][0]
metadatas = results["metadatas"][0]


for i, (document, distance, metadata) in enumerate(
    zip(documents, distances, metadatas),
    start=1
):

    print(f"--- Result {i} ---")
    print("Distance:", distance)
    print("Metadata:", metadata)
    print("Chunk:")
    print(document[:1000])
    print()