import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from backend.core.rag.rag_chain import load_document

router = APIRouter()

UPLOAD_DIR = Path("data/uploads")
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
MAX_FILE_SIZE = 50 * 1024 * 1024


@router.post("/upload/file")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a PDF or Word document.
    Ingests, embeds, and stores it in the vector store.
    """
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}. Use PDF or Word documents."
        )

    save_path = UPLOAD_DIR / file.filename
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 50MB."
        )

    with open(save_path, "wb") as f:
        f.write(content)

    try:
        chunks_stored = load_document(str(save_path))
    except Exception as e:
        os.remove(save_path)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}"
        )

    return JSONResponse(content={
        "status": "success",
        "message": f"Document uploaded and indexed successfully",
        "filename": file.filename,
        "chunks_stored": chunks_stored
    })


@router.post("/upload/url")
async def upload_url(payload: dict):
    """
    Ingest a web URL.
    Scrapes, embeds, and stores it in the vector store.
    """
    url = payload.get("url", "").strip()

    if not url:
        raise HTTPException(status_code=400, detail="URL is required.")

    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL format.")

    try:
        chunks_stored = load_document(url)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process URL: {str(e)}"
        )

    return JSONResponse(content={
        "status": "success",
        "message": "URL ingested and indexed successfully",
        "url": url,
        "chunks_stored": chunks_stored
    })
