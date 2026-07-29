# PDF RAG Assistant — Windows Kurulumu

## 1. Python ortamını oluştur

Projeyi PyCharm'da açtıktan sonra `setup_windows.bat` dosyasını çalıştırabilirsin. Betik `venv` veya `.venv` ortamını algılar, bağımlılıkları kurar ve yoksa `.env` dosyasını oluşturur.

Elle kurulum:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

## 2. Gemini anahtarını ekle

`.env` dosyasına Google AI Studio'dan aldığın anahtarı yaz:

```env
GEMINI_API_KEY=GERCEK_ANAHTARIN
GEMINI_MODEL=gemini-3.6-flash
```

`.env` dosyasını veya anahtarın göründüğü ekran görüntülerini GitHub'a yükleme.

## 3. Taranmış PDF desteğini kur

Taranmış veya görüntü tabanlı PDF kullanacaksan bir kez çalıştır:

```powershell
.\install_ocr_windows.bat
```

Betik Tesseract OCR'ı ve Türkçe/İngilizce dil dosyalarını hazırlar. Kurulumdan sonra PyCharm'ı ve açık terminalleri tamamen kapatıp yeniden aç.

Kontrol:

```powershell
python scripts\check_ocr.py
python scripts\doctor.py
```

Beklenen OCR çıktısı:

```text
Dil sayısı: 2
Türkçe: var
İngilizce: var
Kullanılacak OCR dili: tur+eng
```

Tesseract otomatik bulunamazsa `.env` içine ileri eğik çizgi kullanarak yolu yaz:

```env
OCR_TESSDATA_PATH=C:/Users/KULLANICI/Desktop/pdf-rag-assistant/data/tessdata
OCR_LANGUAGE=tur+eng
```

Windows yolunda `\t` ifadesinin tab karakterine dönüşmemesi için ters eğik çizgi yerine `/` kullan.

## 4. Uygulamayı başlat

```powershell
python run_project.py
```

Alternatif olarak `start_windows.bat` dosyasını çalıştırabilirsin. Terminalde gösterilen arayüz adresini aç.

## 5. PDF indeksle ve soru sor

1. Sol menüden PDF seç.
2. **PDF'leri indeksle** düğmesine bas.
3. Metin tabanlı sayfalar doğrudan çıkarılır; görüntü sayfalarında OCR otomatik devreye girer.
4. Belgeyle ilgili bir soru sor.
5. Yanıtın altındaki dosya, sayfa, skor ve kaynak metnini kontrol et.
