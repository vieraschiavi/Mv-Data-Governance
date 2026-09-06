# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Reuniones: de lo que se dijo a lo que hay que hacer.

El problema
───────────
El relevamiento de un cliente pasa en reuniones. Alguien dice "el maestro de
clientes lo mantiene Comercial, pero los códigos viejos los pisa el ERP de
noche" y esa frase vale más que una semana de perfilado — porque explica un
defecto que los datos muestran pero no justifican. Después nadie se acuerda
de quién lo dijo, y la decisión se vuelve a discutir en la reunión siguiente.

Qué hace este módulo
────────────────────
1. Lee la transcripción de la reunión y la parte en intervenciones con
   ORADOR, MINUTO y TEXTO.
2. Arma la minuta: quién habló, cuánto, y qué dijo cada uno.
3. Marca los hallazgos —decisiones, compromisos, riesgos, pendientes,
   preguntas abiertas— con la CITA TEXTUAL y el minuto. Nunca parafrasea un
   compromiso: un "yo no dije eso" se gana mostrando el minuto, no un
   resumen.
4. Los cruza con las 12 etapas del pipeline (``mvdg.pipeline_doc``), que es
   para lo que se hizo la reunión: saber qué toca hacer en ingesta, en
   calidad, en linaje.

De dónde sale la transcripción
──────────────────────────────
Tres caminos, en orden de menos a más frágil:

  · **La que ya generó la plataforma.** Zoom, Teams, Meet y WebEx graban y
    exportan `.vtt` / `.srt` / `.txt`, y ahí el ORADOR viene identificado
    por el sistema que sabe quién tenía el micrófono abierto. Es el camino
    bueno y no necesita ni red ni IA: se parsea acá con la biblioteca
    estándar.
  · **Un audio, transcrito con la clave del usuario** (``mvdg.transcribe``).
    Opcional y apagado por defecto, porque el audio de una reunión de un
    cliente sale de la máquina — ver la advertencia de ese módulo.
  · **Pegar el texto a mano.** Siempre funciona.

