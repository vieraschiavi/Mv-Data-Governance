# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Pasar un audio a texto, con la clave del usuario.

Lo primero, porque es lo que importa
────────────────────────────────────
**Transcribir un audio acá manda ese audio a un servidor de un tercero.**

En este producto eso no es un detalle técnico: el audio es una reunión de un
cliente, donde se habla de sus sistemas, sus problemas y su gente con nombre
y apellido. Por eso:

  · Está APAGADO por defecto y no se enciende solo.
  · La pantalla lo pide explícitamente cada vez, no una casilla que se
    marcó una vez hace tres meses y nadie recuerda.
  · No hay ninguna transcripción "de fábrica": sin la clave del usuario esta
    función no hace nada, y el programa sigue funcionando entero con la
    transcripción que ya generó Zoom/Teams/Meet/WebEx, que es el camino
    recomendado — ahí el audio nunca sale de la infraestructura donde ya
    estaba.

Por qué no se transcribe localmente
───────────────────────────────────
Un modelo de voz que corra en la PC (Whisper y parientes) arrastra PyTorch:
cientos de megas de dependencias más los pesos del modelo, dentro del
instalador que baja cada cliente. Es la clase de decisión que se toma una
vez y se paga en cada descarga, cada actualización y cada antivirus
corporativo que mira un binario de 2 GB con desconfianza.

La alternativa honesta no es transcribir peor: es no transcribir nosotros.
Zoom, Teams, Meet y WebEx ya transcriben —y con el orador identificado, que
es algo que un audio de un micrófono no da— y exportan `.vtt` / `.srt` /
`.txt`. ``mvdg.meetings`` los lee sin red y sin clave.

Qué proveedores sirven
──────────────────────
Solo los que exponen transcripción de audio con una API key simple:

  openai       /v1/audio/transcriptions
  compatible   el mismo formato, contra la URL que configure el usuario
               (Groq, Azure OpenAI, un servidor propio con Whisper...)
  gemini       audio en línea dentro de generateContent

