@echo off
setlocal
cd /d "%~dp0"

if exist venv\Scripts\python.exe (
    set VENV_DIR=venv
) else if exist .venv\Scripts\python.exe (
    set VENV_DIR=.venv
) else (
    echo Sanal ortam bulunamadi.
    pause
    exit /b 1
)

call %VENV_DIR%\Scripts\activate.bat
python scripts\doctor.py %*
pause
