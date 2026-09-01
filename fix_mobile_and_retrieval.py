import os

# Fix 1: Mobile responsive page.tsx with hamburger menu
page = '''\
"use client"
import { useState } from "react"
import { useSession } from "@/hooks/useSession"
import { Sidebar } from "@/components/ui/Sidebar"
import { ChatInterface } from "@/components/chat/ChatInterface"
import { motion, AnimatePresence } from "framer-motion"
import { Menu } from "lucide-react"

export default function Home() {
  const { session, setDocumentLoaded, clearDocument } = useSession()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <main className="flex h-screen w-screen overflow-hidden bg-brain-bg">
      <div
        className="absolute inset-0 opacity-30 pointer-events-none"
        style={{ background: "radial-gradient(ellipse at 20% 50%, rgba(74,158,255,0.08) 0%, transparent 60%), radial-gradient(ellipse at 80% 20%, rgba(167,139,250,0.06) 0%, transparent 60%)" }}
      />

      <div className="hidden md:flex">
        <Sidebar session={session} onDocumentLoaded={setDocumentLoaded} onClear={clearDocument} />
      </div>

      <AnimatePresence>
        {sidebarOpen && (
          <>
            <motion.div
              className="fixed inset-0 bg-black/60 z-40 md:hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSidebarOpen(false)}
            />
            <motion.div
              className="fixed left-0 top-0 h-full z-50 md:hidden"
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
            >
              <Sidebar
                session={session}
                onDocumentLoaded={(name, chunks) => { setDocumentLoaded(name, chunks); setSidebarOpen(false) }}
                onClear={() => { clearDocument(); setSidebarOpen(false) }}
              />
            </motion.div>
          </>
        )}
      </AnimatePresence>

      <motion.div
        className="flex-1 flex flex-col min-w-0 min-h-0 overflow-hidden"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <div className="px-4 md:px-6 py-3 md:py-4 border-b border-brain-border glass-strong shrink-0">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3 min-w-0">
              <button
                className="md:hidden p-2 rounded-lg text-brain-muted hover:text-brain-text hover:bg-brain-card transition-colors shrink-0"
                onClick={() => setSidebarOpen(true)}
              >
                <Menu size={18} />
              </button>
              <div className="min-w-0">
                <h1 className="text-sm font-semibold text-brain-text truncate">
                  {session.loaded ? session.name : "Document Brain"}
                </h1>
                <p className="text-xs text-brain-muted truncate">
                  {session.loaded
                    ? session.chunks.toLocaleString() + " chunks indexed"
                    : "Upload a document to begin"}
                </p>
              </div>
            </div>
            {session.loaded && (
              <div className="flex items-center gap-1.5 px-2 md:px-3 py-1.5 rounded-full bg-brain-card border border-brain-border shrink-0">
                <div className="w-1.5 h-1.5 rounded-full bg-brain-success animate-pulse" />
                <span className="text-xs text-brain-muted">Ready</span>
              </div>
            )}
          </div>
        </div>
        <ChatInterface session={session} />
      </motion.div>
    </main>
  )
}
'''

os.makedirs("frontend-react/app", exist_ok=True)
with open("frontend-react/app/page.tsx", "w", encoding="utf-8", newline="\n") as f:
    f.write(page)
print("Written: frontend-react/app/page.tsx - mobile responsive")

