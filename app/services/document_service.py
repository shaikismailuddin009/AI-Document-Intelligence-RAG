from pathlib import Path
import re

from pypdf import PdfReader


def sanitize_filename(filename: str) -> str:
    """Strip directory components and replace unsafe characters.

    Used to keep the *original* filename (stored as metadata / shown in the
    UI) safe to display and log, even though the file itself is saved on
    disk under its document_id, not this name.
    """
    name = Path(filename).name
    name = re.sub(r"[^A-Za-z0-9._ -]", "_", name)
    return name.strip() or "document.pdf"


def extract_text_from_pdf(file_path: Path) -> str:
    reader = PdfReader(file_path)

    pages_text = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages_text.append(text)

    return "\n".join(pages_text)


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")

    # Replace multiple spaces with one space
    text = re.sub(r"[ \t]+", " ", text)

    # Replace excessive newlines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> list[str]:

    words = text.split()

    if not words:
        return []

    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size")

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size

        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks