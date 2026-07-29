from pathlib import Path


def test_live_ui_uses_general_pdf_branding() -> None:
    ui = Path("ui/streamlit_app.py").read_text(encoding="utf-8")
    assert 'APP_NAME = "PDF RAG Assistant"' in ui
    assert "General-purpose PDF RAG" in ui
    assert "disaster-specific" not in ui.lower()


def test_project_version_is_1_0_0() -> None:
    package = Path("app/__init__.py").read_text(encoding="utf-8")
    assert '__version__ = "1.0.0"' in package
