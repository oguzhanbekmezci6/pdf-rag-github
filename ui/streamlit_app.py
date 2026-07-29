import json
import os

import requests
import streamlit as st

from app import __version__

APP_NAME = "PDF RAG Assistant"
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title=APP_NAME,
    page_icon="📄",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {max-width: 1120px; padding-top: 2rem; padding-bottom: 4rem;}
    .hero {
      padding: 1.6rem 1.8rem; border: 1px solid rgba(128,128,128,.25);
      border-radius: 20px; margin-bottom: 1.5rem;
    }
    .hero h1 {margin: 0 0 .4rem 0; letter-spacing: -.02em;}
    .muted {opacity: .72; line-height: 1.6;}
    .version-badge {
      display: inline-block; margin-top: .8rem; padding: .18rem .55rem;
      border: 1px solid rgba(128,128,128,.25); border-radius: 999px;
      font-size: .78rem; opacity: .72;
    }
    .flow {
      padding: .8rem 1rem; border-radius: 12px;
      background: rgba(128,128,128,.08); margin: .6rem 0 1.2rem;
    }
    div[data-testid="stMetric"] {
      padding: .8rem 1rem; border: 1px solid rgba(128,128,128,.18);
      border-radius: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="hero">
      <h1>{APP_NAME}</h1>
      <div class="muted">
        Metin tabanlı ve taranmış PDF'leri yerel olarak indeksler, gerektiğinde OCR uygular,
        ilgili sayfaları bulur ve Gemini ile kaynak numaralı yanıt üretir. PDF'nin tamamı Gemini'ye gönderilmez.
      </div>
      <div class="version-badge">V{__version__} · General-purpose PDF RAG</div>
    </div>
    """,
    unsafe_allow_html=True,
)


def error_detail(response: requests.Response | None, fallback: str) -> str:
    if response is None:
        return fallback
    try:
        payload = response.json()
        return str(payload.get("detail", payload))
    except (ValueError, AttributeError):
        return response.text or fallback


def api_health() -> dict:
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return {
            "status": "offline",
            "app_name": "-",
            "version": "-",
            "collection_ready": False,
            "indexed_chunks": 0,
            "gemini_configured": False,
            "gemini_model": "-",
            "ocr_available": False,
            "ocr_language": None,
        }


health = api_health()
backend_matches = health.get("app_name") == APP_NAME
online = health.get("status") == "ok" and backend_matches

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(
    "API",
    "Çevrimiçi" if online else ("Eski backend" if health.get("status") == "ok" else "Kapalı"),
)
col2.metric(
    "PDF indeksi",
    "Hazır" if online and health["collection_ready"] else ("Boş" if online else "Bilinmiyor"),
)
col3.metric("İndekslenen parça", health["indexed_chunks"] if online else "-")
col4.metric(
    "Yanıt modeli",
    "Gemini bağlı" if online and health["gemini_configured"] else (
        "Anahtar yok" if online else "Bilinmiyor"
    ),
)
col5.metric(
    "OCR",
    (f"Hazır ({health.get('ocr_language')})" if health.get("ocr_available") else "Kurulu değil")
    if online else "Bilinmiyor",
)

if health.get("status") == "ok" and not backend_matches:
    st.error(
        "Bu arayüz eski bir backend sürecine bağlandı. Açık eski PyCharm/terminal "
        "süreçlerini durdurup bu klasörde `python run_project.py` çalıştır."
    )
elif not online:
    st.error(
        "FastAPI backend'e ulaşılamıyor. Proje klasöründe `python run_project.py` "
        "çalıştır veya `python scripts/doctor.py` ile kurulumu kontrol et."
    )

with st.sidebar:
    st.header("PDF koleksiyonu")
    st.caption("Metin çıkarma, OCR, chunking, embedding ve vektör araması bilgisayarında çalışır.")
    if online and not health.get("ocr_available"):
        st.warning("Taranmış PDF desteği için `install_ocr_windows.bat` dosyasını çalıştır.")
    uploaded_files = st.file_uploader(
        "PDF dosyaları",
        type=["pdf"],
        accept_multiple_files=True,
        help="Metin tabanlı PDF doğrudan işlenir. Taranmış sayfalarda Tesseract OCR otomatik devreye girer.",
        disabled=not online,
    )

    if st.button(
        "PDF'leri indeksle",
        type="primary",
        use_container_width=True,
        disabled=not online,
    ):
        if not uploaded_files:
            st.warning("Önce en az bir PDF seç.")
        else:
            payload = [
                ("files", (item.name, item.getvalue(), "application/pdf"))
                for item in uploaded_files
            ]
            try:
                with st.spinner("PDF metinleri çıkarılıyor, gerekirse OCR uygulanıyor ve vektörler oluşturuluyor..."):
                    response = requests.post(
                        f"{API_URL}/documents/upload",
                        files=payload,
                        timeout=900,
                    )
                    response.raise_for_status()
                result = response.json()
                ocr_pages = sum(item.get("ocr_pages", 0) for item in result["indexed"])
                message = f"{len(result['indexed'])} PDF, {result['total_chunks']} parça indekslendi."
                if ocr_pages:
                    message += f" {ocr_pages} sayfada OCR kullanıldı."
                st.success(message)
                st.rerun()
            except requests.RequestException as exc:
                st.error(f"İndeksleme başarısız: {error_detail(exc.response, str(exc))}")

    st.divider()
    confirm_reset = st.checkbox("Yerel indeks ve yüklenen PDF'leri silmeyi onaylıyorum")
    if st.button(
        "Koleksiyonu temizle",
        use_container_width=True,
        disabled=not online or not confirm_reset,
    ):
        try:
            response = requests.delete(f"{API_URL}/documents/reset", timeout=30)
            response.raise_for_status()
            result = response.json()
            st.success(
                f"Koleksiyon temizlendi; {result['uploaded_files_deleted']} yerel PDF silindi."
            )
            st.rerun()
        except requests.RequestException as exc:
            st.error(f"İşlem başarısız: {error_detail(exc.response, str(exc))}")

    st.divider()
    st.caption(f"API sürümü: {health['version']} · Model: {health['gemini_model']}")

st.subheader("PDF'lerine soru sor")
st.markdown(
    (
        '<div class="flow">Soru → yerel embedding → Qdrant benzerlik araması → '
        'ilgili PDF parçaları → Gemini → sayfa kaynaklı yanıt</div>'
    ),
    unsafe_allow_html=True,
)
question = st.text_area(
    "Soru",
    placeholder=(
        "Örnek: Belgenin ana bulguları nelerdir? / Rapora göre takımın sezon "
        "performansını etkileyen faktörler neler?"
    ),
    height=110,
    disabled=not online,
)

ask_disabled = not online or not health["collection_ready"] or not question.strip()
if st.button("Kaynaklı yanıt üret", type="primary", disabled=ask_disabled):
    try:
        with st.spinner("İlgili PDF parçaları aranıyor ve yanıt oluşturuluyor..."):
            response = requests.post(
                f"{API_URL}/ask",
                json={"question": question.strip()},
                timeout=240,
            )
            response.raise_for_status()
        result = response.json()

        st.markdown("### Yanıt")
        if result["grounded"]:
            st.success(result["answer"])
        else:
            st.warning(result["answer"])

        st.caption(
            f"Yanıt sağlayıcısı: {result['model']} · "
            f"Kaynak sayısı: {len(result['sources'])}"
        )

        export = {
            "question": question.strip(),
            "answer": result["answer"],
            "model": result["model"],
            "sources": result["sources"],
        }
        st.download_button(
            "Yanıtı JSON olarak indir",
            data=json.dumps(export, ensure_ascii=False, indent=2),
            file_name="pdf_rag_answer.json",
            mime="application/json",
        )

        st.markdown("### Getirilen PDF kaynakları")
        if not result["sources"]:
            st.info("Uygun PDF parçası bulunamadı.")
        for source in result["sources"]:
            title = (
                f"[{source['source_id']}] {source['filename']} · "
                f"Sayfa {source['page']} · Benzerlik {source['score']:.3f}"
            )
            with st.expander(title, expanded=source["source_id"] == 1):
                st.write(source["text"])
    except requests.RequestException as exc:
        st.error(f"Yanıt alınamadı: {error_detail(exc.response, str(exc))}")

if online and not health["collection_ready"]:
    st.info("Soru sormadan önce sol menüden en az bir metin tabanlı PDF indeksle.")

st.divider()
st.caption(
    "PDF'ler, OCR işlemi, embedding vektörleri ve Qdrant verisi yerelde tutulur. Yanıt üretimi için "
    "yalnızca soru ve getirilen kaynak parçaları Gemini'ye gönderilir. Gizli belgeler için "
    "üretim ortamı güvenlik ve sağlayıcı politikaları ayrıca değerlendirilmelidir."
)
