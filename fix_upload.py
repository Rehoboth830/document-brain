content = '''\
import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from backend.core.rag.rag_chain import load_document

router = APIRouter()

UPLOAD_DIR = Path("data/uploads")
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
MAX_FILE_SIZE = 50 * 1024 * 1024


@router.post("/upload/file")
async def upload_file(
    file: UploadFile = File(...),
    session_id: str = Form(None)
):
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {extension}")

    save_path = UPLOAD_DIR / file.filename
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB.")

    with open(save_path, "wb") as f:
        f.write(content)

    try:
        chunks_stored, used_session = load_document(str(save_path), session_id=session_id)
    except Exception as e:
        os.remove(save_path)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

    return JSONResponse(content={
        "status": "success",
        "message": "Document uploaded and indexed successfully",
        "filename": file.filename,
        "chunks_stored": chunks_stored,
        "session_id": used_session
    })


@router.post("/upload/url")
async def upload_url(payload: dict):
    url = payload.get("url", "").strip()
    session_id = payload.get("session_id")

    if not url:
        raise HTTPException(status_code=400, detail="URL is required.")
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL format.")

    try:
        chunks_stored, used_session = load_document(url, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process URL: {str(e)}")

    return JSONResponse(content={
        "status": "success",
        "message": "URL ingested and indexed successfully",
        "url": url,
        "chunks_stored": chunks_stored,
        "session_id": used_session
    })
'''

with open("backend/api/upload.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
print("upload.py fixed - session_id now Form field")
