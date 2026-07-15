"""
MV Data Governance · Conector de migración hacia Collibra.

Mismo principio de diseño que ``purview_export.py``: es un **acelerador**
que empuja el catálogo, el diccionario y el glosario ya gobernados por este
programa hacia Collibra — nunca una fachada que solo el consultor puede
tocar. Ver el docstring de ``purview_export`` para la explicación completa
del criterio "acelerador vs. caja negra".

Diferencia clave con Purview: el modelo de datos de Collibra (Communities
→ Domains → Assets → Attributes) es **configurable por instancia** — cada
cliente tiene sus propios IDs de dominio y, en general, sus propios tipos
de asset para "Tabla"/"Columna" (dependen de qué Operating Model instaló
cada organización). No hay forma de adivinarlos desde afuera. Por eso:

    - ``COLLIBRA_DOMAIN_ID`` es OBLIGATORIO — lo saca el usuario de su
      propia instancia (Settings → Domains, o la URL al entrar al dominio).
    - ``COLLIBRA_TABLE_TYPE_ID`` / ``COLLIBRA_COLUMN_TYPE_ID`` también son
      obligatorios si vas a empujar catálogo/diccionario — dependen del
      Operating Model de cada cliente (Data Dictionary vs. otro).
    - ``COLLIBRA_TERM_TYPE_ID`` tiene un default: el UUID de "Business
      Term" que Collibra documenta como parte de su modelo de fábrica
      (``00000000-0000-0000-0000-000000011001``) — funciona out-of-the-box
      en la mayoría de las instancias, pero es igual de sobreescribible.
    - El typeId de "Definition" (para la descripción) SÍ es un UUID fijo
      de fábrica en toda instancia Collibra: ``00000000-0000-0000-0000-000000000202``.

Apagado por defecto. Credenciales propias del usuario (nunca las maneja
este programa más allá de leer variables de entorno): ``COLLIBRA_BASE_URL``,
``COLLIBRA_USERNAME``, ``COLLIBRA_PASSWORD``, ``COLLIBRA_DOMAIN_ID``.

Implementado contra la documentación oficial del Collibra Developer Portal
(REST API 2.0) verificada el 2026-07-15. NO se probó contra una instancia
real de Collibra (no hay una disponible en este entorno de desarrollo, y
Collibra no ofrece un entorno de prueba de autoservicio gratuito — a
diferencia de Purview). Usá ``dry_run=True`` para revisar el payload antes
de mandar nada, y probá primero contra un dominio de prueba.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

import pandas as pd

_TIMEOUT = 30
_REQUIRED_ENV = ("COLLIBRA_BASE_URL", "COLLIBRA_USERNAME", "COLLIBRA_PASSWORD",
                 "COLLIBRA_DOMAIN_ID")
# UUIDs de fábrica documentados por Collibra (developer.collibra.com) — el
# de "Definition" es fijo en toda instancia; el de "Business Term" es el
# default del modelo estándar pero overridable.
DEFINITION_ATTRIBUTE_TYPE_ID = "00000000-0000-0000-0000-000000000202"
_DEFAULT_TERM_TYPE_ID = "00000000-0000-0000-0000-000000011001"


def configured() -> bool:
    return all(os.environ.get(v) for v in _REQUIRED_ENV)


def catalog_configured() -> bool:
    """Además de lo básico, empujar catálogo/diccionario necesita los IDs
    de tipo de asset Tabla/Columna del Operating Model del cliente."""
    return configured() and bool(os.environ.get("COLLIBRA_TABLE_TYPE_ID")) \
        and bool(os.environ.get("COLLIBRA_COLUMN_TYPE_ID"))


def _base_url() -> str:
    return os.environ["COLLIBRA_BASE_URL"].rstrip("/")


def _http_json(url: str, headers: dict, method: str = "GET",
               body: dict | None = None) -> tuple[dict, list[str]]:
    """Devuelve (json, set_cookie_headers) — necesitamos las cookies para
    la sesión de Collibra."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        cookies = resp.headers.get_all("Set-Cookie") or []
        raw = resp.read()
        return (json.loads(raw.decode("utf-8")) if raw else {}), cookies


def _sign_in() -> str:
    """Login por sesión (usuario/contraseña propios del cliente). Devuelve
    la cookie JSESSIONID a mandar en el resto de los requests."""
    url = f"{_base_url()}/rest/2.0/auth/sessions"
    body = {"username": os.environ["COLLIBRA_USERNAME"],
            "password": os.environ["COLLIBRA_PASSWORD"]}
    _, cookies = _http_json(url, {"Content-Type": "application/json"}, method="POST", body=body)
    for c in cookies:
        if c.startswith("JSESSIONID="):
            return c.split(";", 1)[0]
    raise RuntimeError("Collibra no devolvió JSESSIONID al iniciar sesión.")


def _sign_out(cookie: str) -> None:
    """Best-effort: cerrar la sesión nunca debe romper el push si falla."""
    try:
        _http_json(f"{_base_url()}/rest/2.0/auth/sessions/current",
                  {"Cookie": cookie}, method="DELETE")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, KeyError, ValueError):
        pass


def _headers(cookie: str) -> dict:
    return {"Cookie": cookie, "Content-Type": "application/json"}


