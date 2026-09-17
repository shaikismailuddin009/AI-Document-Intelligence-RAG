from app.services.vector_store_service import search_document
from app.services.context_service import build_context
from app.services.llm_service import generate_answer


def answer_question(question: str, top_k: int = 3):
    # 1. Retrieve relevant chunks from ChromaDB
    results = search_document(
        query=question,
        top_k=top_k
    )

    # 2. Build context from retrieved chunks
    context = build_context(results)

    # 3. Generate answer using the LLM
    answer = generate_answer(
        question=question,
        context=context
    )

    return {
        "question": question,
        "answer": answer,
        "context": context
    }