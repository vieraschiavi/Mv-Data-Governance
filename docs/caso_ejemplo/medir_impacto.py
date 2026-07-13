"""
MV Data Governance · Medición reproducible del impacto (caso de ejemplo).

Compara la calidad de una cartera de datos "ANTES" del proyecto de gobierno
(datos degradados, como llegan sin gobernanza) contra "DESPUÉS" (los datos
trabajados de la demo). Todo se computa con el mismo motor de reglas del
programa: los números del caso de la web salen de acá, no están inventados.

La degradación y el resumen viven en ``mvdg.lab_case`` (compartido con el
tab "Laboratorio" del dashboard) para no duplicar la lógica.

Ejecutar desde la raíz del repo:
    python docs/caso_ejemplo/medir_impacto.py
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from mvdg.lab_case import lab_measure  # noqa: E402


def medir() -> dict:
    m = lab_measure()
    antes, despues = m["summary_before"], m["summary_after"]
    return {
        "antes": antes,
        "despues": despues,
        "mejora_indice": m["mejora_indice"],
        "reduccion_filas_pct": m["reduccion_filas_pct"],
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
