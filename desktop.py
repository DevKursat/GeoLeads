#!/usr/bin/env python3
"""
GeoLeads Pro - Native Desktop Application Launcher
Runs backend server in background daemon and launches a dedicated native desktop window.
Supports pywebview with automatic fallback to native Chrome/Edge app-window mode or default browser.
"""
import os
import sys
import time
import socket
import threading
import subprocess
import webbrowser
from pathlib import Path

# Add backend directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.main import run_server


def find_available_port(default_port: int = 8000) -> int:
    """Finds an available local TCP port."""
    for port in range(default_port, default_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return default_port


def wait_for_server(port: int, timeout: float = 8.0) -> bool:
    """Waits until the local HTTP server is accepting connections."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except (OSError, ConnectionRefusedError):
            time.sleep(0.15)
    return False


def start_backend(port: int):
    """Starts the GeoLeads backend server."""
    # Ensure current working directory is backend for db/static resolution
    os.chdir(str(BACKEND_DIR))
    run_server(port=port)


def launch_native_app_window(url: str, title: str = "GeoLeads Pro"):
    """
    Attempts to launch the window in:
    1. pywebview (True native embedded webview window)
    2. Chrome / Brave / Edge App Mode (--app=URL), which renders as a dedicated desktop window without browser chrome
    3. Default system web browser
    """
    # 1. Try pywebview if installed
    try:
        import webview
        print("[*] pywebview tespit edildi. Yerel masaüstü penceresi açılıyor...")
        webview.create_window(
            title=title,
            url=url,
            width=1280,
            height=840,
            min_size=(960, 640),
            background_color="#020617"
        )
        webview.start()
        return
    except (ImportError, Exception) as e:
        # Fall back to native app mode
        pass

    # 2. Try launching Chrome/Edge/Brave in standalone app mode
    chrome_candidates = [
        # macOS
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        # Linux
        "google-chrome",
        "google-chrome-stable",
        "chromium-browser",
        "chromium",
        "brave-browser",
        # Windows paths checked via PATH or env
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
    ]

    for candidate in chrome_candidates:
        if os.path.isfile(candidate) or subprocess.run(["which", candidate], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0 if sys.platform != "win32" and "/" not in candidate else False:
            try:
                print(f"[*] Masaüstü pencere modu başlatılıyor ({os.path.basename(candidate)} --app)...")
                proc = subprocess.Popen(
                    [candidate, f"--app={url}", "--window-size=1280,840"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                proc.wait()
                return
            except Exception:
                continue

    # 3. Final Fallback: System browser
    print(f"[*] Standart tarayıcıda açılıyor: {url}")
    webbrowser.open(url)


def main():
    print("=" * 60)
    print("      🎯 GeoLeads Pro - Masaüstü Uygulaması Başlatıcı      ")
    print("=" * 60)

    port = find_available_port(8000)
    url = f"http://127.0.0.1:{port}"

    # Start server in daemon thread so it terminates when the main thread terminates
    server_thread = threading.Thread(target=start_backend, args=(port,), daemon=True)
    server_thread.start()

    print(f"[*] GeoLeads motoru hazırlanıyor (Port: {port})...")
    if not wait_for_server(port, timeout=10.0):
        print("[!] Sunucu zamanında yanıt vermedi, yine de pencere açılıyor...")

    print(f"[✓] GeoLeads hazır: {url}")
    print("[*] Masaüstü arayüzü açılıyor...")

    try:
        launch_native_app_window(url, title="GeoLeads Pro - B2B Müşteri Bulma & Satış Motoru")
    except KeyboardInterrupt:
        print("\n[✓] GeoLeads Masaüstü kapatıldı.")
    except Exception as e:
        print(f"[!] Hata: {e}")


if __name__ == "__main__":
    main()
