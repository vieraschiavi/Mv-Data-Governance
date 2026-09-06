# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · El relevamiento: preguntar, anotar quién respondió, repreguntar.

Qué resuelve
────────────
El banco de preguntas vive en ``mvdg.interview_bank``. Este módulo es lo que
lo convierte en trabajo: guarda POR CLIENTE quién respondió qué, mide cuánto
del pipeline quedó cubierto, y —lo que más se usa— dice **qué repreguntar**
cuando una respuesta quedó a medias.

Las repreguntas funcionan SIN clave de IA
─────────────────────────────────────────
Es la decisión de diseño que sostiene el módulo. Una respuesta a medias tiene
formas reconocibles, y reconocerlas no necesita un modelo:

  · se preguntó "cada cuánto" o "cuántos" y la respuesta no trae un número;
  · la respuesta dice "depende", "más o menos", "creo que", "a veces";
  · se preguntó por un responsable y no hay ningún nombre ni área;
  · la respuesta tiene cuatro palabras.

Cada una de esas dispara una repregunta concreta, más las que el banco ya
trae escritas para esa pregunta puntual. Con una clave de IA configurada se
agregan además repreguntas generadas sobre la respuesta exacta
(``ai_provider.ai_follow_ups``) — pero eso es un extra, no el camino: un
relevamiento se hace en la sala de reuniones de un cliente, que es
exactamente donde puede no haber internet.

Dónde se guarda
───────────────
En la carpeta del cliente (``mvdg.workspace.client_root``), un JSON por
cliente. Va ahí y no en un archivo global porque las respuestas de Conaprole
no tienen por qué viajar en el mismo archivo que las de otro cliente — y
porque así el proyecto entero de un cliente se exporta o se borra de una
sola vez, que es lo que se necesita cuando el proyecto termina.
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
from datetime import datetime, timezone

import pandas as pd

from .interview_bank import PREGUNTAS

_ARCHIVO = "relevamiento.json"

#: Estados de una pregunta dentro del relevamiento.
ESTADOS = ("pendiente", "respondida", "no_aplica")


def _tr(es: str, en: str, pt: str) -> dict:
    return {"es": es, "en": en, "pt": pt}


def _texto(bloque: dict, lang: str) -> str:
    return bloque.get(lang, bloque["es"])


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _plano(texto: str) -> str:
    sin = unicodedata.normalize("NFD", str(texto).lower())
    return "".join(c for c in sin if unicodedata.category(c) != "Mn")


# ---------------------------------------------------------------------------
# Las áreas: las mismas 12 etapas del pipeline, no una taxonomía paralela
# ---------------------------------------------------------------------------
def areas(lang: str = "es") -> list[dict]:
    """Las áreas del pipeline que tienen preguntas, en el orden del pipeline.

    Salen de ``mvdg.pipeline_doc``: preguntar y construir tienen que hablar
    de las mismas etapas, o el relevamiento termina cubriendo un pipeline
    que no es el que se implementa.
    """
    from . import pipeline_doc

    con_preguntas = {q["area"] for q in PREGUNTAS}
    return [{"key": e["key"], "n": e["n"], "titulo": e["titulo"],
             "preguntas": sum(1 for q in PREGUNTAS if q["area"] == e["key"])}
            for e in pipeline_doc.documentar(lang) if e["key"] in con_preguntas]


def questions(lang: str = "es", area: str | None = None) -> list[dict]:
    """Las preguntas traducidas, opcionalmente filtradas por área."""
    salida = []
    for q in PREGUNTAS:
        if area and q["area"] != area:
            continue
        salida.append({
            "id": q["id"], "area": q["area"],
            "pregunta": _texto(q["pregunta"], lang),
            "porque": _texto(q["porque"], lang),
            "a_quien": _texto(q["a_quien"], lang),
            "repreguntas": [_texto(r, lang) for r in q["repreguntas"]],
        })
    return salida


def question(qid: str, lang: str = "es") -> dict | None:
    return next((q for q in questions(lang) if q["id"] == qid), None)


# ---------------------------------------------------------------------------
# Respuestas guardadas, por cliente
# ---------------------------------------------------------------------------
def _archivo(client_id: str) -> str:
    from . import workspace
    return os.path.join(workspace.client_root(client_id), _ARCHIVO)


