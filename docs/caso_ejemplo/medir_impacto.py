"""
MV Data Governance · Medición reproducible del impacto (caso de ejemplo).

Compara la calidad de una cartera de datos "ANTES" del proyecto de gobierno
(datos degradados, como llegan sin gobernanza) contra "DESPUÉS" (los datos
trabajados de la demo). Todo se computa con el mismo motor de reglas del
programa: los números del caso de la web salen de acá, no están inventados.

Ejecutar desde la raíz del repo:
    python docs/caso_ejemplo/medir_impacto.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from mvdg.demo_data import load_demo_tables  # noqa: E402
from mvdg.quality import (open_issues, overall_index,  # noqa: E402
                          quality_by_dimension, run_rules)


def _degradar(tables: dict) -> dict:
    """Reproduce el estado 'sin gobierno': muchos nulos, duplicados,
    formatos inválidos, FKs huérfanas y dominios inconsistentes."""
    rng = np.random.default_rng(2024)
    before = {k: v.copy() for k, v in tables.items()}

    c = before["dim_customers"]
    i = rng.choice(len(c), int(len(c) * 0.45), replace=False)
    c.loc[i[: len(i) // 2], "email"] = None
    c.loc[i[len(i) // 2 : int(len(i) * 0.8)], "email"] = "correo_sin_arroba"
    c.loc[i[int(len(i) * 0.8) :], "segment"] = "RETAIL"
    before["dim_customers"] = pd.concat(
        [c, c.sample(int(len(c) * 0.15), random_state=1)], ignore_index=True)

    s = before["fct_sales"]
    j = rng.choice(len(s), int(len(s) * 0.30), replace=False)
    s.loc[j[: len(j) // 3], "amount"] = None
    s.loc[j[len(j) // 3 : int(len(j) * 0.6)], "amount"] = \
        -abs(s.loc[j[len(j) // 3 : int(len(j) * 0.6)], "amount"].fillna(80))
    s.loc[j[int(len(j) * 0.6) : int(len(j) * 0.8)], "customer_id"] = 99999
    s.loc[j[int(len(j) * 0.8) :], "channel"] = "WEB"

    p = before["dim_products"]
    k = rng.choice(len(p), int(len(p) * 0.35), replace=False)
    p.loc[k[: len(k) // 2], "unit_price"] = -abs(p.loc[k[: len(k) // 2], "unit_price"])
    p.loc[k[len(k) // 2 :], "category"] = None

    pay = before["fct_payments"]
    m = rng.choice(len(pay), int(len(pay) * 0.20), replace=False)
    pay.loc[m[: len(m) // 2], "method"] = None
    pay.loc[m[len(m) // 2 :], "status"] = "?"

    return before


def medir() -> dict:
    after = load_demo_tables()
    before = _degradar(after)
    rb, ra = run_rules(before), run_rules(after)

    def resumen(res):
        return {
            "indice": overall_index(res),
            "reglas_ok": int((res.status == "pass").sum()),
            "reglas_total": len(res),
            "fallas": int((res.status == "fail").sum()),
            "alertas": int((res.status == "warn").sum()),
            "filas_afectadas": int(res.affected_rows.sum()),
            "por_dimension": quality_by_dimension(res)
            .set_index("dimension")["quality_index"].round(1).to_dict(),
        }

    antes, despues = resumen(rb), resumen(ra)
    return {
        "antes": antes,
        "despues": despues,
        "mejora_indice": round(despues["indice"] - antes["indice"], 1),
        "reduccion_filas_pct": round(
            100 * (antes["filas_afectadas"] - despues["filas_afectadas"])
            / max(1, antes["filas_afectadas"])),
    }


if __name__ == "__main__":
    r = medir()
    print(json.dumps(r, indent=2, ensure_ascii=False))
    print(f"\nÍndice: {r['antes']['indice']} → {r['despues']['indice']} "
          f"(+{r['mejora_indice']} pts)")
    print(f"Reglas OK: {r['antes']['reglas_ok']}/{r['antes']['reglas_total']} → "
          f"{r['despues']['reglas_ok']}/{r['despues']['reglas_total']}")
    print(f"Fallas: {r['antes']['fallas']} → {r['despues']['fallas']}")
    print(f"Filas problemáticas: {r['antes']['filas_afectadas']} → "
          f"{r['despues']['filas_afectadas']} (−{r['reduccion_filas_pct']}%)")
