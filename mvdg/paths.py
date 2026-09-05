# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Dónde vive lo persistente.

Este módulo existe para NO arrastrar pandas donde no hace falta.

``data_dir()`` vivía en ``mvdg/clients.py``, que importa pandas arriba de
todo para el CRUD de fichas de clientes. Pero ``mvdg/licensing.py`` —el
verificador de licencias, que corre en el arranque de todo— también lo
necesitaba, así que importar `licensing` arrastraba pandas.

Eso se hizo visible cuando el workflow del instalador owner falló en main:

    File "mvdg/licensing.py", line 45, in <module>
        from .clients import data_dir
    File "mvdg/clients.py", line 21, in <module>
        import pandas as pd
    ModuleNotFoundError: No module named 'pandas'

El paso solo quería validar un token de licencia en un runner con Python
limpio. Instalar pandas ahí para leer una firma Ed25519 sería tapar el
síntoma: el verificador de licencias tiene que poder importarse con la
biblioteca estándar y nada más.

Solo stdlib acá adentro. A propósito.
"""
from __future__ import annotations

import os
import sys


def data_dir() -> str:
    """Carpeta donde vive TODO lo persistente (clientes, curaduría, licencia,
    conexiones, importado, organigrama - un solo directorio para todo eso).

    Prioridad:
    1. ``MVDG_DATA_DIR`` explícita: control manual, gana siempre.
    2. Instalación empaquetada (``sys.frozen``): una carpeta ``Data`` AL LADO
       del ejecutable — si se puede escribir ahí. Así lo que el usuario
       eligió en "Seleccionar carpeta de destino" del instalador (C:, D:, un
       pendrive) es también donde quedan sus datos. Si NO se puede
       (instalado en Archivos de programa con admin y corriendo como usuario
       normal), se cae al perfil del usuario en vez de morir con
       PermissionError: mejor guardar en ~ que no arrancar.
    3. Todo lo demás (portable .bat, corriendo desde código fuente):
       ``~/.mv_data_governance``. Ahí no hay una carpeta de instalación fija
       a la cual atarse - el usuario puede mover la carpeta del programa
       libremente sin que sus datos queden huérfanos en otro lado.
    """
    override = os.environ.get("MVDG_DATA_DIR")
    if override:
        d = override
    elif getattr(sys, "frozen", False):
        d = (_dir_junto_al_exe_escribible()
             or os.path.join(os.path.expanduser("~"), ".mv_data_governance"))
    else:
        d = os.path.join(os.path.expanduser("~"), ".mv_data_governance")
    os.makedirs(d, exist_ok=True)
    return d


# Cache del sondeo de escritura por carpeta del ejecutable: probar la
# escritura una vez por carpeta alcanza, y data_dir() se llama seguido.
_ESCRITURA_PROBADA: dict[str, str] = {}


def _dir_junto_al_exe_escribible() -> str | None:
    """``Data`` al lado del .exe — SOLO si de verdad se puede escribir ahí.

    El caso que rompía: instalar en ``C:\\Archivos de programa`` (el default
    del instalador) y abrir el programa como usuario normal. Ahí
    ``makedirs`` falla con PermissionError, y como el .exe corre sin consola
    (console=False en el spec), el programa moría EN SILENCIO al primer
    arranque — "no funciona", sin ningún mensaje. Y no alcanza con que la
    carpeta exista: puede haberla creado el instalador con permisos de
    admin y aún así no dejarnos escribir adentro — por eso se sondea
    escribiendo un archivo de verdad, no mirando permisos declarados."""
    base = os.path.dirname(sys.executable)
    if base in _ESCRITURA_PROBADA:
        return _ESCRITURA_PROBADA[base] or None
    d = os.path.join(base, "Data")
    try:
        os.makedirs(d, exist_ok=True)
        sonda = os.path.join(d, ".sonda_escritura")
        with open(sonda, "w", encoding="utf-8") as fh:
            fh.write("ok")
        os.remove(sonda)
        _ESCRITURA_PROBADA[base] = d
        return d
    except OSError:
        _ESCRITURA_PROBADA[base] = ""
        return None
