# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Conector de METADATA de Power BI (solo estructura, cero filas).

A diferencia de ``connectors.py`` (que trae DATOS de una base vía SQLAlchemy),
este módulo trae la ESTRUCTURA de un modelo de Power BI: tablas, columnas,
medidas con su DAX, relaciones y roles RLS — nunca las filas. Cumple la misma
regla que ``docs/IA_EXTERNA.md``: se procesa metadato, no datos reales.

Dos caminos, alineados con las dos opciones de distribución del producto:

  A) OFFLINE / cualquier empresa — ``read_pbip(folder)``
     Lee la carpeta ``definition`` (TMDL) de un proyecto ``.pbip`` guardado por
     Power BI Desktop. NO requiere tenant, credenciales ni internet. Si el
     archivo ``.pbi/cache.abf`` fue borrado (recomendado), el modelo ni siquiera
     tiene datos: solo estructura. Es el modo más seguro y el que corre en
     equipos con TI restrictiva.

  B) TENANT-WIDE / gobernanza — ``read_scanner(...)`` / ``ingest_tenant(...)``
     Usa la Scanner API (Admin REST ``admin/workspaces/...``) con un service
     principal propio del usuario para catalogar TODO el tenant de una sola
     vez: enumera los workspaces (``admin/groups``), pide el scan
     (``getInfo``), espera (``scanStatus``) y trae el resultado
     (``scanResult``) — datasets, tablas, medidas, DAX, expresiones M, roles
     RLS, relaciones y reportes de cada workspace. Devuelve metadata, nunca
     filas. Apagado por defecto: solo corre si están cargadas
     ``POWERBI_TENANT_ID`` / ``POWERBI_CLIENT_ID`` / ``POWERBI_CLIENT_SECRET``
     como variables de entorno propias del usuario — ver ``docs/BI_TENANT_SCAN.md``.
     Implementado con ``urllib`` (misma librería estándar que ``ai_provider.py``,
     sin agregar una dependencia nueva al proyecto).

Ambos caminos entregan uno o más ``PowerBIModel`` que se normalizan a las
MISMAS tablas que ya usa el motor de gobierno:

    to_catalog(model)     -> columnas de catalog.catalog_df
    to_dictionary(model)  -> columnas de catalog.dictionary_df
    to_glossary(model)    -> columnas de glossary.glossary_df   (cada medida = término)
    to_lineage(model)     -> columnas de lineage.lineage_df      (SQL/fuente → tabla → dataset → reporte)
    to_quality(model)     -> columnas de quality.evaluate_rules  (salud del modelo)
    to_sources(model)     -> una fila por tabla con el origen SQL/M detectado en su partición

El linaje queda cableado de punta a punta: si la partición M de una tabla usa
``Sql.Database(...)`` (u otro conector reconocible), ``to_lineage`` agrega ese
origen como primer tramo — SQL → tabla → dataset (modelo) → reporte — sobre
el mismo grafo de 5 capas (source/raw/curated/mart/bi) que ya dibuja
``lineage.lineage_figure`` para el resto del programa. ``ingest_tenant()``
hace lo mismo para TODOS los datasets del tenant a la vez, concatenando las
tablas normalizadas de cada uno.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

import pandas as pd

_TIMEOUT = 60  # segundos, por request HTTP

# ----------------------------------------------------------------- modelo
@dataclass
class Measure:
    table: str
    name: str
    dax: str
    display_folder: str = ""
    description: str = ""


@dataclass
class Column:
    table: str
    name: str
    data_type: str = ""
    source_column: str = ""
    is_calculated: bool = False
    dax: str = ""


@dataclass
class Relationship:
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    both_directions: bool = False


@dataclass
class PowerBIModel:
    name: str = "SemanticModel"
    tables: list[str] = field(default_factory=list)
    columns: list[Column] = field(default_factory=list)
    measures: list[Measure] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    roles: list[str] = field(default_factory=list)      # roles RLS detectados
    reports: list[str] = field(default_factory=list)     # reportes que usan el modelo
    table_sources: dict[str, str] = field(default_factory=dict)  # tabla -> origen (SQL/M), detectado
    workspace: str = ""    # workspace de origen — solo se completa en el camino tenant (Scanner API)
    dataset_id: str = ""   # id del dataset en el Scanner API — solo para linkear reportes al escanear
    source: str = "PBIP (offline)"
    # Lo que declara el programa que generó el archivo, cuando dejó rastro.
    # Vacío para cualquier modelo hecho a mano en Desktop, que es el caso
    # normal: nada de acá abajo puede ser obligatorio.
    generator: str = ""
    table_rows: dict[str, int] = field(default_factory=dict)  # tabla -> filas declaradas


# ------------------------------------------------------- helpers de parseo TMDL
def _indent(line: str) -> int:
    """Ancho de sangría (tabs y espacios cuentan como 1 cada uno)."""
    return len(line) - len(line.lstrip("\t "))


def _unquote(name: str) -> str:
    name = name.strip()
    if len(name) >= 2 and name[0] in "'\"" and name[-1] == name[0]:
        return name[1:-1]
    return name


_MEASURE_RE = re.compile(r"^\s*measure\s+('[^']+'|\"[^\"]+\"|[^\s=]+)\s*=\s*(.*)$")
_COLUMN_RE = re.compile(r"^\s*column\s+('[^']+'|\"[^\"]+\"|[^\s]+)\s*$")
_TABLE_RE = re.compile(r"^\s*table\s+('[^']+'|\"[^\"]+\"|[^\s]+)\s*$")
_PARTITION_RE = re.compile(r"^\s*partition\s+")
# comentario de documentación nativo de TMDL ("/// texto"), en la(s) línea(s)
# inmediatamente antes de un table/measure/column — se usa como descripción
# si el objeto no trae una propiedad "description:" explícita.
_DESC_COMMENT_RE = re.compile(r"^\s*///\s?(.*)$")
# cualquier propiedad TMDL de la forma "nombre: valor" (formatString,
# lineageTag, sourceLineageTag, dataCategory, summarizeBy, etc.) — se usa
# para no confundir metadatos con continuaciones reales de DAX.
_TMDL_TRAIT_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]*\s*:(\s|$)")

