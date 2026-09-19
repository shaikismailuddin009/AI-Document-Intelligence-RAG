import os

from app.services.vector_store_service import search_document
from app.services.context_service import build_context, build_sources
from app.services.llm_service import generate_answer

NO_CONTEXT_MESSAGE = (
    "I could not find any relevant information in the uploaded documents."
)

LOW_RELEVANCE_MESSAGE = (
    "The uploaded documents don't appear to contain information relevant "
    "to this question, so I'm not going to guess at an answer."
)

ANSWER_UNAVAILABLE_MESSAGE = (
    "I found relevant document sections, but generating an answer failed. "
    "Please try again in a moment."
)

# Below this cosine similarity, treat the retrieved chunks as "not actually
# relevant" rather than let the LLM stretch to answer from a weak match.
# This is a simple, unvalidated heuristic threshold — not a scientifically
# calibrated cutoff — and is deliberately configurable since the "right"
# value depends on your documents and embedding model.
MIN_RELEVANT_SIMILARITY = float(os.getenv("RAG_MIN_SIMILARITY", "0.15"))


def answer_question(
    question: str,
    top_k: int = 3,
    document_id: str | None = None,
):
    # 1. Retrieve relevant chunks from ChromaDB (optionally scoped to one document)
    results = search_document(
        query=question,
        top_k=top_k,
        document_id=document_id,
    )

    documents = results.get("documents", [[]])[0]

    # No chunks at all (empty collection, or no match for a document filter)
    # short-circuits before calling the LLM.
    if not documents:
        return {
            "question": question,
            "answer": NO_CONTEXT_MESSAGE,
            "context": "",
            "sources": [],
        }

    # 2. Build context + source list from retrieved chunks
    context = build_context(results)
    sources = build_sources(results)

    # 3. If even the best match is weak, don't pretend the documents answer
    # the question — skip the LLM call but still surface what was found so
    # the sources remain inspectable/traceable.
    best_similarity = max((s["similarity"] for s in sources), default=0.0)

    if best_similarity < MIN_RELEVANT_SIMILARITY:
        return {
            "question": question,
            "answer": LOW_RELEVANCE_MESSAGE,
            "context": context,
            "sources": sources,
        }

    # 4. Generate answer using the LLM, grounded only in that context.
    # An LLM/API failure degrades gracefully (sources are still returned)
    # instead of surfacing a raw exception to the caller.
    try:
        answer = generate_answer(
            question=question,
            context=context,
        )
    except Exception:
        answer = ANSWER_UNAVAILABLE_MESSAGE

    return {
        "question": question,
        "answer": answer,
        "context": context,
        "sources": sources,
    }
