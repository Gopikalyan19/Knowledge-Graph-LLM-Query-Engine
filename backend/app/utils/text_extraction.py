from pathlib import Path
from PyPDF2 import PdfReader


def extract_text_from_file(path: str) -> str:
    file_path = Path(path)
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(str(file_path))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        return "\n".join(pages).strip()

    if suffix in [".txt", ".md"]:
        return file_path.read_text(encoding="utf-8", errors="ignore").strip()

    raise ValueError("Only PDF, TXT, and MD files are supported")


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = max(end - overlap, end) if end >= len(text) else end - overlap
    return chunks
