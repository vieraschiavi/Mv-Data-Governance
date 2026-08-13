# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Activación del owner, en un solo paso.

Qué hace (todo automático, sin pegar nada a mano)
-------------------------------------------------
1. Si todavía no existe el par de claves de licencias, lo **genera** y deja
   la clave pública escrita en ``mvdg/licensing.py``. Sin ese paso ninguna
   licencia valida — ni una firmada correctamente —, así que es lo primero.
2. Guarda la clave **privada** fuera del repo, en la carpeta de datos del
   programa, con permisos restringidos.
3. Calcula el id de ESTA máquina.
4. Se firma a sí mismo una licencia plan ``owner`` con ese id y el email
   del dueño.
5. La **activa**: el programa abre desbloqueado a partir de la próxima vez.
6. Imprime el token para pegarlo como secreto ``MVDG_OWNER_TOKEN`` en
   GitHub (necesario solo si querés que el instalador del owner se
   construya ya desbloqueado desde Actions).

Por qué esto corre acá y no en la nube
--------------------------------------
Dos cosas no se pueden hacer desde otra máquina, y no es un capricho:

* **La clave privada** es la que emite TODAS las licencias del producto.
  Quien la tenga puede fabricarse licencias infinitas y las de tus clientes
  dejan de significar nada. Tiene que nacer y quedarse en tu equipo — no
  viajar por un chat, un log o un contenedor efímero.
* **El id de máquina** de un servidor en la nube es el de ese servidor, que
  además se destruye al rato. La licencia tiene que atarse a TU PC, si no
  no te sirve a vos y sí le serviría a cualquiera.