# heurísticas sobre la expresión M de una partición (Power Query) — nunca leen
# filas, solo el texto de la consulta, para identificar de dónde viene la tabla.
_SQL_DB_RE = re.compile(r"Sql\.Database(?:s)?\s*\(\s*\"([^\"]+)\"(?:\s*,\s*\"([^\"]+)\")?")
_NATIVE_QUERY_RE = re.compile(r"Value\.NativeQuery")
_MQUERY_FN_RE = re.compile(r"\b([A-Z][A-Za-z0-9]*\.[A-Za-z0-9]+)\s*\(")


def _source_label_from_mquery(text: str) -> str | None:
    """A partir del texto de una partición M, devuelve una etiqueta legible del
    origen real de la tabla (servidor SQL, consulta nativa, u otro conector),
    o None si no se pudo detectar nada."""
    m = _SQL_DB_RE.search(text)
    if m:
        server, database = m.group(1), m.group(2)
        return f"SQL Server · {server}/{database}" if database else f"SQL Server · {server}"
    if _NATIVE_QUERY_RE.search(text):
        return "SQL (consulta nativa · Value.NativeQuery)"
    m = _MQUERY_FN_RE.search(text)
    if m:
        return f"Power Query · {m.group(1)}"
    return None


def _parse_measure_block(lines: list[str], i: int, table_name: str,
                         pending_desc: list[str]) -> tuple[Measure, int]:
    """Una medida y su DAX, que puede seguir en líneas más indentadas.

    Devuelve la medida y el índice de la primera línea que ya no le pertenece."""
    line = lines[i]
    m = _MEASURE_RE.match(line)
    base_indent = _indent(line)
    name = _unquote(m.group(1))
    dax_parts = [m.group(2).rstrip()]
    folder, desc = "", " ".join(pending_desc).strip()
    j = i + 1
    while j < len(lines):
        nxt = lines[j]
        if not nxt.strip():
            j += 1
            continue
        low = nxt.strip()
        if _indent(nxt) <= base_indent:
            break  # nuevo objeto de la tabla
        # propiedades conocidas de la medida
        if low.startswith("displayFolder:"):
            folder = low.split(":", 1)[1].strip()
        elif low.startswith("description:"):
            desc = low.split(":", 1)[1].strip()   # explícita: pisa el "///" si había
        elif low.startswith(("annotation", "changedProperty", "isHidden")) or \
                _TMDL_TRAIT_RE.match(low):
            pass   # metadato TMDL (formatString, lineageTag, sourceLineageTag,
                   # dataCategory, summarizeBy, etc.) — no es DAX
        else:
            dax_parts.append(low)  # continuación real del DAX
        j += 1
    dax = " ".join(p for p in dax_parts if p).strip()
    return Measure(table_name, name, dax, folder, desc), j


def _parse_column_block(lines: list[str], i: int,
                        table_name: str) -> tuple[Column, int]:
    """Una columna con su dataType / sourceColumn / expresión si es calculada."""
    line = lines[i]
    base_indent = _indent(line)
    name = _unquote(_COLUMN_RE.match(line).group(1))
    dtype, src, cdax, is_calc = "", "", "", False
    j = i + 1
    while j < len(lines):
        nxt = lines[j]
        if not nxt.strip():
            j += 1
            continue
        if _indent(nxt) <= base_indent:
            break
        low = nxt.strip()
        if low.startswith("dataType:"):
            dtype = low.split(":", 1)[1].strip()
        elif low.startswith("sourceColumn:"):
            src = low.split(":", 1)[1].strip()
        elif low.startswith("expression"):
            is_calc = True
            cdax = low.split("=", 1)[1].strip() if "=" in low else ""
        j += 1
    return Column(table_name, name, dtype, src, is_calc, cdax), j


def _parse_partition_block(lines: list[str], i: int) -> tuple[str | None, int]:
    """El bloque de partición (expresión M): de acá sale el origen real."""
    base_indent = _indent(lines[i])
    block_lines = []
    j = i + 1
    while j < len(lines):
        nxt = lines[j]
        if nxt.strip() and _indent(nxt) <= base_indent:
            break
        block_lines.append(nxt)
        j += 1
    return _source_label_from_mquery("\n".join(block_lines)), j


def _parse_table_tmdl(text: str) -> tuple[str, list[Column], list[Measure], str | None]:
    """Parsea un archivo TMDL de tabla: devuelve (nombre_tabla, columnas, medidas,
    fuente detectada de la partición — SQL Server u otro conector, o None).

    Este bucle solo decide QUÉ tipo de bloque empieza en cada línea; el detalle
    de cada uno vive en su propio parser arriba."""
    lines = text.splitlines()
    table_name = ""
    columns: list[Column] = []
    measures: list[Measure] = []
    table_source: str | None = None
    pending_desc: list[str] = []   # "/// ..." acumulados, esperando su objeto

    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        m = _DESC_COMMENT_RE.match(line)
        if m:
            pending_desc.append(m.group(1).strip())
            i += 1
            continue

        m = _TABLE_RE.match(line)
        if m and not table_name:
            table_name = _unquote(m.group(1))
            pending_desc = []
            i += 1
            continue

        if _MEASURE_RE.match(line):
            medida, i = _parse_measure_block(lines, i, table_name, pending_desc)
            measures.append(medida)
            pending_desc = []
            continue

        if _COLUMN_RE.match(line):
            columna, i = _parse_column_block(lines, i, table_name)
            columns.append(columna)
            pending_desc = []
            continue

        if _PARTITION_RE.match(line):
            fuente, i = _parse_partition_block(lines, i)
            if table_source is None:
                table_source = fuente
            pending_desc = []
            continue

        pending_desc = []   # línea suelta que no es "///" ni una declaración: corta la racha
        i += 1

    return table_name, columns, measures, table_source


