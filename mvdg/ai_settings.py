"""
MV Data Governance · Preferencias de IA: qué proveedor, qué modelo, qué key.

Para qué
--------
Hasta acá la IA externa se configuraba SOLO con variables de entorno, que es
cómodo para un servidor y hostil para alguien que abre un .exe: hay que cerrar
el programa, tocar variables del sistema y volver a abrirlo. Este módulo pone
esa configuración adentro del programa.

Y agrega lo que pedía el uso real: **elegir el modelo**. No es un detalle
estético — entre el modelo más chico y el más grande de un mismo proveedor hay
un orden de magnitud de diferencia en costo por llamada, y el que paga es el
usuario con su propia API key. Dejarlo clavado en un default sería decidirle
el gasto.

Cómo se guarda cada cosa
------------------------
* La **API key** es un secreto: va al keyring del sistema operativo, con el
  mismo mecanismo (y el mismo respaldo ofuscado) que ya usan las contraseñas
  de conexión en ``mvdg.connectors``. No se escribe un segundo almacén de
  secretos: uno solo, auditado en un lugar.
* El **modelo elegido** y la **lista de modelos** no son secretos y van a un
  JSON en la carpeta de datos. Meterlos en el keyring sería usar un candado
  para guardar el diario.

La variable de entorno le gana a lo guardado
--------------------------------------------
Si alguien exporta ``ANTHROPIC_API_KEY``, esa manda. Es lo que espera quien
automatiza (CI, un servidor, un contenedor): la configuración explícita del
entorno no puede quedar tapada por algo que alguien guardó una vez desde la
interfaz.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

from .clients import data_dir

_ARCHIVO = "ia_preferencias.json"
_TIMEOUT = 15

# ---------------------------------------------------------------------------
# Los proveedores que el usuario puede elegir.
#
# `listado` es cómo se le pregunta a cada uno qué modelos tiene HOY. Esa es la
# razón del botón "Actualizar": los proveedores sacan modelos nuevos todo el
# tiempo, y una lista hardcodeada envejece mal — a los dos meses el programa
# ofrece modelos viejos y esconde los nuevos, que suelen ser más baratos.
#
# `base` vacío = el proveedor no habla el formato de OpenAI y tiene su propia
# forma (Anthropic y Gemini).
# ---------------------------------------------------------------------------
PROVEEDORES = {
    "claude": {
        "etiqueta": "Claude (Anthropic)",
        "env_key": "ANTHROPIC_API_KEY",
        "base": "https://api.anthropic.com/v1",
        "listado": "anthropic",
        "default": "claude-sonnet-5",
    },
    "openai": {
        "etiqueta": "ChatGPT (OpenAI)",
        "env_key": "OPENAI_API_KEY",
        "base": "https://api.openai.com/v1",
        "listado": "openai",
        "default": "gpt-4o-mini",
    },
    "gemini": {
        "etiqueta": "Gemini (Google)",
        "env_key": "GEMINI_API_KEY",
        "base": "https://generativelanguage.googleapis.com/v1beta",
        "listado": "gemini",
        "default": "gemini-1.5-flash",
    },
    "grok": {
        "etiqueta": "Grok (xAI)",
        "env_key": "XAI_API_KEY",
        "base": "https://api.x.ai/v1",
        "listado": "openai",          # xAI expone la API con forma de OpenAI
        "default": "grok-2-latest",
    },
    "compatible": {
        "etiqueta": "Otro (compatible con OpenAI)",
        "env_key": "MVDG_AI_API_KEY",
        "base": "",                   # lo pone el usuario
        "listado": "openai",
        "default": "",
    },
}

# GitHub Copilot NO está en la lista, y no es un olvido: no expone una API
# REST de "pedime un texto" con solo una key — se autentica por OAuth de
# GitHub adentro de un IDE. Ofrecerlo sería poner una opción que nunca puede
# funcionar. Quien use un gateway que lo exponga en formato OpenAI lo entra
# por "compatible".
SIN_API_PROPIA = {"copilot": "GitHub Copilot"}


def _archivo() -> str:
    return os.path.join(data_dir(), _ARCHIVO)


def _leer() -> dict:
    try:
        with open(_archivo(), encoding="utf-8") as fh:
            datos = json.load(fh)
        return datos if isinstance(datos, dict) else {}
    except (OSError, ValueError):
        return {}


def _escribir(datos: dict) -> None:
    destino = _archivo()
    tmp = destino + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(datos, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, destino)


# ------------------------------------------------------------------ API key
def _id_keyring(proveedor: str) -> str:
    return f"ia:{proveedor}"


def guardar_key(proveedor: str, key: str) -> str:
    """Guarda la API key. Devuelve dónde quedó, para poder decírselo al
    usuario: no es lo mismo el keyring del SO que el respaldo ofuscado."""
    from .connectors import _keyring_delete, _keyring_set
    if proveedor not in PROVEEDORES:
        raise ValueError(f"proveedor desconocido: {proveedor}")
    key = (key or "").strip()
    datos = _leer()
    respaldo = datos.setdefault("keys", {})
    if not key:
        _keyring_delete(_id_keyring(proveedor))
        respaldo.pop(proveedor, None)
        _escribir(datos)
        return "borrada"
    if _keyring_set(_id_keyring(proveedor), key):
        respaldo.pop(proveedor, None)     # no dejar copia en claro al lado
        _escribir(datos)
        return "keyring"
    # Sin keyring del SO (Linux headless, por ejemplo) se guarda ofuscada, que
    # es lo que ya hace connectors para las contraseñas. Se DEVUELVE distinto
    # para que la interfaz pueda avisarlo: ofuscado no es cifrado.
    from .connectors import _obfuscate
    respaldo[proveedor] = _obfuscate(key)
    _escribir(datos)
    return "ofuscada"


def leer_key(proveedor: str) -> str:
    """La API key vigente: primero la variable de entorno, después lo
    guardado. El entorno gana porque es la configuración explícita de quien
    automatiza."""
    cfg = PROVEEDORES.get(proveedor)
    if not cfg:
        return ""
    del_entorno = (os.environ.get(cfg["env_key"]) or "").strip()
    if del_entorno:
        return del_entorno
    from .connectors import _deobfuscate, _keyring_get
    guardada = _keyring_get(_id_keyring(proveedor))
    if guardada:
        return guardada
    crudo = _leer().get("keys", {}).get(proveedor, "")
    return _deobfuscate(crudo) if crudo else ""


# ------------------------------------------------------------------- modelo
def guardar_modelo(proveedor: str, modelo: str) -> None:
    datos = _leer()
    datos.setdefault("modelos", {})[proveedor] = (modelo or "").strip()
    _escribir(datos)


def modelo_elegido(proveedor: str) -> str:
    """El modelo a usar: el elegido por el usuario, o el default del
    proveedor. Nunca vacío para los proveedores que tienen default."""
    guardado = _leer().get("modelos", {}).get(proveedor, "")
    if guardado:
        return guardado
    return PROVEEDORES.get(proveedor, {}).get("default", "")


def base_url(proveedor: str) -> str:
    """La URL base. Para "compatible" la pone el usuario; se le saca el
    /chat/completions si lo pegó de la doc del proveedor, que es el error de
    tipeo más común y termina en un 404 que se lee como "la IA no anda"."""
    cfg = PROVEEDORES.get(proveedor, {})
    if cfg.get("base"):
        return cfg["base"]
    guardada = _leer().get("base_url", "") or os.environ.get("MVDG_AI_BASE_URL", "")
    guardada = guardada.strip().rstrip("/")
    if guardada.endswith("/chat/completions"):
        guardada = guardada[: -len("/chat/completions")]
    return guardada


def guardar_base_url(url: str) -> None:
    datos = _leer()
    datos["base_url"] = (url or "").strip()
    _escribir(datos)


# ------------------------------------------------- listado de modelos (vivo)
def _get_json(url: str, headers: dict) -> dict:
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def listar_modelos(proveedor: str) -> list[str]:
    """Le pregunta al proveedor qué modelos tiene disponibles para ESA key.

    Es lo que hace el botón "Actualizar". Devuelve lista vacía si no se puede
    (sin key, sin internet, endpoint que cambió): el llamador muestra el
    aviso y el usuario sigue con el modelo que ya tenía. Nunca lanza — quedar
    sin lista es un contratiempo, no un error del programa.
    """
    cfg = PROVEEDORES.get(proveedor)
    key = leer_key(proveedor)
    if not cfg or not key:
        return []
    base = base_url(proveedor)
    if not base:
        return []
    try:
        if cfg["listado"] == "anthropic":
            datos = _get_json(f"{base}/models",
                              {"x-api-key": key, "anthropic-version": "2023-06-01"})
            nombres = [m.get("id", "") for m in datos.get("data", [])]
        elif cfg["listado"] == "gemini":
            datos = _get_json(f"{base}/models?key={key}", {})
            # Gemini devuelve "models/gemini-1.5-flash"; se muestra el nombre
            # corto, que es el que después hay que mandar en la llamada.
            nombres = [m.get("name", "").split("/")[-1]
                       for m in datos.get("models", [])]
        else:                       # forma de OpenAI (OpenAI, xAI, y compatibles)
            datos = _get_json(f"{base}/models", {"Authorization": f"Bearer {key}"})
            nombres = [m.get("id", "") for m in datos.get("data", [])]
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
            ValueError, KeyError, TypeError, OSError):
        return []
    return sorted({n for n in nombres if n})


def refrescar_modelos(proveedor: str) -> list[str]:
    """Pide la lista al proveedor y la cachea. Si la consulta falla se
    CONSERVA la lista anterior: dejar al usuario sin opciones porque se cayó
    internet un segundo sería peor que mostrarle una lista de ayer."""
    nombres = listar_modelos(proveedor)
    if not nombres:
        return modelos_conocidos(proveedor)
    datos = _leer()
    datos.setdefault("catalogo", {})[proveedor] = {
        "modelos": nombres, "actualizado": int(time.time()),
    }
    _escribir(datos)
    return nombres


def modelos_conocidos(proveedor: str) -> list[str]:
    """La última lista traída del proveedor. Si nunca se actualizó, al menos
    el default, para que el desplegable no aparezca vacío."""
    entrada = _leer().get("catalogo", {}).get(proveedor, {})
    modelos = entrada.get("modelos") or []
    if modelos:
        return list(modelos)
    default = PROVEEDORES.get(proveedor, {}).get("default", "")
    return [default] if default else []


def actualizado_en(proveedor: str) -> int:
    """Cuándo se trajo la lista por última vez (epoch), o 0."""
    return int(_leer().get("catalogo", {}).get(proveedor, {}).get("actualizado", 0))


def proveedores_configurados() -> list[str]:
    """Los que tienen key cargada, en el orden de PROVEEDORES."""
    return [p for p in PROVEEDORES if leer_key(p)]
