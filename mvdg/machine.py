"""
MV Data Governance · Identificador de máquina (para licencias atadas).

Para qué sirve
--------------
Una licencia normal (la que compra un cliente) vale en cualquier PC: es un
permiso, no un candado. Pero la licencia del **owner** desbloquea todo y es
perpetua, así que si el archivo se filtra, quien lo tenga se queda con el
producto completo gratis.

Atar esa licencia a una máquina resuelve eso: el token lleva el campo ``mid``
y ``licensing.verify()`` lo rechaza si no coincide con la PC donde corre. Un
instalador del owner que se filtre abre en modo demo en cualquier otra
máquina.

Qué NO es
---------
Esto **no es DRM ni protección anticopia**, y no pretende serlo. El id se
calcula de datos que un atacante decidido puede leer y falsificar. Lo que
frena es el caso realista: que un .exe ya desbloqueado circule por mail o
por un pendrive y funcione. Contra alguien que sabe parchear un binario no
hay defensa del lado del cliente — eso se resuelve con contratos, no con
código.

Cómo se calcula
---------------
Hash de tres cosas estables en una PC de escritorio: nombre del equipo,
dirección MAC de la placa de red y arquitectura del sistema. Se hashea (y no
se guardan en claro) para no filtrar el nombre de la máquina del usuario
dentro de un token que puede viajar por mail.
"""
from __future__ import annotations

import hashlib
import platform
import uuid

# Largo del id: 16 hex (64 bits). Alcanza de sobra para que dos máquinas no
# colisionen por accidente, y entra cómodo en un token que se copia y pega.
_LARGO = 16


def machine_id() -> str:
    """Identificador estable de esta máquina (16 caracteres hex).

    Si algún dato no se puede leer, se usa lo que haya: un id calculado con
    menos fuentes sigue siendo estable en la misma PC, que es lo único que
    importa acá. Nunca lanza: quedarse sin poder abrir el programa por no
    poder leer la MAC sería mucho peor que un id menos específico.
    """
    partes = []
    try:
        partes.append(platform.node() or "")
    except Exception:
        partes.append("")
    try:
        # uuid.getnode() devuelve la MAC; si no la consigue, inventa un valor
        # aleatorio y marca el bit 41. En ese caso NO sirve (cambiaría en cada
        # arranque), así que se descarta.
        nodo = uuid.getnode()
        partes.append(str(nodo) if not (nodo >> 40) % 2 else "")
    except Exception:
        partes.append("")
    try:
        partes.append(platform.machine() or "")
    except Exception:
        partes.append("")
    crudo = "|".join(partes).encode("utf-8", "replace")
    return hashlib.sha256(crudo).hexdigest()[:_LARGO]


def matches(mid: str | None) -> bool:
    """¿El id de una licencia corresponde a esta máquina?

    ``None`` o vacío = licencia sin atar, vale en cualquier lado (es el caso
    de todas las licencias que se venden). La comparación es sin distinguir
    mayúsculas y sin espacios: el token se copia y pega a mano.
    """
    if not mid:
        return True
    return str(mid).strip().lower() == machine_id()
