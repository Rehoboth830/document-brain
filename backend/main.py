from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.api.upload import router as upload_router
from backend.api.query import router as query_router
from backend.api.session import router as session_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Warming up embedding model...")
    from backend.core.embeddings.pinecone_store import get_ef
    get_ef()
    print("Embedding model ready")
    yield


app = FastAPI(
    title="Document Brain API",
    description="Intelligent RAG system - ask questions about any document with AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api/v1", tags=["Upload"])
app.include_router(query_router, prefix="/api/v1", tags=["Query"])
app.include_router(session_router, prefix="/api/v1", tags=["Session"])


@app.get("/")
async def root():
    return {
        "service": "Document Brain API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }
