"""
MV Data Governance · Conector inverso (pull) desde Collibra.

Complemento de ``collibra_export.py`` (que empuja de acá hacia Collibra):
este módulo **trae** lo que ya está gobernado en Collibra hacia este
programa — para no volver a tipear a mano un glosario o un catálogo que
la empresa ya armó ahí. Mismo principio de acelerador que el resto de
esta capa: no reemplaza a Collibra como fuente de verdad, solo evita
duplicar trabajo ya hecho.

Alcance verificado (y por qué es más chico de lo que se podría pedir):
esto trae **assets (Tabla) y Business Terms, con su atributo de
Definición** — verificado contra la documentación pública del Collibra
Developer Portal (2026-07-16): `GET /rest/2.0/assets` (filtrable por
domainId/typeIds, paginado con el sobre estándar
`{total, offset, limit, results}`) y `GET /rest/2.0/attributes`
(filtrable por assetId).

**Lo que NO trae, a propósito**: las asignaciones de Owner/Steward
(el recurso "Responsibility" de Collibra). Existe una API para eso, pero
no encontré su forma exacta de request/response documentada públicamente
con suficiente detalle como para implementarla sin adivinar — y adivinar
un endpoint es exactamente lo que este proyecto se propuso no hacer nunca.
Si necesitás esto, la Swagger UI de tu propia instancia
(`https://tu-instancia.collibra.com/rest/2.0/ui`) tiene la especificación
exacta de tu versión — es la vía correcta para completar esto con
confianza, no adivinando desde afuera.

Apagado por defecto. Mismas variables que ``collibra_export.py``:
``COLLIBRA_BASE_URL``, ``COLLIBRA_USERNAME``, ``COLLIBRA_PASSWORD``,
``COLLIBRA_DOMAIN_ID``, ``COLLIBRA_TABLE_TYPE_ID``,
``COLLIBRA_TERM_TYPE_ID`` (mismo default de fábrica que el push).

Nota de diseño: las llamadas HTTP/sesión se hacen SIEMPRE a través del
módulo ``collibra_export`` (``_cb.func(...)``, nunca ``from ... import
func``) para que ambos conectores compartan un único punto donde
parchear el transporte (tests, o un futuro cliente HTTP distinto) — si se
importaran los nombres sueltos, quedarían congelados en el momento del
import y un parche sobre ``collibra_export`` no se vería reflejado acá.
"""
from __future__ import annotations

import os

from . import collibra_export as _cb

_PAGE_LIMIT = 200


def table_pull_configured() -> bool:
    return _cb.configured() and bool(os.environ.get("COLLIBRA_TABLE_TYPE_ID"))


def _list_assets(type_id: str, domain_id: str, cookie: str) -> list[dict]:
    assets, offset = [], 0
    while True:
        url = (f"{_cb._base_url()}/rest/2.0/assets?domainId={domain_id}&typeIds={type_id}"
              f"&offset={offset}&limit={_PAGE_LIMIT}")
        data = _cb._http_json(url, _cb._headers(cookie))[0]
        results = data.get("results", [])
        assets.extend(results)
        offset += len(results)
        if not results or offset >= data.get("total", offset):
            break
    return assets


def _get_definition(asset_id: str, cookie: str) -> str:
    url = (f"{_cb._base_url()}/rest/2.0/attributes?assetId={asset_id}"
          f"&typeIds={_cb.DEFINITION_ATTRIBUTE_TYPE_ID}")
    data = _cb._http_json(url, _cb._headers(cookie))[0]
    results = data.get("results", [])
    return results[0]["value"] if results else ""


def pull_glossary(dry_run: bool = True) -> dict:
    """Trae los Business Term del dominio configurado, con su Definición.

    A diferencia del push (donde dry_run arma el payload SIN red y sin
    credenciales), acá ``dry_run`` no puede tener ese significado: para
    saber qué hay en Collibra hace falta consultarlo sí o sí. Lo que
    ``dry_run=True`` (default) garantiza es que esta función SOLO lee — el
    llamador decide después si guarda algo en el programa (glosario/
    catálogo local) con esos datos, o si era solo para mirar. Siempre
    requiere credenciales configuradas."""
    if not _cb.configured():
        raise RuntimeError("Collibra no configurado — faltan variables de entorno.")
    domain_id = os.environ["COLLIBRA_DOMAIN_ID"]
    term_type_id = os.environ.get("COLLIBRA_TERM_TYPE_ID") or _cb._DEFAULT_TERM_TYPE_ID
    cookie = _cb._sign_in()
    try:
        assets = _list_assets(term_type_id, domain_id, cookie)
        terms = []
        for a in assets:
            definition = _get_definition(a["id"], cookie)
            terms.append({"collibra_id": a["id"], "name": a["name"], "definition": definition})
    finally:
        _cb._sign_out(cookie)
    return {"dry_run": dry_run, "term_count": len(terms), "terms": terms}


def pull_catalog(dry_run: bool = True) -> dict:
    """Trae los assets de tipo Tabla del dominio configurado, con su
    Definición — para precargar 📚 Catálogo sin tipear de nuevo lo que
    Collibra ya tiene documentado."""
    if not table_pull_configured():
        raise RuntimeError("Collibra no configurado para catálogo — falta "
                           "COLLIBRA_TABLE_TYPE_ID.")
    domain_id = os.environ["COLLIBRA_DOMAIN_ID"]
    table_type_id = os.environ["COLLIBRA_TABLE_TYPE_ID"]
    cookie = _cb._sign_in()
    try:
        assets = _list_assets(table_type_id, domain_id, cookie)
        tables = []
        for a in assets:
            definition = _get_definition(a["id"], cookie)
            tables.append({"collibra_id": a["id"], "name": a["name"], "description": definition})
    finally:
        _cb._sign_out(cookie)
    return {"dry_run": dry_run, "table_count": len(tables), "tables": tables}


def pull_all(dry_run: bool = True) -> dict:
    glossary = pull_glossary(dry_run=dry_run)
    catalog = pull_catalog(dry_run=dry_run) if table_pull_configured() else \
        {"dry_run": dry_run, "table_count": 0, "tables": [],
         "skipped_reason": "falta COLLIBRA_TABLE_TYPE_ID"}
    return {"dry_run": dry_run, "glossary": glossary, "catalog": catalog}
