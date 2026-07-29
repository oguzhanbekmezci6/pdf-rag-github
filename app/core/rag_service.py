import logging
from pathlib import Path

from app.config import Settings
from app.core.document_parser import parse_pdf
from app.core.embeddings import embed_documents, embed_query
from app.core.gemini_client import GeminiClient
from app.core.models import RetrievedChunk
from app.core.prompting import NO_EVIDENCE_MESSAGE, build_grounded_prompt
from app.core.vector_store import VectorStore
from app.schemas import SourceItem, UploadResult

logger = logging.getLogger(__name__)


class RagService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.vector_store = VectorStore(settings)
        self.gemini = GeminiClient(settings)

    def ingest_pdf(self, file_path: Path, original_filename: str) -> UploadResult:
        parsed = parse_pdf(
            file_path,
            chunk_size=self.settings.chunk_size,
            overlap=self.settings.chunk_overlap,
            ocr_enabled=self.settings.ocr_enabled,
            ocr_language=self.settings.ocr_language,
            ocr_dpi=self.settings.ocr_dpi,
            ocr_min_chars=self.settings.ocr_min_chars,
            ocr_tessdata_path=self.settings.ocr_tessdata_path or None,
        )
        if not parsed.chunks:
            raise ValueError(
                "PDF'den metin çıkarılamadı. Sayfalar boş, çok düşük kaliteli veya desteklenmeyen biçimde olabilir."
            )

        logger.info("Embedding %s chunks from %s", len(parsed.chunks), original_filename)
        vectors = embed_documents([chunk.text for chunk in parsed.chunks])
        self.vector_store.upsert_document(
            filename=original_filename,
            stored_path=file_path,
            chunks=parsed.chunks,
            vectors=vectors,
        )
        return UploadResult(
            filename=original_filename,
            pages=parsed.page_count,
            chunks=len(parsed.chunks),
            ocr_pages=parsed.ocr_pages,
            ocr_language=parsed.ocr_language,
        )

    def ask(self, question: str, top_k: int | None = None) -> tuple[str, list[SourceItem], bool]:
        limit = top_k or self.settings.retrieval_top_k
        query_vector = embed_query(question)
        retrieved = self.vector_store.search(query_vector=query_vector, top_k=limit)
        useful = [item for item in retrieved if item.score >= self.settings.minimum_score]

        sources = self._to_source_items(useful)
        if not useful:
            return NO_EVIDENCE_MESSAGE, sources, False

        prompt = build_grounded_prompt(question, useful)
        answer = self.gemini.generate(prompt)
        return answer, sources, True

    @staticmethod
    def _to_source_items(items: list[RetrievedChunk]) -> list[SourceItem]:
        return [
            SourceItem(
                source_id=index,
                filename=item.filename,
                page=item.page,
                chunk_index=item.chunk_index,
                score=round(item.score, 4),
                text=item.text,
            )
            for index, item in enumerate(items, start=1)
        ]
