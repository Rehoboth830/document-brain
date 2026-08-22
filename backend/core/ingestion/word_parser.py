from docx import Document
from pathlib import Path


def parse_word(file_path: str) -> list[dict]:
    """
    Read a Word document and extract text paragraph by paragraph.
    Returns a list of dicts with paragraph number and text content.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Word file not found: {file_path}")

    if not file_path.suffix.lower() in [".docx", ".doc"]:
        raise ValueError(f"File is not a Word document: {file_path}")

    doc = Document(str(file_path))

    paragraphs = []
    paragraph_num = 0

    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraph_num += 1
            paragraphs.append({
                "page_number": paragraph_num,
                "text": text,
                "source": file_path.name,
                "source_type": "word"
            })

    if not paragraphs:
        raise ValueError(f"No text found in Word document: {file_path.name}")

    print(f"Word doc parsed: {file_path.name} — {len(paragraphs)} paragraphs extracted")
    return paragraphs
