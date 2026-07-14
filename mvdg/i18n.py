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
    "tab_clients": {"es": "🏢 Empresas", "en": "🏢 Companies", "pt": "🏢 Empresas"},
    "tab_help": {"es": "❓ Ayuda", "en": "❓ Help", "pt": "❓ Ajuda"},
    "tab_lab": {"es": "🧪 Laboratorio", "en": "🧪 Lab", "pt": "🧪 Laboratório"},
    "tab_dmbok": {"es": "📘 DMBOK", "en": "📘 DMBOK", "pt": "📘 DMBOK"},
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
        "es": "Conectate directo a tu base de datos (PostgreSQL, MySQL, SQL "
              "Server, Oracle, SQLite). Cargás servidor, usuario y contraseña, "
              "los guardás y traés tus tablas al gobierno — igual que un CSV.",
        "en": "Connect directly to your database (PostgreSQL, MySQL, SQL "
              "Server, Oracle, SQLite). Enter host, user and password, save "
              "them and bring your tables into governance — just like a CSV.",
        "pt": "Conecte-se direto ao seu banco de dados (PostgreSQL, MySQL, SQL "
              "Server, Oracle, SQLite). Informe host, usuário e senha, salve-os "
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
}


def t(key: str, lang: str = DEFAULT_LANG) -> str:
    """Traduce ``key`` al idioma ``lang`` (cae a español si falta)."""
    entry = _T.get(key)
    if entry is None:
        return key
    return entry.get(lang) or entry[DEFAULT_LANG]


def all_keys() -> list[str]:
    return list(_T.keys())
