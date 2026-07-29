@echo off
setlocal
cd /d "%~dp0"

if exist venv\Scripts\python.exe (
    set VENV_DIR=venv
) else if exist .venv\Scripts\python.exe (
    set VENV_DIR=.venv
) else (
    echo Sanal ortam bulunamadi. Ilk once setup_windows.bat dosyasini calistir.
    pause
    exit /b 1
)

call %VENV_DIR%\Scripts\activate.bat
python scripts\doctor.py
if errorlevel 1 (
    pause
    exit /b 1
)
python run_project.py
pause
