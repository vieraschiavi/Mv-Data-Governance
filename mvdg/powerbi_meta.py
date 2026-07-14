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


def list_workspace_ids(token: str, top: int = 5000) -> list[dict]:
    """Lista ``{id, name}`` de todos los workspaces activos del tenant, vía
    ``admin/groups`` — el primer paso para escanear TODO el tenant sin que el
    usuario tenga que pasar IDs a mano."""
    headers = {"Authorization": f"Bearer {token}"}
    url = (f"{_ADMIN_BASE}/groups?$top={top}"
          "&$filter=type eq 'Workspace' and state eq 'Active'")
    data = _http_json(url, headers)
    return [{"id": g["id"], "name": g.get("name", "")} for g in data.get("value", [])]


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
    return pd.DataFrame([{
        "dataset": model.name,
        "domain": f"BI / Power BI · {model.workspace}" if model.workspace else "BI / Power BI",
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
