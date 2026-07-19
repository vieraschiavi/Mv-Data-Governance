"""
MV Data Governance · Servidor MCP (Model Context Protocol) de la gobernanza.

Expone la capa de gobierno del programa (catálogo, diccionario, glosario,
calidad, linaje, contratos de datos y alertas) como herramientas MCP, para que
cualquier cliente de IA (Claude Code, VS Code, Copilot, un agente propio) pueda
consultarla en lenguaje natural — el mismo patrón que Microsoft usa con sus
servidores MCP de Power BI (Modeling MCP local y Fabric/Power BI remoto).

Principios (los mismos de toda la plataforma):
  - **Solo lectura**: ninguna herramienta modifica nada.
  - **Solo metadata**: se expone catálogo/reglas/linaje/contratos; NUNCA filas
    de datos de clientes. La promesa "nada viaja a internet" se mantiene: el
    transporte es stdio LOCAL (el cliente lanza este proceso en tu máquina).
  - **Apagado por defecto**: el servidor solo corre si el usuario lo lanza o
    lo configura en su cliente MCP.
  - **Nada inventado**: todo sale de los módulos reales del programa; la
    evaluación de contratos es contra la última corrida real de reglas.

Uso (cliente MCP por stdio):
    python -m mvdg.mcp_server

Configuración en Claude Code:
    claude mcp add mvdg -- python -m mvdg.mcp_server

SDK verificado: mcp 1.28.1 (PyPI, 2026-07-19) — FastMCP + transporte stdio.
"""
from __future__ import annotations

import json

import pandas as pd

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover - entorno sin el SDK
    raise ImportError(
        "El servidor MCP necesita el SDK oficial de Model Context Protocol: "
        "pip install mcp  (viene incluido en requirements.txt)") from exc

from . import contracts, deliverable, samples, scope

LANGS = ("es", "en", "pt")

mcp = FastMCP("mvdg_mcp")


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _lang(lang: str) -> str:
    lang = (lang or "es").strip().lower()
    if lang not in LANGS:
        raise ValueError(
            f"Idioma '{lang}' no soportado. Usá uno de: {', '.join(LANGS)}.")
    return lang


def _df_json(df: pd.DataFrame) -> str:
    return json.dumps(df.to_dict(orient="records"),
                      ensure_ascii=False, default=str)


def _dataset_or_error(dataset: str, lang: str) -> str | None:
    """None si el dataset existe; mensaje de error accionable si no."""
    valid = contracts.product_keys(lang)
    if dataset and dataset not in valid:
        return (f"Error: dataset '{dataset}' no existe. "
                f"Datasets gobernados: {', '.join(valid)}.")
    return None


# ---------------------------------------------------------------------------
# tools (todas read-only, metadata only)
# ---------------------------------------------------------------------------

@mcp.tool(
    name="mvdg_catalog",
    annotations={"title": "Catálogo de datos gobernado",
                 "readOnlyHint": True, "destructiveHint": False,
                 "idempotentHint": True, "openWorldHint": False},
)
def mvdg_catalog(lang: str = "es") -> str:
    """Catálogo de datos gobernado completo (demo + casos reales).

    Devuelve un JSON (lista de objetos) con un registro por dataset:
    dataset, domain, description, owner, steward, classification, source,
    refresh, rows, columns. Es metadata del catálogo — nunca filas de datos.

    Args:
        lang: Idioma de las descripciones: "es" (default), "en" o "pt".
    """
    lang = _lang(lang)
    return _df_json(scope.combined_catalog(lang))


