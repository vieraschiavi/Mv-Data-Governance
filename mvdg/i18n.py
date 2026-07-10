"""
MV Data Governance · Internacionalización (ES / EN / PT).

Uso:
    from mvdg.i18n import t, LANGS
    t("app_title", "es")  -> "MV Data Governance"

Todas las claves existen en los tres idiomas; ``tests/test_core.py`` verifica
la paridad para que nunca falte una traducción.
"""
from __future__ import annotations

LANGS = ["es", "en", "pt"]
LANG_NAMES = {"es": "Español", "en": "English", "pt": "Português"}
DEFAULT_LANG = "es"

_T: dict[str, dict[str, str]] = {
    # ------------------------------------------------------------------ app
    "app_title": {
        "es": "MV Data Governance",
        "en": "MV Data Governance",
        "pt": "MV Data Governance",
    },
    "app_tagline": {
        "es": "Gobierno de datos claro, medible y listo para BI",
        "en": "Clear, measurable, BI-ready data governance",
        "pt": "Governança de dados clara, mensurável e pronta para BI",
    },
    "language": {"es": "Idioma", "en": "Language", "pt": "Idioma"},
    "sidebar_help": {
        "es": "Plataforma de gobierno de datos: catálogo, calidad, linaje, "
              "glosario, políticas y exportación a cualquier BI.",
        "en": "Data governance platform: catalog, quality, lineage, glossary, "
              "policies and export to any BI tool.",
        "pt": "Plataforma de governança de dados: catálogo, qualidade, "
              "linhagem, glossário, políticas e exportação para qualquer BI.",
    },
    "demo_note": {
        "es": "Demo con datos 100% sintéticos — sin información real de clientes.",
        "en": "Demo with 100% synthetic data — no real customer information.",
        "pt": "Demo com dados 100% sintéticos — sem informações reais de clientes.",
    },
    # ----------------------------------------------------------------- tabs
    "tab_overview": {"es": "📊 Panorama", "en": "📊 Overview", "pt": "📊 Panorama"},
    "tab_catalog": {"es": "📚 Catálogo", "en": "📚 Catalog", "pt": "📚 Catálogo"},
    "tab_quality": {"es": "✅ Calidad", "en": "✅ Quality", "pt": "✅ Qualidade"},
    "tab_lineage": {"es": "🧬 Linaje", "en": "🧬 Lineage", "pt": "🧬 Linhagem"},
    "tab_glossary": {"es": "📖 Glosario", "en": "📖 Glossary", "pt": "📖 Glossário"},
    "tab_policies": {"es": "🛡️ Políticas", "en": "🛡️ Policies", "pt": "🛡️ Políticas"},
    "tab_profiler": {"es": "🔎 Mis datos", "en": "🔎 My data", "pt": "🔎 Meus dados"},
    "tab_bi": {"es": "📤 BI & API", "en": "📤 BI & API", "pt": "📤 BI & API"},
    # ------------------------------------------------------------- overview
    "kpi_datasets": {"es": "Datasets gobernados", "en": "Governed datasets", "pt": "Datasets governados"},
    "kpi_columns": {"es": "Columnas documentadas", "en": "Documented columns", "pt": "Colunas documentadas"},
    "kpi_quality": {"es": "Índice de calidad", "en": "Quality index", "pt": "Índice de qualidade"},
    "kpi_rules": {"es": "Reglas de calidad", "en": "Quality rules", "pt": "Regras de qualidade"},
    "kpi_rules_pass": {"es": "Reglas aprobadas", "en": "Rules passing", "pt": "Regras aprovadas"},
    "kpi_pii": {"es": "Columnas PII protegidas", "en": "Protected PII columns", "pt": "Colunas PII protegidas"},
    "kpi_stewards": {"es": "Data stewards", "en": "Data stewards", "pt": "Data stewards"},
    "kpi_terms": {"es": "Términos de negocio", "en": "Business terms", "pt": "Termos de negócio"},
    "ov_quality_by_domain": {
        "es": "Índice de calidad por dominio",
        "en": "Quality index by domain",
        "pt": "Índice de qualidade por domínio",
    },
    "ov_quality_by_dim": {
        "es": "Calidad por dimensión",
        "en": "Quality by dimension",
        "pt": "Qualidade por dimensão",
    },
    "ov_trend": {
        "es": "Evolución del índice de calidad (12 meses)",
        "en": "Quality index trend (12 months)",
        "pt": "Evolução do índice de qualidade (12 meses)",
    },
    "ov_issues": {
        "es": "Incidencias abiertas por severidad",
        "en": "Open issues by severity",
        "pt": "Ocorrências abertas por severidade",
    },
    # -------------------------------------------------------------- catalog
    "cat_intro": {
        "es": "Inventario único de datasets: dueño, steward, dominio, "
              "clasificación, frescura y calidad.",
        "en": "Single inventory of datasets: owner, steward, domain, "
              "classification, freshness and quality.",
        "pt": "Inventário único de datasets: dono, steward, domínio, "
              "classificação, atualidade e qualidade.",
    },
    "cat_search": {"es": "Buscar dataset…", "en": "Search dataset…", "pt": "Buscar dataset…"},
    "cat_domain": {"es": "Dominio", "en": "Domain", "pt": "Domínio"},
    "cat_all": {"es": "Todos", "en": "All", "pt": "Todos"},
    "cat_detail": {"es": "Diccionario de datos", "en": "Data dictionary", "pt": "Dicionário de dados"},
    "cat_pick": {"es": "Elegí un dataset", "en": "Pick a dataset", "pt": "Escolha um dataset"},
    "col_dataset": {"es": "Dataset", "en": "Dataset", "pt": "Dataset"},
    "col_description": {"es": "Descripción", "en": "Description", "pt": "Descrição"},
    "col_owner": {"es": "Dueño", "en": "Owner", "pt": "Dono"},
    "col_steward": {"es": "Steward", "en": "Steward", "pt": "Steward"},
    "col_classification": {"es": "Clasificación", "en": "Classification", "pt": "Classificação"},
    "col_freshness": {"es": "Frescura", "en": "Freshness", "pt": "Atualidade"},
    "col_rows": {"es": "Filas", "en": "Rows", "pt": "Linhas"},
    "col_quality": {"es": "Calidad", "en": "Quality", "pt": "Qualidade"},
    "col_column": {"es": "Columna", "en": "Column", "pt": "Coluna"},
    "col_type": {"es": "Tipo", "en": "Type", "pt": "Tipo"},
    "col_pii": {"es": "PII", "en": "PII", "pt": "PII"},
    "col_nullable": {"es": "Admite nulos", "en": "Nullable", "pt": "Aceita nulos"},
    "col_term": {"es": "Término de negocio", "en": "Business term", "pt": "Termo de negócio"},
    # -------------------------------------------------------------- quality
    "q_intro": {
        "es": "Motor de reglas sobre 6 dimensiones: completitud, unicidad, "
              "validez, consistencia, puntualidad y exactitud.",
        "en": "Rule engine across 6 dimensions: completeness, uniqueness, "
              "validity, consistency, timeliness and accuracy.",
        "pt": "Motor de regras em 6 dimensões: completude, unicidade, "
              "validade, consistência, pontualidade e exatidão.",
    },
    "q_run": {"es": "Ejecutar reglas ahora", "en": "Run rules now", "pt": "Executar regras agora"},
    "q_results": {"es": "Resultados por regla", "en": "Results per rule", "pt": "Resultados por regra"},
    "q_rule": {"es": "Regla", "en": "Rule", "pt": "Regra"},
    "q_dimension": {"es": "Dimensión", "en": "Dimension", "pt": "Dimensão"},
    "q_score": {"es": "Puntaje", "en": "Score", "pt": "Pontuação"},
    "q_status": {"es": "Estado", "en": "Status", "pt": "Status"},
    "q_pass": {"es": "✅ Aprobada", "en": "✅ Pass", "pt": "✅ Aprovada"},
    "q_warn": {"es": "🟡 Alerta", "en": "🟡 Warning", "pt": "🟡 Alerta"},
    "q_fail": {"es": "🔴 Falla", "en": "🔴 Fail", "pt": "🔴 Falha"},
    "q_threshold": {"es": "Umbral", "en": "Threshold", "pt": "Limite"},
    "q_affected": {"es": "Filas afectadas", "en": "Affected rows", "pt": "Linhas afetadas"},
    "q_heatmap": {
        "es": "Mapa de calor · dataset × dimensión",
        "en": "Heatmap · dataset × dimension",
        "pt": "Mapa de calor · dataset × dimensão",
    },
    "dim_completeness": {"es": "Completitud", "en": "Completeness", "pt": "Completude"},
    "dim_uniqueness": {"es": "Unicidad", "en": "Uniqueness", "pt": "Unicidade"},
    "dim_validity": {"es": "Validez", "en": "Validity", "pt": "Validade"},
    "dim_consistency": {"es": "Consistencia", "en": "Consistency", "pt": "Consistência"},
    "dim_timeliness": {"es": "Puntualidad", "en": "Timeliness", "pt": "Pontualidade"},
    "dim_accuracy": {"es": "Exactitud", "en": "Accuracy", "pt": "Exatidão"},
    # -------------------------------------------------------------- lineage
    "lin_intro": {
        "es": "Trazabilidad de punta a punta: de la fuente al tablero de BI. "
              "Seleccioná un nodo para ver de dónde viene y a dónde va.",
        "en": "End-to-end traceability: from source to BI dashboard. "
              "Select a node to see where data comes from and where it goes.",
        "pt": "Rastreabilidade de ponta a ponta: da fonte ao painel de BI. "
              "Selecione um nó para ver de onde vem e para onde vai.",
    },
    "lin_focus": {"es": "Enfocar activo", "en": "Focus asset", "pt": "Focar ativo"},
    "lin_upstream": {"es": "Aguas arriba", "en": "Upstream", "pt": "A montante"},
    "lin_downstream": {"es": "Aguas abajo", "en": "Downstream", "pt": "A jusante"},
    "lin_layer_source": {"es": "Fuentes", "en": "Sources", "pt": "Fontes"},
    "lin_layer_raw": {"es": "Capa cruda", "en": "Raw layer", "pt": "Camada bruta"},
    "lin_layer_curated": {"es": "Capa curada", "en": "Curated layer", "pt": "Camada curada"},
    "lin_layer_mart": {"es": "Data marts", "en": "Data marts", "pt": "Data marts"},
    "lin_layer_bi": {"es": "BI / Consumo", "en": "BI / Consumption", "pt": "BI / Consumo"},
    # ------------------------------------------------------------- glossary
    "g_intro": {
        "es": "Glosario de negocio: una definición oficial por término, con "
              "dueño y datasets vinculados — en los tres idiomas.",
        "en": "Business glossary: one official definition per term, with "
              "owner and linked datasets — in all three languages.",
        "pt": "Glossário de negócio: uma definição oficial por termo, com "
              "dono e datasets vinculados — nos três idiomas.",
    },
    "g_search": {"es": "Buscar término…", "en": "Search term…", "pt": "Buscar termo…"},
    "g_term": {"es": "Término", "en": "Term", "pt": "Termo"},
    "g_definition": {"es": "Definición", "en": "Definition", "pt": "Definição"},
    "g_linked": {"es": "Datasets vinculados", "en": "Linked datasets", "pt": "Datasets vinculados"},
    # ------------------------------------------------------------- policies
    "p_intro": {
        "es": "Políticas de datos y su cumplimiento verificado automáticamente "
              "contra el catálogo y las reglas de calidad.",
        "en": "Data policies with compliance automatically verified against "
              "the catalog and quality rules.",
        "pt": "Políticas de dados com conformidade verificada automaticamente "
              "contra o catálogo e as regras de qualidade.",
    },
    "p_policy": {"es": "Política", "en": "Policy", "pt": "Política"},
    "p_category": {"es": "Categoría", "en": "Category", "pt": "Categoria"},
    "p_compliance": {"es": "Cumplimiento", "en": "Compliance", "pt": "Conformidade"},
    "p_evidence": {"es": "Evidencia", "en": "Evidence", "pt": "Evidência"},
    "p_compliant": {"es": "✅ Cumple", "en": "✅ Compliant", "pt": "✅ Conforme"},
    "p_partial": {"es": "🟡 Parcial", "en": "🟡 Partial", "pt": "🟡 Parcial"},
    "p_noncompliant": {"es": "🔴 No cumple", "en": "🔴 Non-compliant", "pt": "🔴 Não conforme"},
    # ------------------------------------------------------------- profiler
    "pr_intro": {
        "es": "Subí tu propio archivo (CSV o Excel) y MV Data Governance lo "
              "perfila al instante: esquema, nulos, duplicados, calidad por "
              "columna y sugerencias de reglas.",
        "en": "Upload your own file (CSV or Excel) and MV Data Governance "
              "profiles it instantly: schema, nulls, duplicates, per-column "
              "quality and rule suggestions.",
        "pt": "Envie seu próprio arquivo (CSV ou Excel) e o MV Data Governance "
              "o perfila na hora: esquema, nulos, duplicados, qualidade por "
              "coluna e sugestões de regras.",
    },
    "pr_upload": {"es": "Archivo CSV o Excel", "en": "CSV or Excel file", "pt": "Arquivo CSV ou Excel"},
    "pr_overview": {"es": "Resumen del archivo", "en": "File summary", "pt": "Resumo do arquivo"},
    "pr_col_profile": {"es": "Perfil por columna", "en": "Per-column profile", "pt": "Perfil por coluna"},
    "pr_nulls": {"es": "% nulos", "en": "% nulls", "pt": "% nulos"},
    "pr_unique": {"es": "Valores únicos", "en": "Unique values", "pt": "Valores únicos"},
    "pr_dupes": {"es": "Filas duplicadas", "en": "Duplicate rows", "pt": "Linhas duplicadas"},
    "pr_suggestions": {"es": "Reglas sugeridas", "en": "Suggested rules", "pt": "Regras sugeridas"},
    "pr_pii_hint": {
        "es": "Posible PII detectada — revisá clasificación y enmascaramiento.",
        "en": "Possible PII detected — review classification and masking.",
        "pt": "Possível PII detectada — revise classificação e mascaramento.",
    },
    # ------------------------------------------------------------------- bi
    "bi_intro": {
        "es": "Todo lo que ves acá se puede consumir desde cualquier BI: "
              "Power BI, Tableau, Looker, MicroStrategy, Qlik, Excel… "
              "vía archivos (CSV/Excel/JSON/Parquet) o vía API REST.",
        "en": "Everything you see here can be consumed from any BI tool: "
              "Power BI, Tableau, Looker, MicroStrategy, Qlik, Excel… "
              "via files (CSV/Excel/JSON/Parquet) or via REST API.",
        "pt": "Tudo o que você vê aqui pode ser consumido de qualquer BI: "
              "Power BI, Tableau, Looker, MicroStrategy, Qlik, Excel… "
              "via arquivos (CSV/Excel/JSON/Parquet) ou via API REST.",
    },
    "bi_files": {"es": "Exportar archivos", "en": "Export files", "pt": "Exportar arquivos"},
    "bi_pick_table": {"es": "Tabla a exportar", "en": "Table to export", "pt": "Tabela para exportar"},
    "bi_download_csv": {"es": "⬇️ Descargar CSV", "en": "⬇️ Download CSV", "pt": "⬇️ Baixar CSV"},
    "bi_download_xlsx": {"es": "⬇️ Descargar Excel", "en": "⬇️ Download Excel", "pt": "⬇️ Baixar Excel"},
    "bi_download_json": {"es": "⬇️ Descargar JSON", "en": "⬇️ Download JSON", "pt": "⬇️ Baixar JSON"},
    "bi_download_parquet": {"es": "⬇️ Descargar Parquet", "en": "⬇️ Download Parquet", "pt": "⬇️ Baixar Parquet"},
    "bi_export_all": {
        "es": "📦 Exportar paquete BI completo (Excel multi-hoja)",
        "en": "📦 Export full BI bundle (multi-sheet Excel)",
        "pt": "📦 Exportar pacote BI completo (Excel multi-abas)",
    },
    "bi_api": {"es": "API REST para BI", "en": "REST API for BI", "pt": "API REST para BI"},
    "bi_api_help": {
        "es": "Levantá la API con `python -m api.main` (o el .bat) y conectá "
              "tu BI a estos endpoints (JSON o CSV con `?format=csv`):",
        "en": "Start the API with `python -m api.main` (or the .bat) and point "
              "your BI tool at these endpoints (JSON, or CSV with `?format=csv`):",
        "pt": "Inicie a API com `python -m api.main` (ou o .bat) e aponte seu "
              "BI para estes endpoints (JSON, ou CSV com `?format=csv`):",
    },
    "bi_guide": {
        "es": "Guía paso a paso por herramienta en `docs/BI_INTEGRATION.md`.",
        "en": "Step-by-step guide per tool in `docs/BI_INTEGRATION.md`.",
        "pt": "Guia passo a passo por ferramenta em `docs/BI_INTEGRATION.md`.",
    },
    # ------------------------------------------------------------- tables
    "tbl_catalog": {"es": "Catálogo de datasets", "en": "Dataset catalog", "pt": "Catálogo de datasets"},
    "tbl_dictionary": {"es": "Diccionario de columnas", "en": "Column dictionary", "pt": "Dicionário de colunas"},
    "tbl_quality": {"es": "Resultados de calidad", "en": "Quality results", "pt": "Resultados de qualidade"},
    "tbl_lineage": {"es": "Aristas de linaje", "en": "Lineage edges", "pt": "Arestas de linhagem"},
    "tbl_glossary": {"es": "Glosario", "en": "Glossary", "pt": "Glossário"},
    "tbl_policies": {"es": "Políticas", "en": "Policies", "pt": "Políticas"},
    "tbl_kpis": {"es": "KPIs de gobierno", "en": "Governance KPIs", "pt": "KPIs de governança"},
}


def t(key: str, lang: str = DEFAULT_LANG) -> str:
    """Traduce ``key`` al idioma ``lang`` (cae a español si falta)."""
    entry = _T.get(key)
    if entry is None:
        return key
    return entry.get(lang) or entry[DEFAULT_LANG]


def all_keys() -> list[str]:
    return list(_T.keys())
