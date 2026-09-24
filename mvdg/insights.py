# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Insights del estado de gobierno (estilo Purview).

Microsoft Purview llama a esto "Data Estate Insights" y Collibra
"dashboards de stewardship": un tablero que no mide la calidad de los DATOS
sino la salud del GOBIERNO — ¿cuánto del patrimonio de datos tiene dueño con
nombre y apellido? ¿cuánto está clasificado? ¿cuántas definiciones revisó un
responsable de verdad? Acá se calcula igual, 100% local, cruzando lo que ya
existe en el programa:

    catálogo (demo + 4 ejemplos) · reglas de calidad · detección de PII ·
    curaduría (pestaña ) · responsables por organigrama (pestaña )

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


def coverage_for(catalog: pd.DataFrame, results: pd.DataFrame,
                 lang: str = "es") -> pd.DataFrame:
    """La misma tabla de coberturas que ``governance_coverage``, pero sobre
    el catálogo que se le pasa y no sobre el de la demo.

    Es la que usa el programa cuando el usuario cargó sus datos: antes el
    «índice de gobierno» de Panorama se calculaba siempre sobre los datasets
    de la demo, así que el cliente veía un 80 % de dueños asignados que no
    eran suyos. Dueño y steward salen del organigrama (o de Curaduría) si
    están; la clasificación, del catálogo; las reglas, de los resultados.
    """
    from . import curation, orgchart

    asg = orgchart.load_assignments()
    asg_by_ds = (asg.set_index("dataset").to_dict("index")
                 if asg is not None and len(asg) else {})
    cur = curation.list_items(lang)
    con_reglas = set(results["dataset"]) if len(results) else set()
    rows = []
    for d in catalog.to_dict("records"):
        ds = d["dataset"]
        a = asg_by_ds.get(ds, {})
        cur_ds = cur[cur["dataset"] == ds] if len(cur) else cur
        reviewed = ((cur_ds["status"] != "sugerido_ia").mean() * 100
                    if len(cur_ds) else 0.0)
        rows.append({
            "dataset": ds,
            "owner_named": _named(a.get("owner_name")) or _named(d.get("owner")),
            "steward_named": (_named(a.get("steward_name"))
                              or _named(d.get("steward"))),
            "classified": d.get("classification") not in (None, "", "Sin clasificar"),
            "has_rules": ds in con_reglas,
            "curation_pct": round(reviewed, 1),
        })
    return pd.DataFrame(rows, columns=["dataset", "owner_named", "steward_named",
                                       "classified", "has_rules", "curation_pct"])


def summary_of(df: pd.DataFrame) -> dict:
    """El resumen de una tabla de coberturas, sea de la demo o del usuario.
    Sin datasets devuelve ceros en vez de dividir por cero."""
    n = len(df)

    def pct(col: str) -> float:
        return round(100.0 * int(df[col].sum()) / n, 1) if n else 0.0

    owner_pct, steward_pct = pct("owner_named"), pct("steward_named")
    class_pct, rules_pct = pct("classified"), pct("has_rules")
    curation_pct = round(float(df["curation_pct"].mean()), 1) if n else 0.0
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


def governance_summary(lang: str = "es") -> dict:
    """Resumen ejecutivo de la demo: % de cada cobertura + índice (0-100)."""
    return summary_of(governance_coverage(lang))
