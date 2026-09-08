# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
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

Ojo con lo que "servidor autorizado" NO cubre: esa lista decide en qué
MÁQUINA puede arrancar el programa, no QUIÉN puede entrar una vez que ya
está arriba — con la lista sola, cualquiera que llegue a host:puerto en la
red de la empresa entra sin login. Por eso, en modo servidor, si se define
``MVDG_SERVER_PASSWORD`` se exige esa contraseña compartida antes de
mostrar el dashboard (ver ``auth_required``/``check_password``, aplicado en
``app/app.py``). Sin esa variable, el servidor sigue funcionando (como
antes) pero queda abierto a quien llegue a la red — se avisa igual que se
avisa el modo "servidor abierto" sin lista de hosts.

Licencia sin que nadie escriba nada (``MVDG_SERVER_LICENSE_TOKEN``)
--------------------------------------------------------------------
Caso real: el dueño del producto es también consultor en un cliente que NO
deja instalar ni un .exe/.bat en su laptop, y cuyos datos no pueden salir
del servidor/VM del cliente. El instalador **owner** (el que abre
desbloqueado sin pegar nada) no sirve ahí: esa licencia va atada A SU
LAPTOP a propósito, así que en cualquier otra máquina abre en demo — es la
misma protección que evita que un .exe owner filtrado desbloquee cualquier
PC. Acá el camino es al revés: se emite un token ``owner`` atado al id de
ESE SERVIDOR (no al de la laptop) con

    python packaging/licencias.py maquina        # corrido UNA VEZ en el server
    python packaging/licencias.py firmar --plan owner --maquina <ese id> \\
        --email <tu-email>                       # corrido en TU máquina, con tu privada

