"""
MV Data Governance · Modo servidor (web) para despliegue en la empresa.

La 3ª forma de usar el programa (además del .exe y del .bat portable): correrlo
como servidor web en la infraestructura de la empresa, para que varios usuarios
lo abran desde el navegador sin instalar nada en cada PC. Todo sigue siendo
local a la empresa — nada viaja a internet.

"Servidores autorizados por la empresa": para que el programa NO pueda
levantarse en cualquier máquina, este módulo verifica que el servidor donde se
ejecuta esté en una lista de hosts autorizados por TI. La lista se define con:

  - la variable de entorno  MVDG_AUTHORIZED_HOSTS  (hostnames/IPs separados por
    coma), o
  - un archivo  server_authorized.txt  en la carpeta del programa (un host por
    línea; las líneas que empiezan con # son comentarios).

Si la lista está vacía, el servidor arranca igual pero avisa que está en modo
abierto (sin restricción). El valor especial ``*`` autoriza cualquier host.

Host y puerto de escucha se configuran con MVDG_SERVER_HOST (por defecto
0.0.0.0, accesible en la red de la empresa) y MVDG_SERVER_PORT (por defecto
8501).
"""
from __future__ import annotations

import os
import socket
import sys

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8501
AUTHORIZED_FILE = "server_authorized.txt"


def local_identities() -> set[str]:
    """Nombres e IPs con los que se puede identificar esta máquina."""
    ids = {"localhost", "127.0.0.1"}
    try:
        host = socket.gethostname()
        if host:
            ids.add(host.lower())
        try:
            ids.add(socket.getfqdn(host).lower())
        except Exception:
            pass
        try:
            for info in socket.getaddrinfo(host, None):
                ids.add(info[4][0].lower())
        except Exception:
            pass
    except Exception:
        pass
    # IP saliente (sin abrir conexión real) para cubrir la IP de LAN
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("192.0.2.1", 9))  # dirección TEST-NET, no genera tráfico
            ids.add(s.getsockname()[0].lower())
        finally:
            s.close()
    except Exception:
        pass
    return {i for i in ids if i}


def parse_authorized(raw: str | None) -> list[str]:
    """Convierte texto (env var o archivo) en lista de hosts autorizados.

    Acepta tanto una env var (``a,b,c`` en una línea) como un archivo con un
    host por línea y comentarios ``#``. Los comentarios se descartan ANTES de
    separar por comas, para no partir una línea de comentario que tenga comas.
    """
    if not raw:
        return []
    out: list[str] = []
    for line in raw.splitlines():
        entry = line.strip()
        if not entry or entry.startswith("#"):
            continue
        for part in entry.split(","):
            host = part.strip().lower()
            if host:
                out.append(host)
    return out


def load_authorized(base_dir: str | None = None,
                    env: dict | None = None) -> list[str]:
    """Lee la lista de hosts autorizados: primero la env var, si no el archivo."""
    env = env if env is not None else os.environ
    raw = env.get("MVDG_AUTHORIZED_HOSTS")
    if raw:
        return parse_authorized(raw)
    base = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, AUTHORIZED_FILE)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return parse_authorized(fh.read())
        except OSError:
            return []
    return []


def authorization_status(authorized: list[str],
                         identities: set[str] | None = None) -> dict:
    """¿Está este servidor autorizado a hostear el programa?

    Devuelve {'mode': 'open'|'authorized'|'denied', 'matched': str|None}.
    - 'open'       -> no hay lista configurada (corre, con aviso).
    - 'authorized' -> este host está en la lista (o la lista es '*').
    - 'denied'     -> hay lista pero este host no figura (no debe arrancar).
    """
    if not authorized:
        return {"mode": "open", "matched": None}
    authorized = [h.strip().lower() for h in authorized if h.strip()]
    if "*" in authorized:
        return {"mode": "authorized", "matched": "*"}
    ids = identities if identities is not None else local_identities()
    ids = {i.lower() for i in ids}
    for host in authorized:
        if host in ids:
            return {"mode": "authorized", "matched": host}
    return {"mode": "denied", "matched": None}


def _resolve_host_port(env: dict | None = None) -> tuple[str, int]:
    env = env if env is not None else os.environ
    host = env.get("MVDG_SERVER_HOST", DEFAULT_HOST).strip() or DEFAULT_HOST
    try:
        port = int(env.get("MVDG_SERVER_PORT", DEFAULT_PORT))
    except (TypeError, ValueError):
        port = DEFAULT_PORT
    return host, port


def _base_dir() -> str:
    return getattr(sys, "_MEIPASS",
                   os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_server(argv_out: list | None = None) -> int:
    """Arranca el dashboard en modo servidor si el host está autorizado.

    Si ``argv_out`` es una lista, se rellena con los argumentos de Streamlit y
    NO se lanza el servidor (modo test / dry-run). Devuelve un código de salida.
    """
    base = _base_dir()
    host, port = _resolve_host_port()
    authorized = load_authorized(base)
    status = authorization_status(authorized)

    if status["mode"] == "denied":
        me = sorted(local_identities())
        sys.stderr.write(
            "\n  [MV Data Governance] Servidor NO autorizado / server NOT authorized /\n"
            "  servidor NAO autorizado.\n"
            "  ES: Este equipo (" + ", ".join(me) + ") no figura en la lista de\n"
            "      servidores autorizados (" + ", ".join(authorized) + ").\n"
            "  EN: This host is not in the authorized-servers list.\n"
            "  PT: Este host nao esta na lista de servidores autorizados.\n"
            "  → TI/IT: agregá este host a MVDG_AUTHORIZED_HOSTS o al archivo "
            + AUTHORIZED_FILE + ".\n\n")
        return 2

    if status["mode"] == "open":
        sys.stderr.write(
            "\n  [MV Data Governance] Modo servidor ABIERTO / OPEN server mode /\n"
            "  modo servidor ABERTO — sin lista de hosts autorizados.\n"
            "  Para restringir a servidores de la empresa, definí "
            "MVDG_AUTHORIZED_HOSTS\n  o creá el archivo " + AUTHORIZED_FILE + ".\n\n")
    else:
        sys.stderr.write(
            "\n  [MV Data Governance] Servidor autorizado / authorized / autorizado ("
            + str(status["matched"]) + "). Iniciando / starting / iniciando...\n\n")

    app_path = os.path.join(base, "app", "app.py")
    os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "true")
    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")

    argv = ["streamlit", "run", app_path,
            "--server.address", host,
            "--server.port", str(port),
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
            "--theme.base", "dark",
            "--theme.primaryColor", "#f2b441",
            "--theme.backgroundColor", "#081527",
            "--theme.secondaryBackgroundColor", "#0c2137",
            "--theme.textColor", "#eaf1fb"]

    if argv_out is not None:
        argv_out[:] = argv
        return 0

    print(f"MV Data Governance (servidor) -> http://{host}:{port}")
    from streamlit.web import cli as stcli
    sys.argv = argv
    return int(stcli.main() or 0)


if __name__ == "__main__":
    raise SystemExit(run_server())
