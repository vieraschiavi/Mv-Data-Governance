"""
MV Data Governance · Persistencia local de lo traído (pull) desde
Purview/Collibra.

Gap real que tenían ``purview_pull``/``collibra_pull``: traían los términos
y tablas y los mostraban (o los dejaban descargar como CSV), pero no
quedaban guardados en el programa — cerrabas la sesión y había que volver a
traerlos. Este módulo los persiste, igual que ``curation.py`` persiste los
veredictos de un responsable:

    ~/.mv_data_governance/importado.json

Y — más importante que guardar el archivo — lo importado entra al MISMO
circuito de gobierno que todo lo demás: aparece en 🖊️ Curaduría como
cualquier otra definición, con su origen visible ("importado de Purview" /
"importado de Collibra") y su texto pre-establecido (el que trajo la
plataforma externa) esperando que un Data Owner/Steward lo valide o lo
corrija acá. No se inventa una tabla/columna nueva en el catálogo rígido de
demo (``catalog.py``) — eso es un modelo fijo pensado para los 4 datasets
sintéticos — sino que "lo importado" es su propia colección, visible y
exportable, con el mismo tratamiento de responsable que cualquier otro dato
gobernado por este programa.
"""
from __future__ import annotations

import json
import os
from datetime import datetime

import pandas as pd

from .clients import data_dir

SOURCES = ("purview", "collibra")


def _file() -> str:
    return os.path.join(data_dir(), "importado.json")


def _load() -> dict:
    path = _file()
    if not os.path.exists(path):
        return {"terms": {}, "tables": {}}
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            return {"terms": {}, "tables": {}}
        data.setdefault("terms", {})
        data.setdefault("tables", {})
        return data
    except (json.JSONDecodeError, OSError):
        return {"terms": {}, "tables": {}}


def _write(data: dict) -> None:
    tmp = _file() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, _file())


def _key(source: str, external_id: str) -> str:
    return f"{source}:{external_id}"


# -------------------------------------------------------------------- save
def save_terms(source: str, terms: list[dict]) -> int:
    """Guarda (upsert, por id externo) los términos traídos de
    ``purview_pull``/``collibra_pull`` — ``terms`` es la lista tal cual la
    devuelven esos módulos: ``[{"name", "definition", "<fuente>_id"}, ...]``.
    Devuelve cuántos se guardaron/actualizaron."""
    if source not in SOURCES:
        raise ValueError(f"Fuente desconocida: {source}")
    data = _load()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    n = 0
    for term in terms:
        ext_id = term.get(f"{source}_id") or term.get("collibra_id") or term.get("purview_id")
        if not ext_id or not term.get("name"):
            continue
        key = _key(source, ext_id)
        data["terms"][key] = {
            "source": source, "external_id": ext_id,
            "name": term["name"], "definition": term.get("definition", ""),
            "imported_at": now,
        }
        n += 1
    _write(data)
    return n


def save_tables(source: str, tables: list[dict]) -> int:
    """Igual que ``save_terms`` pero para tablas de catálogo."""
    if source not in SOURCES:
        raise ValueError(f"Fuente desconocida: {source}")
    data = _load()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    n = 0
    for tbl in tables:
        ext_id = tbl.get(f"{source}_id") or tbl.get("collibra_id") or tbl.get("purview_id")
        if not ext_id or not tbl.get("name"):
            continue
        key = _key(source, ext_id)
        data["tables"][key] = {
            "source": source, "external_id": ext_id,
            "name": tbl["name"], "description": tbl.get("description", ""),
            "imported_at": now,
        }
        n += 1
    _write(data)
    return n


# -------------------------------------------------------------------- list
def list_terms() -> pd.DataFrame:
    data = _load()
    rows = list(data["terms"].values())
    return pd.DataFrame(rows, columns=["source", "external_id", "name", "definition", "imported_at"])


def list_tables() -> pd.DataFrame:
    data = _load()
    rows = list(data["tables"].values())
    return pd.DataFrame(rows, columns=["source", "external_id", "name", "description", "imported_at"])


def delete_term(source: str, external_id: str) -> bool:
    data = _load()
    key = _key(source, external_id)
    if key not in data["terms"]:
        return False
    del data["terms"][key]
    _write(data)
    return True


def delete_table(source: str, external_id: str) -> bool:
    data = _load()
    key = _key(source, external_id)
    if key not in data["tables"]:
        return False
    del data["tables"][key]
    _write(data)
    return True


# ----------------------------------------------------- items para curaduría
def curation_items(lang: str = "es") -> list[dict]:
    """Items importados en el mismo formato que ``curation._demo_items``/
    ``_sample_items`` — así entran al inventario de 🖊️ Curaduría con su
    origen (Purview/Collibra) visible en vez de quedar aislados en su
    propia pantalla."""
    data = _load()
    items = []
    for key, term in data["terms"].items():
        items.append({
            "item_id": f"glossary:imported:{key}",
            "kind": "glossary",
            "dataset": f"⬇️ {term['source']}",
            "label": term["name"],
            "proposed": term.get("definition", ""),
            "default_owner": "",
        })
    for key, tbl in data["tables"].items():
        items.append({
            "item_id": f"catalog:imported:{key}",
            "kind": "catalog",
            "dataset": f"⬇️ {tbl['source']}",
            "label": tbl["name"],
            "proposed": tbl.get("description", ""),
            "default_owner": "",
        })
    return items
