# AI Document Intelligence & RAG System

An AI-powered document question-answering system built with **Retrieval-Augmented Generation (RAG)**. Upload PDF documents, ask questions about them in natural language, and get answers grounded in the actual document content — with the exact source chunks cited alongside every answer.

---

## Overview

Traditional document search relies on keyword matching. This project uses semantic search to understand the *meaning* of a question and retrieve the most relevant sections of a document, then passes that context to an LLM so answers are grounded in the source material instead of the model's general knowledge — and are explicitly labelled as unanswerable when the document doesn't cover the question.

### Problem statement

Reading long PDFs to find one specific answer is slow. This system lets you upload a document once and then ask it questions directly, with every answer traceable back to the exact chunk of text it came from.

---

## Features

**Document processing**
- PDF upload, text extraction, cleaning, and chunking (configurable size/overlap)
- Multiple documents, each with a generated unique ID, upload time, processing status, and chunk count
- Document management: list, view, delete (deletion removes both the file and its vectors)

**Semantic search & retrieval**
- `all-MiniLM-L6-v2` sentence-transformer embeddings (384-dimensional)
- ChromaDB persistent vector store
- Configurable `top_k`, optional per-document filtering (ask about one document or search across all of them)

**RAG pipeline**
- Question → embedding → similarity search → context construction → LLM generation
- Answers are grounded only in retrieved context; the system explicitly says so when nothing relevant is found, instead of guessing
- Every answer includes its sources: filename, chunk index, an approximate similarity score, and the chunk content itself

**Frontend**
- React + TypeScript + Vite + Tailwind CSS
- Upload, document library, question interface, answer + expandable sources
- Loading states, empty states, and real error messages (no mock data)

---

## Architecture

```text
frontend/ (React + Vite)
      │  REST (fetch, centralized API client)
      ▼
app/main.py (FastAPI, CORS)
      │
      ├── api/documents.py  → document_service, embedding_service, vector_store_service, document_registry_service
      └── api/rag.py        → rag_service → vector_store_service, context_service, llm_service
```

### RAG workflow

```text
PDF Document
     │
     ▼
Text Extraction (pypdf) → Cleaning → Chunking
     │
     ▼
Embeddings (all-MiniLM-L6-v2, 384-dim)
     │
     ▼
ChromaDB  (tagged with document_id, filename, chunk_index)

User Question
     │
     ▼
Question Embedding → ChromaDB similarity search (optionally scoped to one document)
     │
     ▼
Relevant Chunks → Context (labelled per source) → LLM
     │
     ▼
Grounded Answer + Sources
```

---

## Technology stack

| Layer | Tech |
|---|---|
| Backend | Python, FastAPI, Pydantic, Uvicorn |
| Document processing | pypdf |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Vector database | ChromaDB |
| LLM | OpenAI API |
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| Testing | pytest |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |

---

## Project structure

```text
AI-Document-Intelligence-RAG/
│
├── app/
│   ├── api/
│   │   ├── documents.py         # upload / list / get / delete / extract
│   │   └── rag.py               # /rag/ask
│   ├── services/
│   │   ├── document_service.py            # extract, clean, chunk, sanitize filename
│   │   ├── embedding_service.py           # sentence-transformer embeddings
│   │   ├── document_embedding_service.py  # extract+clean+chunk+embed in one call
│   │   ├── document_registry_service.py   # JSON-backed document metadata store
│   │   ├── search_service.py              # legacy in-memory cosine search (see note below)
│   │   ├── vector_store_service.py        # ChromaDB storage/search/delete
│   │   ├── context_service.py             # build_context, build_sources
│   │   ├── llm_service.py                 # OpenAI call, grounded prompt
│   │   └── rag_service.py                 # ties retrieval → context → LLM together
│   ├── data/
│   │   ├── uploads/             # stored PDFs (git-ignored)
│   │   ├── chroma/              # vector store (git-ignored)
│   │   └── documents.json       # document metadata (git-ignored)
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── api/client.ts        # centralized fetch wrapper, single source of the backend URL
│   │   ├── components/          # UploadPanel, DocumentList, AskPanel, SourceList, StatusBadge
│   │   ├── types/                # shared TS types matching backend response shapes
│   │   └── App.tsx
│   └── package.json
│
├── tests/                       # pytest suite (services + API, mocked embedding/LLM calls)
├── scripts/evaluate_rag.py      # small retrieval evaluation script
├── .github/workflows/ci.yml
├── Dockerfile / docker-compose.yml / frontend/Dockerfile
├── .env.example
└── requirements.txt
```

