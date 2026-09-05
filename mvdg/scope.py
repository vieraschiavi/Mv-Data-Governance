# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Alcance combinado: demo + casos de ejemplo de Mis datos.

El pedido que origina esto: los 4 casos reales/externos de Mis datos
(Rotulado de alimentos, Dirty Cafe Sales, Bank Marketing, openFDA) estaban
gobernados de punta a punta *dentro de su pestaña* — pero el resto del
programa (Panorama, Catálogo, Calidad, Linaje, Glosario,
Políticas, BI & API) seguía mostrando SOLO los 4 datasets sintéticos
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

Todo es opt-in del dashboard vía el toggle "Incluir casos de Mis datos"
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
    return _lineage_to_df(nodes, edges)


# ─────────────────────────────────────────────────────────────────────────
# Tercera fuente: los datasets que carga el propio usuario
# ─────────────────────────────────────────────────────────────────────────
# El problema que cierra: el usuario subía su Excel/CSV o lo traía de SQL en
# "Mis datos", lo veía perfilado ahí… y el resto del programa seguía
# mostrando solo la demo. Catálogo, Calidad, Linaje, Glosario, Políticas y
# BI & API no se enteraban de que existía. Para alguien evaluando el
# producto con sus propios datos, eso lo vuelve una demo bonita en vez de
# una herramienta.
#
# Las funciones de abajo toman ``{nombre: DataFrame}`` — plano, sin
# Streamlit — y producen exactamente las mismas columnas que la demo y que
# los casos de ejemplo, para que aguas arriba nadie tenga que saber de
# dónde vino cada fila.
#
# Honestidad del alcance, igual que con los casos de ejemplo:
#   - Catálogo, diccionario y reglas de calidad son REALES: las reglas se
#     generan del archivo (``auto_rules``) y se CORREN contra los datos.
#   - El dueño/steward salen vacíos a propósito: el programa no los puede
#     adivinar, y ponerle "N/D" a un campo de gobierno es peor que dejarlo
#     para que alguien lo complete en Curaduría.
#   - El linaje es el honesto de un archivo cargado a mano: origen → dataset
#     → BI. No se inventan capas raw/mart que no existen.

# Prefijo de los ids de linaje, para no chocar con un dataset de demo que se
# llame igual que el archivo del usuario.
_USER_SRC = "user_src_"


def _items(user_datasets) -> list[tuple[str, "pd.DataFrame"]]:
    """Normaliza la entrada y descarta lo vacío.

    Un dict vacío, None, o un DataFrame sin filas tienen que comportarse
    igual: como si el usuario no hubiera cargado nada.
    """
    if not user_datasets:
        return []
    return [(str(n), df) for n, df in user_datasets.items()
            if df is not None and len(df)]


def user_catalog(user_datasets, lang: str = "es",
                 columnas=None) -> pd.DataFrame:
    """Una fila de catálogo por dataset cargado, con las columnas de la demo."""
    from .i18n import t
    from .profiler import summary
    filas = []
    for nombre, df in _items(user_datasets):
        info = summary(df)
        filas.append({
            "dataset": nombre,
            "domain": t("scope_user_domain", lang),
            "description": t("scope_user_desc", lang).format(
                filas=info["rows"], columnas=info["columns"]),
            # Dueño y steward vacíos: son decisiones de la organización, no
            # datos del archivo. Curaduría los completa.
            "owner": "", "steward": "",
            # Literal, NO traducido: `classification` es un token que el
            # motor compara (policies.py busca exactamente "PII" para
            # verificar que un dataset con columnas personales esté
            # clasificado). Traducirlo lo rompía en silencio: el dataset
            # aparecía con PII en el diccionario y la política de
            # clasificación seguía diciendo que estaba todo bien.
            "classification": "PII" if info["pii_columns"] else "Sin clasificar",
            "source": t("scope_user_source", lang),
            "refresh": t("scope_user_refresh", lang),
            "rows": info["rows"], "columns": info["columns"],
            "last_updated": TODAY.date().isoformat(),
        })
    if not filas:
        return pd.DataFrame(columns=list(columnas) if columnas is not None else None)
    out = pd.DataFrame(filas)
    return out[list(columnas)] if columnas is not None else out


def user_dictionary(user_datasets, lang: str = "es") -> pd.DataFrame:
    """Diccionario de datos de lo cargado: una fila por columna, con PII."""
    from .i18n import t
    from .profiler import profile_table
    partes = []
    for nombre, df in _items(user_datasets):
        perfil = profile_table(df)
        partes.append(pd.DataFrame({
            "dataset": nombre,
            "column": perfil["column"],
            "type": perfil["dtype"],
            "pii": perfil["possible_pii"],
            "business_term": "",
            "description": perfil.apply(
                lambda r: t("scope_user_col_desc", lang).format(
                    nulos=r["null_pct"], distintos=r["unique_values"]), axis=1),
        }))
    if not partes:
        return pd.DataFrame(columns=["dataset", "column", "type", "pii",
                                     "business_term", "description"])
    return pd.concat(partes, ignore_index=True)


def user_results(user_datasets, lang: str = "es") -> pd.DataFrame:
    """Reglas de calidad generadas del archivo y CORRIDAS contra los datos."""
    from .auto_rules import auto_quality_results
    partes = [auto_quality_results(df, nombre, lang)
              for nombre, df in _items(user_datasets)]
    partes = [p for p in partes if not p.empty]
    if not partes:
        return pd.DataFrame(columns=["rule_id", "dataset", "column", "dimension",
                                     "description", "score", "threshold",
                                     "status", "affected_rows"])
    return pd.concat(partes, ignore_index=True)


def user_lineage(user_datasets, lang: str = "es",
                 nodes=None, edges=None) -> tuple[list[dict], list[tuple[str, str]]]:
    """Suma al grafo el linaje honesto de un archivo cargado: origen → dataset → BI."""
    from .i18n import t
    nodos = [dict(n) for n in (nodes if nodes is not None else NODES)]
    aristas = list(edges if edges is not None else EDGES)
    for nombre, _df in _items(user_datasets):
        src = f"{_USER_SRC}{nombre}"
        nodos.append({"id": src, "label": t("scope_user_source", lang), "layer": "source"})
        nodos.append({"id": nombre, "label": nombre, "layer": "curated"})
        aristas.append((src, nombre))
        aristas.append((nombre, "bi_dashboard"))
    return nodos, aristas


def lineage_to_df(nodes, edges) -> pd.DataFrame:
    """Un grafo ya armado, como tabla plana. Público a propósito: la UI
    dibuja y tabula el MISMO grafo, en vez de calcularlo dos veces y
    arriesgarse a que el dibujo y la tabla no coincidan."""
    return _lineage_to_df(nodes, edges)


def _lineage_to_df(nodes, edges) -> pd.DataFrame:
    by_id = {n["id"]: n for n in nodes}
    return pd.DataFrame([{
        "source_id": a, "source": by_id[a]["label"],
        "source_layer": by_id[a]["layer"],
        "target_id": b, "target": by_id[b]["label"],
        "target_layer": by_id[b]["layer"],
    } for a, b in edges])
