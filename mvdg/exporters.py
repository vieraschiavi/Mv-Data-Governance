# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Exportadores compatibles con cualquier BI.

Formatos: CSV, Excel (una tabla o paquete multi-hoja), JSON y Parquet
(si pyarrow está disponible). Los mismos DataFrames que sirve la API REST.
"""
from __future__ import annotations

import io
import json

import pandas as pd

from .catalog import catalog_df, dictionary_df
from .glossary import glossary_df
from .lineage import lineage_df
from .policies import policies_df
from .quality import (overall_index, quality_by_dataset,
                      quality_by_dimension, run_rules)


def scope_lineage_df(grafo) -> pd.DataFrame:
    """Aplana un grafo ``(nodos, aristas)`` a la tabla de linaje."""
    from . import scope
    return scope.lineage_to_df(*grafo)


def governance_tables(lang: str = "es",
                      include_samples: bool = False,
                      user_datasets: dict | None = None) -> dict[str, pd.DataFrame]:
    """Todas las tablas de gobierno, listas para exportar o servir por API.

    Con ``include_samples=True`` el universo es el combinado demo + casos de
    ejemplo de Mis datos (ver ``mvdg.scope``) — mismo esquema de tablas,
    más filas. El default sigue siendo solo la demo (compatibilidad con la
    API y los tests existentes).

    ``user_datasets`` (``{nombre: DataFrame}``) suma lo que cargó el propio
    usuario. Es lo que hace que el Excel que subió termine en el bundle de
    Power BI y en la API, y no solo en la pestaña donde lo cargó — que era
    justamente el agujero: el cliente exportaba a BI y se llevaba la demo.
    """
    # El grafo de linaje se lleva aparte del DataFrame porque sumarle los
    # datasets del usuario se hace sobre NODOS y ARISTAS, no sobre la tabla
    # ya aplanada. Aplanarlo antes de tiempo hacía que el linaje del usuario
    # reemplazara al de los casos de ejemplo en vez de sumarse.
    grafo = None
    if include_samples:
        from . import scope
        results = scope.combined_results(lang)
        catalog = scope.combined_catalog(lang)
        dictionary = scope.combined_dictionary(lang)
        grafo = scope.combined_lineage(lang)
        glossary = scope.combined_glossary(lang)
    else:
        results = run_rules(lang=lang)
        catalog = catalog_df(lang)
        dictionary = dictionary_df(lang)
        glossary = glossary_df(lang)
    lineage = scope_lineage_df(grafo) if grafo else lineage_df()

    if user_datasets:
        from . import scope
        nodos, aristas = scope.user_lineage(
            user_datasets, lang,
            nodes=grafo[0] if grafo else None, edges=grafo[1] if grafo else None)
        results = pd.concat([results, scope.user_results(user_datasets, lang)],
                            ignore_index=True)
        catalog = pd.concat(
            [catalog, scope.user_catalog(user_datasets, lang, columnas=catalog.columns)],
            ignore_index=True)
        dictionary = pd.concat([dictionary, scope.user_dictionary(user_datasets, lang)],
                               ignore_index=True)
        lineage = scope.lineage_to_df(nodos, aristas)

    # Las políticas se derivan del catálogo y del diccionario finales: si se
    # calcularan antes de sumar lo del usuario, sus columnas con PII no
    # dispararían ninguna política.
    policies = (policies_df(lang, results, catalog=catalog, dictionary=dictionary)
                if (include_samples or user_datasets) else policies_df(lang, results))
    kpis = pd.DataFrame([{
        "kpi": "quality_index", "value": overall_index(results)},
        {"kpi": "rules_total", "value": len(results)},
        {"kpi": "rules_pass", "value": int((results["status"] == "pass").sum())},
        {"kpi": "rules_warn", "value": int((results["status"] == "warn").sum())},
        {"kpi": "rules_fail", "value": int((results["status"] == "fail").sum())},
    ])
    return {
        "catalog": catalog,
        "dictionary": dictionary,
        "quality_results": results,
        "quality_by_dataset": quality_by_dataset(results),
        "quality_by_dimension": quality_by_dimension(results),
        "lineage": lineage,
        "glossary": glossary,
        "policies": policies,
        "kpis": kpis,
    }


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def to_json_bytes(df: pd.DataFrame) -> bytes:
    return json.dumps(df.to_dict(orient="records"),
                      ensure_ascii=False, indent=2, default=str).encode("utf-8")


def to_excel_bytes(df: pd.DataFrame, sheet: str = "data") -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter",
                       engine_kwargs={"options": {"in_memory": True}}) as xw:
        df.to_excel(xw, sheet_name=sheet[:31], index=False)
    return buf.getvalue()


def to_parquet_bytes(df: pd.DataFrame) -> bytes | None:
    """Parquet si hay motor disponible; ``None`` si no lo hay."""
    try:
        buf = io.BytesIO()
        df.to_parquet(buf, index=False)
        return buf.getvalue()
    except ImportError:
        return None


def bi_bundle_xlsx(lang: str = "es") -> bytes:
    """Excel multi-hoja con todo el paquete de gobierno (para cualquier BI)."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter",
                       engine_kwargs={"options": {"in_memory": True}}) as xw:
        for name, df in governance_tables(lang).items():
            df.to_excel(xw, sheet_name=name[:31], index=False)
    return buf.getvalue()
