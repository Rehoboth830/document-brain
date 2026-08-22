import sys
import os
from backend.core.embeddings.vector_store import store_chunks, clear_store, get_store_count
from backend.core.embeddings.retriever import retrieve_chunks
from backend.core.ingestion.ingestion import ingest_document
from backend.core.rag.llm import get_llm
from backend.core.rag.prompt import get_prompt


def format_context(chunks: list[dict]) -> str:
    """
    Format retrieved chunks into a clean context string for the LLM.
    Each chunk is labelled with its source and page number.
    """
    context_parts = []

    for i, chunk in enumerate(chunks):
        source = chunk["source"]
        page = chunk["page_number"]
        text = chunk["text"]

        context_parts.append(
            f"[Source {i+1} | {source} | Page {page}]\n{text}"
        )

    return "\n\n---\n\n".join(context_parts)


def extract_citations(chunks: list[dict]) -> list[dict]:
    """
    Extract clean citation info from retrieved chunks.
    """
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


def load_document(source: str) -> int:
    """
    Ingest a document and store all chunks in the vector store.
    Returns the number of chunks stored.
    """
    print(f"Loading document: {source[:60]}")
    clear_store()
    chunks = ingest_document(source)
    stored = store_chunks(chunks)
    print(f"Document loaded: {stored} chunks in vector store")
    return stored


def ask(question: str, n_results: int = 5) -> dict:
    """
    The main RAG function.
    Takes a question, retrieves context, generates an answer with citations.
    Returns answer text and citation list.
    """
    if get_store_count() == 0:
        return {
            "answer": "No document loaded. Please upload a document first.",
            "citations": [],
            "question": question
        }

    chunks = retrieve_chunks(question, n_results=n_results)

    context = format_context(chunks)
    citations = extract_citations(chunks)

    llm = get_llm()
    prompt = get_prompt()
    chain = prompt | llm

    response = chain.invoke({
        "context": context,
        "question": question
    })

    answer = response.content

    if "<think>" in answer:
        if "</think>" in answer:
            answer = answer.split("</think>")[-1].strip()

    return {
        "answer": answer,
        "citations": citations,
        "question": question
    }
