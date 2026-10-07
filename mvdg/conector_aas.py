# © 2026 Martín Viera. Todos los derechos reservados.
"""
conector_aas.py — Azure Analysis Services (el MDW) como fuente de «Mis datos»
=============================================================================
Analysis Services habla DAX, no SQL. Esta conexión lee las tablas del modelo
(en solo lectura: sólo `EVALUATE`, con un tope de filas por tabla) y las
devuelve como DataFrames, que se gobiernan como cualquier otro dataset:
catálogo, calidad, linaje, glosario y exportación a BI.

Para hablar con Analysis Services hace falta el cliente ADOMD.NET de Microsoft
(pythonnet + pyadomd en Windows). Ese conector ya vive en la suite Adium All in
One (`adium_allinone.analysis_services`), con el usuario y la contraseña
corporativos, la ventana de inicio de sesión de Microsoft (MFA) o un token.
Cuando MV Data Governance corre adentro de la suite se usa ése; suelto, se
avisa qué hace falta.

Los errores salen con un `codigo` (la clave de i18n que los explica en ES/EN/PT)
y, si vienen del conector, su `detalle` tal cual: el motor no escribe textos de
pantalla.
"""
from __future__ import annotations

import re

AUTENTICACIONES = ("usuario", "ventana", "token")
TOPE_DEFAULT = 100_000
_ASAZURE = re.compile(r"^(asazure|powerbi)://\S+$", re.I)


class ErrorAAS(Exception):
    """Algo que el usuario tiene que corregir. `codigo` es la clave de i18n (`aas_err_*`)."""

    def __init__(self, codigo: str, detalle: str = ""):
        super().__init__(f"{codigo}: {detalle}" if detalle else codigo)
        self.codigo, self.detalle = codigo, detalle


def motor_suite():
    """El conector de Analysis Services de la suite, o None si MV Data Governance corre suelto."""
    try:
        from adium_allinone import analysis_services
    except Exception:  # noqa: BLE001 — suelto: la suite no está en este proceso
        return None
    return analysis_services


def validar(servidor: str, modelo: str, auth: str, usuario: str = "", clave: str = "",
            token: str = "") -> tuple[str, str]:
    servidor = (servidor or "").strip()
    if not _ASAZURE.match(servidor):
        raise ErrorAAS("aas_err_servidor")
    if not (modelo or "").strip():
        raise ErrorAAS("aas_err_modelo")
    if auth not in AUTENTICACIONES:
        raise ErrorAAS("aas_err_auth", auth)
    if auth == "usuario" and not ((usuario or "").strip() and clave):
        raise ErrorAAS("aas_err_usuario")
    if auth == "token" and not (token or "").strip():
        raise ErrorAAS("aas_err_token")
    return servidor, modelo.strip()


def _motor(AS):
    AS = AS or motor_suite()
    if AS is None:
        raise ErrorAAS("aas_err_suelto")
    return AS


def _preparar(AS, servidor: str, auth: str, usuario: str, clave: str) -> None:
    faltan = AS.librerias_faltantes() if hasattr(AS, "librerias_faltantes") else []
    if faltan:
        detalle = AS.diagnostico_faltantes(faltan) if hasattr(AS, "diagnostico_faltantes") else ""
        raise ErrorAAS("aas_err_librerias", ", ".join(faltan) + (f" — {detalle}" if detalle else ""))
    try:
        AS.usar_usuario(servidor, usuario if auth == "usuario" else "", clave if auth == "usuario" else "")
        AS.usar_ventana(servidor, auth == "ventana")
    except Exception as e:  # noqa: BLE001 — p. ej. un usuario que no es un mail: el conector dice qué corregir
        raise ErrorAAS("aas_err_conector", str(e)) from e


def listar_tablas(servidor: str, modelo: str, auth: str = "usuario", usuario: str = "", clave: str = "",
                  token: str = "", AS=None) -> list[str]:
    """Las tablas del modelo, para elegir cuáles traer."""
    servidor, modelo = validar(servidor, modelo, auth, usuario, clave, token)
    AS = _motor(AS)
    _preparar(AS, servidor, auth, usuario, clave)
    try:
        return list(AS.tablas_del_modelo(servidor, modelo, token if auth == "token" else ""))
    except Exception as e:  # noqa: BLE001 — permiso, red, MFA: el conector ya explica la causa
        raise ErrorAAS("aas_err_conector", str(e)) from e


def leer(servidor: str, modelo: str, auth: str = "usuario", usuario: str = "", clave: str = "",
         token: str = "", tablas=None, limite: int | None = TOPE_DEFAULT, AS=None):
    """Trae las tablas (todas o las elegidas) en solo lectura: ({tabla: DataFrame}, avisos)."""
    servidor, modelo = validar(servidor, modelo, auth, usuario, clave, token)
    AS = _motor(AS)
    _preparar(AS, servidor, auth, usuario, clave)
    try:
        lec = AS.leer(servidor, modelo, token if auth == "token" else "",
                      tablas=list(tablas) if tablas else None, limite=limite or None)
    except Exception as e:  # noqa: BLE001
        raise ErrorAAS("aas_err_conector", str(e)) from e
    con_datos = getattr(lec, "con_datos", None) or getattr(lec, "tablas", ())
    datos = {t.nombre: t.datos for t in con_datos if getattr(t, "datos", None) is not None}
    if not datos:
        raise ErrorAAS("aas_err_vacio")
    return datos, list(getattr(lec, "avisos", ()))
