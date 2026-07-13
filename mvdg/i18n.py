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
    "h_dmbok": {"es": "Marco DAMA-DMBOK: las 11 áreas del gobierno de datos",
                "en": "DAMA-DMBOK framework: the 11 data-governance areas",
                "pt": "Marco DAMA-DMBOK: as 11 áreas da governança de dados"},
    "h_dmbok_note": {
        "es": "El DMBOK (Data Management Body of Knowledge) es el estándar de "
              "referencia de la industria en gobierno de datos, publicado por "
              "DAMA International. Acá está explicado dos veces: en criollo, "
              "para quien no es técnico, y con el detalle técnico. Con qué "
              "color cubre esta plataforma cada área, sin exagerar.",
        "en": "The DMBOK (Data Management Body of Knowledge) is the industry "
              "reference standard for data governance, published by DAMA "
              "International. It's explained twice here: in plain words, for "
              "non-technical readers, and with technical detail. Color-coded "
              "with how much this platform actually covers each area.",
        "pt": "O DMBOK (Data Management Body of Knowledge) é o padrão de "
              "referência da indústria em governança de dados, publicado pela "
              "DAMA International. Está explicado duas vezes aqui: em "
              "linguagem simples, para quem não é técnico, e com o detalhe "
              "técnico. Com a cor de quanto esta plataforma cobre cada área, "
              "sem exagerar.",
    },
    "h_dmbok_plain": {"es": "En criollo", "en": "In plain words", "pt": "Em linguagem simples"},
    "h_dmbok_tech": {"es": "Detalle técnico", "en": "Technical detail", "pt": "Detalhe técnico"},
    "h_dmbok_covered": {"es": "✅ Cubierta", "en": "✅ Covered", "pt": "✅ Coberta"},
    "h_dmbok_partial": {"es": "🟡 Parcial", "en": "🟡 Partial", "pt": "🟡 Parcial"},
    "h_dmbok_out": {"es": "⬜ Fuera de alcance", "en": "⬜ Out of scope", "pt": "⬜ Fora de escopo"},
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
}


def t(key: str, lang: str = DEFAULT_LANG) -> str:
    """Traduce ``key`` al idioma ``lang`` (cae a español si falta)."""
    entry = _T.get(key)
    if entry is None:
        return key
    return entry.get(lang) or entry[DEFAULT_LANG]


def all_keys() -> list[str]:
    return list(_T.keys())
