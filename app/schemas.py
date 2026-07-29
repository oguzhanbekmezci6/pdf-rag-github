from pydantic import BaseModel, Field


class SourceItem(BaseModel):
    source_id: int
    filename: str
    page: int
    chunk_index: int
    score: float
    text: str


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    top_k: int | None = Field(default=None, ge=1, le=10)


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
    model: str
    grounded: bool


class UploadResult(BaseModel):
    filename: str
    pages: int
    chunks: int
    ocr_pages: int = 0
    ocr_language: str | None = None


class UploadResponse(BaseModel):
    indexed: list[UploadResult]
    total_chunks: int


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    collection_ready: bool
    indexed_chunks: int
    gemini_configured: bool
    gemini_model: str
    ocr_available: bool
    ocr_language: str | None = None


class ResetResponse(BaseModel):
    index_deleted: bool
    uploaded_files_deleted: int
