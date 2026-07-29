$ErrorActionPreference = "Stop"

Write-Host "PDF RAG Assistant - Tesseract OCR kurulumu" -ForegroundColor Cyan

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    throw "winget bulunamadı. Microsoft App Installer'ı güncelle veya Tesseract'ı elle kur."
}

winget install -e --id UB-Mannheim.TesseractOCR --accept-package-agreements --accept-source-agreements

# Language data is kept inside the project so administrator permission is not
# required for writing under Program Files.
$tessdata = Join-Path $PSScriptRoot "data\tessdata"
New-Item -ItemType Directory -Force -Path $tessdata | Out-Null

$languageFiles = @{
    "eng" = "https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/eng.traineddata"
    "tur" = "https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/tur.traineddata"
}

foreach ($language in $languageFiles.Keys) {
    $target = Join-Path $tessdata "$language.traineddata"
    if (-not (Test-Path $target)) {
        Write-Host "$language dil dosyası indiriliyor..."
        Invoke-WebRequest -Uri $languageFiles[$language] -OutFile $target
    }
}

$envFile = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $PSScriptRoot ".env.example") $envFile
}

$normalized = $tessdata.Replace('\\', '/')
$content = Get-Content $envFile -Raw
$line = "OCR_TESSDATA_PATH=`"$normalized`""
if ($content -match '(?m)^OCR_TESSDATA_PATH=.*$') {
    $content = [regex]::Replace($content, '(?m)^OCR_TESSDATA_PATH=.*$', $line)
} else {
    $content = $content.TrimEnd() + "`r`n$line`r`n"
}
Set-Content -Path $envFile -Value $content -Encoding UTF8

Write-Host "OCR kurulumu tamamlandı." -ForegroundColor Green
Write-Host "Dil dosyaları: $tessdata" -ForegroundColor Green
Write-Host "PyCharm ve açık terminalleri tamamen kapatıp yeniden aç." -ForegroundColor Yellow
Write-Host "Sonra: python scripts\doctor.py" -ForegroundColor Yellow
