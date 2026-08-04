"""
MV Data Governance · Informe de auditoría del archivo propio (Excel).

Por qué existe este módulo
--------------------------
El recorrido comercial clave era: el consultor sube SU archivo, ve el
catálogo de calidad en pantalla… y ahí terminaba. Todo lo que veía quedaba
atrapado en el navegador — la pestaña 📦 Entregable solo arma informes para
los 4 casos de ejemplo del repo, no para el archivo del usuario. Este módulo
cierra ese circuito: un Excel profesional, trilingüe, que el consultor puede
mandarle a SU cliente el mismo día de la demo.

Qué contiene el informe (4 hojas)
---------------------------------
1. Resumen ejecutivo — KPIs del archivo: filas, columnas, duplicados,
   % nulos, índice de calidad, reglas aprobadas y columnas con posible PII.
2. Perfil por columna — tipo, % nulos, valores únicos, muestra y marca PII.
3. Reglas de calidad — las reglas auto-generadas CORRIDAS contra los datos,
   con puntaje, umbral y estado. Los mismos números que muestra la pantalla:
   ambos salen de ``auto_quality_results``, no hay una segunda fuente.
4. Plan de corrección — por cada regla en warn/fail: causa probable, arreglo
   de corto plazo, prevención y a quién asignarlo (``remediation``).

Igual que el resto del motor, esto no levanta Streamlit ni toca la red:
entra un DataFrame, sale ``bytes`` de un .xlsx.
"""
from __future__ import annotations

import io

import pandas as pd

from .auto_rules import auto_quality_results
from .i18n import t
from .profiler import profile_table, summary
from .quality import overall_index
from .remediation import suggest_fix

# Paleta de la marca (la misma del dashboard y la landing).
_AZUL_OSCURO = "#081527"
_AMBAR = "#f2b441"
_ROJO = "#c0392b"
_NARANJA = "#e67e22"
_VERDE = "#1e8449"

_DIMENSIONES = ["completeness", "uniqueness", "validity", "consistency",
                "timeliness", "accuracy"]


def _labels(lang: str) -> tuple[dict, dict]:
    dim = {d: t(f"dim_{d}", lang) for d in _DIMENSIONES}
    est = {"pass": t("q_pass", lang), "warn": t("q_warn", lang),
           "fail": t("q_fail", lang)}
    return dim, est


def file_report_tables(df: pd.DataFrame, dataset_name: str,
                       lang: str = "es") -> dict:
    """Las tablas del informe, como DataFrames — la única fuente de números.

    Separado de la escritura del .xlsx a propósito: los tests auditan estas
    tablas contra el motor directamente, y el Excel solo las serializa. Así
    "lo que dice el informe" y "lo que dice la pantalla" no pueden divergir.
    """
    info = summary(df)
    ares = auto_quality_results(df, dataset_name, lang)
    dim_label, est_label = _labels(lang)
    # summary() trae el CONTEO de columnas PII; para un informe sirven los
    # NOMBRES (el cliente quiere saber cuáles, no cuántas).
    crudo = profile_table(df)
    pii_nombres = crudo.loc[crudo["possible_pii"], "column"].tolist()

    resumen = pd.DataFrame([
        (t("col_dataset", lang), dataset_name),
        (t("col_rows", lang), int(info["rows"])),
        (t("col_columns_count", lang), int(info["columns"])),
        (t("pr_dupes", lang), int(info["duplicate_rows"])),
        (t("pr_nulls", lang), f"{info['null_cells_pct']}%"),
        (t("kpi_quality", lang),
         f"{overall_index(ares)} / 100" if len(ares) else "—"),
        (t("kpi_rules_pass", lang),
         f"{int((ares['status'] == 'pass').sum())} / {len(ares)}"
         if len(ares) else "0 / 0"),
        (t("frep_pii_cols", lang), ", ".join(pii_nombres) or "—"),
    ], columns=[t("frep_field", lang), t("frep_value", lang)])

    perfil = crudo.rename(columns={
        "column": t("col_column", lang), "dtype": t("col_type", lang),
        "null_pct": t("pr_nulls", lang), "unique_values": t("pr_unique", lang),
        "possible_pii": t("col_pii", lang),
    })

    calidad = ares.copy()
    if len(calidad):
        calidad["dimension"] = calidad["dimension"].map(
            lambda d: dim_label.get(d, d))
        calidad["status"] = calidad["status"].map(
            lambda s: est_label.get(s, s))
    calidad = calidad.rename(columns={
        "rule_id": "ID", "dataset": t("col_dataset", lang),
        "column": t("col_column", lang), "dimension": t("q_dimension", lang),
        "description": t("q_rule", lang), "score": t("q_score", lang),
        "threshold": t("q_threshold", lang), "status": t("q_status", lang),
        "affected_rows": t("q_affected", lang),
    })

    rotas = ares[ares["status"] != "pass"]
    plan = pd.DataFrame([
        {"ID": r["rule_id"],
         t("col_column", lang): r["column"],
         t("q_rule", lang): r["description"],
         t("fix_root", lang): fix["root_cause"],
         t("fix_short", lang): fix["short_term"],
         t("fix_long", lang): fix["long_term"],
         t("fix_owner", lang): fix["owner"]}
        for _, r in rotas.iterrows()
        for fix in [suggest_fix(r["rule_id"], r["dimension"], r["column"],
                                int(r["affected_rows"]), lang)]
    ])

    return {"summary": resumen, "profile": perfil,
            "quality": calidad, "fixes": plan, "_results": ares}


