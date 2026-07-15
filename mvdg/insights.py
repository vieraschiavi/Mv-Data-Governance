"""
MV Data Governance · Insights del estado de gobierno (estilo Purview).

Microsoft Purview llama a esto "Data Estate Insights" y Collibra
"dashboards de stewardship": un tablero que no mide la calidad de los DATOS
sino la salud del GOBIERNO — ¿cuánto del patrimonio de datos tiene dueño con
nombre y apellido? ¿cuánto está clasificado? ¿cuántas definiciones revisó un
responsable de verdad? Acá se calcula igual, 100% local, cruzando lo que ya
existe en el programa:

    catálogo (demo + 4 ejemplos) · reglas de calidad · detección de PII ·
    curaduría (pestaña 🖊️) · responsables por organigrama (pestaña 👥)

El resultado es una tabla por dataset + un resumen con el "índice de
gobierno" (0-100): el promedio de cinco coberturas — responsable nombrado,
steward nombrado, clasificación, reglas de calidad y curaduría de
definiciones. Complementa al índice de CALIDAD del Panorama: uno mide los
datos, el otro mide el gobierno sobre esos datos.
"""
from __future__ import annotations

import pandas as pd


def _named(value: str) -> bool:
    """Un responsable "con nombre" es una persona, no un equipo genérico:
    heurística simple — contiene un espacio y no empieza con palabras de
    equipo (Gerencia/Equipo/Team/...)."""
    v = str(value or "").strip()
    if not v:
        return False
    team_words = ("gerencia", "equipo", "team", "equipe", "área", "area",
                  "departamento", "department", "dirección", "direcao")
    return not any(v.lower().startswith(w) for w in team_words)


def governance_coverage(lang: str = "es") -> pd.DataFrame:
    """Tabla por dataset con las 5 coberturas de gobierno (booleans/%)."""
    from . import curation, orgchart, samples
    from .catalog import _DATASETS
    from .quality import RULES

    asg = orgchart.load_assignments()
    asg_by_ds = (asg.set_index("dataset").to_dict("index")
                 if asg is not None and len(asg) else {})
    cur = curation.list_items(lang)
    rules_demo = {r.dataset for r in RULES}

    rows = []
    # datasets de demo
    for d in _DATASETS:
        ds = d["dataset"]
        a = asg_by_ds.get(ds, {})
        cur_ds = cur[cur["dataset"].str.contains(ds, regex=False)]
        reviewed = (cur_ds["status"] != "sugerido_ia").mean() * 100 if len(cur_ds) else 0.0
        rows.append({
            "dataset": ds,
            "owner_named": _named(a.get("owner_name")) or _named(d["steward"]),
            "steward_named": _named(a.get("steward_name")) or _named(d["steward"]),
            "classified": bool(d["classification"]),
            "has_rules": ds in rules_demo,
            "curation_pct": round(reviewed, 1),
        })
    # datasets de ejemplo
    for key, s in samples.SAMPLES.items():
        a = asg_by_ds.get(key, {})
        cur_ds = cur[cur["dataset"] == key]
        reviewed = (cur_ds["status"] != "sugerido_ia").mean() * 100 if len(cur_ds) else 0.0
        rows.append({
            "dataset": key,
            "owner_named": _named(a.get("owner_name")),
            "steward_named": _named(a.get("steward_name")),
            "classified": bool(s["classification"]),
            "has_rules": bool(s["rules"]),
            "curation_pct": round(reviewed, 1),
        })
    return pd.DataFrame(rows)


def governance_summary(lang: str = "es") -> dict:
    """Resumen ejecutivo: % de cada cobertura + índice de gobierno (0-100)."""
    df = governance_coverage(lang)
    n = len(df)
    owner_pct = round(100.0 * int(df["owner_named"].sum()) / n, 1)
    steward_pct = round(100.0 * int(df["steward_named"].sum()) / n, 1)
    class_pct = round(100.0 * int(df["classified"].sum()) / n, 1)
    rules_pct = round(100.0 * int(df["has_rules"].sum()) / n, 1)
    curation_pct = round(float(df["curation_pct"].mean()), 1)
    index = round((owner_pct + steward_pct + class_pct + rules_pct + curation_pct) / 5, 1)
    return {
        "datasets": n,
        "owner_pct": owner_pct,
        "steward_pct": steward_pct,
        "classified_pct": class_pct,
        "rules_pct": rules_pct,
        "curation_pct": curation_pct,
        "governance_index": index,
    }
