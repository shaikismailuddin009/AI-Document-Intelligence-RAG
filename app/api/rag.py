from fastapi import APIRouter
from pydantic import BaseModel

from app.services.rag_service import answer_question


router = APIRouter(prefix="/rag", tags=["RAG"])


class QuestionRequest(BaseModel):
    question: str


@router.post("/ask")
def ask_question(request: QuestionRequest):
    result = answer_question(request.question)

    return {
        "question": result["question"],
        "answer": result["answer"],
        "context": result["context"]
    }