import logging
from dataclasses import dataclass
from pathlib import Path

import pymupdf

from app.core.chunking import TextChunk, chunk_page_text, normalize_text

logger = logging.getLogger(__name__)


class UnsupportedDocumentError(ValueError):
    pass


class OcrUnavailableError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedDocument:
    page_count: int
    chunks: list[TextChunk]
    ocr_pages: int
    ocr_language: str | None


def get_ocr_runtime(
    requested_language: str = "tur+eng",
    tessdata_path: str | None = None,
) -> tuple[bool, str | None, str | None]:
    """Return OCR availability, usable language string and tessdata path."""
    try:
        tessdata = pymupdf.get_tessdata(tessdata_path or None)
    except Exception:
        return False, None, None

    tessdata_dir = Path(tessdata)
    available = {
        item.stem
        for item in tessdata_dir.glob("*.traineddata")
        if item.is_file()
    }
    requested = [part.strip() for part in requested_language.split("+") if part.strip()]
    selected = [language for language in requested if language in available]

    if not selected:
        if "eng" in available:
            selected = ["eng"]
        else:
            return False, None, str(tessdata_dir)

    return True, "+".join(selected), str(tessdata_dir)


def _ocr_page_text(
    page: pymupdf.Page,
    language: str,
    dpi: int,
    tessdata: str,
) -> str:
    try:
        text_page = page.get_textpage_ocr(
            language=language,
            dpi=dpi,
            full=True,
            tessdata=tessdata,
        )
        return page.get_text("text", textpage=text_page, sort=True)
    except Exception as exc:
        raise OcrUnavailableError(
            "Taranmış PDF algılandı ancak OCR çalıştırılamadı. "
            "Windows'ta `install_ocr_windows.bat` dosyasını çalıştır, "
            "PyCharm'ı yeniden aç ve PDF'yi tekrar indeksle."
        ) from exc


def parse_pdf(
    path: Path,
    chunk_size: int,
    overlap: int,
    *,
    ocr_enabled: bool = True,
    ocr_language: str = "tur+eng",
    ocr_dpi: int = 220,
    ocr_min_chars: int = 30,
    ocr_tessdata_path: str | None = None,
) -> ParsedDocument:
    if path.suffix.lower() != ".pdf":
        raise UnsupportedDocumentError("Bu sürüm yalnızca PDF dosyalarını destekler.")

    chunks: list[TextChunk] = []
    ocr_pages = 0
    runtime_checked = False
    runtime_available = False
    usable_language: str | None = None
    tessdata: str | None = None

    with pymupdf.open(path) as document:
        page_count = document.page_count
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text", sort=True)
            normalized = normalize_text(text)
            has_visual_content = bool(page.get_images(full=True) or page.get_drawings())
            needs_ocr = len(normalized) < ocr_min_chars and has_visual_content

            if needs_ocr and ocr_enabled:
                if not runtime_checked:
                    runtime_available, usable_language, tessdata = get_ocr_runtime(
                        requested_language=ocr_language,
                        tessdata_path=ocr_tessdata_path,
                    )
                    runtime_checked = True

                if not runtime_available or not usable_language or not tessdata:
                    raise OcrUnavailableError(
                        "PDF taranmış görüntüler içeriyor ve bilgisayarda Tesseract OCR bulunamadı. "
                        "`install_ocr_windows.bat` dosyasını çalıştır, PyCharm'ı yeniden aç "
                        "ve PDF'yi tekrar indeksle."
                    )

                logger.info("Running OCR on page %s with %s", page_number, usable_language)
                text = _ocr_page_text(
                    page=page,
                    language=usable_language,
                    dpi=ocr_dpi,
                    tessdata=tessdata,
                )
                if normalize_text(text):
                    ocr_pages += 1

            chunks.extend(
                chunk_page_text(
                    text=text,
                    page=page_number,
                    chunk_size=chunk_size,
                    overlap=overlap,
                )
            )

    return ParsedDocument(
        page_count=page_count,
        chunks=chunks,
        ocr_pages=ocr_pages,
        ocr_language=usable_language if ocr_pages else None,
    )
