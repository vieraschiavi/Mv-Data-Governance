"""
MV Data Governance · Laboratorio: caso de ejemplo completo, de punta a punta.

Un mismo dataset sintético (retail multicanal) recorre las 7 etapas típicas
de un proyecto de gobierno de datos: catalogar, medir calidad, gobernar
(dueños + glosario), corregir en origen, trazar linaje, verificar políticas
y publicar a BI. Cada etapa trae teoría en lenguaje simple + técnico, y se
ilustra con datos y números reales (el mismo motor de reglas del programa),
no con ejemplos inventados.

``degrade_tables`` reproduce el estado "sin gobierno" (nulos, duplicados,
formatos inválidos, FKs huérfanas, dominios inconsistentes) para poder
comparar ANTES vs. DESPUÉS con evidencia. La usa también
``docs/caso_ejemplo/medir_impacto.py`` (fuente de los números del caso
publicado en la web).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .demo_data import load_demo_tables
from .quality import open_issues, overall_index, quality_by_dimension, run_rules


def degrade_tables(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Reproduce el estado 'sin gobierno': muchos nulos, duplicados, formatos
    inválidos, FKs huérfanas y dominios inconsistentes. Determinístico."""
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


def _resumen(res: pd.DataFrame) -> dict:
    return {
        "indice": overall_index(res),
        "reglas_ok": int((res.status == "pass").sum()),
        "reglas_total": len(res),
        "fallas": int((res.status == "fail").sum()),
        "alertas": int((res.status == "warn").sum()),
        "filas_afectadas": int(res.affected_rows.sum()),
    }


def lab_measure(lang: str = "es") -> dict:
    """Corre el motor de reglas sobre el dataset degradado (antes) y el
    gobernado (después) y arma todo lo que necesita el dashboard del
    laboratorio: resultados crudos, resumen y comparación por dimensión."""
    after_tables = load_demo_tables()
    before_tables = degrade_tables(after_tables)

    res_before = run_rules(before_tables, lang)
    res_after = run_rules(after_tables, lang)

    dim_before = quality_by_dimension(res_before).rename(columns={"quality_index": "antes"})
    dim_after = quality_by_dimension(res_after).rename(columns={"quality_index": "despues"})
    by_dimension = dim_before.merge(dim_after, on="dimension")

    summary_before, summary_after = _resumen(res_before), _resumen(res_after)
    return {
        "results_before": res_before,
        "results_after": res_after,
        "issues_before": open_issues(res_before),
        "issues_after": open_issues(res_after),
        "by_dimension": by_dimension,
        "summary_before": summary_before,
        "summary_after": summary_after,
        "mejora_indice": round(summary_after["indice"] - summary_before["indice"], 1),
        "reduccion_filas_pct": round(
            100 * (summary_before["filas_afectadas"] - summary_after["filas_afectadas"])
            / max(1, summary_before["filas_afectadas"])),
    }


