import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path

VECTORSTORE_PATH = "data/vectorstore"
COLLECTION_NAME = "document_brain"

_client = None
_collection = None
_ef = None


def get_ef():
    global _ef
    if _ef is None:
        _ef = embedding_functions.DefaultEmbeddingFunction()
    return _ef


def get_client():
    global _client
    if _client is None:
        Path(VECTORSTORE_PATH).mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=VECTORSTORE_PATH)
        print("ChromaDB client initialized")
    return _client


def get_collection():
    global _collection
    if _collection is None:
        client = get_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=get_ef(),
            metadata={"hnsw:space": "cosine"}
        )
        print("Collection ready: " + COLLECTION_NAME)
    return _collection


def store_chunks(chunks: list[dict]) -> int:
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

    batch_size = 50
    stored = 0

    for i in range(0, len(chunks), batch_size):
        collection.upsert(
            ids=ids[i:i+batch_size],
            documents=texts[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size]
        )
        stored += len(ids[i:i+batch_size])
        print(f"Stored {stored}/{len(chunks)} chunks...")

    print(f"Vector store complete: {stored} chunks stored")
    return stored


def get_store_count() -> int:
    collection = get_collection()
    return collection.count()


def clear_store():
    global _client, _collection
    client = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
        print("Vector store cleared")
    except Exception:
        pass
    _collection = None
