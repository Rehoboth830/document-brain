import fitz
from pathlib import Path


def parse_pdf(file_path: str) -> list[dict]:
    """
    Read a PDF file and extract text page by page.
    Returns a list of dicts with page number and text content.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    if not file_path.suffix.lower() == ".pdf":
        raise ValueError(f"File is not a PDF: {file_path}")

    pages = []

    doc = fitz.open(str(file_path))

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()

        if text.strip():
            pages.append({
                "page_number": page_num + 1,
                "text": text,
                "source": file_path.name,
                "source_type": "pdf"
            })

    doc.close()

    if not pages:
        raise ValueError(f"No text found in PDF: {file_path.name}")

    print(f"PDF parsed: {file_path.name} — {len(pages)} pages extracted")
    return pages
