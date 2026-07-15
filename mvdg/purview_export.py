"""
MV Data Governance · Conector de migración hacia Microsoft Purview.

Principio de diseño (explícito, no accidental — surgió charlando con el
usuario sobre cómo posicionar esto sin vender humo): este conector es un
**acelerador**, no un reemplazo silencioso de Purview.

    Tu programa hace el trabajo pesado (perfilar, correr las reglas de
    calidad, generar el glosario, detectar PII, curar las definiciones con
    un responsable) y al final EMPUJA el resultado a Purview por API, que
    sigue siendo la plataforma que el cliente audita y usa después de que
    el consultor se va. Nunca al revés: Purview no queda como una fachada
    que solo vos podés tocar — el flujo tiene que quedar documentado y
    repetible por cualquiera del equipo del cliente.

Qué empuja, y de dónde sale cada dato:
    - Catálogo → una entidad ``rdbms_table`` por dataset (tipo genérico de
      Atlas/Purview, no específico de una nube — no asumimos que la fuente
      sea Azure).
    - Diccionario → una entidad ``rdbms_column`` por columna.
    - Glosario → un Glossary "MV Data Governance" + un término por
      definición. El estado en Purview (Draft/Approved) sale de la
      pestaña 🖊️ Curaduría: si un Data Owner/Steward ya validó o modificó
      la definición, se manda **Approved**; si sigue siendo la sugerencia
      de IA sin revisar, se manda **Draft** — Purview refleja fielmente
      qué está realmente gobernado y qué no.
    - PII → clasificaciones (``entity/bulk/classification``) sobre las
      columnas marcadas ``pii=True`` en el diccionario.

Apagado por defecto. Necesita un service principal propio del usuario
(nunca lo maneja este programa más allá de leer variables de entorno):
``PURVIEW_TENANT_ID``, ``PURVIEW_CLIENT_ID``, ``PURVIEW_CLIENT_SECRET``,
``PURVIEW_ACCOUNT_NAME``. Rol necesario: Data Curator sobre la colección
que vas a usar (ver docs/PURVIEW_COLLIBRA.md para los pasos completos).

Implementado contra la documentación oficial de Microsoft Learn (REST API
de Purview, basada en Apache Atlas 2023-09-01) — endpoints y forma de los
payloads verificados contra esa doc el 2026-07-15. NO se probó contra un
tenant real de Purview (no hay uno disponible en este entorno de
desarrollo): antes de confiar en un push real, usá ``dry_run=True`` para
revisar exactamente qué se mandaría, y probá primero contra una colección
de prueba.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

import pandas as pd

_TIMEOUT = 30
_ENV = ("PURVIEW_TENANT_ID", "PURVIEW_CLIENT_ID", "PURVIEW_CLIENT_SECRET",
        "PURVIEW_ACCOUNT_NAME")
# override completo si tu Purview usa el "nuevo portal" (api.purview-service.microsoft.com)
# en vez del clásico ({account}.purview.azure.com) — ver docs/PURVIEW_COLLIBRA.md
_API_BASE_ENV = "PURVIEW_API_BASE"
_GLOSSARY_NAME = "MV Data Governance"

# heurística de clasificación PII por nombre de columna -> tipo de
# clasificación nativo de Purview (Microsoft Information Protection).
# Si ninguna palabra clave matchea, se usa el genérico MICROSOFT.PERSONAL.NAME.
_PII_CLASSIFICATION_HINTS = (
    (("email", "correo", "mail"), "MICROSOFT.PERSONAL.EMAIL"),
    (("phone", "telefono", "teléfono", "celular"), "MICROSOFT.PERSONAL.IPADDRESS"),
    (("ssn", "social_security"), "MICROSOFT.GOVERNMENT.US.SOCIAL_SECURITY_NUMBER"),
)
_PII_CLASSIFICATION_DEFAULT = "MICROSOFT.PERSONAL.NAME"


def configured() -> bool:
    """¿Hay service principal cargado? (apagado por defecto)."""
    return all(os.environ.get(v) for v in _ENV)


def _account_name() -> str:
    return os.environ["PURVIEW_ACCOUNT_NAME"]


def _api_base() -> str:
    override = os.environ.get(_API_BASE_ENV)
    if override:
        return override.rstrip("/")
    return f"https://{_account_name()}.purview.azure.com"


def _http_json(url: str, headers: dict, method: str = "GET", body: dict | None = None) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        raw = resp.read()
        return json.loads(raw.decode("utf-8")) if raw else {}


def _http_form(url: str, form: dict) -> dict:
    data = urllib.parse.urlencode(form).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_token() -> str:
    """OAuth2 client-credentials contra Azure AD. El resource fijo
    'https://purview.azure.net' es el que documenta Microsoft Learn para
    la API clásica de Purview (no confundir con el scope de Graph/PBI)."""
    tenant = os.environ["PURVIEW_TENANT_ID"]
    url = f"https://login.microsoftonline.com/{tenant}/oauth2/token"
    form = {"client_id": os.environ["PURVIEW_CLIENT_ID"],
            "client_secret": os.environ["PURVIEW_CLIENT_SECRET"],
            "grant_type": "client_credentials",
            "resource": "https://purview.azure.net"}
    return _http_form(url, form)["access_token"]


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _pii_classification(column: str) -> str:
    c = column.lower()
    for keywords, classification in _PII_CLASSIFICATION_HINTS:
        if any(k in c for k in keywords):
            return classification
    return _PII_CLASSIFICATION_DEFAULT


# --------------------------------------------------------------- payloads
def build_entity_payload(catalog: pd.DataFrame, dictionary: pd.DataFrame) -> list[dict]:
    """Arma las entidades rdbms_table/rdbms_column a partir del catálogo y
    el diccionario del programa. No pega a la red — solo arma el payload,
    para poder previsualizarlo (dry-run) sin credenciales."""
    entities = []
    for _, row in catalog.iterrows():
        ds = row["dataset"]
        entities.append({
            "typeName": "rdbms_table",
            "attributes": {
                "qualifiedName": f"mvdg://{ds}",
                "name": ds,
                "description": row.get("description", ""),
                "owner": row.get("steward") or row.get("owner", ""),
            },
            "status": "ACTIVE",
        })
    for _, row in dictionary.iterrows():
        ds, col = row["dataset"], row["column"]
        entities.append({
            "typeName": "rdbms_column",
            "attributes": {
                "qualifiedName": f"mvdg://{ds}#{col}",
                "name": col,
                "description": row.get("description", ""),
                "data_type": row.get("type", ""),
            },
            "status": "ACTIVE",
        })
    return entities


def build_glossary_terms(glossary: pd.DataFrame, curation_lookup=None) -> list[dict]:
    """Arma los términos del glosario. ``curation_lookup(term_id) ->
    (status, text)`` es opcional — si se pasa (normalmente
    ``mvdg.curation``), el estado en Purview refleja la curaduría real:
    Approved si un responsable validó/modificó, Draft si sigue siendo la
    sugerencia de IA sin revisar."""
    terms = []
    for _, row in glossary.iterrows():
        text = row["definition"]
        status = "Draft"
        if curation_lookup is not None:
            cur_status, cur_text = curation_lookup(row["term_id"])
            if cur_status in ("validado", "modificado"):
                status = "Approved"
            if cur_text:
                text = cur_text
        terms.append({
            "name": row["term"],
            "shortDescription": text[:255],
            "longDescription": text,
            "status": status,
        })
    return terms


def build_classification_payload(dictionary: pd.DataFrame, entity_guids: dict[str, str]) -> list[dict]:
    """Arma un pedido de clasificación por cada columna PII, agrupando por
    tipo de clasificación. ``entity_guids`` mapea qualifiedName -> guid
    real (lo devuelve Purview al crear las entidades)."""
    by_classification: dict[str, list[str]] = {}
    for _, row in dictionary[dictionary["pii"] == True].iterrows():  # noqa: E712
        qn = f"mvdg://{row['dataset']}#{row['column']}"
        guid = entity_guids.get(qn)
        if not guid:
            continue
        cls = _pii_classification(row["column"])
        by_classification.setdefault(cls, []).append(guid)
    return [{"classification": {"typeName": cls}, "entityGuids": guids}
            for cls, guids in by_classification.items()]


# ------------------------------------------------------------------ push
def push_catalog(catalog: pd.DataFrame, dictionary: pd.DataFrame,
                 dry_run: bool = True, token: str | None = None) -> dict:
    """Empuja catálogo + diccionario como entidades rdbms_table/rdbms_column.
    Con dry_run=True (default) no pega a la red: devuelve el payload que
    SE mandaría, para previsualizar antes de confiar credenciales reales.
    ``token`` es opcional — si no se pasa, pide uno nuevo (úsalo para
    reusar un mismo token entre varias llamadas, como hace push_all)."""
    payload = {"referredEntities": {}, "entities": build_entity_payload(catalog, dictionary)}
    if dry_run:
        return {"dry_run": True, "payload": payload, "entity_count": len(payload["entities"])}
    if not configured():
        raise RuntimeError("Purview no configurado — faltan variables de entorno.")
    token = token or _get_token()
    url = f"{_api_base()}/catalog/api/atlas/v2/entity/bulk"
    result = _http_json(url, _headers(token), method="POST", body=payload)
    # Atlas devuelve las entidades creadas/actualizadas en mutatedEntities;
    # las mapeamos por qualifiedName para poder clasificar PII después.
    mutated = result.get("mutatedEntities", {}).get("CREATE", []) + \
        result.get("mutatedEntities", {}).get("UPDATE", [])
    guid_by_qn = {m["attributes"]["qualifiedName"]: m["guid"] for m in mutated
                 if "qualifiedName" in m.get("attributes", {})}
    return {"dry_run": False, "response": result, "entity_count": len(payload["entities"]),
            "guid_by_qualified_name": guid_by_qn}


def push_glossary(glossary: pd.DataFrame, curation_lookup=None,
                  dry_run: bool = True, token: str | None = None) -> dict:
    """Crea (si hace falta) el glosario 'MV Data Governance' y empuja un
    término por definición, con el estado Draft/Approved reflejando la
    curaduría real (ver build_glossary_terms)."""
    terms = build_glossary_terms(glossary, curation_lookup)
    if dry_run:
        return {"dry_run": True, "terms": terms, "term_count": len(terms)}
    if not configured():
        raise RuntimeError("Purview no configurado — faltan variables de entorno.")
    token = token or _get_token()
    base = _api_base()
    headers = _headers(token)
    glossaries = _http_json(f"{base}/catalog/api/atlas/v2/glossary", headers)
    existing = next((g for g in glossaries if g.get("name") == _GLOSSARY_NAME), None)
    if existing is None:
        existing = _http_json(f"{base}/catalog/api/atlas/v2/glossary", headers,
                              method="POST", body={"name": _GLOSSARY_NAME,
                                                    "shortDescription": "Glosario gobernado por MV Data Governance"})
    glossary_guid = existing["guid"]
    created = []
    for term in terms:
        body = {**term, "anchor": {"glossaryGuid": glossary_guid}}
        created.append(_http_json(f"{base}/catalog/api/atlas/v2/glossary/term",
                                  headers, method="POST", body=body))
    return {"dry_run": False, "glossary_guid": glossary_guid, "term_count": len(created),
            "created": created}


def push_pii_classifications(dictionary: pd.DataFrame, entity_guids: dict[str, str],
                             dry_run: bool = True, token: str | None = None) -> dict:
    """Aplica clasificaciones de PII sobre las entidades ya creadas
    (necesita entity_guids: qualifiedName -> guid, que devuelve push_catalog)."""
    requests = build_classification_payload(dictionary, entity_guids)
    if dry_run:
        return {"dry_run": True, "requests": requests,
                "classification_count": sum(len(r["entityGuids"]) for r in requests)}
    if not configured():
        raise RuntimeError("Purview no configurado — faltan variables de entorno.")
    token = token or _get_token()
    url = f"{_api_base()}/catalog/api/atlas/v2/entity/bulk/classification"
    responses = [_http_json(url, _headers(token), method="POST", body=r) for r in requests]
    return {"dry_run": False, "requests_sent": len(responses),
            "classification_count": sum(len(r["entityGuids"]) for r in requests)}


def push_all(catalog: pd.DataFrame, dictionary: pd.DataFrame, glossary: pd.DataFrame,
            curation_lookup=None, dry_run: bool = True) -> dict:
    """Orquesta el push completo: catálogo -> glosario -> clasificaciones
    PII (usa los guids reales devueltos por el paso de catálogo). Pide un
    solo token OAuth2 y lo reusa en los 3 pasos, en vez de tres roundtrips
    de autenticación por separado."""
    token = _get_token() if (not dry_run and configured()) else None
    cat_result = push_catalog(catalog, dictionary, dry_run=dry_run, token=token)
    gloss_result = push_glossary(glossary, curation_lookup, dry_run=dry_run, token=token)
    if dry_run:
        # en preview no hay guids reales todavía (recién se crearían en el
        # push real) — usamos el qualifiedName como placeholder para poder
        # mostrar igual cuántas columnas se clasificarían y con qué tipo.
        guid_map = {f"mvdg://{r['dataset']}#{r['column']}": f"mvdg://{r['dataset']}#{r['column']}"
                   for _, r in dictionary.iterrows()}
    else:
        guid_map = cat_result.get("guid_by_qualified_name", {})
    pii_result = push_pii_classifications(dictionary, guid_map, dry_run=dry_run, token=token)
    return {"dry_run": dry_run, "catalog": cat_result, "glossary": gloss_result,
            "pii": pii_result}