Qué NO hace
───────────
No separa oradores de un audio de una reunión presencial: un solo micrófono
da un solo canal, y distinguir voces (diarización) necesita un modelo pesado
que no puede viajar dentro del instalador de cada cliente. Cuando la
transcripción no trae orador, las intervenciones quedan sin asignar y la
pantalla deja asignarlas a mano. Es preferible a inventar una atribución:
una minuta que le pone en la boca a alguien algo que no dijo es peor que no
tener minuta.
"""
from __future__ import annotations

import re
import unicodedata

import pandas as pd

SIN_ORADOR = ""

# Tipos de hallazgo, en el orden en que le importan a quien lee la minuta.
TIPOS = ("decision", "compromiso", "riesgo", "pendiente", "pregunta", "dato")


def _tr(es: str, en: str, pt: str) -> dict:
    return {"es": es, "en": en, "pt": pt}


def _texto(bloque: dict, lang: str) -> str:
    return bloque.get(lang, bloque["es"])


def _sin_tildes(texto: str) -> str:
    """Comparar sin acentos: en una transcripción automática son una lotería."""
    plano = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in plano if unicodedata.category(c) != "Mn")


# ---------------------------------------------------------------------------
# Parseo de transcripciones
# ---------------------------------------------------------------------------
# Los cuatro formatos que exportan las plataformas son variaciones del mismo
# esquema: una marca de tiempo y una línea de texto que puede venir con el
# nombre adelante. Se parsean juntos porque separarlos en cuatro funciones
# duplicaría el 90% del código y dejaría cuatro lugares donde arreglar el
# mismo borde.

# 00:01:23.456 --> 00:01:27.000   (VTT)   ·   00:01:23,456 --> ...  (SRT)
_TIEMPO = re.compile(
    r"(\d{1,2}:)?(\d{1,2}):(\d{2})[.,](\d{1,3})\s*-->\s*"
    r"(?:(\d{1,2}:)?(\d{1,2}):(\d{2})[.,](\d{1,3}))")

# <v Ana García>texto</v>  — así marca Teams (y a veces Zoom) al orador
_VOZ = re.compile(r"<v\s+([^>]+?)\s*>(.*?)(?:</v>)?\s*$", re.DOTALL)

# "Ana García: texto"  ·  "[00:01:23] Ana García: texto"  ·  "Ana (00:01) : texto"
# La regex solo separa por los dos puntos; decidir si lo de la izquierda es un
# nombre o una oración lo hace `_parece_nombre` más abajo, que es donde está
# el borde difícil.
#
# La marca de tiempo de dos partes se lee mm:ss, igual que la muestra `_mmss`:
# leerla como hh:mm mandaría el minuto 2 a la hora 2.
_MARCA = re.compile(r"^\s*\[?(\d{1,2}:\d{2}(?::\d{2})?)\]?\s*")
_NOMBRE = re.compile(r"^([^:]{1,60}?)\s*(?:\((?:\d{1,2}:\d{2}(?::\d{2})?)\))?\s*:\s+(.*)$")

_ETIQUETAS_VTT = ("WEBVTT", "NOTE", "STYLE", "REGION")


def _segundos(h, m, s, ms) -> float:
    return int(h[:-1] if h else 0) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def _mmss(segundos: float) -> str:
    total = int(segundos or 0)
    return f"{total // 60:02d}:{total % 60:02d}"


# Palabras que aparecen en una ORACIÓN y nunca en el nombre de una persona.
# Son el filtro contra el falso positivo que más daño hace: "El problema es
# este: el ERP pisa los códigos" tomado como una intervención de alguien
# llamado "El problema es este". Un solo caso así llena la tabla de oradores
# de nombres inventados, y a partir de ahí nadie le cree a la minuta.
#
# Es una lista de palabras funcionales y no un análisis gramatical a
# propósito: se puede leer, se puede auditar y se puede ampliar cuando
# aparezca un caso nuevo. Van sin tilde porque se comparan sin tilde.
_PALABRAS_DE_PROSA = frozenset("""
es son era eran esta estan hay tiene tienen que porque pero cuando como esto
este esta eso esa fue seria van no si lo nos les del para por con sin sobre
is are was were that this the what with there has have will would and but not
we you they our their from for about
e sao estao tem isso esse essa foi vai nao nos seu sua para por com sem sobre
""".split())

_MAX_PALABRAS_NOMBRE = 5


def _parece_nombre(candidato: str) -> bool:
    """¿Lo que hay antes de los dos puntos es un orador o una oración?"""
    if not candidato or candidato.endswith(".") or candidato[0].islower():
        return False
    palabras = candidato.split()
    if not palabras or len(palabras) > _MAX_PALABRAS_NOMBRE:
        return False
    return not any(_sin_tildes(p.strip("(),")) in _PALABRAS_DE_PROSA
                   for p in palabras)


def _partir_orador(linea: str) -> tuple[str, str]:
    """``"Ana García: hola"`` → ``("Ana García", "hola")``. Sin nombre: ``("", linea)``."""
    voz = _VOZ.match(linea.strip())
    if voz:
        return voz.group(1).strip(), voz.group(2).strip()
    m = _NOMBRE.match(linea)
    if not m:
        return SIN_ORADOR, linea.strip()
    nombre = m.group(1).strip()
    if not _parece_nombre(nombre):
        return SIN_ORADOR, linea.strip()
    return nombre, m.group(2).strip()


def _bloques(texto: str) -> list[list[str]]:
    """El archivo partido en bloques separados por líneas en blanco."""
    bloque: list[str] = []
    salida: list[list[str]] = []
    for linea in texto.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if linea.strip():
            bloque.append(linea)
        elif bloque:
            salida.append(bloque)
            bloque = []
    if bloque:
        salida.append(bloque)
    return salida


def _de_bloque_con_tiempo(bloque: list[str]) -> dict | None:
    """Un bloque VTT/SRT (índice opcional, tiempos, texto) → intervención."""
    tiempos = None
    cuerpo: list[str] = []
    for linea in bloque:
        if linea.strip().upper().startswith(_ETIQUETAS_VTT):
            continue
        m = _TIEMPO.search(linea)
        if m and tiempos is None:
            tiempos = (_segundos(*m.group(1, 2, 3, 4)), _segundos(*m.group(5, 6, 7, 8)))
            continue
        if tiempos is None and linea.strip().isdigit():
            continue        # el número de subtítulo del SRT
        cuerpo.append(linea)
    if tiempos is None or not cuerpo:
        return None
    orador, primera = _partir_orador(cuerpo[0])
    resto = [_partir_orador(x)[1] for x in cuerpo[1:]]
    texto = " ".join(x for x in [primera, *resto] if x).strip()
    if not texto:
        return None
    return {"inicio": tiempos[0], "fin": tiempos[1], "orador": orador, "texto": texto}


def _de_linea_suelta(linea: str) -> dict | None:
    """Una línea de texto pegado a mano: ``[00:12] Ana: ...`` o ``Ana: ...``."""
    marca = _MARCA.match(linea)
    inicio = 0.0
    if marca:
        partes = [int(p) for p in marca.group(1).split(":")]
        inicio = (partes[0] * 60 + partes[1] if len(partes) == 2
                  else partes[0] * 3600 + partes[1] * 60 + partes[2])
        linea = linea[marca.end():]
    orador, texto = _partir_orador(linea)
    if not texto.strip():
        return None
    return {"inicio": float(inicio), "fin": float(inicio), "orador": orador,
            "texto": texto.strip()}


def parse_transcript(texto: str) -> list[dict]:
    """Transcripción cruda → intervenciones ``{inicio, fin, orador, texto}``.

    Acepta VTT (Teams/Meet/WebEx), SRT, el TXT que exporta Zoom y texto
    pegado a mano. El formato se deduce del contenido y no de la extensión:
    la mitad de las plataformas exporta un `.txt` que por dentro es un VTT,
    y confiar en el nombre del archivo dejaba la minuta vacía sin decir por
    qué.
    """
    if not texto or not texto.strip():
        return []
    salida = []
    for bloque in _bloques(texto):
        inter = _de_bloque_con_tiempo(bloque)
        if inter:
            salida.append(inter)
            continue
        # Sin marca de tiempo: cada línea del bloque vale por sí sola.
        for linea in bloque:
            if linea.strip().upper().startswith(_ETIQUETAS_VTT):
                continue
            suelta = _de_linea_suelta(linea)
            if suelta:
                salida.append(suelta)
    return _unir_seguidas(salida)


def _unir_seguidas(inter: list[dict]) -> list[dict]:
    """Junta intervenciones consecutivas del mismo orador.

    Un VTT parte cada frase en un subtítulo de 3 segundos: sin esto, "quién
    dijo qué" sale como doscientas líneas de seis palabras y no se puede
    leer. La cita textual se conserva entera, que es lo que importa.
    """
    salida: list[dict] = []
    for act in inter:
        if salida and salida[-1]["orador"] == act["orador"] and act["inicio"] - salida[-1]["fin"] <= 3.0:
            salida[-1]["texto"] = f"{salida[-1]['texto']} {act['texto']}".strip()
            salida[-1]["fin"] = max(salida[-1]["fin"], act["fin"])
        else:
            salida.append(dict(act))
    return salida


def transcript_df(inter: list[dict]) -> pd.DataFrame:
    """Las intervenciones como tabla, con el minuto ya legible."""
    filas = [{"minuto": _mmss(i["inicio"]), "orador": i["orador"],
              "texto": i["texto"], "segundos": round(max(i["fin"] - i["inicio"], 0), 1)}
             for i in inter]
    return pd.DataFrame(filas, columns=["minuto", "orador", "texto", "segundos"])


# ---------------------------------------------------------------------------
# Quién habló y cuánto
# ---------------------------------------------------------------------------
def speakers(inter: list[dict], lang: str = "es") -> pd.DataFrame:
    """Un renglón por orador: intervenciones, palabras, minutos y su peso.

    El peso importa en un relevamiento: si el 80% lo habló el consultor, no
    fue un relevamiento — fue una presentación, y las respuestas que faltan
    van a aparecer como supuestos más adelante.
    """
    sin_asignar = _texto(_tr("(sin asignar)", "(unassigned)", "(sem atribuir)"), lang)
    filas: dict[str, dict] = {}
    for i in inter:
        clave = i["orador"] or sin_asignar
        fila = filas.setdefault(clave, {"orador": clave, "intervenciones": 0,
                                        "palabras": 0, "segundos": 0.0})
        fila["intervenciones"] += 1
        fila["palabras"] += len(i["texto"].split())
        fila["segundos"] += max(i["fin"] - i["inicio"], 0)
    if not filas:
        return pd.DataFrame(columns=["orador", "intervenciones", "palabras",
                                     "minutos", "peso_%"])
    df = pd.DataFrame(filas.values())
    total = df["palabras"].sum() or 1
    df["minutos"] = (df["segundos"] / 60).round(1)
    df["peso_%"] = (df["palabras"] * 100 / total).round(1)
    return (df.drop(columns=["segundos"])
              .sort_values("palabras", ascending=False, ignore_index=True))


# ---------------------------------------------------------------------------
# Hallazgos: decisiones, compromisos, riesgos, pendientes
# ---------------------------------------------------------------------------
# Marcadores por tipo y por idioma. Es deliberadamente simple —frases, no un
# modelo— porque tiene que correr sin red, sin clave y sin sorpresas, y
# porque el que lee la minuta puede AUDITAR por qué una frase quedó marcada.
# Un clasificador que acierta el 90% y no explica el 10% restante hace que se
# revise la minuta entera igual, o peor: que no se revise.
_MARCADORES = {
    "decision": _tr(
        "decidimos|se decide|quedamos en|acordamos|se acordo|va a ser|definimos|"
        "queda definido|resolvimos|la decision es",
        "we decided|it was decided|we agreed|agreed that|we settled on|"
        "the decision is|we will go with",
        "decidimos|ficou decidido|combinamos|acordamos|definimos|"
        "a decisao e|vamos com"),
    "compromiso": _tr(
        "me comprometo|yo me encargo|lo hago yo|te lo paso|te lo mando|"
        "para el|antes del|antes de fin|lo tengo listo|queda a cargo|"
        "se encarga|nos manda|va a enviar|voy a enviar|te envio",
        "i will send|i'll send|i'll take|i take care|i will own|by friday|"
        "by end of|will be ready|is responsible for|will provide",
        "eu envio|vou enviar|eu cuido|fico responsavel|te mando|"
        "ate sexta|ate o fim|vai enviar|fica encarregado"),
    "riesgo": _tr(
        "el problema es|no tenemos|no existe|no esta documentado|se pisa|"
        "se duplica|no coincide|nadie sabe|depende de una persona|"
        "esta en un excel|se hace a mano|no hay backup|no hay respaldo|"
        "esta desactualizado|se cae|falla",
        "the problem is|we don't have|does not exist|not documented|"
        "gets overwritten|duplicated|doesn't match|nobody knows|"
        "single point|in an excel|done by hand|no backup|out of date|breaks",
        "o problema e|nao temos|nao existe|nao esta documentado|"
        "e sobrescrito|duplicado|nao bate|ninguem sabe|depende de uma pessoa|"
        "esta num excel|feito a mao|nao ha backup|desatualizado|quebra"),
    "pendiente": _tr(
        "queda pendiente|lo vemos despues|hay que revisar|falta definir|"
        "lo confirmamos|tenemos que ver|habria que|nos falta|pendiente de",
        "pending|we'll see later|need to review|to be defined|"
        "we'll confirm|we need to check|still missing|tbd",
        "fica pendente|vemos depois|precisa revisar|falta definir|"
        "vamos confirmar|precisamos ver|ainda falta|pendente de"),
    "pregunta": _tr(
        "quien|como se|donde esta|cada cuanto|por que|cuantos|cual es",
        "who |how do|where is|how often|why does|how many|what is",
        "quem|como se|onde esta|com que frequencia|por que|quantos|qual e"),
}

_ETIQUETA_TIPO = {
    "decision": _tr("Decisión", "Decision", "Decisão"),
    "compromiso": _tr("Compromiso", "Commitment", "Compromisso"),
    "riesgo": _tr("Riesgo", "Risk", "Risco"),
    "pendiente": _tr("Pendiente", "Open item", "Pendente"),
    "pregunta": _tr("Pregunta abierta", "Open question", "Pergunta aberta"),
    "dato": _tr("Dato del negocio", "Business fact", "Dado do negócio"),
}


def etiqueta_tipo(tipo: str, lang: str = "es") -> str:
    return _texto(_ETIQUETA_TIPO.get(tipo, _ETIQUETA_TIPO["dato"]), lang)


def _tipo_de(texto_plano: str, lang: str) -> str | None:
    for tipo in TIPOS:
        patron = _MARCADORES.get(tipo)
        if not patron:
            continue
        for marcador in _texto(patron, lang).split("|"):
            if marcador and marcador in texto_plano:
                return tipo
    return None


def findings(inter: list[dict], lang: str = "es") -> pd.DataFrame:
    """Decisiones, compromisos, riesgos y pendientes, con quién y en qué minuto.

    La cita es TEXTUAL y va con su minuto: así se puede volver a la
    grabación y escucharla. Una minuta que resume un compromiso pierde
    exactamente lo que la hace servir para algo.
    """
    filas = []
    for i in inter:
        plano = _sin_tildes(i["texto"])
        # Se busca en los tres idiomas: una reunión en Montevideo con un
        # gerente regional mezcla español e inglés en la misma frase.
        tipo = None
        for idioma in (lang, "es", "en", "pt"):
            tipo = _tipo_de(plano, idioma)
            if tipo:
                break
        if not tipo:
            continue
        filas.append({
            "tipo": etiqueta_tipo(tipo, lang),
            "tipo_id": tipo,
            "minuto": _mmss(i["inicio"]),
            "orador": i["orador"],
            "cita": i["texto"],
        })
    return pd.DataFrame(filas, columns=["tipo", "tipo_id", "minuto", "orador", "cita"])


# ---------------------------------------------------------------------------
# De la reunión al pipeline
# ---------------------------------------------------------------------------
# Vocabulario por etapa del pipeline (las mismas 12 de mvdg.pipeline_doc). El
# cruce es lo que convierte una minuta en trabajo: "esto que dijeron toca la
# ingesta y el linaje". Sin esto la reunión queda como un documento lindo que
# nadie vuelve a abrir.
_VOCABULARIO = {
    "ingesta": ("excel", "csv", "archivo", "base de datos", "sql", "erp", "sap",
                "extraccion", "extraer", "conexion", "planilla", "file",
                "spreadsheet", "database", "extract", "planilha", "arquivo"),
    "perfilado": ("nulos", "vacios", "duplicados", "formato", "tipo de dato",
                  "cuantos registros", "volumen", "nulls", "empty", "duplicates",
                  "nulos", "vazios", "duplicados", "volume"),
    "catalogo": ("dueno", "responsable", "quien mantiene", "owner", "steward",
                 "area responsable", "quem mantem", "responsavel", "dono"),
    "diccionario": ("que significa", "definicion", "nomenclatura", "campo",
                    "columna", "glosario del campo", "what does it mean",
                    "definition", "field", "column", "o que significa", "campo"),
    "reglas": ("validacion", "control", "no puede ser", "tiene que ser",
               "obligatorio", "regla", "validation", "must be", "required",
               "rule", "validacao", "obrigatorio", "regra"),
    "indice": ("calidad", "score", "indicador", "kpi", "medir", "quality",
               "measure", "qualidade", "medir"),
    "features": ("calculado", "derivado", "formula", "indicador nuevo",
                 "calculated", "derived", "formula", "calculado", "derivado"),
    "mdm": ("maestro", "duplicado de cliente", "mismo cliente", "unificar",
            "codigo unico", "master", "golden record", "unify", "mestre",
            "unificar", "codigo unico"),
    "linaje": ("de donde sale", "de donde viene", "origen", "aguas arriba",
               "alimenta", "depende de", "where does it come from", "upstream",
               "feeds", "de onde vem", "origem", "alimenta"),
    "glosario": ("termino", "negocio lo llama", "en el negocio", "glosario",
                 "term", "business calls it", "glossary", "termo", "glossario"),
    "politicas": ("politica", "norma", "auditoria", "cumplimiento", "gdpr",
                  "datos personales", "confidencial", "permiso", "acceso",
                  "policy", "audit", "compliance", "personal data", "access",
                  "politica", "auditoria", "dados pessoais", "acesso"),
    "publicacion": ("power bi", "powerbi", "tableau", "reporte", "dashboard",
                    "tablero", "informe", "report", "relatorio", "painel"),
}


def pipeline_links(inter: list[dict], lang: str = "es") -> pd.DataFrame:
    """Qué dijeron que toca cada etapa del pipeline.

    Devuelve un renglón por (etapa, intervención). Una misma frase puede
    tocar dos etapas y eso no es un error: "el maestro de clientes lo pisa
    el ERP" es MDM y es linaje.
    """
    from . import pipeline_doc

    titulos = {e["key"]: (e["n"], e["titulo"])
               for e in pipeline_doc.documentar(lang)}
    filas = []
    for i in inter:
        plano = _sin_tildes(i["texto"])
        for clave, palabras in _VOCABULARIO.items():
            if clave not in titulos:
                continue
            pegan = [p for p in palabras if p in plano]
            if not pegan:
                continue
            n, titulo = titulos[clave]
            filas.append({"n": n, "etapa": titulo, "etapa_id": clave,
                          "minuto": _mmss(i["inicio"]), "orador": i["orador"],
                          "cita": i["texto"], "pistas": ", ".join(sorted(set(pegan))[:4])})
    df = pd.DataFrame(filas, columns=["n", "etapa", "etapa_id", "minuto",
                                      "orador", "cita", "pistas"])
    return df.sort_values(["n", "minuto"], ignore_index=True) if len(df) else df


# ---------------------------------------------------------------------------
# La minuta completa
# ---------------------------------------------------------------------------
_TITULO = _tr("Minuta de reunión", "Meeting minutes", "Ata de reunião")
_SIN_NADA = _tr("La transcripción está vacía: no hay nada que minutar.",
                "The transcript is empty: there is nothing to minute.",
                "A transcrição está vazia: não há nada para registrar.")


def minutes(inter: list[dict], lang: str = "es", titulo: str = "",
            fecha: str = "", participantes: str = "") -> dict:
    """La minuta armada: resumen, quién habló, hallazgos y cruce con el pipeline.

    Es un ``dict`` y no un texto para que la pantalla, el Excel y el
    documento Word salgan todos de la MISMA medición — que es lo que evita
    que el PDF diga una cosa y la pantalla otra.
    """
    hall = findings(inter, lang)
    return {
        "titulo": titulo or _texto(_TITULO, lang),
        "fecha": fecha,
        "participantes": participantes,
        "lang": lang,
        "intervenciones": len(inter),
        "duracion_min": round(max((i["fin"] for i in inter), default=0) / 60, 1),
        "oradores": speakers(inter, lang),
        "hallazgos": hall,
        "pipeline": pipeline_links(inter, lang),
        "transcripcion": transcript_df(inter),
        "vacia": not inter,
        "aviso_vacia": _texto(_SIN_NADA, lang),
    }


# ---------------------------------------------------------------------------
# La minuta como documento (HTML / Word / PDF vía mvdg.doc_export)
# ---------------------------------------------------------------------------
_DOC_SUB = _tr(
    "Quién dijo qué, con el minuto de cada cita, y qué le toca a cada etapa "
    "del pipeline de datos.",
    "Who said what, with the timestamp of every quote, and what each stage of "
    "the data pipeline has to do about it.",
    "Quem disse o quê, com o minuto de cada citação, e o que cabe a cada "
    "etapa do pipeline de dados.")

_ET_DOC = {
    "participantes": _tr("Participantes", "Participants", "Participantes"),
    "fecha": _tr("Fecha", "Date", "Data"),
    "duracion": _tr("Duración", "Duration", "Duração"),
    "intervenciones": _tr("Intervenciones", "Turns", "Intervenções"),
    "quien_hablo": _tr("Quién habló", "Who spoke", "Quem falou"),
    "hallazgos": _tr("Decisiones, compromisos y riesgos",
                     "Decisions, commitments and risks",
                     "Decisões, compromissos e riscos"),
    "pipeline": _tr("Qué le toca a cada etapa del pipeline",
                    "What each pipeline stage has to do",
                    "O que cabe a cada etapa do pipeline"),
    "nada": _tr("No se detectó ninguno.", "None detected.", "Nenhum detectado."),
    "pie": _tr("MV Data Governance · minuta generada desde la transcripción",
               "MV Data Governance · minutes generated from the transcript",
               "MV Data Governance · ata gerada a partir da transcrição"),
}


def _bloques_oradores(minuta: dict, lang: str) -> list[tuple[str, str]]:
    df = minuta["oradores"]
    if not len(df):
        return [("—", _texto(_ET_DOC["nada"], lang))]
    return [(str(f["orador"]),
             f"{f['intervenciones']} · {f['palabras']} · {f['peso_%']}%")
            for _, f in df.iterrows()]


def to_document(minuta: dict, lang: str = "es") -> dict:
    """La minuta lista para ``mvdg.doc_export``.

    Las citas van textuales y con su minuto también en el documento: si el
    Word que se manda por mail resumiera los compromisos, perdería
    exactamente lo que hace que sirva para reclamarlos.
    """
    hall, pipe = minuta["hallazgos"], minuta["pipeline"]
    secciones = [{
        "n": 1, "titulo": _texto(_ET_DOC["quien_hablo"], lang), "modulo": "",
        "bloques": _bloques_oradores(minuta, lang),
        "evidencia": "", "evidencia_etiqueta": "",
    }, {
        "n": 2, "titulo": _texto(_ET_DOC["hallazgos"], lang), "modulo": "",
        "bloques": ([(f"{f['tipo']} · {f['minuto']} · {f['orador']}", f["cita"])
                     for _, f in hall.iterrows()]
                    or [("—", _texto(_ET_DOC["nada"], lang))]),
        "evidencia": "", "evidencia_etiqueta": "",
    }, {
        "n": 3, "titulo": _texto(_ET_DOC["pipeline"], lang), "modulo": "",
        "bloques": ([(f"{f['n']}. {f['etapa']} · {f['minuto']}", f["cita"])
                     for _, f in pipe.iterrows()]
                    or [("—", _texto(_ET_DOC["nada"], lang))]),
        "evidencia": "", "evidencia_etiqueta": "",
    }]
    meta = [(_texto(_ET_DOC["fecha"], lang), minuta.get("fecha") or "—"),
            (_texto(_ET_DOC["participantes"], lang),
             minuta.get("participantes") or "—"),
            (_texto(_ET_DOC["duracion"], lang), f"{minuta['duracion_min']} min"),
            (_texto(_ET_DOC["intervenciones"], lang), str(minuta["intervenciones"]))]
    return {
        "titulo": minuta["titulo"],
        "subtitulo": _texto(_DOC_SUB, lang),
        "lang": lang, "meta": meta,
        "pie": _texto(_ET_DOC["pie"], lang),
        "secciones": secciones,
    }
