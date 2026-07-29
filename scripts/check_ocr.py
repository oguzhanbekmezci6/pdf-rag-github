import os
from pathlib import Path

import pymupdf
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def main() -> int:
    configured = os.getenv("OCR_TESSDATA_PATH", "").strip() or None
    try:
        tessdata = Path(pymupdf.get_tessdata(configured))
    except Exception as exc:
        print(f"OCR HAZIR DEĞİL: {exc}")
        print("Windows'ta install_ocr_windows.bat dosyasını çalıştır.")
        return 1

    available = sorted(path.stem for path in tessdata.glob("*.traineddata"))
    selected = [language for language in ("tur", "eng") if language in available]

    print(f"Tessdata: {tessdata}")
    print(f"Dil sayısı: {len(available)}")
    print(f"Türkçe: {'var' if 'tur' in available else 'yok'}")
    print(f"İngilizce: {'var' if 'eng' in available else 'yok'}")
    print(f"Kullanılacak OCR dili: {'+'.join(selected) if selected else 'bulunamadı'}")
    return 0 if selected else 1


if __name__ == "__main__":
    raise SystemExit(main())
