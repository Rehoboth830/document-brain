from fastapi import FastAPI

app = FastAPI(
    title="Document Brain API",
    description="Intelligent RAG system for document Q&A",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"status": "Document Brain API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}
