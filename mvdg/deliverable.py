"""
MV Data Governance · 📦 Entregable final por caso de ejemplo.

El pedido que origina esto: "mostrame una pestaña de entregable final de
cada uno de los demos luego de terminar el trabajo de gobernanza de datos"
— el laboratorio (medicamentos_openfda), el banco (bank_marketing_uci), el
gobierno uruguayo (rotulado_alimentos) y el caso de gastronomía
(cafe_sales_kaggle).

El entregable es lo que un consultor deja sobre la mesa al terminar el
trabajo de gobernanza sobre UN caso: la ficha del dataset, los KPIs finales
(calidad, documentación, PII, avance de curaduría), el diccionario, los
resultados reales de las reglas, el glosario del caso, su linaje honesto y
el estado de migración a Purview/Collibra (cuántas entidades/términos
saldrían, calculado con los conectores reales en modo previsualización).
Todo descargable: un Excel multi-hoja + un resumen ejecutivo en Markdown.

Nada acá se inventa: cada número sale de correr de verdad las reglas del
caso sobre su archivo, de la curaduría real guardada en disco, y de los
mismos payloads que usaría el push real a Purview/Collibra.
"""
from __future__ import annotations

import io

import pandas as pd

from . import collibra_export, curation, purview_export, samples
from .quality import overall_index
from .remediation import suggest_fix

_D = {
    "sheet_ficha": {"es": "Ficha", "en": "Overview", "pt": "Ficha"},
    "sheet_dic": {"es": "Diccionario", "en": "Dictionary", "pt": "Dicionário"},
    "sheet_cal": {"es": "Calidad", "en": "Quality", "pt": "Qualidade"},
    "sheet_glo": {"es": "Glosario", "en": "Glossary", "pt": "Glossário"},
    "sheet_lin": {"es": "Linaje", "en": "Lineage", "pt": "Linhagem"},
    "sheet_plan": {"es": "Plan de acción", "en": "Action plan", "pt": "Plano de ação"},
}


def _t(key: str, lang: str) -> str:
    v = _D[key]
    return v.get(lang, v["es"])


def case_keys() -> list[str]:
    return samples.sample_keys()


def _case_tables(key: str, lang: str):
    """Catálogo (1 fila), diccionario (con columna dataset), glosario y
    resultados del caso — mismas formas que consumen los conectores."""
    meta = samples.sample_meta(key, lang)
    cat = pd.DataFrame([samples.sample_catalog_row(key, lang)])
    dic = samples.sample_dictionary_df(key, lang).copy()
    dic.insert(0, "dataset", key)
    glo = samples.sample_glossary_df(key, lang)
    res = samples.sample_quality_results(key, lang)
    return meta, cat, dic, glo, res


def curation_progress(key: str, lang: str = "es") -> dict:
    """Avance de curaduría REAL del caso: cuántas de sus definiciones
    (ficha, columnas y términos) ya validó/modificó un responsable."""
    df = curation.list_items(lang)
    mine = df[df["dataset"] == key]
    total = len(mine)
    reviewed = int((mine["status"] != "sugerido_ia").sum())
    return {"total": total, "reviewed": reviewed,
            "pct": round(100.0 * reviewed / total, 1) if total else 0.0}


def _curation_lookup(key: str, lang: str):
    def lookup(term_id):
        rec = curation.get_record(f"glossary:{key}:{term_id}", lang)
        return (rec["status"], rec.get("text") or "") if rec else ("sugerido_ia", "")
    return lookup


def migration_readiness(key: str, lang: str = "es") -> dict:
    """Qué saldría hacia Purview y Collibra para ESTE caso — calculado con
    los conectores reales en dry-run (mismos payloads que el push real),
    sin credenciales y sin tocar la red."""
    _meta, cat, dic, glo, _res = _case_tables(key, lang)
    lookup = _curation_lookup(key, lang)
    pv = purview_export.push_all(cat, dic, glo, curation_lookup=lookup, dry_run=True)
    cb = collibra_export.push_all(cat, dic, glo, curation_lookup=lookup, dry_run=True)
    approved = sum(1 for t in pv["glossary"]["terms"] if t["status"] == "Approved")
    return {
        "purview_entities": pv["catalog"]["entity_count"],
        "purview_terms": pv["glossary"]["term_count"],
        "purview_terms_approved": approved,
        "purview_pii": pv["pii"]["classification_count"],
        "collibra_assets": cb["catalog"]["asset_count"],
        "collibra_terms": cb["glossary"]["term_count"],
    }


def case_lineage_df(key: str, lang: str = "es") -> pd.DataFrame:
    meta = samples.sample_meta(key, lang)
    return pd.DataFrame([
        {"source": meta["source"], "target": key,
         "source_layer": "source", "target_layer": "curated"},
        {"source": key, "target": "Power BI / Tableau / BI",
         "source_layer": "curated", "target_layer": "bi"},
    ])


