"""
MV Data Governance · Conector de METADATA de Tableau (solo estructura, cero filas).

Mismo principio que ``powerbi_meta.py``: gobierna la CAPA DE BI en sí —
workbooks, datasources publicados, campos y campos calculados — nunca las
filas de datos. Usa la Metadata API (GraphQL) de Tableau Server/Cloud,
autenticada con un Personal Access Token (PAT) propio del usuario.

Flujo (``read_site``):
  1. Sign-in REST (``/api/{version}/auth/signin``) con el PAT -> token de sesión.
  2. Metadata API (``/api/metadata/graphql``) con ese token -> catálogo
     completo del sitio: workbooks, datasources publicados, sus campos (con
     la fórmula de los calculados) y las tablas de base de datos de las que
     salen.
  3. Sign-out (best-effort).

Apagado por defecto: solo corre si están cargadas ``TABLEAU_SERVER_URL`` /
``TABLEAU_TOKEN_NAME`` / ``TABLEAU_TOKEN_SECRET`` como variables de entorno
propias del usuario — ver ``docs/BI_TENANT_SCAN.md``. Implementado con
``urllib`` (misma librería estándar que ``ai_provider.py`` y el camino
tenant de Power BI), sin agregar una dependencia nueva al proyecto.

Nota sobre el esquema GraphQL: la consulta de ``_GRAPHQL_QUERY`` sigue el
esquema publicado por Tableau para la Metadata API (workbooks ->
upstreamDatasources -> fields/upstreamTables). No se probó contra un sitio
real de Tableau en este repo — si tu versión de Tableau Server difiere,
puede necesitar un ajuste puntual en esa consulta; el resto del módulo (el
parseo del JSON y los normalizadores) no depende de la versión.

Se normaliza a las MISMAS tablas que ya usa el motor de gobierno (paralelo
exacto a ``powerbi_meta.py``, un datasource publicado = un "dataset"):

    to_catalog(model)     -> columnas de catalog.catalog_df
    to_dictionary(model)  -> columnas de catalog.dictionary_df
    to_glossary(model)    -> columnas de glossary.glossary_df   (cada campo calculado = término)
    to_lineage(model)     -> columnas de lineage.lineage_df      (tabla BD → datasource → workbook)
    to_quality(model)     -> columnas de quality.evaluate_rules  (salud del sitio)
    to_sources(model)     -> una fila por datasource con las tablas de origen detectadas
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field

import pandas as pd

_TIMEOUT = 60  # segundos, por request HTTP
_API_VERSION = "3.22"


# ----------------------------------------------------------------- modelo
@dataclass
class Field:
    datasource: str
    name: str
    data_type: str = ""
    is_calculated: bool = False
    formula: str = ""
    description: str = ""


@dataclass
class Datasource:
    name: str
    project: str = ""
    upstream_tables: list[str] = field(default_factory=list)


@dataclass
class TableauModel:
    site: str = "Tableau"
    workbooks: list[str] = field(default_factory=list)
    datasources: list[Datasource] = field(default_factory=list)
    fields: list[Field] = field(default_factory=list)
    workbook_links: list[tuple[str, str]] = field(default_factory=list)  # (datasource, workbook)
    source: str = "Tableau Metadata API"


# --------------------------------------------------------------- conexión
_TABLEAU_ENV = ("TABLEAU_SERVER_URL", "TABLEAU_TOKEN_NAME", "TABLEAU_TOKEN_SECRET")


def configured() -> bool:
    """¿Hay credenciales de Tableau cargadas como variable de entorno?"""
    return all(os.environ.get(v) for v in _TABLEAU_ENV)


def _http_json(url: str, headers: dict, method: str = "GET", body: dict | None = None) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _sign_in(server: str, token_name: str, token_secret: str,
            site_content_url: str = "") -> tuple[str, str]:
    """Sign-in REST con Personal Access Token. Devuelve (token de sesión, site_id)."""
    url = f"{server.rstrip('/')}/api/{_API_VERSION}/auth/signin"
    body = {"credentials": {
        "personalAccessTokenName": token_name,
        "personalAccessTokenSecret": token_secret,
        "site": {"contentUrl": site_content_url},
    }}
    data = _http_json(url, {"Content-Type": "application/json", "Accept": "application/json"},
                      method="POST", body=body)
    cred = data["credentials"]
    return cred["token"], cred["site"]["id"]


def _sign_out(server: str, token: str) -> None:
    """Best-effort: cerrar la sesión nunca debe romper el escaneo si falla."""
    try:
        _http_json(f"{server.rstrip('/')}/api/{_API_VERSION}/auth/signout",
                  {"X-Tableau-Auth": token}, method="POST")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, KeyError, ValueError):
        pass


_GRAPHQL_QUERY = """
{
  workbooks {
    name
    projectName
    upstreamDatasources {
      name
      fields {
        name
        description
        ... on CalculatedField { formula }
      }
      upstreamTables {
        name
        schema
        database { name connectionType }
      }
    }
  }
}
"""


def _query_metadata(server: str, token: str) -> dict:
    url = f"{server.rstrip('/')}/api/metadata/graphql"
    return _http_json(url, {"X-Tableau-Auth": token, "Content-Type": "application/json"},
                      method="POST", body={"query": _GRAPHQL_QUERY})


def _model_from_metadata(data: dict, site: str = "Tableau") -> TableauModel:
    """Convierte la respuesta GraphQL de la Metadata API en un TableauModel."""
    model = TableauModel(site=site)
    seen_ds: set[str] = set()
    for wb in (data.get("data", {}).get("workbooks", []) or []):
        wname = wb.get("name", "")
        model.workbooks.append(wname)
        for ds in (wb.get("upstreamDatasources", []) or []):
            dname = ds.get("name", "")
            model.workbook_links.append((dname, wname))
            if dname in seen_ds:
                continue
            seen_ds.add(dname)
            tables = []
            for t in (ds.get("upstreamTables", []) or []):
                label = ".".join(p for p in (t.get("schema", ""), t.get("name", "")) if p)
                db = t.get("database") or {}
                if db.get("connectionType"):
                    label += f" ({db['connectionType']})"
                tables.append(label)
            model.datasources.append(Datasource(name=dname, upstream_tables=tables))
            for f in (ds.get("fields", []) or []):
                formula = f.get("formula", "") or ""
                model.fields.append(Field(
                    datasource=dname, name=f.get("name", ""),
                    is_calculated=bool(formula), formula=formula,
                    description=f.get("description", "") or ""))
    return model


def read_site(server: str | None = None, token_name: str | None = None,
             token_secret: str | None = None, site_content_url: str | None = None) -> TableauModel:
    """Escanea TODO el sitio de Tableau vía Metadata API: workbooks,
    datasources publicados, campos y sus tablas de origen. Nunca lee filas.

    Sin credenciales pasadas explícitamente, las toma de las variables de
    entorno (``TABLEAU_SERVER_URL`` / ``TABLEAU_TOKEN_NAME`` /
    ``TABLEAU_TOKEN_SECRET`` / ``TABLEAU_SITE`` opcional) — nunca las pide,
    nunca las guarda."""
    server = server or os.environ.get("TABLEAU_SERVER_URL")
    token_name = token_name or os.environ.get("TABLEAU_TOKEN_NAME")
    token_secret = token_secret or os.environ.get("TABLEAU_TOKEN_SECRET")
    site_content_url = site_content_url if site_content_url is not None else \
        os.environ.get("TABLEAU_SITE", "")
    if not all((server, token_name, token_secret)):
        raise RuntimeError(
            "Faltan credenciales: configurá TABLEAU_SERVER_URL / TABLEAU_TOKEN_NAME / "
            "TABLEAU_TOKEN_SECRET (y opcionalmente TABLEAU_SITE) — ver docs/BI_TENANT_SCAN.md.")

    token, _site_id = _sign_in(server, token_name, token_secret, site_content_url)
    try:
        data = _query_metadata(server, token)
    finally:
        _sign_out(server, token)
    return _model_from_metadata(data, site=site_content_url or "Default")


# ---------------------------------------------------- normalización a MVDG
def to_catalog(model: TableauModel, lang: str = "es") -> pd.DataFrame:
    """Una fila por DATASOURCE publicado, con las columnas de catalog_df."""
    rows = [{
        "dataset": ds.name,
        "domain": f"BI / Tableau · {model.site}",
        "description": f"Datasource publicado de Tableau · {len(ds.upstream_tables)} tablas de origen",
        "owner": "—",
        "steward": "—",
        "classification": "PII?" if any(
            k in fl.name.lower() for fl in model.fields if fl.datasource == ds.name
            for k in ("doc", "cedula", "email", "nombre", "telefono")) else "Interno",
        "source": model.source,
        "refresh": "—",
        "rows": 0,                       # metadata, sin filas
        "columns": sum(1 for fl in model.fields if fl.datasource == ds.name),
        "last_updated": pd.Timestamp.today().date().isoformat(),
    } for ds in model.datasources]
    return pd.DataFrame(rows)


def to_dictionary(model: TableauModel) -> pd.DataFrame:
    """Una fila por campo, con las columnas de dictionary_df."""
    rows = [{
        "dataset": f"{model.site}.{fl.datasource}",
        "column": fl.name,
        "type": "calculated" if fl.is_calculated else "",
        "pii": any(k in fl.name.lower() for k in
                   ("doc", "cedula", "email", "nombre", "telefono", "direccion")),
        "business_term": "",
        "description": f"Cálculo: {fl.formula}" if fl.is_calculated else fl.description,
    } for fl in model.fields]
    return pd.DataFrame(rows)


def to_glossary(model: TableauModel) -> pd.DataFrame:
    """Cada CAMPO CALCULADO es un término de negocio: nombre + fórmula como definición."""
    calc = [fl for fl in model.fields if fl.is_calculated]
    rows = [{
        "term_id": f"T{i:03d}",
        "term": fl.name,
        "definition": fl.description or f"[Cálculo] {fl.formula}",
        "owner": "Modelo BI",
        "linked_datasets": f"{model.site}.{fl.datasource}",
    } for i, fl in enumerate(calc, 1)]
    return pd.DataFrame(rows)


def to_lineage(model: TableauModel) -> pd.DataFrame:
    """Linaje REAL dentro de Tableau: tabla de BD → datasource publicado →
    workbook (columnas de lineage_df), sobre el mismo grafo de 5 capas que
    usa el resto del programa."""
    rows = []
    for ds in model.datasources:
        for tbl in ds.upstream_tables:
            rows.append({
                "source_id": f"src_{ds.name}_{tbl}", "source": tbl, "source_layer": "source",
                "target_id": f"ds_{ds.name}", "target": ds.name, "target_layer": "curated",
            })
    for dname, wname in model.workbook_links:
        rows.append({
            "source_id": f"ds_{dname}", "source": dname, "source_layer": "curated",
            "target_id": f"wb_{wname}", "target": wname, "target_layer": "bi",
        })
    return pd.DataFrame(rows)


def to_sources(model: TableauModel) -> pd.DataFrame:
    """Una fila por datasource con las tablas de origen detectadas (o vacío)."""
    return pd.DataFrame([{
        "table": ds.name,
        "source": "; ".join(ds.upstream_tables) if ds.upstream_tables else "",
    } for ds in model.datasources])


def to_quality(model: TableauModel, lang: str = "es") -> pd.DataFrame:
    """Reglas de SALUD DEL SITIO como resultados de calidad (columnas de
    evaluate_rules) — el mismo patrón que ``powerbi_meta.to_quality``."""
    def status(score: float, thr: float) -> str:
        return "pass" if score >= thr else ("warn" if score >= thr - 15 else "fail")

    calc = [fl for fl in model.fields if fl.is_calculated]
    n_calc = max(len(calc), 1)
    documented = sum(1 for fl in calc if fl.description)
    seen: dict[str, int] = {}
    for fl in calc:
        key = re.sub(r"\s+", " ", fl.formula.strip().lower())
        seen[key] = seen.get(key, 0) + 1
    dupes = sum(v - 1 for v in seen.values() if v > 1)

    n_ds = max(len(model.datasources), 1)
    traced = sum(1 for ds in model.datasources if ds.upstream_tables)

    n_wb = max(len(model.workbooks), 1)
    linked_wbs = {w for _, w in model.workbook_links}
    embedded = max(len(model.workbooks) - len(linked_wbs), 0)

    checks = [
        ("TAB-01", "documentación de campos calculados",
         round(100 * documented / n_calc, 1), 80, "completeness", n_calc - documented),
        ("TAB-02", "campos calculados sin fórmula duplicada",
         round(100 * (n_calc - dupes) / n_calc, 1), 90, "uniqueness", dupes),
        ("TAB-03", "datasources con origen trazado (tabla de BD detectada)",
         round(100 * traced / n_ds, 1), 80, "consistency", n_ds - traced),
        ("TAB-04", "workbooks sobre datasource publicado (no embebido)",
         round(100 * (n_wb - embedded) / n_wb, 1), 70, "validity", embedded),
    ]
    rows = [{
        "rule_id": rid, "dataset": model.site, "column": "—", "dimension": dim,
        "description": desc, "score": sc, "threshold": thr,
        "status": status(sc, thr), "affected_rows": aff,
    } for rid, desc, sc, thr, dim, aff in checks]
    return pd.DataFrame(rows)


def ingest_site(lang: str = "es", **kwargs) -> dict[str, pd.DataFrame]:
    """Atajo: escanea el sitio y devuelve las tablas normalizadas listas para el motor."""
    model = read_site(**kwargs)
    return {
        "catalog": to_catalog(model, lang),
        "dictionary": to_dictionary(model),
        "glossary": to_glossary(model),
        "lineage": to_lineage(model),
        "quality": to_quality(model, lang),
        "sources": to_sources(model),
        "_model": model,
    }
