from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_pages(pages: list[dict], chunk_size: int = 500, chunk_overlap: int = 50) -> list[dict]:
    """
    Split cleaned pages into overlapping chunks for embedding.
    Each chunk keeps track of its source document and page number.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    all_chunks = []
    chunk_id = 0

    for page in pages:
        raw_chunks = splitter.split_text(page["text"])

        for chunk_text in raw_chunks:
            if chunk_text.strip():
                chunk_id += 1
                all_chunks.append({
                    "chunk_id": chunk_id,
                    "text": chunk_text.strip(),
                    "source": page["source"],
                    "source_type": page["source_type"],
                    "page_number": page["page_number"]
                })

    print(f"Chunking complete: {len(pages)} pages → {len(all_chunks)} chunks")
    return all_chunks