def file_report_xlsx(df: pd.DataFrame, dataset_name: str,
                     lang: str = "es") -> bytes:
    """El informe listo para descargar: 4 hojas con formato profesional."""
    tablas = file_report_tables(df, dataset_name, lang)
    hojas = [
        (t("frep_sheet_summary", lang)[:31], tablas["summary"]),
        (t("frep_sheet_profile", lang)[:31], tablas["profile"]),
        (t("frep_sheet_quality", lang)[:31], tablas["quality"]),
        (t("frep_sheet_fixes", lang)[:31], tablas["fixes"]),
    ]
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter",
                        engine_kwargs={"options": {"in_memory": True}}) as xw:
        libro = xw.book
        f_encabezado = libro.add_format({
            "bold": True, "font_color": "white", "bg_color": _AZUL_OSCURO,
            "border": 1, "text_wrap": True, "valign": "top"})
        f_estado = {
            t("q_pass", lang): libro.add_format({"font_color": _VERDE, "bold": True}),
            t("q_warn", lang): libro.add_format({"font_color": _NARANJA, "bold": True}),
            t("q_fail", lang): libro.add_format({"font_color": _ROJO, "bold": True}),
        }
        f_titulo = libro.add_format({"bold": True, "font_size": 14,
                                     "font_color": _AZUL_OSCURO})
        f_pie = libro.add_format({"italic": True, "font_color": "#666666"})

        for nombre, tabla in hojas:
            # a partir de la fila 2: la 0 es el título, la 1 queda de aire
            tabla.to_excel(xw, sheet_name=nombre, index=False, startrow=2)
            hoja = xw.sheets[nombre]
            hoja.write(0, 0, f"{t('app_title', lang)} — {dataset_name}", f_titulo)
            for j, col in enumerate(tabla.columns):
                hoja.write(2, j, str(col), f_encabezado)
                ancho = max([len(str(col))] +
                            [len(str(v)) for v in tabla[col].head(200)] or [10])
                hoja.set_column(j, j, min(max(ancho + 2, 10), 60))
            # estado de cada regla con color (solo la hoja de calidad lo tiene)
            col_estado = (list(tabla.columns).index(t("q_status", lang))
                          if t("q_status", lang) in tabla.columns else None)
            if col_estado is not None:
                for i, valor in enumerate(tabla[t("q_status", lang)]):
                    fmt = f_estado.get(str(valor))
                    if fmt is not None:
                        hoja.write(3 + i, col_estado, str(valor), fmt)
            hoja.write(len(tabla) + 4, 0, t("frep_generated", lang), f_pie)
            hoja.freeze_panes(3, 0)
    return buf.getvalue()