# Fix 2: Better retrieval in rag_chain.py
rag_chain = '''\
import re
from backend.core.embeddings.pinecone_store import (
    store_chunks_pinecone,
    retrieve_chunks_pinecone,
    clear_namespace,
    generate_session_id
)
from backend.core.ingestion.ingestion import ingest_document
from backend.core.rag.llm import get_llm
from backend.core.rag.prompt import get_prompt


def format_context(chunks: list[dict]) -> str:
    context_parts = []
    for i, chunk in enumerate(chunks):
        context_parts.append(
            f"[Source {i+1} | {chunk[\'source\']} | Page {chunk[\'page_number\']}]\\n{chunk[\'text\']}"
        )
    return "\\n\\n---\\n\\n".join(context_parts)


def extract_citations(chunks: list[dict]) -> list[dict]:
    citations = []
    seen = set()
    for chunk in chunks:
        key = f"{chunk[\'source\']}_{chunk[\'page_number\']}"
        if key not in seen:
            seen.add(key)
            citations.append({
                "source": chunk["source"],
                "page_number": chunk["page_number"],
                "source_type": chunk["source_type"],
                "similarity": chunk["similarity"]
            })
    return citations


def clean_answer(text: str) -> str:
    if "</think>" in text:
        text = text.split("</think>")[-1]
    text = text.strip()
    return text


def is_summary_request(question: str) -> bool:
    keywords = [
        "summarize", "summary", "overview",
        "what is this", "what is this about", "what is this document",
        "what is this pdf", "what is the document about", "what is the pdf about",
        "what does this document", "what does this pdf", "what is it about",
        "tell me about this", "describe this", "explain this document",
        "what does this cover", "what is covered", "give me an overview",
        "author", "who wrote", "who is the author", "written by",
        "what topics", "main topics", "key points", "main points",
        "what subject", "subject of this", "about this"
    ]
    q = question.lower()
    return any(k in q for k in keywords)


def load_document(source: str, session_id: str = None) -> tuple[int, str]:
    if session_id is None:
        session_id = generate_session_id()
    print(f"Loading document: {source[:60]}")
    print(f"Session ID: {session_id}")
    clear_namespace(session_id)
    chunks = ingest_document(source)
    stored = store_chunks_pinecone(chunks, namespace=session_id)
    print(f"Document loaded: {stored} chunks in Pinecone namespace {session_id}")
    return stored, session_id


def ask(question: str, session_id: str, n_results: int = 8,
        conversation_history: list[dict] = None) -> dict:
    if not session_id:
        return {
            "answer": "No document loaded. Please upload a document first.",
            "citations": [], "question": question, "confidence": "none"
        }

    summary_mode = is_summary_request(question)
    if summary_mode:
        n_results = 12

    try:
        chunks = retrieve_chunks_pinecone(question, namespace=session_id, n_results=n_results)
    except Exception:
        return {
            "answer": "No document loaded. Please upload a document first.",
            "citations": [], "question": question, "confidence": "none"
        }

    if not chunks:
        return {
            "answer": "No document loaded. Please upload a document first.",
            "citations": [], "question": question, "confidence": "none"
        }

    avg_similarity = sum(c["similarity"] for c in chunks) / len(chunks)
    threshold = 0.10 if summary_mode else 0.20

    if avg_similarity < threshold:
        return {
            "answer": "I could not find relevant information about this in the provided document. Try rephrasing your question.",
            "citations": [], "question": question, "confidence": "low"
        }

    context = format_context(chunks)
    citations = extract_citations(chunks)

    history_text = ""
    if conversation_history:
        recent = conversation_history[-4:]
        history_lines = []
        for msg in recent:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_lines.append(f"{role}: {msg[\'content\'][:200]}")
        history_text = "\\n".join(history_lines)

    llm = get_llm()

    if history_text:
        from langchain_core.prompts import ChatPromptTemplate
        prompt_with_history = ChatPromptTemplate.from_template(
            """You are Document Brain - a precise AI assistant that answers questions strictly based on the provided document context.

RULES:
- Answer ONLY using the information in the context below
- If the answer is not in the context, say exactly: "I could not find that information in the provided document."
- Always cite which page your answer comes from
- Be concise and direct
- Never make up information

RECENT CONVERSATION:
{history}

CONTEXT FROM DOCUMENT:
{context}

QUESTION:
{question}

ANSWER (with source citations):"""
        )
        chain = prompt_with_history | llm
    else:
        prompt = get_prompt()
        chain = prompt | llm

    try:
        if history_text:
            response = chain.invoke({"history": history_text, "context": context, "question": question})
        else:
            response = chain.invoke({"context": context, "question": question})
        answer = clean_answer(response.content)
    except Exception as e:
        error_msg = str(e).lower()
        if "rate limit" in error_msg or "429" in error_msg:
            answer = "The AI is temporarily busy. Please wait 30 seconds and try again."
        else:
            answer = f"Error: {str(e)}"

    return {
        "answer": answer,
        "citations": citations,
        "question": question,
        "confidence": "high"
    }
'''

with open("backend/core/rag/rag_chain.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(rag_chain)
print("Written: backend/core/rag/rag_chain.py - better retrieval + conversation history")

# Fix 3: Update query endpoint
query = '''\
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from backend.core.rag.rag_chain import ask

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class QueryRequest(BaseModel):
    question: str
    session_id: str
    n_results: int = 8
    conversation_history: Optional[list[Message]] = None


@router.post("/query")
async def query_document(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    if not request.session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")

    history = None
    if request.conversation_history:
        history = [{"role": m.role, "content": m.content} for m in request.conversation_history]

    try:
        result = ask(
            request.question,
            session_id=request.session_id,
            n_results=request.n_results,
            conversation_history=history
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

    return JSONResponse(content={
        "status": "success",
        "question": result["question"],
        "answer": result["answer"],
        "citations": result["citations"],
        "confidence": result.get("confidence", "high")
    })
'''

with open("backend/api/query.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(query)
print("Written: backend/api/query.py - conversation history support")

print("\nAll fixes applied successfully")
