from backend.core.embeddings.vector_store import get_collection


def retrieve_chunks(query: str, n_results: int = 5) -> list[dict]:
    collection = get_collection()

    total_chunks = collection.count()
    if total_chunks == 0:
        raise ValueError("No documents in vector store. Please upload a document first.")

    n_results = min(n_results, total_chunks)
    print(f"Retrieving top {n_results} chunks for query: {query[:60]}...")

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
        similarity = round(1 - dist, 4)
        chunks.append({
            "rank": i + 1,
            "text": doc,
            "source": meta["source"],
            "source_type": meta["source_type"],
            "page_number": meta["page_number"],
            "similarity": similarity
        })

    print(f"Retrieved {len(chunks)} relevant chunks")
    return chunks
