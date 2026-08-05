"""
MV Data Governance · Licencias (verificación local, firma de clave pública).

Qué resuelve
------------
Hasta acá el circuito de pago terminaba a medias: ``api/verify-payment.js``
confirmaba el pago con MercadoPago y le devolvía al cliente una cadena de
licencia… que **ningún lado del programa leía**. Es decir: no había forma de
distinguir a alguien que pagó de alguien que no.

Por qué clave pública y no el HMAC que ya existía
-------------------------------------------------
``api/_license.js`` firma con HMAC-SHA256 y un secreto compartido
(``LICENSE_SECRET``). Ese esquema sirve cuando los dos extremos son de
confianza (dos funciones del backend), pero **no** para verificar del lado del
cliente: verificar un HMAC exige el mismo secreto que lo firma, así que habría
que embeberlo en el programa que se distribuye. Cualquiera que lo extraiga
—de un ``.pyd`` con ``strings``, o reverseando— puede fabricarse licencias
infinitas, y encima queda expuesto el secreto del backend de pagos.

Con Ed25519 el backend firma con la clave **privada** (que nunca sale del
servidor) y el programa verifica con la **pública**, que es inofensiva aunque
se extraiga. Por eso este módulo verifica el formato ``MVDG2`` (Ed25519) y no
el ``MVDG1`` (HMAC), que se mantiene solo para el uso interno del backend.

El límite honesto
-----------------
Esto es verificación del lado del cliente: alguien con conocimiento puede
parchear el binario y saltear el chequeo. No es DRM inviolable —no existe tal
cosa en software que se instala— sino el mecanismo que hace que el uso pago sea
una decisión explícita y no un accidente, y que le da sustento técnico a lo que
el LICENSE dice en palabras. Compilar el motor (packaging/build_compiled.py)
sube el costo de ese parcheo, no lo elimina.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import time

from .clients import data_dir

# ---------------------------------------------------------------------------
# Clave pública del emisor de licencias.
#
# Se completa con packaging/licencias.py keygen (imprime exactamente qué pegar
# acá y qué cargar como LICENSE_PRIVATE_KEY en el backend).
#
# Vacía = ninguna licencia valida = todo el mundo queda en plan demo. Es a
# propósito que falle CERRADO: si se olvidan de configurarla, el síntoma es
# "los clientes que pagaron no pueden activar" (ruidoso y se arregla al
# instante), no "todo el mundo tiene todo gratis" (silencioso).
#
# Es la clave PÚBLICA: no es un secreto y no pasa nada si se lee del binario.
# ---------------------------------------------------------------------------
PUBLIC_KEY_B64 = ""

_PREFIJO = "MVDG2"
_ARCHIVO = "licencia.json"
# Token que viaja dentro del build del owner (ver _licencia_empaquetada).
_ARCHIVO_EMPAQUETADO = "licencia_owner.txt"

# Planes conocidos, de menor a mayor. "demo" es el piso: sin licencia válida,
# el programa funciona igual pero con las funciones marcadas abajo apagadas.
#
# "owner" es el plan del dueño del producto: no se vende, se AUTO-EMITE. Con
# el par de claves generado por `packaging/licencias.py keygen`, el dueño se
# firma a sí mismo una licencia perpetua:
#
#     python packaging/licencias.py firmar --plan owner --email <tu-email>
#
# y la activa en la pestaña Ayuda como cualquier cliente activaría la suya.
# Es el mismo circuito verificado (Ed25519, firma cerrada) que ya cubren los
# tests — no un atajo aparte: hace falta la clave PRIVADA (que nunca sale del
# dueño) para emitir un token "owner" válido, así que no es algo que alguien
# pueda activarse leyendo el código fuente, aunque viaje en texto plano en la
# versión portable. has_feature() la trata como comodín: desbloquea todo,
# incluso funciones que se agreguen a FUNCIONES_PAGAS más adelante y a las que
# se olvide sumar "owner" a mano.
PLAN_DEMO = "demo"
PLAN_OWNER = "owner"
# "trial" es el plan Professional (USD 390/mes) por 14 días, auto-emitido sin
# pago: api/trial.js firma el mismo token MVDG2 que emitiría una compra real,
# pero con `exp` a 14 días y sin pasar por MercadoPago. verify() YA rechaza
# tokens vencidos (ver más abajo) — el vencimiento del trial no necesita
# ningún código nuevo acá, solo que "trial" habilite lo mismo que
# "professional" en FUNCIONES_PAGAS.
PLAN_TRIAL = "trial"
PLANES = (PLAN_DEMO, "licencia", PLAN_TRIAL, "professional", "enterprise", PLAN_OWNER)

# ---------------------------------------------------------------------------
# POLÍTICA COMERCIAL — qué necesita licencia paga.
#
# Esto es una decisión de NEGOCIO, no técnica: está acá, en un solo lugar y
# explícito, para que se cambie sin tocar nada más. Cada función pedida en el
# programa se resuelve contra esta tabla vía has_feature().
#
# El default es deliberadamente CONSERVADOR: se abre todo lo que hace lucir al
# producto (catálogo, calidad, linaje, glosario, perfilado, MDM, exportación a
# BI, y trabajar con datos propios) y se pide licencia solo para lo que
# únicamente tiene sentido dentro de una empresa ya decidida a comprar —
# empujar metadata a Purview/Collibra y escanear un tenant entero de BI.
#
# Si querés un demo más restringido (por ejemplo, pedir licencia para usar
# datos propios), agregá "mis_datos" a FUNCIONES_PAGAS y listo.
# ---------------------------------------------------------------------------
FUNCIONES_PAGAS: dict[str, tuple[str, ...]] = {
    # función -> planes que la habilitan. "trial" da acceso a lo mismo que
    # "professional" (es el mismo plan, por 14 días) — así el trial demuestra
    # el tier completo, no una versión recortada de "a ver si les gusta".
    "migracion_purview": ("professional", "enterprise", PLAN_TRIAL),
    "migracion_collibra": ("professional", "enterprise", PLAN_TRIAL),
    "escaneo_tenant_bi": ("professional", "enterprise", PLAN_TRIAL),
}


def _b64u_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _archivo() -> str:
    return os.path.join(data_dir(), _ARCHIVO)


def verify(token: str, public_key_b64: str | None = None,
           check_machine: bool = True) -> dict | None:
    """Verifica una licencia ``MVDG2.<payload>.<firma>``.

    Devuelve el payload si la firma es válida y no está vencida; ``None`` en
    cualquier otro caso. No lanza: una licencia inválida es un estado normal
    (alguien pegó mal la clave), no un error del programa.

    ``check_machine=False`` verifica todo MENOS que el campo ``mid`` sea de
    esta PC. Lo usa el emisor de licencias (packaging/licencias.py) para su
    chequeo de sanidad: firma un token atado a OTRA máquina (la del owner) y
    necesita confirmar que la firma quedó bien sin que lo rechace por no ser
    esa máquina. El programa del cliente siempre usa el default.
    """
    pub = public_key_b64 if public_key_b64 is not None else PUBLIC_KEY_B64
    if not pub or not token or not isinstance(token, str):
        return None
    partes = token.strip().split(".")
    if len(partes) != 3 or partes[0] != _PREFIJO:
        return None
    _, body, firma = partes
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PublicKey)
    except ImportError:
        # Sin 'cryptography' no se puede verificar nada. Falla cerrado: mejor
        # que el cliente vea "no se pudo validar" a que se habilite gratis.
        return None
    try:
        key = Ed25519PublicKey.from_public_bytes(_b64u_decode(pub))
        key.verify(_b64u_decode(firma), body.encode("ascii"))
    except (InvalidSignature, ValueError, TypeError):
        return None
    try:
        payload = json.loads(_b64u_decode(body).decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    exp = payload.get("exp")
    if exp is not None:
        try:
            if float(exp) < time.time():
                return None  # vencida
        except (TypeError, ValueError):
            return None
    if payload.get("plan") not in PLANES:
        return None
    # Licencia ATADA a una máquina (campo "mid"): se usa para el build del
    # owner, que viene desbloqueado de fábrica. Si ese .exe se filtra, en
    # cualquier otra PC el id no coincide y queda en plan demo. Las licencias
    # que se VENDEN no llevan "mid" y siguen valiendo en cualquier máquina —
    # atarle la licencia a la PC a un cliente que pagó sería hostil.
    if check_machine:
        from .machine import matches
        if not matches(payload.get("mid")):
            return None
    return payload


def save(token: str) -> dict | None:
    """Valida y guarda la licencia. Devuelve el payload, o None si no valida
    (en cuyo caso NO se guarda nada: no se persiste basura)."""
    payload = verify(token)
    if payload is None:
        return None
    destino = _archivo()
    tmp = destino + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump({"token": token.strip(), "payload": payload}, fh,
                  ensure_ascii=False, indent=2)
    os.replace(tmp, destino)
    return payload


def clear() -> None:
    """Saca la licencia guardada (vuelve a plan demo)."""
    try:
        os.remove(_archivo())
    except OSError:
        pass


def _licencia_empaquetada() -> str | None:
    """Token que viaja DENTRO del programa, si lo hay (build del owner).

    El instalador del owner trae ``licencia_owner.txt`` al lado del .exe: así
    el programa abre ya desbloqueado, sin pegar el token a mano cada vez que
    se reinstala. No es un atajo de seguridad — ese token igual tiene que
    pasar ``verify()`` como cualquier otro (firma Ed25519 válida y, en el
    caso del owner, atado a la máquina). Si no valida, se ignora."""
    candidatas = []
    if getattr(sys, "frozen", False):
        candidatas.append(os.path.dirname(sys.executable))
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidatas.append(meipass)
    else:
        candidatas.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    for base in candidatas:
        ruta = os.path.join(base, _ARCHIVO_EMPAQUETADO)
        try:
            with open(ruta, encoding="utf-8") as fh:
                token = fh.read().strip()
            if token:
                return token
        except OSError:
            continue
    return None


def current() -> dict | None:
    """Licencia guardada, **revalidando la firma** en cada lectura.

    Revalidar y no confiar en el JSON guardado es el punto: si alguien edita
    licencia.json a mano para ponerse plan "enterprise", la firma deja de
    coincidir con el payload y la licencia se descarta.

    Si no hay licencia guardada, se prueba la empaquetada (build del owner).
    """
    ruta = _archivo()
    if not os.path.exists(ruta):
        token = _licencia_empaquetada()
        return verify(token) if token else None
    try:
        with open(ruta, encoding="utf-8") as fh:
            guardado = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(guardado, dict):
        return None
    return verify(guardado.get("token", ""))


def plan() -> str:
    """Plan vigente: el de la licencia válida, o "demo"."""
    payload = current()
    if not payload:
        return PLAN_DEMO
    return payload.get("plan") or PLAN_DEMO


def has_feature(funcion: str) -> bool:
    """¿El plan vigente habilita esta función?

    Una función que no figura en FUNCIONES_PAGAS está disponible para todos —
    el default es abierto, y lo pago se declara explícitamente. El plan
    "owner" siempre pasa: es el dueño del producto, no un plan que se venda."""
    if plan() == PLAN_OWNER:
        return True
    requeridos = FUNCIONES_PAGAS.get(funcion)
    if not requeridos:
        return True
    return plan() in requeridos


def status() -> dict:
    """Resumen para mostrar en la interfaz."""
    payload = current()
    return {
        "plan": plan(),
        "licenciado": payload is not None,
        "email": (payload or {}).get("email"),
        "emitida": (payload or {}).get("iat"),
        "vence": (payload or {}).get("exp"),
        "emisor_configurado": bool(PUBLIC_KEY_B64),
        "funciones_pagas": sorted(FUNCIONES_PAGAS),
    }