def _parse_relationships_tmdl(text: str) -> list[Relationship]:
    rels: list[Relationship] = []
    cur: dict = {}

    def flush():
        if "from" in cur and "to" in cur:
            ft, fc = (cur["from"].split(".", 1) + [""])[:2]
            tt, tc = (cur["to"].split(".", 1) + [""])[:2]
            rels.append(Relationship(
                _unquote(ft), _unquote(fc), _unquote(tt), _unquote(tc),
                cur.get("both", False)))

    for line in text.splitlines():
        low = line.strip()
        if low.startswith("relationship "):
            flush()
            cur = {}
        elif low.startswith("fromColumn:"):
            cur["from"] = low.split(":", 1)[1].strip()
        elif low.startswith("toColumn:"):
            cur["to"] = low.split(":", 1)[1].strip()
        elif low.startswith("crossFilteringBehavior:") and "bothDirections" in low:
            cur["both"] = True
    flush()
    return rels


# ------------------------------------------------------------ camino A: PBIP
def read_pbip(folder: str) -> PowerBIModel:
    """Lee la carpeta de un proyecto .pbip (o directamente su carpeta ``definition``).

    Busca la carpeta ``definition`` del semantic model, parsea los TMDL de
    ``tables/`` y ``relationships.tmdl``, detecta roles RLS y reportes.
    """
    root = folder
    # localizar la carpeta definition del semantic model
    definition = None
    for dirpath, dirnames, filenames in os.walk(root):
        if os.path.basename(dirpath) == "definition" and (
            "model.tmdl" in filenames or "tables" in dirnames):
            definition = dirpath
            break
    if definition is None:
        # ¿nos pasaron directamente la carpeta definition?
        if os.path.exists(os.path.join(root, "model.tmdl")) or \
           os.path.isdir(os.path.join(root, "tables")):
            definition = root
        else:
            raise FileNotFoundError(
                "No encontré la carpeta 'definition' del modelo. Guardá el "
                "reporte como .pbip (formato TMDL) y pasá esa carpeta.")

    model = PowerBIModel(source="PBIP (offline)")

    # nombre del modelo (opcional, desde el .platform si está)
    plat = os.path.join(os.path.dirname(definition), ".platform")
    if os.path.exists(plat):
        try:
            with open(plat, encoding="utf-8") as fh:
                model.name = json.load(fh).get("metadata", {}).get("displayName", model.name)
        except Exception:
            pass

    # tablas
    tables_dir = os.path.join(definition, "tables")
    tmdl_files = []
    if os.path.isdir(tables_dir):
        tmdl_files = [os.path.join(tables_dir, f) for f in os.listdir(tables_dir)
                      if f.endswith(".tmdl")]
    else:  # algunos exports meten todo en model.tmdl
        mp = os.path.join(definition, "model.tmdl")
        if os.path.exists(mp):
            tmdl_files = [mp]

    for path in tmdl_files:
        with open(path, encoding="utf-8") as fh:
            tname, cols, meas, tsrc = _parse_table_tmdl(fh.read())
        if tname:
            model.tables.append(tname)
            if tsrc:
                model.table_sources[tname] = tsrc
        model.columns.extend(cols)
        model.measures.extend(meas)

    # relaciones
    rel_path = os.path.join(definition, "relationships.tmdl")
    if os.path.exists(rel_path):
        with open(rel_path, encoding="utf-8") as fh:
            model.relationships = _parse_relationships_tmdl(fh.read())

    # roles RLS
    roles_dir = os.path.join(definition, "roles")
    if os.path.isdir(roles_dir):
        model.roles = [os.path.splitext(f)[0] for f in os.listdir(roles_dir)
                       if f.endswith(".tmdl")]

    # reportes que apuntan a este modelo (carpetas *.Report hermanas)
    proj = os.path.dirname(os.path.dirname(definition))
    if os.path.isdir(proj):
        model.reports = [d[:-7] for d in os.listdir(proj) if d.endswith(".Report")]

    return model


# ------------------------------------------- camino A2: .pbit / .pbix (zip)
# Un .pbit (plantilla) y un .pbix (reporte) son archivos ZIP. Adentro, el
# modelo puede venir de dos formas muy distintas:
#
#   DataModelSchema -> JSON (TMSL) con tablas, columnas, medidas y
#                      relaciones. Es lo que trae SIEMPRE un .pbit, y es
#                      perfectamente legible.
#   DataModel       -> respaldo binario de Analysis Services. Es lo que trae
#                      un .pbix con datos adentro. NO se puede leer sin las
#                      librerías de Analysis Services, que son de Windows y
#                      pesan cientos de megas.
#
# Por eso el .pbit anda siempre y el .pbix anda solo si además trae el
# schema. Cuando no lo trae, se dice exactamente qué hacer en vez de fallar
# con un error de zip que no le sirve a nadie.
_PBIT_SCHEMA = ("datamodelschema", "datamodelschema.json")
_PBIT_BINARIO = ("datamodel", "datamodel.xml")


