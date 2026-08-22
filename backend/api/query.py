from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backend.core.rag.rag_chain import ask
from backend.core.embeddings.vector_store import get_store_count

router = APIRouter()


class QueryRequest(BaseModel):
    question: str
    n_results: int = 5


@router.post("/query")
async def query_document(request: QueryRequest):
    """
    Ask a question about the loaded document.
    Returns answer with citations.
    """
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    if get_store_count() == 0:
        raise HTTPException(
            status_code=400,
            detail="No document loaded. Please upload a document first."
        )

    try:
        result = ask(request.question, n_results=request.n_results)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query failed: {str(e)}"
        )

    return JSONResponse(content={
        "status": "success",
        "question": result["question"],
        "answer": result["answer"],
        "citations": result["citations"],
        "confidence": result.get("confidence", "high")
    })
