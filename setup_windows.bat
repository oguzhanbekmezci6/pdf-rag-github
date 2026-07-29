@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    set PYTHON_CMD=py
) else (
    set PYTHON_CMD=python
)

if exist venv\Scripts\python.exe (
    set VENV_DIR=venv
) else if exist .venv\Scripts\python.exe (
    set VENV_DIR=.venv
) else (
    set VENV_DIR=.venv
    %PYTHON_CMD% -m venv %VENV_DIR%
    if errorlevel 1 goto :error
)

call %VENV_DIR%\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 goto :error

rem Remove legacy/conflicting Google packages before installing the official SDK.
python -m pip uninstall -y google google-generativeai >nul 2>nul
python -m pip install -r requirements.txt
if errorlevel 1 goto :error
python -m pip install -r requirements-dev.txt
if errorlevel 1 goto :error

if not exist .env copy .env.example .env >nul

python scripts\doctor.py
if errorlevel 1 goto :error

echo.
echo Kurulum tamamlandi.
echo .env dosyasina GEMINI_API_KEY degerini ekle.
echo Taranmis PDF kullanacaksan install_ocr_windows.bat dosyasini bir kez calistir.
echo Ardindan start_windows.bat dosyasini calistir.
pause
exit /b 0

:error
echo.
echo Kurulum basarisiz oldu. Yukaridaki hata mesajini kontrol et.
pause
exit /b 1