def _texto_del_zip(crudo: bytes) -> str:
    """El DataModelSchema viene en UTF-16-LE con BOM. No siempre: algunos
    exports y herramientas de terceros lo escriben en UTF-8, así que se
    prueban las dos en vez de asumir."""
    for enc in ("utf-16", "utf-16-le", "utf-8-sig", "utf-8"):
        try:
            texto = crudo.decode(enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
        if texto.lstrip().startswith("{"):
            return texto
    raise ValueError("El DataModelSchema no está en una codificación conocida.")


def _tmsl_columnas(tabla: dict, nombre_tabla: str) -> list[Column]:
    cols = []
    for c in tabla.get("columns") or []:
        if not isinstance(c, dict) or c.get("isHidden") and c.get("type") == "rowNumber":
            continue
        expr = c.get("expression")
        if isinstance(expr, list):
            expr = "\n".join(str(x) for x in expr)
        cols.append(Column(
            table=nombre_tabla, name=str(c.get("name", "")),
            data_type=str(c.get("dataType", "")),
            source_column=str(c.get("sourceColumn", "")),
            is_calculated=c.get("type") == "calculated",
            dax=str(expr or "")))
    return cols


def _tmsl_medidas(tabla: dict, nombre_tabla: str) -> list[Measure]:
    medidas = []
    for m in tabla.get("measures") or []:
        if not isinstance(m, dict):
            continue
        expr = m.get("expression")
        if isinstance(expr, list):
            expr = "\n".join(str(x) for x in expr)
        medidas.append(Measure(
            table=nombre_tabla, name=str(m.get("name", "")), dax=str(expr or ""),
            display_folder=str(m.get("displayFolder", "")),
            description=str(m.get("description", ""))))
    return medidas


def _tmsl_fuente(tabla: dict) -> str | None:
    """El origen real de la tabla, desde la expresión M de su partición —
    mismo criterio que usa el camino TMDL, para que un mismo modelo dé la
    misma respuesta venga de .pbip o de .pbit."""
    for p in tabla.get("partitions") or []:
        if not isinstance(p, dict):
            continue
        src = p.get("source") or {}
        expr = src.get("expression")
        if isinstance(expr, list):
            expr = "\n".join(str(x) for x in expr)
        etiqueta = _source_label_from_mquery(str(expr or ""))
        if etiqueta:
            return etiqueta
    return None


def _tmsl_relaciones(modelo: dict) -> list[Relationship]:
    rels = []
    for r in modelo.get("relationships") or []:
        if not isinstance(r, dict):
            continue
        rels.append(Relationship(
            from_table=str(r.get("fromTable", "")), from_column=str(r.get("fromColumn", "")),
            to_table=str(r.get("toTable", "")), to_column=str(r.get("toColumn", "")),
            both_directions=r.get("crossFilteringBehavior") == "bothDirections"))
    return rels


def _schema_del_zip(path: str) -> dict:
    """Saca el TMSL del .pbit/.pbix, o explica por qué no se puede."""
    import zipfile

    from .errors import ErrorTraducible

    with zipfile.ZipFile(path) as zf:
        por_nombre = {n.rsplit("/", 1)[-1].lower(): n for n in zf.namelist()}
        entrada = next((por_nombre[n] for n in _PBIT_SCHEMA if n in por_nombre), None)
        if entrada is None:
            if any(n in por_nombre for n in _PBIT_BINARIO):
                raise ErrorTraducible(
                    "err_pbix_binario",
                    "El archivo trae DataModel (respaldo binario de Analysis "
                    "Services), no DataModelSchema.")
            raise ErrorTraducible(
                "err_pbi_sin_modelo",
                f"Entradas del archivo: {sorted(por_nombre)[:12]}")
        return json.loads(_texto_del_zip(zf.read(entrada)))


# ------------------------------------------- el traspaso desde el generador
# Un generador de modelos sabe cosas que el TMSL no cuenta: cuántas filas
# trae cada tabla —van comprimidas dentro del Power Query—, qué papel juega
# cada una, y por qué cada medida está escrita como está. Cuando el archivo
# lo dejó anotado, se lee. Cuando no —un .pbit hecho a mano en Desktop, que
# es el caso normal— no pasa nada: el resto del programa funciona igual y
# los campos quedan como estaban. Ningún archivo puede quedar peor por no
# traer esto.
ANOTACION_TRASPASO = "MVDaxLab_Gobernanza"
FORMATO_TRASPASO = 1


def _traspaso(modelo: dict) -> dict | None:
    """El manifiesto del generador, o None si no está o no se entiende."""
    for a in modelo.get("annotations") or []:
        if not isinstance(a, dict) or a.get("name") != ANOTACION_TRASPASO:
            continue
        try:
            datos = json.loads(a.get("value") or "")
        except (ValueError, TypeError):
            return None
        if isinstance(datos, dict) and datos.get("formato") == FORMATO_TRASPASO:
            return datos
        return None
    return None


def _aplicar_traspaso(m: PowerBIModel, modelo: dict) -> None:
    """Completa el modelo leído con lo que el generador dejó declarado."""
    datos = _traspaso(modelo)
    if not datos:
        return
    m.generator = str(datos.get("generador") or "")
    for t in datos.get("tablas") or []:
        if isinstance(t, dict) and isinstance(t.get("filas"), int):
            m.table_rows[str(t.get("nombre", ""))] = int(t["filas"])
    # La definición de negocio de cada medida. No pisa una descripción que
    # el modelo ya traiga: lo que escribió una persona gana siempre.
    porques = {(str(x.get("tabla", "")), str(x.get("nombre", ""))): str(x.get("porque", ""))
               for x in datos.get("medidas") or [] if isinstance(x, dict)}
    for med in m.measures:
        if not med.description:
            med.description = porques.get((med.table, med.name), "")


def read_pbit(path: str) -> PowerBIModel:
    """Lee un .pbit (o un .pbix que traiga el schema) y devuelve el modelo.

    Misma salida que ``read_pbip``: de acá para arriba, al resto del programa
    le da igual de qué formato vino."""
    schema = _schema_del_zip(path)
    modelo = schema.get("model") or {}
    ext = os.path.splitext(path)[1].lstrip(".").upper() or "PBIT"
    m = PowerBIModel(source=f"{ext} (offline)")
    m.name = str(schema.get("name") or os.path.splitext(os.path.basename(path))[0]
                 or "SemanticModel")

    for tabla in modelo.get("tables") or []:
        if not isinstance(tabla, dict):
            continue
        nombre = str(tabla.get("name", ""))
        if not nombre:
            continue
        m.tables.append(nombre)
        m.columns.extend(_tmsl_columnas(tabla, nombre))
        m.measures.extend(_tmsl_medidas(tabla, nombre))
        fuente = _tmsl_fuente(tabla)
        if fuente:
            m.table_sources[nombre] = fuente

    m.relationships = _tmsl_relaciones(modelo)
    m.roles = [str(r.get("name", "")) for r in modelo.get("roles") or []
               if isinstance(r, dict) and r.get("name")]
    _aplicar_traspaso(m, modelo)
    # El .pbit lleva el reporte adentro, no como carpeta hermana: el reporte
    # es el archivo mismo.
    m.reports = [os.path.splitext(os.path.basename(path))[0]]
    return m


def ingest_pbit(path: str, lang: str = "es") -> dict[str, pd.DataFrame]:
    """Atajo: lee un .pbit/.pbix y devuelve las tablas normalizadas."""
    return _normalizar(read_pbit(path), lang)


# Lo que el usuario tiene a mano, sin pedirle que sepa la diferencia.
EXT_POWERBI = (".pbit", ".pbix", ".pbip", ".zip")


def ingest_powerbi_file(path: str, lang: str = "es") -> dict[str, pd.DataFrame]:
    """Un solo punto de entrada para cualquier archivo de Power BI.

    El usuario no tiene por qué saber que .pbip es una carpeta y .pbit un
    zip: elige su archivo y esto decide cómo leerlo. Antes la pestaña solo
    aceptaba la carpeta .pbip, así que pasarle el .pbit —que es lo que la
    mayoría tiene— fallaba sin explicar que el formato no era ese.
    """
    from .errors import ErrorTraducible

    if os.path.isdir(path):
        return ingest_pbip(path, lang)
    ext = os.path.splitext(path)[1].lower()
    if ext in (".pbit", ".pbix"):
        return ingest_pbit(path, lang)
    if ext == ".zip":
        # Un zip puede ser el .pbip comprimido (carpeta TMDL) o un .pbit
        # renombrado. Se prueba el TMDL y, si no está, el schema.
        import tempfile
        import zipfile
        tmp = tempfile.mkdtemp(prefix="mvdg_pbi_")
        with zipfile.ZipFile(path) as zf:
            zf.extractall(tmp)
        try:
            return ingest_pbip(tmp, lang)
        except FileNotFoundError:
            return ingest_pbit(path, lang)
    raise ErrorTraducible("err_pbi_extension", f"Extensión recibida: {ext or '(ninguna)'}")


# ----------------------------------------------------- camino B: Scanner API
_PBI_ENV = ("POWERBI_TENANT_ID", "POWERBI_CLIENT_ID", "POWERBI_CLIENT_SECRET")
_ADMIN_BASE = "https://api.powerbi.com/v1.0/myorg/admin"
_SCAN_BATCH_SIZE = 100          # límite práctico de workspaces por request de getInfo
_SCAN_POLL_SECONDS = 2
_SCAN_MAX_POLLS = 60            # ~2 minutos de espera máxima por lote


def tenant_configured() -> bool:
    """¿Hay credenciales de service principal cargadas para el escaneo tenant-wide?"""
    return all(os.environ.get(v) for v in _PBI_ENV)


def _http_json(url: str, headers: dict, method: str = "GET", body: dict | None = None) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _http_form(url: str, form: dict) -> dict:
    data = urllib.parse.urlencode(form).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_token(tenant_id: str, client_id: str, client_secret: str) -> str:
    """OAuth2 client-credentials contra Azure AD — el service principal es del
    usuario, esta función solo lo usa para pedir un token efímero."""
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    form = {"grant_type": "client_credentials", "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://analysis.windows.net/powerbi/api/.default"}
    return _http_form(url, form)["access_token"]


def list_workspace_ids(token: str, top: int = 5000, max_pages: int = 20) -> list[dict]:
    """Lista ``{id, name}`` de todos los workspaces activos del tenant, vía
    ``admin/groups`` — el primer paso para escanear TODO el tenant sin que el
    usuario tenga que pasar IDs a mano.

    Un tenant multinacional puede tener más de 5.000 workspaces (el máximo
    por página de esta API): se pagina con ``$skip`` hasta agotar los
    resultados o llegar a ``max_pages`` (por defecto 20 × 5.000 = 100.000
    workspaces, más que suficiente para cualquier tenant real)."""
    headers = {"Authorization": f"Bearer {token}"}
    out: list[dict] = []
    for page in range(max_pages):
        skip = page * top
        url = (f"{_ADMIN_BASE}/groups?$top={top}&$skip={skip}"
              "&$filter=type eq 'Workspace' and state eq 'Active'")
        data = _http_json(url, headers)
        batch = data.get("value", [])
        out.extend({"id": g["id"], "name": g.get("name", "")} for g in batch)
        if len(batch) < top:
            break
    return out


def _chunk(items: list, size: int):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def _scan_batch(token: str, workspace_ids: list[str]) -> dict:
    """Un ciclo completo getInfo -> scanStatus (poll) -> scanResult para un
    lote de workspaces (máx. ``_SCAN_BATCH_SIZE`` por vez, límite de la API)."""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = (f"{_ADMIN_BASE}/workspaces/getInfo"
          "?lineage=True&datasetSchema=True&datasetExpressions=True")
    info = _http_json(url, headers, method="POST", body={"workspaces": workspace_ids})
    scan_id = info["id"]
    status_url = f"{_ADMIN_BASE}/workspaces/scanStatus/{scan_id}"
    for _ in range(_SCAN_MAX_POLLS):
        status = _http_json(status_url, headers)
        if status.get("status") == "Succeeded":
            break
        time.sleep(_SCAN_POLL_SECONDS)
    else:
        raise TimeoutError(
            "El scan de Power BI (Admin API) no terminó a tiempo. "
            "Probá de nuevo o escaneá menos workspaces por vez.")
    return _http_json(f"{_ADMIN_BASE}/workspaces/scanResult/{scan_id}", headers)


def read_scanner(tenant_id: str | None = None, client_id: str | None = None,
                 client_secret: str | None = None, workspace_ids: list[str] | None = None,
                 max_workspaces: int | None = None) -> list[PowerBIModel]:
    """Escanea TODO el tenant (o los workspaces pasados) vía Scanner API y
    devuelve un ``PowerBIModel`` por cada dataset encontrado — nunca filas.

    Sin credenciales pasadas explícitamente, las toma de las variables de
    entorno (``POWERBI_TENANT_ID`` / ``POWERBI_CLIENT_ID`` /
    ``POWERBI_CLIENT_SECRET``) — nunca las pide, nunca las guarda."""
    tenant_id = tenant_id or os.environ.get("POWERBI_TENANT_ID")
    client_id = client_id or os.environ.get("POWERBI_CLIENT_ID")
    client_secret = client_secret or os.environ.get("POWERBI_CLIENT_SECRET")
    if not all((tenant_id, client_id, client_secret)):
        raise RuntimeError(
            "Faltan credenciales del service principal: configurá "
            "POWERBI_TENANT_ID / POWERBI_CLIENT_ID / POWERBI_CLIENT_SECRET "
            "como variables de entorno (ver docs/BI_TENANT_SCAN.md).")

    token = _get_token(tenant_id, client_id, client_secret)
    if workspace_ids is None:
        workspace_ids = [w["id"] for w in list_workspace_ids(token)]
    if max_workspaces:
        workspace_ids = workspace_ids[:max_workspaces]

    models: list[PowerBIModel] = []
    for batch in _chunk(workspace_ids, _SCAN_BATCH_SIZE):
        if not batch:
            continue
        data = _scan_batch(token, batch)
        models.extend(_models_from_scanner(data))
    return models


def _models_from_scanner(data: dict) -> list[PowerBIModel]:
    """Convierte el JSON de un scanResult de la Scanner API en un
    ``PowerBIModel`` POR DATASET (un tenant puede tener miles)."""
    models: list[PowerBIModel] = []
    for ws in data.get("workspaces", []) or []:
        ws_name = ws.get("name", "")
        ws_models: list[PowerBIModel] = []
        for ds in ws.get("datasets", []) or []:
            model = PowerBIModel(
                name=ds.get("name", "SemanticModel"), source="Scanner API (tenant)",
                workspace=ws_name, dataset_id=ds.get("id", ""))
            for t in ds.get("tables", []) or []:
                tname = t.get("name", "")
                model.tables.append(tname)
                for c in t.get("columns", []) or []:
                    model.columns.append(Column(tname, c.get("name", ""), c.get("dataType", "")))
                for m in t.get("measures", []) or []:
                    model.measures.append(Measure(
                        tname, m.get("name", ""), m.get("expression", ""),
                        description=m.get("description", "")))
                src_texts = [s.get("expression", "") for s in (t.get("source") or [])
                            if isinstance(s, dict)]
                if src_texts:
                    label = _source_label_from_mquery("\n".join(src_texts))
                    if label:
                        model.table_sources[tname] = label
            for r in ds.get("relationships", []) or []:
                model.relationships.append(Relationship(
                    r.get("fromTable", ""), r.get("fromColumn", ""),
                    r.get("toTable", ""), r.get("toColumn", ""),
                    r.get("crossFilteringBehavior", "") == "BothDirections"))
            model.roles = [ro.get("name", "") for ro in (ds.get("roles") or [])]
            ws_models.append(model)
        # reportes: se linkean por datasetId cuando el Scanner lo trae; si un
        # workspace tiene un solo dataset, se lo asignamos igual sin ambigüedad.
        for rp in ws.get("reports", []) or []:
            rname = rp.get("name", "")
            target = next((m for m in ws_models if m.dataset_id and
                          m.dataset_id == rp.get("datasetId")), None)
            if target is None and len(ws_models) == 1:
                target = ws_models[0]
            if target is not None:
                target.reports.append(rname)
        models.extend(ws_models)
    return models


def ingest_tenant(lang: str = "es", **kwargs) -> dict[str, pd.DataFrame | list]:
    """Escanea TODO el tenant (``read_scanner``) y devuelve las tablas
    normalizadas de gobierno, agregadas sobre todos los datasets/workspaces
    encontrados — mismo esquema por columna que ``ingest_pbip``, para que el
    resto del programa (tablero, exportadores, API) no tenga que distinguir
    entre un modelo local y un tenant completo."""
    models = read_scanner(**kwargs)
    cols = {
        "catalog": ["dataset", "domain", "description", "owner", "steward", "classification",
                   "source", "refresh", "rows", "columns", "last_updated"],
        "dictionary": ["dataset", "column", "type", "pii", "business_term", "description"],
        "glossary": ["term_id", "term", "definition", "owner", "linked_datasets"],
        "lineage": ["source_id", "source", "source_layer", "target_id", "target", "target_layer"],
        "quality": ["rule_id", "dataset", "column", "dimension", "description", "score",
                   "threshold", "status", "affected_rows"],
        "sources": ["table", "source"],
    }
    if not models:
        out = {k: pd.DataFrame(columns=v) for k, v in cols.items()}
        out["_models"] = []
        return out
    return {
        "catalog": pd.concat([to_catalog(m, lang) for m in models], ignore_index=True),
        "dictionary": pd.concat([to_dictionary(m) for m in models], ignore_index=True),
        "glossary": pd.concat([to_glossary(m) for m in models], ignore_index=True),
        "lineage": pd.concat([to_lineage(m) for m in models], ignore_index=True),
        "quality": pd.concat([to_quality(m, lang) for m in models], ignore_index=True),
        "sources": pd.concat([to_sources(m) for m in models], ignore_index=True),
        "_models": models,
    }


# ---------------------------------------------------- normalización a MVDG
def to_catalog(model: PowerBIModel, lang: str = "es") -> pd.DataFrame:
    """Una fila por MODELO (dataset semántico), con las columnas de catalog_df."""
    # `rows` era 0 fijo con el comentario «metadata, sin filas», y para un
    # modelo leído del TMSL es cierto. Pero un .pbit que trae los datos
    # empotrados SÍ tiene filas, y el generador las declara: decir 0 cuando
    # el archivo dice 3694 no es prudencia, es un dato mal. Sin declaración
    # sigue siendo 0, que es lo honesto ahí.
    descripcion = (f"Modelo semántico Power BI · {len(model.tables)} tablas, "
                   f"{len(model.measures)} medidas")
    if model.generator:
        descripcion += f" · generado con {model.generator}"
    return pd.DataFrame([{
        "dataset": model.name,
        "domain": f"BI / Power BI · {model.workspace}" if model.workspace else "BI / Power BI",
        "description": descripcion,
        "owner": "—",
        "steward": "—",
        "classification": "PII?" if any(
            k in c.name.lower() for c in model.columns
            for k in ("doc", "cedula", "email", "nombre", "telefono")) else "Interno",
        "source": model.source,
        "refresh": "—",
        "rows": sum(model.table_rows.values()),
        "columns": len(model.columns),
        "last_updated": pd.Timestamp.today().date().isoformat(),
    }])


def to_dictionary(model: PowerBIModel) -> pd.DataFrame:
    """Una fila por columna del modelo, con las columnas de dictionary_df."""
    rows = [{
        "dataset": f"{model.name}.{c.table}",
        "column": c.name,
        "type": c.data_type or ("calculated" if c.is_calculated else ""),
        "pii": any(k in c.name.lower() for k in
                   ("doc", "cedula", "email", "nombre", "telefono", "direccion")),
        "business_term": "",
        "description": (f"Columna calculada: {c.dax}" if c.is_calculated
                        else f"Origen: {c.source_column}" if c.source_column else ""),
    } for c in model.columns]
    return pd.DataFrame(rows)


def to_glossary(model: PowerBIModel) -> pd.DataFrame:
    """Cada MEDIDA es un término de negocio: nombre + DAX como definición."""
    rows = [{
        "term_id": f"M{i:03d}",
        "term": m.name,
        "definition": m.description or f"[DAX] {m.dax}",
        "owner": m.display_folder or "Modelo BI",
        "linked_datasets": f"{model.name}.{m.table}",
    } for i, m in enumerate(model.measures, 1)]
    return pd.DataFrame(rows)


def to_lineage(model: PowerBIModel) -> pd.DataFrame:
    """Linaje REAL dentro de Power BI: SQL/fuente → tabla → modelo → reporte
    (columnas de lineage_df). El primer tramo solo aparece para las tablas
    donde se pudo detectar el origen (SQL Server u otro conector) en su
    partición M — si no se detectó nada, la tabla arranca la cadena."""
    rows = []
    for t in model.tables:
        src_label = model.table_sources.get(t)
        if src_label:
            rows.append({
                "source_id": f"src_{t}", "source": src_label, "source_layer": "source",
                "target_id": f"tbl_{t}", "target": t, "target_layer": "curated",
            })
        rows.append({
            "source_id": f"tbl_{t}", "source": t, "source_layer": "curated",
            "target_id": f"model_{model.name}", "target": model.name, "target_layer": "mart",
        })
    for rep in (model.reports or ["(reporte)"]):
        rows.append({
            "source_id": f"model_{model.name}", "source": model.name, "source_layer": "mart",
            "target_id": f"rep_{rep}", "target": rep, "target_layer": "bi",
        })
    return pd.DataFrame(rows)


def to_sources(model: PowerBIModel) -> pd.DataFrame:
    """Una fila por tabla con el origen SQL/M detectado (o vacío si no se pudo
    detectar) — para mostrar en el tablero qué tan bien se pudo trazar la
    cadena SQL → dataset → reporte."""
    return pd.DataFrame([{
        "table": t, "source": model.table_sources.get(t, ""),
    } for t in model.tables])


def to_quality(model: PowerBIModel, lang: str = "es") -> pd.DataFrame:
    """Reglas de SALUD DEL MODELO como resultados de calidad (columnas de evaluate_rules).

    Dimensión 'model' — se integra al motor de 6 dimensiones DAMA como una 7ª
    de gobierno del modelo BI. Cada chequeo devuelve score 0-100 + estado.
    """
    def status(score: float, thr: float) -> str:
        return "pass" if score >= thr else ("warn" if score >= thr - 15 else "fail")

    n_meas = max(len(model.measures), 1)
    documented = sum(1 for m in model.measures if m.description)
    # medidas duplicadas por DAX idéntico
    seen: dict[str, int] = {}
    for m in model.measures:
        key = re.sub(r"\s+", " ", m.dax.strip().lower())
        seen[key] = seen.get(key, 0) + 1
    dupes = sum(v - 1 for v in seen.values() if v > 1)
    # columnas referenciadas por alguna medida (heurística: nombre aparece en algún DAX)
    dax_blob = " ".join(m.dax for m in model.measures).lower()
    orphan_cols = sum(1 for c in model.columns if c.name.lower() not in dax_blob)
    # anti-patrón: columna calculada que probablemente debería ser medida
    calc_cols = sum(1 for c in model.columns if c.is_calculated)

    checks = [
        ("PBI-01", "documentación de medidas",
         round(100 * documented / n_meas, 1), 80, "completeness", n_meas - documented),
        ("PBI-02", "medidas sin DAX duplicado",
         round(100 * (n_meas - dupes) / n_meas, 1), 90, "uniqueness", dupes),
        ("PBI-03", "cobertura RLS (roles definidos)",
         100.0 if model.roles else 0.0, 50, "validity", 0 if model.roles else 1),
        ("PBI-04", "columnas referenciadas (no huérfanas)",
         round(100 * (len(model.columns) - orphan_cols) / max(len(model.columns), 1), 1),
         60, "consistency", orphan_cols),
        ("PBI-05", "columnas calculadas (candidatas a medida)",
         round(100 * (len(model.columns) - calc_cols) / max(len(model.columns), 1), 1),
         85, "validity", calc_cols),
    ]
    rows = [{
        "rule_id": rid, "dataset": model.name, "column": "—", "dimension": dim,
        "description": desc, "score": sc, "threshold": thr,
        "status": status(sc, thr), "affected_rows": aff,
    } for rid, desc, sc, thr, dim, aff in checks]
    return pd.DataFrame(rows)


def _normalizar(model: PowerBIModel, lang: str = "es") -> dict[str, pd.DataFrame]:
    """Las tablas de gobierno de un modelo, sea de donde sea que se leyó.

    Estaba copiado en cada ``ingest_*``; con .pbit sumándose como tercer
    origen, una copia más era una copia de más — y la que se olvidara de
    actualizar iba a dar tablas distintas para el mismo modelo."""
    return {
        "catalog": to_catalog(model, lang),
        "dictionary": to_dictionary(model),
        "glossary": to_glossary(model),
        "lineage": to_lineage(model),
        "quality": to_quality(model, lang),
        "sources": to_sources(model),
        "_model": model,
    }


def ingest_pbip(folder: str, lang: str = "es") -> dict[str, pd.DataFrame]:
    """Atajo: lee un .pbip y devuelve las tablas normalizadas listas para el motor."""
    return _normalizar(read_pbip(folder), lang)


# ------------------------------------------------- ejemplo incluido (real)
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EXAMPLE_DIR = os.path.join(_ROOT, "assets", "samples", "powerbi", "AdventureWorksDemo",
                            "AdventureWorksDemo.SemanticModel")

# workspaces simulados para el ejemplo ILUSTRATIVO de tenant multinacional —
# ver assets/samples/THIRD_PARTY_DATA.md. No representa una empresa real.
_EXAMPLE_TENANT_WORKSPACES = [
    ("Ventas EMEA", "Panel Ejecutivo EMEA"),
    ("Ventas LATAM", "Panel Ejecutivo LATAM"),
    ("Ventas APAC", "Panel Ejecutivo APAC"),
    ("Finanzas Corporativas", "Panel de Finanzas Global"),
]
_EXAMPLE_SOURCE_NOTE = ("Ejemplo ilustrativo — modelo real (Adventure Works Demo, GitHub, MIT) "
                        "replicado en workspaces simulados para representar una empresa "
                        "multinacional. No es un escaneo real de un tenant.")


def load_example_model() -> PowerBIModel:
    """El modelo real de ejemplo incluido con el programa — un proyecto
    .pbip/TMDL público (MIT) de GitHub. Ver assets/samples/THIRD_PARTY_DATA.md."""
    return read_pbip(_EXAMPLE_DIR)


def load_example_tenant() -> list[PowerBIModel]:
    """Ejemplo ILUSTRATIVO de cómo se ve ``ingest_tenant()`` a escala: el
    mismo modelo real de ``load_example_model()``, replicado y re-etiquetado
    en varios workspaces simulados representando una empresa multinacional
    (ej. "Ventas EMEA/LATAM/APAC"). Deliberadamente NO es un escaneo real —
    no reemplaza al modo Scanner API con tus propias credenciales, que sí
    trae datos verdaderos de tu tenant."""
    base = load_example_model()
    models = []
    for i, (workspace, report) in enumerate(_EXAMPLE_TENANT_WORKSPACES, 1):
        m = PowerBIModel(
            name=base.name, tables=list(base.tables), columns=list(base.columns),
            measures=list(base.measures), relationships=list(base.relationships),
            roles=list(base.roles), reports=[report],
            table_sources=dict(base.table_sources), workspace=workspace,
            dataset_id=f"example-{i}", source=_EXAMPLE_SOURCE_NOTE)
        models.append(m)
    return models


def ingest_example(lang: str = "es") -> dict[str, pd.DataFrame]:
    """Atajo: el ejemplo real (un solo modelo) con las tablas normalizadas."""
    model = load_example_model()
    return {
        "catalog": to_catalog(model, lang),
        "dictionary": to_dictionary(model),
        "glossary": to_glossary(model),
        "lineage": to_lineage(model),
        "quality": to_quality(model, lang),
        "sources": to_sources(model),
        "_model": model,
    }


def ingest_example_tenant(lang: str = "es") -> dict[str, pd.DataFrame | list]:
    """Atajo: el ejemplo ilustrativo de tenant multinacional, con las tablas
    normalizadas agregadas — mismo esquema de salida que ``ingest_tenant()``."""
    models = load_example_tenant()
    return {
        "catalog": pd.concat([to_catalog(m, lang) for m in models], ignore_index=True),
        "dictionary": pd.concat([to_dictionary(m) for m in models], ignore_index=True),
        "glossary": pd.concat([to_glossary(m) for m in models], ignore_index=True),
        "lineage": pd.concat([to_lineage(m) for m in models], ignore_index=True),
        "quality": pd.concat([to_quality(m, lang) for m in models], ignore_index=True),
        "sources": pd.concat([to_sources(m) for m in models], ignore_index=True),
        "_models": models,
    }
