import re


def clean_text(text: str) -> str:
    """
    Clean raw extracted text by removing noise and normalizing whitespace.
    """
    if not text or not text.strip():
        return ""

    text = re.sub(r'[ \t]+', ' ', text)

    text = re.sub(r'\n{3,}', '\n\n', text)

    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    text = re.sub(r'\s*\n\s*', '\n', text)

    text = text.strip()

    return text


def clean_pages(pages: list[dict]) -> list[dict]:
    """
    Clean text in a list of page/section dicts.
    Removes pages that become empty after cleaning.
    """
    cleaned = []

    for page in pages:
        cleaned_text = clean_text(page["text"])

        if cleaned_text and len(cleaned_text) > 20:
            cleaned.append({
                **page,
                "text": cleaned_text
            })

    print(f"Text cleaned: {len(pages)} pages in — {len(cleaned)} pages out")
    return cleaned
