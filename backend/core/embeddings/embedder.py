from sentence_transformers import SentenceTransformer
from typing import List

MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def get_model() -> SentenceTransformer:
    """
    Load the embedding model once and reuse it.
    Like hiring one translator and keeping them on staff.
    """
    global _model
    if _model is None:
        print(f"Loading embedding model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
        print(f"Embedding model loaded successfully")
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Convert a list of text strings into embedding vectors.
    Each text becomes a list of 384 floats.
    """
    model = get_model()
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings.tolist()


def embed_query(query: str) -> List[float]:
    """
    Convert a single question into an embedding vector.
    Used at query time to find similar chunks.
    """
    model = get_model()
    embedding = model.encode([query])
    return embedding[0].tolist()
