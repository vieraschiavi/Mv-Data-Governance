"""
MV Data Governance · Alcance combinado: demo + casos de ejemplo de 🔎 Mis datos.

El pedido que origina esto: los 4 casos reales/externos de 🔎 Mis datos
(Rotulado de alimentos, Dirty Cafe Sales, Bank Marketing, openFDA) estaban
gobernados de punta a punta *dentro de su pestaña* — pero el resto del
programa (📊 Panorama, 📚 Catálogo, ✅ Calidad, 🧬 Linaje, 📖 Glosario,
🛡️ Políticas, 📤 BI & API) seguía mostrando SOLO los 4 datasets sintéticos
de demo. Este módulo arma el universo combinado para que esos casos fluyan
por todas las pestañas y el recorrido end-to-end sea completo.

Qué se simula y qué no (honestidad del alcance):
    - Catálogo, diccionario, reglas de calidad y glosario de cada caso son
      REALES (viven en ``mvdg.samples``, con datos y reglas que corren de
      verdad sobre los archivos).
    - El linaje de los casos es el honesto de un archivo: fuente (openFDA /
      Kaggle / UCI / acta oficial) → dataset curado → BI. No hay capas
      raw/mart reales para un CSV — no se inventan.
    - ``last_updated`` de los casos usa la fecha de hoy (igual criterio que
      la demo).

Todo es opt-in del dashboard vía el toggle "🧩 Incluir casos de Mis datos"
del sidebar — las funciones de demo originales quedan intactas (los tests
y la API por dataset no cambian de significado).
"""
from __future__ import annotations

import pandas as pd

from . import samples
from .catalog import catalog_df, dictionary_df
from .demo_data import TODAY
from .glossary import glossary_df
from .lineage import EDGES, NODES


def combined_catalog(lang: str = "es", tables=None) -> pd.DataFrame:
    """Catálogo demo + una fila por caso de ejemplo (mismas columnas)."""
    cat = catalog_df(lang, tables)
    rows = []
    for key in samples.sample_keys():
        row = samples.sample_catalog_row(key, lang)
        row["last_updated"] = TODAY.date().isoformat()
        rows.append(row)
    return pd.concat([cat, pd.DataFrame(rows)[list(cat.columns)]],
                     ignore_index=True)


def combined_dictionary(lang: str = "es", dataset: str | None = None) -> pd.DataFrame:
    """Diccionario demo + columnas de cada caso (con su columna ``dataset``)."""
    parts = [dictionary_df(lang)]
    for key in samples.sample_keys():
        d = samples.sample_dictionary_df(key, lang).copy()
        d.insert(0, "dataset", key)
        parts.append(d)
    out = pd.concat(parts, ignore_index=True)
    if dataset:
        out = out[out["dataset"] == dataset].reset_index(drop=True)
    return out


def combined_results(lang: str = "es",
                     demo_results: pd.DataFrame | None = None) -> pd.DataFrame:
    """Resultados de calidad demo + los de las reglas reales de cada caso.

    ``demo_results`` es opcional para reusar el resultado ya cacheado por el
    dashboard (correr las 17 reglas de demo de nuevo sería gratis pero
    innecesario)."""
    from .quality import run_rules
    parts = [demo_results if demo_results is not None else run_rules(lang=lang)]
    parts += [samples.sample_quality_results(key, lang)
              for key in samples.sample_keys()]
    return pd.concat(parts, ignore_index=True)


def combined_glossary(lang: str = "es") -> pd.DataFrame:
    parts = [glossary_df(lang)]
    parts += [samples.sample_glossary_df(key, lang)
              for key in samples.sample_keys()]
    return pd.concat(parts, ignore_index=True)


def combined_lineage(lang: str = "es") -> tuple[list[dict], list[tuple[str, str]]]:
    """Grafo de linaje demo + el linaje honesto de cada caso de ejemplo:
    fuente externa → dataset curado → el mismo dashboard de BI de la demo.
    (Un CSV no tiene capas raw/mart reales — no se inventan.)"""
    nodes = [dict(n) for n in NODES]
    edges = list(EDGES)
    for key in samples.sample_keys():
        meta = samples.sample_meta(key, lang)
        src_id = f"src_{key}"
        nodes.append({"id": src_id, "label": meta["source"], "layer": "source"})
        nodes.append({"id": key, "label": key, "layer": "curated"})
        edges.append((src_id, key))
        edges.append((key, "bi_dashboard"))
    return nodes, edges


def combined_lineage_df(lang: str = "es") -> pd.DataFrame:
    """El mismo grafo combinado como tabla plana (exportable a BI)."""
    nodes, edges = combined_lineage(lang)
    by_id = {n["id"]: n for n in nodes}
    return pd.DataFrame([{
        "source_id": a, "source": by_id[a]["label"],
        "source_layer": by_id[a]["layer"],
        "target_id": b, "target": by_id[b]["label"],
        "target_layer": by_id[b]["layer"],
    } for a, b in edges])
