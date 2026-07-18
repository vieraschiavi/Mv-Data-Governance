"""
MV Data Governance · Data Products, contratos de datos y alarmística.

Cubre el eje "moderno" del gobierno de datos que piden los equipos que trabajan
con Data Mesh / Data Products (y que aparece textual en avisos laborales de
Data Governance Analyst): datasets tratados como PRODUCTOS con dominio y roles
(Domain Owner, Product Owner, Productor, Consumidor), CONTRATOS de datos entre
productores y consumidores (reglas, umbrales, SLA y qué pasa si falla) y
ALARMÍSTICA operando sobre el linaje (cada incumplimiento sabe a qué activos
aguas abajo afecta y a quién avisar).

Principio de honestidad del producto: acá NO se inventa nada.
  - Los dominios, dueños, stewards, fuentes y frecuencias salen del catálogo
    real (``catalog.catalog_df`` para la demo, ``samples.sample_catalog_row``
    para los casos reales).
  - Las reglas y umbrales del contrato son las reglas de calidad que el
    programa YA ejecuta (``quality`` / ``samples``): el contrato no declara
    umbrales nuevos, formaliza los existentes entre las partes.
  - El estado del contrato se evalúa contra la ÚLTIMA corrida real de reglas.
  - El impacto aguas abajo se calcula recorriendo el linaje real
    (``scope.combined_lineage``), no una lista hardcodeada.
  - La alarmística es "al abrir/evaluar" (on-demand): este programa corre
    local y sin telemetría, no hay un demonio 24/7 vigilando. Eso se dice
    tal cual en la UI en vez de simular monitoreo continuo.

Los acuerdos firmados (quién acordó el contrato, rol y fecha) se persisten en
``data_dir()/contratos.json`` — mismo patrón local-first que el resto.
"""
from __future__ import annotations

import io
import json
import os
from datetime import datetime, timezone

import pandas as pd

from . import catalog, samples, scope
from .clients import data_dir
from .remediation import suggest_fix


def _tr(es: str, en: str, pt: str) -> dict:
    return {"es": es, "en": en, "pt": pt}


# ---------------------------------------------------------------------------
# Persistencia de acuerdos (documentar acuerdos entre las partes)
# ---------------------------------------------------------------------------

def _file() -> str:
    return os.path.join(data_dir(), "contratos.json")


def _load() -> dict:
    path = _file()
    if not os.path.exists(path):
        return {"agreements": {}}
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            return {"agreements": {}}
        data.setdefault("agreements", {})
        return data
    except (json.JSONDecodeError, OSError):
        return {"agreements": {}}


def _write(data: dict) -> None:
    os.makedirs(data_dir(), exist_ok=True)
    tmp = _file() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, _file())


def save_agreement(dataset: str, signed_by: str, role: str) -> None:
    """Firma (documenta) el acuerdo del contrato de un producto de datos."""
    data = _load()
    data["agreements"][dataset] = {
        "signed_by": signed_by.strip(),
        "role": role.strip(),
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }
    _write(data)


def agreement_for(dataset: str) -> dict | None:
    return _load()["agreements"].get(dataset)


def delete_agreement(dataset: str) -> None:
    data = _load()
    data["agreements"].pop(dataset, None)
    _write(data)


# ---------------------------------------------------------------------------
# Linaje: consumidores e impacto aguas abajo (recorrido real del grafo)
# ---------------------------------------------------------------------------

def _lineage_maps(lang: str) -> tuple[dict[str, str], dict[str, list[str]]]:
    """(id→label, id→hijos directos) del linaje combinado real."""
    nodes, edges = scope.combined_lineage(lang)
    labels = {n["id"]: n["label"] for n in nodes}
    children: dict[str, list[str]] = {}
    for src, dst in edges:
        children.setdefault(src, []).append(dst)
    return labels, children


def downstream(dataset: str, lang: str = "es") -> list[str]:
    """Etiquetas de TODOS los nodos aguas abajo del dataset (BFS en el grafo)."""
    labels, children = _lineage_maps(lang)
    seen: list[str] = []
    queue = list(children.get(dataset, []))
    visited = {dataset}
    while queue:
        node = queue.pop(0)
        if node in visited:
            continue
        visited.add(node)
        seen.append(labels.get(node, node))
        queue.extend(children.get(node, []))
    return seen


# ---------------------------------------------------------------------------
# Productos de datos: catálogo real → producto + roles del modelo
# ---------------------------------------------------------------------------

