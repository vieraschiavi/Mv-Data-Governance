"""
MV Data Governance · Lanzador del programa (Windows / cualquier SO).

Punto de entrada tanto del .bat portable como del ejecutable empaquetado con
PyInstaller. Arranca el dashboard Streamlit embebido en un puerto libre y
abre el navegador automáticamente — el usuario solo hace doble clic.
"""
from __future__ import annotations

import os
import sys
import threading
import time
import webbrowser


def _base_dir() -> str:
    """Carpeta con los recursos (bundle PyInstaller o raíz del repo)."""
    return getattr(sys, "_MEIPASS",
                   os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _puerto_libre() -> int:
    """Puerto libre para no chocar con otras apps (p. ej. otra en 8501).

    La deteccion vive en mvdg.netports porque la version que estaba aca
    usaba SO_REUSEADDR, que en Windows permite atarse a un puerto de OTRA
    aplicacion en vez de detectar que esta ocupado."""
    base = _base_dir()
    if base not in sys.path:
        sys.path.insert(0, base)
    from mvdg.netports import elegir_puerto
    return elegir_puerto("127.0.0.1")


def _puerto_pedido() -> int:
    """Puerto que el usuario fijo a mano (STREAMLIT_SERVER_PORT), o 0.

    Si lo fijo y OTRA aplicacion ya lo esta usando, no lo cambiamos por
    atras: eso lo dejaria buscando el programa en una direccion que no es.
    Se corta con un mensaje que dice que hacer, en vez del traceback de
    Tornado ("address already in use") que no le dice nada a un usuario de
    escritorio. Sin la variable definida no hay contrato que respetar y el
    lanzador elige puerto solo."""
    crudo = os.environ.get("STREAMLIT_SERVER_PORT", "").strip()
    if not crudo:
        return 0
    try:
        port = int(crudo)
    except ValueError:
        _salir_con_aviso(
            f"STREAMLIT_SERVER_PORT={crudo!r} no es un numero de puerto.\n"
            "  ES: dejala sin definir para que el programa elija uno solo.\n"
            "  EN: leave it unset to let the program pick one.\n"
            "  PT: deixe-a indefinida para o programa escolher sozinho.")
    base = _base_dir()
    if base not in sys.path:
        sys.path.insert(0, base)
    from mvdg.netports import puerto_libre
    if not puerto_libre("127.0.0.1", port):
        _salir_con_aviso(
            f"El puerto {port} ya esta en uso por otro programa / port {port} "
            f"is already in use / a porta {port} ja esta em uso.\n"
            f"  ES: cerra ese programa, usa STREAMLIT_SERVER_PORT=<otro "
            f"puerto>, o dejala sin definir para que el programa elija.\n"
            f"  EN: close that program, set STREAMLIT_SERVER_PORT=<other "
            f"port>, or leave it unset to let the program pick.\n"
            f"  PT: feche esse programa, use STREAMLIT_SERVER_PORT=<outra "
            f"porta>, ou deixe-a indefinida para o programa escolher.")
    return port


def _salir_con_aviso(mensaje: str) -> None:
    """Mensaje accionable y salida limpia (sin traceback en la consola)."""
    sys.stderr.write(f"\n  [MV Data Governance] {mensaje}\n\n")
    raise SystemExit(3)


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


def _dispatch_module_flag() -> bool:
    """Soporte de ``-m <módulo>`` cuando este launcher corre como .exe
    congelado (PyInstaller).

    El botón "Probar servidor MCP" (app/app.py) y el selfcheck
    (mvdg/selfcheck.py) lanzan un subproceso con
    ``sys.executable, ["-m", "mvdg.mcp_server"]`` — el mismo patrón que
    usarían con un ``python.exe`` normal. En el .bat portable eso funciona
    porque ``sys.executable`` ES python.exe. Pero en el .exe empaquetado,
    ``sys.executable`` es este mismo binario congelado, que no sabe
    interpretar "-m módulo" como haría un intérprete real — sin este atajo,
    el subproceso simplemente relanzaría el dashboard completo (una segunda
    ventana) en vez de correr ``mvdg.mcp_server``. Acá lo interceptamos y
    corremos el módulo pedido con runpy, igual que ``python -m`` haría.
    Devuelve True si se consumió el flag (el caller no debe seguir)."""
    if len(sys.argv) >= 3 and sys.argv[1] == "-m":
        import runpy
        runpy.run_module(sys.argv[2], run_name="__main__", alter_sys=True)
        return True
    return False


def main() -> None:
    if _dispatch_module_flag():
        return

    base = _base_dir()
    app_path = os.path.join(base, "app", "app.py")

    # Modo "programa": sin telemetría ni pantallas de desarrollo.
    os.environ.setdefault("STREAMLIT_GLOBAL_DEVELOPMENT_MODE", "false")
    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")
    os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "true")

    port = _puerto_pedido() or _puerto_libre()
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