def load_answers(client_id: str) -> dict:
    """``{qid: {responsable, area_responsable, respuesta, estado, fecha}}``."""
    ruta = _archivo(client_id)
    if not os.path.exists(ruta):
        return {}
    try:
        with open(ruta, encoding="utf-8") as fh:
            datos = json.load(fh)
        return datos if isinstance(datos, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _guardar(client_id: str, datos: dict) -> None:
    ruta = _archivo(client_id)
    tmp = ruta + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(datos, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, ruta)


def save_answer(client_id: str, qid: str, respuesta: str = "",
                responsable: str = "", area_responsable: str = "",
                estado: str = "", notas: str = "") -> dict:
    """Anota (o actualiza) la respuesta de una pregunta y persiste a disco.

    El ``estado`` se deduce si no se pasa: con texto es ``respondida``, sin
    texto vuelve a ``pendiente``. Borrar una respuesta tiene que dejar la
    pregunta pendiente otra vez, no "respondida en blanco".
    """
    datos = load_answers(client_id)
    if not estado:
        estado = "respondida" if str(respuesta).strip() else "pendiente"
    datos[qid] = {
        "respuesta": str(respuesta).strip(),
        "responsable": str(responsable).strip(),
        "area_responsable": str(area_responsable).strip(),
        "estado": estado if estado in ESTADOS else "pendiente",
        "notas": str(notas).strip(),
        "fecha": _ahora(),
    }
    _guardar(client_id, datos)
    return datos[qid]


def delete_answer(client_id: str, qid: str) -> bool:
    datos = load_answers(client_id)
    if qid not in datos:
        return False
    del datos[qid]
    _guardar(client_id, datos)
    return True


# ---------------------------------------------------------------------------
# Cuánto del pipeline quedó cubierto
# ---------------------------------------------------------------------------
def answers_df(client_id: str, lang: str = "es") -> pd.DataFrame:
    """Todas las preguntas con su respuesta (o vacía), lista para mostrar."""
    guardadas = load_answers(client_id)
    titulos = {a["key"]: a["titulo"] for a in areas(lang)}
    filas = []
    for q in questions(lang):
        r = guardadas.get(q["id"], {})
        filas.append({
            "id": q["id"], "area": titulos.get(q["area"], q["area"]),
            "area_id": q["area"], "pregunta": q["pregunta"],
            "a_quien": q["a_quien"], "porque": q["porque"],
            "responsable": r.get("responsable", ""),
            "area_responsable": r.get("area_responsable", ""),
            "respuesta": r.get("respuesta", ""),
            "estado": r.get("estado", "pendiente"),
            "notas": r.get("notas", ""),
            "fecha": r.get("fecha", ""),
        })
    return pd.DataFrame(filas)


def progress(client_id: str, lang: str = "es") -> pd.DataFrame:
    """Cobertura por área: cuántas preguntas hay, cuántas se respondieron.

    Es lo que se mira antes de cerrar una reunión: qué área quedó sin tocar.
    Un relevamiento con el 90% en ingesta y 0% en políticas no está al 45%
    — está entero por hacer del lado que va a frenar el proyecto.
    """
    df = answers_df(client_id, lang)
    if df.empty:
        return pd.DataFrame(columns=["area", "preguntas", "respondidas",
                                     "no_aplica", "cobertura_%"])
    orden = {a["key"]: a["n"] for a in areas(lang)}
    filas = []
    for area_id, grupo in df.groupby("area_id", sort=False):
        respondidas = int((grupo["estado"] == "respondida").sum())
        no_aplica = int((grupo["estado"] == "no_aplica").sum())
        cuentan = len(grupo) - no_aplica
        filas.append({
            "n": orden.get(area_id, 99),
            "area": grupo["area"].iloc[0],
            "preguntas": len(grupo),
            "respondidas": respondidas,
            "no_aplica": no_aplica,
            "cobertura_%": round(respondidas * 100 / cuentan, 1) if cuentan else 100.0,
        })
    return (pd.DataFrame(filas).sort_values("n", ignore_index=True)
            .drop(columns=["n"]))


def overall_coverage(client_id: str) -> float:
    """Un número: qué porcentaje del banco está respondido (0-100)."""
    guardadas = load_answers(client_id)
    aplican = [q for q in PREGUNTAS
               if guardadas.get(q["id"], {}).get("estado") != "no_aplica"]
    if not aplican:
        return 100.0
    respondidas = sum(1 for q in aplican
                      if guardadas.get(q["id"], {}).get("estado") == "respondida")
    return round(respondidas * 100 / len(aplican), 1)


# ---------------------------------------------------------------------------
# El casillero de repreguntas
# ---------------------------------------------------------------------------
# Detectores de respuesta a medias. Cada uno mira UNA cosa y, si pega, aporta
# una repregunta. Son deliberadamente pocos y explicables: el consultor tiene
# que poder mirar la repregunta y entender por qué se la propusieron.

_VAGAS = _tr(
    "depende|mas o menos|creo que|me parece|a veces|varia|no se|no estoy seguro|"
    "habria que ver|en general|por ahi|algo asi",
    "it depends|more or less|i think|i guess|sometimes|varies|i don't know|"
    "not sure|we'd have to check|in general|kind of",
    "depende|mais ou menos|acho que|as vezes|varia|nao sei|nao tenho certeza|"
    "teria que ver|em geral|mais ou menos isso")

_PIDE_NUMERO = _tr(
    "cuanto|cuantos|cuantas|cada cuanto|con que frecuencia|volumen|"
    "que porcentaje|cuanto tarda",
    "how much|how many|how often|how long|volume|what percentage",
    "quanto|quantos|quantas|com que frequencia|volume|que percentual")

_PIDE_PERSONA = _tr(
    "quien|responsable|dueno|steward|a cargo|autoriza|decide",
    "who |owner|steward|responsible|in charge|authorise|authorize|decides",
    "quem|responsavel|dono|steward|a cargo|autoriza|decide")

_REPREGUNTAS_GENERICAS = {
    "sin_numero": _tr(
        "La respuesta no trae ningún número. ¿Cuánto/cuántos exactamente? "
        "Un número aproximado sirve más que ninguno.",
        "The answer has no number in it. How much/how many exactly? "
        "An approximate number is worth more than none.",
        "A resposta não traz nenhum número. Quanto/quantos exatamente? "
        "Um número aproximado vale mais que nenhum."),
    "sin_persona": _tr(
        "No quedó un nombre ni un área. ¿Quién específicamente, con nombre y "
        "apellido o al menos el cargo?",
        "No name or area was given. Who specifically, by name or at least by "
        "role?",
        "Não ficou um nome nem uma área. Quem especificamente, com nome ou ao "
        "menos o cargo?"),
    "vaga": _tr(
        "La respuesta quedó en condicional. ¿Podés dar un ejemplo concreto de "
        "la última vez que pasó?",
        "The answer stayed conditional. Can you give a concrete example of the "
        "last time it happened?",
        "A resposta ficou no condicional. Pode dar um exemplo concreto da "
        "última vez que aconteceu?"),
    "corta": _tr(
        "La respuesta es muy corta para dejarla anotada así. ¿Qué habría que "
        "agregarle para que alguien que no estuvo en la reunión la entienda?",
        "The answer is too short to record as is. What would you add so that "
        "someone who was not in the meeting understands it?",
        "A resposta é curta demais para ficar registrada assim. O que "
        "acrescentaria para quem não esteve na reunião entender?"),
    "sin_responder": _tr(
        "Todavía sin responder. Antes de cerrar el relevamiento hay que "
        "preguntarla o marcarla como que no aplica.",
        "Still unanswered. Before closing the interview it has to be asked or "
        "marked as not applicable.",
        "Ainda sem resposta. Antes de fechar o levantamento é preciso "
        "perguntá-la ou marcá-la como não aplicável."),
}

_MINIMO_PALABRAS = 6


def _pega(patron: dict, texto_plano: str, lang: str) -> bool:
    return any(p and p in texto_plano
               for p in _texto(patron, lang).split("|"))


def follow_ups(qid: str, respuesta: str, lang: str = "es") -> list[str]:
    """Qué repreguntar. Local, determinístico, sin red y sin clave.

    Devuelve primero las repreguntas que dispararon los detectores (las que
    apuntan a lo que ESTA respuesta dejó abierto) y después las que el banco
    trae escritas para la pregunta. Ese orden importa: lo específico arriba,
    porque en una reunión se leen las dos primeras y listo.
    """
    q = question(qid, lang)
    if not q:
        return []
    dicho = str(respuesta).strip()
    if not dicho:
        return [_texto(_REPREGUNTAS_GENERICAS["sin_responder"], lang), *q["repreguntas"]]

    plano_pregunta = _plano(q["pregunta"])
    plano_respuesta = _plano(dicho)
    salida: list[str] = []

    if _pega(_PIDE_NUMERO, plano_pregunta, lang) and not re.search(r"\d", dicho):
        salida.append(_texto(_REPREGUNTAS_GENERICAS["sin_numero"], lang))
    if _pega(_PIDE_PERSONA, plano_pregunta, lang) and len(dicho.split()) < 4:
        salida.append(_texto(_REPREGUNTAS_GENERICAS["sin_persona"], lang))
    if _pega(_VAGAS, plano_respuesta, lang):
        salida.append(_texto(_REPREGUNTAS_GENERICAS["vaga"], lang))
    if len(dicho.split()) < _MINIMO_PALABRAS:
        salida.append(_texto(_REPREGUNTAS_GENERICAS["corta"], lang))

    for extra in q["repreguntas"]:
        if extra not in salida:
            salida.append(extra)
    return salida


def ai_follow_ups(qid: str, respuesta: str, lang: str = "es") -> list[str] | None:
    """Repreguntas generadas sobre ESTA respuesta, si hay clave configurada.

    ``None`` cuando no hay proveedor o la llamada falla — el llamador ya
    tiene :func:`follow_ups`, que no depende de nada. Manda al proveedor la
    pregunta y la respuesta del cliente: quien llama tiene que haberlo
    advertido en pantalla.
    """
    from . import ai_provider

    q = question(qid, lang)
    if not q:
        return None
    titulo = next((a["titulo"] for a in areas(lang) if a["key"] == q["area"]), q["area"])
    return ai_provider.ai_follow_ups(q["pregunta"], respuesta, titulo, lang)


# ---------------------------------------------------------------------------
# Salida
# ---------------------------------------------------------------------------
_DOC_TITULO = _tr("Relevamiento del pipeline de datos",
                  "Data pipeline discovery",
                  "Levantamento do pipeline de dados")
_DOC_SUB = _tr("Preguntas por área del pipeline, con quién respondió cada una.",
               "Questions by pipeline area, with who answered each one.",
               "Perguntas por área do pipeline, com quem respondeu cada uma.")
_ET = {
    "respuesta": _tr("Respuesta", "Answer", "Resposta"),
    "responsable": _tr("Respondió", "Answered by", "Respondeu"),
    "porque": _tr("Por qué se pregunta", "Why it is asked", "Por que se pergunta"),
    "a_quien": _tr("A quién preguntarle", "Who to ask", "A quem perguntar"),
    "sin_responder": _tr("Sin responder", "Unanswered", "Sem resposta"),
    "no_aplica": _tr("No aplica", "Not applicable", "Não se aplica"),
    "cobertura": _tr("Cobertura", "Coverage", "Cobertura"),
    "cliente": _tr("Cliente", "Client", "Cliente"),
    "pie": _tr("MV Data Governance · relevamiento",
               "MV Data Governance · discovery",
               "MV Data Governance · levantamento"),
}


def to_document(client_id: str, lang: str = "es", nombre_cliente: str = "") -> dict:
    """El relevamiento como documento para ``mvdg.doc_export`` (HTML/Word/PDF).

    Se agrupa por área del pipeline y cada área es una sección: es el orden
    en que se hace el trabajo, así que es el orden en que se lee.
    """
    df = answers_df(client_id, lang)
    secciones = []
    for n, (area_id, grupo) in enumerate(df.groupby("area_id", sort=False), start=1):
        bloques = []
        for _, fila in grupo.iterrows():
            if fila["estado"] == "no_aplica":
                dicho = _texto(_ET["no_aplica"], lang)
            else:
                dicho = fila["respuesta"] or _texto(_ET["sin_responder"], lang)
            quien = " · ".join(x for x in (fila["responsable"],
                                           fila["area_responsable"]) if x)
            bloques.append((f"{fila['id']} · {fila['pregunta']}", dicho))
            if quien:
                bloques.append((_texto(_ET["responsable"], lang), quien))
        secciones.append({
            "n": n, "titulo": grupo["area"].iloc[0], "modulo": f"{area_id}",
            "bloques": bloques,
            "evidencia": f"{int((grupo['estado'] == 'respondida').sum())}/{len(grupo)}",
            "evidencia_etiqueta": _texto(_ET["cobertura"], lang),
        })
    return {
        "titulo": _texto(_DOC_TITULO, lang),
        "subtitulo": _texto(_DOC_SUB, lang),
        "lang": lang,
        "meta": [
            (_texto(_ET["cliente"], lang), nombre_cliente or client_id),
            (_texto(_ET["cobertura"], lang), f"{overall_coverage(client_id)}%"),
        ],
        "pie": _texto(_ET["pie"], lang),
        "secciones": secciones,
    }