Uso:  doble clic en MV_Owner_Activar.bat   (o  python packaging/owner_setup.py)
"""
from __future__ import annotations

import base64
import json
import os
import re
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

EMAIL_POR_DEFECTO = "vieraschiavi@gmail.com"
ARCHIVO_LICENSING = os.path.join(RAIZ, "mvdg", "licensing.py")
NOMBRE_PRIVADA = "clave_privada_licencias.txt"


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _sin_acentos(texto: str) -> str:
    """La consola de Windows usa cp850/cp1252 y rompe con acentos."""
    tabla = str.maketrans("áéíóúÁÉÍÓÚñÑ¿¡ü", "aeiouAEIOUnN??u")
    return texto.translate(tabla)


def _p(texto: str = "") -> None:
    try:
        print(texto)
    except UnicodeEncodeError:
        print(_sin_acentos(texto))


def _ruta_privada() -> str:
    from mvdg.clients import data_dir
    return os.path.join(data_dir(), NOMBRE_PRIVADA)


def _guardar_privada(priv_b64: str) -> str:
    """Guarda la privada FUERA del repo (nunca se commitea) y, donde el
    sistema lo permita, solo legible por el usuario."""
    ruta = _ruta_privada()
    with open(ruta, "w", encoding="utf-8") as fh:
        fh.write(priv_b64)
    try:
        os.chmod(ruta, 0o600)
    except OSError:
        pass          # Windows: los permisos POSIX no aplican, no es un error
    return ruta


def _leer_privada() -> str | None:
    """La privada, de la variable de entorno o del archivo local."""
    del_entorno = (os.environ.get("LICENSE_PRIVATE_KEY") or "").strip()
    if del_entorno:
        return del_entorno
    try:
        with open(_ruta_privada(), encoding="utf-8") as fh:
            return fh.read().strip() or None
    except OSError:
        return None


def _escribir_publica_en_el_codigo(pub_b64: str) -> None:
    """Deja PUBLIC_KEY_B64 escrita en mvdg/licensing.py.

    Se reemplaza solo la asignación, con una expresión anclada: el archivo
    tiene la palabra PUBLIC_KEY_B64 varias veces en los comentarios que
    explican por qué es pública, y un reemplazo por texto suelto las
    tocaría."""
    with open(ARCHIVO_LICENSING, encoding="utf-8") as fh:
        codigo = fh.read()
    nuevo, n = re.subn(r'^PUBLIC_KEY_B64 = "[^"]*"$',
                       f'PUBLIC_KEY_B64 = "{pub_b64}"',
                       codigo, count=1, flags=re.MULTILINE)
    if n != 1:
        raise SystemExit("No se encontro la linea PUBLIC_KEY_B64 en "
                         "mvdg/licensing.py — .se edito a mano?")
    with open(ARCHIVO_LICENSING, "w", encoding="utf-8") as fh:
        fh.write(nuevo)


def _generar_par() -> tuple[str, str]:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    priv = Ed25519PrivateKey.generate()
    priv_b64 = _b64u(priv.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()))
    pub_b64 = _b64u(priv.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw))
    return priv_b64, pub_b64


def _firmar(priv_b64: str, payload: dict) -> str:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    priv = Ed25519PrivateKey.from_private_bytes(
        base64.urlsafe_b64decode(priv_b64 + "=" * (-len(priv_b64) % 4)))
    body = _b64u(json.dumps(payload, ensure_ascii=False,
                            separators=(",", ":"), sort_keys=True).encode("utf-8"))
    return f"MVDG2.{body}.{_b64u(priv.sign(body.encode('ascii')))}"


def main(email: str | None = None) -> int:
    email = (email or EMAIL_POR_DEFECTO).strip()
    _p()
    _p("  =====================================================")
    _p("   MV Data Governance - Activacion del owner")
    _p("  =====================================================")
    _p()

    from mvdg import licensing
    from mvdg.machine import machine_id

    # --- 1. par de claves ---------------------------------------------------
    priv_b64 = _leer_privada()
    if not licensing.PUBLIC_KEY_B64:
        _p("  [1/5] No habia par de claves: generandolo...")
        priv_b64, pub_b64 = _generar_par()
        _escribir_publica_en_el_codigo(pub_b64)
        ruta = _guardar_privada(priv_b64)
        licensing.PUBLIC_KEY_B64 = pub_b64      # para el resto de ESTA corrida
        _p("        clave publica -> escrita en mvdg/licensing.py")
        _p(f"        clave privada -> {ruta}")
        _p("        (esa privada NO esta en el repo y no se sube a ningun lado:")
        _p("         es la que emite todas las licencias. Hace un backup.)")
    elif not priv_b64:
        _p("  [1/5] ERROR: el programa ya tiene una clave publica configurada,")
        _p("        pero no encuentro la privada correspondiente.")
        _p()
        _p(f"        Buscada en: LICENSE_PRIVATE_KEY y {_ruta_privada()}")
        _p()
        _p("        Si tenes la privada guardada, ponela en ese archivo.")
        _p("        Si la perdiste, hay que generar un par nuevo — y las")
        _p("        licencias ya emitidas dejarian de validar.")
        return 1
    else:
        _p("  [1/5] Par de claves ya configurado: se reutiliza.")

    # --- 2. id de esta maquina ---------------------------------------------
    mid = machine_id()
    _p(f"  [2/5] Id de esta maquina: {mid}")

    # --- 3. firmar la licencia del owner -----------------------------------
    token = _firmar(priv_b64, {
        "plan": licensing.PLAN_OWNER,
        "email": email,
        "iat": int(time.time()),
        "pid": f"owner-{int(time.time())}",
        "mid": mid,          # atada: si el archivo se filtra, no sirve
    })
    _p(f"  [3/5] Licencia firmada para {email} (plan owner, sin vencimiento)")

    # --- 4. verificarla por la MISMA ruta que usa el programa ---------------
    payload = licensing.verify(token)
    if payload is None:
        _p("  [4/5] ERROR: la licencia recien emitida NO verifica.")
        _p("        No se activa nada. (.La privada corresponde a la publica?)")
        return 1
    _p("  [4/5] Verificada con la ruta real del programa (Ed25519 + maquina)")

    # --- 5. activarla -------------------------------------------------------
    if licensing.save(token) is None:
        _p("  [5/5] ERROR: no se pudo guardar la licencia.")
        return 1
    _p("  [5/5] Activada: el programa abre desbloqueado desde ahora.")
    _p()
    _p(f"        plan={licensing.plan()}  "
       f"Purview={licensing.has_feature('migracion_purview')}  "
       f"Collibra={licensing.has_feature('migracion_collibra')}  "
       f"TenantBI={licensing.has_feature('escaneo_tenant_bi')}")
    _p()
    _p("  ---------------------------------------------------------------")
    _p("  Para que el instalador del owner salga ya desbloqueado desde")
    _p("  GitHub (Actions -> Instalador Owner), pega este token como")
    _p("  secreto MVDG_OWNER_TOKEN:")
    _p()
    _p(f"  {token}")
    _p()
    _p("  Y si generaste el par recien, commitea mvdg/licensing.py: sin la")
    _p("  clave publica adentro, el programa que reciben tus clientes no")
    _p("  puede validar NINGUNA licencia (queda todo en plan demo).")
    _p("  ---------------------------------------------------------------")
    _p()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else None))
