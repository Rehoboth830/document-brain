from pathlib import Path
from backend.core.ingestion.pdf_parser import parse_pdf
from backend.core.ingestion.word_parser import parse_word
from backend.core.ingestion.url_parser import parse_url
from backend.core.ingestion.text_cleaner import clean_pages
from backend.core.ingestion.chunker import chunk_pages


def ingest_document(source: str) -> list[dict]:
    """
    Universal ingestion function.
    Accepts a file path (PDF or Word) or a URL.
    Returns cleaned, chunked text ready for embedding.
    """
    source = source.strip()

    if source.startswith(("http://", "https://")):
        print(f"Source detected: URL")
        raw_pages = parse_url(source)

    else:
        file_path = Path(source)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {source}")

        extension = file_path.suffix.lower()

        if extension == ".pdf":
            print(f"Source detected: PDF")
            raw_pages = parse_pdf(source)

        elif extension in [".docx", ".doc"]:
            print(f"Source detected: Word document")
            raw_pages = parse_word(source)

        else:
            raise ValueError(f"Unsupported file type: {extension}. Use PDF, Word, or URL.")

    cleaned = clean_pages(raw_pages)
    chunks = chunk_pages(cleaned)

    print(f"Ingestion complete: {len(chunks)} chunks ready")
    print(f"Source: {source[:60]}")
    print()

    return chunks
