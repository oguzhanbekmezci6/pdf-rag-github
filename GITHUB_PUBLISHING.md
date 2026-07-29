# GitHub Yayınlama Rehberi

## Repo bilgileri

**Repository name**

```text
pdf-rag-assistant
```

**Description**

```text
Source-grounded PDF question answering with local embeddings, OCR, Qdrant retrieval, Gemini generation and page-level citations.
```

**Visibility**

```text
Public
```

**Topics**

```text
rag
retrieval-augmented-generation
pdf-question-answering
document-ai
semantic-search
ocr
fastapi
streamlit
qdrant
sentence-transformers
gemini-api
python
vector-database
turkish-nlp
```

## GitHub'da repo oluştururken

- `Add a README file` seçme; README zaten projede var.
- `.gitignore` seçme; proje kendi `.gitignore` dosyasını içeriyor.
- License seçme; MIT lisansı zaten projede var.

## İlk push öncesi kontrol

```powershell
git status
Get-ChildItem -Force
Get-ChildItem -Recurse -File | Select-String -Pattern "AIza"
python scripts\doctor.py
python -m pip install -r requirements-dev.txt
ruff check .
pytest
```

Kontrol listesi:

- `.env` Git'e eklenmemeli.
- Gerçek Gemini anahtarı hiçbir dosyada bulunmamalı.
- `data/uploads/` içinde kişisel PDF bulunmamalı.
- `data/qdrant/`, `data/models/` ve `data/tessdata/` yüklenmemeli.
- Ekran görüntülerinde API anahtarı veya özel belge içeriği görünmemeli.

## İlk Git komutları

```powershell
git init
git branch -M main
git add .
git status
git commit -m "feat: publish PDF RAG Assistant v1.0.0"
git remote add origin https://github.com/oguzhanbekmezci6/pdf-rag-assistant.git
git push -u origin main
```

`origin already exists` hatası alınırsa:

```powershell
git remote set-url origin https://github.com/oguzhanbekmezci6/pdf-rag-assistant.git
git push -u origin main
```

## Push sonrasında yapılacaklar

1. Repo açıklamasını ve topic'leri ekle.
2. `About` alanında Releases ve Issues özelliklerini açık bırak.
3. `Settings → Security` bölümünden Dependabot alerts, secret scanning ve push protection seçeneklerini kontrol et.
4. Actions sekmesinde CI testinin geçtiğini doğrula.
5. `Releases → Draft a new release` bölümünden `v1.0.0` etiketiyle release oluştur.
6. `RELEASE_NOTES.md` içeriğini release açıklaması olarak kullan.
7. Repo'yu GitHub profilinde sabitle.

## Release komutları

```powershell
git tag -a v1.0.0 -m "PDF RAG Assistant v1.0.0"
git push origin v1.0.0
```

## Profilde kullanabileceğin kısa proje açıklaması

```text
Built a source-grounded PDF RAG application with local multilingual embeddings, OCR, Qdrant retrieval, FastAPI, Streamlit and Gemini-based answer generation.
```