# ---------------------------------------------------------------------------
# Teoría por etapa: cada paso del laboratorio explicado en criollo y técnico,
# más qué se ve concretamente en el programa en ese paso. dmbok_area referencia
# la sección de mvdg.help_center.DMBOK_AREAS para que el usuario pueda cruzar
# ambas pantallas.
# ---------------------------------------------------------------------------
LAB_STEPS: list[dict] = [
    {
        "step_id": "contexto",
        "title": {"es": "0. El caso: una empresa retail multicanal",
                  "en": "0. The case: a multichannel retail company",
                  "pt": "0. O caso: uma empresa varejista multicanal"},
        "plain": {"es": "Una empresa vende por web, tienda, app y mayorista. Cada área mira sus propios números y no siempre coinciden. Vamos a gobernar sus datos de punta a punta, en 7 pasos.",
                  "en": "A company sells through web, store, app and wholesale. Every department looks at its own numbers and they don't always match. We'll govern its data end-to-end, in 7 steps.",
                  "pt": "Uma empresa vende por web, loja, app e atacado. Cada área olha seus próprios números e nem sempre batem. Vamos governar seus dados de ponta a ponta, em 7 passos."},
        "tech": {"es": "4 tablas sintéticas (dim_customers, dim_products, fct_sales, fct_payments) con problemas de calidad inyectados a propósito y semilla fija — 100% reproducible.",
                 "en": "4 synthetic tables (dim_customers, dim_products, fct_sales, fct_payments) with quality issues injected on purpose and a fixed seed — 100% reproducible.",
                 "pt": "4 tabelas sintéticas (dim_customers, dim_products, fct_sales, fct_payments) com problemas de qualidade injetados de propósito e semente fixa — 100% reproduzível."},
        "dmbok_area": None,
    },
    {
        "step_id": "catalogar",
        "title": {"es": "1. Catalogar: saber qué datos existen",
                  "en": "1. Catalog: knowing what data exists",
                  "pt": "1. Catalogar: saber quais dados existem"},
        "plain": {"es": "Antes de gobernar algo hay que saber que existe. El primer paso es un inventario: qué tablas hay, quién es dueño de cada una, y qué significa cada columna.",
                  "en": "Before governing something you have to know it exists. The first step is an inventory: which tables exist, who owns each one, and what each column means.",
                  "pt": "Antes de governar algo é preciso saber que existe. O primeiro passo é um inventário: quais tabelas existem, quem é dono de cada uma, e o que significa cada coluna."},
        "tech": {"es": "Catálogo de datasets (dueño, steward, clasificación, frescura) + diccionario de columnas (tipo, PII, término de negocio vinculado).",
                 "en": "Dataset catalog (owner, steward, classification, freshness) + column dictionary (type, PII, linked business term).",
                 "pt": "Catálogo de datasets (dono, steward, classificação, atualidade) + dicionário de colunas (tipo, PII, termo de negócio vinculado)."},
        "dmbok_area": "Gestión de metadatos",
    },
    {
        "step_id": "medir_antes",
        "title": {"es": "2. Medir calidad — ANTES de gobernar",
                  "en": "2. Measure quality — BEFORE governing",
                  "pt": "2. Medir qualidade — ANTES de governar"},
        "plain": {"es": "Así llegan los datos sin gobierno: emails vacíos, montos negativos, clientes que no existen, categorías escritas de mil formas distintas. Lo medimos con evidencia, no a ojo.",
                  "en": "This is how data arrives without governance: empty emails, negative amounts, customers that don't exist, categories written a thousand different ways. We measure it with evidence, not by eye.",
                  "pt": "É assim que os dados chegam sem governança: e-mails vazios, valores negativos, clientes que não existem, categorias escritas de mil formas diferentes. Medimos com evidência, não a olho."},
        "tech": {"es": "Las mismas 17 reglas sobre las 6 dimensiones DAMA, corridas contra una versión degradada de los datos (nulos +45%, FKs huérfanas, dominios inconsistentes).",
                 "en": "The same 17 rules across the 6 DAMA dimensions, run against a degraded version of the data (nulls +45%, orphan FKs, inconsistent domains).",
                 "pt": "As mesmas 17 regras nas 6 dimensões DAMA, rodadas contra uma versão degradada dos dados (nulos +45%, FKs órfãs, domínios inconsistentes)."},
        "dmbok_area": "Calidad de datos",
    },
    {
        "step_id": "gobernar",
        "title": {"es": "3. Gobernar: dueños y definiciones acordadas",
                  "en": "3. Govern: owners and agreed definitions",
                  "pt": "3. Governar: donos e definições acordadas"},
        "plain": {"es": "Esta parte NO la resuelve ningún software: un gerente tiene que aceptar ser dueño del dato, y el negocio tiene que acordar qué significa 'cliente activo'. Acá se registra ese acuerdo.",
                  "en": "No software solves this part: a manager has to accept owning the data, and the business has to agree on what 'active customer' means. This is where that agreement gets recorded.",
                  "pt": "Nenhum software resolve esta parte: um gerente precisa aceitar ser dono do dado, e o negócio precisa acordar o que significa 'cliente ativo'. Aqui se registra esse acordo."},
        "tech": {"es": "Glosario de negocio trilingüe (7 términos, 1 definición oficial cada uno) + dueños/stewards ya asignados en el catálogo del paso 1.",
                 "en": "Trilingual business glossary (7 terms, 1 official definition each) + owners/stewards already assigned in the step-1 catalog.",
                 "pt": "Glossário de negócio trilíngue (7 termos, 1 definição oficial cada) + donos/stewards já atribuídos no catálogo do passo 1."},
        "dmbok_area": "Gobierno de datos",
    },
    {
        "step_id": "medir_despues",
        "title": {"es": "4. Corregir en origen y medir — DESPUÉS",
                  "en": "4. Fix at the source and measure — AFTER",
                  "pt": "4. Corrigir na origem e medir — DEPOIS"},
        "plain": {"es": "Con dueños definidos y validaciones puestas en el origen (el formulario, el sistema), los mismos datos llegan limpios. Comparamos el mismo semáforo, antes vs. después.",
                  "en": "With owners defined and validations placed at the source (the form, the system), the same data arrives clean. We compare the same traffic light, before vs. after.",
                  "pt": "Com donos definidos e validações colocadas na origem (o formulário, o sistema), os mesmos dados chegam limpos. Comparamos o mesmo semáforo, antes vs. depois."},
        "tech": {"es": "Las 17 reglas corridas contra los datos gobernados (sin degradar). La comparación es apples-to-apples: mismo motor, mismos umbrales.",
                 "en": "The 17 rules run against the governed (non-degraded) data. The comparison is apples-to-apples: same engine, same thresholds.",
                 "pt": "As 17 regras rodadas contra os dados governados (sem degradar). A comparação é apples-to-apples: mesmo motor, mesmos limiares."},
        "dmbok_area": "Calidad de datos",
    },
    {
        "step_id": "linaje",
        "title": {"es": "5. Trazar el linaje: de dónde viene cada dato",
                  "en": "5. Trace lineage: where each piece of data comes from",
                  "pt": "5. Rastrear a linhagem: de onde vem cada dado"},
        "plain": {"es": "Cuando algo sale mal en un tablero, hay que poder rastrear hacia atrás hasta el sistema de origen para saber dónde arreglarlo.",
                  "en": "When something goes wrong on a dashboard, you need to be able to trace it back to the source system to know where to fix it.",
                  "pt": "Quando algo dá errado num painel, é preciso poder rastrear para trás até o sistema de origem para saber onde corrigir."},
        "tech": {"es": "Grafo dirigido fuente → cruda → curada → mart → BI (CRM/ERP/POS/Pasarela → dim_customers/fct_sales/… → mart_ventas_360 → Power BI/Tableau).",
                 "en": "Directed graph source → raw → curated → mart → BI (CRM/ERP/POS/Gateway → dim_customers/fct_sales/… → mart_ventas_360 → Power BI/Tableau).",
                 "pt": "Grafo direcionado fonte → cru → curado → mart → BI (CRM/ERP/POS/Gateway → dim_customers/fct_sales/… → mart_ventas_360 → Power BI/Tableau)."},
        "dmbok_area": "Linaje e integración de datos",
    },
    {
        "step_id": "politicas",
        "title": {"es": "6. Verificar políticas con evidencia",
                  "en": "6. Verify policies with evidence",
                  "pt": "6. Verificar políticas com evidência"},
        "plain": {"es": "En vez de un checklist marcado a mano ('¿cumplimos? sí/no'), cada política se verifica automáticamente contra los datos reales.",
                  "en": "Instead of a hand-checked checklist ('do we comply? yes/no'), every policy is verified automatically against the real data.",
                  "pt": "Em vez de uma checklist marcada à mão ('cumprimos? sim/não'), cada política é verificada automaticamente contra os dados reais."},
        "tech": {"es": "6 políticas evaluadas contra catálogo + resultados de calidad: dueños asignados, columnas documentadas, PII clasificada, índice ≥95, sin fallas críticas, términos vinculados.",
                 "en": "6 policies evaluated against the catalog + quality results: owners assigned, columns documented, PII classified, index ≥95, no critical failures, terms linked.",
                 "pt": "6 políticas avaliadas contra o catálogo + resultados de qualidade: donos atribuídos, colunas documentadas, PII classificada, índice ≥95, sem falhas críticas, termos vinculados."},
        "dmbok_area": "Gobierno de datos",
    },
    {
        "step_id": "bi",
        "title": {"es": "7. Publicar a BI: una sola versión de la verdad",
                  "en": "7. Publish to BI: one single version of the truth",
                  "pt": "7. Publicar para BI: uma única versão da verdade"},
        "plain": {"es": "El resultado final: los mismos datos, ya medidos y confiables, llegan a Power BI, Tableau o cualquier herramienta que ya uses — sin copiar y pegar planillas.",
                  "en": "The final result: the same data, already measured and trustworthy, reaches Power BI, Tableau or any tool you already use — no more copy-pasting spreadsheets.",
                  "pt": "O resultado final: os mesmos dados, já medidos e confiáveis, chegam ao Power BI, Tableau ou qualquer ferramenta que você já use — sem copiar e colar planilhas."},
        "tech": {"es": "API REST (9 tablas de gobierno) + exportación CSV/Excel/JSON/Parquet + bundle .xlsx multi-hoja listo para conectar.",
                 "en": "REST API (9 governance tables) + CSV/Excel/JSON/Parquet export + ready-to-connect multi-sheet .xlsx bundle.",
                 "pt": "API REST (9 tabelas de governança) + exportação CSV/Excel/JSON/Parquet + pacote .xlsx multi-aba pronto para conectar."},
        "dmbok_area": "Data warehousing y BI",
    },
]


def lab_steps(lang: str = "es") -> list[dict]:
    """Los 8 pasos (0–7) del laboratorio, resueltos al idioma pedido."""
    return [{
        "step_id": s["step_id"],
        "title": s["title"].get(lang, s["title"]["es"]),
        "plain": s["plain"].get(lang, s["plain"]["es"]),
        "tech": s["tech"].get(lang, s["tech"]["es"]),
        "dmbok_area": s["dmbok_area"],
    } for s in LAB_STEPS]
