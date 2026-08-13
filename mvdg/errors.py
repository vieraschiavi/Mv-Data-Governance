# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Errores en idioma humano.

Traduce una excepción a un mensaje que le sirva a quien está usando el
programa: qué pasó y **qué hacer al respecto**. El detalle técnico no se
tira — se devuelve aparte, para mostrarlo plegado y poder pasárselo a
soporte sin obligar a nadie a leer un traceback.

    from mvdg.errors import friendly_error
    msg, detalle = friendly_error(exc, "es", contexto="archivo")

Vive en el motor (no en ``app/app.py``) para que la API, el modo servidor y
los conectores puedan dar exactamente el mismo mensaje ante la misma falla.
"""
from __future__ import annotations

from .i18n import DEFAULT_LANG, t

# Contextos: matizan el mensaje según qué estaba haciendo el usuario.
CONTEXTOS = ("archivo", "conexion", "red", "generico")


def _nombre_excepcion(exc: BaseException) -> str:
    return type(exc).__name__


def _clave_por_tipo(exc: BaseException, contexto: str) -> str | None:
    """Mapea la excepción a una clave de i18n con consejo accionable.

    Se compara por NOMBRE de clase y no con isinstance para no tener que
    importar pandas/sqlalchemy/openpyxl acá: el motor tiene que poder
    importarse sin ellos, y estas dependencias son opcionales según el flujo.
    """
    nombre = _nombre_excepcion(exc)
    texto = str(exc).lower()

    # --- archivos que el usuario sube ---
    if nombre == "UnicodeDecodeError":
        return "err_encoding"
    if nombre == "EmptyDataError" or "no columns to parse" in texto:
        return "err_vacio"
    if nombre in ("ParserError", "ParserWarning") or "error tokenizing" in texto:
        return "err_csv_malformado"
    if nombre == "BadZipFile" or "not a zip file" in texto:
        return "err_zip"
    if nombre in ("JSONDecodeError",) or "expecting value" in texto:
        return "err_json"
    if nombre == "PermissionError":
        return "err_permiso"
    if nombre == "FileNotFoundError":
        return "err_no_existe"
    if nombre == "MemoryError":
        return "err_memoria"
    if nombre == "XLRDError" or "excel file format cannot be determined" in texto:
        return "err_excel_formato"

    # --- dependencias que faltan (driver de base, motor de Excel) ---
    if nombre in ("ModuleNotFoundError", "ImportError"):
        return "err_falta_driver"

    # --- base de datos ---
    if nombre in ("OperationalError", "InterfaceError", "DatabaseError"):
        if any(p in texto for p in ("password", "authentication", "login",
                                    "access denied", "contraseña")):
            return "err_credenciales"
        if any(p in texto for p in ("could not translate host", "unknown host",
                                    "name or service not known", "timeout",
                                    "connection refused", "no such host")):
            return "err_host"
        return "err_base_datos"
    if nombre == "ProgrammingError":
        return "err_consulta"

    # --- red ---
    if nombre in ("URLError", "HTTPError", "ConnectionError", "Timeout",
                  "TimeoutError", "ConnectionRefusedError", "SSLError",
                  "ConnectionResetError"):
        return "err_red"

    if contexto == "archivo":
        return "err_archivo_generico"
    if contexto == "conexion":
        return "err_base_datos"
    if contexto == "red":
        return "err_red"
    return None


def friendly_error(exc: BaseException, lang: str = DEFAULT_LANG,
                   contexto: str = "generico") -> tuple[str, str]:
    """Devuelve ``(mensaje_accionable, detalle_tecnico)``.

    El mensaje va traducido y dice qué hacer. El detalle técnico es
    ``TipoDeError: texto`` — se muestra plegado, nunca como respuesta
    principal, y sirve para reportar el problema."""
    clave = _clave_por_tipo(exc, contexto)
    mensaje = t(clave, lang) if clave else t("err_generico", lang)
    detalle = f"{_nombre_excepcion(exc)}: {exc}"
    return mensaje, detalle
