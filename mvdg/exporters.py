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


def governance_tables(lang: str = "es") -> dict[str, pd.DataFrame]:
    """Todas las tablas de gobierno, listas para exportar o servir por API."""
    results = run_rules(lang=lang)
    kpis = pd.DataFrame([{
        "kpi": "quality_index", "value": overall_index(results)},
        {"kpi": "rules_total", "value": len(results)},
        {"kpi": "rules_pass", "value": int((results["status"] == "pass").sum())},
        {"kpi": "rules_warn", "value": int((results["status"] == "warn").sum())},
        {"kpi": "rules_fail", "value": int((results["status"] == "fail").sum())},
    ])
    return {
        "catalog": catalog_df(lang),
        "dictionary": dictionary_df(lang),
        "quality_results": results,
        "quality_by_dataset": quality_by_dataset(results),
        "quality_by_dimension": quality_by_dimension(results),
        "lineage": lineage_df(),
        "glossary": glossary_df(lang),
        "policies": policies_df(lang, results),
        "kpis": kpis,
    }


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def to_json_bytes(df: pd.DataFrame) -> bytes:
    return json.dumps(df.to_dict(orient="records"),
                      ensure_ascii=False, indent=2, default=str).encode("utf-8")


def to_excel_bytes(df: pd.DataFrame, sheet: str = "data") -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as xw:
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
    with pd.ExcelWriter(buf, engine="xlsxwriter") as xw:
        for name, df in governance_tables(lang).items():
            df.to_excel(xw, sheet_name=name[:31], index=False)
    return buf.getvalue()
