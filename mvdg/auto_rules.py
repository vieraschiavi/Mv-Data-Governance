"""
MV Data Governance · Catálogo de calidad automático para datos propios.

Convierte cualquier CSV/Excel que suba un usuario en reglas de calidad REALES
(evaluadas contra los datos, con puntaje y estado) en vez de solo texto
sugerido. Es la diferencia entre "perfilado" (mvdg/profiler.py) y "catálogo
de calidad": acá cada regla corre y devuelve pass/warn/fail, igual que las
del motor de demo (mvdg/quality.py).

Deliberadamente conservador: solo genera reglas de completitud (no-nulos) y
unicidad (columna que parece clave + filas duplicadas), que son inferibles
de cualquier tabla sin conocer el dominio. Validez, consistencia,
puntualidad y exactitud dependen de reglas de negocio que el motor no puede
adivinar — no se fingen. Ver ``run_checks`` en mvdg/selfcheck.py para el
mismo criterio aplicado a otras heurísticas del programa.
"""
from __future__ import annotations

import pandas as pd

from .quality import Rule, _not_null, _unique, evaluate_rules


def _d(es: str, en: str, pt: str) -> dict:
    return {"es": es, "en": en, "pt": pt}


def _no_duplicate_rows():
    """Filas 100% idénticas en TODAS las columnas — no solo una clave."""
    def check(df: pd.DataFrame):
        n = len(df)
        bad = int(df.duplicated().sum())
        return (100.0 * (n - bad) / n if n else 100.0, bad)
    return check


def build_rules(df: pd.DataFrame, dataset_name: str, lang: str = "es") -> list[Rule]:
    """Reglas de completitud y unicidad generadas a partir del propio archivo.

    Mismas heurísticas que ``profiler.suggest_rules`` (nulos parciales,
    columnas con pinta de clave), pero convertidas en ``Rule`` ejecutables en
    vez de texto: se corren de verdad contra ``df`` con ``evaluate_rules``."""
    rules: list[Rule] = []
    n = len(df)
    if not n:
        return rules

    # IDs secuenciales (no el nombre del archivo): un filename con espacios,
    # puntos o caracteres raros no tiene por qué ser un rule_id válido, y un
    # contador nunca colisiona ni se trunca.
    contador = 0

    def _id() -> str:
        nonlocal contador
        contador += 1
        return f"AUTO-{contador:02d}"

    for col in df.columns:
        col = str(col)
        s = df[col]
        null_pct = 100.0 * s.isna().sum() / n

        # Completitud: solo si hay nulos Y no está prácticamente vacía (una
        # columna con 90% nulos no es "casi completa fallando", es una
        # columna que probablemente no aplica a este dataset).
        if 0 < null_pct <= 50:
            rules.append(Rule(
                _id(), dataset_name, col, "completeness",
                _d(f"«{col}» debería estar siempre completo",
                   f"“{col}” should always be filled in",
                   f"«{col}» deveria estar sempre preenchido"),
                _not_null(col), threshold=95.0))

        # Unicidad: sin nulos y todos los valores distintos = pinta de clave.
        if n > 1 and null_pct == 0 and s.nunique(dropna=True) == n:
            rules.append(Rule(
                _id(), dataset_name, col, "uniqueness",
                _d(f"«{col}» parece una clave — no debería repetirse",
                   f"“{col}” looks like a key — it should not repeat",
                   f"«{col}» parece uma chave — não deveria se repetir"),
                _unique(col), threshold=100.0))

    # Regla de tabla completa (no de una columna): el nombre de columna es
    # solo para mostrar en la UI, "column" no puede quedar vacío ni apuntar
    # a una columna real — eso haría pensar que ESA columna es el problema
    # cuando en realidad es la fila entera repetida.
    columna_tabla = _d("(fila completa)", "(entire row)", "(linha completa)")
    rules.append(Rule(
        _id(), dataset_name, columna_tabla.get(lang, columna_tabla["es"]),
        "uniqueness",
        _d("No debería haber filas 100% duplicadas",
           "There should be no 100% duplicate rows",
           "Não deveria haver linhas 100% duplicadas"),
        _no_duplicate_rows(), threshold=98.0))

    return rules


def auto_quality_results(df: pd.DataFrame, dataset_name: str,
                         lang: str = "es") -> pd.DataFrame:
    """Corre las reglas auto-generadas y devuelve el DataFrame de resultados
    — mismo formato que ``quality.run_rules``, listo para ``overall_index``,
    ``quality_by_dimension`` y ``_render_fixes`` en la UI."""
    rules = build_rules(df, dataset_name, lang)
    if not rules:
        return pd.DataFrame(columns=["rule_id", "dataset", "column", "dimension",
                                     "description", "score", "threshold",
                                     "status", "affected_rows"])
    return evaluate_rules(rules, {dataset_name: df}, lang)