y se deja el token resultante en ``MVDG_SERVER_LICENSE_TOKEN`` antes de
arrancar. ``run_server`` lo activa (vía ``licensing.save`` — firma Y máquina
se verifican igual que cualquier licencia) antes de abrir el dashboard: el
primer navegador que llega ya lo ve desbloqueado, sin pestaña de licencia,
sin que nadie tenga que copiar ni pegar nada ahí. Un token que no verifica
(vencido, mal copiado, atado a otra máquina) no activa nada — el servidor
sigue en el plan que ya tuviera, nunca por eso se cae.
"""
from __future__ import annotations

import hmac
import os
import socket
import sys

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8501
AUTHORIZED_FILE = "server_authorized.txt"
_SERVER_MODE_ENV = "MVDG_SERVER_MODE"
_PASSWORD_ENV = "MVDG_SERVER_PASSWORD"
_LICENSE_TOKEN_ENV = "MVDG_SERVER_LICENSE_TOKEN"


def server_mode_active() -> bool:
    """¿Este proceso arrancó vía ``run_server`` (modo servidor), a
    diferencia del .bat/.exe de escritorio? Lo marca ``run_server`` con una
    variable de entorno antes de levantar Streamlit — así ``app/app.py``
    puede diferenciar sin que el módulo de la UI necesite saber cómo se
    lanzó el proceso."""
    return os.environ.get(_SERVER_MODE_ENV) == "1"


def auth_required() -> bool:
    """¿Hay que pedir la contraseña compartida antes de mostrar el
    dashboard? Solo aplica en modo servidor Y si se configuró
    MVDG_SERVER_PASSWORD — en modo escritorio (un solo usuario, en su
    propia PC) no tiene sentido pedir login."""
    return server_mode_active() and bool(os.environ.get(_PASSWORD_ENV))


def check_password(candidate: str) -> bool:
    """Comparación en tiempo constante (evita timing attacks) contra
    MVDG_SERVER_PASSWORD. Si la variable no está seteada, siempre False —
    nunca "sin contraseña configurada = cualquiera entra silenciosamente"."""
    expected = os.environ.get(_PASSWORD_ENV, "")
    if not expected:
        return False
    return hmac.compare_digest((candidate or "").encode("utf-8"), expected.encode("utf-8"))


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


def activate_license_from_env() -> tuple[bool, str | None]:
    """Activa la licencia en ``MVDG_SERVER_LICENSE_TOKEN``, si hay una.

    Separada de ``run_server`` para poder probarla sin levantar Streamlit de
    verdad (``run_server(argv_out=...)`` la llama antes del dry-run).

    Pasa SIEMPRE por ``licensing.save()``: verifica firma Ed25519 y que el
    ``mid`` del token sea el de ESTA máquina, exactamente igual que
    cualquier otra licencia. No hay atajo acá — un token robado de otro
    servidor no sirve en este, ni uno vencido, ni uno mal copiado.

    Devuelve ``(activo, plan)``. Si la variable no está seteada: ``(False,
    None)`` sin tocar la licencia que ya hubiera (no pisa una activación
    manual previa por el solo hecho de no haber cambiado la variable)."""
    token = (os.environ.get(_LICENSE_TOKEN_ENV) or "").strip()
    if not token:
        return False, None
    from . import licensing
    payload = licensing.save(token)
    if payload is None:
        return False, None
    return True, payload.get("plan")


def _avisar_activacion_licencia(activada: bool, plan_activado: str | None) -> None:
    """El mensaje de ``activate_license_from_env()``, separado de
    ``run_server`` nada más que para no pasar las 100 líneas que el motor
    se prohíbe (``test_sin_funciones_gigantes_en_el_motor``)."""
    if activada:
        sys.stderr.write(
            f"  [MV Data Governance] Licencia activada desde {_LICENSE_TOKEN_ENV} "
            f"(plan={plan_activado}): el dashboard abre desbloqueado desde el "
            "primer navegador que llegue, sin pestaña de licencia / license "
            f"activated from {_LICENSE_TOKEN_ENV} (plan={plan_activado}): the "
            "dashboard opens unlocked for the first browser that reaches it, "
            f"no license screen / licença ativada a partir de "
            f"{_LICENSE_TOKEN_ENV} (plano={plan_activado}): o dashboard abre "
            "desbloqueado para o primeiro navegador, sem aba de licença.\n\n")
    elif os.environ.get(_LICENSE_TOKEN_ENV, "").strip():
        sys.stderr.write(
            f"  [MV Data Governance] {_LICENSE_TOKEN_ENV} está definida pero NO "
            "activó ninguna licencia (firma inválida, vencida, o atada a otra "
            "máquina): el servidor sigue en el plan que ya tuviera, no se cae "
            f"por esto / {_LICENSE_TOKEN_ENV} is set but did NOT activate any "
            "license (invalid signature, expired, or bound to a different "
            f"machine): the server keeps whichever plan it already had / "
            f"{_LICENSE_TOKEN_ENV} está definida mas NÃO ativou nenhuma "
            "licença: o servidor continua no plano que já tinha.\n\n")


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


def _port_free(host: str, port: int) -> bool:
    """.Esta el puerto libre de verdad?

    Delegado a mvdg.netports: la version anterior ponia SO_REUSEADDR, que en
    Windows permite hacer bind sobre un puerto que otra app ya ocupa. O sea
    que este chequeo — el que existe justamente para NO pisar a nadie —
    devolvia "libre" en el sistema operativo donde mas importa."""
    from mvdg.netports import puerto_libre
    return puerto_libre(host, port)


def run_server(argv_out: list | None = None) -> int:
    """Arranca el dashboard en modo servidor si el host está autorizado.

    Si ``argv_out`` es una lista, se rellena con los argumentos de Streamlit y
    NO se lanza el servidor (modo test / dry-run). Devuelve un código de salida.
    """
    os.environ[_SERVER_MODE_ENV] = "1"
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

    if not auth_required():
        sys.stderr.write(
            "  [MV Data Governance] Sin MVDG_SERVER_PASSWORD: quien llegue a "
            f"http://{host}:{port} en la red entra sin login / anyone reaching "
            f"http://{host}:{port} on the network gets in without a login /\n"
            "  quem chegar no endereço na rede entra sem login. Para pedir "
            "contraseña compartida, definí MVDG_SERVER_PASSWORD.\n\n")

    _avisar_activacion_licencia(*activate_license_from_env())

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

    # Este es el puerto que TI distribuye al resto de la empresa para llegar
    # al servidor — un punto fijo, no algo que deba "resolverse" saltando en
    # silencio a otro puerto si ya está ocupado (eso dejaría a todo el mundo
    # apuntando a una URL muerta sin saber por qué). Se corta acá con un
    # mensaje claro en vez del traceback crudo de Streamlit/Tornado.
    if not _port_free(host, port):
        sys.stderr.write(
            f"\n  [MV Data Governance] El puerto {port} ya está en uso por otro "
            f"programa / port {port} is already in use by another program / a "
            f"porta {port} ja esta em uso por outro programa.\n"
            f"  ES: Cerrá ese programa, o corré con MVDG_SERVER_PORT=<otro "
            f"puerto> para usar otro (avisale a quien lo vaya a usar en la "
            f"red).\n"
            f"  EN: Close that program, or run with MVDG_SERVER_PORT=<port> to "
            f"use a different one (tell whoever will reach it over the "
            f"network).\n"
            f"  PT: Feche esse programa, ou rode com MVDG_SERVER_PORT=<porta> "
            f"para usar outra (avise quem for acessar pela rede).\n\n")
        return 3

    print(f"MV Data Governance (servidor) -> http://{host}:{port}")
    from streamlit.web import cli as stcli
    sys.argv = argv
    return int(stcli.main() or 0)


if __name__ == "__main__":
    raise SystemExit(run_server())
