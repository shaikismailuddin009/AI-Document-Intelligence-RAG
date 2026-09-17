
# AI Document Intelligence & RAG System

An AI-powered document question-answering system that uses **Retrieval-Augmented Generation (RAG)** to allow users to upload PDF documents and ask questions about their content.

The system processes documents, creates semantic embeddings, stores them in a vector database, retrieves relevant document sections, and uses an LLM to generate grounded answers.

---

## 🚀 Project Overview

Traditional document search relies mainly on keyword matching. This project uses semantic search and Retrieval-Augmented Generation to understand the meaning of a user's question and retrieve relevant information from uploaded documents.

### Basic workflow

```text
PDF Document
     │
     ▼
Text Extraction
     │
     ▼
Text Cleaning
     │
     ▼
Text Chunking
     │
     ▼
Embeddings
     │
     ▼
ChromaDB
     │
     │
User Question
     │
     ▼
Question Embedding
     │
     ▼
Semantic Search
     │
     ▼
Relevant Chunks
     │
     ▼
Context
     │
     ▼
LLM
     │
     ▼
Grounded Answer
````

---

## ✨ Features

### Document Processing

* PDF document upload
* PDF text extraction
* Text cleaning
* Text chunking
* Configurable chunk size and overlap

### Semantic Search

* Sentence Transformer embeddings
* `all-MiniLM-L6-v2` embedding model
* 384-dimensional embeddings
* Semantic similarity search
* ChromaDB vector storage

### RAG Pipeline

* Question embedding
* Relevant document retrieval
* Context construction
* LLM-based answer generation
* Context-grounded responses
* Hallucination reduction through context-only prompting

### Backend API

Built with FastAPI.

Current endpoints include:

```text
POST /documents/upload
POST /documents/extract
POST /documents/process
POST /rag/ask
GET  /
GET  /health
```

Interactive API documentation is available through FastAPI Swagger UI.

---

## 🛠️ Technology Stack

### Backend

* Python
* FastAPI
* Pydantic
* Uvicorn

### Document Processing

* pypdf

### AI / Machine Learning

* Sentence Transformers
* `all-MiniLM-L6-v2`
* OpenAI API

### Vector Database

* ChromaDB

### Frontend

* React
* Vite
* TypeScript
* Tailwind CSS

### Testing

* pytest

### Development Tools

* Git
* GitHub
* VS Code

---

## 📁 Project Structure

```text
AI-Document-Intelligence-RAG/
│
├── app/
│   ├── __init__.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── documents.py
│   │   └── rag.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_service.py
│   │   ├── embedding_service.py
│   │   ├── document_embedding_service.py
│   │   ├── search_service.py
│   │   ├── vector_store_service.py
│   │   ├── context_service.py
│   │   └── llm_service.py
│   │
│   ├── data/
│   │   ├── uploads/
│   │   └── chroma/
│   │
│   └── main.py
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
│
├── tests/
│
├── docs/
│
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── ...
```

---

# 🔧 Installation

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-Document-Intelligence-RAG.git
cd AI-Document-Intelligence-RAG
```

---

## 2. Create a Python virtual environment

### Windows

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## 3. Install backend dependencies

```powershell
pip install -r requirements.txt
```

---

## 4. Configure environment variables

Create a `.env` file in the project root.

```env
OPENAI_API_KEY=your_api_key_here
```

### Security

Never commit `.env` to GitHub.

The API key should only be stored locally through environment variables.

Use `.env.example` as a template.

---

# ▶️ Running the Backend

From the project root:

```powershell
.\venv\Scripts\Activate.ps1
```

Start FastAPI:

```powershell
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 🖥️ Running the Frontend

Open a second terminal.

Navigate to the frontend:

```powershell
cd frontend
```

Install dependencies if required:

```powershell
npm install
```

Start the development server:

```powershell
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

# 🧪 Testing the RAG System

## Using Swagger

Open:

```text
http://127.0.0.1:8000/docs
```

Find:

```text
POST /rag/ask
```

Use:

```json
{
  "question": "What machine learning methods are discussed in this paper?"
}
```

The system performs:

```text
Question
   ↓
Embedding
   ↓
Vector Search
   ↓
Relevant Chunks
   ↓
Context
   ↓
LLM
   ↓
Answer
```

---

# 🧠 How RAG Works

Retrieval-Augmented Generation combines information retrieval with large language models.

Instead of asking the LLM to answer only from its general knowledge, this system first retrieves relevant information from the uploaded document.

### Step 1 — Document ingestion

The user uploads a PDF.

### Step 2 — Text extraction

Text is extracted from the PDF using `pypdf`.

### Step 3 — Text cleaning

Unnecessary whitespace and invalid characters are cleaned.

### Step 4 — Chunking

The document is divided into smaller text sections.

### Step 5 — Embeddings

