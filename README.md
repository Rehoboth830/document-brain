# Document Brain

> An intelligent RAG system that reads any document and answers questions about it with source citations.

## What it does
- Upload PDF, Word documents, or paste any URL
- Ask questions in plain English
- Get precise answers with exact source citations
- Supports multiple documents in one session

## Tech Stack
- **LLM**: Groq (llama-3.3-70b) — free and fast
- **RAG**: LangChain + ChromaDB
- **Embeddings**: Sentence Transformers
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Deployment**: Render + Streamlit Cloud

## Architecture
`\
User Question
     │
     ▼
Streamlit UI
     │
     ▼
FastAPI Backend
     │
     ├── Document Ingestion (PDF / Word / URL)
     │
     ├── Embeddings + ChromaDB Vector Store
     │
     └── RAG Chain (Retriever + Groq LLM)
               │
               ▼
         Answer + Citations
`\

## Setup
`\ash
git clone https://github.com/Rehoboth830/document-brain.git
cd document-brain
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
`\

## Status
🚧 Currently in active development
