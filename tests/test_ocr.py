from pathlib import Path

import pymupdf
import pytest

from app.core.document_parser import get_ocr_runtime, parse_pdf


def _make_scanned_pdf(path: Path) -> None:
    source = pymupdf.open()
    page = source.new_page(width=595, height=842)
    page.insert_text((60, 100), "Scanned document OCR test 2026", fontsize=20)
    pixmap = page.get_pixmap(dpi=180, colorspace=pymupdf.csRGB, alpha=False)

    scanned = pymupdf.open()
    target = scanned.new_page(width=595, height=842)
    target.insert_image(target.rect, pixmap=pixmap)
    scanned.save(path)
    scanned.close()
    source.close()


def test_scanned_pdf_uses_ocr(tmp_path: Path) -> None:
    available, language, _ = get_ocr_runtime("eng")
    if not available:
        pytest.skip("Tesseract OCR is not available")

    pdf = tmp_path / "scanned.pdf"
    _make_scanned_pdf(pdf)
    result = parse_pdf(pdf, chunk_size=500, overlap=50, ocr_language=language or "eng")

    assert result.ocr_pages == 1
    assert result.chunks
    assert "OCR test" in result.chunks[0].text


def test_blank_page_does_not_require_ocr(tmp_path: Path) -> None:
    pdf = tmp_path / "blank.pdf"
    document = pymupdf.open()
    document.new_page()
    document.save(pdf)
    document.close()

    result = parse_pdf(pdf, chunk_size=500, overlap=50, ocr_enabled=True)
    assert result.ocr_pages == 0
    assert result.chunks == []
