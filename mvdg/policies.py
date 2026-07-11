"""
MV Data Governance · Políticas de datos y cumplimiento automático.

Cada política define una verificación objetiva contra el catálogo o los
resultados de calidad; el estado (cumple / parcial / no cumple) sale de esa
evidencia, no de una casilla marcada a mano.
"""
from __future__ import annotations

import pandas as pd

from .catalog import catalog_df, dictionary_df, pii_columns
from .quality import overall_index, run_rules


def _d(es: str, en: str, pt: str) -> dict:
    return {"es": es, "en": en, "pt": pt}


_POLICIES = [
    {
        "policy_id": "POL-01",
        "name": _d("Todo dataset tiene dueño y steward",
                   "Every dataset has an owner and a steward",
                   "Todo dataset tem dono e steward"),
        "category": _d("Responsabilidad", "Accountability", "Responsabilidade"),
    },
    {
        "policy_id": "POL-02",
        "name": _d("Toda columna está documentada",
                   "Every column is documented",
                   "Toda coluna está documentada"),
        "category": _d("Documentación", "Documentation", "Documentação"),
    },
    {
        "policy_id": "POL-03",
        "name": _d("Datos personales (PII) identificados y clasificados",
                   "Personal data (PII) identified and classified",
                   "Dados pessoais (PII) identificados e classificados"),
        "category": _d("Privacidad", "Privacy", "Privacidade"),
    },
    {
        "policy_id": "POL-04",
        "name": _d("Índice de calidad global ≥ 95",
                   "Overall quality index ≥ 95",
                   "Índice de qualidade global ≥ 95"),
        "category": _d("Calidad", "Quality", "Qualidade"),
    },
    {
        "policy_id": "POL-05",
        "name": _d("Sin reglas de calidad en falla crítica",
                   "No quality rules in critical failure",
                   "Sem regras de qualidade em falha crítica"),
        "category": _d("Calidad", "Quality", "Qualidade"),
    },
    {
        "policy_id": "POL-06",
        "name": _d("Términos de negocio vinculados al catálogo",
                   "Business terms linked to the catalog",
                   "Termos de negócio vinculados ao catálogo"),
        "category": _d("Semántica", "Semantics", "Semântica"),
    },
]


def policies_df(lang: str = "es",
                results: pd.DataFrame | None = None) -> pd.DataFrame:
    """Evalúa cada política y devuelve estado + evidencia en ``lang``."""
    results = results if results is not None else run_rules(lang=lang)
    cat = catalog_df(lang)
    dic = dictionary_df(lang)

    rows = []

    def add(pid: str, status: str, evidence: dict):
        p = next(p for p in _POLICIES if p["policy_id"] == pid)
        rows.append({
            "policy_id": pid,
            "policy": p["name"].get(lang, p["name"]["es"]),
            "category": p["category"].get(lang, p["category"]["es"]),
            "status": status,  # compliant | partial | noncompliant
            "evidence": evidence.get(lang, evidence["es"]),
        })

    # POL-01: dueño y steward en todos los datasets
    missing = cat[(cat["owner"] == "") | (cat["steward"] == "")]
    add("POL-01", "compliant" if missing.empty else "partial", _d(
        f"{len(cat)}/{len(cat)} datasets con dueño y steward asignados.",
        f"{len(cat)}/{len(cat)} datasets with owner and steward assigned.",
        f"{len(cat)}/{len(cat)} datasets com dono e steward atribuídos."))

    # POL-02: columnas documentadas (descripción no vacía)
    undoc = dic[dic["description"].str.strip() == ""]
    add("POL-02", "compliant" if undoc.empty else "partial", _d(
        f"{len(dic) - len(undoc)}/{len(dic)} columnas con descripción.",
        f"{len(dic) - len(undoc)}/{len(dic)} columns with a description.",
        f"{len(dic) - len(undoc)}/{len(dic)} colunas com descrição."))

    # POL-03: PII marcada y dataset clasificado como PII
    pii = pii_columns()
    pii_ds = {ds for ds, _ in pii}
    classified = set(cat[cat["classification"] == "PII"]["dataset"])
    ok = pii_ds <= classified
    add("POL-03", "compliant" if ok else "partial", _d(
        f"{len(pii)} columnas PII marcadas; datasets clasificados: {', '.join(sorted(classified))}.",
        f"{len(pii)} PII columns flagged; classified datasets: {', '.join(sorted(classified))}.",
        f"{len(pii)} colunas PII marcadas; datasets classificados: {', '.join(sorted(classified))}."))

    # POL-04: índice global
    idx = overall_index(results)
    add("POL-04", "compliant" if idx >= 95 else ("partial" if idx >= 90 else "noncompliant"), _d(
        f"Índice de calidad actual: {idx}.",
        f"Current quality index: {idx}.",
        f"Índice de qualidade atual: {idx}."))

    # POL-05: sin fallas críticas
    fails = int((results["status"] == "fail").sum())
    warns = int((results["status"] == "warn").sum())
    add("POL-05", "compliant" if fails == 0 else "noncompliant", _d(
        f"{fails} reglas en falla, {warns} en alerta.",
        f"{fails} rules failing, {warns} in warning.",
        f"{fails} regras em falha, {warns} em alerta."))

    # POL-06: términos vinculados
    linked = dic["business_term"].nunique()
    add("POL-06", "compliant" if linked >= 5 else "partial", _d(
        f"{linked} términos de negocio en uso en el diccionario.",
        f"{linked} business terms in use in the dictionary.",
        f"{linked} termos de negócio em uso no dicionário."))

    return pd.DataFrame(rows)