> **Note on `search_service.py`:** this is an earlier in-memory cosine-similarity search that predates the ChromaDB integration. The live `/rag/ask` path uses `vector_store_service.search_document` (ChromaDB), not this module. It's kept because `test_search.py` still exercises it, but it isn't part of the production retrieval path.

---

## Installation

### 1. Clone

```bash
git clone https://github.com/YOUR_USERNAME/AI-Document-Intelligence-RAG.git
cd AI-Document-Intelligence-RAG
```

### 2. Backend setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Environment variables

```bash
cp .env.example .env
```

Then fill in your own `OPENAI_API_KEY` in `.env`. Never commit `.env` — only `.env.example` (placeholders only) is tracked.

### 4. Run the backend

```powershell
uvicorn app.main:app --reload
```

- API: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`

### 5. Frontend setup

```bash
cd frontend
cp .env.example .env   # set VITE_API_BASE_URL if the backend isn't on the default
npm install
npm run dev
```

Frontend: `http://localhost:5173`

---

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/documents/upload` | Upload a PDF; extracts, chunks, embeds, and stores it in one call |
| `GET` | `/documents` | List all documents and their status |
| `GET` | `/documents/{document_id}` | Get one document's metadata |
| `DELETE` | `/documents/{document_id}` | Delete a document's file and its vector chunks |
| `POST` | `/documents/extract` | Preview-only: extract raw text without storing anything |
| `POST` | `/rag/ask` | Ask a question, optionally scoped to one document |

Interactive request/response docs, with descriptions and error responses for every route, are auto-generated at `/docs` (Swagger) and `/redoc`.

### Example: `POST /rag/ask`

Request:
```json
{
  "question": "What machine learning methods are discussed in this paper?",
  "top_k": 3,
  "document_id": null
}
```

Response:
```json
{
  "question": "What machine learning methods are discussed in this paper?",
  "answer": "The paper discusses SVM, KNN, and Decision Tree classifiers...",
  "sources": [
    {
      "document_id": "3c4410e3-8e60-4bf1-91ee-af087b9cae02",
      "filename": "base paper.pdf",
      "chunk_index": 4,
      "similarity": 0.83,
      "content": "Support Vector Machine (SVM), K-Nearest Neighbors..."
    }
  ]
}
```

- `document_id: null` (or omitted) searches across all uploaded documents; pass a specific `document_id` to scope the question to one document — an unknown `document_id` returns `404`.
- An empty/whitespace-only `question` returns `400`; `top_k` outside `1–10` returns `422` (Pydantic validation).
- If the best-matching chunk's similarity is below `RAG_MIN_SIMILARITY` (default `0.15`, see `.env.example`), the system returns "the documents don't appear to contain information relevant to this question" instead of asking the LLM to guess — the retrieved sources are still returned so you can see what was (weakly) matched.
- If the LLM call itself fails (e.g. OpenAI outage), the endpoint still returns `200` with the retrieved sources and a message saying generation failed, rather than a raw `500` — retrieval succeeding shouldn't be thrown away because generation didn't.
- `similarity` is `1 − cosine distance`, and is exact (not approximate) because the ChromaDB collection is explicitly configured with `hnsw:space: "cosine"` in `vector_store_service.py`.

---

## Testing

```bash
pytest -v
```

The suite covers:
- `document_service`: extraction, cleaning, chunking, filename sanitization, edge cases (empty text, invalid chunk params, blank PDFs)
- `embedding_service`: embedding generation and dimensionality
- `context_service`: source-labelled context building, source-list construction (including `document_id`)
- `vector_store_service`: storing, filtering by `document_id` (document isolation — one document's chunks never leak into another's search results), deleting — against an isolated in-memory Chroma collection, never the real data
- `rag_service`: retrieval → context → answer wiring, the "no relevant chunks" short-circuit, the relevance-threshold short-circuit, and graceful degradation when the LLM call raises — all with the LLM mocked
- `llm_service`: prompt construction, with the OpenAI client mocked (no API key or network call needed)
- API layer (`/documents/*`, `/rag/ask`, `/health`): validation, error handling, 404s (including an unknown `document_id` on `/rag/ask`), the PDF magic-byte check — via FastAPI's `TestClient`

No test requires a real `OPENAI_API_KEY` or hits the real OpenAI API — the LLM client is mocked wherever it's exercised.

---

## RAG evaluation

```bash
python scripts/evaluate_rag.py
```

Runs a small set of sample questions (`scripts/eval_dataset.json`) against the currently-indexed documents, checks whether the **retrieved chunks** contain the expected keywords (retrieval recall), and — unless `--skip-answers` is passed — also calls the real LLM and checks whether the **generated answer** mentions them (answer recall).

```bash
python scripts/evaluate_rag.py --skip-answers   # retrieval only, no OPENAI_API_KEY / network needed
```

**Limitations:** both metrics are keyword-presence heuristics — a smoke test, not a validated benchmark. Keyword presence in an answer doesn't mean the answer is factually correct, well-formed, or fully responsive to the question. The shipped dataset entries are illustrative placeholders; replace them with real questions and keywords from your own documents before drawing conclusions from the numbers.

---

## Docker

```bash
docker compose up --build
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

Chroma data and uploads persist in named volumes (`chroma_data`, `uploads_data`) so they survive container restarts. The backend reads `OPENAI_API_KEY` from `.env` via `env_file` — the key is never baked into the image. The backend image has a `HEALTHCHECK` against `/health` (60s start period, since first startup also loads the embedding model).

---

## CI/CD

`.github/workflows/ci.yml` runs on every push/PR to `main`:
1. Backend: install dependencies, run `pytest` (with a dummy `OPENAI_API_KEY` — no real key or network call needed, since the LLM client is mocked in tests)
2. Frontend: install dependencies, run `npm run build`

The workflow fails if either step fails.

---

## Security

- `OPENAI_API_KEY` is read from environment variables only, never hard-coded
- `.env` is git-ignored; `.env.example` ships placeholders only
- Uploaded files are stored under a generated `document_id`, not the user-supplied filename, and filenames are sanitized before being stored as metadata — closes a path-traversal / overwrite risk in the original filename-as-path design
- `app/data/uploads/`, `app/data/chroma/`, and `app/data/documents.json` are git-ignored (previously, compiled `.pyc` files, the Chroma binary store, and the sample PDF were accidentally committed — cleaned up)
- Errors return a generic message to the client; details go to server-side exceptions, not the response body
- Uploads are checked against both file extension and PDF magic bytes (`%PDF-`), not extension alone — catches a renamed non-PDF file
- The RAG endpoint doesn't fabricate answers for low-relevance retrieval (see `RAG_MIN_SIMILARITY`), and an LLM failure degrades to a clear message instead of leaking an exception

---

## Limitations

- PDF extraction quality depends on document structure; scanned/image-only PDFs need OCR (not implemented)
- Document metadata is stored in a single JSON file — fine for a portfolio project, not a concurrent-write-safe production database
- The "similarity" score (`1 − cosine distance`) is exact given the collection's cosine configuration, but it's a raw embedding-space distance, not a calibrated confidence value — a 0.4 doesn't mean "40% likely correct"
- `RAG_MIN_SIMILARITY` (default `0.15`) is an unvalidated heuristic threshold, not a scientifically calibrated cutoff — tune it for your own documents/embedding model
- No authentication / user-level document isolation — all documents are visible to anyone who can reach the API
- The RAG evaluation script is a keyword heuristic, not a rigorous benchmark
- Large document collections have not been load-tested

## Future improvements

- OCR for scanned PDFs
- Hybrid search (keyword + semantic) and reranking
- Conversation memory / multi-turn follow-up questions
- Streaming answers
- Authentication and per-user document scoping
- A real database for document metadata instead of a JSON file
- Structured RAG evaluation with a larger, labelled question set

---

## Interview discussion points

- Why chunking with overlap matters for retrieval quality, and the size/overlap trade-off
- Why chunk metadata (document_id, filename, chunk_index) is threaded through storage → retrieval → context → API response to make answers citable
- Why the OpenAI client is lazily instantiated (importability without a key, testability without mocking module-level state)
- The trade-off in storing document metadata as JSON vs. a real database
- Why filenames are sanitized and files are stored under a generated ID rather than the original filename

---

## Author

**Shaik Ismailuddin** — B.Tech Computer Science Engineering

---

## Project status

Core RAG pipeline, multi-document support, source-aware answers, document management, a React frontend, automated tests, Docker, and CI/CD are implemented. See **Limitations** and **Future improvements** above for what's intentionally left out of this iteration.