def product_keys(lang: str = "es") -> list[str]:
    demo = catalog.catalog_df(lang)["dataset"].tolist()
    return demo + samples.sample_keys()


def _product_row(dataset: str, lang: str) -> dict:
    """Ficha de producto desde el catálogo real (demo o caso)."""
    demo = catalog.catalog_df(lang)
    hit = demo[demo["dataset"] == dataset]
    if len(hit):
        row = hit.iloc[0].to_dict()
    else:
        row = samples.sample_catalog_row(dataset, lang)
    return {
        "dataset": dataset,
        "domain": row.get("domain", ""),
        # Roles del modelo (Data Mesh): el dueño del dominio es el owner del
        # catálogo; el Product Owner operativo es el steward. Productor =
        # sistema fuente real; consumidores = aguas abajo del linaje real.
        "domain_owner": row.get("owner", ""),
        "product_owner": row.get("steward", ""),
        "producer": row.get("source", ""),
        "consumers": ", ".join(downstream(dataset, lang)) or "—",
        "sla_refresh": row.get("refresh", ""),
        "classification": row.get("classification", ""),
    }


# ---------------------------------------------------------------------------
# Evaluación del contrato contra la última corrida REAL de reglas
# ---------------------------------------------------------------------------

STATUSES = ("vigente", "borrador")          # acuerdo documentado ↔ sin firmar
COMPLIANCE = ("cumple", "en_riesgo", "incumple")


def _compliance(sub: pd.DataFrame) -> tuple[str, float]:
    """Estado del contrato según los estados reales de sus reglas."""
    total = len(sub)
    if total == 0:
        return "cumple", 100.0
    passing = int((sub["status"] == "pass").sum())
    pct = round(passing / total * 100.0, 1)
    if (sub["status"] == "fail").any():
        return "incumple", pct
    if (sub["status"] == "warn").any():
        return "en_riesgo", pct
    return "cumple", pct


def contracts_df(lang: str = "es",
                 results: pd.DataFrame | None = None) -> pd.DataFrame:
    """Un contrato por producto de datos, evaluado con resultados reales."""
    if results is None:
        results = scope.combined_results(lang)
    rows = []
    for key in product_keys(lang):
        prod = _product_row(key, lang)
        sub = results[results["dataset"] == key]
        comp, pct = _compliance(sub)
        agr = agreement_for(key)
        rows.append({
            **prod,
            "rules": len(sub),
            "rules_pass": int((sub["status"] == "pass").sum()),
            "rules_warn": int((sub["status"] == "warn").sum()),
            "rules_fail": int((sub["status"] == "fail").sum()),
            "compliance_pct": pct,
            "compliance": comp,
            "agreement": "vigente" if agr else "borrador",
            "signed_by": (agr or {}).get("signed_by", ""),
            "signed_role": (agr or {}).get("role", ""),
            "signed_date": (agr or {}).get("date", ""),
        })
    return pd.DataFrame(rows)


def alerts_df(lang: str = "es",
              results: pd.DataFrame | None = None) -> pd.DataFrame:
    """Alarmística: una alerta por regla no aprobada, con impacto aguas abajo
    (linaje real), a quién avisar (roles reales) y acción inmediata sugerida
    (motor de remediación existente)."""
    if results is None:
        results = scope.combined_results(lang)
    prods = {k: _product_row(k, lang) for k in product_keys(lang)}
    rows = []
    for _, r in results[results["status"] != "pass"].iterrows():
        prod = prods.get(r["dataset"])
        if prod is None:            # regla de un dataset fuera del alcance
            continue
        fix = suggest_fix(r["rule_id"], r["dimension"], r["column"],
                          int(r["affected_rows"]), lang)
        sev = "fail" if r["status"] == "fail" else "warn"
        notify = (prod["product_owner"] if sev == "warn"
                  else f'{prod["domain_owner"]} + {prod["product_owner"]}')
        rows.append({
            "dataset": r["dataset"],
            "domain": prod["domain"],
            "rule_id": r["rule_id"],
            "column": r["column"],
            "dimension": r["dimension"],
            "severity": sev,
            "score": r["score"],
            "threshold": r["threshold"],
            "affected_rows": int(r["affected_rows"]),
            "impact_downstream": prod["consumers"],
            "notify": notify,
            "action": fix["short_term"],
        })
    cols = ["dataset", "domain", "rule_id", "column", "dimension", "severity",
            "score", "threshold", "affected_rows", "impact_downstream",
            "notify", "action"]
    df = pd.DataFrame(rows, columns=cols)
    if len(df):
        df = df.sort_values(["severity", "dataset"],
                            ascending=[True, True]).reset_index(drop=True)
    return df


