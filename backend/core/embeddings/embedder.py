from chromadb.utils import embedding_functions

_ef = None


def get_embedding_function():
    """
    Get ChromaDB default embedding function.
    Uses all-MiniLM-L6-v2 but managed by ChromaDB directly.
    Much more memory efficient than loading SentenceTransformer manually.
    """
    global _ef
    if _ef is None:
        _ef = embedding_functions.DefaultEmbeddingFunction()
        print("Embedding function initialized")
    return _ef


def embed_texts(texts: list[str]) -> list[list[float]]:
    ef = get_embedding_function()
    embeddings = ef(texts)
    return embeddings


def embed_query(query: str) -> list[float]:
    ef = get_embedding_function()
    embeddings = ef([query])
    return embeddings[0]