Claude no toma audio, así que con Claude configurado esta función avisa en
vez de fallar en silencio.
"""
from __future__ import annotations

import base64
import json
import mimetypes
import os
import urllib.error
import urllib.request
import uuid

# Un audio de una hora comprimido pesa decenas de megas y la subida es lenta;
# el timeout de las llamadas de texto (20 s) no alcanza ni de cerca.
_TIMEOUT = 300

#: Proveedores que pueden transcribir. Los demás quedan afuera a propósito.
PROVEEDORES = ("openai", "compatible", "gemini")

_MODELO_POR_DEFECTO = {
    "openai": "gpt-4o-transcribe",
    "compatible": "whisper-1",
    "gemini": "gemini-1.5-flash",
}

_VAR_MODELO = "MVDG_AI_MODEL_TRANSCRIPCION"

EXTENSIONES = (".mp3", ".mp4", ".m4a", ".wav", ".webm", ".ogg", ".flac", ".mpeg", ".mpga")


def _tr(es: str, en: str, pt: str) -> dict:
    return {"es": es, "en": en, "pt": pt}


_MOTIVOS = {
    "sin_proveedor": _tr(
        "No hay ninguna clave de IA configurada. Cargá la tuya en Ayuda → "
        "Configuración de IA, o subí la transcripción que ya generó Zoom, "
        "Teams, Meet o WebEx (no necesita clave ni internet).",
        "No AI key is configured. Add yours in Help → AI settings, or upload "
        "the transcript Zoom, Teams, Meet or WebEx already generated (needs "
        "no key and no internet).",
        "Não há nenhuma chave de IA configurada. Carregue a sua em Ajuda → "
        "Configuração de IA, ou envie a transcrição que o Zoom, Teams, Meet "
        "ou WebEx já gerou (não precisa de chave nem internet)."),
    "proveedor_sin_audio": _tr(
        "El proveedor configurado no transcribe audio. Solo pueden ChatGPT "
        "(OpenAI), Gemini y los servicios compatibles con OpenAI. Podés subir "
        "la transcripción de la plataforma en su lugar.",
        "The configured provider does not transcribe audio. Only ChatGPT "
        "(OpenAI), Gemini and OpenAI-compatible services can. You can upload "
        "the platform's transcript instead.",
        "O provedor configurado não transcreve áudio. Apenas ChatGPT "
        "(OpenAI), Gemini e serviços compatíveis com OpenAI conseguem. Você "
        "pode enviar a transcrição da plataforma."),
    "sin_audio": _tr("No se recibió ningún audio.", "No audio was received.",
                     "Nenhum áudio foi recebido."),
    "fallo": _tr(
        "El proveedor no pudo transcribir el audio. Revisá la conexión y la "
        "clave; si el archivo es muy largo, probá partirlo.",
        "The provider could not transcribe the audio. Check the connection "
        "and the key; if the file is very long, try splitting it.",
        "O provedor não conseguiu transcrever o áudio. Verifique a conexão e "
        "a chave; se o arquivo for muito longo, tente dividi-lo."),
}


def motivo(clave: str, lang: str = "es") -> str:
    bloque = _MOTIVOS.get(clave, _MOTIVOS["fallo"])
    return bloque.get(lang, bloque["es"])


def proveedor_disponible() -> str | None:
    """El proveedor configurado, SI puede transcribir audio. Si no, ``None``."""
    from . import ai_provider

    actual = ai_provider.configured_provider()
    return actual if actual in PROVEEDORES else None


def _modelo(proveedor: str) -> str:
    return (os.environ.get(_VAR_MODELO, "").strip()
            or _MODELO_POR_DEFECTO.get(proveedor, "whisper-1"))


def _tipo_mime(nombre: str) -> str:
    return mimetypes.guess_type(nombre)[0] or "application/octet-stream"


def _multipart(campos: dict[str, str], nombre_archivo: str,
               audio: bytes) -> tuple[bytes, str]:
    """Arma un cuerpo multipart/form-data a mano.

    A mano y no con `requests` porque `requests` no es dependencia de este
    proyecto y sumarla para una sola llamada opcional sería pagar un paquete
    entero —y su cadena de dependencias— dentro del instalador de cada
    cliente. El formato es cuatro líneas de texto por campo.
    """
    borde = f"----mvdg{uuid.uuid4().hex}"
    partes: list[bytes] = []
    for clave, valor in campos.items():
        partes.append(
            f'--{borde}\r\nContent-Disposition: form-data; name="{clave}"\r\n\r\n'
            f"{valor}\r\n".encode())
    partes.append(
        f'--{borde}\r\nContent-Disposition: form-data; name="file"; '
        f'filename="{os.path.basename(nombre_archivo)}"\r\n'
        f"Content-Type: {_tipo_mime(nombre_archivo)}\r\n\r\n".encode())
    partes.append(audio)
    partes.append(f"\r\n--{borde}--\r\n".encode())
    return b"".join(partes), f"multipart/form-data; boundary={borde}"


def _base_openai(proveedor: str) -> str:
    if proveedor != "compatible":
        return "https://api.openai.com/v1"
    return (os.environ.get("MVDG_AI_BASE_URL", "").strip().rstrip("/")
            or "https://api.openai.com/v1")


def _openai_shape(audio: bytes, nombre: str, api_key: str, proveedor: str) -> str:
    cuerpo, tipo = _multipart({"model": _modelo(proveedor),
                               "response_format": "text"}, nombre, audio)
    pedido = urllib.request.Request(
        f"{_base_openai(proveedor)}/audio/transcriptions", data=cuerpo,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": tipo})
    with urllib.request.urlopen(pedido, timeout=_TIMEOUT) as r:  # noqa: S310
        return r.read().decode("utf-8", "replace").strip()


def _gemini(audio: bytes, nombre: str, api_key: str, _proveedor: str) -> str:
    modelo = _modelo("gemini")
    cuerpo = json.dumps({"contents": [{"parts": [
        {"text": "Transcribe this audio verbatim. Keep speaker labels if you "
                 "can tell them apart, one line per turn as 'Name: text'. "
                 "Do not summarize."},
        {"inline_data": {"mime_type": _tipo_mime(nombre),
                         "data": base64.b64encode(audio).decode()}},
    ]}]}).encode()
    pedido = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{modelo}:generateContent?key={api_key}",
        data=cuerpo, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(pedido, timeout=_TIMEOUT) as r:  # noqa: S310
        data = json.loads(r.read().decode())
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


_MOTORES = {"openai": _openai_shape, "compatible": _openai_shape, "gemini": _gemini}


def transcribir(audio: bytes, nombre: str = "reunion.wav",
                lang: str = "es") -> dict:
    """Audio → texto, con el proveedor que el usuario configuró.

    Devuelve siempre un ``dict``: ``{"ok": True, "texto": ...}`` o
    ``{"ok": False, "motivo": <clave>, "mensaje": <texto traducido>}``. Nunca
    lanza — un fallo de red no puede tirar abajo la pantalla de una reunión
    que alguien está tomando en vivo.

    El audio se manda al proveedor. Quien llama tiene que haber preguntado
    antes: acá no se pide permiso, se asume que ya se pidió.
    """
    if not audio:
        return {"ok": False, "motivo": "sin_audio", "mensaje": motivo("sin_audio", lang)}

    from . import ai_provider

    actual = ai_provider.configured_provider()
    if not actual:
        return {"ok": False, "motivo": "sin_proveedor",
                "mensaje": motivo("sin_proveedor", lang)}
    if actual not in _MOTORES:
        return {"ok": False, "motivo": "proveedor_sin_audio",
                "mensaje": motivo("proveedor_sin_audio", lang)}

    api_key = ai_provider._key_for(actual)
    if not api_key:
        return {"ok": False, "motivo": "sin_proveedor",
                "mensaje": motivo("sin_proveedor", lang)}
    try:
        texto = _MOTORES[actual](audio, nombre, api_key, actual)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
            KeyError, IndexError, ValueError, OSError):
        return {"ok": False, "motivo": "fallo", "mensaje": motivo("fallo", lang)}
    if not texto:
        return {"ok": False, "motivo": "fallo", "mensaje": motivo("fallo", lang)}
    return {"ok": True, "texto": texto, "proveedor": actual, "modelo": _modelo(actual)}
