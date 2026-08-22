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
            f"[Source {i+1} | {chunk['source']} | Page {chunk['page_number']}]\n{chunk['text']}"
        )
    return "\n\n---\n\n".join(context_parts)


def extract_citations(chunks: list[dict]) -> list[dict]:
    citations = []
    seen = set()
    for chunk in chunks:
        key = f"{chunk['source']}_{chunk['page_number']}"
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
        'summarize', 'summary', 'overview',
        'what is this', 'what is this about', 'what is this document',
        'what is this pdf', 'what is the document about', 'what is the pdf about',
        'what does this document', 'what does this pdf', 'what is it about',
        'tell me about this', 'describe this', 'explain this document',
        'what does this cover', 'what is covered', 'give me an overview',
        'author', 'who wrote', 'who is the author', 'written by',
        'what topics', 'main topics', 'key points', 'main points',
        'what subject', 'subject of this', 'about this'
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


def ask(question: str, session_id: str, n_results: int = 5) -> dict:
    if not session_id:
        return {
            "answer": "No document loaded. Please upload a document first.",
            "citations": [],
            "question": question,
            "confidence": "none"
        }

    summary_mode = is_summary_request(question)
    if summary_mode:
        n_results = 10

    try:
        chunks = retrieve_chunks_pinecone(question, namespace=session_id, n_results=n_results)
    except Exception as e:
        return {
            "answer": "No document loaded. Please upload a document first.",
            "citations": [],
            "question": question,
            "confidence": "none"
        }

    if not chunks:
        return {
            "answer": "No document loaded. Please upload a document first.",
            "citations": [],
            "question": question,
            "confidence": "none"
        }

    avg_similarity = sum(c["similarity"] for c in chunks) / len(chunks)

    threshold = 0.15 if summary_mode else 0.28

    if avg_similarity < threshold:
        return {
            "answer": "I could not find relevant information about this in the provided document. Try rephrasing your question.",
            "citations": [],
            "question": question,
            "confidence": "low"
        }

    context = format_context(chunks)
    citations = extract_citations(chunks)

    llm = get_llm()
    prompt = get_prompt()
    chain = prompt | llm

    try:
        response = chain.invoke({
            "context": context,
            "question": question
        })
        answer = clean_answer(response.content)
    except Exception as e:
        error_msg = str(e).lower()
        if "rate limit" in error_msg or "429" in error_msg:
            answer = "The AI service is temporarily busy due to rate limits. Please wait 30 seconds and try again."
        else:
            answer = f"An error occurred: {str(e)}"

    return {
        "answer": answer,
        "citations": citations,
        "question": question,
        "confidence": "high"
    }
