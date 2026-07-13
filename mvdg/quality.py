"""
MV Data Governance · Motor de reglas de calidad de datos.

Seis dimensiones estándar (DAMA): completitud, unicidad, validez,
consistencia, puntualidad y exactitud. Cada regla se evalúa contra los
datos reales y devuelve un puntaje 0–100, el estado (pass/warn/fail según
umbral) y cuántas filas quedaron afectadas.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

from .demo_data import TODAY, load_demo_tables

DIMENSIONS = ["completeness", "uniqueness", "validity",
              "consistency", "timeliness", "accuracy"]

_EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.]+$")


@dataclass(frozen=True)
class Rule:
    rule_id: str
    dataset: str
    column: str
    dimension: str            # una de DIMENSIONS
    description: dict         # {"es":…, "en":…, "pt":…}
    check: Callable[[pd.DataFrame], tuple[float, int]]  # -> (score 0-100, filas afectadas)
    threshold: float = 95.0   # score mínimo para "pass"; warn si >= threshold-5


def _not_null(col: str):
    def check(df: pd.DataFrame):
        n = len(df)
        bad = int(df[col].isna().sum())
        return (100.0 * (n - bad) / n if n else 100.0, bad)
    return check


def _unique(col: str):
    def check(df: pd.DataFrame):
        n = len(df)
        bad = int(df.duplicated(subset=[col]).sum())
        return (100.0 * (n - bad) / n if n else 100.0, bad)
    return check


def _regex(col: str, pattern: re.Pattern):
    def check(df: pd.DataFrame):
        s = df[col].dropna().astype(str)
        n = len(df)
        bad = int((~s.str.match(pattern)).sum()) + int(df[col].isna().sum())
        return (100.0 * (n - bad) / n if n else 100.0, bad)
    return check


def _positive(col: str):
    def check(df: pd.DataFrame):
        n = len(df)
        s = pd.to_numeric(df[col], errors="coerce")
        bad = int((s.isna() | (s <= 0)).sum())
        return (100.0 * (n - bad) / n if n else 100.0, bad)
    return check


def _in_set(col: str, allowed: set[str]):
    def check(df: pd.DataFrame):
        n = len(df)
        bad = int((~df[col].isin(allowed)).sum())
        return (100.0 * (n - bad) / n if n else 100.0, bad)
    return check


def _max_age(col: str, max_days: int):
    def check(df: pd.DataFrame):
        n = len(df)
        age = (TODAY - pd.to_datetime(df[col], errors="coerce")).dt.days
        bad = int((age.isna() | (age > max_days)).sum())
        return (100.0 * (n - bad) / n if n else 100.0, bad)
    return check


def _fk(col: str, ref_table: str, ref_col: str):
    def check(df: pd.DataFrame, _ref=(ref_table, ref_col)):
        tables = load_demo_tables()
        valid = set(tables[_ref[0]][_ref[1]])
        n = len(df)
        bad = int((~df[col].isin(valid)).sum())
        return (100.0 * (n - bad) / n if n else 100.0, bad)
    return check


def _d(es: str, en: str, pt: str) -> dict:
    return {"es": es, "en": en, "pt": pt}


RULES: list[Rule] = [
    # ------------------------------------------------------- dim_customers
    Rule("CUS-01", "dim_customers", "customer_id", "uniqueness",
         _d("customer_id debe ser único", "customer_id must be unique", "customer_id deve ser único"),
         _unique("customer_id"), 99.5),
    Rule("CUS-02", "dim_customers", "email", "completeness",
         _d("email no puede ser nulo", "email must not be null", "email não pode ser nulo"),
         _not_null("email"), 98.0),
    Rule("CUS-03", "dim_customers", "email", "validity",
         _d("email con formato válido", "email must have a valid format", "email com formato válido"),
         _regex("email", _EMAIL_RE), 99.5),
    Rule("CUS-04", "dim_customers", "segment", "consistency",
         _d("segment dentro del dominio permitido", "segment within allowed domain", "segment dentro do domínio permitido"),
         _in_set("segment", {"Retail", "Corporate", "SMB"}), 99.0),
    # -------------------------------------------------------- dim_products
    Rule("PRD-01", "dim_products", "product_id", "uniqueness",
         _d("product_id debe ser único", "product_id must be unique", "product_id deve ser único"),
         _unique("product_id"), 100.0),
    Rule("PRD-02", "dim_products", "unit_price", "accuracy",
         _d("unit_price debe ser positivo", "unit_price must be positive", "unit_price deve ser positivo"),
         _positive("unit_price"), 99.9),
    Rule("PRD-03", "dim_products", "category", "completeness",
         _d("category no puede ser nula", "category must not be null", "category não pode ser nula"),
         _not_null("category"), 98.0),
    # ----------------------------------------------------------- fct_sales
    Rule("SAL-01", "fct_sales", "sale_id", "uniqueness",
         _d("sale_id debe ser único", "sale_id must be unique", "sale_id deve ser único"),
         _unique("sale_id"), 100.0),
    Rule("SAL-02", "fct_sales", "amount", "completeness",
         _d("amount no puede ser nulo", "amount must not be null", "amount não pode ser nulo"),
         _not_null("amount"), 99.0),
    Rule("SAL-03", "fct_sales", "amount", "accuracy",
         _d("amount debe ser positivo", "amount must be positive", "amount deve ser positivo"),
         _positive("amount"), 98.0),
    Rule("SAL-04", "fct_sales", "customer_id", "consistency",
         _d("customer_id existe en dim_customers (FK)", "customer_id exists in dim_customers (FK)", "customer_id existe em dim_customers (FK)"),
         _fk("customer_id", "dim_customers", "customer_id"), 99.5),
    Rule("SAL-05", "fct_sales", "channel", "consistency",
         _d("channel dentro del dominio permitido", "channel within allowed domain", "channel dentro do domínio permitido"),
         _in_set("channel", {"web", "tienda", "app", "mayorista"}), 99.0),
    Rule("SAL-06", "fct_sales", "sale_date", "timeliness",
         _d("ventas con antigüedad ≤ 400 días", "sales no older than 400 days", "vendas com idade ≤ 400 dias"),
         _max_age("sale_date", 400), 99.0),
    # -------------------------------------------------------- fct_payments
    Rule("PAY-01", "fct_payments", "payment_id", "uniqueness",
         _d("payment_id debe ser único", "payment_id must be unique", "payment_id deve ser único"),
         _unique("payment_id"), 100.0),
    Rule("PAY-02", "fct_payments", "method", "completeness",
         _d("method no puede ser nulo", "method must not be null", "method não pode ser nulo"),
         _not_null("method"), 98.5),
    Rule("PAY-03", "fct_payments", "payment_date", "timeliness",
         _d("pagos con antigüedad ≤ 730 días", "payments no older than 730 days", "pagamentos com idade ≤ 730 dias"),
         _max_age("payment_date", 730), 99.0),
    Rule("PAY-04", "fct_payments", "status", "validity",
         _d("status dentro del dominio permitido", "status within allowed domain", "status dentro do domínio permitido"),
         _in_set("status", {"ok", "pendiente", "rechazado"}), 99.5),
]


def evaluate_rules(rules: list[Rule], tables: dict[str, pd.DataFrame],
                   lang: str = "es") -> pd.DataFrame:
    """Corre una lista de reglas cualquiera contra un dict de tablas y
    devuelve el DataFrame de resultados (score, umbral, estado, filas
    afectadas). Reutilizado por ``run_rules`` (las 4 tablas de demo) y por
    ``mvdg.samples`` (datasets de ejemplo externos)."""
    rows = []
    for r in rules:
        df = tables[r.dataset]
        score, affected = r.check(df)
        score = round(float(score), 2)
        if score >= r.threshold:
            status = "pass"
        elif score >= r.threshold - 2:
            status = "warn"
        else:
            status = "fail"
        rows.append({
            "rule_id": r.rule_id,
            "dataset": r.dataset,
            "column": r.column,
            "dimension": r.dimension,
            "description": r.description.get(lang, r.description["es"]),
            "score": score,
            "threshold": r.threshold,
            "status": status,
            "affected_rows": affected,
        })
    return pd.DataFrame(rows)


def run_rules(tables: dict[str, pd.DataFrame] | None = None,
              lang: str = "es") -> pd.DataFrame:
    """Ejecuta las 17 reglas de los datasets de demo y devuelve los resultados."""
    tables = tables or load_demo_tables()
    return evaluate_rules(RULES, tables, lang)


def quality_by_dataset(results: pd.DataFrame) -> pd.DataFrame:
    """Índice de calidad promedio por dataset."""
    return (results.groupby("dataset", as_index=False)["score"]
            .mean().round(2).rename(columns={"score": "quality_index"}))


def quality_by_dimension(results: pd.DataFrame) -> pd.DataFrame:
    """Índice de calidad promedio por dimensión."""
    return (results.groupby("dimension", as_index=False)["score"]
            .mean().round(2).rename(columns={"score": "quality_index"}))


def quality_matrix(results: pd.DataFrame) -> pd.DataFrame:
    """Matriz dataset × dimensión (para heatmap)."""
    return results.pivot_table(index="dataset", columns="dimension",
                               values="score", aggfunc="mean").round(2)


def overall_index(results: pd.DataFrame) -> float:
    return round(float(results["score"].mean()), 2)


def quality_trend(results: pd.DataFrame, months: int = 12) -> pd.DataFrame:
    """Serie mensual sintética que converge al índice actual (para el gráfico
    de evolución de la demo; con datos reales se persiste cada corrida)."""
    current = overall_index(results)
    rng = np.random.default_rng(7)
    base = max(60.0, current - 14)
    steps = np.linspace(base, current, months) + rng.normal(0, 0.7, months)
    steps[-1] = current
    idx = pd.period_range(end=TODAY.to_period("M"), periods=months, freq="M")
    return pd.DataFrame({"month": idx.astype(str),
                         "quality_index": np.round(np.clip(steps, 0, 100), 2)})


def open_issues(results: pd.DataFrame) -> pd.DataFrame:
    """Incidencias abiertas derivadas de reglas en warn/fail."""
    sev = {"warn": "media", "fail": "alta"}
    issues = results[results["status"] != "pass"].copy()
    issues["severity"] = issues["status"].map(sev)
    return issues[["rule_id", "dataset", "column", "dimension",
                   "severity", "score", "affected_rows"]].reset_index(drop=True)
