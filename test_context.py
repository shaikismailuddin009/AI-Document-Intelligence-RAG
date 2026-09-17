from app.services.vector_store_service import search_document
from app.services.context_service import build_context


query = "What machine learning methods are discussed in this paper?"


results = search_document(
    query=query,
    top_k=3
)


context = build_context(results)


print("\nQUESTION:")
print(query)

print("\n" + "=" * 60)
print("RETRIEVED CONTEXT")
print("=" * 60)

print(context)