@mcp.tool(
    name="mvdg_dictionary",
    annotations={"title": "Diccionario de columnas (con PII)",
                 "readOnlyHint": True, "destructiveHint": False,
                 "idempotentHint": True, "openWorldHint": False},
)
def mvdg_dictionary(dataset: str = "", lang: str = "es") -> str:
    """Diccionario de datos por columna, con marca de PII.

    Devuelve un JSON con un registro por columna: dataset, column, type,
    description, pii (bool) y ejemplo si existe.

    Args:
        dataset: Opcional — filtra a un solo dataset (ej. "medicamentos_openfda").
                 Vacío devuelve todas las columnas de todos los datasets.
        lang: Idioma: "es" (default), "en" o "pt".
    """
    lang = _lang(lang)
    err = _dataset_or_error(dataset, lang)
    if err:
        return err
    dic = scope.combined_dictionary(lang)
    if dataset:
        dic = dic[dic["dataset"] == dataset]
    return _df_json(dic)


@mcp.tool(
    name="mvdg_glossary",
    annotations={"title": "Glosario de negocio (con estado de curaduría)",
                 "readOnlyHint": True, "destructiveHint": False,
                 "idempotentHint": True, "openWorldHint": False},
)
def mvdg_glossary(lang: str = "es") -> str:
    """Glosario de negocio gobernado con definiciones y estado.

    Devuelve un JSON con un registro por término (término, definición,
    dominio/dataset y metadatos disponibles).

    Args:
        lang: Idioma: "es" (default), "en" o "pt".
    """
    lang = _lang(lang)
    return _df_json(scope.combined_glossary(lang))


@mcp.tool(
    name="mvdg_quality",
    annotations={"title": "Resultados de calidad (última corrida real)",
                 "readOnlyHint": True, "destructiveHint": False,
                 "idempotentHint": True, "openWorldHint": False},
)
def mvdg_quality(dataset: str = "", lang: str = "es") -> str:
    """Resultados de la última corrida REAL de reglas de calidad.

    Devuelve un JSON con un registro por regla: rule_id, dataset, column,
    dimension, description, score, threshold, status (pass/warn/fail),
    affected_rows. Los scores salen de ejecutar las reglas de verdad, no
    están simulados.

    Args:
        dataset: Opcional — filtra a un dataset. Vacío = todos.
        lang: Idioma: "es" (default), "en" o "pt".
    """
    lang = _lang(lang)
    err = _dataset_or_error(dataset, lang)
    if err:
        return err
    res = scope.combined_results(lang)
    if dataset:
        res = res[res["dataset"] == dataset]
    return _df_json(res)


@mcp.tool(
    name="mvdg_lineage",
    annotations={"title": "Linaje de datos (grafo fuente→curado→BI)",
                 "readOnlyHint": True, "destructiveHint": False,
                 "idempotentHint": True, "openWorldHint": False},
)
def mvdg_lineage(lang: str = "es") -> str:
    """Grafo de linaje completo del alcance gobernado.

    Devuelve un JSON: {"nodes": [{id, label, layer}...],
    "edges": [[origen, destino]...]}. Las capas son source/raw/curated/
    mart/bi según el activo.

    Args:
        lang: Idioma de las etiquetas: "es" (default), "en" o "pt".
    """
    lang = _lang(lang)
    nodes, edges = scope.combined_lineage(lang)
    return json.dumps({"nodes": nodes, "edges": [list(e) for e in edges]},
                      ensure_ascii=False)


@mcp.tool(
    name="mvdg_contracts",
    annotations={"title": "Contratos de datos (Data Products)",
                 "readOnlyHint": True, "destructiveHint": False,
                 "idempotentHint": True, "openWorldHint": False},
)
def mvdg_contracts(lang: str = "es") -> str:
    """Contratos de datos por producto gobernado, evaluados con reglas reales.

    Devuelve un JSON con un registro por producto: dataset, domain, roles del
    modelo (domain_owner, product_owner, producer, consumers), sla_refresh,
    reglas (total/pass/warn/fail), compliance_pct, compliance
    (cumple/en_riesgo/incumple) y estado del acuerdo (vigente/borrador con
    firmante y fecha).

    Args:
        lang: Idioma: "es" (default), "en" o "pt".
    """
    lang = _lang(lang)
    return _df_json(contracts.contracts_df(lang))


