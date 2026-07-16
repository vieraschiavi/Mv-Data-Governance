"""
MV Data Governance · Curaduría: validación de definiciones por los responsables.

El principio (el mismo que usan Purview y Collibra en sus workflows de
stewardship): **nada arranca en blanco, y nada queda sin responsable**.

- Toda definición del programa (términos del glosario, descripciones de
  datasets del catálogo, descripciones de columnas del diccionario) viene
  **pre-establecida** — es la recomendación inicial generada con IA al
  construir el producto, lista para usarse tal cual.
- Pero una definición no es oficial porque la sugirió una IA: es oficial
  cuando **el Data Owner o Data Steward la valida** (tal cual) o **la
  modifica** con su propio texto. Este módulo guarda ese veredicto en disco,
  con nombre, cargo, fecha y notas del responsable.

Estados de cada definición:
    sugerido_ia  → la pre-establecida, nadie la revisó todavía (implícito)
    validado     → un responsable la aprobó tal cual
    modificado   → un responsable la reemplazó por su propio texto

Persistencia local (igual que conexiones y fichas de empresas):
    ~/.mv_data_governance/curaduria.json
"""
from __future__ import annotations

import json
import os
from datetime import datetime

import pandas as pd

from .clients import data_dir

STATUSES = ("sugerido_ia", "validado", "modificado")


def _file() -> str:
    return os.path.join(data_dir(), "curaduria.json")


# ------------------------------------------------------------- persistencia
def load_records() -> dict:
    """Registros de curaduría por item_id. {item_id: {lang: registro}}"""
    path = _file()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _write(records: dict) -> None:
    tmp = _file() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, _file())


def save_validation(item_id: str, lang: str, status: str, text: str,
                    responsible_name: str, responsible_role: str,
                    notes: str = "") -> dict:
    """Guarda el veredicto del responsable sobre una definición.

    ``status`` debe ser "validado" o "modificado" (el estado "sugerido_ia"
    no se guarda: es el implícito de todo lo no revisado)."""
    if status not in ("validado", "modificado"):
        raise ValueError(f"Estado inválido: {status}")
    if not responsible_name.strip():
        raise ValueError("Falta el nombre del responsable.")
    record = {
        "status": status,
        "text": text.strip() if status == "modificado" else "",
        "responsible_name": responsible_name.strip(),
        "responsible_role": responsible_role.strip(),
        "notes": notes.strip(),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    records = load_records()
    records.setdefault(item_id, {})[lang] = record
    _write(records)
    return record


def reset_item(item_id: str, lang: str | None = None) -> bool:
    """Vuelve una definición al estado pre-establecido (sugerido_ia)."""
    records = load_records()
    if item_id not in records:
        return False
    if lang is None:
        del records[item_id]
    else:
        records[item_id].pop(lang, None)
        if not records[item_id]:
            del records[item_id]
    _write(records)
    return True


def get_record(item_id: str, lang: str) -> dict | None:
    return load_records().get(item_id, {}).get(lang)


# ------------------------------------------------------ inventario de items
def _demo_items(lang: str) -> list[dict]:
    from .catalog import _COLUMNS, _DATASETS
    from .glossary import _TERMS
    items = []
    for t in _TERMS:
        items.append({
            "item_id": f"glossary:demo:{t['term_id']}",
            "kind": "glossary",
            "dataset": ", ".join(t["datasets"]),
            "label": t["name"].get(lang, t["name"]["es"]),
            "proposed": t["definition"].get(lang, t["definition"]["es"]),
            "default_owner": t["owner"],
        })
    for d in _DATASETS:
        items.append({
            "item_id": f"catalog:demo:{d['dataset']}",
            "kind": "catalog",
            "dataset": d["dataset"],
            "label": d["dataset"],
            "proposed": d["description"].get(lang, d["description"]["es"]),
            "default_owner": f"{d['owner']} / {d['steward']}",
        })
    for ds, cols in _COLUMNS.items():
        for c in cols:
            items.append({
                "item_id": f"column:{ds}:{c['column']}",
                "kind": "column",
                "dataset": ds,
                "label": c["column"],
                "proposed": c["d"].get(lang, c["d"]["es"]),
                "default_owner": "",
            })
    return items


def _sample_items(lang: str) -> list[dict]:
    from . import samples
    items = []
    for key, s in samples.SAMPLES.items():
        items.append({
            "item_id": f"catalog:{key}:{key}",
            "kind": "catalog",
            "dataset": key,
            "label": s["name"].get(lang, s["name"]["es"]),
            "proposed": s["description"].get(lang, s["description"]["es"]),
            "default_owner": s["steward"].get(lang, s["steward"]["es"]),
        })
        for t in s["terms"]:
            items.append({
                "item_id": f"glossary:{key}:{t['term_id']}",
                "kind": "glossary",
                "dataset": key,
                "label": t["name"].get(lang, t["name"]["es"]),
                "proposed": t["definition"].get(lang, t["definition"]["es"]),
                "default_owner": t["owner"],
            })
        for c in s["columns"]:
            items.append({
                "item_id": f"column:{key}:{c['column']}",
                "kind": "column",
                "dataset": key,
                "label": c["column"],
                "proposed": c["d"].get(lang, c["d"]["es"]),
                "default_owner": "",
            })
    return items


def _imported_items(lang: str) -> list[dict]:
    """Lo traído (pull) de Purview/Collibra y guardado localmente — ver
    ``mvdg.imported``. Entra al mismo inventario de curaduría que todo lo
    demás: nada que se importa queda sin responsable acá tampoco."""
    from . import imported
    return imported.curation_items(lang)


def list_items(lang: str = "es") -> pd.DataFrame:
    """Inventario completo de definiciones curables, con su estado actual,
    el texto vigente (pre-establecido u oficial del responsable) y quién
    lo validó/modificó."""
    records = load_records()
    rows = []
    for it in _demo_items(lang) + _sample_items(lang) + _imported_items(lang):
        rec = records.get(it["item_id"], {}).get(lang)
        status = rec["status"] if rec else "sugerido_ia"
        effective = (rec["text"] if rec and rec["status"] == "modificado"
                     and rec.get("text") else it["proposed"])
        rows.append({
            "item_id": it["item_id"], "kind": it["kind"],
            "dataset": it["dataset"], "label": it["label"],
            "status": status, "text": effective,
            "proposed": it["proposed"],
            "responsible_name": rec["responsible_name"] if rec else "",
            "responsible_role": rec["responsible_role"] if rec else "",
            "validated_at": rec["date"] if rec else "",
            "notes": rec["notes"] if rec else "",
            "default_owner": it["default_owner"],
        })
    return pd.DataFrame(rows)


def effective_text(item_id: str, lang: str, fallback: str) -> str:
    """Texto vigente de una definición: el del responsable si la modificó,
    el pre-establecido si no."""
    rec = get_record(item_id, lang)
    if rec and rec["status"] == "modificado" and rec.get("text"):
        return rec["text"]
    return fallback


def summary(lang: str = "es") -> dict:
    """Métricas del avance de curaduría: cuántas definiciones hay en cada
    estado y % de revisadas por un responsable."""
    df = list_items(lang)
    total = len(df)
    counts = df["status"].value_counts().to_dict()
    reviewed = counts.get("validado", 0) + counts.get("modificado", 0)
    return {
        "total": total,
        "sugerido_ia": counts.get("sugerido_ia", 0),
        "validado": counts.get("validado", 0),
        "modificado": counts.get("modificado", 0),
        "reviewed_pct": round(100.0 * reviewed / total, 1) if total else 0.0,
    }