def findings_df(key: str, lang: str = "es",
                results: pd.DataFrame | None = None) -> pd.DataFrame:
    """Hallazgos del caso con su plan de remediación: cada regla que no
    pasó (warn/fail) + causa raíz, corrección de corto y largo plazo y a
    quién le toca — el mismo motor de sugerencias (mvdg.remediation) que
    usa la pestaña ✅ Calidad. Esto es lo que convierte una "regla en
    falla" en un entregable profesional: el problema, diagnosticado y con
    plan de acción, no escondido."""
    if results is None:
        results = samples.sample_quality_results(key, lang)
    rows = []
    for _, r in results[results["status"] != "pass"].iterrows():
        fix = suggest_fix(r["rule_id"], r["dimension"], r["column"],
                          int(r["affected_rows"]), lang)
        rows.append({
            "rule_id": r["rule_id"], "column": r["column"],
            "dimension": r["dimension"], "status": r["status"],
            "score": r["score"], "threshold": r["threshold"],
            "affected_rows": int(r["affected_rows"]),
            "root_cause": fix["root_cause"],
            "short_term": fix["short_term"],
            "long_term": fix["long_term"],
            "owner": fix["owner"],
        })
    return pd.DataFrame(rows, columns=[
        "rule_id", "column", "dimension", "status", "score", "threshold",
        "affected_rows", "root_cause", "short_term", "long_term", "owner"])


def build_deliverable(key: str, lang: str = "es") -> dict:
    """El entregable completo de un caso, listo para mostrarse o exportarse."""
    meta, cat, dic, glo, res = _case_tables(key, lang)
    cur = curation_progress(key, lang)
    n_pass = int((res["status"] == "pass").sum())
    n_fail = int((res["status"] == "fail").sum())
    documented = int((dic["description"].str.strip() != "").sum())
    kpis = {
        "rows": int(cat.iloc[0]["rows"]),
        "columns": int(cat.iloc[0]["columns"]),
        "quality_index": overall_index(res),
        "rules_total": len(res),
        "rules_pass": n_pass,
        "rules_fail": n_fail,
        "documented_pct": round(100.0 * documented / len(dic), 1) if len(dic) else 0.0,
        "pii_columns": int((dic["pii"] == True).sum()),  # noqa: E712
        "curation_pct": cur["pct"],
        "curation_reviewed": cur["reviewed"],
        "curation_total": cur["total"],
    }
    return {
        "key": key, "meta": meta, "kpis": kpis,
        "catalog": cat, "dictionary": dic, "glossary": glo,
        "quality_results": res, "findings": findings_df(key, lang, res),
        "lineage": case_lineage_df(key, lang),
        "migration": migration_readiness(key, lang),
    }


def deliverable_xlsx_bytes(key: str, lang: str = "es") -> bytes:
    """Excel multi-hoja del entregable: Ficha, Diccionario, Calidad,
    Glosario y Linaje — para dejarle al cliente."""
    d = build_deliverable(key, lang)
    meta, kpis = d["meta"], d["kpis"]
    ficha = pd.DataFrame(
        [(k, v) for k, v in {**{
            "dataset": key, "nombre": meta["name"], "dominio": meta["domain"],
            "descripción": meta["description"], "dueño": meta["owner"],
            "steward": meta["steward"], "clasificación": meta["classification"],
            "fuente": meta["source"], "licencia": meta["license"],
        }, **kpis}.items()], columns=["campo", "valor"])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter",
                       engine_kwargs={"options": {"in_memory": True}}) as xw:
        ficha.to_excel(xw, sheet_name=_t("sheet_ficha", lang)[:31], index=False)
        d["dictionary"].to_excel(xw, sheet_name=_t("sheet_dic", lang)[:31], index=False)
        d["quality_results"].to_excel(xw, sheet_name=_t("sheet_cal", lang)[:31], index=False)
        d["glossary"].to_excel(xw, sheet_name=_t("sheet_glo", lang)[:31], index=False)
        d["lineage"].to_excel(xw, sheet_name=_t("sheet_lin", lang)[:31], index=False)
        d["findings"].to_excel(xw, sheet_name=_t("sheet_plan", lang)[:31], index=False)
    return buf.getvalue()