@mcp.tool(
    name="mvdg_alerts",
    annotations={"title": "Alertas de calidad con impacto aguas abajo",
                 "readOnlyHint": True, "destructiveHint": False,
                 "idempotentHint": True, "openWorldHint": False},
)
def mvdg_alerts(lang: str = "es") -> str:
    """Alarmística: una alerta por regla no aprobada, con impacto en el linaje.

    Devuelve un JSON con un registro por alerta: dataset, domain, rule_id,
    column, dimension, severity (warn/fail), score, threshold, affected_rows,
    impact_downstream (activos aguas abajo según el linaje real), notify
    (a quién avisar según severidad) y action (acción inmediata sugerida).

    Args:
        lang: Idioma: "es" (default), "en" o "pt".
    """
    lang = _lang(lang)
    return _df_json(contracts.alerts_df(lang))


@mcp.tool(
    name="mvdg_case_deliverable",
    annotations={"title": "Entregable ejecutivo de un caso real",
                 "readOnlyHint": True, "destructiveHint": False,
                 "idempotentHint": True, "openWorldHint": False},
)
def mvdg_case_deliverable(case: str, lang: str = "es") -> str:
    """Resumen ejecutivo (Markdown) del entregable de gobernanza de un caso.

    Incluye KPIs reales, hallazgos con plan de remediación y estado de
    migración a Purview/Collibra.

    Args:
        case: Uno de los casos reales incluidos: rotulado_alimentos,
              cafe_sales_kaggle, bank_marketing_uci, medicamentos_openfda.
        lang: Idioma: "es" (default), "en" o "pt".
    """
    lang = _lang(lang)
    valid = samples.sample_keys()
    if case not in valid:
        return (f"Error: caso '{case}' no existe. "
                f"Casos disponibles: {', '.join(valid)}.")
    return deliverable.executive_summary_md(case, lang)


@mcp.tool(
    name="mvdg_search",
    annotations={"title": "Buscar en catálogo, diccionario y glosario",
                 "readOnlyHint": True, "destructiveHint": False,
                 "idempotentHint": True, "openWorldHint": False},
)
def mvdg_search(term: str, lang: str = "es") -> str:
    """Búsqueda por texto en catálogo, diccionario y glosario gobernados.

    Devuelve un JSON {"catalog": [...], "dictionary": [...],
    "glossary": [...]} con los registros cuya descripción, nombre o término
    contiene el texto (sin distinguir mayúsculas).

    Args:
        term: Texto a buscar (mínimo 2 caracteres), ej. "NDC", "PII", "ventas".
        lang: Idioma: "es" (default), "en" o "pt".
    """
    lang = _lang(lang)
    term = (term or "").strip()
    if len(term) < 2:
        return "Error: el término de búsqueda necesita al menos 2 caracteres."
    t = term.lower()

    def _hits(df: pd.DataFrame, cols: list[str]) -> list[dict]:
        if df.empty:
            return []
        mask = pd.Series(False, index=df.index)
        for c in cols:
            if c in df.columns:
                mask |= df[c].astype(str).str.lower().str.contains(
                    t, regex=False)
        return df[mask].to_dict(orient="records")

    cat = scope.combined_catalog(lang)
    dic = scope.combined_dictionary(lang)
    glo = scope.combined_glossary(lang)
    out = {
        "catalog": _hits(cat, ["dataset", "domain", "description", "owner"]),
        "dictionary": _hits(dic, ["dataset", "column", "description"]),
        "glossary": _hits(glo, [c for c in glo.columns]),
    }
    return json.dumps(out, ensure_ascii=False, default=str)


def main() -> None:
    """Arranque por stdio (el cliente MCP lanza este proceso)."""
    mcp.run()


if __name__ == "__main__":
    main()
