"""
MV Data Governance · Deteccion de puertos ocupados (correcta en Windows).

Por que existe este modulo
--------------------------
El programa elegia puerto asi::

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))   # si no explota, "esta libre"

En Linux/macOS eso funciona. **En Windows significa lo contrario.** Ahi
``SO_REUSEADDR`` no sirve para reciclar sockets en TIME_WAIT: permite atarse
a un puerto que **otra aplicacion ya esta usando**. Por eso Microsoft agrego
``SO_EXCLUSIVEADDRUSE``, que es el que garantiza exclusividad.

Consecuencia en el producto (que corre justamente en Windows): el chequeo
decia "libre" para un puerto ocupado por otra app, y el programa arrancaba
encima. Quien recibe cada conexion queda indeterminado — dos servidores
peleandose el mismo puerto. Y de paso, el aviso de "el puerto ya esta en
uso" de la API nunca se disparaba en Windows, que es donde hace falta.

Como se resuelve aca
--------------------
Dos preguntas distintas, porque una sola no alcanza:

1. **.Hay alguien escuchando?** Se intenta CONECTAR. Si alguien acepta, el
   puerto es de otro, sin importar la semantica de bind de cada sistema.
   Ademas es inmune a los falsos positivos por TIME_WAIT: un socket que
   quedo cerrandose no acepta conexiones, y no tiene por que bloquearnos.
2. **.Podemos reservarlo en exclusiva?** Se intenta bind sin
   ``SO_REUSEADDR``, y en Windows con ``SO_EXCLUSIVEADDRUSE``.

Solo si las dos dan que si, el puerto se considera libre.
"""
from __future__ import annotations

import os
import socket

# Puertos que prueba el lanzador del dashboard, en orden. No son 8501 a
# proposito: ese es el default de Streamlit y es justo el que suele estar
# ocupado por otra app de Streamlit del mismo usuario.
PUERTOS_DASHBOARD = (8641, 8652, 8663, 8674, 8685)

# Espera para el intento de conexion. Contra localhost, "no hay nadie" vuelve
# como "conexion rechazada" al instante; el timeout solo cubre el caso raro de
# un firewall que descarta los paquetes en silencio.
_TIMEOUT_CONEXION = 0.35


def _host_conectable(host: str) -> str:
    """Host al que conectarse para sondear.

    A "0.0.0.0" (o "::") no se conecta nadie: son comodines de escucha, no
    destinos. Si el servidor va a escuchar en todas las interfaces, el sondeo
    se hace contra loopback, que es donde igual quedaria publicado."""
    return "127.0.0.1" if host in ("", "0.0.0.0", "::") else host


def hay_alguien_escuchando(host: str, port: int) -> bool:
    """True si algo acepta conexiones en ese puerto (otra app lo esta usando)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(_TIMEOUT_CONEXION)
        try:
            return s.connect_ex((_host_conectable(host), port)) == 0
        except OSError:
            return False


def _se_puede_reservar(host: str, port: int) -> bool:
    """True si podemos quedarnos con el puerto en EXCLUSIVA."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # En Windows este es el unico flag que garantiza exclusividad. Sin el,
        # bind puede tener exito sobre un puerto ajeno.
        if os.name == "nt" and hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            try:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            except OSError:
                pass
        # OJO: NO se pone SO_REUSEADDR. Justamente lo que se quiere saber es
        # si el puerto esta realmente libre, no si podemos forzarlo.
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def puerto_libre(host: str, port: int) -> bool:
    """.Esta el puerto realmente disponible para nosotros?"""
    if hay_alguien_escuchando(host, port):
        return False
    return _se_puede_reservar(host, port)


def elegir_puerto(host: str = "127.0.0.1",
                  candidatos: tuple[int, ...] = PUERTOS_DASHBOARD) -> int:
    """Primer puerto libre de la lista; si estan todos ocupados, uno que
    asigne el sistema operativo (siempre libre por definicion)."""
    for p in candidatos:
        if puerto_libre(host, p):
            return p
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, 0))
        return s.getsockname()[1]
