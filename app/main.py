import logging
import re
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import get_settings
from app.core.document_parser import get_ocr_runtime
from app.core.gemini_client import GeminiGenerationError
from app.core.rag_service import RagService
from app.schemas import (
    AskRequest,
    AskResponse,
    HealthResponse,
    ResetResponse,
    UploadResponse,
)

settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)
rag_service = RagService(settings)

app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description="Source-grounded PDF question-answering API with local retrieval and page-level citations.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def safe_filename(filename: str) -> str:
    base = Path(filename).name
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", base)
    return cleaned or "document.pdf"


def save_upload(uploaded: UploadFile, destination: Path) -> int:
    max_bytes = settings.max_upload_mb * 1024 * 1024
    total = 0
    first_bytes = b""

    with destination.open("wb") as output:
        while True:
            block = uploaded.file.read(1024 * 1024)
            if not block:
                break
            if not first_bytes:
                first_bytes = block[:5]
            total += len(block)
            if total > max_bytes:
                raise ValueError(
                    f"Dosya {settings.max_upload_mb} MB yükleme sınırını aşıyor."
                )
            output.write(block)

    if not first_bytes.startswith(b"%PDF"):
        raise ValueError("Dosya geçerli bir PDF başlığı taşımıyor.")
    return total


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": __version__,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    indexed_chunks = rag_service.vector_store.count_points()
    ocr_available, ocr_language, _ = get_ocr_runtime(
        requested_language=settings.ocr_language,
        tessdata_path=settings.ocr_tessdata_path or None,
    )
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=__version__,
        collection_ready=indexed_chunks > 0,
        indexed_chunks=indexed_chunks,
        gemini_configured=rag_service.gemini.is_configured,
        gemini_model=settings.gemini_model,
        ocr_available=ocr_available,
        ocr_language=ocr_language,
    )


@app.post("/documents/upload", response_model=UploadResponse)
def upload_documents(files: list[UploadFile] = File(...)) -> UploadResponse:
    if not files:
        raise HTTPException(status_code=400, detail="En az bir PDF seçmelisin.")
    if len(files) > settings.max_files_per_upload:
        raise HTTPException(
            status_code=400,
            detail=f"Tek seferde en fazla {settings.max_files_per_upload} PDF yüklenebilir.",
        )

    indexed = []
    total_chunks = 0

    for uploaded in files:
        original_name = uploaded.filename or "document.pdf"
        if Path(original_name).suffix.lower() != ".pdf":
            raise HTTPException(status_code=415, detail=f"Desteklenmeyen dosya: {original_name}")

        stored_name = f"{uuid.uuid4().hex}_{safe_filename(original_name)}"
        destination = settings.upload_path / stored_name

        try:
            size = save_upload(uploaded, destination)
            logger.info("Saved upload %s (%s bytes)", original_name, size)
            result = rag_service.ingest_pdf(destination, original_name)
            indexed.append(result)
            total_chunks += result.chunks
        except ValueError as exc:
            destination.unlink(missing_ok=True)
            raise HTTPException(status_code=422, detail=f"{original_name}: {exc}") from exc
        except Exception as exc:
            destination.unlink(missing_ok=True)
            logger.exception("Document ingestion failed for %s", original_name)
            raise HTTPException(
                status_code=500,
                detail=f"{original_name} işlenirken beklenmeyen bir hata oluştu.",
            ) from exc
        finally:
            uploaded.file.close()

    return UploadResponse(indexed=indexed, total_chunks=total_chunks)


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    try:
        answer, sources, grounded = rag_service.ask(request.question, request.top_k)
        return AskResponse(
            answer=answer,
            sources=sources,
            model=(
                settings.gemini_model
                if rag_service.gemini.is_configured
                else "extractive-fallback"
            ),
            grounded=grounded,
        )
    except GeminiGenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Question answering failed")
        raise HTTPException(
            status_code=500,
            detail="Soru işlenirken beklenmeyen bir hata oluştu.",
        ) from exc


@app.delete("/documents/reset", response_model=ResetResponse)
def reset_documents() -> ResetResponse:
    deleted = rag_service.vector_store.reset()
    deleted_files = 0
    for path in settings.upload_path.glob("*.pdf"):
        path.unlink(missing_ok=True)
        deleted_files += 1
    return ResetResponse(index_deleted=deleted, uploaded_files_deleted=deleted_files)
