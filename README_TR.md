# PDF RAG Assistant — Türkçe

PDF RAG Assistant; metin tabanlı ve taranmış PDF dosyalarını indeksleyen, soruyla ilgili sayfaları yerel vektör aramasıyla bulan ve yalnızca seçilen kaynak parçalarını Gemini'ye göndererek kaynaklı yanıt üreten genel amaçlı bir RAG projesidir.

Bu projeyi, istatistik mezunu olarak yalnızca model geliştirmeyi değil; belge işleme, OCR, embedding, vektör veritabanı, API, arayüz, test ve güvenlik gibi uçtan uca bir yapay zekâ uygulamasının parçalarını öğrenmek için geliştirdim.

> Az sayıda kişisel PDF için belgeleri doğrudan ChatGPT veya Gemini'ye yüklemek daha kolay olabilir. Bu proje ise tekrar kullanılabilir indeksleme, yerel retrieval, sayfa seviyesinde kaynak takibi ve başka uygulamalara bağlanabilecek bir API geliştirmeye odaklanır.

## Sistem nasıl çalışıyor?

```text
PDF yükleme
→ PyMuPDF ile sayfa metni çıkarma
→ metin yoksa Tesseract OCR
→ metni parçalara ayırma
→ yerel embedding oluşturma
→ Qdrant'a kaydetme
→ soruyu embedding'e dönüştürme
→ en ilgili parçaları bulma
→ soru + kaynak parçalarını Gemini'ye gönderme
→ dosya ve sayfa bilgili yanıt
```

PDF'nin tamamı ve sayısal embedding vektörleri Gemini'ye gönderilmez. Yalnızca kullanıcı sorusu ile retrieval katmanının seçtiği sınırlı metin parçaları gönderilir.

## Temel özellikler

- Birden fazla PDF yükleme ve kalıcı indeksleme
- PyMuPDF ile sayfa bazlı metin çıkarma
- Taranmış sayfalarda otomatik Tesseract OCR
- Türkçe ve İngilizce OCR
- Sentence Transformers ile yerel embedding
- Qdrant Local vektör veritabanı
- Benzerlik skoru ve top-k ayarlı semantic search
- Gemini ile kaynak numaralı yanıt
- Dosya adı, sayfa, chunk, skor ve kaynak metni gösterimi
- FastAPI backend ve OpenAPI dokümantasyonu
- Streamlit arayüz
- JSON yanıt indirme
- Windows kurulum ve OCR betikleri
- Docker, testler, CI ve Dependabot
- `.env`, yüklenen PDF ve yerel vektör verilerinin Git dışında tutulması

## Windows kurulumu

```powershell
git clone https://github.com/oguzhanbekmezci6/pdf-rag-assistant.git
cd pdf-rag-assistant
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env` dosyasına Gemini anahtarını yaz:

```env
GEMINI_API_KEY=GERCEK_ANAHTARIN
GEMINI_MODEL=gemini-3.6-flash
```

Taranmış PDF desteği için:

```powershell
.\install_ocr_windows.bat
python scripts\check_ocr.py
```

OCR kurulumundan sonra PyCharm'ı kapatıp yeniden aç. Ardından:

```powershell
python run_project.py
```

## İlk kullanım

1. Sol menüden bir veya daha fazla PDF seç.
2. **PDF'leri indeksle** düğmesine bas.
3. PDF'lerin içeriğiyle ilgili bir soru sor.
4. Yanıtın altındaki dosya, sayfa, benzerlik skoru ve kaynak metinlerini incele.

Akademik makale, futbol raporu, mahkeme kararı, ders notu, finansal rapor, teknik kılavuz, yönetmelik ve benzeri metin tabanlı PDF'ler kullanılabilir.

## Test ve kalite kontrolü

```powershell
python scripts\doctor.py
python scripts\doctor.py --gemini
python -m pip install -r requirements-dev.txt
ruff check .
pytest
python -m compileall -q app ui scripts run_project.py
```

## Öğrendiklerim

- RAG mimarisini çalışan bir uygulamaya dönüştürme
- Retrieval ile generation görevlerini ayırma
- Sayfa bilgisini koruyarak kaynak gösterme
- Normal PDF metni ile OCR çıktısını aynı pipeline'a alma
- FastAPI ve Streamlit'i ayrı katmanlar olarak çalıştırma
- Qdrant ile yerel vektör verisi yönetme
- Windows üzerinde SDK, port, süreç ve OCR yolu sorunlarını teşhis etme
- Yapay zekâ projesinde test, CI, gizlilik ve sınırlamaları belgeleme

## Mevcut sınırlar

- Yalnızca dense semantic search vardır; BM25 hybrid search henüz yoktur.
- Cross-encoder reranker bulunmaz.
- Tek ortak koleksiyon kullanılır; kullanıcı veya çalışma alanı ayrımı yoktur.
- Kimlik doğrulama, şifreli depolama ve üretim seviyesi rate limiting yoktur.
- Karmaşık tablolar ve çok sütunlu sayfalar yapı kaybedebilir.
- OCR başarısı tarama kalitesine bağlıdır.

Daha fazla teknik ayrıntı için [README.md](README.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) ve [docs/TROUBLESHOOTING_TR.md](docs/TROUBLESHOOTING_TR.md) dosyalarını inceleyebilirsin.
