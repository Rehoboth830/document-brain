import chromadb
from chromadb.config import Settings
from backend.core.embeddings.embedder import embed_texts
from pathlib import Path

VECTORSTORE_PATH = "data/vectorstore"
COLLECTION_NAME = "document_brain"

_client = None
_collection = None


def get_client():
    """
    Get or create the ChromaDB client.
    Persists data to disk so it survives restarts.
    """
    global _client
    if _client is None:
        Path(VECTORSTORE_PATH).mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=VECTORSTORE_PATH)
        print("ChromaDB client initialized")
    return _client


def get_collection():
    """
    Get or create the ChromaDB collection.
    A collection is like a table in a database.
    """
    global _collection
    if _collection is None:
        client = get_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        print("Collection ready: " + COLLECTION_NAME)
    return _collection


def store_chunks(chunks: list[dict]) -> int:
    """
    Embed and store a list of chunks in ChromaDB.
    Returns the number of chunks stored.
    """
    collection = get_collection()

    texts = [chunk["text"] for chunk in chunks]
    ids = [str(chunk["chunk_id"]) for chunk in chunks]
    metadatas = [
        {
            "source": chunk["source"],
            "source_type": chunk["source_type"],
            "page_number": str(chunk["page_number"])
        }
        for chunk in chunks
    ]

    print(f"Embedding {len(chunks)} chunks...")
    embeddings = embed_texts(texts)

    batch_size = 100
    stored = 0

    for i in range(0, len(chunks), batch_size):
        batch_ids = ids[i:i+batch_size]
        batch_texts = texts[i:i+batch_size]
        batch_embeddings = embeddings[i:i+batch_size]
        batch_metadatas = metadatas[i:i+batch_size]

        collection.upsert(
            ids=batch_ids,
            documents=batch_texts,
            embeddings=batch_embeddings,
            metadatas=batch_metadatas
        )
        stored += len(batch_ids)
        print(f"Stored {stored}/{len(chunks)} chunks...")

    print(f"Vector store complete: {stored} chunks stored in ChromaDB")
    return stored


def get_store_count() -> int:
    """
    Return how many chunks are currently in the vector store.
    """
    collection = get_collection()
    return collection.count()


def clear_store():
    """
    Clear all chunks from the vector store.
    Used when a new document session starts.
    """
    global _client, _collection
    client = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
        print("Vector store cleared")
    except Exception:
        pass
    _collection = None
