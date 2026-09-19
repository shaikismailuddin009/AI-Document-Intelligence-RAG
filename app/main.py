import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.documents import router as document_router
from app.api.rag import router as rag_router


app = FastAPI(
    title="AI Document Intelligence & RAG API",
    description="Backend API for document ingestion and question answering",
    version="1.0.0",
)


# Frontend origin(s) allowed to call this API. Comma-separated list via env
# var so it's configurable per environment (dev/staging/prod) without a
# code change. Defaults to the local Vite dev server.
_allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(document_router)
app.include_router(rag_router)


@app.get("/", tags=["Health"], summary="Service info")
def root():
    return {
        "message": "AI Document Intelligence & RAG API is running"
    }


@app.get("/health", tags=["Health"], summary="Health check")
def health():
    return {
        "status": "healthy"
    }