# --------------------------------------------------------------- payloads
def build_asset_payloads(catalog: pd.DataFrame, dictionary: pd.DataFrame,
                         table_type_id: str, column_type_id: str,
                         domain_id: str) -> list[dict]:
    """Un asset por dataset (Tabla) + uno por columna (Columna), con su
    descripción como atributo separado (así lo pide la API de Collibra)."""
    assets = []
    for _, row in catalog.iterrows():
        assets.append({
            "kind": "table", "dataset": row["dataset"], "column": None,
            "asset": {"name": row["dataset"], "typeId": table_type_id, "domainId": domain_id},
            "description": row.get("description", ""),
        })
    for _, row in dictionary.iterrows():
        assets.append({
            "kind": "column", "dataset": row["dataset"], "column": row["column"],
            "asset": {"name": f"{row['dataset']}.{row['column']}",
                     "typeId": column_type_id, "domainId": domain_id},
            "description": row.get("description", ""),
        })
    return assets


def build_term_payloads(glossary: pd.DataFrame, term_type_id: str, domain_id: str,
                        curation_lookup=None) -> list[dict]:
    terms = []
    for _, row in glossary.iterrows():
        text = row["definition"]
        if curation_lookup is not None:
            _status, cur_text = curation_lookup(row["term_id"])
            if cur_text:
                text = cur_text
        terms.append({
            "term_id": row["term_id"],
            "asset": {"name": row["term"], "typeId": term_type_id, "domainId": domain_id},
            "description": text,
        })
    return terms


# ------------------------------------------------------------------ push
def _push_assets(payloads: list[dict], cookie: str) -> list[dict]:
    created = []
    for item in payloads:
        asset = _http_json(f"{_base_url()}/rest/2.0/assets", _headers(cookie),
                           method="POST", body=item["asset"])[0]
        if item.get("description"):
            _http_json(f"{_base_url()}/rest/2.0/attributes", _headers(cookie), method="POST",
                      body={"assetId": asset["id"], "typeId": DEFINITION_ATTRIBUTE_TYPE_ID,
                            "value": item["description"]})
        created.append({**item, "asset_id": asset.get("id")})
    return created


def push_catalog(catalog: pd.DataFrame, dictionary: pd.DataFrame, dry_run: bool = True,
                 cookie: str | None = None) -> dict:
    """``cookie`` es opcional — si no se pasa, inicia (y cierra) su propia
    sesión. Pasalo para reusar una sesión entre varias llamadas (push_all)."""
    domain_id = os.environ.get("COLLIBRA_DOMAIN_ID", "")
    table_type_id = os.environ.get("COLLIBRA_TABLE_TYPE_ID", "")
    column_type_id = os.environ.get("COLLIBRA_COLUMN_TYPE_ID", "")
    payloads = build_asset_payloads(catalog, dictionary, table_type_id or "<COLLIBRA_TABLE_TYPE_ID>",
                                    column_type_id or "<COLLIBRA_COLUMN_TYPE_ID>",
                                    domain_id or "<COLLIBRA_DOMAIN_ID>")
    if dry_run:
        return {"dry_run": True, "payloads": payloads, "asset_count": len(payloads)}
    if not catalog_configured():
        raise RuntimeError("Collibra no configurado para catálogo — faltan "
                           "COLLIBRA_DOMAIN_ID/COLLIBRA_TABLE_TYPE_ID/COLLIBRA_COLUMN_TYPE_ID.")
    own_session = cookie is None
    cookie = cookie or _sign_in()
    try:
        created = _push_assets(payloads, cookie)
    finally:
        if own_session:
            _sign_out(cookie)
    return {"dry_run": False, "asset_count": len(created), "created": created}


def push_glossary(glossary: pd.DataFrame, curation_lookup=None, dry_run: bool = True,
                  cookie: str | None = None) -> dict:
    domain_id = os.environ.get("COLLIBRA_DOMAIN_ID", "")
    term_type_id = os.environ.get("COLLIBRA_TERM_TYPE_ID") or _DEFAULT_TERM_TYPE_ID
    payloads = build_term_payloads(glossary, term_type_id, domain_id or "<COLLIBRA_DOMAIN_ID>",
                                   curation_lookup)
    if dry_run:
        return {"dry_run": True, "terms": payloads, "term_count": len(payloads)}
    if not configured():
        raise RuntimeError("Collibra no configurado — faltan variables de entorno.")
    own_session = cookie is None
    cookie = cookie or _sign_in()
    try:
        created = _push_assets(payloads, cookie)
    finally:
        if own_session:
            _sign_out(cookie)
    return {"dry_run": False, "term_count": len(created), "created": created}


def push_all(catalog: pd.DataFrame, dictionary: pd.DataFrame, glossary: pd.DataFrame,
            curation_lookup=None, dry_run: bool = True) -> dict:
    """Orquesta el push completo, reusando una sola sesión (JSESSIONID)
    entre catálogo y glosario en vez de loguearse dos veces."""
    cookie = _sign_in() if (not dry_run and configured()) else None
    try:
        cat_result = push_catalog(catalog, dictionary, dry_run=dry_run, cookie=cookie)
        gloss_result = push_glossary(glossary, curation_lookup, dry_run=dry_run, cookie=cookie)
    finally:
        if cookie:
            _sign_out(cookie)
    return {"dry_run": dry_run, "catalog": cat_result, "glossary": gloss_result}
