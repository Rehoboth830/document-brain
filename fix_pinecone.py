content = '''import os
import uuid
from pinecone import Pinecone, ServerlessSpec
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = "document-brain"
DIMENSION = 384
METRIC = "cosine"

_pc = None
_index = None
_ef = None


def get_ef():
    global _ef
    if _ef is None:
        _ef = embedding_functions.DefaultEmbeddingFunction()
    return _ef


def get_client():
    global _pc
    if _pc is None:
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY not found in .env file.")
        _pc = Pinecone(api_key=api_key)
        print("Pinecone client initialized")
    return _pc


def get_index():
    global _index
    if _index is None:
        pc = get_client()
        existing = [i.name for i in pc.list_indexes()]
        if INDEX_NAME not in existing:
            print(f"Creating Pinecone index: {INDEX_NAME}")
            pc.create_index(
                name=INDEX_NAME,
                dimension=DIMENSION,
                metric=METRIC,
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            print("Index created successfully")
        _index = pc.Index(INDEX_NAME)
        print(f"Connected to Pinecone index: {INDEX_NAME}")
    return _index


def to_list(embedding):
    """Convert numpy array or any array-like to plain Python list."""
    if hasattr(embedding, "tolist"):
        return embedding.tolist()
    return list(embedding)


def store_chunks_pinecone(chunks: list[dict], namespace: str) -> int:
    index = get_index()
    ef = get_ef()

    texts = [chunk["text"] for chunk in chunks]
    print(f"Embedding {len(chunks)} chunks for namespace: {namespace}")
    embeddings = ef(texts)

    batch_size = 100
    stored = 0

    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i+batch_size]
        batch_embeddings = embeddings[i:i+batch_size]

        vectors = []
        for chunk, embedding in zip(batch_chunks, batch_embeddings):
            vectors.append({
                "id": f"{namespace}_{chunk[\'chunk_id\']}",
                "values": to_list(embedding),
                "metadata": {
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "source_type": chunk["source_type"],
                    "page_number": str(chunk["page_number"])
                }
            })

        index.upsert(vectors=vectors, namespace=namespace)
        stored += len(vectors)
        print(f"Stored {stored}/{len(chunks)} chunks...")

    print(f"Pinecone store complete: {stored} chunks in namespace {namespace}")
    return stored


def retrieve_chunks_pinecone(query: str, namespace: str, n_results: int = 5) -> list[dict]:
    index = get_index()
    ef = get_ef()

    print(f"Retrieving top {n_results} chunks from namespace: {namespace}")
    query_embedding = to_list(ef([query])[0])

    results = index.query(
        vector=query_embedding,
        top_k=n_results,
        namespace=namespace,
        include_metadata=True
    )

    chunks = []
    for i, match in enumerate(results.matches):
        chunks.append({
            "rank": i + 1,
            "text": match.metadata.get("text", ""),
            "source": match.metadata.get("source", ""),
            "source_type": match.metadata.get("source_type", ""),
            "page_number": match.metadata.get("page_number", "?"),
            "similarity": round(match.score, 4)
        })

    print(f"Retrieved {len(chunks)} chunks")
    return chunks


def get_namespace_count(namespace: str) -> int:
    try:
        index = get_index()
        stats = index.describe_index_stats()
        ns_stats = stats.namespaces.get(namespace)
        if ns_stats:
            return ns_stats.vector_count
        return 0
    except Exception:
        return 0


def clear_namespace(namespace: str):
    try:
        index = get_index()
        index.delete(delete_all=True, namespace=namespace)
        print(f"Namespace cleared: {namespace}")
    except Exception:
        pass


def generate_session_id() -> str:
    return str(uuid.uuid4())[:8]
'''

with open("backend/core/embeddings/pinecone_store.py", "w", encoding="utf-8") as f:
    f.write(content)
print("pinecone_store.py fixed - ndarray conversion added")
