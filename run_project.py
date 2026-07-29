from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from app import __version__

ROOT = Path(__file__).resolve().parent


def find_free_port(start: int, attempts: int = 20) -> int:
    for port in range(start, start + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise RuntimeError(f"{start}-{start + attempts - 1} aralığında boş port bulunamadı.")


def stop_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=8)
    except subprocess.TimeoutExpired:
        process.kill()


def wait_for_url(url: str, process: subprocess.Popen[bytes], timeout_seconds: int = 90) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return False
        try:
            with urlopen(url, timeout=2) as response:
                return response.status == 200
        except (URLError, TimeoutError):
            time.sleep(1)
    return False


def main() -> None:
    python = sys.executable
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)

    api_port = find_free_port(8000)
    ui_port = find_free_port(8501)
    api_url = f"http://127.0.0.1:{api_port}"
    ui_url = f"http://127.0.0.1:{ui_port}"

    print(f"PDF RAG Assistant V{__version__}")
    print(f"Proje klasörü: {ROOT}")
    if api_port != 8000 or ui_port != 8501:
        print(
            "Uyarı: Eski uygulama süreçleri varsayılan portları kullanıyor. "
            f"Yeni sürüm API {api_port}, arayüz {ui_port} portunda açılacak."
        )
    print(f"Python: {python}")
    print("FastAPI başlatılıyor...")

    api = subprocess.Popen(
        [
            python,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(api_port),
        ],
        cwd=ROOT,
        env=env,
    )

    if not wait_for_url(f"{api_url}/health", api):
        stop_process(api)
        raise SystemExit(
            "FastAPI başlatılamadı. Yukarıdaki import/kurulum hatasını düzeltip "
            "python scripts/doctor.py komutunu çalıştır."
        )

    print(f"API hazır: {api_url}/docs")
    print("Streamlit başlatılıyor...")
    ui_env = env.copy()
    ui_env["API_URL"] = api_url
    ui = subprocess.Popen(
        [
            python,
            "-m",
            "streamlit",
            "run",
            "ui/streamlit_app.py",
            "--server.port",
            str(ui_port),
            "--server.address",
            "127.0.0.1",
            "--server.headless",
            "true",
        ],
        cwd=ROOT,
        env=ui_env,
    )

    processes = [api, ui]

    def stop_all(*_: object) -> None:
        for process in reversed(processes):
            stop_process(process)

    signal.signal(signal.SIGINT, stop_all)
    signal.signal(signal.SIGTERM, stop_all)

    if not wait_for_url(ui_url, ui):
        stop_all()
        raise SystemExit("Streamlit arayüzü başlatılamadı.")

    launch_url = f"{ui_url}/?version={__version__}"
    print(f"Arayüz: {launch_url}")
    webbrowser.open(launch_url)

    try:
        while True:
            if api.poll() is not None:
                raise SystemExit("FastAPI beklenmedik şekilde kapandı.")
            if ui.poll() is not None:
                raise SystemExit(ui.returncode or 0)
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        stop_all()


if __name__ == "__main__":
    main()
