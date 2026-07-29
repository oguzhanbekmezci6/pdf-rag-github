import pytest

from app.core.chunking import chunk_page_text, normalize_text


def test_normalize_text_removes_excess_whitespace() -> None:
    assert normalize_text("Merhaba   dünya\n\n\nTest") == "Merhaba dünya\n\nTest"


def test_chunking_preserves_page_and_sequence() -> None:
    text = " ".join([f"Cümle {index}." for index in range(100)])
    chunks = chunk_page_text(text, page=7, chunk_size=220, overlap=40)

    assert len(chunks) > 1
    assert all(chunk.page == 7 for chunk in chunks)
    assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))
    assert all(chunk.text for chunk in chunks)


def test_empty_text_returns_no_chunks() -> None:
    assert chunk_page_text("   \n\n", page=1) == []


def test_invalid_overlap_raises() -> None:
    with pytest.raises(ValueError):
        chunk_page_text("örnek", page=1, chunk_size=100, overlap=100)
