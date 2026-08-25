content = """\
# Document Brain

> **Production-grade RAG system** — Ask questions about any document with AI-powered source citations.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-documentbrain.vercel.app-4a9eff?style=for-the-badge&logo=vercel)](https://documentbrain.vercel.app)
[![Backend](https://img.shields.io/badge/API-Railway-purple?style=for-the-badge&logo=railway)](https://document-brain-api-production-c9a2.up.railway.app/api/v1/health)
[![GitHub](https://img.shields.io/badge/GitHub-Rehoboth830-black?style=for-the-badge&logo=github)](https://github.com/Rehoboth830/document-brain)

---

## What It Does

Document Brain is a production-grade **Retrieval Augmented Generation (RAG)** system that reads any document and answers questions about it with precise, page-level source citations.

- Upload a **PDF**, **Word document**, or paste any **URL**
- Ask questions in plain English
- Get precise answers with **exact page citations** and relevance scores
- Every user gets an **isolated session** — your documents stay private
- Documents **persist across sessions** via Pinecone cloud vector storage

---

## Live Demo

**[documentbrain.vercel.app](https://documentbrain.vercel.app)**

---

## Architecture

```
User Question
     │
     ▼
React/Next.js Frontend (Vercel)
     │
     ▼
FastAPI Backend (Railway) ──── No cold starts, always on
     │
     ├── Document Ingestion
     │   ├── PDF Parser (PyMuPDF)
     │   ├── Word Parser (python-docx)
     │   └── URL Scraper (BeautifulSoup)
     │
     ├── Text Processing
     │   ├── Cleaner
     │   └── Chunker (500-word overlapping chunks)
     │
     ├── Embeddings (ChromaDB default — all-MiniLM-L6-v2)
     │
     └── Vector Store (Pinecone Cloud)
          │
          └── Similarity Search
               │
               ▼
          RAG Chain (LangChain)
               │
               ▼
          LLM (Groq — Qwen 3.6 27B)
               │
               ▼
     Answer + Page Citations
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Framer Motion |
| Backend | FastAPI, Python 3.13, LangChain |
| Vector Store | Pinecone (cloud-hosted, persistent) |
| LLM | Groq API — Qwen 3.6 27B |
| Embeddings | all-MiniLM-L6-v2 (384 dimensions) |
| Frontend Deployment | Vercel |
| Backend Deployment | Railway (always-on, no cold starts) |

---

## Key Engineering Decisions

**Why Pinecone over ChromaDB?**
ChromaDB persists to disk — which gets wiped on cloud restarts. Pinecone is cloud-hosted, so vectors survive server restarts and app redeployments. Each user's documents are stored in isolated namespaces.

**Why Groq over OpenAI?**
Groq's inference is significantly faster and free-tier friendly. Qwen 3.6 27B provides strong reasoning capabilities with extended context windows for complex documents.

**Why Railway over Render?**
Render's free tier sleeps after 15 minutes of inactivity — causing 60-second cold starts that break the user experience. Railway's always-on hosting eliminates this entirely.

**Session Architecture**
Each browser session generates a unique ID stored in localStorage. This ID is used as a Pinecone namespace — completely isolating each user's document vectors. Sessions persist across browser refreshes without requiring re-upload.

---

## Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API key (free at console.groq.com)
- Pinecone API key (free at pinecone.io)

### Backend

```bash
git clone https://github.com/Rehoboth830/document-brain.git
cd document-brain

python -m venv venv
venv\\Scripts\\activate  # Windows
# source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
```

Create `.env` in the project root:
```
GROQ_API_KEY=your_groq_key_here
PINECONE_API_KEY=your_pinecone_key_here
```

Start the backend:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 --reload-dir backend
```

### Frontend

```bash
cd frontend-react
npm install
```

Create `frontend-react/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

Start the frontend:
```bash
npm run dev
```

Open `http://localhost:3000`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/upload/file` | Upload PDF or Word document |
| `POST` | `/api/v1/upload/url` | Ingest a web URL |
| `POST` | `/api/v1/query` | Ask a question about the loaded document |
| `POST` | `/api/v1/session/clear` | Clear the current session |
| `GET` | `/api/v1/health` | Health check |

### Example Query

```bash
curl -X POST https://document-brain-api-production-c9a2.up.railway.app/api/v1/query \\
  -H "Content-Type: application/json" \\
  -d '{"question": "What is this document about?", "session_id": "your_session_id"}'
```

---

## Project Structure

```
document-brain/
├── backend/
│   ├── api/
│   │   ├── upload.py        # File & URL upload endpoints
│   │   ├── query.py         # Question answering endpoint
│   │   └── session.py       # Session management
│   └── core/
│       ├── ingestion/
│       │   ├── pdf_parser.py
│       │   ├── word_parser.py
│       │   ├── url_parser.py
│       │   ├── text_cleaner.py
│       │   ├── chunker.py
│       │   └── ingestion.py  # Unified ingestion pipeline
│       ├── embeddings/
│       │   ├── embedder.py
│       │   ├── pinecone_store.py
│       │   └── retriever.py
│       └── rag/
│           ├── llm.py
│           ├── prompt.py
│           └── rag_chain.py
├── frontend-react/           # Next.js 14 React frontend
│   ├── app/
│   ├── components/
│   │   ├── chat/
│   │   ├── ui/
│   │   └── upload/
│   ├── hooks/
│   ├── lib/
│   └── types/
├── streamlit_app.py          # Streamlit fallback UI
└── requirements.txt
```

---

## Built By

**Akinde Olugbenga Tope**

IBM AI Engineering Professional Certificate | IBM Generative AI Engineering | IBM Data Science | AI Automation Engineer with n8n | Prompt Engineering (Vanderbilt University)

[![GitHub](https://img.shields.io/badge/GitHub-Rehoboth830-black?logo=github)](https://github.com/Rehoboth830)
"""

with open("README.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
print("README.md written successfully")
