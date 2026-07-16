"""
MV Data Governance · Conector inverso (pull) desde Microsoft Purview.

Complemento de ``purview_export.py`` (que empuja de acá hacia Purview): este
módulo **trae** lo que ya está gobernado en Purview hacia este programa —
mismo principio de acelerador que el resto de esta capa, y el mismo gap que
tenía ``collibra_pull`` antes de existir este módulo: sin esto, la migración
Purview era de ida solamente.

Alcance verificado (2026-07-16, Microsoft Learn):
    - Glosario: ``GET /catalog/api/atlas/v2/glossary`` para encontrar el
      glosario "MV Data Governance" (mismo que crea ``purview_export``) y
      ``GET /catalog/api/atlas/v2/glossary/{glossaryGuid}/terms`` para
      listar sus términos — endpoint confirmado contra la referencia REST
      de Purview (datamapdataplane/glossary/list-terms).
    - Catálogo: ``POST /datamap/api/search/query`` (Discovery Query) para
      encontrar entidades ``rdbms_table`` ya registradas. Nota importante:
      esta es una raíz DISTINTA (``/datamap/api/...``) a la que usa el
      resto del módulo (``/catalog/api/atlas/v2/...``, que sigue
      funcionando para entity/bulk y glossary) — la búsqueda/discovery
      clásica bajo ``/catalog/api/...`` ya no está documentada por
      Microsoft como un endpoint propio (su página de referencia
      redirige a la de ``/datamap/...``), así que para ESTO puntualmente
      se usa la ruta vigente. El envoltorio de respuesta también es
      distinto al de Atlas: ``{"value": [...], "continuationToken": ...}``
      con paginación por cursor (``continuationToken``), no offset/limit.

Apagado por defecto. Mismas variables que ``purview_export.py``:
``PURVIEW_TENANT_ID``, ``PURVIEW_CLIENT_ID``, ``PURVIEW_CLIENT_SECRET``,
``PURVIEW_ACCOUNT_NAME``.

Nota de diseño: las llamadas HTTP/token se hacen SIEMPRE a través del
módulo ``purview_export`` (``_pv.func(...)``, nunca ``from ... import
func``) — mismo motivo que ``collibra_pull``: importar los nombres sueltos
los congela en el momento del import y un parche sobre ``purview_export``
(tests, o un futuro cliente HTTP distinto) no se vería reflejado acá.
"""
from __future__ import annotations

from . import purview_export as _pv

_SEARCH_API_VERSION = "2023-09-01"
_MAX_PAGES = 20


def configured() -> bool:
    return _pv.configured()


def pull_glossary(dry_run: bool = True) -> dict:
    """Trae los términos del glosario "MV Data Governance" en Purview, con
    su definición.

    Igual que en ``collibra_pull``: ``dry_run`` no puede significar "sin
    red" acá (para saber qué hay en Purview hace falta consultarlo sí o
    sí). Lo que garantiza ``dry_run=True`` (default) es que esta función
    SOLO lee — el llamador decide después si guarda algo en el programa con
    esos datos. Siempre requiere credenciales configuradas."""
    if not _pv.configured():
        raise RuntimeError("Purview no configurado — faltan variables de entorno.")
    token = _pv._get_token()
    base = _pv._api_base()
    headers = _pv._headers(token)
    glossaries = _pv._http_json(f"{base}/catalog/api/atlas/v2/glossary", headers)
    existing = next((g for g in glossaries if g.get("name") == _pv._GLOSSARY_NAME), None)
    if existing is None:
        return {"dry_run": dry_run, "term_count": 0, "terms": []}
    listed = _pv._http_json(
        f"{base}/catalog/api/atlas/v2/glossary/{existing['guid']}/terms", headers)
    terms = []
    for t in listed:
        if not isinstance(t, dict) or not t.get("guid") or not t.get("name"):
            continue
        terms.append({
            "purview_id": t["guid"], "name": t["name"],
            "definition": t.get("longDescription") or t.get("shortDescription") or "",
        })
    return {"dry_run": dry_run, "term_count": len(terms), "terms": terms}


def pull_catalog(dry_run: bool = True) -> dict:
    """Trae las tablas (entidades ``rdbms_table``) ya registradas en
    Purview, vía la API de Discovery vigente hoy (ver docstring del
    módulo sobre por qué esto usa ``/datamap/...`` y no ``/catalog/...``).
    Pagina con ``continuationToken`` hasta agotar resultados o llegar a
    ``_MAX_PAGES`` (tope de seguridad, no un catálogo sin fin real)."""
    if not _pv.configured():
        raise RuntimeError("Purview no configurado — faltan variables de entorno.")
    token = _pv._get_token()
    base = _pv._api_base()
    headers = _pv._headers(token)
    url = f"{base}/datamap/api/search/query?api-version={_SEARCH_API_VERSION}"
    tables, continuation, pages = [], None, 0
    while pages < _MAX_PAGES:
        body = {"filter": {"entityType": "rdbms_table"}, "limit": 100}
        if continuation:
            body["continuationToken"] = continuation
        data = _pv._http_json(url, headers, method="POST", body=body)
        for item in data.get("value", []):
            if item.get("id") and item.get("name"):
                tables.append({
                    "purview_id": item["id"], "name": item["name"],
                    "description": item.get("description", ""),
                })
        continuation = data.get("continuationToken")
        pages += 1
        if not continuation:
            break
    return {"dry_run": dry_run, "table_count": len(tables), "tables": tables}


def pull_all(dry_run: bool = True) -> dict:
    return {"dry_run": dry_run, "glossary": pull_glossary(dry_run=dry_run),
            "catalog": pull_catalog(dry_run=dry_run)}
