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
    "tab_mdm": {"es": "🔗 MDM", "en": "🔗 MDM", "pt": "🔗 MDM"},
    "tab_quality": {"es": "✅ Calidad", "en": "✅ Quality", "pt": "✅ Qualidade"},
    "tab_lineage": {"es": "🧬 Linaje", "en": "🧬 Lineage", "pt": "🧬 Linhagem"},
    "tab_glossary": {"es": "📖 Glosario", "en": "📖 Glossary", "pt": "📖 Glossário"},
    "tab_curation": {"es": "🖊️ Curaduría", "en": "🖊️ Curation", "pt": "🖊️ Curadoria"},
    "tab_responsibles": {"es": "👥 Responsables", "en": "👥 Responsibles", "pt": "👥 Responsáveis"},
    "tab_policies": {"es": "🛡️ Políticas", "en": "🛡️ Policies", "pt": "🛡️ Políticas"},
    "tab_profiler": {"es": "🔎 Mis datos", "en": "🔎 My data", "pt": "🔎 Meus dados"},
    "tab_bi": {"es": "📤 BI & API", "en": "📤 BI & API", "pt": "📤 BI & API"},
    "tab_clients": {"es": "🏢 Empresas", "en": "🏢 Companies", "pt": "🏢 Empresas"},
    "tab_workspace": {"es": "📁 Proyecto", "en": "📁 Project", "pt": "📁 Projeto"},
    "tab_help": {"es": "❓ Ayuda", "en": "❓ Help", "pt": "❓ Ajuda"},
    "tab_lab": {"es": "🧪 Laboratorio", "en": "🧪 Lab", "pt": "🧪 Laboratório"},
    "tab_dmbok": {"es": "📘 Estándares", "en": "📘 Standards", "pt": "📘 Padrões"},
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
    "fix_title": {"es": "💡 Cómo corregir cada falla (sugerencia de la IA)", "en": "💡 How to fix each issue (AI suggestion)", "pt": "💡 Como corrigir cada falha (sugestão da IA)"},
    "fix_note": {
        "es": "Al lado de cada regla en warn o fail: causa probable, qué hacer con las filas ya cargadas y cómo evitar que vuelva a pasar. 100% local — no sale ningún dato de tu equipo para generar esto.",
        "en": "Next to every warn/fail rule: likely cause, what to do with the rows already loaded, and how to prevent it from happening again. 100% local — no data leaves your machine to generate this.",
        "pt": "Ao lado de cada regra em warn ou fail: causa provável, o que fazer com as linhas já carregadas e como evitar que aconteça de novo. 100% local — nenhum dado sai da sua máquina para gerar isto.",
    },
    "fix_none": {"es": "✅ Sin fallas que corregir: todas las reglas pasan.", "en": "✅ Nothing to fix: all rules pass.", "pt": "✅ Nada a corrigir: todas as regras passam."},
    "fix_root": {"es": "🔎 Causa probable", "en": "🔎 Likely cause", "pt": "🔎 Causa provável"},
    "fix_short": {"es": "🩹 Corto plazo (las filas ya cargadas)", "en": "🩹 Short term (rows already loaded)", "pt": "🩹 Curto prazo (linhas já carregadas)"},
    "fix_long": {"es": "🛠️ Prevención (que no vuelva a pasar)", "en": "🛠️ Prevention (so it doesn't happen again)", "pt": "🛠️ Prevenção (para não acontecer de novo)"},
    "fix_owner": {"es": "Asignar a", "en": "Assign to", "pt": "Atribuir a"},
    "fix_local_title": {"es": "Asistencia local (sin conexión)", "en": "Local assistance (offline)", "pt": "Assistência local (sem conexão)"},
    "fix_note_ai": {
        "es": "🤖 IA externa conectada: **{provider}** — vas a poder pedir, regla por regla, una sugerencia generada en vivo por ese modelo, además de la local. Solo se manda el metadato de la falla (dataset, columna, regla, cantidad de filas), nunca datos reales.",
        "en": "🤖 External AI connected: **{provider}** — you can request, rule by rule, a suggestion generated live by that model, in addition to the local one. Only the failure's metadata is sent (dataset, column, rule, row count), never real data.",
        "pt": "🤖 IA externa conectada: **{provider}** — você vai poder pedir, regra por regra, uma sugestão gerada ao vivo por esse modelo, além da local. Só é enviado o metadado da falha (dataset, coluna, regra, quantidade de linhas), nunca dados reais.",
    },
    "fix_ai_button": {"es": "✨ Pedir sugerencia a {provider}", "en": "✨ Ask {provider} for a suggestion", "pt": "✨ Pedir sugestão a {provider}"},
    "fix_ai_loading": {"es": "Consultando…", "en": "Asking…", "pt": "Consultando…"},
    "fix_ai_title": {"es": "Sugerencia generada por {provider}", "en": "Suggestion generated by {provider}", "pt": "Sugestão gerada por {provider}"},
    "fix_ai_error": {
        "es": "No se pudo obtener una respuesta de la IA externa (sin conexión, key inválida o error del servicio). Usá la sugerencia local de arriba mientras tanto.",
        "en": "Couldn't get a response from the external AI (offline, invalid key, or service error). Use the local suggestion above in the meantime.",
        "pt": "Não foi possível obter uma resposta da IA externa (sem conexão, chave inválida ou erro do serviço). Use a sugestão local acima enquanto isso.",
    },
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
    # ------------------------------------------------------------- curation
    "cu_intro": {
        "es": "Ninguna definición arranca en blanco y ninguna queda sin responsable: "
              "todo lo que ves (glosario, catálogo, diccionario) viene pre-establecido "
              "por IA como recomendación inicial, y acá el Data Owner o Data Steward "
              "lo valida tal cual o lo modifica con su texto oficial — con nombre, "
              "cargo y fecha, guardado en tu equipo. Es el mismo flujo de curaduría "
              "que usan Purview y Collibra.",
        "en": "No definition starts blank and none is left without a responsible person: "
              "everything you see (glossary, catalog, dictionary) comes pre-established "
              "by AI as an initial recommendation, and here the Data Owner or Data Steward "
              "validates it as-is or replaces it with their official text — with name, "
              "role and date, stored on your machine. It's the same curation flow "
              "Purview and Collibra use.",
        "pt": "Nenhuma definição começa em branco e nenhuma fica sem responsável: "
              "tudo o que você vê (glossário, catálogo, dicionário) vem pré-estabelecido "
              "por IA como recomendação inicial, e aqui o Data Owner ou Data Steward "
              "valida como está ou substitui pelo seu texto oficial — com nome, "
              "cargo e data, salvo no seu equipamento. É o mesmo fluxo de curadoria "
              "que Purview e Collibra usam.",
    },
    "cu_total": {"es": "Definiciones", "en": "Definitions", "pt": "Definições"},
    "cu_pending": {"es": "Sugeridas por IA (sin revisar)", "en": "AI-suggested (unreviewed)", "pt": "Sugeridas por IA (sem revisão)"},
    "cu_validated": {"es": "Validadas", "en": "Validated", "pt": "Validadas"},
    "cu_modified": {"es": "Modificadas", "en": "Modified", "pt": "Modificadas"},
    "cu_progress": {"es": "{pct}% revisado por un responsable", "en": "{pct}% reviewed by a responsible person", "pt": "{pct}% revisado por um responsável"},
    "cu_kind_glossary": {"es": "Término de glosario", "en": "Glossary term", "pt": "Termo de glossário"},
    "cu_kind_catalog": {"es": "Descripción de dataset", "en": "Dataset description", "pt": "Descrição de dataset"},
    "cu_kind_column": {"es": "Descripción de columna", "en": "Column description", "pt": "Descrição de coluna"},
    "cu_st_ai": {"es": "🤖 Sugerido por IA", "en": "🤖 AI-suggested", "pt": "🤖 Sugerido por IA"},
    "cu_st_val": {"es": "✅ Validado", "en": "✅ Validated", "pt": "✅ Validado"},
    "cu_st_mod": {"es": "🖊️ Modificado", "en": "🖊️ Modified", "pt": "🖊️ Modificado"},
    "cu_filter_kind": {"es": "Tipo", "en": "Kind", "pt": "Tipo"},
    "cu_filter_dataset": {"es": "Dataset", "en": "Dataset", "pt": "Dataset"},
    "cu_filter_status": {"es": "Estado", "en": "Status", "pt": "Status"},
    "cu_all": {"es": "(todos)", "en": "(all)", "pt": "(todos)"},
    "cu_col_kind": {"es": "Tipo", "en": "Kind", "pt": "Tipo"},
    "cu_col_item": {"es": "Ítem", "en": "Item", "pt": "Item"},
    "cu_col_status": {"es": "Estado", "en": "Status", "pt": "Status"},
    "cu_col_text": {"es": "Definición vigente", "en": "Current definition", "pt": "Definição vigente"},
    "cu_col_resp": {"es": "Responsable", "en": "Responsible", "pt": "Responsável"},
    "cu_col_role": {"es": "Cargo", "en": "Role", "pt": "Cargo"},
    "cu_col_date": {"es": "Fecha", "en": "Date", "pt": "Data"},
    "cu_review_one": {"es": "Revisar una definición", "en": "Review a definition", "pt": "Revisar uma definição"},
    "cu_pick": {"es": "Definición a revisar", "en": "Definition to review", "pt": "Definição a revisar"},
    "cu_proposed": {"es": "Texto pre-establecido (recomendación IA):", "en": "Pre-established text (AI recommendation):", "pt": "Texto pré-estabelecido (recomendação IA):"},
    "cu_already": {
        "es": "{status} por {name} ({role}) el {date}.",
        "en": "{status} by {name} ({role}) on {date}.",
        "pt": "{status} por {name} ({role}) em {date}.",
    },
    "cu_official_text": {"es": "Texto oficial del responsable", "en": "Responsible's official text", "pt": "Texto oficial do responsável"},
    "cu_action": {"es": "¿Qué hace el responsable?", "en": "What does the responsible person do?", "pt": "O que o responsável faz?"},
    "cu_action_validar": {"es": "✅ Validar tal cual", "en": "✅ Validate as-is", "pt": "✅ Validar como está"},
    "cu_action_modificar": {"es": "🖊️ Modificar el texto", "en": "🖊️ Modify the text", "pt": "🖊️ Modificar o texto"},
    "cu_new_text": {"es": "Texto oficial (reemplaza al sugerido)", "en": "Official text (replaces the suggested one)", "pt": "Texto oficial (substitui o sugerido)"},
    "cu_resp_name": {"es": "Nombre del responsable", "en": "Responsible person's name", "pt": "Nome do responsável"},
    "cu_resp_role": {"es": "Cargo (ej. Data Owner de Ventas)", "en": "Role (e.g. Sales Data Owner)", "pt": "Cargo (ex. Data Owner de Vendas)"},
    "cu_notes": {"es": "Notas (opcional)", "en": "Notes (optional)", "pt": "Notas (opcional)"},
    "cu_save": {"es": "💾 Guardar veredicto", "en": "💾 Save verdict", "pt": "💾 Salvar veredito"},
    "cu_saved": {"es": "Veredicto guardado.", "en": "Verdict saved.", "pt": "Veredito salvo."},
    "cu_need_name": {"es": "Falta el nombre del responsable.", "en": "The responsible person's name is missing.", "pt": "Falta o nome do responsável."},
    "cu_reset": {"es": "↩️ Volver a la sugerencia IA", "en": "↩️ Back to the AI suggestion", "pt": "↩️ Voltar à sugestão IA"},
    "cu_reset_ok": {"es": "Definición devuelta al estado sugerido por IA.", "en": "Definition returned to AI-suggested state.", "pt": "Definição devolvida ao estado sugerido por IA."},
    "cu_local_note": {
        "es": "Los veredictos se guardan solo en tu equipo (~/.mv_data_governance/curaduria.json) y persisten entre sesiones.",
        "en": "Verdicts are stored only on your machine (~/.mv_data_governance/curaduria.json) and persist between sessions.",
        "pt": "Os vereditos são salvos apenas no seu equipamento (~/.mv_data_governance/curaduria.json) e persistem entre sessões.",
    },
    # ---------------------------------------------------- governance insights
    "gi_title": {"es": "🏛️ Estado del gobierno (estilo Purview, 100% local)", "en": "🏛️ Governance estate (Purview-style, 100% local)", "pt": "🏛️ Estado da governança (estilo Purview, 100% local)"},
    "gi_caption": {
        "es": "No mide la calidad de los datos — mide la salud del GOBIERNO sobre esos datos: cuánto del patrimonio tiene responsable con nombre, clasificación, reglas y definiciones revisadas. Mejora a medida que usás las pestañas 👥 Responsables y 🖊️ Curaduría.",
        "en": "It doesn't measure data quality — it measures the health of the GOVERNANCE over that data: how much of the estate has a named responsible, classification, rules and reviewed definitions. It improves as you use the 👥 Responsibles and 🖊️ Curation tabs.",
        "pt": "Não mede a qualidade dos dados — mede a saúde da GOVERNANÇA sobre esses dados: quanto do patrimônio tem responsável com nome, classificação, regras e definições revisadas. Melhora à medida que você usa as abas 👥 Responsáveis e 🖊️ Curadoria.",
    },
    "gi_index": {"es": "Índice de gobierno", "en": "Governance index", "pt": "Índice de governança"},
    "gi_owner": {"es": "Con owner nombrado", "en": "Named owner", "pt": "Com owner nomeado"},
    "gi_steward": {"es": "Con steward nombrado", "en": "Named steward", "pt": "Com steward nomeado"},
    "gi_classified": {"es": "Clasificados", "en": "Classified", "pt": "Classificados"},
    "gi_rules": {"es": "Con reglas de calidad", "en": "With quality rules", "pt": "Com regras de qualidade"},
    "gi_curation": {"es": "Definiciones revisadas", "en": "Definitions reviewed", "pt": "Definições revisadas"},
    "gi_detail": {"es": "Detalle por dataset", "en": "Per-dataset detail", "pt": "Detalhe por dataset"},
    "gi_col_owner": {"es": "Owner nombrado", "en": "Named owner", "pt": "Owner nomeado"},
    "gi_col_steward": {"es": "Steward nombrado", "en": "Named steward", "pt": "Steward nomeado"},
    "gi_col_classified": {"es": "Clasificado", "en": "Classified", "pt": "Classificado"},
    "gi_col_rules": {"es": "Reglas", "en": "Rules", "pt": "Regras"},
    "gi_col_curation": {"es": "% curado", "en": "% curated", "pt": "% curado"},
    "gi_how_to_improve": {
        "es": "¿Cómo subir el índice? Asigná personas con nombre y cargo en 👥 Responsables (los datasets de ejemplo arrancan con equipos genéricos a propósito) y validá definiciones en 🖊️ Curaduría.",
        "en": "How to raise the index? Assign named people in 👥 Responsibles (the sample datasets start with generic teams on purpose) and validate definitions in 🖊️ Curation.",
        "pt": "Como subir o índice? Atribua pessoas com nome e cargo em 👥 Responsáveis (os datasets de exemplo começam com equipes genéricas de propósito) e valide definições em 🖊️ Curadoria.",
    },
    # --------------------------------------------------------- responsibles
    "rs_intro": {
        "es": "Cargá el organigrama de la empresa (Excel/CSV, una tabla traída por "
              "conexión SQL, o una foto) y el programa completa automáticamente, por "
              "defecto, el Data Owner y el Data Steward de cada dataset — con nombre y "
              "cargo — según el área que mejor matchea cada dominio y la jerarquía de "
              "los cargos. Después editás lo que quieras y lo guardás: la sugerencia "
              "nunca es la palabra final.",
        "en": "Load the company org chart (Excel/CSV, a table brought via SQL "
              "connection, or a photo) and the program automatically fills in, by "
              "default, each dataset's Data Owner and Data Steward — with name and "
              "role — based on the area that best matches each domain and the "
              "seniority of the roles. Then edit whatever you want and save: the "
              "suggestion is never the final word.",
        "pt": "Carregue o organograma da empresa (Excel/CSV, uma tabela trazida por "
              "conexão SQL, ou uma foto) e o programa preenche automaticamente, por "
              "padrão, o Data Owner e o Data Steward de cada dataset — com nome e "
              "cargo — conforme a área que melhor combina com cada domínio e a "
              "hierarquia dos cargos. Depois edite o que quiser e salve: a sugestão "
              "nunca é a palavra final.",
    },
    "rs_source": {"es": "¿De dónde viene el organigrama?", "en": "Where does the org chart come from?", "pt": "De onde vem o organograma?"},
    "rs_src_file": {"es": "📄 Excel / CSV", "en": "📄 Excel / CSV", "pt": "📄 Excel / CSV"},
    "rs_src_photo": {"es": "📷 Foto (IA externa)", "en": "📷 Photo (external AI)", "pt": "📷 Foto (IA externa)"},
    "rs_src_saved": {"es": "💾 Guardado", "en": "💾 Saved", "pt": "💾 Salvo"},
    "rs_upload": {"es": "Subí el organigrama (.xlsx/.csv)", "en": "Upload the org chart (.xlsx/.csv)", "pt": "Envie o organograma (.xlsx/.csv)"},
    "rs_upload_hint": {
        "es": "Alcanza con columnas de nombre, cargo y área (jefe y email son opcionales) — se detectan por el encabezado, en cualquier orden e idioma. ¿La tabla está en una base? Traela por conexión SQL en 🔎 Mis datos, exportala y subila acá.",
        "en": "Columns for name, role and area are enough (manager and email are optional) — detected by header, in any order and language. Is the table in a database? Bring it via SQL connection in 🔎 My data, export it and upload it here.",
        "pt": "Bastam colunas de nome, cargo e área (chefe e email são opcionais) — detectadas pelo cabeçalho, em qualquer ordem e idioma. A tabela está num banco? Traga-a por conexão SQL em 🔎 Meus dados, exporte e envie aqui.",
    },
    "rs_parsed": {"es": "Organigrama leído: {n} personas.", "en": "Org chart read: {n} people.", "pt": "Organograma lido: {n} pessoas."},
    "rs_photo_needs_ai": {
        "es": "Leer una foto requiere la IA externa opcional (tu propia API key de Claude/ChatGPT/Gemini — ver docs/IA_EXTERNA.md). Sin eso, usá el camino Excel/CSV, que es 100% local.",
        "en": "Reading a photo requires the optional external AI (your own Claude/ChatGPT/Gemini API key — see docs/IA_EXTERNA.md). Without it, use the Excel/CSV path, which is 100% local.",
        "pt": "Ler uma foto requer a IA externa opcional (sua própria API key de Claude/ChatGPT/Gemini — veja docs/IA_EXTERNA.md). Sem isso, use o caminho Excel/CSV, que é 100% local.",
    },
    "rs_photo_disclosure": {
        "es": "⚠️ La foto se envía a {provider} para extraer el texto — es la única función del programa que manda una imagen afuera, y solo cuando vos apretás el botón. Si el organigrama es confidencial, usá el camino Excel/CSV (100% local).",
        "en": "⚠️ The photo is sent to {provider} to extract the text — it's the only feature in the program that sends an image out, and only when you press the button. If the org chart is confidential, use the Excel/CSV path (100% local).",
        "pt": "⚠️ A foto é enviada a {provider} para extrair o texto — é a única função do programa que envia uma imagem para fora, e somente quando você aperta o botão. Se o organograma é confidencial, use o caminho Excel/CSV (100% local).",
    },
    "rs_upload_photo": {"es": "Subí la foto del organigrama", "en": "Upload the org chart photo", "pt": "Envie a foto do organograma"},
    "rs_extract_photo": {"es": "🔍 Extraer personas de la foto", "en": "🔍 Extract people from the photo", "pt": "🔍 Extrair pessoas da foto"},
    "rs_photo_failed": {
        "es": "No se pudieron extraer personas de la imagen (falló la llamada o la IA no encontró un organigrama legible).",
        "en": "Couldn't extract people from the image (the call failed or the AI found no readable org chart).",
        "pt": "Não foi possível extrair pessoas da imagem (a chamada falhou ou a IA não encontrou um organograma legível).",
    },
    "rs_none_saved": {"es": "Todavía no hay un organigrama guardado — cargalo por archivo o foto.", "en": "No org chart saved yet — load it from a file or photo.", "pt": "Ainda não há organograma salvo — carregue por arquivo ou foto."},
    "rs_people": {"es": "Personas del organigrama", "en": "People in the org chart", "pt": "Pessoas do organograma"},
    "rs_people_edit_hint": {"es": "Editá celdas, agregá o borrá filas antes de guardar.", "en": "Edit cells, add or remove rows before saving.", "pt": "Edite células, adicione ou remova linhas antes de salvar."},
    "rs_save_org": {"es": "💾 Guardar organigrama", "en": "💾 Save org chart", "pt": "💾 Salvar organograma"},
    "rs_org_saved": {"es": "Organigrama guardado.", "en": "Org chart saved.", "pt": "Organograma salvo."},
    "rs_assignments": {"es": "Responsables por dataset (nombre y cargo)", "en": "Responsibles per dataset (name and role)", "pt": "Responsáveis por dataset (nome e cargo)"},
    "rs_suggest": {"es": "🪄 Completar responsables por defecto", "en": "🪄 Fill in default responsibles", "pt": "🪄 Preencher responsáveis por padrão"},
    "rs_asg_hint": {
        "es": "Sugerido por área y jerarquía (columna «match» dice qué se usó). Editá los nombres/cargos que haga falta — al guardar, esas filas quedan marcadas «editado».",
        "en": "Suggested by area and seniority (the “match” column says what was used). Edit any names/roles as needed — on save, those rows are marked “edited”.",
        "pt": "Sugerido por área e hierarquia (a coluna «match» diz o que foi usado). Edite os nomes/cargos que precisar — ao salvar, essas linhas ficam marcadas «editado».",
    },
    "rs_owner_name": {"es": "Data Owner", "en": "Data Owner", "pt": "Data Owner"},
    "rs_owner_role": {"es": "Cargo del owner", "en": "Owner's role", "pt": "Cargo do owner"},
    "rs_steward_name": {"es": "Data Steward", "en": "Data Steward", "pt": "Data Steward"},
    "rs_steward_role": {"es": "Cargo del steward", "en": "Steward's role", "pt": "Cargo do steward"},
    "rs_match": {"es": "Match", "en": "Match", "pt": "Match"},
    "rs_estado": {"es": "Estado", "en": "Status", "pt": "Status"},
    "rs_save_asg": {"es": "💾 Guardar responsables", "en": "💾 Save responsibles", "pt": "💾 Salvar responsáveis"},
    "rs_asg_saved": {"es": "Responsables guardados.", "en": "Responsibles saved.", "pt": "Responsáveis salvos."},
    "rs_local_note": {
        "es": "El organigrama y los responsables se guardan solo en tu equipo (organigrama.json / responsables.json) y persisten entre sesiones.",
        "en": "The org chart and responsibles are stored only on your machine (organigrama.json / responsables.json) and persist between sessions.",
        "pt": "O organograma e os responsáveis são salvos apenas no seu equipamento (organigrama.json / responsables.json) e persistem entre sessões.",
    },
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
        "es": "Subí un archivo (CSV o Excel) o conectate directo a tu base de "
              "datos, y MV Data Governance lo perfila al instante: esquema, "
              "nulos, duplicados, calidad por columna y sugerencias de reglas.",
        "en": "Upload a file (CSV or Excel) or connect directly to your "
              "database, and MV Data Governance profiles it instantly: schema, "
              "nulls, duplicates, per-column quality and rule suggestions.",
        "pt": "Envie um arquivo (CSV ou Excel) ou conecte-se direto ao seu "
              "banco de dados, e o MV Data Governance o perfila na hora: "
              "esquema, nulos, duplicados, qualidade por coluna e sugestões.",
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
    "pr_source": {"es": "Fuente de datos", "en": "Data source", "pt": "Fonte de dados"},
    "pr_src_file": {"es": "📄 Archivo (CSV/Excel)", "en": "📄 File (CSV/Excel)", "pt": "📄 Arquivo (CSV/Excel)"},
    "pr_src_db": {"es": "🗄️ Base de datos", "en": "🗄️ Database", "pt": "🗄️ Banco de dados"},
    "pr_src_example": {"es": "🧪 Dataset de ejemplo (real)", "en": "🧪 Example dataset (real)", "pt": "🧪 Dataset de exemplo (real)"},
    "pr_example_missing": {
        "es": "No se encontró el dataset de ejemplo en el paquete.",
        "en": "The example dataset was not found in the package.",
        "pt": "O dataset de exemplo não foi encontrado no pacote.",
    },
    "pr_example_pick": {"es": "Elegí el dataset de ejemplo", "en": "Pick the example dataset", "pt": "Escolha o dataset de exemplo"},
    "pr_example_intro": {
        "es": "De punta a punta, no solo perfilado: ficha con dueño y steward, reglas de calidad con "
              "umbral y estado, definiciones de negocio, y exportación/API lista para Power BI o Tableau.",
        "en": "End to end, not just profiling: a card with owner and steward, quality rules with "
              "threshold and status, business definitions, and export/API ready for Power BI or Tableau.",
        "pt": "De ponta a ponta, não só perfilamento: ficha com dono e steward, regras de qualidade com "
              "limiar e status, definições de negócio, e exportação/API pronta para Power BI ou Tableau.",
    },
    "pr_example_card": {"es": "Ficha del dataset", "en": "Dataset card", "pt": "Ficha do dataset"},
    "pr_example_source_lbl": {"es": "Fuente", "en": "Source", "pt": "Fonte"},
    "pr_example_license_lbl": {"es": "Licencia", "en": "License", "pt": "Licença"},
    "pr_example_metrics": {"es": "Métricas de calidad (reglas con umbral)", "en": "Quality metrics (rules with threshold)", "pt": "Métricas de qualidade (regras com limiar)"},
    "pr_example_glossary_title": {"es": "Definiciones de negocio", "en": "Business definitions", "pt": "Definições de negócio"},
    "pr_example_bi_title": {"es": "Exportar y conectar a BI", "en": "Export and connect to BI", "pt": "Exportar e conectar ao BI"},
    "pr_example_bi_note": {
        "es": "Mismos datos y resultados de calidad, listos para Power BI (Obtener datos → Web), Tableau "
              "(Conector de datos web) o cualquier BI que lea CSV/Excel/JSON/Parquet o una API REST.",
        "en": "Same data and quality results, ready for Power BI (Get Data → Web), Tableau "
              "(Web Data Connector), or any BI tool that reads CSV/Excel/JSON/Parquet or a REST API.",
        "pt": "Mesmos dados e resultados de qualidade, prontos para Power BI (Obter dados → Web), Tableau "
              "(Conector de dados web) ou qualquer BI que leia CSV/Excel/JSON/Parquet ou uma API REST.",
    },
    "pr_example_generic_toggle": {
        "es": "También: perfilado genérico (sin reglas configuradas), para comparar",
        "en": "Also: generic profiling (no configured rules), for comparison",
        "pt": "Também: perfilamento genérico (sem regras configuradas), para comparar",
    },
    "pr_example_data": {"es": "Datos", "en": "Data", "pt": "Dados"},

    # ------------------------------------------------------------- connectors
    "db_intro": {
        "es": "Conectate directo a tu base de datos: 5 motores SQL clásicos "
              "(PostgreSQL, MySQL, SQL Server, Oracle, SQLite) o un data "
              "warehouse/lake de nube (Snowflake, BigQuery, Databricks, Azure "
              "Synapse). Cargás las credenciales, las guardás y traés tus "
              "tablas al gobierno — igual que un CSV.",
        "en": "Connect directly to your database: 5 classic SQL engines "
              "(PostgreSQL, MySQL, SQL Server, Oracle, SQLite) or a cloud data "
              "warehouse/lake (Snowflake, BigQuery, Databricks, Azure "
              "Synapse). Enter the credentials, save them and bring your "
              "tables into governance — just like a CSV.",
        "pt": "Conecte-se direto ao seu banco de dados: 5 motores SQL "
              "clássicos (PostgreSQL, MySQL, SQL Server, Oracle, SQLite) ou "
              "um data warehouse/lake de nuvem (Snowflake, BigQuery, "
              "Databricks, Azure Synapse). Informe as credenciais, salve-as "
              "e traga suas tabelas para a governança — como um CSV.",
    },
    "db_saved_conns": {"es": "Conexiones guardadas", "en": "Saved connections", "pt": "Conexões salvas"},
    "db_new_conn": {"es": "(nueva conexión)", "en": "(new connection)", "pt": "(nova conexão)"},
    "db_engine": {"es": "Motor", "en": "Engine", "pt": "Motor"},
    "db_name": {"es": "Nombre de la conexión", "en": "Connection name", "pt": "Nome da conexão"},
    "db_host": {"es": "Servidor / host", "en": "Server / host", "pt": "Servidor / host"},
    "db_port": {"es": "Puerto", "en": "Port", "pt": "Porta"},
    "db_database": {"es": "Base de datos", "en": "Database", "pt": "Banco de dados"},
    "db_sqlite_path": {"es": "Ruta del archivo .db/.sqlite", "en": "Path to .db/.sqlite file", "pt": "Caminho do arquivo .db/.sqlite"},
    "db_user": {"es": "Usuario", "en": "User", "pt": "Usuário"},
    "db_password": {"es": "Contraseña", "en": "Password", "pt": "Senha"},
    "db_save_pwd": {"es": "Guardar contraseña (local, ofuscada)", "en": "Save password (local, obfuscated)", "pt": "Salvar senha (local, ofuscada)"},
    "db_test": {"es": "🔌 Probar conexión", "en": "🔌 Test connection", "pt": "🔌 Testar conexão"},
    "db_save": {"es": "💾 Guardar conexión", "en": "💾 Save connection", "pt": "💾 Salvar conexão"},
    "db_saved_ok": {"es": "Conexión guardada.", "en": "Connection saved.", "pt": "Conexão salva."},
    "db_delete": {"es": "🗑️ Eliminar conexión", "en": "🗑️ Delete connection", "pt": "🗑️ Excluir conexão"},
    "db_need_name": {"es": "Poné un nombre para la conexión.", "en": "Enter a name for the connection.", "pt": "Informe um nome para a conexão."},
    "db_pick_table": {"es": "Tabla a traer", "en": "Table to load", "pt": "Tabela para trazer"},
    "db_limit": {"es": "Máximo de filas", "en": "Max rows", "pt": "Máximo de linhas"},
    "db_load": {"es": "⬇️ Traer y perfilar tabla", "en": "⬇️ Load and profile table", "pt": "⬇️ Trazer e perfilar tabela"},
    "db_query": {"es": "…o una consulta SQL (SELECT)", "en": "…or a SQL query (SELECT)", "pt": "…ou uma consulta SQL (SELECT)"},
    "db_run_query": {"es": "▶️ Ejecutar consulta y perfilar", "en": "▶️ Run query and profile", "pt": "▶️ Executar consulta e perfilar"},
    "db_connect_first": {"es": "Probá y guardá una conexión para ver sus tablas.", "en": "Test and save a connection to see its tables.", "pt": "Teste e salve uma conexão para ver suas tabelas."},
    "db_local_note": {
        "es": "Las conexiones se guardan solo en tu equipo. La contraseña queda "
              "ofuscada; podés no guardarla y escribirla al conectar.",
        "en": "Connections are stored only on your machine. The password is "
              "obfuscated; you can choose not to save it and type it on connect.",
        "pt": "As conexões são salvas apenas no seu equipamento. A senha fica "
              "ofuscada; você pode não salvá-la e digitá-la ao conectar.",
    },
    "db_no_driver": {
        "es": "Falta el driver de este motor. Instalalo con: pip install {pip}",
        "en": "The driver for this engine is missing. Install it with: pip install {pip}",
        "pt": "Falta o driver deste motor. Instale com: pip install {pip}",
    },
    "db_cloud_no_port": {
        "es": "Sin puerto (ver parámetros abajo)",
        "en": "No port (see parameters below)",
        "pt": "Sem porta (veja parâmetros abaixo)",
    },
    "db_extra_params": {
        "es": "Parámetros propios del motor (JSON)",
        "en": "Engine-specific parameters (JSON)",
        "pt": "Parâmetros próprios do motor (JSON)",
    },
    "db_extra_hint": {
        "es": "Snowflake/BigQuery/Databricks no usan servidor+puerto — acá van sus "
              "parámetros propios en JSON. Ejemplo para este motor: {example}",
        "en": "Snowflake/BigQuery/Databricks don't use host+port — enter their own "
              "parameters here as JSON. Example for this engine: {example}",
        "pt": "Snowflake/BigQuery/Databricks não usam servidor+porta — informe aqui "
              "seus parâmetros próprios em JSON. Exemplo para este motor: {example}",
    },
    "db_extra_invalid_json": {
        "es": "El JSON de parámetros no es válido — corregilo antes de probar o guardar.",
        "en": "The parameters JSON is invalid — fix it before testing or saving.",
        "pt": "O JSON de parâmetros é inválido — corrija antes de testar ou salvar.",
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
        "es": "Levantá la API con `python -m bi_api.main` (o el .bat) y conectá "
              "tu BI a estos endpoints (JSON o CSV con `?format=csv`):",
        "en": "Start the API with `python -m bi_api.main` (or the .bat) and point "
              "your BI tool at these endpoints (JSON, or CSV with `?format=csv`):",
        "pt": "Inicie a API com `python -m bi_api.main` (ou o .bat) e aponte seu "
              "BI para estes endpoints (JSON, ou CSV com `?format=csv`):",
    },
    "bi_guide": {
        "es": "Guía paso a paso por herramienta en `docs/BI_INTEGRATION.md`.",
        "en": "Step-by-step guide per tool in `docs/BI_INTEGRATION.md`.",
        "pt": "Guia passo a passo por ferramenta em `docs/BI_INTEGRATION.md`.",
    },
    # -------------------------------------------------------- migración (mig)
    "mig_title": {"es": "🔀 Migración a Purview / Collibra", "en": "🔀 Migration to Purview / Collibra", "pt": "🔀 Migração para Purview / Collibra"},
    "mig_intro": {
        "es": "Empujá el catálogo, el diccionario y el glosario ya gobernados acá "
              "hacia Purview o Collibra por API. Es un **acelerador, no un "
              "reemplazo**: el programa hace el trabajo pesado (perfilar, reglas de "
              "calidad, glosario, PII, curaduría con responsable) y al final "
              "empuja el resultado — Purview/Collibra siguen siendo la plataforma "
              "que tu equipo audita y usa después. El estado Draft/Approved de "
              "cada término sale de la pestaña 🖊️ Curaduría real, no se inventa.",
        "en": "Push the catalog, dictionary and glossary already governed here "
              "into Purview or Collibra via API. It's an **accelerator, not a "
              "replacement**: the program does the heavy lifting (profiling, "
              "quality rules, glossary, PII, curation with a responsible person) "
              "and pushes the result at the end — Purview/Collibra remain the "
              "platform your team audits and uses afterward. Each term's Draft/"
              "Approved status comes from the real 🖊️ Curation tab, not invented.",
        "pt": "Empurre o catálogo, o dicionário e o glossário já governados aqui "
              "para o Purview ou Collibra via API. É um **acelerador, não um "
              "substituto**: o programa faz o trabalho pesado (perfilamento, "
              "regras de qualidade, glossário, PII, curadoria com responsável) e "
              "no final empurra o resultado — Purview/Collibra continuam sendo a "
              "plataforma que sua equipe audita e usa depois. O status Draft/"
              "Approved de cada termo vem da aba 🖊️ Curadoria real, não é inventado.",
    },
    "mig_target": {"es": "Destino", "en": "Target", "pt": "Destino"},
    "mig_purview_env": {
        "es": "Sin configurar — el preview funciona igual, sin credenciales. Para empujar de verdad, cargá `PURVIEW_TENANT_ID`, `PURVIEW_CLIENT_ID`, `PURVIEW_CLIENT_SECRET`, `PURVIEW_ACCOUNT_NAME` (ver `docs/PURVIEW_COLLIBRA.md`).",
        "en": "Not configured — the preview still works, no credentials needed. To actually push, set `PURVIEW_TENANT_ID`, `PURVIEW_CLIENT_ID`, `PURVIEW_CLIENT_SECRET`, `PURVIEW_ACCOUNT_NAME` (see `docs/PURVIEW_COLLIBRA.md`).",
        "pt": "Não configurado — o preview funciona igual, sem credenciais. Para empurrar de verdade, configure `PURVIEW_TENANT_ID`, `PURVIEW_CLIENT_ID`, `PURVIEW_CLIENT_SECRET`, `PURVIEW_ACCOUNT_NAME` (veja `docs/PURVIEW_COLLIBRA.md`).",
    },
    "mig_collibra_env": {
        "es": "Sin configurar — el preview funciona igual, sin credenciales. Para empujar de verdad, cargá `COLLIBRA_BASE_URL`, `COLLIBRA_USERNAME`, `COLLIBRA_PASSWORD`, `COLLIBRA_DOMAIN_ID`, `COLLIBRA_TABLE_TYPE_ID`, `COLLIBRA_COLUMN_TYPE_ID` (ver `docs/PURVIEW_COLLIBRA.md`).",
        "en": "Not configured — the preview still works, no credentials needed. To actually push, set `COLLIBRA_BASE_URL`, `COLLIBRA_USERNAME`, `COLLIBRA_PASSWORD`, `COLLIBRA_DOMAIN_ID`, `COLLIBRA_TABLE_TYPE_ID`, `COLLIBRA_COLUMN_TYPE_ID` (see `docs/PURVIEW_COLLIBRA.md`).",
        "pt": "Não configurado — o preview funciona igual, sem credenciais. Para empurrar de verdade, configure `COLLIBRA_BASE_URL`, `COLLIBRA_USERNAME`, `COLLIBRA_PASSWORD`, `COLLIBRA_DOMAIN_ID`, `COLLIBRA_TABLE_TYPE_ID`, `COLLIBRA_COLUMN_TYPE_ID` (veja `docs/PURVIEW_COLLIBRA.md`).",
    },
    "mig_configured": {
        "es": "✅ Credenciales cargadas — el botón de push real está disponible.",
        "en": "✅ Credentials loaded — the real push button is available.",
        "pt": "✅ Credenciais carregadas — o botão de push real está disponível.",
    },
    "mig_preview": {"es": "👁️ Previsualizar (sin credenciales)", "en": "👁️ Preview (no credentials)", "pt": "👁️ Pré-visualizar (sem credenciais)"},
    "mig_push": {"es": "🚀 Empujar de verdad", "en": "🚀 Push for real", "pt": "🚀 Empurrar de verdade"},
    "mig_done": {"es": "Empujado.", "en": "Pushed.", "pt": "Empurrado."},
    "mig_entities": {"es": "Entidades/assets", "en": "Entities/assets", "pt": "Entidades/assets"},
    "mig_terms": {"es": "Términos de glosario", "en": "Glossary terms", "pt": "Termos de glossário"},
    "mig_detail": {"es": "Ver el payload completo", "en": "View the full payload", "pt": "Ver o payload completo"},
    "mig_local_note": {
        "es": "Apagado por defecto. Las credenciales son tuyas y solo las lee este programa de las variables de entorno — nunca se piden en pantalla ni se guardan. Implementado contra la documentación oficial de cada proveedor; no probado contra un tenant/instancia real (ver docs/PURVIEW_COLLIBRA.md).",
        "en": "Off by default. Your credentials are only read from environment variables by this program — never requested on screen or stored. Implemented against each provider's official docs; not tested against a live tenant/instance (see docs/PURVIEW_COLLIBRA.md).",
        "pt": "Desligado por padrão. Suas credenciais são lidas apenas das variáveis de ambiente por este programa — nunca pedidas na tela nem salvas. Implementado contra a documentação oficial de cada provedor; não testado contra um tenant/instância real (veja docs/PURVIEW_COLLIBRA.md).",
    },
    # ------------------------------------------------------- enforcement (enf)
    "enf_title": {"es": "🔒 Enforcement de acceso (genera DDL, no bloquea nada solo)", "en": "🔒 Access enforcement (generates DDL, blocks nothing by itself)", "pt": "🔒 Enforcement de acesso (gera DDL, não bloqueia nada sozinho)"},
    "enf_intro": {
        "es": "Bloquear una consulta en vivo requiere estar en el camino del dato (un proxy, o Purview dentro de Azure) — este programa NO se hace pasar por eso. Lo que sí hace: te genera el DDL real (GRANT/REVOKE por clasificación + enmascaramiento de columnas PII) a partir de tu catálogo ya gobernado, para que vos (o tu DBA) lo revises y lo corras contra la base. Nunca se conecta a ejecutar nada de esto.",
        "en": "Blocking a live query requires sitting in the data path (a proxy, or Purview inside Azure) — this program does NOT pretend to be that. What it does: generates real DDL (GRANT/REVOKE by classification + PII column masking) from your already-governed catalog, for you (or your DBA) to review and run against the database. It never connects to execute any of this.",
        "pt": "Bloquear uma consulta em tempo real exige estar no caminho do dado (um proxy, ou o Purview dentro do Azure) — este programa NÃO finge ser isso. O que ele faz: gera o DDL real (GRANT/REVOKE por classificação + mascaramento de colunas PII) a partir do seu catálogo já governado, para você (ou seu DBA) revisar e rodar contra o banco. Nunca se conecta para executar nada disso.",
    },
    "enf_engine": {"es": "Motor de base de datos", "en": "Database engine", "pt": "Motor de banco de dados"},
    "enf_roles": {"es": "Roles autorizados por clasificación (uno por línea: clasificación: rol)", "en": "Authorized roles per classification (one per line: classification: role)", "pt": "Papéis autorizados por classificação (um por linha: classificação: papel)"},
    "enf_roles_help": {
        "es": "Ej: PII: rol_rrhh — el rol que sí puede ver las tablas clasificadas PII. Podés agregar varios roles a la misma clasificación en líneas separadas.",
        "en": "E.g.: PII: rol_rrhh — the role allowed to see PII-classified tables. You can add several roles to the same classification on separate lines.",
        "pt": "Ex: PII: rol_rrhh — o papel que pode ver as tabelas classificadas como PII. Você pode adicionar vários papéis à mesma classificação em linhas separadas.",
    },
    "enf_generate": {"es": "📝 Generar DDL", "en": "📝 Generate DDL", "pt": "📝 Gerar DDL"},
    "enf_grants": {"es": "Sentencias GRANT/REVOKE", "en": "GRANT/REVOKE statements", "pt": "Sentenças GRANT/REVOKE"},
    "enf_masks": {"es": "Sentencias de enmascaramiento", "en": "Masking statements", "pt": "Sentenças de mascaramento"},
    "enf_download": {"es": "⬇️ Descargar el .sql", "en": "⬇️ Download the .sql", "pt": "⬇️ Baixar o .sql"},
    "enf_local_note": {
        "es": "100% local: es texto SQL generado a partir de tu catálogo — el programa nunca abre una conexión para ejecutarlo. Cubre PostgreSQL (Row-Level Security nativo) y SQL Server (Dynamic Data Masking + Row-Level Security nativos).",
        "en": "100% local: it's SQL text generated from your catalog — the program never opens a connection to run it. Covers PostgreSQL (native Row-Level Security) and SQL Server (native Dynamic Data Masking + Row-Level Security).",
        "pt": "100% local: é texto SQL gerado a partir do seu catálogo — o programa nunca abre uma conexão para executá-lo. Cobre PostgreSQL (Row-Level Security nativo) e SQL Server (Dynamic Data Masking + Row-Level Security nativos).",
    },
    # -------------------------------------------------------------- MIP (mip)
    "mip_title": {"es": "🏷️ Etiquetas de sensibilidad (Microsoft Information Protection)", "en": "🏷️ Sensitivity labels (Microsoft Information Protection)", "pt": "🏷️ Rótulos de sensibilidade (Microsoft Information Protection)"},
    "mip_intro": {
        "es": "Una etiqueta MIP es cifrado real embebido en el archivo de Office, atado a la infraestructura de Microsoft — no hay forma de reimplementarla localmente. Este conector llama a la API REAL de Microsoft Graph para aplicar una etiqueta de verdad a un archivo que ya vive en OneDrive/SharePoint, usando la clasificación que este catálogo ya calculó.",
        "en": "An MIP label is real encryption embedded in the Office file, tied to Microsoft's infrastructure — there's no way to reimplement it locally. This connector calls the REAL Microsoft Graph API to apply a real label to a file that already lives in OneDrive/SharePoint, using the classification this catalog already computed.",
        "pt": "Um rótulo MIP é criptografia real embutida no arquivo do Office, atrelada à infraestrutura da Microsoft — não há como reimplementá-lo localmente. Este conector chama a API REAL do Microsoft Graph para aplicar um rótulo de verdade a um arquivo que já vive no OneDrive/SharePoint, usando a classificação que este catálogo já calculou.",
    },
    "mip_scope_note": {
        "es": "⚠️ Solo aplica a datasets cuyo archivo fuente ya está en OneDrive/SharePoint — una tabla de base de datos o un CSV que nunca pasó por Microsoft 365 no tiene \"etiqueta MIP\" posible (la etiqueta vive en el formato del archivo, no en el dato en abstracto).",
        "en": "⚠️ Only applies to datasets whose source file already lives in OneDrive/SharePoint — a database table or a CSV that never went through Microsoft 365 has no possible \"MIP label\" (the label lives in the file format, not in the abstract data).",
        "pt": "⚠️ Só se aplica a datasets cujo arquivo fonte já está no OneDrive/SharePoint — uma tabela de banco de dados ou um CSV que nunca passou pelo Microsoft 365 não tem \"rótulo MIP\" possível (o rótulo vive no formato do arquivo, não no dado em abstrato).",
    },
    "mip_env": {
        "es": "Sin configurar — cargá `MIP_TENANT_ID`, `MIP_CLIENT_ID`, `MIP_CLIENT_SECRET` (mismo service principal que Power BI/Purview, con permiso `Files.ReadWrite.All`) para resolver links y aplicar etiquetas de verdad.",
        "en": "Not configured — set `MIP_TENANT_ID`, `MIP_CLIENT_ID`, `MIP_CLIENT_SECRET` (same service principal pattern as Power BI/Purview, with `Files.ReadWrite.All` permission) to resolve links and apply real labels.",
        "pt": "Não configurado — configure `MIP_TENANT_ID`, `MIP_CLIENT_ID`, `MIP_CLIENT_SECRET` (mesmo padrão de service principal do Power BI/Purview, com permissão `Files.ReadWrite.All`) para resolver links e aplicar rótulos de verdade.",
    },
    "mip_file_map": {"es": "Datasets con archivo en OneDrive/SharePoint (uno por línea: dataset: link para compartir)", "en": "Datasets with a file in OneDrive/SharePoint (one per line: dataset: sharing link)", "pt": "Datasets com arquivo no OneDrive/SharePoint (um por linha: dataset: link de compartilhamento)"},
    "mip_file_map_help": {
        "es": "Pegá el link para compartir del archivo (clic derecho → Compartir → Copiar vínculo) de cada dataset que corresponda. Los datasets sin línea acá se listan aparte, sin etiqueta posible.",
        "en": "Paste the sharing link (right-click → Share → Copy link) for each matching dataset. Datasets without a line here are listed separately, with no possible label.",
        "pt": "Cole o link de compartilhamento (clique direito → Compartilhar → Copiar link) de cada dataset correspondente. Datasets sem linha aqui são listados à parte, sem rótulo possível.",
    },
    "mip_needs_creds_to_resolve": {
        "es": "{dataset}: cargá las credenciales para resolver este link.",
        "en": "{dataset}: load credentials to resolve this link.",
        "pt": "{dataset}: carregue as credenciais para resolver este link.",
    },
    "mip_preview": {"es": "👁️ Previsualizar etiquetas", "en": "👁️ Preview labels", "pt": "👁️ Pré-visualizar rótulos"},
    "mip_push": {"es": "🚀 Aplicar etiquetas reales", "en": "🚀 Apply real labels", "pt": "🚀 Aplicar rótulos reais"},
    "mip_skipped": {
        "es": "Sin archivo mapeado (no tienen etiqueta MIP posible): {datasets}",
        "en": "No file mapped (no possible MIP label): {datasets}",
        "pt": "Sem arquivo mapeado (sem rótulo MIP possível): {datasets}",
    },
    "mip_local_note": {
        "es": "Apagado por defecto. Implementado contra Microsoft Graph API v1.0/beta (Microsoft Learn); no probado contra un tenant M365 real. La etiqueta sugerida sale SIEMPRE de las etiquetas reales configuradas en tu tenant — nunca se inventa un id.",
        "en": "Off by default. Implemented against Microsoft Graph API v1.0/beta (Microsoft Learn); not tested against a live M365 tenant. The suggested label ALWAYS comes from the real labels configured in your tenant — never an invented id.",
        "pt": "Desligado por padrão. Implementado contra a Microsoft Graph API v1.0/beta (Microsoft Learn); não testado contra um tenant M365 real. O rótulo sugerido SEMPRE vem dos rótulos reais configurados no seu tenant — nunca um id inventado.",
    },
    # -------------------------------------------------------- scan all (scanall)
    "scanall_title": {"es": "🔎 Escanear todas las conexiones guardadas", "en": "🔎 Scan all saved connections", "pt": "🔎 Escanear todas as conexões salvas"},
    "scanall_intro": {
        "es": "Un clic en vez de elegir conexión por conexión: lista las tablas de TODAS tus conexiones guardadas de una vez. Cubre los motores que vos configuraste acá (9 hoy) — no es descubrimiento automático de fuentes nuevas como el escaneo de tenant de Purview, que agrega agentes dentro de Azure y encuentra recursos sin que nadie cargue una conexión a mano.",
        "en": "One click instead of picking connections one by one: lists the tables of ALL your saved connections at once. Covers the engines you configured here (9 today) — it's not automatic discovery of new sources like Purview's tenant scan, which deploys agents inside Azure and finds resources without anyone loading a connection by hand.",
        "pt": "Um clique em vez de escolher conexão por conexão: lista as tabelas de TODAS as suas conexões salvas de uma vez. Cobre os motores que você configurou aqui (9 hoje) — não é descoberta automática de fontes novas como o escaneamento de tenant do Purview, que implanta agentes dentro do Azure e encontra recursos sem que ninguém carregue uma conexão manualmente.",
    },
    "scanall_run": {"es": "▶️ Escanear todas ahora", "en": "▶️ Scan all now", "pt": "▶️ Escanear todas agora"},
    "scanall_tables": {"es": "Tablas encontradas", "en": "Tables found", "pt": "Tabelas encontradas"},
    "scanall_errors": {"es": "Conexiones con error", "en": "Connections with errors", "pt": "Conexões com erro"},
    "scanall_none": {"es": "No hay conexiones guardadas todavía — agregá una en 🔎 Mis datos.", "en": "No saved connections yet — add one in 🔎 My data.", "pt": "Ainda não há conexões salvas — adicione uma em 🔎 Meus dados."},
    "scanall_local_note": {
        "es": "Una conexión caída no frena el escaneo de las demás — el error queda registrado en su fila.",
        "en": "A connection that's down doesn't stop the scan of the rest — the error is recorded in its row.",
        "pt": "Uma conexão fora do ar não interrompe o escaneamento das demais — o erro fica registrado na sua linha.",
    },
    # -------------------------------------------------------------- clients
    "cl_intro": {
        "es": "Fichas de empresas clientes: contacto, BI que usan, restricciones "
              "de TI y madurez. Se guardan en tu equipo y persisten entre sesiones.",
        "en": "Client company records: contact, BI tools, IT restrictions and "
              "maturity. Stored on your machine and persisted across sessions.",
        "pt": "Fichas de empresas clientes: contato, BI usado, restrições de TI "
              "e maturidade. Salvas no seu computador e persistentes entre sessões.",
    },
    "cl_new": {"es": "➕ Nueva ficha / editar", "en": "➕ New record / edit", "pt": "➕ Nova ficha / editar"},
    "cl_pick_edit": {"es": "Editar ficha existente", "en": "Edit existing record", "pt": "Editar ficha existente"},
    "cl_new_option": {"es": "(nueva empresa)", "en": "(new company)", "pt": "(nova empresa)"},
    "cl_company": {"es": "Empresa", "en": "Company", "pt": "Empresa"},
    "cl_country": {"es": "País", "en": "Country", "pt": "País"},
    "cl_industry": {"es": "Rubro", "en": "Industry", "pt": "Setor"},
    "cl_contact": {"es": "Contacto", "en": "Contact", "pt": "Contato"},
    "cl_email": {"es": "Email", "en": "Email", "pt": "E-mail"},
    "cl_bi": {"es": "Herramientas de BI", "en": "BI tools", "pt": "Ferramentas de BI"},
    "cl_restriction": {"es": "Restricción de TI", "en": "IT restriction", "pt": "Restrição de TI"},
    "cl_r_exe": {"es": "Permite instalar .exe", "en": "Allows installing .exe", "pt": "Permite instalar .exe"},
    "cl_r_noexe": {"es": "No permite .exe (pero sí Python)", "en": "No .exe allowed (Python OK)", "pt": "Não permite .exe (mas Python sim)"},
    "cl_r_web": {"es": "Solo web / servidor", "en": "Web/server only", "pt": "Somente web / servidor"},
    "cl_pack": {"es": "Paquete recomendado", "en": "Recommended package", "pt": "Pacote recomendado"},
    "cl_pack_a": {"es": "Opción A · Instalador .exe", "en": "Option A · .exe installer", "pt": "Opção A · Instalador .exe"},
    "cl_pack_b": {"es": "Opción B · Portable .bat", "en": "Option B · Portable .bat", "pt": "Opção B · Portátil .bat"},
    "cl_pack_web": {"es": "Despliegue web (servidor)", "en": "Web deployment (server)", "pt": "Implantação web (servidor)"},
    "cl_maturity": {"es": "Madurez de gobierno (1–5)", "en": "Governance maturity (1–5)", "pt": "Maturidade de governança (1–5)"},
    "cl_status": {"es": "Estado", "en": "Status", "pt": "Status"},
    "cl_notes": {"es": "Notas", "en": "Notes", "pt": "Notas"},
    "cl_save": {"es": "💾 Guardar ficha", "en": "💾 Save record", "pt": "💾 Salvar ficha"},
    "cl_saved": {"es": "Ficha guardada.", "en": "Record saved.", "pt": "Ficha salva."},
    "cl_need_name": {"es": "Poné al menos el nombre de la empresa.", "en": "Enter at least the company name.", "pt": "Informe pelo menos o nome da empresa."},
    "cl_delete": {"es": "🗑️ Eliminar ficha", "en": "🗑️ Delete record", "pt": "🗑️ Excluir ficha"},
    "cl_deleted": {"es": "Ficha eliminada.", "en": "Record deleted.", "pt": "Ficha excluída."},
    "cl_list": {"es": "Fichas guardadas", "en": "Saved records", "pt": "Fichas salvas"},
    "cl_empty": {"es": "Todavía no hay fichas: creá la primera acá arriba.", "en": "No records yet: create the first one above.", "pt": "Ainda não há fichas: crie a primeira acima."},
    "cl_where": {
        "es": "Se guardan en {path} (JSON). Podés respaldarlas copiando ese archivo.",
        "en": "Stored at {path} (JSON). Back them up by copying that file.",
        "pt": "Salvas em {path} (JSON). Faça backup copiando esse arquivo.",
    },
    # ------------------------------------------------------------- workspace
    "ws_intro": {
        "es": "El proyecto de cada cliente: guardá cada etapa de tu trabajo "
              "(el dataset que perfilaste, los duplicados/MDM, el escaneo de "
              "Power BI o Tableau, el paquete para BI) en disco, para no "
              "perder nada y retomar donde quedaste. 100% local.",
        "en": "Each client's project: save every stage of your work (the "
              "dataset you profiled, the duplicates/MDM, the Power BI or "
              "Tableau scan, the BI bundle) to disk, so nothing is lost and "
              "you can pick up where you left off. 100% local.",
        "pt": "O projeto de cada cliente: salve cada etapa do seu trabalho (o "
              "dataset que perfilou, os duplicados/MDM, o escaneamento de "
              "Power BI ou Tableau, o pacote para BI) em disco, para não "
              "perder nada e retomar de onde parou. 100% local.",
    },
    "ws_no_clients": {
        "es": "Primero creá una empresa en la pestaña 🏢 Empresas: el proyecto "
              "se guarda por cliente.",
        "en": "First create a company in the 🏢 Companies tab: the project is "
              "saved per client.",
        "pt": "Primeiro crie uma empresa na aba 🏢 Empresas: o projeto é salvo "
              "por cliente.",
    },
    "ws_pick_client": {"es": "Cliente", "en": "Client", "pt": "Cliente"},
    "ws_summary_stages": {"es": "Etapas guardadas", "en": "Saved stages", "pt": "Etapas salvas"},
    "ws_summary_tables": {"es": "Tablas", "en": "Tables", "pt": "Tabelas"},
    "ws_summary_rows": {"es": "Filas guardadas", "en": "Saved rows", "pt": "Linhas salvas"},
    "ws_summary_updated": {"es": "Última actualización", "en": "Last update", "pt": "Última atualização"},
    "ws_save_title": {"es": "💾 Guardar la etapa actual", "en": "💾 Save the current stage", "pt": "💾 Salvar a etapa atual"},
    "ws_capture_hint": {
        "es": "Elegí qué de lo que trabajaste hasta ahora en esta sesión querés "
              "guardar en el proyecto del cliente. Lo que no aparezca acá es "
              "porque todavía no lo generaste en esta sesión.",
        "en": "Choose what you've worked on so far in this session to save into "
              "the client's project. Anything not shown here is because you "
              "haven't generated it yet in this session.",
        "pt": "Escolha o que você trabalhou até agora nesta sessão para salvar "
              "no projeto do cliente. O que não aparece aqui é porque você "
              "ainda não gerou nesta sessão.",
    },
    "ws_include_dataset": {"es": "Dataset perfilado ({name})", "en": "Profiled dataset ({name})", "pt": "Dataset perfilado ({name})"},
    "ws_include_mdm": {"es": "Reporte de duplicados / MDM", "en": "Duplicates / MDM report", "pt": "Relatório de duplicados / MDM"},
    "ws_include_powerbi": {"es": "Escaneo de Power BI (catálogo, calidad, linaje)", "en": "Power BI scan (catalog, quality, lineage)", "pt": "Escaneamento de Power BI (catálogo, qualidade, linhagem)"},
    "ws_include_tableau": {"es": "Escaneo de Tableau (catálogo, calidad, linaje)", "en": "Tableau scan (catalog, quality, lineage)", "pt": "Escaneamento de Tableau (catálogo, qualidade, linhagem)"},
    "ws_include_governance": {"es": "Paquete de gobierno (catálogo, reglas, glosario, linaje, políticas…)", "en": "Governance bundle (catalog, rules, glossary, lineage, policies…)", "pt": "Pacote de governança (catálogo, regras, glossário, linhagem, políticas…)"},
    "ws_stage_name": {"es": "Nombre de la etapa (ej. \"Catálogo inicial\", \"Después de corregir\")", "en": "Stage name (e.g. \"Initial catalog\", \"After fixing\")", "pt": "Nome da etapa (ex. \"Catálogo inicial\", \"Depois de corrigir\")"},
    "ws_stage_notes": {"es": "Notas (opcional)", "en": "Notes (optional)", "pt": "Notas (opcional)"},
    "ws_save_btn": {"es": "💾 Guardar etapa", "en": "💾 Save stage", "pt": "💾 Salvar etapa"},
    "ws_saved_ok": {"es": "Etapa \"{name}\" guardada ({n} tabla/s).", "en": "Stage \"{name}\" saved ({n} table/s).", "pt": "Etapa \"{name}\" salva ({n} tabela/s)."},
    "ws_need_name": {"es": "Poné un nombre para la etapa.", "en": "Enter a name for the stage.", "pt": "Informe um nome para a etapa."},
    "ws_need_selection": {"es": "Elegí al menos una cosa para guardar.", "en": "Select at least one thing to save.", "pt": "Escolha ao menos uma coisa para salvar."},
    "ws_stages_title": {"es": "📚 Etapas guardadas", "en": "📚 Saved stages", "pt": "📚 Etapas salvas"},
    "ws_no_stages": {"es": "Todavía no guardaste ninguna etapa para este cliente.", "en": "You haven't saved any stage for this client yet.", "pt": "Você ainda não salvou nenhuma etapa para este cliente."},
    "ws_col_table": {"es": "Tabla", "en": "Table", "pt": "Tabela"},
    "ws_reload": {"es": "👁️ Ver / descargar", "en": "👁️ View / download", "pt": "👁️ Ver / baixar"},
    "ws_delete": {"es": "🗑️ Eliminar etapa", "en": "🗑️ Delete stage", "pt": "🗑️ Excluir etapa"},
    "ws_deleted": {"es": "Etapa eliminada.", "en": "Stage deleted.", "pt": "Etapa excluída."},
    "ws_export_title": {"es": "📦 Respaldar / restaurar el proyecto completo", "en": "📦 Back up / restore the whole project", "pt": "📦 Backup / restaurar o projeto completo"},
    "ws_export_hint": {
        "es": "Descargá todo el proyecto del cliente (todas las etapas) en un "
              "ZIP para respaldarlo o llevarlo a otra máquina, o restaurá uno "
              "que hayas descargado antes.",
        "en": "Download the client's whole project (all stages) as a ZIP to "
              "back it up or move it to another machine, or restore one you "
              "downloaded before.",
        "pt": "Baixe todo o projeto do cliente (todas as etapas) em um ZIP "
              "para backup ou para levar a outra máquina, ou restaure um que "
              "você baixou antes.",
    },
    "ws_export_btn": {"es": "⬇️ Descargar proyecto (ZIP)", "en": "⬇️ Download project (ZIP)", "pt": "⬇️ Baixar projeto (ZIP)"},
    "ws_import_btn": {"es": "Restaurar desde un ZIP", "en": "Restore from a ZIP", "pt": "Restaurar de um ZIP"},
    "ws_import_replace": {"es": "Reemplazar las etapas actuales (en vez de sumar)", "en": "Replace current stages (instead of merging)", "pt": "Substituir as etapas atuais (em vez de somar)"},
    "ws_do_import": {"es": "⬆️ Importar", "en": "⬆️ Import", "pt": "⬆️ Importar"},
    "ws_imported_ok": {"es": "Proyecto importado: {n} etapa/s en total.", "en": "Project imported: {n} stage/s in total.", "pt": "Projeto importado: {n} etapa/s no total."},
    "ws_where": {
        "es": "Se guarda en {path} (local). Respaldalo copiando esa carpeta o con el ZIP de arriba.",
        "en": "Stored at {path} (local). Back it up by copying that folder or with the ZIP above.",
        "pt": "Salvo em {path} (local). Faça backup copiando essa pasta ou com o ZIP acima.",
    },
    # ----------------------------------------------------------------- help
    "h_intro": {
        "es": "Qué automatiza esta plataforma, qué requiere personas, y los "
              "speeches listos para lograr la parte humana y cerrar el círculo.",
        "en": "What this platform automates, what requires people, and the "
              "ready-made speeches to achieve the human part and close the loop.",
        "pt": "O que esta plataforma automatiza, o que requer pessoas, e os "
              "speeches prontos para alcançar a parte humana e fechar o ciclo.",
    },
    "h_matrix": {"es": "¿Qué se automatiza y qué no?", "en": "What is automated and what is not?", "pt": "O que é automatizado e o que não é?"},
    "h_matrix_note": {
        "es": "La mitad técnica del gobierno de datos es 100% automática en esta "
              "plataforma. La mitad organizacional (dueños, definiciones, "
              "correcciones en origen, adopción) NO la puede automatizar ningún "
              "software: se logra con las conversaciones de abajo.",
        "en": "The technical half of data governance is 100% automatic in this "
              "platform. The organizational half (owners, definitions, fixes at "
              "the source, adoption) CANNOT be automated by any software: it is "
              "achieved with the conversations below.",
        "pt": "A metade técnica da governança de dados é 100% automática nesta "
              "plataforma. A metade organizacional (donos, definições, correções "
              "na origem, adoção) NÃO pode ser automatizada por nenhum software: "
              "consegue-se com as conversas abaixo.",
    },
    "h_area": {"es": "Área", "en": "Area", "pt": "Área"},
    "h_level": {"es": "Automatización", "en": "Automation", "pt": "Automação"},
    "h_detail": {"es": "Detalle", "en": "Detail", "pt": "Detalhe"},
    "h_auto": {"es": "✅ Automático", "en": "✅ Automatic", "pt": "✅ Automático"},
    "h_partial": {"es": "🟡 Parcial", "en": "🟡 Partial", "pt": "🟡 Parcial"},
    "h_human": {"es": "🧑 Requiere personas", "en": "🧑 Requires people", "pt": "🧑 Requer pessoas"},
    "h_speeches": {"es": "Speeches IA para la parte no automatizable", "en": "AI speeches for the non-automatable part", "pt": "Speeches IA para a parte não automatizável"},
    "h_speeches_note": {
        "es": "Guiones listos para copiar o decir, uno por conversación crítica. "
              "Con estos cinco, cualquier empresa cierra el círculo completo del "
              "gobierno de datos.",
        "en": "Ready-to-copy scripts, one per critical conversation. With these "
              "five, any company closes the full data-governance loop.",
        "pt": "Roteiros prontos para copiar ou falar, um por conversa crítica. "
              "Com estes cinco, qualquer empresa fecha o ciclo completo da "
              "governança de dados.",
    },
    "h_audience": {"es": "Audiencia", "en": "Audience", "pt": "Audiência"},
    "h_packs": {"es": "Dos formas de instalar (según restricciones de TI)", "en": "Two ways to install (per IT restrictions)", "pt": "Duas formas de instalar (conforme restrições de TI)"},
    "h_packs_note": {
        "es": "Opción A — instalador .exe (no requiere Python; para empresas que "
              "permiten instalar software). Opción B — portable .bat "
              "autoinstalable con Streamlit (no instala nada en el sistema; para "
              "empresas que bloquean .exe pero permiten Python). Mismas "
              "funcionalidades en ambas. Detalles en la carpeta distribucion/.",
        "en": "Option A — .exe installer (no Python required; for companies that "
              "allow installing software). Option B — self-installing portable "
              ".bat with Streamlit (installs nothing system-wide; for companies "
              "that block .exe but allow Python). Same features in both. Details "
              "in the distribucion/ folder.",
        "pt": "Opção A — instalador .exe (não requer Python; para empresas que "
              "permitem instalar software). Opção B — .bat portátil "
              "autoinstalável com Streamlit (não instala nada no sistema; para "
              "empresas que bloqueiam .exe mas permitem Python). Mesmas "
              "funcionalidades em ambas. Detalhes na pasta distribucion/.",
    },
    "h_dmbok_covered": {"es": "✅ Cubierta", "en": "✅ Covered", "pt": "✅ Coberta"},
    "h_dmbok_partial": {"es": "🟡 Parcial", "en": "🟡 Partial", "pt": "🟡 Parcial"},
    "h_dmbok_out": {"es": "⬜ Fuera de alcance", "en": "⬜ Out of scope", "pt": "⬜ Fora de escopo"},
    # -------------------------------------------------- tutorial DMBOK
    "dk_intro": {
        "es": "Tutorial completo del estándar **DAMA-DMBOK** (Data Management Body of "
              "Knowledge): teoría, conceptos, roles, madurez y el ciclo de vida del dato, "
              "con tableros. Explicado en criollo y técnico, en los 3 idiomas.",
        "en": "Complete tutorial of the **DAMA-DMBOK** standard (Data Management Body of "
              "Knowledge): theory, concepts, roles, maturity and the data lifecycle, with "
              "dashboards. Explained plainly and technically, in 3 languages.",
        "pt": "Tutorial completo do padrão **DAMA-DMBOK** (Data Management Body of "
              "Knowledge): teoria, conceitos, papéis, maturidade e o ciclo de vida do "
              "dado, com painéis. Explicado em linguagem simples e técnica, nos 3 idiomas.",
    },
    "dk_what": {"es": "¿Qué es el DAMA-DMBOK?", "en": "What is DAMA-DMBOK?", "pt": "O que é o DAMA-DMBOK?"},
    "dk_what_p": {
        "es": "El DMBOK es el estándar de referencia mundial en gestión de datos, "
              "publicado por DAMA International. Organiza la disciplina en 11 áreas de "
              "conocimiento (la 'Rueda DAMA'), con el gobierno de datos en el centro "
              "coordinando a las otras 10. Este tutorial recorre las 11 áreas, los "
              "principios, los conceptos clave, los roles, el modelo de madurez y el "
              "ciclo de vida del dato — y marca, con honestidad, qué cubre esta plataforma.",
        "en": "The DMBOK is the world reference standard for data management, published "
              "by DAMA International. It organizes the discipline into 11 knowledge areas "
              "(the 'DAMA Wheel'), with data governance at the center coordinating the "
              "other 10. This tutorial covers the 11 areas, the principles, key concepts, "
              "roles, the maturity model and the data lifecycle — and honestly marks what "
              "this platform covers.",
        "pt": "O DMBOK é o padrão de referência mundial em gestão de dados, publicado "
              "pela DAMA International. Organiza a disciplina em 11 áreas de conhecimento "
              "(a 'Roda DAMA'), com a governança de dados no centro coordenando as outras "
              "10. Este tutorial percorre as 11 áreas, os princípios, os conceitos-chave, "
              "os papéis, o modelo de maturidade e o ciclo de vida do dado — e marca, com "
              "honestidade, o que esta plataforma cobre.",
    },
    "dk_principles": {"es": "Principios rectores", "en": "Guiding principles", "pt": "Princípios norteadores"},
    "dk_radar": {"es": "Cobertura por área (qué tanto cubre la plataforma)",
                 "en": "Coverage by area (how much the platform covers)",
                 "pt": "Cobertura por área (quanto a plataforma cobre)"},
    "dk_areas": {"es": "Las 11 áreas de conocimiento", "en": "The 11 knowledge areas", "pt": "As 11 áreas de conhecimento"},
    "dk_covered": {"es": "Áreas cubiertas", "en": "Covered areas", "pt": "Áreas cobertas"},
    "dk_partial": {"es": "Cobertura parcial", "en": "Partial coverage", "pt": "Cobertura parcial"},
    "dk_out": {"es": "Fuera de alcance", "en": "Out of scope", "pt": "Fora de escopo"},
    "dk_deliverables": {"es": "Entregables típicos", "en": "Typical deliverables", "pt": "Entregáveis típicos"},
    "dk_plain": {"es": "🙋 En criollo", "en": "🙋 In plain words", "pt": "🙋 Em linguagem simples"},
    "dk_tech": {"es": "🛠️ Técnico", "en": "🛠️ Technical", "pt": "🛠️ Técnico"},
    "dk_concepts": {"es": "Conceptos clave (glosario del estándar)", "en": "Key concepts (standard glossary)", "pt": "Conceitos-chave (glossário do padrão)"},
    "dk_concept_search": {"es": "Buscar concepto…", "en": "Search a concept…", "pt": "Buscar conceito…"},
    "dk_roles": {"es": "Roles del gobierno de datos", "en": "Data governance roles", "pt": "Papéis da governança de dados"},
    "dk_role": {"es": "Rol", "en": "Role", "pt": "Papel"},
    "dk_responsibility": {"es": "Responsabilidad", "en": "Responsibility", "pt": "Responsabilidade"},
    "dk_maturity": {"es": "Modelo de madurez del gobierno de datos", "en": "Data governance maturity model", "pt": "Modelo de maturidade da governança de dados"},
    "dk_maturity_note": {
        "es": "5 niveles, de 'cada uno con su planilla' a 'los datos como activo estratégico'. "
              "El objetivo de un proyecto de gobierno es subir de nivel de forma medible.",
        "en": "5 levels, from 'everyone with their own spreadsheet' to 'data as a strategic "
              "asset'. A governance project aims to climb levels measurably.",
        "pt": "5 níveis, de 'cada um com sua planilha' a 'dados como ativo estratégico'. "
              "Um projeto de governança busca subir de nível de forma mensurável.",
    },
    "dk_level": {"es": "Nivel", "en": "Level", "pt": "Nível"},
    "dk_lifecycle": {"es": "Ciclo de vida del dato (POSMAD)", "en": "Data lifecycle (POSMAD)", "pt": "Ciclo de vida do dado (POSMAD)"},
    "dk_lifecycle_note": {
        "es": "El dato se gobierna en todo su recorrido, no solo cuando se usa: "
              "Planificar → Obtener → Almacenar → Mantener → Aplicar → Disponer.",
        "en": "Data is governed across its whole journey, not only when used: "
              "Plan → Obtain → Store → Maintain → Apply → Dispose.",
        "pt": "O dado é governado em todo o seu percurso, não só quando usado: "
              "Planejar → Obter → Armazenar → Manter → Aplicar → Descartar.",
    },
    "dk_quality_dims": {"es": "Las 6 dimensiones de calidad (DAMA), medidas en tus datos",
                        "en": "The 6 quality dimensions (DAMA), measured on your data",
                        "pt": "As 6 dimensões de qualidade (DAMA), medidas nos seus dados"},
    "dk_subtab_dmbok": {"es": "📘 DAMA-DMBOK", "en": "📘 DAMA-DMBOK", "pt": "📘 DAMA-DMBOK"},
    "dk_subtab_cobit": {"es": "🎯 COBIT 2019", "en": "🎯 COBIT 2019", "pt": "🎯 COBIT 2019"},
    "dk_subtab_iso": {"es": "🌐 ISO/IEC 38505", "en": "🌐 ISO/IEC 38505", "pt": "🌐 ISO/IEC 38505"},
    # ------------------------------------------------------ COBIT 2019
    "co_intro": {
        "es": "Autoevaluación honesta frente a **COBIT 2019** (ISACA): de sus 40 objetivos "
              "de gobierno/gestión de TI, estos son los 8 relacionados directamente con "
              "datos. No es una certificación — es una guía de qué cubre esta plataforma y "
              "qué queda en manos de tu organización.",
        "en": "An honest self-assessment against **COBIT 2019** (ISACA): of its 40 IT "
              "governance/management objectives, these are the 8 directly related to data. "
              "Not a certification — a guide to what this platform covers and what's left to "
              "your organization.",
        "pt": "Autoavaliação honesta frente ao **COBIT 2019** (ISACA): dos seus 40 objetivos "
              "de governança/gestão de TI, estes são os 8 relacionados diretamente a dados. "
              "Não é uma certificação — é um guia do que esta plataforma cobre e do que fica "
              "a cargo da sua organização.",
    },
    "co_radar": {"es": "Cobertura por objetivo", "en": "Coverage by objective", "pt": "Cobertura por objetivo"},
    "co_objectives": {"es": "Los 8 objetivos relacionados con datos",
                      "en": "The 8 data-related objectives", "pt": "Os 8 objetivos relacionados a dados"},
    "co_covered": {"es": "Objetivos cubiertos", "en": "Covered objectives", "pt": "Objetivos cobertos"},
    "co_partial": {"es": "Cobertura parcial", "en": "Partial coverage", "pt": "Cobertura parcial"},
    "co_out": {"es": "Fuera de alcance", "en": "Out of scope", "pt": "Fora de escopo"},
    # ------------------------------------------------------ ISO/IEC 38505
    "iso_intro": {
        "es": "**ISO/IEC 38505** aplica los 6 principios de gobierno de ISO/IEC 38500 "
              "específicamente a los datos, más el modelo de evaluación Valor/Riesgo/"
              "Restricción (VRC) para decisiones sobre datos. Misma autoevaluación honesta "
              "que el resto de esta pestaña.",
        "en": "**ISO/IEC 38505** applies the 6 governance principles of ISO/IEC 38500 "
              "specifically to data, plus the Value/Risk/Constraint (VRC) evaluation model "
              "for data decisions. Same honest self-assessment as the rest of this tab.",
        "pt": "**ISO/IEC 38505** aplica os 6 princípios de governança da ISO/IEC 38500 "
              "especificamente aos dados, mais o modelo de avaliação Valor/Risco/Restrição "
              "(VRC) para decisões sobre dados. Mesma autoavaliação honesta do resto desta "
              "aba.",
    },
    "iso_radar": {"es": "Cobertura por principio", "en": "Coverage by principle", "pt": "Cobertura por princípio"},
    "iso_principles": {"es": "Los 6 principios de gobierno, aplicados a datos",
                       "en": "The 6 governance principles, applied to data",
                       "pt": "Os 6 princípios de governança, aplicados a dados"},
    "iso_vrc_title": {"es": "Modelo Valor / Riesgo / Restricción (VRC)",
                      "en": "Value / Risk / Constraint (VRC) model",
                      "pt": "Modelo Valor / Risco / Restrição (VRC)"},
    "iso_vrc_col_dim": {"es": "Dimensión", "en": "Dimension", "pt": "Dimensão"},
    "iso_vrc_col_text": {"es": "Qué evalúa", "en": "What it evaluates", "pt": "O que avalia"},
    "iso_vrc_col_mapped": {"es": "Cómo lo cubre el programa", "en": "How the program covers it",
                           "pt": "Como o programa cobre isso"},
    "iso_covered": {"es": "Principios cubiertos", "en": "Covered principles", "pt": "Princípios cobertos"},
    "iso_partial": {"es": "Cobertura parcial", "en": "Partial coverage", "pt": "Cobertura parcial"},
    "iso_out": {"es": "Fuera de alcance", "en": "Out of scope", "pt": "Fora de escopo"},
    # -------------------------------------------------------- laboratorio
    "lab_intro": {
        "es": "Un caso completo de punta a punta, con teoría y dashboards reales: la misma empresa retail recorre las 7 etapas de un proyecto de gobierno de datos, del catálogo a la publicación en BI.",
        "en": "A complete end-to-end case, with theory and real dashboards: the same retail company goes through the 7 stages of a data governance project, from the catalog to publishing to BI.",
        "pt": "Um caso completo de ponta a ponta, com teoria e dashboards reais: a mesma empresa varejista percorre as 7 etapas de um projeto de governança de dados, do catálogo à publicação em BI.",
    },
    "lab_plain": {"es": "🙋 En criollo", "en": "🙋 In plain words", "pt": "🙋 Em linguagem simples"},
    "lab_tech": {"es": "🛠️ Detalle técnico", "en": "🛠️ Technical detail", "pt": "🛠️ Detalhe técnico"},
    "lab_dmbok_tag": {"es": "Área DAMA-DMBOK", "en": "DAMA-DMBOK area", "pt": "Área DAMA-DMBOK"},
    "lab_before": {"es": "Antes (sin gobierno)", "en": "Before (ungoverned)", "pt": "Antes (sem governança)"},
    "lab_after": {"es": "Después (gobernado)", "en": "After (governed)", "pt": "Depois (governado)"},
    "lab_compare_dim": {"es": "Calidad por dimensión: antes vs. después", "en": "Quality by dimension: before vs. after", "pt": "Qualidade por dimensão: antes vs. depois"},
    "lab_index": {"es": "Índice de calidad", "en": "Quality index", "pt": "Índice de qualidade"},
    "lab_rows_affected": {"es": "Filas con problemas", "en": "Rows with issues", "pt": "Linhas com problemas"},
    "lab_rules_fail": {"es": "Reglas en falla", "en": "Rules failing", "pt": "Regras em falha"},
    "lab_delta": {"es": "Mejora del índice", "en": "Index improvement", "pt": "Melhora do índice"},
    "lab_rows_cut": {"es": "Reducción de filas problemáticas", "en": "Reduction in problem rows", "pt": "Redução de linhas problemáticas"},
    "lab_issues_before": {"es": "Top incidencias detectadas (antes)", "en": "Top detected issues (before)", "pt": "Principais incidências detectadas (antes)"},
    "lab_summary_title": {"es": "Resultado del laboratorio", "en": "Lab result", "pt": "Resultado do laboratório"},
    "lab_reproducible": {"es": "Reproducible: python docs/caso_ejemplo/medir_impacto.py — mismo motor de reglas, sin datos inventados.",
                          "en": "Reproducible: python docs/caso_ejemplo/medir_impacto.py — same rule engine, no invented numbers.",
                          "pt": "Reproduzível: python docs/caso_ejemplo/medir_impacto.py — mesmo motor de regras, sem números inventados."},
    # ------------------------------------------------------------- tables
    "tbl_catalog": {"es": "Catálogo de datasets", "en": "Dataset catalog", "pt": "Catálogo de datasets"},
    "tbl_dictionary": {"es": "Diccionario de columnas", "en": "Column dictionary", "pt": "Dicionário de colunas"},
    "tbl_quality": {"es": "Resultados de calidad", "en": "Quality results", "pt": "Resultados de qualidade"},
    "tbl_lineage": {"es": "Aristas de linaje", "en": "Lineage edges", "pt": "Arestas de linhagem"},
    "tbl_glossary": {"es": "Glosario", "en": "Glossary", "pt": "Glossário"},
    "tbl_policies": {"es": "Políticas", "en": "Policies", "pt": "Políticas"},
    "tbl_kpis": {"es": "KPIs de gobierno", "en": "Governance KPIs", "pt": "KPIs de governança"},
    # ------------------------------------------------------------- Power BI
    "tab_pbi": {"es": "🔷 Power BI", "en": "🔷 Power BI", "pt": "🔷 Power BI"},
    "pbi_intro": {
        "es": "Gobierná el modelo de Power BI en sí: tablas, columnas, medidas (DAX), "
              "relaciones y RLS — solo estructura, nunca tus filas.",
        "en": "Govern the Power BI model itself: tables, columns, measures (DAX), "
              "relationships and RLS — structure only, never your rows.",
        "pt": "Governe o modelo do Power BI em si: tabelas, colunas, medidas (DAX), "
              "relações e RLS — apenas estrutura, nunca suas linhas.",
    },
    "pbi_secure_note": {
        "es": "Guardá el reporte como .pbip (formato TMDL) y borrá el archivo "
              ".pbi/cache.abf: el modelo queda con toda su estructura y cero datos.",
        "en": "Save the report as .pbip (TMDL format) and delete the .pbi/cache.abf "
              "file: the model keeps its full structure with zero data.",
        "pt": "Salve o relatório como .pbip (formato TMDL) e apague o arquivo "
              ".pbi/cache.abf: o modelo fica com toda a estrutura e zero dados.",
    },
    "pbi_source": {"es": "Origen", "en": "Source", "pt": "Origem"},
    "pbi_src_path": {"es": "📁 Carpeta local .pbip", "en": "📁 Local .pbip folder",
                     "pt": "📁 Pasta local .pbip"},
    "pbi_src_zip": {"es": "📦 Subir .zip del .pbip", "en": "📦 Upload .pbip .zip",
                    "pt": "📦 Enviar .zip do .pbip"},
    "pbi_path": {"es": "Ruta a la carpeta del proyecto .pbip",
                 "en": "Path to the .pbip project folder",
                 "pt": "Caminho para a pasta do projeto .pbip"},
    "pbi_path_hint": {
        "es": "La carpeta que contiene *.SemanticModel/definition (TMDL).",
        "en": "The folder containing *.SemanticModel/definition (TMDL).",
        "pt": "A pasta que contém *.SemanticModel/definition (TMDL).",
    },
    "pbi_zip": {"es": "Archivo .zip del proyecto .pbip", "en": ".pbip project .zip file",
                "pt": "Arquivo .zip do projeto .pbip"},
    "pbi_load": {"es": "Analizar modelo", "en": "Analyze model", "pt": "Analisar modelo"},
    "pbi_model": {"es": "Modelo", "en": "Model", "pt": "Modelo"},
    "pbi_tables": {"es": "Tablas", "en": "Tables", "pt": "Tabelas"},
    "pbi_measures": {"es": "Medidas", "en": "Measures", "pt": "Medidas"},
    "pbi_columns": {"es": "Columnas", "en": "Columns", "pt": "Colunas"},
    "pbi_roles": {"es": "Roles RLS", "en": "RLS roles", "pt": "Papéis RLS"},
    "pbi_catalog_title": {"es": "📇 Catálogo del modelo", "en": "📇 Model catalog",
                          "pt": "📇 Catálogo do modelo"},
    "pbi_dict_title": {"es": "📚 Columnas del modelo", "en": "📚 Model columns",
                       "pt": "📚 Colunas do modelo"},
    "pbi_measures_title": {"es": "📖 Medidas y DAX (glosario)", "en": "📖 Measures & DAX (glossary)",
                           "pt": "📖 Medidas e DAX (glossário)"},
    "pbi_health_title": {"es": "✅ Salud del modelo", "en": "✅ Model health",
                         "pt": "✅ Saúde do modelo"},
    "pbi_health_overall": {"es": "Índice de modelo", "en": "Model index", "pt": "Índice do modelo"},
    "pbi_lineage_title": {"es": "🧬 Linaje del modelo", "en": "🧬 Model lineage",
                          "pt": "🧬 Linhagem do modelo"},
    "pbi_lineage_hint": {
        "es": "Cadena completa: origen SQL detectado → tabla → dataset (modelo) → reporte.",
        "en": "Full chain: detected SQL source → table → dataset (model) → report.",
        "pt": "Cadeia completa: origem SQL detectada → tabela → dataset (modelo) → relatório.",
    },
    "pbi_sources_title": {"es": "🗄️ Origen SQL por tabla", "en": "🗄️ SQL source per table",
                          "pt": "🗄️ Origem SQL por tabela"},
    "pbi_sources_hint": {
        "es": "Detectado leyendo la expresión M de cada partición (solo texto de la consulta, "
              "nunca se ejecuta ni trae filas).",
        "en": "Detected by reading each partition's M expression (only the query text, "
              "never executed, never fetches rows).",
        "pt": "Detectado lendo a expressão M de cada partição (apenas o texto da consulta, "
              "nunca executada, nunca traz linhas).",
    },
    "pbi_source_col_table": {"es": "Tabla", "en": "Table", "pt": "Tabela"},
    "pbi_source_col_src": {"es": "Origen detectado", "en": "Detected source", "pt": "Origem detectada"},
    "pbi_source_none": {"es": "sin detectar", "en": "not detected", "pt": "não detectado"},
    "pbi_refactor": {"es": "✨ Refactor DAX con {provider}", "en": "✨ Refactor DAX with {provider}",
                     "pt": "✨ Refatorar DAX com {provider}"},
    "pbi_refactor_hint": {
        "es": "Con tu API key configurada, pedile a la IA que audite y mejore el DAX "
              "(se manda solo el DAX, nunca datos).",
        "en": "With your API key set, ask the AI to audit and improve the DAX "
              "(only the DAX is sent, never data).",
        "pt": "Com sua API key configurada, peça à IA para auditar e melhorar o DAX "
              "(envia-se apenas o DAX, nunca dados).",
    },
    "pbi_r_assessment": {"es": "Veredicto", "en": "Assessment", "pt": "Veredicto"},
    "pbi_r_issues": {"es": "Problemas detectados", "en": "Issues found", "pt": "Problemas encontrados"},
    "pbi_r_dax": {"es": "DAX refactorizado", "en": "Refactored DAX", "pt": "DAX refatorado"},
    "pbi_r_expl": {"es": "Por qué es mejor", "en": "Why it's better", "pt": "Por que é melhor"},
    "pbi_no_model": {"es": "Cargá un .pbip para ver su estructura.",
                     "en": "Load a .pbip to see its structure.",
                     "pt": "Carregue um .pbip para ver sua estrutura."},
    "pbi_err": {"es": "No pude leer el modelo", "en": "Could not read the model",
                "pt": "Não consegui ler o modelo"},
    "pbi_wait": {"es": "Analizando el modelo…", "en": "Analyzing the model…",
                 "pt": "Analisando o modelo…"},
    # ------------------------------------------------- Power BI, modo tenant
    "pbi_mode": {"es": "Modo", "en": "Mode", "pt": "Modo"},
    "pbi_mode_offline": {"es": "📁 Proyecto local (.pbip)", "en": "📁 Local project (.pbip)",
                         "pt": "📁 Projeto local (.pbip)"},
    "pbi_mode_tenant": {"es": "🌐 Tenant completo (Scanner API)", "en": "🌐 Full tenant (Scanner API)",
                        "pt": "🌐 Tenant completo (Scanner API)"},
    "pbi_tenant_off": {
        "es": "Apagado por defecto. Para escanear TODO el tenant, configurá tu propio service "
              "principal como variables de entorno: `POWERBI_TENANT_ID`, `POWERBI_CLIENT_ID`, "
              "`POWERBI_CLIENT_SECRET` — ver docs/BI_TENANT_SCAN.md. Nunca te las pedimos ni las "
              "guardamos.",
        "en": "Off by default. To scan the WHOLE tenant, set your own service principal as "
              "environment variables: `POWERBI_TENANT_ID`, `POWERBI_CLIENT_ID`, "
              "`POWERBI_CLIENT_SECRET` — see docs/BI_TENANT_SCAN.md. We never ask for or store them.",
        "pt": "Desligado por padrão. Para escanear TODO o tenant, configure sua própria service "
              "principal como variáveis de ambiente: `POWERBI_TENANT_ID`, `POWERBI_CLIENT_ID`, "
              "`POWERBI_CLIENT_SECRET` — veja docs/BI_TENANT_SCAN.md. Nunca as pedimos nem as guardamos.",
    },
    "pbi_tenant_hint": {
        "es": "Escanea todos los workspaces activos del tenant vía la Scanner API (Admin REST) — "
              "solo metadata, nunca filas.",
        "en": "Scans every active workspace in the tenant via the Scanner API (Admin REST) — "
              "metadata only, never rows.",
        "pt": "Escaneia todos os workspaces ativos do tenant via a Scanner API (Admin REST) — "
              "apenas metadados, nunca linhas.",
    },
    "pbi_tenant_max_ws": {"es": "Máximo de workspaces a escanear", "en": "Max workspaces to scan",
                          "pt": "Máximo de workspaces a escanear"},
    "pbi_tenant_scan": {"es": "🌐 Escanear tenant completo", "en": "🌐 Scan full tenant",
                        "pt": "🌐 Escanear tenant completo"},
    "pbi_datasets": {"es": "Datasets", "en": "Datasets", "pt": "Datasets"},
    "pbi_tenant_pick_dataset": {"es": "Ver medidas del dataset…", "en": "View measures for dataset…",
                                "pt": "Ver medidas do dataset…"},
    "pbi_mode_example": {"es": "🧪 Ejemplo incluido", "en": "🧪 Bundled example", "pt": "🧪 Exemplo incluído"},
    "pbi_example_kind": {"es": "Qué ejemplo ver", "en": "Which example to view", "pt": "Qual exemplo ver"},
    "pbi_example_single": {
        "es": "Modelo real (Adventure Works Demo, GitHub, MIT)",
        "en": "Real model (Adventure Works Demo, GitHub, MIT)",
        "pt": "Modelo real (Adventure Works Demo, GitHub, MIT)",
    },
    "pbi_example_tenant": {
        "es": "Tenant multinacional (ilustrativo)",
        "en": "Multinational tenant (illustrative)",
        "pt": "Tenant multinacional (ilustrativo)",
    },
    "pbi_example_single_note": {
        "es": "Modelo real de Power BI (10 tablas, 17 medidas DAX) de un repositorio público de "
              "GitHub, licencia MIT — no es sintético. Detalle y atribución completa en "
              "assets/samples/THIRD_PARTY_DATA.md.",
        "en": "A real Power BI model (10 tables, 17 DAX measures) from a public GitHub repo, "
              "MIT licensed — not synthetic. Full details and attribution in "
              "assets/samples/THIRD_PARTY_DATA.md.",
        "pt": "Um modelo real de Power BI (10 tabelas, 17 medidas DAX) de um repositório público "
              "do GitHub, licença MIT — não é sintético. Detalhes e atribuição completa em "
              "assets/samples/THIRD_PARTY_DATA.md.",
    },
    "pbi_example_tenant_note": {
        "es": "⚠️ Ilustrativo, no un escaneo real: es el mismo modelo real de arriba, replicado y "
              "re-etiquetado en varios workspaces simulados, para mostrar cómo se ve "
              "ingest_tenant() a escala en una empresa multinacional. Para un escaneo real de tu "
              "propio tenant, usá el modo 🌐 Tenant completo con tus credenciales.",
        "en": "⚠️ Illustrative, not a real scan: it's the same real model above, replicated and "
              "relabeled across several simulated workspaces, to show what ingest_tenant() looks "
              "like at multinational scale. For a real scan of your own tenant, use 🌐 Full tenant "
              "mode with your own credentials.",
        "pt": "⚠️ Ilustrativo, não um escaneamento real: é o mesmo modelo real acima, replicado e "
              "reetiquetado em vários workspaces simulados, para mostrar como fica o "
              "ingest_tenant() em escala numa multinacional. Para um escaneamento real do seu "
              "próprio tenant, use o modo 🌐 Tenant completo com suas credenciais.",
    },
    # ---------------------------------------------------------------- Tableau
    "tab_tableau": {"es": "📊 Tableau", "en": "📊 Tableau", "pt": "📊 Tableau"},
    "tab_intro": {
        "es": "Gobierná tu sitio de Tableau: workbooks, datasources publicados, campos "
              "calculados y su origen — solo estructura, nunca tus filas.",
        "en": "Govern your Tableau site: workbooks, published datasources, calculated "
              "fields and their source — structure only, never your rows.",
        "pt": "Governe seu site do Tableau: workbooks, datasources publicados, campos "
              "calculados e sua origem — apenas estrutura, nunca suas linhas.",
    },
    "tab_off": {
        "es": "Apagado por defecto. Para escanear tu sitio, configurá tu propio Personal "
              "Access Token como variables de entorno: `TABLEAU_SERVER_URL`, "
              "`TABLEAU_TOKEN_NAME`, `TABLEAU_TOKEN_SECRET` (y opcional `TABLEAU_SITE`) — "
              "ver docs/BI_TENANT_SCAN.md. Nunca te lo pedimos ni lo guardamos.",
        "en": "Off by default. To scan your site, set your own Personal Access Token as "
              "environment variables: `TABLEAU_SERVER_URL`, `TABLEAU_TOKEN_NAME`, "
              "`TABLEAU_TOKEN_SECRET` (and optionally `TABLEAU_SITE`) — see "
              "docs/BI_TENANT_SCAN.md. We never ask for or store it.",
        "pt": "Desligado por padrão. Para escanear seu site, configure seu próprio Personal "
              "Access Token como variáveis de ambiente: `TABLEAU_SERVER_URL`, "
              "`TABLEAU_TOKEN_NAME`, `TABLEAU_TOKEN_SECRET` (e opcional `TABLEAU_SITE`) — "
              "veja docs/BI_TENANT_SCAN.md. Nunca o pedimos nem o guardamos.",
    },
    "tab_scan": {"es": "📊 Escanear sitio completo", "en": "📊 Scan full site",
                "pt": "📊 Escanear site completo"},
    "tab_wait": {"es": "Escaneando el sitio…", "en": "Scanning the site…",
                "pt": "Escaneando o site…"},
    "tab_err": {"es": "No pude escanear el sitio", "en": "Could not scan the site",
               "pt": "Não consegui escanear o site"},
    "tab_no_model": {"es": "Escaneá tu sitio para ver su estructura.",
                     "en": "Scan your site to see its structure.",
                     "pt": "Escaneie seu site para ver sua estrutura."},
    "tab_workbooks": {"es": "Workbooks", "en": "Workbooks", "pt": "Workbooks"},
    "tab_datasources": {"es": "Datasources", "en": "Datasources", "pt": "Datasources"},
    "tab_fields": {"es": "Campos", "en": "Fields", "pt": "Campos"},
    "tab_calc_fields": {"es": "Campos calculados", "en": "Calculated fields", "pt": "Campos calculados"},
    "tab_catalog_title": {"es": "📇 Catálogo de datasources", "en": "📇 Datasource catalog",
                          "pt": "📇 Catálogo de datasources"},
    "tab_health_title": {"es": "✅ Salud del sitio", "en": "✅ Site health", "pt": "✅ Saúde do site"},
    "tab_health_overall": {"es": "Índice del sitio", "en": "Site index", "pt": "Índice do site"},
    "tab_sources_title": {"es": "🗄️ Origen por datasource", "en": "🗄️ Source per datasource",
                          "pt": "🗄️ Origem por datasource"},
    "tab_sources_hint": {
        "es": "Tablas de base de datos detectadas como origen de cada datasource publicado.",
        "en": "Database tables detected as the source of each published datasource.",
        "pt": "Tabelas de banco de dados detectadas como origem de cada datasource publicado.",
    },
    "tab_lineage_title": {"es": "🧬 Linaje del sitio", "en": "🧬 Site lineage", "pt": "🧬 Linhagem do site"},
    "tab_lineage_hint": {
        "es": "Cadena completa: tabla de base de datos → datasource publicado → workbook.",
        "en": "Full chain: database table → published datasource → workbook.",
        "pt": "Cadeia completa: tabela de banco de dados → datasource publicado → workbook.",
    },
    "tab_calc_title": {"es": "📖 Campos calculados (glosario)", "en": "📖 Calculated fields (glossary)",
                       "pt": "📖 Campos calculados (glossário)"},
    "tab_refactor": {"es": "✨ Refactor con {provider}", "en": "✨ Refactor with {provider}",
                     "pt": "✨ Refatorar com {provider}"},
    "tab_refactor_hint": {
        "es": "Con tu API key configurada, pedile a la IA que audite y mejore la fórmula "
              "(se manda solo la fórmula, nunca datos).",
        "en": "With your API key set, ask the AI to audit and improve the formula "
              "(only the formula is sent, never data).",
        "pt": "Com sua API key configurada, peça à IA para auditar e melhorar a fórmula "
              "(envia-se apenas a fórmula, nunca dados).",
    },
    "tab_r_formula": {"es": "Fórmula refactorizada", "en": "Refactored formula", "pt": "Fórmula refatorada"},
    "tab_mode": {"es": "Modo", "en": "Mode", "pt": "Modo"},
    "tab_mode_offline": {"es": "📁 Workbook local (.twb/.twbx)", "en": "📁 Local workbook (.twb/.twbx)",
                         "pt": "📁 Workbook local (.twb/.twbx)"},
    "tab_mode_site": {"es": "🌐 Sitio completo (Metadata API)", "en": "🌐 Full site (Metadata API)",
                      "pt": "🌐 Site completo (Metadata API)"},
    "tab_mode_example": {"es": "🧪 Ejemplo incluido", "en": "🧪 Bundled example", "pt": "🧪 Exemplo incluído"},
    "tab_path": {"es": "Ruta al archivo .twb o .twbx", "en": "Path to the .twb or .twbx file",
                "pt": "Caminho para o arquivo .twb ou .twbx"},
    "tab_path_hint": {
        "es": "Un .twbx trae extractos de datos empaquetados — el programa nunca los lee, solo "
              "el XML de estructura (.twb) adentro.",
        "en": "A .twbx bundles packaged data extracts — the program never reads them, only the "
              "structure XML (.twb) inside.",
        "pt": "Um .twbx traz extratos de dados empacotados — o programa nunca os lê, apenas o "
              "XML de estrutura (.twb) dentro.",
    },
    "tab_upload": {"es": "Subir archivo .twb/.twbx", "en": "Upload .twb/.twbx file",
                  "pt": "Enviar arquivo .twb/.twbx"},
    "tab_load": {"es": "Analizar workbook", "en": "Analyze workbook", "pt": "Analisar workbook"},
    "tab_example_note": {
        "es": "Workbook de ejemplo escrito originalmente para este programa (no descargado de "
              "GitHub — los repos públicos encontrados no tenían licencia clara). Detalle en "
              "assets/samples/THIRD_PARTY_DATA.md.",
        "en": "Example workbook written originally for this program (not downloaded from GitHub "
              "— the public repos found had no clear license). Details in "
              "assets/samples/THIRD_PARTY_DATA.md.",
        "pt": "Workbook de exemplo escrito originalmente para este programa (não baixado do "
              "GitHub — os repositórios públicos encontrados não tinham licença clara). "
              "Detalhes em assets/samples/THIRD_PARTY_DATA.md.",
    },
    # ------------------------------------------------------------------ MDM
    "mdm_intro": {
        "es": "**Master Data Management**: encuentra filas que probablemente representen la "
              "MISMA entidad (cliente, producto…) con datos levemente distintos, y arma el "
              "**golden record** que las unifica. Matching por reglas ponderadas, 100% local.",
        "en": "**Master Data Management**: finds rows that likely represent the SAME entity "
              "(customer, product…) with slightly different data, and builds the **golden "
              "record** that unifies them. Weighted rule matching, 100% local.",
        "pt": "**Master Data Management**: encontra linhas que provavelmente representam a "
              "MESMA entidade (cliente, produto…) com dados levemente diferentes, e monta o "
              "**golden record** que as unifica. Matching por regras ponderadas, 100% local.",
    },
    "mdm_warning": {
        "es": "⚠️ Un nombre común (\"Ana Costa\") solo no alcanza para marcar un duplicado — "
              "hace falta que además coincida un identificador fuerte (documento, email). Así "
              "se evitan falsos positivos entre personas distintas con el mismo nombre.",
        "en": "⚠️ A common name (\"Ana Costa\") alone isn't enough to flag a duplicate — a "
              "strong identifier (ID, email) must also match. This avoids false positives "
              "between different people sharing a name.",
        "pt": "⚠️ Um nome comum (\"Ana Costa\") sozinho não basta para marcar um duplicado — é "
              "preciso que um identificador forte (documento, email) também coincida. Isso "
              "evita falsos positivos entre pessoas diferentes com o mesmo nome.",
    },
    "mdm_pick_dataset": {"es": "Dataset a analizar", "en": "Dataset to analyze", "pt": "Dataset a analisar"},
    "mdm_src_demo": {"es": "demo sintético", "en": "synthetic demo", "pt": "demo sintético"},
    "mdm_pick_columns": {"es": "Columnas para buscar duplicados",
                         "en": "Columns to search for duplicates",
                         "pt": "Colunas para buscar duplicados"},
    "mdm_block_column": {
        "es": "Agrupar por (acelera la comparación en datasets grandes)",
        "en": "Group by (speeds up comparison on large datasets)",
        "pt": "Agrupar por (acelera a comparação em datasets grandes)",
    },
    "mdm_no_block": {"es": "— sin agrupar —", "en": "— no grouping —", "pt": "— sem agrupar —"},
    "mdm_min_confidence": {"es": "Confianza mínima (%)", "en": "Minimum confidence (%)",
                           "pt": "Confiança mínima (%)"},
    "mdm_run": {"es": "🔗 Buscar duplicados", "en": "🔗 Find duplicates", "pt": "🔗 Buscar duplicados"},
    "mdm_wait": {"es": "Comparando filas…", "en": "Comparing rows…", "pt": "Comparando linhas…"},
    "mdm_none_found": {
        "es": "No se encontraron duplicados con esta confianza mínima y estas columnas.",
        "en": "No duplicates found with this minimum confidence and these columns.",
        "pt": "Nenhum duplicado encontrado com esta confiança mínima e estas colunas.",
    },
    "mdm_results": {"es": "{n} clusters de posibles duplicados encontrados",
                    "en": "{n} possible-duplicate clusters found",
                    "pt": "{n} clusters de possíveis duplicados encontrados"},
    "mdm_col_cluster": {"es": "Cluster", "en": "Cluster", "pt": "Cluster"},
    "mdm_col_rows": {"es": "Filas", "en": "Rows", "pt": "Linhas"},
    "mdm_col_confidence": {"es": "Confianza (%)", "en": "Confidence (%)", "pt": "Confiança (%)"},
    "mdm_col_matched": {"es": "Coincide en", "en": "Matched on", "pt": "Coincide em"},
    "mdm_rows_label": {"es": "filas", "en": "rows", "pt": "linhas"},
    "mdm_cols_label": {"es": "columnas", "en": "columns", "pt": "colunas"},
    "mdm_golden_title": {"es": "✨ Golden record propuesto", "en": "✨ Proposed golden record",
                         "pt": "✨ Golden record proposto"},
}


def t(key: str, lang: str = DEFAULT_LANG) -> str:
    """Traduce ``key`` al idioma ``lang`` (cae a español si falta)."""
    entry = _T.get(key)
    if entry is None:
        return key
    return entry.get(lang) or entry[DEFAULT_LANG]


def all_keys() -> list[str]:
    return list(_T.keys())
