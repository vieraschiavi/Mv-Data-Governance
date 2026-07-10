"""
MV Data Governance · Lanzador del programa (Windows / cualquier SO).

Punto de entrada tanto del .bat portable como del ejecutable empaquetado con
PyInstaller. Arranca el dashboard Streamlit embebido en un puerto libre y
abre el navegador automáticamente — el usuario solo hace doble clic.
"""
from __future__ import annotations

import os
import socket
import sys
import threading
import time
import webbrowser


def _base_dir() -> str:
    """Carpeta con los recursos (bundle PyInstaller o raíz del repo)."""
    return getattr(sys, "_MEIPASS",
                   os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _puerto_libre() -> int:
    """Puerto libre para no chocar con otras apps (p. ej. otra en 8501)."""
    for p in (8641, 8652, 8663, 8674, 8685):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _abrir_navegador(url: str) -> None:
    """Espera a que el servidor levante y abre el navegador una sola vez."""
    import urllib.request
    for _ in range(120):
        time.sleep(0.5)
        try:
            urllib.request.urlopen(url, timeout=1)
            break
        except Exception:
            continue
    webbrowser.open(url)


def main() -> None:
    base = _base_dir()
    app_path = os.path.join(base, "app", "app.py")

    # Modo "programa": sin telemetría ni pantallas de desarrollo.
    os.environ.setdefault("STREAMLIT_GLOBAL_DEVELOPMENT_MODE", "false")
    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")
    os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "true")

    port = int(os.environ.get("STREAMLIT_SERVER_PORT", 0)) or _puerto_libre()
    url = f"http://127.0.0.1:{port}"
    print(f"MV Data Governance -> {url}")

    threading.Thread(target=_abrir_navegador, args=(url,), daemon=True).start()

    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", app_path,
                "--server.port", str(port),
                "--server.address", "127.0.0.1",
                "--browser.gatherUsageStats", "false",
                "--theme.base", "dark",
                "--theme.primaryColor", "#f2b441",
                "--theme.backgroundColor", "#081527",
                "--theme.secondaryBackgroundColor", "#0c2137",
                "--theme.textColor", "#eaf1fb"]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
