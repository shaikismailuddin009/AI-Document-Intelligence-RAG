from fastapi import FastAPI
from app.api.documents import router as document_router
from app.api.rag import router as rag_router


app = FastAPI(
    title="AI Document Intelligence & RAG API",
    description="Backend API for document ingestion and question answering",
    version="1.0.0"
)


app.include_router(document_router)
app.include_router(rag_router)


@app.get("/")
def root():
    return {
        "message": "AI Document Intelligence & RAG API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }