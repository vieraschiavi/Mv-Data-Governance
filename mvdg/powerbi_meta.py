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

  B) TENANT-WIDE / gobernanza — ``read_scanner(...)``  (esqueleto)
     Usa la Scanner API (Admin REST ``admin/workspaces/getInfo``) con service
     principal para catalogar TODO el tenant: datasets, reportes, medidas, DAX,
     M, RLS y linaje. Devuelve metadata, nunca filas.

Ambos caminos entregan un ``PowerBIModel`` que se normaliza a las MISMAS tablas
que ya usa el motor de gobierno:

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
``lineage.lineage_figure`` para el resto del programa.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field

import pandas as pd

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
    source: str = "PBIP (offline)"


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


def _parse_table_tmdl(text: str) -> tuple[str, list[Column], list[Measure], str | None]:
    """Parsea un archivo TMDL de tabla: devuelve (nombre_tabla, columnas, medidas,
    fuente detectada de la partición — SQL Server u otro conector, o None)."""
    lines = text.splitlines()
    table_name = ""
    columns: list[Column] = []
    measures: list[Measure] = []
    table_source: str | None = None

    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        m = _TABLE_RE.match(line)
        if m and not table_name:
            table_name = _unquote(m.group(1))
            i += 1
            continue

        # ----- medida (el DAX puede continuar en líneas más indentadas)
        m = _MEASURE_RE.match(line)
        if m:
            base_indent = _indent(line)
            name = _unquote(m.group(1))
            dax_parts = [m.group(2).rstrip()]
            folder, desc = "", ""
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                if not nxt.strip():
                    j += 1
                    continue
                ind = _indent(nxt)
                low = nxt.strip()
                if ind <= base_indent:
                    break  # nuevo objeto de la tabla
                # propiedades conocidas de la medida
                if low.startswith("displayFolder:"):
                    folder = low.split(":", 1)[1].strip()
                elif low.startswith("description:"):
                    desc = low.split(":", 1)[1].strip()
                elif low.startswith(("formatString:", "lineageTag:", "annotation",
                                     "changedProperty", "isHidden", "formatStringDefinition")):
                    pass
                else:
                    dax_parts.append(nxt.strip())  # continuación del DAX
                j += 1
            dax = " ".join(p for p in dax_parts if p).strip()
            measures.append(Measure(table_name, name, dax, folder, desc))
            i = j
            continue

        # ----- columna (leemos dataType / sourceColumn / expresión si es calculada)
        m = _COLUMN_RE.match(line)
        if m:
            base_indent = _indent(line)
            name = _unquote(m.group(1))
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
            columns.append(Column(table_name, name, dtype, src, is_calc, cdax))
            i = j
            continue

        # ----- partición (expresión M): de acá sale el origen real de la tabla
        if _PARTITION_RE.match(line):
            base_indent = _indent(line)
            block_lines = []
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                if nxt.strip() and _indent(nxt) <= base_indent:
                    break
                block_lines.append(nxt)
                j += 1
            if table_source is None:
                table_source = _source_label_from_mquery("\n".join(block_lines))
            i = j
            continue

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


# ----------------------------------------------------- camino B: Scanner API
def read_scanner(workspace_ids: list[str], token: str) -> PowerBIModel:
    """Esqueleto de ingesta tenant-wide vía Scanner API (Admin REST).

    Flujo real: POST admin/workspaces/getInfo?lineage=True&datasetSchema=True&
    datasetExpressions=True  ->  GetScanStatus  ->  GetScanResult.
    Requiere tenant setting 'Enhance admin APIs responses with detailed metadata'
    (+ DAX/mashup) y service principal con rol admin de lectura.
    Devuelve metadata, nunca filas.
    """
    import time
    import requests  # dependencia opcional; solo para el camino online

    base = "https://api.powerbi.com/v1.0/myorg/admin/workspaces"
    hdr = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(
        f"{base}/getInfo?lineage=True&datasetSchema=True&datasetExpressions=True",
        headers=hdr, json={"workspaces": workspace_ids}, timeout=60)
    r.raise_for_status()
    scan_id = r.json()["id"]
    while True:
        st = requests.get(f"{base}/scanStatus/{scan_id}", headers=hdr, timeout=30).json()
        if st.get("status") == "Succeeded":
            break
        time.sleep(2)
    data = requests.get(f"{base}/scanResult/{scan_id}", headers=hdr, timeout=120).json()
    return _model_from_scanner(data)


def _model_from_scanner(data: dict) -> PowerBIModel:
    """Convierte el JSON de la Scanner API en un PowerBIModel."""
    model = PowerBIModel(source="Scanner API (tenant)")
    for ws in data.get("workspaces", []):
        for ds in ws.get("datasets", []):
            model.name = ds.get("name", model.name)
            for t in ds.get("tables", []):
                tname = t.get("name", "")
                model.tables.append(tname)
                for c in t.get("columns", []):
                    model.columns.append(Column(
                        tname, c.get("name", ""), c.get("dataType", "")))
                for m in t.get("measures", []):
                    model.measures.append(Measure(
                        tname, m.get("name", ""), m.get("expression", ""),
                        description=m.get("description", "")))
        model.reports += [rp.get("name", "") for rp in ws.get("reports", [])]
    return model


# ---------------------------------------------------- normalización a MVDG
def to_catalog(model: PowerBIModel, lang: str = "es") -> pd.DataFrame:
    """Una fila por MODELO (dataset semántico), con las columnas de catalog_df."""
    return pd.DataFrame([{
        "dataset": model.name,
        "domain": "BI / Power BI",
        "description": f"Modelo semántico Power BI · {len(model.tables)} tablas, "
                       f"{len(model.measures)} medidas",
        "owner": "—",
        "steward": "—",
        "classification": "PII?" if any(
            k in c.name.lower() for c in model.columns
            for k in ("doc", "cedula", "email", "nombre", "telefono")) else "Interno",
        "source": model.source,
        "refresh": "—",
        "rows": 0,                       # metadata, sin filas
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


def ingest_pbip(folder: str, lang: str = "es") -> dict[str, pd.DataFrame]:
    """Atajo: lee un .pbip y devuelve las tablas normalizadas listas para el motor."""
    model = read_pbip(folder)
    return {
        "catalog": to_catalog(model, lang),
        "dictionary": to_dictionary(model),
        "glossary": to_glossary(model),
        "lineage": to_lineage(model),
        "quality": to_quality(model, lang),
        "sources": to_sources(model),
        "_model": model,
    }
