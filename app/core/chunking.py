import re
from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    text: str
    page: int
    chunk_index: int


def normalize_text(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_page_text(
    text: str,
    page: int,
    chunk_size: int = 900,
    overlap: int = 150,
) -> list[TextChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size pozitif olmalıdır")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap, 0 ile chunk_size arasında olmalıdır")

    clean = normalize_text(text)
    if not clean:
        return []

    chunks: list[TextChunk] = []
    start = 0
    chunk_index = 0

    while start < len(clean):
        hard_end = min(start + chunk_size, len(clean))
        end = hard_end

        if hard_end < len(clean):
            search_start = start + int(chunk_size * 0.60)
            candidates = [
                clean.rfind("\n\n", search_start, hard_end),
                clean.rfind(". ", search_start, hard_end),
                clean.rfind("; ", search_start, hard_end),
            ]
            best = max(candidates)
            if best > start:
                end = best + (2 if clean[best:best + 2] in {". ", "; "} else 0)

        chunk_text = clean[start:end].strip()
        if chunk_text:
            chunks.append(TextChunk(text=chunk_text, page=page, chunk_index=chunk_index))
            chunk_index += 1

        if end >= len(clean):
            break
        start = max(end - overlap, start + 1)

    return chunks
