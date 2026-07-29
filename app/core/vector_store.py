import uuid
from pathlib import Path

from qdrant_client import QdrantClient, models

from app.config import Settings
from app.core.chunking import TextChunk
from app.core.models import RetrievedChunk


class VectorStore:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = QdrantClient(path=str(settings.qdrant_path))

    def collection_exists(self) -> bool:
        return self.client.collection_exists(self.settings.collection_name)

    def count_points(self) -> int:
        if not self.collection_exists():
            return 0
        return int(
            self.client.count(
                collection_name=self.settings.collection_name,
                exact=True,
            ).count
        )

    def ensure_collection(self, vector_size: int) -> None:
        if self.collection_exists():
            return
        self.client.create_collection(
            collection_name=self.settings.collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE,
            ),
        )

    def delete_document(self, filename: str) -> None:
        if not self.collection_exists():
            return
        self.client.delete(
            collection_name=self.settings.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="filename",
                            match=models.MatchValue(value=filename),
                        )
                    ]
                )
            ),
            wait=True,
        )

    def upsert_document(
        self,
        filename: str,
        stored_path: Path,
        chunks: list[TextChunk],
        vectors: list[list[float]],
    ) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("Chunk ve vektör sayıları eşleşmiyor.")
        if not chunks:
            return

        self.ensure_collection(len(vectors[0]))
        self.delete_document(filename)

        points: list[models.PointStruct] = []
        for chunk, vector in zip(chunks, vectors, strict=True):
            stable_key = f"{filename}|{chunk.page}|{chunk.chunk_index}|{chunk.text}"
            point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, stable_key))
            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "filename": filename,
                        "stored_path": str(stored_path),
                        "page": chunk.page,
                        "chunk_index": chunk.chunk_index,
                        "text": chunk.text,
                    },
                )
            )

        self.client.upsert(
            collection_name=self.settings.collection_name,
            points=points,
            wait=True,
        )

    def search(self, query_vector: list[float], top_k: int) -> list[RetrievedChunk]:
        if not self.collection_exists():
            return []

        response = self.client.query_points(
            collection_name=self.settings.collection_name,
            query=query_vector,
            limit=top_k,
            with_payload=True,
        )

        results: list[RetrievedChunk] = []
        for point in response.points:
            payload = point.payload or {}
            results.append(
                RetrievedChunk(
                    filename=str(payload.get("filename", "Bilinmeyen belge")),
                    page=int(payload.get("page", 0)),
                    chunk_index=int(payload.get("chunk_index", 0)),
                    text=str(payload.get("text", "")),
                    score=float(point.score),
                )
            )
        return results

    def reset(self) -> bool:
        if not self.collection_exists():
            return False
        self.client.delete_collection(self.settings.collection_name)
        return True