def kpis(lang: str = "es",
         results: pd.DataFrame | None = None) -> dict:
    """KPIs del tablero de contratos (todo derivado de datos reales)."""
    con = contracts_df(lang, results)
    ale = alerts_df(lang, results)
    return {
        "products": len(con),
        "ok": int((con["compliance"] == "cumple").sum()),
        "at_risk": int((con["compliance"] == "en_riesgo").sum()),
        "breached": int((con["compliance"] == "incumple").sum()),
        "alerts": len(ale),
        "signed": int((con["agreement"] == "vigente").sum()),
    }


# ---------------------------------------------------------------------------
# Marco teórico: Data Mesh, Data Products y contratos de datos (trilingüe).
# Mismo espíritu que dmbok.py: teoría en criollo + técnico + con qué pieza
# concreta del programa se practica cada concepto.
# ---------------------------------------------------------------------------

THEORY: list[dict] = [
    {
        "key": "domain",
        "concept": _tr("Dominio de datos", "Data domain", "Domínio de dados"),
        "plain": _tr(
            "En vez de un equipo central dueño de TODOS los datos, cada área de negocio (ventas, finanzas, regulatorio) es dueña de los suyos: los conoce, los produce y responde por ellos.",
            "Instead of one central team owning ALL data, each business area (sales, finance, regulatory) owns its own data: it knows it, produces it and answers for it.",
            "Em vez de uma equipe central dona de TODOS os dados, cada área de negócio (vendas, finanças, regulatório) é dona dos seus: conhece, produz e responde por eles."),
        "practice": _tr(
            "Cada dataset del catálogo tiene su columna «dominio» (Clientes, Ventas, Farmacéutica/Regulatorio…) heredada por el producto de datos.",
            "Each catalog dataset carries its «domain» column (Customers, Sales, Pharma/Regulatory…) inherited by the data product.",
            "Cada dataset do catálogo tem sua coluna «domínio» (Clientes, Vendas, Farmacêutica/Regulatório…) herdada pelo produto de dados."),
    },
    {
        "key": "product",
        "concept": _tr("Data Product (dato como producto)", "Data Product (data as a product)", "Data Product (dado como produto)"),
        "plain": _tr(
            "Tratar un dataset como se trata un producto: con dueño, usuarios, calidad medida, documentación y ciclo de vida — no como un archivo que «quedó ahí».",
            "Treat a dataset the way you treat a product: with an owner, users, measured quality, documentation and a lifecycle — not as a file that «ended up there».",
            "Tratar um dataset como se trata um produto: com dono, usuários, qualidade medida, documentação e ciclo de vida — não como um arquivo que «ficou lá»."),
        "practice": _tr(
            "La pestaña 🤝 Contratos lista cada dataset gobernado como producto: dominio, roles, SLA, estado del contrato y consumidores reales del linaje.",
            "The 🤝 Contracts tab lists every governed dataset as a product: domain, roles, SLA, contract status and real consumers from lineage.",
            "A aba 🤝 Contratos lista cada dataset governado como produto: domínio, papéis, SLA, status do contrato e consumidores reais da linhagem."),
    },
    {
        "key": "contract",
        "concept": _tr("Contrato de datos", "Data contract", "Contrato de dados"),
        "plain": _tr(
            "El acuerdo explícito entre quien produce un dato y quien lo consume: qué reglas cumple, con qué umbrales, cada cuánto se refresca (SLA) y qué pasa si falla. Sin contrato, el consumidor descubre los problemas en producción.",
            "The explicit agreement between whoever produces a dataset and whoever consumes it: which rules it meets, at which thresholds, how often it refreshes (SLA) and what happens on failure. Without a contract, consumers discover problems in production.",
            "O acordo explícito entre quem produz um dado e quem o consome: quais regras cumpre, com quais limiares, com que frequência se atualiza (SLA) e o que acontece se falhar. Sem contrato, o consumidor descobre os problemas em produção."),
        "practice": _tr(
            "El contrato de cada producto formaliza las reglas de calidad REALES ya definidas (con sus umbrales), el refresco del catálogo como SLA y el escalamiento por severidad. Se evalúa contra la última corrida real de reglas.",
            "Each product's contract formalizes the REAL quality rules already defined (with their thresholds), the catalog refresh as SLA and severity-based escalation. It is evaluated against the latest real rule run.",
            "O contrato de cada produto formaliza as regras de qualidade REAIS já definidas (com seus limiares), a atualização do catálogo como SLA e o escalonamento por severidade. É avaliado contra a última execução real de regras."),
    },
    {
        "key": "sla",
        "concept": _tr("SLA / umbrales", "SLA / thresholds", "SLA / limiares"),
        "plain": _tr(
            "El «cuánto es aceptable», por escrito: 95% de completitud, refresco diario, cero duplicados. Un número acordado convierte una discusión subjetiva en un semáforo.",
            "The «how much is acceptable», in writing: 95% completeness, daily refresh, zero duplicates. An agreed number turns a subjective argument into a traffic light.",
            "O «quanto é aceitável», por escrito: 95% de completude, atualização diária, zero duplicados. Um número acordado transforma uma discussão subjetiva em um semáforo."),
        "practice": _tr(
            "Cada regla del programa ya tiene su umbral (threshold); el contrato lo hereda tal cual — no declara números nuevos. La frecuencia (SLA de refresco) sale del campo real «refresh» del catálogo.",
            "Every rule in the program already has its threshold; the contract inherits it as-is — it declares no new numbers. Frequency (refresh SLA) comes from the catalog's real «refresh» field.",
            "Cada regra do programa já tem seu limiar (threshold); o contrato o herda tal qual — não declara números novos. A frequência (SLA de atualização) vem do campo real «refresh» do catálogo."),
    },
    {
        "key": "alerts",
        "concept": _tr("Alarmística y KPIs sobre el linaje", "Alerting and KPIs over lineage", "Alarmística e KPIs sobre a linhagem"),
        "plain": _tr(
            "Que algo avise cuando un dato se rompe — y que el aviso diga a QUIÉN le afecta aguas abajo, no solo «falló una regla». Así el dato se usa con confianza.",
            "Something should alert when data breaks — and the alert should say WHO is affected downstream, not just «a rule failed». That is how data gets used with confidence.",
            "Algo deve avisar quando um dado quebra — e o aviso deve dizer QUEM é afetado rio abaixo, não só «uma regra falhou». Assim o dado é usado com confiança."),
        "practice": _tr(
            "Cada regla no aprobada genera una alerta con: severidad, score vs. umbral, activos aguas abajo afectados (recorriendo el linaje real), a quién avisar (PO / Domain Owner según severidad) y la acción inmediata del motor de remediación. Honesto: la evaluación es al abrir la pestaña — este programa corre local, sin demonio 24/7.",
            "Every non-passing rule raises an alert with: severity, score vs. threshold, affected downstream assets (walking the real lineage), whom to notify (PO / Domain Owner by severity) and the immediate action from the remediation engine. Honest: evaluation happens when the tab opens — this program runs locally, no 24/7 daemon.",
            "Cada regra não aprovada gera um alerta com: severidade, score vs. limiar, ativos afetados rio abaixo (percorrendo a linhagem real), quem notificar (PO / Domain Owner conforme severidade) e a ação imediata do motor de remediação. Honesto: a avaliação acontece ao abrir a aba — este programa roda localmente, sem daemon 24/7."),
    },
    {
        "key": "roles",
        "concept": _tr("Roles del modelo: Domain Owner, PO, Productor, Consumidor", "Model roles: Domain Owner, PO, Producer, Consumer", "Papéis do modelo: Domain Owner, PO, Produtor, Consumidor"),
        "plain": _tr(
            "Domain Owner: responde por el dominio ante el negocio. Product Owner (PO): opera el producto día a día. Productor: el sistema/equipo que genera el dato. Consumidor: quien lo usa (BI, otro dominio, un modelo).",
            "Domain Owner: answers for the domain to the business. Product Owner (PO): runs the product day to day. Producer: the system/team generating the data. Consumer: whoever uses it (BI, another domain, a model).",
            "Domain Owner: responde pelo domínio perante o negócio. Product Owner (PO): opera o produto no dia a dia. Produtor: o sistema/equipe que gera o dado. Consumidor: quem o usa (BI, outro domínio, um modelo)."),
        "practice": _tr(
            "Domain Owner = dueño del catálogo; PO = steward; Productor = sistema fuente real (CRM, ERP, openFDA…); Consumidores = nodos aguas abajo del linaje real. Nada se inventa: si el catálogo cambia, los roles cambian.",
            "Domain Owner = catalog owner; PO = steward; Producer = real source system (CRM, ERP, openFDA…); Consumers = downstream nodes of the real lineage. Nothing is invented: change the catalog and the roles change.",
            "Domain Owner = dono do catálogo; PO = steward; Produtor = sistema fonte real (CRM, ERP, openFDA…); Consumidores = nós rio abaixo da linhagem real. Nada é inventado: mude o catálogo e os papéis mudam."),
    },
    {
        "key": "agreement",
        "concept": _tr("Acuerdos documentados", "Documented agreements", "Acordos documentados"),
        "plain": _tr(
            "Facilitar la conversación entre Datos, Producto y Negocio termina en algo escrito: quién acordó qué y cuándo. Un acuerdo no documentado es una opinión.",
            "Facilitating the conversation between Data, Product and Business ends in something written: who agreed to what and when. An undocumented agreement is an opinion.",
            "Facilitar a conversa entre Dados, Produto e Negócio termina em algo escrito: quem acordou o quê e quando. Um acordo não documentado é uma opinião."),
        "practice": _tr(
            "Cada contrato se firma con nombre, rol y fecha (queda en el equipo local, auditable). Un contrato sin firma figura como «borrador»; firmado pasa a «vigente».",
            "Each contract is signed with name, role and date (stored locally, auditable). An unsigned contract shows as «draft»; once signed it becomes «active».",
            "Cada contrato é assinado com nome, papel e data (fica no equipamento local, auditável). Um contrato sem assinatura aparece como «rascunho»; assinado passa a «vigente»."),
    },
    {
        "key": "federated",
        "concept": _tr("Gobernanza federada y adopción", "Federated governance and adoption", "Governança federada e adoção"),
        "plain": _tr(
            "Las reglas comunes (seguridad, calidad mínima, glosario) se definen una vez para todos; cada dominio las aplica en lo suyo. El objetivo final no es el control: es que el dato se ADOPTE y genere valor de negocio sin frenar la agilidad.",
            "Common rules (security, minimum quality, glossary) are defined once for everyone; each domain applies them to its own data. The end goal is not control: it is data ADOPTION generating business value without slowing the business down.",
            "As regras comuns (segurança, qualidade mínima, glossário) são definidas uma vez para todos; cada domínio as aplica no que é seu. O objetivo final não é o controle: é que o dado seja ADOTADO e gere valor de negócio sem frear a agilidade."),
        "practice": _tr(
            "Las políticas, dimensiones de calidad y el glosario son transversales; cada producto los cumple en su dominio. Los KPIs del tablero (cumplen / en riesgo / incumplen, curaduría, documentación) miden la adopción, no solo el control.",
            "Policies, quality dimensions and the glossary are cross-cutting; each product meets them within its domain. The dashboard KPIs (compliant / at risk / breached, curation, documentation) measure adoption, not just control.",
            "As políticas, dimensões de qualidade e o glossário são transversais; cada produto os cumpre no seu domínio. Os KPIs do painel (cumprem / em risco / descumprem, curadoria, documentação) medem a adoção, não só o controle."),
    },
]


