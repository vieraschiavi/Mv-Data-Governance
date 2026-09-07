# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Screencast REAL de la app (no una animación).

A diferencia de build_video.py (que dibuja una animación con PIL + narración
TTS para el video promocional de la landing), esto graba la aplicación
Streamlit CORRIENDO DE VERDAD: levanta app/app.py, la navega con Playwright
por el flujo Catálogo → Calidad → Linaje → BI/API — el mismo que promociona
la landing — y guarda la grabación tal cual, sin edición.

Requiere Playwright con Chromium ya instalado (no se instala acá; en CI o
en una compilación no interactiva, saltealo). No corre en el pipeline de
tests — es una herramienta de documentación, se corre a mano cuando cambia
la UI y hay que rehacer el screencast.

Uso:
    python assets/video/record_screencast.py
    # → assets/video/MVDataGovernance_Screencast_real.webm

WebM (no mp4) a propósito: es lo que graba Chromium nativamente sin
recodificar, y todos los navegadores modernos lo reproducen sin plugins.
"""
from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_FINAL = os.path.join(REPO_ROOT, "assets", "video", "MVDataGovernance_Screencast_real.webm")
OUT_LANDING = os.path.join(REPO_ROOT, "landing", "video", "MVDataGovernance_Screencast_real.webm")


def _puerto_libre() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _esperar_servidor(url: str, intentos: int = 40) -> None:
    for _ in range(intentos):
        try:
            urllib.request.urlopen(url, timeout=1)
            return
        except Exception:
            time.sleep(0.5)
    raise SystemExit(f"Streamlit no levantó en {url}")


def _chromium_launch_kwargs() -> dict:
    """Algunos entornos (p. ej. este sandbox) declaran
    PLAYWRIGHT_BROWSERS_PATH con un Chromium completo ya instalado, pero sin
    la variante "chrome-headless-shell" que Playwright intenta por defecto.
    Si existe ese binario, lo usamos explícito; si no, dejamos que
    Playwright resuelva como siempre (caso normal en una máquina de
    desarrollo con `playwright install chromium` corrido)."""
    base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if base:
        candidato = os.path.join(base, "chromium")
        if os.path.exists(candidato):
            return {"executable_path": candidato}
    return {}


def main() -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit(
            "Falta playwright: pip install playwright && playwright install chromium"
        ) from None

    puerto = _puerto_libre()
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app/app.py",
         "--server.headless", "true", "--server.port", str(puerto),
         "--server.address", "127.0.0.1"],
        cwd=REPO_ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        _esperar_servidor(f"http://127.0.0.1:{puerto}/")
        tmp_dir = os.path.join(REPO_ROOT, "assets", "video", ".screencast_tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        with sync_playwright() as pw:
            b = pw.chromium.launch(**_chromium_launch_kwargs())
            ctx = b.new_context(
                viewport={"width": 1440, "height": 900},
                record_video_dir=tmp_dir,
                record_video_size={"width": 1440, "height": 900},
            )
            p = ctx.new_page()
            p.goto(f"http://127.0.0.1:{puerto}/", wait_until="load", timeout=30000)
            p.wait_for_timeout(5500)  # que las tarjetas de Panorama terminen de cargar

            def ir_a(nombre: str, espera_ms: int) -> None:
                p.locator(f'[data-testid="stTab"]:has-text("{nombre}")').first.click()
                p.wait_for_timeout(espera_ms)

            # El mismo flujo que promociona la landing: catálogo -> calidad
            # (6 dimensiones) -> linaje end-to-end -> BI/API.
            ir_a("Panorama", 2500)
            ir_a("Catálogo", 3800)
            ir_a("Calidad", 3000)
            p.mouse.wheel(0, 400)
            p.wait_for_timeout(2500)
            ir_a("Linaje", 4200)
            ir_a("BI & API", 4000)
            p.wait_for_timeout(1200)

            video_path = p.video.path()
            ctx.close()
            b.close()

        shutil.move(video_path, OUT_FINAL)
        shutil.copyfile(OUT_FINAL, OUT_LANDING)
        shutil.rmtree(tmp_dir, ignore_errors=True)
        print(f"listo -> {OUT_FINAL}")
        print(f"copiado a -> {OUT_LANDING}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    main()
