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


def _navegadores_ventana() -> list[str]:
    """Rutas candidatas a un navegador con modo aplicación (--app).

    En Windows, Edge viene preinstalado en 10/11 — es la garantía de que el
    modo ventana funciona sin instalar nada. Chrome se prueba después. En
    Linux/macOS (desarrollo) se buscan los equivalentes en el PATH."""
    if os.name == "nt":
        pf = os.environ.get("ProgramFiles", r"C:\Program Files")
        pf86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        local = os.environ.get("LOCALAPPDATA", "")
        return [
            os.path.join(pf86, "Microsoft", "Edge", "Application", "msedge.exe"),
            os.path.join(pf, "Microsoft", "Edge", "Application", "msedge.exe"),
            os.path.join(pf, "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(pf86, "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(local, "Google", "Chrome", "Application", "chrome.exe"),
        ]
    import shutil
    rutas = [shutil.which(n) for n in
             ("microsoft-edge", "google-chrome", "chromium", "chromium-browser")]
    return [r for r in rutas if r]


def _comando_ventana(url: str, navegador: str) -> list[str]:
    """El comando que abre la app como VENTANA DE PROGRAMA, no como pestaña.

    ``--app=URL`` es el modo aplicación de Edge/Chrome: ventana propia, sin
    barra de direcciones ni pestañas, con su entrada en la barra de tareas —
    lo que un usuario de escritorio espera de un programa instalado."""
    return [navegador, f"--app={url}", "--window-size=1440,900"]


def _abrir_programa(url: str) -> None:
    """Espera a que el servidor levante y abre la VENTANA del programa.

    Si hay Edge/Chrome, ventana de aplicación (sin cromo de navegador). Si
    no hay ninguno — raro en Windows, donde Edge viene de fábrica — se cae
    al navegador por defecto: mejor una pestaña que nada."""
    import subprocess
    import urllib.request
    for _ in range(120):
        time.sleep(0.5)
        try:
            urllib.request.urlopen(url, timeout=1)
            break
        except Exception:
            continue
    for navegador in _navegadores_ventana():
        if os.path.isfile(navegador):
            try:
                subprocess.Popen(_comando_ventana(url, navegador),
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
                return
            except OSError:
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


def _log_y_avisar_error(detalle: str) -> str:
    """Deja el traceback en un log y, en Windows, muestra un diálogo.

    El .exe corre sin consola (console=False en el spec): sin esto, cualquier
    excepción en el arranque hace que el programa "no haga nada" — la peor
    experiencia posible de un instalador. El log va al lado del .exe si se
    puede escribir ahí, o a TEMP si no (Archivos de programa sin admin)."""
    import tempfile
    nombre = "mvdg_error.log"
    for carpeta in (os.path.dirname(os.path.abspath(sys.executable)),
                    tempfile.gettempdir()):
        ruta = os.path.join(carpeta, nombre)
        try:
            with open(ruta, "a", encoding="utf-8") as fh:
                fh.write(detalle + "\n" + "-" * 60 + "\n")
            break
        except OSError:
            continue
    else:
        ruta = "(no se pudo escribir el log)"
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                None,
                "El programa no pudo arrancar.\n"
                "The program could not start.\n"
                "O programa nao pode iniciar.\n\n"
                f"Log: {ruta}",
                "MV Data Governance", 0x10)  # MB_ICONERROR
        except Exception:
            pass
    return ruta


def main() -> None:
    """Punto de entrada con los errores VISIBLES: si algo explota en el
    arranque, queda un mvdg_error.log y (en Windows) un diálogo con la ruta
    — nunca más un doble clic que no hace nada."""
    try:
        _main()
    except SystemExit:
        raise
    except Exception:
        import traceback
        _log_y_avisar_error(traceback.format_exc())
        raise


def _main() -> None:
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

    threading.Thread(target=_abrir_programa, args=(url,), daemon=True).start()

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
