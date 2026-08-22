import requests
from bs4 import BeautifulSoup
from pathlib import Path


def parse_url(url: str) -> list[dict]:
    """
    Fetch a webpage and extract clean text content.
    Returns a list of dicts with section number and text content.
    """
    if not url.startswith(("http://", "https://")):
        raise ValueError(f"Invalid URL - must start with http:// or https://: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise TimeoutError(f"URL took too long to respond: {url}")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Could not fetch URL: {url} — {str(e)}")

    soup = BeautifulSoup(response.content, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    sections = []
    section_num = 0

    for tag in soup.find_all(["p", "h1", "h2", "h3", "h4", "li"]):
        text = tag.get_text(separator=" ", strip=True)
        if text and len(text) > 30:
            section_num += 1
            sections.append({
                "page_number": section_num,
                "text": text,
                "source": url,
                "source_type": "url"
            })

    if not sections:
        raise ValueError(f"No readable content found at URL: {url}")

    print(f"URL parsed: {url[:60]}... — {len(sections)} sections extracted")
    return sections
