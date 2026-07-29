from __future__ import annotations

import argparse
import os
import sys
from importlib import import_module
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

REQUIRED_IMPORTS = {
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "streamlit": "streamlit",
    "qdrant-client": "qdrant_client",
    "sentence-transformers": "sentence_transformers",
    "PyMuPDF": "pymupdf",
    "google-genai": "google.genai",
}


def package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "kurulu değil"


def main() -> int:
    parser = argparse.ArgumentParser(description="PDF RAG Assistant kurulum denetimi")
    parser.add_argument(
        "--gemini",
        action="store_true",
        help="Gemini API anahtarıyla gerçek bir test isteği gönderir.",
    )
    args = parser.parse_args()

    failures: list[str] = []
    print(f"Python: {sys.executable}")
    print(f"Sürüm: {sys.version.split()[0]}")
    if sys.version_info < (3, 10):
        failures.append("Python 3.10 veya daha yeni bir sürüm gerekli.")

    print("\nPaket kontrolleri:")
    for package, module in REQUIRED_IMPORTS.items():
        try:
            import_module(module)
            print(f"  OK  {package} {package_version(package)}")
        except Exception as exc:
            print(f"  HATA {package}: {exc}")
            failures.append(f"{package} içe aktarılamadı")

    try:
        legacy_google = version("google")
    except PackageNotFoundError:
        legacy_google = ""
    if legacy_google:
        failures.append(
            "'google' adlı çakışan paket kurulu. `python -m pip uninstall -y google` çalıştır."
        )

    env_path = ROOT / ".env"
    key = os.getenv("GEMINI_API_KEY", "").strip()
    print("\nYapılandırma:")
    print(f"  .env: {'var' if env_path.exists() else 'yok'}")
    key_status = "tanımlı" if key and key != "your_api_key_here" else "tanımlı değil"
    print(f"  GEMINI_API_KEY: {key_status}")
    print(f"  GEMINI_MODEL: {os.getenv('GEMINI_MODEL', 'gemini-3.6-flash')}")

    print("\nOCR:")
    try:
        import pymupdf

        tessdata = Path(pymupdf.get_tessdata(os.getenv("OCR_TESSDATA_PATH") or None))
        languages = {path.stem for path in tessdata.glob("*.traineddata")}
        requested = [
            part.strip()
            for part in os.getenv("OCR_LANGUAGE", "tur+eng").split("+")
            if part.strip()
        ]
        usable = [language for language in requested if language in languages]
        print(f"  Tesseract tessdata: {tessdata}")
        print(f"  Kullanılabilir dil: {'+'.join(usable) if usable else 'yok'}")
        if not usable:
            print("  UYARI: İstenen OCR dil dosyaları bulunamadı; taranmış PDF'ler işlenemez.")
    except Exception as exc:
        print(f"  UYARI: {exc}")
        print("  Taranmış PDF desteği için install_ocr_windows.bat dosyasını çalıştır.")

    if args.gemini:
        if not key or key == "your_api_key_here":
            failures.append("Gemini testi için geçerli GEMINI_API_KEY gerekli.")
        else:
            try:
                from google import genai

                client = genai.Client(api_key=key)
                response = client.models.generate_content(
                    model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
                    contents="Sadece OK yaz.",
                )
                print(f"  Gemini testi: {(response.text or '').strip()}")
            except Exception as exc:
                failures.append(f"Gemini testi başarısız: {exc}")

    if failures:
        print("\nSONUÇ: Düzeltme gerekli")
        for item in failures:
            print(f"  - {item}")
        return 1

    print("\nSONUÇ: Kurulum hazır")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
