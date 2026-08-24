from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backend.core.rag.rag_chain import ask

router = APIRouter()


class QueryRequest(BaseModel):
    question: str
    session_id: str
    n_results: int = 5


@router.post("/query")
async def query_document(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    if not request.session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")

    try:
        result = ask(request.question, session_id=request.session_id, n_results=request.n_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

    return JSONResponse(content={
        "status": "success",
        "question": result["question"],
        "answer": result["answer"],
        "citations": result["citations"],
        "confidence": result.get("confidence", "high")
    })