def theory(lang: str = "es") -> list[dict]:
    """Marco teórico resuelto al idioma pedido."""
    return [{"key": c["key"],
             "concept": c["concept"][lang],
             "plain": c["plain"][lang],
             "practice": c["practice"][lang]} for c in THEORY]


def theory_df(lang: str = "es") -> pd.DataFrame:
    return pd.DataFrame(theory(lang))


# ---------------------------------------------------------------------------
# Export: contratos + alertas + marco teórico en un Excel (100% en memoria)
# ---------------------------------------------------------------------------

_SHEETS = {
    "es": ("Contratos", "Alertas", "Marco teórico"),
    "en": ("Contracts", "Alerts", "Theory"),
    "pt": ("Contratos", "Alertas", "Marco teórico"),
}


def contracts_xlsx_bytes(lang: str = "es",
                         results: pd.DataFrame | None = None) -> bytes:
    if results is None:
        results = scope.combined_results(lang)
    s_con, s_ale, s_teo = _SHEETS.get(lang, _SHEETS["es"])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter",
                        engine_kwargs={"options": {"in_memory": True}}) as xw:
        contracts_df(lang, results).to_excel(xw, sheet_name=s_con, index=False)
        alerts_df(lang, results).to_excel(xw, sheet_name=s_ale, index=False)
        theory_df(lang).to_excel(xw, sheet_name=s_teo, index=False)
    return buf.getvalue()
