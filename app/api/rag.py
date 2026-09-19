from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.rag_service import answer_question
from app.services import document_registry_service as registry


router = APIRouter(prefix="/rag", tags=["RAG"])


class QuestionRequest(BaseModel):
    question: str = Field(
        ..., min_length=1, max_length=2000,
        description="The question to ask. Whitespace-only questions are rejected.",
        examples=["What machine learning methods are discussed in this paper?"],
    )
    top_k: int = Field(
        default=3, ge=1, le=10,
        description="Number of chunks to retrieve (1-10).",
    )
    document_id: Optional[str] = Field(
        default=None,
        description="Restrict retrieval to a single document. Omit or set null to search all documents.",
    )


class SourceItem(BaseModel):
    document_id: Optional[str] = None
    filename: str
    chunk_index: Optional[int]
    similarity: float = Field(description="Cosine similarity in [0, 1], higher is more relevant.")
    content: str


class AnswerResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceItem]


@router.post(
    "/ask",
    response_model=AnswerResponse,
    summary="Ask a question about uploaded documents",
    description=(
        "Retrieves the most relevant chunks (optionally scoped to one document "
        "via document_id), builds grounded context, and asks the LLM to answer "
        "using only that context. If nothing relevant is found, the answer says "
        "so instead of guessing."
    ),
    responses={
        400: {"description": "Empty/whitespace-only question"},
        404: {"description": "document_id does not match any known document"},
        500: {"description": "Retrieval or generation failed unexpectedly"},
    },
)
def ask_question(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if request.document_id and not registry.get_document(request.document_id):
        raise HTTPException(status_code=404, detail="document_id does not match any known document")

    try:
        result = answer_question(
            question=question,
            top_k=request.top_k,
            document_id=request.document_id,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate an answer. Please try again.",
        ) from exc

    return AnswerResponse(
        question=result["question"],
        answer=result["answer"],
        sources=result["sources"],
    )