def executive_summary_md(key: str, lang: str = "es") -> str:
    """Resumen ejecutivo del entregable, en Markdown, en el idioma pedido."""
    d = build_deliverable(key, lang)
    m, k, mig = d["meta"], d["kpis"], d["migration"]
    tpl = {
        "es": (
            "# 📦 Entregable de gobernanza — {name}\n\n"
            "**Dataset:** `{key}` · **Dominio:** {domain} · **Clasificación:** {cls}\n\n"
            "**Dueño:** {owner} · **Steward:** {steward}\n\n"
            "**Fuente:** {source} ({license})\n\n"
            "## Resultados del trabajo de gobernanza\n\n"
            "- **{rows:,}** filas × **{cols}** columnas gobernadas\n"
            "- Índice de calidad final: **{qidx}/100** ({rpass}/{rtotal} reglas OK, {rfail} en falla)\n"
            "- **{doc}%** de columnas documentadas · **{pii}** columnas PII identificadas y marcadas\n"
            "- Curaduría: **{cpct}%** de las definiciones revisadas por un responsable ({crev}/{ctot})\n\n"
            "## Listo para migrar\n\n"
            "- Microsoft Purview: **{pv_e}** entidades + **{pv_t}** términos "
            "({pv_a} ya Approved por curaduría) + **{pv_p}** clasificaciones PII\n"
            "- Collibra: **{cb_a}** assets + **{cb_t}** Business Terms\n\n"
            "*Generado por MV Data Governance — cada número sale de correr las "
            "reglas reales sobre el archivo del caso y de la curaduría guardada.*\n"
        ),
        "en": (
            "# 📦 Governance deliverable — {name}\n\n"
            "**Dataset:** `{key}` · **Domain:** {domain} · **Classification:** {cls}\n\n"
            "**Owner:** {owner} · **Steward:** {steward}\n\n"
            "**Source:** {source} ({license})\n\n"
            "## Governance results\n\n"
            "- **{rows:,}** rows × **{cols}** governed columns\n"
            "- Final quality index: **{qidx}/100** ({rpass}/{rtotal} rules OK, {rfail} failing)\n"
            "- **{doc}%** of columns documented · **{pii}** PII columns identified and flagged\n"
            "- Curation: **{cpct}%** of definitions reviewed by an owner/steward ({crev}/{ctot})\n\n"
            "## Ready to migrate\n\n"
            "- Microsoft Purview: **{pv_e}** entities + **{pv_t}** terms "
            "({pv_a} already Approved via curation) + **{pv_p}** PII classifications\n"
            "- Collibra: **{cb_a}** assets + **{cb_t}** Business Terms\n\n"
            "*Generated by MV Data Governance — every number comes from running "
            "the real rules on the case file and from the saved curation.*\n"
        ),
        "pt": (
            "# 📦 Entregável de governança — {name}\n\n"
            "**Dataset:** `{key}` · **Domínio:** {domain} · **Classificação:** {cls}\n\n"
            "**Dono:** {owner} · **Steward:** {steward}\n\n"
            "**Fonte:** {source} ({license})\n\n"
            "## Resultados do trabalho de governança\n\n"
            "- **{rows:,}** linhas × **{cols}** colunas governadas\n"
            "- Índice de qualidade final: **{qidx}/100** ({rpass}/{rtotal} regras OK, {rfail} em falha)\n"
            "- **{doc}%** das colunas documentadas · **{pii}** colunas PII identificadas e marcadas\n"
            "- Curadoria: **{cpct}%** das definições revisadas por um responsável ({crev}/{ctot})\n\n"
            "## Pronto para migrar\n\n"
            "- Microsoft Purview: **{pv_e}** entidades + **{pv_t}** termos "
            "({pv_a} já Approved pela curadoria) + **{pv_p}** classificações PII\n"
            "- Collibra: **{cb_a}** assets + **{cb_t}** Business Terms\n\n"
            "*Gerado pelo MV Data Governance — cada número vem de rodar as "
            "regras reais no arquivo do caso e da curadoria salva.*\n"
        ),
    }
    heads = {
        "es": ("## Hallazgos y plan de remediación\n\n"
               "El entregable no esconde los problemas: los diagnostica con plan. "
               "Cada hallazgo tiene causa raíz, corrección inmediata, corrección "
               "de fondo y responsable:\n\n"),
        "en": ("## Findings and remediation plan\n\n"
               "The deliverable doesn't hide problems: it diagnoses them with a plan. "
               "Each finding has a root cause, an immediate fix, a structural fix "
               "and an owner:\n\n"),
        "pt": ("## Achados e plano de remediação\n\n"
               "O entregável não esconde os problemas: diagnostica-os com plano. "
               "Cada achado tem causa raiz, correção imediata, correção estrutural "
               "e responsável:\n\n"),
    }
    fnd = d["findings"]
    findings_md = ""
    if len(fnd):
        findings_md = heads.get(lang, heads["es"])
        for _, r in fnd.iterrows():
            findings_md += (
                f"- **{r['rule_id']}** ({r['column']}, {r['status']}, "
                f"{r['affected_rows']:,} filas) — {r['root_cause']} "
                f"→ *{r['short_term']}* — **{r['owner']}**\n")
        findings_md += "\n"
    body = tpl.get(lang, tpl["es"]).format(
        name=m["name"], key=key, domain=m["domain"], cls=m["classification"],
        owner=m["owner"], steward=m["steward"], source=m["source"],
        license=m["license"], rows=k["rows"], cols=k["columns"],
        qidx=k["quality_index"], rpass=k["rules_pass"], rtotal=k["rules_total"],
        rfail=k["rules_fail"], doc=k["documented_pct"], pii=k["pii_columns"],
        cpct=k["curation_pct"], crev=k["curation_reviewed"], ctot=k["curation_total"],
        pv_e=mig["purview_entities"], pv_t=mig["purview_terms"],
        pv_a=mig["purview_terms_approved"], pv_p=mig["purview_pii"],
        cb_a=mig["collibra_assets"], cb_t=mig["collibra_terms"])
    marker = "*Generado por" if lang == "es" else ("*Generated by" if lang == "en" else "*Gerado pelo")
    idx = body.rfind(marker)
    return body[:idx] + findings_md + body[idx:]
