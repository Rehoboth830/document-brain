from fastapi import APIRouter
from fastapi.responses import JSONResponse
from backend.core.embeddings.vector_store import get_store_count, clear_store

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns API status and current vector store size.
    """
    count = get_store_count()
    return JSONResponse(content={
        "status": "healthy",
        "service": "Document Brain API",
        "chunks_in_store": count,
        "document_loaded": count > 0
    })


@router.post("/session/clear")
async def clear_session():
    """
    Clear the current document from the vector store.
    Call this before loading a new document.
    """
    clear_store()
    return JSONResponse(content={
        "status": "success",
        "message": "Session cleared. Ready for a new document."
    })
