from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievedChunk:
    filename: str
    page: int
    chunk_index: int
    text: str
    score: float
