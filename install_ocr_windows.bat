@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_ocr_windows.ps1"
if errorlevel 1 (
  echo.
  echo OCR kurulumu tamamlanamadi. Yukaridaki hatayi kontrol et.
  pause
  exit /b 1
)
pause
