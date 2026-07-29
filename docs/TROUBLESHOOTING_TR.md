# Sorun Giderme

## `PDF'den metin çıkarılamadı`

PDF taranmış görüntülerden oluşuyor olabilir. `install_ocr_windows.bat` dosyasını çalıştır, PyCharm'ı tamamen kapatıp yeniden aç ve şu komutlarla OCR durumunu kontrol et:

```powershell
python scripts\check_ocr.py
python scripts\doctor.py
```

## Dil sayısı `0` görünüyor

`data/tessdata` klasöründe şu iki dosyanın bulunduğunu kontrol et:

```text
tur.traineddata
eng.traineddata
```

Kontrol komutu:

```powershell
Get-ChildItem .\data\tessdata
```

`.env` içinde özel bir yol kullanıyorsan ileri eğik çizgiyle yaz:

```env
OCR_TESSDATA_PATH=C:/Users/KULLANICI/Desktop/pdf-rag-assistant/data/tessdata
OCR_LANGUAGE=tur+eng
```

`C:\...\data\tessdata` biçimindeki `\t` bazı okuma yöntemlerinde tab karakterine dönüşebilir.

## Türkçe karakterler yanlış okunuyor

`tessdata` klasöründe `tur.traineddata` bulunduğundan ve `.env` içinde `OCR_LANGUAGE=tur+eng` yazdığından emin ol. Düşük çözünürlüklü, eğik veya bulanık taramalarda OCR hataları devam edebilir.

## İndeksleme uzun sürüyor

OCR, normal PDF metni çıkarmadan daha yavaştır ve yalnızca yeterli seçilebilir metin bulunmayan sayfalarda çalışır. Büyük ve yüksek çözünürlüklü taranmış PDF'lerde ilk indeksleme birkaç dakika sürebilir.

## API kapalı

Backend'i elle başlat:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Ardından `http://127.0.0.1:8000/health` adresini kontrol et.

## `cannot import name genai from google`

Aktif sanal ortamda eski Google paketlerini kaldırıp güncel SDK'yı yeniden kur:

```powershell
python -m pip uninstall -y google google-generativeai google-genai
python -m pip install --upgrade "google-genai>=2,<3"
```

Kontrol:

```powershell
python -c "from google import genai; print('GENAI IMPORT OK')"
```

## Gemini anahtarı yok görünüyor

`.env` dosyası proje kökünde, `run_project.py` ile aynı seviyede bulunmalıdır. Anahtarın okunup okunmadığını anahtarı ekrana yazdırmadan kontrol et:

```powershell
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(bool(os.getenv('GEMINI_API_KEY')))"
```

Sonuç `True` olmalıdır. `.env.example` yalnızca şablondur; uygulama gerçek anahtarı `.env` dosyasından okur.

## Eski uygulama başlığı görünüyor

Önceki Streamlit süreci hâlâ açıktır. Bütün eski terminalleri durdur ve proje klasöründe yeniden çalıştır:

```powershell
python run_project.py
```

Başlatıcı boş port seçip doğru arayüz URL'sini açar.