Each chunk is converted into a numerical vector using:

```text
all-MiniLM-L6-v2
```

### Step 6 — Vector storage

The embeddings and document chunks are stored in ChromaDB.

### Step 7 — Question embedding

The user's question is converted into an embedding using the same embedding model.

### Step 8 — Retrieval

ChromaDB searches for the chunks that are semantically closest to the question.

### Step 9 — Context construction

The retrieved chunks are combined into context.

### Step 10 — Generation

The context and question are sent to the LLM.

The LLM generates an answer using the retrieved document information.

---

# 📊 Current Implementation

The current system has successfully implemented and tested:

* PDF processing
* Text extraction
* Text cleaning
* Text chunking
* Sentence Transformer embeddings
* 384-dimensional embeddings
* Semantic similarity search
* ChromaDB vector storage
* Context retrieval
* OpenAI LLM integration
* Basic end-to-end RAG pipeline
* FastAPI `/rag/ask` endpoint
* React/Vite frontend

---

# 🗺️ Development Roadmap

## Phase 1 — Source-Aware Responses

* Return document filename
* Return chunk information
* Display sources used for answers
* Remove unnecessary raw context from user-facing responses

## Phase 2 — RAG Quality Improvements

* Improve retrieval
* Improve prompting
* Handle insufficient context
* Test hallucination/failure cases
* Improve answer formatting

## Phase 3 — Multiple Documents

* Support multiple PDFs
* Unique document IDs
* Document-specific metadata
* Cross-document semantic search

## Phase 4 — Document Management

Implement:

* Upload document
* List documents
* View document information
* Delete document
* Delete corresponding vectors

## Phase 5 — Frontend

Improve the frontend with:

* PDF upload interface
* Document list
* Question interface
* Answer display
* Source display
* Loading states
* Error handling

## Phase 6 — Testing

Add automated tests for:

* PDF extraction
* Text cleaning
* Chunking
* Embeddings
* Vector storage
* Semantic search
* RAG pipeline
* Source attribution
* Multiple documents

## Phase 7 — Docker

* Backend Dockerfile
* Frontend Dockerfile
* Docker Compose
* Environment variable configuration

## Phase 8 — CI/CD

GitHub Actions pipeline:

```text
Push to GitHub
      ↓
Install dependencies
      ↓
Run tests
      ↓
Build application
      ↓
Build Docker image
```

## Phase 9 — Deployment

Prepare the application for cloud deployment.

## Phase 10 — Documentation

* Architecture diagram
* API documentation
* Setup guide
* Testing documentation
* Deployment guide
* Project limitations
* Future improvements

---

# 🔐 Security

The project follows basic security practices:

* API keys are stored in environment variables
* `.env` is excluded from Git
* Secrets are not hard-coded
* Sensitive uploaded documents are excluded from version control
* Dependencies are managed through `requirements.txt`

---

# ⚠️ Current Limitations

The current implementation is a development-stage RAG system.

Potential limitations include:

* PDF extraction quality depends on document structure
* Scanned/image-only PDFs require OCR support
* Retrieval quality depends on chunking and embedding quality
* LLM responses depend on retrieved context
* Large document collections require additional optimization
* Authentication and user-level document isolation are not currently implemented

---

# 🔮 Future Improvements

Possible future improvements include:

* OCR support
* Better document parsing
* Hybrid search
* Reranking
* Conversation memory
* Streaming responses
* Authentication
* User-specific document collections
* Advanced RAG evaluation
* Observability and logging
* Cloud deployment
* Production vector database
* Model and prompt evaluation

---

# 🎯 Learning Objectives

This project demonstrates practical experience with:

* Python
* FastAPI
* REST APIs
* PDF processing
* Natural Language Processing
* Embeddings
* Semantic Search
* Vector Databases
* Retrieval-Augmented Generation
* LLM APIs
* Prompt Engineering
* React
* TypeScript
* Git/GitHub
* Automated Testing
* Docker
* CI/CD
* MLOps concepts

---

# 👨‍💻 Author

**Shaik Ismailuddin**

Computer Science Engineering Student

---

## ⭐ Project Status

**Active Development**

The core RAG pipeline is functional. Additional features including source-aware responses, multi-document support, document management, testing improvements, Docker, CI/CD, and deployment are being developed incrementally.

````

### One important change before pushing

Because your frontend currently shows **“Nexus AI”**, while the GitHub project name is **AI Document Intelligence & RAG System**, I'd keep the README/project name consistent unless you intentionally want **Nexus AI** as the product name.

Also, don't include `base paper.pdf`, your resume, `.env`, Chroma data, `venv`, or `node_modules` in GitHub. Those should remain local/ignored.

After replacing the README, run:

```powershell
cd C:\Users\shaik\AI-Document-Intelligence-RAG
git add README.md
git commit -m "Add project documentation"
git push
````

