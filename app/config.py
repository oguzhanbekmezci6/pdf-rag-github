from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PDF RAG Assistant"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    log_level: str = "INFO"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"

    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_device: str = "cpu"
    embedding_cache_path: Path = Path("data/models")

    qdrant_path: Path = Path("data/qdrant")
    upload_path: Path = Path("data/uploads")
    collection_name: str = "pdf_rag_documents"

    chunk_size: int = 900
    chunk_overlap: int = 150
    retrieval_top_k: int = 5
    minimum_score: float = 0.20

    max_upload_mb: int = 50
    max_files_per_upload: int = 10

    ocr_enabled: bool = True
    ocr_language: str = "tur+eng"
    ocr_dpi: int = 220
    ocr_min_chars: int = 30
    ocr_tessdata_path: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def ensure_directories(self) -> None:
        self.qdrant_path.mkdir(parents=True, exist_ok=True)
        self.upload_path.mkdir(parents=True, exist_ok=True)
        self.embedding_cache_path.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
