# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
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
    # -------------------------------------------------- entregable final (del)
    "del_intro": {
        "es": "El entregable final de cada caso: lo que un consultor deja sobre la mesa al terminar el trabajo de gobernanza — ficha, KPIs finales de calidad/documentación/curaduría, diccionario, reglas, glosario, linaje y el estado de migración a Purview/Collibra. Descargable en Excel y como resumen ejecutivo.",
        "en": "The final deliverable for each case: what a consultant leaves on the table when the governance work is done — overview, final quality/documentation/curation KPIs, dictionary, rules, glossary, lineage and Purview/Collibra migration readiness. Downloadable as Excel and as an executive summary.",
        "pt": "O entregável final de cada caso: o que um consultor deixa na mesa ao terminar o trabalho de governança — ficha, KPIs finais de qualidade/documentação/curadoria, dicionário, regras, glossário, linhagem e prontidão de migração para Purview/Collibra. Baixável em Excel e como resumo executivo.",
    },
    "del_pick": {"es": "Caso", "en": "Case", "pt": "Caso"},
    "del_owner": {"es": "Dueño", "en": "Owner", "pt": "Dono"},
    "del_source": {"es": "Fuente", "en": "Source", "pt": "Fonte"},
    "del_kpi_rows": {"es": "Filas × columnas", "en": "Rows × columns", "pt": "Linhas × colunas"},
    "del_kpi_rules": {"es": "Reglas OK", "en": "Rules OK", "pt": "Regras OK"},
    "del_kpi_curation": {"es": "Curaduría revisada", "en": "Curation reviewed", "pt": "Curadoria revisada"},
    "del_kpi_documented": {"es": "Columnas documentadas", "en": "Documented columns", "pt": "Colunas documentadas"},
    "del_kpi_pii": {"es": "Columnas PII", "en": "PII columns", "pt": "Colunas PII"},
    "del_kpi_fails": {"es": "Hallazgos (con plan)", "en": "Findings (with plan)", "pt": "Achados (com plano)"},
    "tab_contracts": {"es": "Contratos", "en": "Contracts", "pt": "Contratos"},
    "mcp_tab_title": {"es": "MCP: IA sobre Tableau y sobre tu gobernanza", "en": "MCP: AI over Tableau and over your governance", "pt": "MCP: IA sobre o Tableau e sobre sua governança"},
    "mcp_tab_body": {
        "es": "Tableau también tiene su servidor MCP oficial: **@tableau/mcp-server** (npm, Apache-2.0). Corre local por stdio y conecta clientes de IA con Tableau Server/Cloud vía las APIs REST y VizQL Data Service: listar y consultar datasources en lenguaje natural (query-datasource vía VizQL Data Service), workbooks, vistas (datos e imagen), métricas Pulse con insights, y búsqueda de contenido. Son 37 herramientas en total (v3.0.0, 2026-07-15); con la config por defecto se publican 21 — las de administración y Prep vienen apagadas (ADMIN_TOOLS_ENABLED / FLOW_TOOLS_ENABLED). Requiere Node 22.7.5+; se configura con variables de entorno (SERVER, SITE_NAME, PAT_NAME, PAT_VALUE — Personal Access Token) y valida la conexión al arrancar: sin un Tableau accesible no publica herramientas. Para Tableau Cloud también existe el servicio hosteado oficial mcp.tableau.com (OAuth 2.1). Estado: «Tableau Supported» (el nivel de soporte oficial más alto de sus developer tools).",
        "en": "Tableau also ships an official MCP server: **@tableau/mcp-server** (npm, Apache-2.0). It runs locally over stdio and connects AI clients to Tableau Server/Cloud via the REST APIs and VizQL Data Service: list and query datasources in natural language (query-datasource via the VizQL Data Service), workbooks, views (data and image), Pulse metrics with insights, and content search. There are 37 tools in total (v3.0.0, 2026-07-15); the default config publishes 21 — admin and Prep tools ship disabled (ADMIN_TOOLS_ENABLED / FLOW_TOOLS_ENABLED). Requires Node 22.7.5+; configured via environment variables (SERVER, SITE_NAME, PAT_NAME, PAT_VALUE — Personal Access Token) and it validates the connection at startup: without a reachable Tableau it publishes no tools. For Tableau Cloud there is also the official hosted service mcp.tableau.com (OAuth 2.1). Status: «Tableau Supported» (the highest official support tier for their developer tools).",
        "pt": "O Tableau também tem seu servidor MCP oficial: **@tableau/mcp-server** (npm, Apache-2.0). Roda localmente via stdio e conecta clientes de IA ao Tableau Server/Cloud pelas APIs REST e VizQL Data Service: listar e consultar datasources em linguagem natural (query-datasource via VizQL Data Service), workbooks, vistas (dados e imagem), métricas Pulse com insights, e busca de conteúdo. São 37 ferramentas no total (v3.0.0, 2026-07-15); com a config padrão publicam-se 21 — as de administração e Prep vêm desligadas (ADMIN_TOOLS_ENABLED / FLOW_TOOLS_ENABLED). Requer Node 22.7.5+; configura-se com variáveis de ambiente (SERVER, SITE_NAME, PAT_NAME, PAT_VALUE — Personal Access Token) e valida a conexão ao iniciar: sem um Tableau acessível não publica ferramentas. Para o Tableau Cloud também existe o serviço hospedado oficial mcp.tableau.com (OAuth 2.1). Status: «Tableau Supported» (o nível de suporte oficial mais alto de suas developer tools).",
    },
    "mcp_tab_cfg": {"es": "Config para cualquier cliente MCP (Claude Code, VS Code):", "en": "Config for any MCP client (Claude Code, VS Code):", "pt": "Config para qualquer cliente MCP (Claude Code, VS Code):"},
    "mcp_tab_verified": {
        "es": "Verificado en laboratorio (2026-07-19): el cliente MCP de este programa lanzó el binario oficial 3.0.0, completó el handshake del protocolo real y listó sus 21 herramientas (con un Tableau simulado local para el chequeo de arranque). Contra un Tableau Server/Cloud VIVO no se probó — mismo criterio de honestidad que Purview/Collibra. Ese circuito está automatizado como test del repo.",
        "en": "Lab-verified (2026-07-19): this program's MCP client launched the official 3.0.0 binary, completed the real protocol handshake and listed its 21 tools (with a local simulated Tableau for the startup check). It was NOT tested against a LIVE Tableau Server/Cloud — same honesty standard as Purview/Collibra. That circuit is automated as a repo test.",
        "pt": "Verificado em laboratório (2026-07-19): o cliente MCP deste programa iniciou o binário oficial 3.0.0, completou o handshake do protocolo real e listou suas 21 ferramentas (com um Tableau simulado local para a checagem de inicialização). NÃO foi testado contra um Tableau Server/Cloud AO VIVO — mesmo critério de honestidade de Purview/Collibra. Esse circuito está automatizado como teste do repositório.",
    },
    "mcp_tab_caveats": {
        "es": "A tener en cuenta (docs oficiales): ① la telemetría de producto de Tableau viene ENCENDIDA por defecto — apagala con PRODUCT_TELEMETRY_ENABLED=false si querés la misma política sin telemetría de este programa; ② un PAT no admite uso concurrente y expira a los 15 días sin uso; ③ Pulse no está disponible en Tableau Server (sí en Cloud); ④ requiere VizQL Data Service habilitado y permiso «API access» sobre los datasources; ⑤ cadencia de releases rápida con cambios incompatibles — fijá la versión (@3.0.0) en vez de @latest para producción.",
        "en": "Worth knowing (official docs): ① Tableau product telemetry ships ON by default — turn it off with PRODUCT_TELEMETRY_ENABLED=false if you want this program's same no-telemetry policy; ② a PAT does not support concurrent use and expires after 15 days unused; ③ Pulse is not available on Tableau Server (Cloud only); ④ requires VizQL Data Service enabled and «API access» permission on datasources; ⑤ fast release cadence with breaking changes — pin the version (@3.0.0) instead of @latest for production.",
        "pt": "Vale saber (docs oficiais): ① a telemetria de produto do Tableau vem LIGADA por padrão — desligue com PRODUCT_TELEMETRY_ENABLED=false se quiser a mesma política sem telemetria deste programa; ② um PAT não admite uso concorrente e expira após 15 dias sem uso; ③ Pulse não está disponível no Tableau Server (só no Cloud); ④ requer VizQL Data Service habilitado e permissão «API access» nos datasources; ⑤ cadência rápida de releases com mudanças incompatíveis — fixe a versão (@3.0.0) em vez de @latest para produção.",
    },
    "mcp_tab_gov": {
        "es": "Y al revés: tu gobernanza también es consultable por IA — el servidor MCP propio del programa (ver pestaña Power BI, sección MCP) expone catálogo, calidad, linaje, contratos y alertas de los datasets que alimentan tus dashboards de Tableau.",
        "en": "And the other way around: your governance is also queryable by AI — the program's own MCP server (see Power BI tab, MCP section) exposes catalog, quality, lineage, contracts and alerts for the datasets feeding your Tableau dashboards.",
        "pt": "E no sentido inverso: sua governança também é consultável por IA — o servidor MCP próprio do programa (ver aba Power BI, seção MCP) expõe catálogo, qualidade, linhagem, contratos e alertas dos datasets que alimentam seus dashboards do Tableau.",
    },
    "mcp_title": {"es": "MCP: IA sobre tus modelos de Power BI y sobre tu gobernanza", "en": "MCP: AI over your Power BI models and your governance", "pt": "MCP: IA sobre seus modelos do Power BI e sua governança"},
    "mcp_intro": {
        "es": "MCP (Model Context Protocol) es el estándar abierto que conecta clientes de IA (Claude, VS Code, Copilot) con tus datos y herramientas. Microsoft publicó dos servidores MCP oficiales para Power BI, y este programa suma un tercero: tu propia capa de gobernanza consultable por IA. Verificado contra la documentación oficial de Microsoft Learn el 2026-07-19; ambos servidores de Microsoft están en Public Preview (los esquemas pueden cambiar).",
        "en": "MCP (Model Context Protocol) is the open standard connecting AI clients (Claude, VS Code, Copilot) to your data and tools. Microsoft published two official MCP servers for Power BI, and this program adds a third one: your own governance layer, queryable by AI. Verified against official Microsoft Learn docs on 2026-07-19; both Microsoft servers are in Public Preview (schemas may change).",
        "pt": "MCP (Model Context Protocol) é o padrão aberto que conecta clientes de IA (Claude, VS Code, Copilot) aos seus dados e ferramentas. A Microsoft publicou dois servidores MCP oficiais para o Power BI, e este programa adiciona um terceiro: sua própria camada de governança consultável por IA. Verificado contra a documentação oficial do Microsoft Learn em 2026-07-19; ambos os servidores da Microsoft estão em Public Preview (os esquemas podem mudar).",
    },
    "mcp_local_title": {"es": "MCP local — Power BI Modeling MCP Server (Public Preview)", "en": "Local MCP — Power BI Modeling MCP Server (Public Preview)", "pt": "MCP local — Power BI Modeling MCP Server (Public Preview)"},
    "mcp_local_body": {
        "es": "Trabaja sobre un modelo ABIERTO en Power BI Desktop (también workspaces de Fabric y proyectos PBIP/TMDL). Crea y edita tablas, columnas, medidas y relaciones en lenguaje natural, aplica cambios masivos con soporte de transacciones, y valida/ejecuta DAX antes de publicar. Solo operaciones de modelado (no edita reportes). Transporte stdio; se lanza con `npx -y @microsoft/powerbi-modeling-mcp@latest --start` (Node 20+), como extensión de VS Code o como ejecutable de Windows. Por defecto pide confirmación antes de modificar el modelo.",
        "en": "Works on a model OPEN in Power BI Desktop (also Fabric workspaces and PBIP/TMDL projects). Creates and edits tables, columns, measures and relationships in natural language, applies bulk changes with transaction support, and validates/executes DAX before publishing. Modeling operations only (no report editing). stdio transport; launched with `npx -y @microsoft/powerbi-modeling-mcp@latest --start` (Node 20+), as a VS Code extension or a Windows executable. By default it asks for confirmation before modifying the model.",
        "pt": "Trabalha sobre um modelo ABERTO no Power BI Desktop (também workspaces do Fabric e projetos PBIP/TMDL). Cria e edita tabelas, colunas, medidas e relações em linguagem natural, aplica mudanças em massa com suporte a transações, e valida/executa DAX antes de publicar. Somente operações de modelagem (não edita relatórios). Transporte stdio; é lançado com `npx -y @microsoft/powerbi-modeling-mcp@latest --start` (Node 20+), como extensão do VS Code ou executável do Windows. Por padrão pede confirmação antes de modificar o modelo.",
    },
    "mcp_remote_title": {"es": "MCP remoto — servidor de Power BI en Fabric (Preview)", "en": "Remote MCP — Power BI server in Fabric (Preview)", "pt": "MCP remoto — servidor do Power BI no Fabric (Preview)"},
    "mcp_remote_body": {
        "es": "Trabaja sobre modelos semánticos PUBLICADOS en el Service. Endpoint oficial: `https://api.fabric.microsoft.com/v1/mcp/powerbi` (Streamable HTTP — no es una REST API tradicional; se accede vía clientes MCP). Autenticación con Entra ID (OAuth): las consultas corren con los permisos del usuario (requiere permiso Build sobre el modelo) y respetan RLS con usuario autenticado — ojo: con service principal la RLS NO se aplica (advertencia oficial). Herramientas: ejecutar DAX, obtener el esquema del modelo (tablas/columnas/medidas/relaciones), metadata de reportes, y generar DAX desde lenguaje natural (esta última usa el motor de Copilot y requiere licencia/capacidad Copilot). Requiere que el admin del tenant habilite el setting de MCP (preview).",
        "en": "Works on semantic models PUBLISHED to the Service. Official endpoint: `https://api.fabric.microsoft.com/v1/mcp/powerbi` (Streamable HTTP — not a traditional REST API; accessed via MCP clients). Entra ID (OAuth) auth: queries run under the user's permissions (Build permission required on the model) and respect RLS with user auth — note: with a service principal RLS is NOT enforced (official warning). Tools: execute DAX, get the model schema (tables/columns/measures/relationships), report metadata, and generate DAX from natural language (the latter uses the Copilot engine and requires a Copilot license/capacity). Requires the tenant admin to enable the MCP (preview) setting.",
        "pt": "Trabalha sobre modelos semânticos PUBLICADOS no Service. Endpoint oficial: `https://api.fabric.microsoft.com/v1/mcp/powerbi` (Streamable HTTP — não é uma REST API tradicional; acessa-se via clientes MCP). Autenticação com Entra ID (OAuth): as consultas rodam com as permissões do usuário (requer permissão Build no modelo) e respeitam RLS com usuário autenticado — atenção: com service principal a RLS NÃO é aplicada (aviso oficial). Ferramentas: executar DAX, obter o esquema do modelo (tabelas/colunas/medidas/relações), metadata de relatórios, e gerar DAX a partir de linguagem natural (esta última usa o motor do Copilot e requer licença/capacidade Copilot). Requer que o admin do tenant habilite a configuração de MCP (preview).",
    },
    "mcp_docs_note": {
        "es": "Fuentes oficiales: learn.microsoft.com → Power BI developer → MCP (overview, get started remoto, herramientas, clientes externos) y github.com/microsoft/powerbi-modeling-mcp. Para conectar clientes que no son de Microsoft (p. ej. Claude) al servidor remoto hay que registrar una app propia en Entra ID (Microsoft lo documenta paso a paso, página «external clients»); este programa NO maneja esas credenciales por diseño — la conexión es directa entre tu cliente MCP y Microsoft.",
        "en": "Official sources: learn.microsoft.com → Power BI developer → MCP (overview, remote get started, tools, external clients) and github.com/microsoft/powerbi-modeling-mcp. To connect non-Microsoft clients (e.g., Claude) to the remote server you must register your own Entra ID app (Microsoft documents it step by step on the «external clients» page); this program does NOT handle those credentials by design — the connection is direct between your MCP client and Microsoft.",
        "pt": "Fontes oficiais: learn.microsoft.com → Power BI developer → MCP (overview, get started remoto, ferramentas, clientes externos) e github.com/microsoft/powerbi-modeling-mcp. Para conectar clientes que não são da Microsoft (p. ex. Claude) ao servidor remoto é preciso registrar um app próprio no Entra ID (a Microsoft documenta passo a passo na página «external clients»); este programa NÃO manipula essas credenciais por design — a conexão é direta entre seu cliente MCP e a Microsoft.",
    },
    "mcp_expose_title": {"es": "Exponer TU gobernanza por MCP (servidor propio incluido)", "en": "Expose YOUR governance via MCP (own server included)", "pt": "Expor SUA governança via MCP (servidor próprio incluído)"},
    "mcp_expose_body": {
        "es": "El programa incluye su propio servidor MCP: 9 herramientas de solo lectura sobre la capa de gobierno (catálogo, diccionario con PII, glosario, calidad real, linaje, contratos de datos, alertas, entregables por caso y búsqueda). Así, desde Claude o VS Code podés preguntar «¿qué columnas PII hay?», «¿qué contratos incumplen y a quién afectan?» o «dame el entregable del laboratorio» — la IA consulta TU gobernanza, no adivina. Solo metadata (nunca filas de datos), transporte stdio local (nada viaja a internet) y apagado por defecto: corre únicamente si vos lo configurás.",
        "en": "The program ships its own MCP server: 9 read-only tools over the governance layer (catalog, dictionary with PII, glossary, real quality, lineage, data contracts, alerts, per-case deliverables and search). From Claude or VS Code you can ask «which PII columns exist?», «which contracts are breached and who is affected?» or «give me the lab deliverable» — the AI queries YOUR governance instead of guessing. Metadata only (never data rows), local stdio transport (nothing travels to the internet) and off by default: it runs only if you configure it.",
        "pt": "O programa inclui seu próprio servidor MCP: 9 ferramentas somente leitura sobre a camada de governança (catálogo, dicionário com PII, glossário, qualidade real, linhagem, contratos de dados, alertas, entregáveis por caso e busca). Do Claude ou VS Code você pode perguntar «quais colunas PII existem?», «quais contratos descumprem e quem é afetado?» ou «me dá o entregável do laboratório» — a IA consulta SUA governança em vez de adivinhar. Somente metadata (nunca linhas de dados), transporte stdio local (nada viaja para a internet) e desligado por padrão: roda só se você configurar.",
    },
    "mcp_expose_status_ok": {"es": "SDK de MCP instalado — el servidor propio está listo para usarse.", "en": "MCP SDK installed — the built-in server is ready to use.", "pt": "SDK do MCP instalado — o servidor próprio está pronto para uso."},
    "mcp_expose_status_missing": {"es": "SDK de MCP no instalado. Instalalo con: pip install mcp (ya figura en requirements.txt).", "en": "MCP SDK not installed. Install it with: pip install mcp (already listed in requirements.txt).", "pt": "SDK do MCP não instalado. Instale com: pip install mcp (já listado em requirements.txt)."},
    "mcp_cfg_claude": {"es": "Configurarlo en Claude Code (terminal):", "en": "Configure it in Claude Code (terminal):", "pt": "Configurar no Claude Code (terminal):"},
    "mcp_cfg_vscode": {"es": "Configurarlo en VS Code (mcp.json):", "en": "Configure it in VS Code (mcp.json):", "pt": "Configurar no VS Code (mcp.json):"},
    "mcp_cfg_pbi_local": {"es": "Y para el Power BI Modeling MCP oficial (cualquier cliente MCP, config del repo de Microsoft):", "en": "And for the official Power BI Modeling MCP (any MCP client, config from Microsoft's repo):", "pt": "E para o Power BI Modeling MCP oficial (qualquer cliente MCP, config do repositório da Microsoft):"},
    "mcp_try_btn": {"es": "Probar el servidor propio (roundtrip real por stdio)", "en": "Try the built-in server (real stdio roundtrip)", "pt": "Testar o servidor próprio (roundtrip real via stdio)"},
    "mcp_try_note": {
        "es": "Lanza el servidor MCP del programa como subproceso, le pide la lista de herramientas por el protocolo real y la muestra. Es la misma verificación que corre el selfcheck.",
        "en": "Spawns the program's MCP server as a subprocess, requests its tool list over the real protocol and shows it. Same verification the selfcheck runs.",
        "pt": "Inicia o servidor MCP do programa como subprocesso, pede a lista de ferramentas pelo protocolo real e a mostra. É a mesma verificação que o selfcheck executa.",
    },
    "mcp_try_ok": {"es": "Roundtrip OK — {n} herramientas publicadas por el servidor propio.", "en": "Roundtrip OK — {n} tools published by the built-in server.", "pt": "Roundtrip OK — {n} ferramentas publicadas pelo servidor próprio."},
    "mcp_honest_note": {
        "es": "Transparencia: el circuito MCP del programa (servidor propio + cliente) está probado end-to-end con transporte stdio real en tests y selfcheck. Contra los servidores oficiales de Microsoft NO se probó en vivo (requieren Power BI Desktop/tenant de Fabric); la integración está implementada y documentada según Microsoft Learn, con fecha de verificación — el mismo criterio de honestidad que los conectores de Purview y Collibra. Advertencia de gobernanza de Microsoft: los clientes MCP actúan con los permisos del usuario — un agente mal configurado puede ejecutar acciones destructivas en el modelo; revisá qué cliente conectás y con qué cuenta.",
        "en": "Transparency: the program's MCP circuit (own server + client) is tested end-to-end over real stdio transport in tests and selfcheck. It was NOT live-tested against Microsoft's official servers (they require Power BI Desktop / a Fabric tenant); the integration is implemented and documented per Microsoft Learn, with verification date — the same honesty standard as the Purview and Collibra connectors. Microsoft governance warning: MCP clients act under the user's permissions — a misconfigured agent can perform destructive actions on the model; review which client you connect and with which account.",
        "pt": "Transparência: o circuito MCP do programa (servidor próprio + cliente) é testado end-to-end com transporte stdio real em testes e selfcheck. NÃO foi testado ao vivo contra os servidores oficiais da Microsoft (exigem Power BI Desktop / tenant do Fabric); a integração está implementada e documentada conforme o Microsoft Learn, com data de verificação — o mesmo critério de honestidade dos conectores Purview e Collibra. Aviso de governança da Microsoft: clientes MCP agem com as permissões do usuário — um agente mal configurado pode executar ações destrutivas no modelo; revise qual cliente você conecta e com qual conta.",
    },
    "con_intro": {
        "es": "Cada dataset gobernado se trata como un PRODUCTO de datos: con dominio, roles (Domain Owner, Product Owner, Productor, Consumidor), un contrato con reglas/umbrales/SLA, y alarmística que dice a quién afecta cada incumplimiento aguas abajo del linaje. Todo se evalúa contra la última corrida real de reglas — nada está simulado.",
        "en": "Every governed dataset is treated as a data PRODUCT: with a domain, roles (Domain Owner, Product Owner, Producer, Consumer), a contract with rules/thresholds/SLA, and alerting that tells who is affected downstream in the lineage by each breach. Everything is evaluated against the latest real rule run — nothing is simulated.",
        "pt": "Cada dataset governado é tratado como um PRODUTO de dados: com domínio, papéis (Domain Owner, Product Owner, Produtor, Consumidor), um contrato com regras/limiares/SLA, e alarmística que diz quem é afetado rio abaixo na linhagem por cada descumprimento. Tudo é avaliado contra a última execução real de regras — nada é simulado.",
    },
    "con_theory": {"es": "Marco teórico: Data Mesh, Data Products y contratos de datos", "en": "Theory: Data Mesh, Data Products and data contracts", "pt": "Marco teórico: Data Mesh, Data Products e contratos de dados"},
    "con_theory_note": {
        "es": "Cada concepto en dos capas: qué significa (en criollo) y con qué pieza concreta de este programa se practica. Complementa los marcos DAMA-DMBOK, COBIT e ISO 38505 de la pestaña DMBOK.",
        "en": "Each concept in two layers: what it means (plainly) and which concrete piece of this program puts it into practice. It complements the DAMA-DMBOK, COBIT and ISO 38505 frameworks in the DMBOK tab.",
        "pt": "Cada conceito em duas camadas: o que significa (em linguagem simples) e com qual peça concreta deste programa se pratica. Complementa os marcos DAMA-DMBOK, COBIT e ISO 38505 da aba DMBOK.",
    },
    "con_kpi_products": {"es": "Productos de datos", "en": "Data products", "pt": "Produtos de dados"},
    "con_kpi_ok": {"es": "Contratos que cumplen", "en": "Compliant contracts", "pt": "Contratos que cumprem"},
    "con_kpi_risk": {"es": "En riesgo", "en": "At risk", "pt": "Em risco"},
    "con_kpi_breach": {"es": "Incumplidos", "en": "Breached", "pt": "Descumpridos"},
    "con_kpi_alerts": {"es": "Alertas activas", "en": "Active alerts", "pt": "Alertas ativos"},
    "con_kpi_signed": {"es": "Acuerdos firmados", "en": "Signed agreements", "pt": "Acordos assinados"},
    "con_table_title": {"es": "Productos, roles y estado del contrato", "en": "Products, roles and contract status", "pt": "Produtos, papéis e status do contrato"},
    "con_table_note": {
        "es": "Roles del modelo: Domain Owner = dueño del catálogo · Product Owner = steward · Productor = sistema fuente real · Consumidores = aguas abajo del linaje real. Si el catálogo cambia, esto cambia.",
        "en": "Model roles: Domain Owner = catalog owner · Product Owner = steward · Producer = real source system · Consumers = downstream of the real lineage. Change the catalog and this changes.",
        "pt": "Papéis do modelo: Domain Owner = dono do catálogo · Product Owner = steward · Produtor = sistema fonte real · Consumidores = rio abaixo da linhagem real. Mude o catálogo e isto muda.",
    },
    "con_pick": {"es": "Elegí un producto de datos", "en": "Pick a data product", "pt": "Escolha um produto de dados"},
    "con_role_do": {"es": "Domain Owner", "en": "Domain Owner", "pt": "Domain Owner"},
    "con_role_po": {"es": "Product Owner (PO)", "en": "Product Owner (PO)", "pt": "Product Owner (PO)"},
    "con_role_prod": {"es": "Productor", "en": "Producer", "pt": "Produtor"},
    "con_role_cons": {"es": "Consumidores", "en": "Consumers", "pt": "Consumidores"},
    "con_sla": {"es": "SLA de refresco", "en": "Refresh SLA", "pt": "SLA de atualização"},
    "con_rules_title": {"es": "Reglas y umbrales del contrato (última corrida real)", "en": "Contract rules and thresholds (latest real run)", "pt": "Regras e limiares do contrato (última execução real)"},
    "con_esc_title": {"es": "Qué pasa si falla (escalamiento acordado)", "en": "What happens on failure (agreed escalation)", "pt": "O que acontece se falhar (escalonamento acordado)"},
    "con_esc_warn": {
        "es": "**En riesgo (warn)**: se avisa al Product Owner para revisar dentro del período del SLA. El dato sigue publicándose con advertencia visible.",
        "en": "**At risk (warn)**: the Product Owner is notified to review within the SLA period. Data keeps publishing with a visible warning.",
        "pt": "**Em risco (warn)**: o Product Owner é avisado para revisar dentro do período do SLA. O dado continua sendo publicado com aviso visível.",
    },
    "con_esc_fail": {
        "es": "**Incumplido (fail)**: se avisa al Domain Owner y al Product Owner, se recomienda frenar el refresco de los consumidores aguas abajo y se abre el plan de remediación (pestaña Entregable).",
        "en": "**Breached (fail)**: the Domain Owner and Product Owner are notified, pausing downstream consumer refresh is recommended and the remediation plan is opened (Deliverable tab).",
        "pt": "**Descumprido (fail)**: o Domain Owner e o Product Owner são avisados, recomenda-se pausar a atualização dos consumidores rio abaixo e abre-se o plano de remediação (aba Entregável).",
    },
    "con_sign_title": {"es": "Documentar el acuerdo", "en": "Document the agreement", "pt": "Documentar o acordo"},
    "con_sign_note": {
        "es": "Un acuerdo no documentado es una opinión. La firma queda guardada en este equipo (nombre, rol y fecha), auditable como la curaduría.",
        "en": "An undocumented agreement is an opinion. The signature is stored on this machine (name, role and date), auditable like curation.",
        "pt": "Um acordo não documentado é uma opinião. A assinatura fica guardada neste equipamento (nome, papel e data), auditável como a curadoria.",
    },
    "con_sign_name": {"es": "Nombre de quien acuerda", "en": "Name of the signer", "pt": "Nome de quem acorda"},
    "con_sign_role": {"es": "Rol (ej.: Data Product Owner)", "en": "Role (e.g., Data Product Owner)", "pt": "Papel (ex.: Data Product Owner)"},
    "con_sign_btn": {"es": "Firmar acuerdo del contrato", "en": "Sign contract agreement", "pt": "Assinar acordo do contrato"},
    "con_need_name": {"es": "Ingresá el nombre de quien firma.", "en": "Enter the signer's name.", "pt": "Informe o nome de quem assina."},
    "con_signed_info": {"es": "Acuerdo vigente — firmado por {name} ({role}) el {date}.", "en": "Agreement active — signed by {name} ({role}) on {date}.", "pt": "Acordo vigente — assinado por {name} ({role}) em {date}."},
    "con_st_cumple": {"es": "🟢 cumple", "en": "🟢 compliant", "pt": "🟢 cumpre"},
    "con_st_en_riesgo": {"es": "🟡 en riesgo", "en": "🟡 at risk", "pt": "🟡 em risco"},
    "con_st_incumple": {"es": "🔴 incumple", "en": "🔴 breached", "pt": "🔴 descumpre"},
    "con_agr_vigente": {"es": "vigente", "en": "active", "pt": "vigente"},
    "con_agr_borrador": {"es": "borrador", "en": "draft", "pt": "rascunho"},
    "con_alerts_title": {"es": "Alarmística sobre el linaje", "en": "Alerting over lineage", "pt": "Alarmística sobre a linhagem"},
    "con_alerts_none": {"es": "Sin alertas: todos los contratos cumplen sus reglas.", "en": "No alerts: every contract meets its rules.", "pt": "Sem alertas: todos os contratos cumprem suas regras."},
    "con_alerts_note": {
        "es": "Cada regla no aprobada genera una alerta con impacto aguas abajo (recorriendo el linaje real), a quién avisar según severidad y la acción inmediata del motor de remediación. Honesto: se evalúa al abrir esta pestaña — el programa corre local y sin telemetría, no hay demonio 24/7; para monitoreo continuo, programá la corrida (Task Scheduler / cron).",
        "en": "Every non-passing rule raises an alert with downstream impact (walking the real lineage), whom to notify by severity and the immediate action from the remediation engine. Honest: evaluation happens when this tab opens — the program runs locally with no telemetry, there is no 24/7 daemon; for continuous monitoring, schedule the run (Task Scheduler / cron).",
        "pt": "Cada regra não aprovada gera um alerta com impacto rio abaixo (percorrendo a linhagem real), quem notificar conforme a severidade e a ação imediata do motor de remediação. Honesto: a avaliação acontece ao abrir esta aba — o programa roda localmente e sem telemetria, não há daemon 24/7; para monitoramento contínuo, agende a execução (Task Scheduler / cron).",
    },
    "con_dl_xlsx": {"es": "Descargar contratos + alertas (Excel)", "en": "Download contracts + alerts (Excel)", "pt": "Baixar contratos + alertas (Excel)"},
    "del_findings": {"es": "Hallazgos y plan de remediación", "en": "Findings and remediation plan", "pt": "Achados e plano de remediação"},
    "del_findings_note": {
        "es": "Un entregable profesional no esconde los problemas del dato: los diagnostica. Cada regla que no pasó aparece acá con su causa raíz, la corrección inmediata, la de fondo y el responsable — ese ES el trabajo de gobernanza. (Los casos de ejemplo usan datos reales sucios a propósito: si todo diera verde, la demo no probaría nada.)",
        "en": "A professional deliverable doesn't hide data problems: it diagnoses them. Every rule that didn't pass shows up here with its root cause, immediate fix, structural fix and owner — that IS the governance work. (The sample cases use genuinely dirty real data on purpose: if everything came out green, the demo would prove nothing.)",
        "pt": "Um entregável profissional não esconde os problemas do dado: diagnostica-os. Cada regra que não passou aparece aqui com sua causa raiz, correção imediata, correção estrutural e responsável — esse É o trabalho de governança. (Os casos de exemplo usam dados reais sujos de propósito: se tudo desse verde, a demo não provaria nada.)",
    },
    "del_mig_title": {"es": "Listo para migrar", "en": "Ready to migrate", "pt": "Pronto para migrar"},
    "del_mig_note": {
        "es": "Calculado con los conectores reales en modo previsualización (mismos payloads que el push real), sin credenciales y sin tocar la red. El estado Approved sale de la curaduría real del caso.",
        "en": "Computed with the real connectors in preview mode (same payloads as the real push), no credentials, no network. Approved status comes from the case's real curation.",
        "pt": "Calculado com os conectores reais em modo prévia (mesmos payloads do push real), sem credenciais e sem tocar a rede. O status Approved vem da curadoria real do caso.",
    },
    "del_download": {"es": "Descargar el entregable", "en": "Download the deliverable", "pt": "Baixar o entregável"},
    "del_download_xlsx": {"es": "Excel multi-hoja (ficha + diccionario + calidad + glosario + linaje)", "en": "Multi-sheet Excel (overview + dictionary + quality + glossary + lineage)", "pt": "Excel multi-planilha (ficha + dicionário + qualidade + glossário + linhagem)"},
    "del_download_md": {"es": "Resumen ejecutivo (Markdown)", "en": "Executive summary (Markdown)", "pt": "Resumo executivo (Markdown)"},
    "del_honest_note": {
        "es": "Cada número sale de correr las reglas reales sobre el archivo del caso y de la curaduría guardada — nada está inventado. Si la curaduría está en 0%, ese es el estado real: pasá por Curaduría a validar definiciones y el entregable lo refleja al instante.",
        "en": "Every number comes from running the real rules on the case file and from the saved curation — nothing is made up. If curation shows 0%, that's the real state: go validate definitions in Curation and the deliverable reflects it instantly.",
        "pt": "Cada número vem de rodar as regras reais no arquivo do caso e da curadoria salva — nada é inventado. Se a curadoria está em 0%, esse é o estado real: valide definições em Curadoria e o entregável reflete na hora.",
    },
    # ------------------------------------------------------- relevamiento
    "srv_intro": {
        "es": "Todo lo que hay que preguntarle al cliente para poder construir el pipeline, separado por área. Anotá quién respondió cada cosa: dentro de dos meses, «lo dijo alguien de Comercial» no alcanza. El casillero de repreguntas te dice qué quedó a medias en cada respuesta.",
        "en": "Everything you need to ask the client to be able to build the pipeline, split by area. Record who answered what: two months from now, \"someone in Sales said so\" is not enough. The follow-up box tells you what each answer left half-open.",
        "pt": "Tudo o que é preciso perguntar ao cliente para poder construir o pipeline, separado por área. Anote quem respondeu cada coisa: daqui a dois meses, «alguém do Comercial disse» não basta. O campo de reperguntas diz o que ficou pela metade em cada resposta.",
    },
    "srv_client": {"es": "Empresa", "en": "Company", "pt": "Empresa"},
    "srv_no_client": {
        "es": "Todavía no hay ninguna empresa cargada. Creá una en la pestaña «{tab}» y volvé: el relevamiento se guarda en la carpeta de esa empresa, no en un archivo suelto.",
        "en": "No company has been created yet. Create one in the \"{tab}\" tab and come back: the discovery is stored in that company's folder, not in a loose file.",
        "pt": "Ainda não há nenhuma empresa cadastrada. Crie uma na aba «{tab}» e volte: o levantamento é guardado na pasta dessa empresa, não em um arquivo solto.",
    },
    "srv_coverage": {"es": "Relevamiento cubierto", "en": "Discovery covered",
                     "pt": "Levantamento coberto"},
    "srv_kpi_questions": {"es": "Preguntas del banco", "en": "Questions in the bank",
                          "pt": "Perguntas do banco"},
    "srv_kpi_areas": {"es": "Áreas del pipeline", "en": "Pipeline areas",
                      "pt": "Áreas do pipeline"},
    "srv_area": {"es": "Área del pipeline", "en": "Pipeline area", "pt": "Área do pipeline"},
    "srv_who": {"es": "Quién respondió (nombre)", "en": "Who answered (name)",
                "pt": "Quem respondeu (nome)"},
    "srv_who_area": {"es": "Su área o cargo", "en": "Their area or role",
                     "pt": "Sua área ou cargo"},
    "srv_answer": {"es": "Qué respondió", "en": "What they answered",
                   "pt": "O que respondeu"},
    "srv_state": {"es": "Estado", "en": "Status", "pt": "Estado"},
    "srv_st_pending": {"es": "Pendiente", "en": "Pending", "pt": "Pendente"},
    "srv_st_answered": {"es": "Respondida", "en": "Answered", "pt": "Respondida"},
    "srv_st_na": {"es": "No aplica", "en": "Not applicable", "pt": "Não se aplica"},
    "srv_save": {"es": "Guardar respuesta", "en": "Save answer", "pt": "Salvar resposta"},
    "srv_saved": {"es": "Guardado.", "en": "Saved.", "pt": "Salvo."},
    "srv_why": {"es": "Por qué se pregunta", "en": "Why it is asked",
                "pt": "Por que se pergunta"},
    "srv_ask_whom": {"es": "A quién preguntarle", "en": "Who to ask",
                     "pt": "A quem perguntar"},
    "srv_followups": {"es": "Qué repreguntar", "en": "What to ask next",
                      "pt": "O que reperguntar"},
    "srv_followups_ai": {"es": "Repreguntas de la IA sobre esta respuesta",
                         "en": "AI follow-ups on this answer",
                         "pt": "Reperguntas da IA sobre esta resposta"},
    "srv_ask_ai": {"es": "Pedirle repreguntas a la IA", "en": "Ask the AI for follow-ups",
                   "pt": "Pedir reperguntas à IA"},
    "srv_ai_warning": {
        "es": "Manda la pregunta y la respuesta del cliente al proveedor de IA que configuraste. Las repreguntas de arriba se calculan acá mismo y no salen de tu máquina.",
        "en": "Sends the question and the client's answer to the AI provider you configured. The follow-ups above are computed locally and never leave your machine.",
        "pt": "Envia a pergunta e a resposta do cliente ao provedor de IA que você configurou. As reperguntas acima são calculadas aqui e não saem da sua máquina.",
    },
    "srv_ai_failed": {
        "es": "La IA no devolvió repreguntas. Las de arriba siguen sirviendo.",
        "en": "The AI returned no follow-ups. The ones above still apply.",
        "pt": "A IA não devolveu reperguntas. As de cima continuam valendo.",
    },
    "srv_no_ai": {
        "es": "Sin clave de IA configurada, las repreguntas de arriba son las que hay — y funcionan sin internet, que es la situación normal en la sala de reuniones de un cliente.",
        "en": "With no AI key configured, the follow-ups above are what you get — and they work with no internet, which is the normal situation in a client's meeting room.",
        "pt": "Sem chave de IA configurada, as reperguntas acima são o que há — e funcionam sem internet, que é a situação normal na sala de reuniões de um cliente.",
    },
    "srv_export": {"es": "Llevarte el relevamiento", "en": "Take the discovery with you",
                   "pt": "Levar o levantamento"},
    "srv_dl_xlsx": {"es": "Bajar Excel", "en": "Download Excel", "pt": "Baixar Excel"},
    # ----------------------------------------------------------- reuniones
    "mtg_intro": {
        "es": "De la reunión a la minuta: quién dijo qué, con el minuto de cada cita, y qué le toca a cada etapa del pipeline. Sirve igual para una reunión presencial que para una de Zoom, Teams, Meet o WebEx.",
        "en": "From the meeting to the minutes: who said what, with the timestamp of every quote, and what each pipeline stage has to do about it. Works the same for an in-person meeting and for one on Zoom, Teams, Meet or WebEx.",
        "pt": "Da reunião para a ata: quem disse o quê, com o minuto de cada citação, e o que cabe a cada etapa do pipeline. Serve igual para uma reunião presencial e para uma no Zoom, Teams, Meet ou WebEx.",
    },
    "mtg_source": {"es": "De dónde sale la reunión", "en": "Where the meeting comes from",
                   "pt": "De onde vem a reunião"},
    "mtg_src_transcript": {"es": "Transcripción de la videollamada",
                           "en": "Transcript from the video call",
                           "pt": "Transcrição da videochamada"},
    "mtg_src_record": {"es": "Grabar acá (presencial)", "en": "Record here (in person)",
                       "pt": "Gravar aqui (presencial)"},
    "mtg_src_audio": {"es": "Subir un audio", "en": "Upload an audio file",
                      "pt": "Enviar um áudio"},
    "mtg_src_paste": {"es": "Pegar el texto", "en": "Paste the text", "pt": "Colar o texto"},
    "mtg_transcript_help": {
        "es": "Es el mejor camino: Zoom, Teams, Meet y WebEx ya transcriben y exportan .vtt, .srt o .txt CON el nombre de cada orador — algo que un micrófono solo no puede dar. No necesita internet ni clave de IA: se lee acá.",
        "en": "This is the best path: Zoom, Teams, Meet and WebEx already transcribe and export .vtt, .srt or .txt WITH each speaker's name — something a single microphone cannot give you. Needs no internet and no AI key: it is parsed here.",
        "pt": "É o melhor caminho: Zoom, Teams, Meet e WebEx já transcrevem e exportam .vtt, .srt ou .txt COM o nome de cada orador — algo que um microfone sozinho não dá. Não precisa de internet nem de chave de IA: é lido aqui.",
    },
    "mtg_record_help": {
        "es": "Para una reunión presencial. Ojo: un micrófono da un solo canal, así que la transcripción no va a saber quién habló — los oradores se asignan a mano después. Preferí la transcripción de la plataforma cuando exista.",
        "en": "For an in-person meeting. Note: one microphone gives one channel, so the transcript will not know who spoke — speakers are assigned by hand afterwards. Prefer the platform's transcript when there is one.",
        "pt": "Para uma reunião presencial. Atenção: um microfone dá um único canal, então a transcrição não saberá quem falou — os oradores são atribuídos à mão depois. Prefira a transcrição da plataforma quando existir.",
    },
    "mtg_record": {"es": "Grabar la reunión", "en": "Record the meeting",
                   "pt": "Gravar a reunião"},
    "mtg_upload_tr": {"es": "Transcripción (.vtt, .srt, .txt)",
                      "en": "Transcript (.vtt, .srt, .txt)",
                      "pt": "Transcrição (.vtt, .srt, .txt)"},
    "mtg_upload_audio": {"es": "Archivo de audio", "en": "Audio file", "pt": "Arquivo de áudio"},
    "mtg_paste": {"es": "Pegá la transcripción o las notas de la reunión",
                  "en": "Paste the transcript or the meeting notes",
                  "pt": "Cole a transcrição ou as notas da reunião"},
    "mtg_ai_warning": {
        "es": "Transcribir manda ESTE AUDIO a {proveedor}. Es una reunión de tu cliente: si eso no está autorizado, subí la transcripción que ya generó la plataforma en vez de transcribir acá.",
        "en": "Transcribing sends THIS AUDIO to {proveedor}. This is your client's meeting: if that is not authorised, upload the transcript the platform already generated instead of transcribing here.",
        "pt": "Transcrever envia ESTE ÁUDIO para {proveedor}. É uma reunião do seu cliente: se isso não estiver autorizado, envie a transcrição que a plataforma já gerou em vez de transcrever aqui.",
    },
    "mtg_ai_confirm": {
        "es": "Entiendo que el audio sale de esta máquina y tengo autorización para hacerlo",
        "en": "I understand the audio leaves this machine and I am authorised to do so",
        "pt": "Entendo que o áudio sai desta máquina e tenho autorização para isso",
    },
    "mtg_transcribe": {"es": "Transcribir", "en": "Transcribe", "pt": "Transcrever"},
    "mtg_transcribing": {"es": "Transcribiendo el audio…", "en": "Transcribing the audio…",
                         "pt": "Transcrevendo o áudio…"},
    "mtg_transcribed": {"es": "Transcripción lista.", "en": "Transcript ready.",
                        "pt": "Transcrição pronta."},
    "mtg_empty": {
        "es": "Todavía no hay nada que minutar: cargá una transcripción, grabá o pegá el texto.",
        "en": "Nothing to minute yet: load a transcript, record, or paste the text.",
        "pt": "Ainda não há nada para registrar: carregue uma transcrição, grave ou cole o texto.",
    },
    "mtg_title": {"es": "Título de la reunión", "en": "Meeting title", "pt": "Título da reunião"},
    "mtg_date": {"es": "Fecha", "en": "Date", "pt": "Data"},
    "mtg_people": {"es": "Participantes", "en": "Participants", "pt": "Participantes"},
    "mtg_kpi_turns": {"es": "Intervenciones", "en": "Turns", "pt": "Intervenções"},
    "mtg_kpi_min": {"es": "Minutos", "en": "Minutes", "pt": "Minutos"},
    "mtg_kpi_findings": {"es": "Hallazgos", "en": "Findings", "pt": "Achados"},
    "mtg_speakers": {"es": "Quién habló", "en": "Who spoke", "pt": "Quem falou"},
    "mtg_speakers_note": {
        "es": "Si el 80% lo habló el consultor, no fue un relevamiento: fue una presentación, y lo que no se preguntó va a volver como un supuesto.",
        "en": "If the consultant did 80% of the talking, it was not a discovery session: it was a presentation, and what went unasked comes back as an assumption.",
        "pt": "Se 80% foi falado pelo consultor, não foi um levantamento: foi uma apresentação, e o que não se perguntou volta como suposição.",
    },
    "mtg_findings": {"es": "Decisiones, compromisos y riesgos",
                     "en": "Decisions, commitments and risks",
                     "pt": "Decisões, compromissos e riscos"},
    "mtg_filter_type": {"es": "Tipo", "en": "Type", "pt": "Tipo"},
    "mtg_no_findings": {
        "es": "No se detectó ninguna decisión ni compromiso. Puede ser que no los haya, o que se hayan dicho de una forma que el detector no reconoce: la transcripción completa está más abajo.",
        "en": "No decision or commitment was detected. There may be none, or they may have been phrased in a way the detector does not recognise: the full transcript is below.",
        "pt": "Nenhuma decisão ou compromisso foi detectado. Pode não haver, ou terem sido ditos de um jeito que o detector não reconhece: a transcrição completa está abaixo.",
    },
    "mtg_pipeline": {"es": "Qué le toca a cada etapa del pipeline",
                     "en": "What each pipeline stage has to do",
                     "pt": "O que cabe a cada etapa do pipeline"},
    "mtg_pipeline_note": {
        "es": "Cada frase de la reunión cruzada contra las 12 etapas. Es lo que convierte la minuta en trabajo: qué toca hacer en ingesta, en calidad, en linaje.",
        "en": "Every sentence of the meeting cross-referenced against the 12 stages. It is what turns the minutes into work: what to do in ingestion, in quality, in lineage.",
        "pt": "Cada frase da reunião cruzada com as 12 etapas. É o que transforma a ata em trabalho: o que fazer na ingestão, na qualidade, na linhagem.",
    },
    "mtg_no_pipeline": {
        "es": "Ninguna frase tocó una etapa del pipeline. Si la reunión era de relevamiento técnico, vale la pena revisar la transcripción a mano.",
        "en": "No sentence touched a pipeline stage. If this was a technical discovery meeting, it is worth reviewing the transcript by hand.",
        "pt": "Nenhuma frase tocou uma etapa do pipeline. Se a reunião era de levantamento técnico, vale revisar a transcrição à mão.",
    },
    "mtg_transcript": {"es": "Transcripción completa", "en": "Full transcript",
                       "pt": "Transcrição completa"},
    "mtg_assign_note": {
        "es": "Si la columna «orador» está vacía es porque la transcripción no traía nombres. El programa NO los adivina a propósito: ponerle en la boca a alguien algo que no dijo es peor que dejarlo sin asignar.",
        "en": "If the \"speaker\" column is empty it is because the transcript carried no names. The program deliberately does NOT guess: putting words in someone's mouth is worse than leaving them unassigned.",
        "pt": "Se a coluna «orador» está vazia é porque a transcrição não trazia nomes. O programa NÃO adivinha de propósito: colocar palavras na boca de alguém é pior que deixar sem atribuir.",
    },
    "mtg_export": {"es": "Llevarte la minuta", "en": "Take the minutes with you",
                   "pt": "Levar a ata"},
    "mtg_dl_xlsx": {"es": "Bajar Excel", "en": "Download Excel", "pt": "Baixar Excel"},
    # -------------------------------------------------- cómo está instalado
    "inst_title": {"es": "Cómo está instalado", "en": "How this is installed",
                   "pt": "Como está instalado"},
    "inst_where": {"es": "Tus datos se guardan en",
                   "en": "Your data is stored in",
                   "pt": "Seus dados são guardados em"},
    "inst_fallback": {
        "es": "Este paquete es el portable (para la VM del cliente), pero su carpeta no admite escritura, así que se está guardando en tu perfil de usuario. En una VM que se resetea al cerrar sesión, ese trabajo se pierde: mové la carpeta del programa a un lugar donde puedas escribir (Documentos, D:\\, un disco de red).",
        "en": "This is the portable package (for the client's VM), but its folder is not writable, so data is going to your user profile instead. On a VM that resets at logoff, that work is lost: move the program folder somewhere you can write (Documents, D:\\, a network drive).",
        "pt": "Este pacote é o portátil (para a VM do cliente), mas a pasta dele não permite escrita, então os dados estão indo para o seu perfil de usuário. Numa VM que se reinicia ao sair, esse trabalho se perde: mova a pasta do programa para um lugar onde você possa escrever (Documentos, D:\\, um disco de rede).",
    },
    # ------------------------------------------------ trazabilidad del pipeline
    "tz_intro": {
        "es": "Todo lo que el programa le hizo a los datos, en el orden real en que pasó. Cada etapa está contada dos veces: en criollo, para quien decide, y en técnico, para quien mantiene el código. La evidencia de cada una se mide sobre esta corrida, no sobre un folleto.",
        "en": "Everything the program did to the data, in the real order it happened. Each stage is told twice: in plain words for whoever decides, and in technical terms for whoever maintains the code. The evidence for each one is measured on this run, not on a brochure.",
        "pt": "Tudo o que o programa fez com os dados, na ordem real em que aconteceu. Cada etapa é contada duas vezes: em bom português, para quem decide, e em termos técnicos, para quem mantém o código. A evidência de cada uma é medida sobre esta execução, não sobre um folheto.",
    },
    "tz_view": {"es": "Para quién lo escribo", "en": "Who I'm writing it for",
                "pt": "Para quem eu escrevo"},
    "tz_view_both": {"es": "Los dos", "en": "Both", "pt": "Os dois"},
    "tz_view_plain": {"es": "Jefe o gerente", "en": "Manager or director",
                      "pt": "Chefe ou gerente"},
    "tz_view_tech": {"es": "Programador", "en": "Developer", "pt": "Programador"},
    "tz_kpi_stages": {"es": "Etapas del pipeline", "en": "Pipeline stages",
                      "pt": "Etapas do pipeline"},
    "tz_kpi_measured": {"es": "Etapas con medición", "en": "Stages with measurement",
                        "pt": "Etapas com medição"},
    "tz_export": {"es": "Llevártelo", "en": "Take it with you", "pt": "Levar com você"},
    "tz_export_note": {
        "es": "El mismo documento en los tres formatos. El HTML se abre en cualquier navegador y desde ahí «Imprimir → Guardar como PDF» sale igual de prolijo; el Word es editable de verdad, para pegarle el logo de la empresa antes de mandarlo.",
        "en": "The same document in all three formats. The HTML opens in any browser and from there \"Print → Save as PDF\" comes out just as clean; the Word file is genuinely editable, so you can drop in the company logo before sending it.",
        "pt": "O mesmo documento nos três formatos. O HTML abre em qualquer navegador e de lá «Imprimir → Salvar como PDF» sai igualmente caprichado; o Word é editável de verdade, para colar o logo da empresa antes de enviar.",
    },
    "tz_dl_html": {"es": "Bajar HTML", "en": "Download HTML", "pt": "Baixar HTML"},
    "tz_dl_docx": {"es": "Bajar Word", "en": "Download Word", "pt": "Baixar Word"},
    "tz_dl_pdf": {"es": "Bajar PDF", "en": "Download PDF", "pt": "Baixar PDF"},
    # -------------------------------------- alcance combinado (demo + Mis datos)
    "scope_toggle": {
        "es": "Incluir los casos de Mis datos en todo el programa",
        "en": "Include the My data cases across the whole program",
        "pt": "Incluir os casos de Meus dados em todo o programa",
    },
    # --- Datasets que carga el propio usuario, gobernados en todas las pestañas ---
    "scope_user_domain": {"es": "Cargado por vos", "en": "Loaded by you",
                          "pt": "Carregado por você"},
    "scope_user_desc": {
        "es": "Dataset cargado en esta sesión: {filas} filas × {columnas} columnas.",
        "en": "Dataset loaded in this session: {filas} rows × {columnas} columns.",
        "pt": "Dataset carregado nesta sessão: {filas} linhas × {columnas} colunas.",
    },
    "scope_user_source": {"es": "Archivo o base cargada por el usuario",
                          "en": "File or database loaded by the user",
                          "pt": "Arquivo ou banco carregado pelo usuário"},
    "scope_user_refresh": {"es": "manual", "en": "manual", "pt": "manual"},
    "scope_user_pii": {"es": "Posible PII", "en": "Possible PII", "pt": "Possível PII"},
    "scope_user_nopii": {"es": "Sin clasificar", "en": "Unclassified",
                         "pt": "Sem classificação"},
    "scope_user_col_desc": {
        "es": "{nulos}% nulos · {distintos} valores distintos.",
        "en": "{nulos}% nulls · {distintos} distinct values.",
        "pt": "{nulos}% nulos · {distintos} valores distintos.",
    },
    "scope_user_badge": {
        "es": "Estás viendo también **{n}** dataset(s) cargados por vos: {nombres}.",
        "en": "You are also seeing **{n}** dataset(s) you loaded: {nombres}.",
        "pt": "Você também está vendo **{n}** dataset(s) carregados por você: {nombres}.",
    },
    "scope_user_none": {
        "es": "Todavía no cargaste ningún dataset. Subí tu Excel, CSV o conectá "
              "una base en la pestaña «Mis datos» y vas a verlo gobernado acá y "
              "en todas las demás pestañas.",
        "en": "You haven't loaded any dataset yet. Upload your Excel or CSV, or "
              "connect a database in the \"My data\" tab, and you'll see it "
              "governed here and across every other tab.",
        "pt": "Você ainda não carregou nenhum dataset. Envie seu Excel ou CSV, ou "
              "conecte um banco na aba \"Meus dados\", e verá tudo governado aqui "
              "e em todas as outras abas.",
    },
    "scope_user_clear": {"es": "Quitar mis datasets cargados",
                         "en": "Remove my loaded datasets",
                         "pt": "Remover meus datasets carregados"},
    "scope_hint": {
        "es": "Con esto activado, los 4 casos reales de Mis datos (Rotulado, Dirty Cafe, Bank Marketing, openFDA) fluyen por Panorama, Catálogo, Calidad, Linaje, Glosario, Políticas y BI & API — el recorrido end-to-end completo. Apagalo para ver solo la demo sintética.",
        "en": "With this on, the 4 real cases from My data (Food labels, Dirty Cafe, Bank Marketing, openFDA) flow through Overview, Catalog, Quality, Lineage, Glossary, Policies and BI & API — the full end-to-end journey. Turn it off to see only the synthetic demo.",
        "pt": "Com isso ativado, os 4 casos reais de Meus dados (Rotulagem, Dirty Cafe, Bank Marketing, openFDA) fluem por Panorama, Catálogo, Qualidade, Linhagem, Glossário, Políticas e BI & API — a jornada end-to-end completa. Desligue para ver só a demo sintética.",
    },
    # ---------------------------------------------------- login (modo servidor)
    # --- Licencias ---
    # --- Configuración de IA (pestaña Ayuda) --------------------------------
    "ia_title": {"es": "Configuración de IA",
                 "en": "AI settings",
                 "pt": "Configuração de IA"},
    "ia_intro": {
        "es": "Opcional. El programa funciona completo sin esto: las sugerencias "
              "locales no necesitan internet ni API key. Si cargás la tuya, cada "
              "sugerencia puede además generarse en vivo con el modelo que elijas. "
              "Las llamadas las paga tu cuenta del proveedor, no MV.",
        "en": "Optional. The app works fully without this: local suggestions need "
              "no internet and no API key. If you add yours, each suggestion can "
              "also be generated live with the model you pick. Calls are billed to "
              "your provider account, not to MV.",
        "pt": "Opcional. O programa funciona completo sem isto: as sugestões locais "
              "não precisam de internet nem de API key. Se você informar a sua, cada "
              "sugestão também pode ser gerada ao vivo com o modelo que escolher. As "
              "chamadas são cobradas na sua conta do provedor, não na da MV."},
    "ia_provider": {"es": "Proveedor", "en": "Provider", "pt": "Provedor"},
    "ia_key": {"es": "Tu API key", "en": "Your API key", "pt": "Sua API key"},
    "ia_key_help": {
        "es": "Se guarda en el llavero del sistema operativo. Nunca se manda a "
              "otro lado que no sea el proveedor que elegiste.",
        "en": "Stored in your operating system keyring. Never sent anywhere other "
              "than the provider you picked.",
        "pt": "Guardada no chaveiro do sistema operacional. Nunca é enviada para "
              "outro lugar além do provedor escolhido."},
    "ia_base_url": {"es": "URL base del servicio",
                    "en": "Service base URL",
                    "pt": "URL base do serviço"},
    "ia_base_help": {
        "es": "Por ejemplo https://openrouter.ai/api/v1 o http://localhost:11434/v1 "
              "para Ollama. Sirve cualquier servicio compatible con OpenAI.",
        "en": "For example https://openrouter.ai/api/v1 or http://localhost:11434/v1 "
              "for Ollama. Any OpenAI-compatible service works.",
        "pt": "Por exemplo https://openrouter.ai/api/v1 ou http://localhost:11434/v1 "
              "para Ollama. Qualquer serviço compatível com OpenAI funciona."},
    "ia_model": {"es": "Modelo", "en": "Model", "pt": "Modelo"},
    "ia_model_help": {
        "es": "Elegí según lo que quieras gastar: entre el modelo más chico y el "
              "más grande de un mismo proveedor puede haber diez veces de "
              "diferencia por llamada.",
        "en": "Pick according to what you want to spend: between the smallest and "
              "the largest model of one provider there can be a tenfold difference "
              "per call.",
        "pt": "Escolha conforme o quanto quer gastar: entre o menor e o maior "
              "modelo de um mesmo provedor pode haver dez vezes de diferença por "
              "chamada."},
    "ia_refresh": {"es": "Actualizar modelos",
                   "en": "Refresh models",
                   "pt": "Atualizar modelos"},
    "ia_refresh_help": {
        "es": "Le pregunta al proveedor qué modelos hay disponibles hoy para tu "
              "key. Los proveedores sacan modelos nuevos seguido, y los nuevos "
              "suelen ser más baratos.",
        "en": "Asks the provider which models are available today for your key. "
              "Providers ship new models often, and newer ones are usually cheaper.",
        "pt": "Pergunta ao provedor quais modelos estão disponíveis hoje para sua "
              "key. Os provedores lançam modelos novos com frequência, e os novos "
              "costumam ser mais baratos."},
    "ia_saved": {"es": "Guardado ", "en": "Saved ", "pt": "Salvo "},
    "ia_saved_obf": {
        "es": "Guardada, pero este equipo no tiene llavero del sistema: quedó "
              "ofuscada en la carpeta de datos. Ofuscado no es cifrado.",
        "en": "Saved, but this machine has no system keyring: it was obfuscated in "
              "the data folder. Obfuscated is not encrypted.",
        "pt": "Salva, mas esta máquina não tem chaveiro do sistema: ficou ofuscada "
              "na pasta de dados. Ofuscado não é criptografado."},
    "ia_need_key": {
        "es": "Cargá primero tu API key para poder traer los modelos.",
        "en": "Add your API key first to fetch the models.",
        "pt": "Informe primeiro sua API key para buscar os modelos."},
    "ia_refresh_fail": {
        "es": "No se pudo traer la lista (key inválida, sin internet, o el "
              "proveedor no responde). Se mantiene la lista anterior.",
        "en": "Could not fetch the list (invalid key, no internet, or the provider "
              "is not responding). The previous list is kept.",
        "pt": "Não foi possível buscar a lista (key inválida, sem internet, ou o "
              "provedor não responde). A lista anterior é mantida."},
    "ia_refresh_ok": {"es": "{n} modelos disponibles",
                      "en": "{n} models available",
                      "pt": "{n} modelos disponíveis"},
    "ia_active": {"es": "En uso: {prov} · {model}",
                  "en": "In use: {prov} · {model}",
                  "pt": "Em uso: {prov} · {model}"},
    "ia_none": {"es": "Sin IA externa: se usan las sugerencias locales.",
                "en": "No external AI: local suggestions are used.",
                "pt": "Sem IA externa: são usadas as sugestões locais."},
    "ia_copilot": {
        "es": "GitHub Copilot no aparece en la lista porque no expone una API "
              "para pedirle un texto con solo una key: se autentica por OAuth "
              "dentro de un editor. Si usás un gateway que lo exponga en formato "
              "OpenAI, entra por «Otro».",
        "en": "GitHub Copilot is not listed because it exposes no API to request "
              "text with just a key: it authenticates via OAuth inside an editor. "
              "If you use a gateway that exposes it in OpenAI format, use «Other».",
        "pt": "O GitHub Copilot não aparece na lista porque não expõe uma API para "
              "pedir texto apenas com uma key: autentica por OAuth dentro de um "
              "editor. Se você usa um gateway que o exponha em formato OpenAI, use "
              "«Outro»."},
    # --- Servidores MCP de las plataformas de BI ----------------------------
    "mcp_bi_title": {"es": "Servidores MCP oficiales de tus plataformas",
                     "en": "Official MCP servers of your platforms",
                     "pt": "Servidores MCP oficiais das suas plataformas"},
    "mcp_bi_intro": {
        "es": "Copiá el bloque en el archivo de configuración de tu cliente MCP "
              "(VS Code, Claude Desktop). MV Data Governance no guarda ni pide "
              "las credenciales de esas plataformas.",
        "en": "Copy the block into your MCP client's configuration file "
              "(VS Code, Claude Desktop). MV Data Governance neither stores nor "
              "asks for those platforms' credentials.",
        "pt": "Copie o bloco no arquivo de configuração do seu cliente MCP "
              "(VS Code, Claude Desktop). O MV Data Governance não guarda nem "
              "pede as credenciais dessas plataformas."},
    "mcp_bi_stdio": {
        "es": "Corre en tu máquina (stdio). El programa también puede lanzarlo.",
        "en": "Runs on your machine (stdio). The app can also launch it.",
        "pt": "Roda na sua máquina (stdio). O programa também pode iniciá-lo."},
    "mcp_bi_http": {
        "es": "Servicio remoto con inicio de sesión interactivo: se conecta "
              "desde tu cliente MCP, no desde acá.",
        "en": "Remote service with interactive sign-in: connect it from your "
              "MCP client, not from here.",
        "pt": "Serviço remoto com login interativo: conecte-o pelo seu cliente "
              "MCP, não daqui."},
    "mcp_bi_docs": {"es": "Documentación oficial", "en": "Official docs",
                    "pt": "Documentação oficial"},
    "lic_title": {"es": "Licencia", "en": "License", "pt": "Licença"},
    "lic_plan": {"es": "Plan actual", "en": "Current plan", "pt": "Plano atual"},
    "lic_demo": {"es": "Demo (gratis)", "en": "Demo (free)", "pt": "Demo (grátis)"},
    "lic_intro": {
        "es": "El programa funciona completo en modo demo. Algunas funciones para empresas requieren una licencia paga — abajo se listan cuáles.",
        "en": "The program runs fully in demo mode. Some enterprise features require a paid license — they are listed below.",
        "pt": "O programa funciona completo em modo demo. Algumas funções para empresas exigem uma licença paga — estão listadas abaixo.",
    },
    "lic_input": {"es": "Pegá acá tu clave de licencia", "en": "Paste your license key here", "pt": "Cole aqui sua chave de licença"},
    "lic_activate": {"es": "Activar licencia", "en": "Activate license", "pt": "Ativar licença"},
    "lic_ok": {
        "es": "Licencia activada · plan {plan}",
        "en": "License activated · {plan} plan",
        "pt": "Licença ativada · plano {plan}",
    },
    "lic_bad": {
        "es": "La clave no es válida (firma incorrecta, vencida o mal copiada). Revisá que la hayas pegado completa.",
        "en": "The key is not valid (bad signature, expired, or mis-copied). Check that you pasted it in full.",
        "pt": "A chave não é válida (assinatura incorreta, vencida ou mal copiada). Verifique se colou por completo.",
    },
    "lic_remove": {"es": "Quitar licencia", "en": "Remove license", "pt": "Remover licença"},
    "lic_removed": {"es": "Licencia quitada — volviste al plan demo.", "en": "License removed — back to the demo plan.", "pt": "Licença removida — de volta ao plano demo."},
    "lic_email": {"es": "Emitida a", "en": "Issued to", "pt": "Emitida para"},
    "lic_expires": {"es": "Vence", "en": "Expires", "pt": "Vence"},
    "lic_never": {"es": "Sin vencimiento", "en": "No expiry", "pt": "Sem vencimento"},
    "lic_paid_features": {"es": "Funciones que requieren licencia", "en": "Features requiring a license", "pt": "Funções que exigem licença"},
    "lic_locked": {
        "es": "Esta función requiere una licencia paga. Podés seguir usando todo el resto del programa; activá tu licencia en la pestaña {tab}.",
        "en": "This feature requires a paid license. You can keep using the rest of the program; activate your license in the {tab} tab.",
        "pt": "Esta função exige uma licença paga. Você pode continuar usando todo o resto do programa; ative sua licença na aba {tab}.",
    },
    "lic_no_issuer": {
        "es": "Este build no tiene configurada la clave pública del emisor, así que no puede validar licencias. Es un problema de empaquetado — avisale a quien te lo entregó.",
        "en": "This build has no issuer public key configured, so it cannot validate licenses. That is a packaging problem — tell whoever delivered it.",
        "pt": "Este build não tem a chave pública do emissor configurada, então não pode validar licenças. É um problema de empacotamento — avise quem o entregou.",
    },
    "auth_title": {"es": "Ingresá la contraseña", "en": "Enter the password", "pt": "Digite a senha"},
    "auth_intro": {
        "es": "Este servidor pide una contraseña compartida antes de mostrar el dashboard (configurada por tu equipo de TI con MVDG_SERVER_PASSWORD).",
        "en": "This server requires a shared password before showing the dashboard (configured by your IT team with MVDG_SERVER_PASSWORD).",
        "pt": "Este servidor pede uma senha compartilhada antes de mostrar o dashboard (configurada pela sua equipe de TI com MVDG_SERVER_PASSWORD).",
    },
    "auth_prompt": {"es": "Contraseña", "en": "Password", "pt": "Senha"},
    "auth_button": {"es": "Entrar", "en": "Sign in", "pt": "Entrar"},
    "auth_wrong": {"es": "Contraseña incorrecta.", "en": "Wrong password.", "pt": "Senha incorreta."},
    # ----------------------------------------------------------------- tabs
    "tab_overview": {"es": "Panorama", "en": "Overview", "pt": "Panorama"},
    "tab_catalog": {"es": "Catálogo", "en": "Catalog", "pt": "Catálogo"},
    "tab_mdm": {"es": "MDM", "en": "MDM", "pt": "MDM"},
    "tab_quality": {"es": "Calidad", "en": "Quality", "pt": "Qualidade"},
    "tab_lineage": {"es": "Linaje", "en": "Lineage", "pt": "Linhagem"},
    "tab_glossary": {"es": "Glosario", "en": "Glossary", "pt": "Glossário"},
    "tab_curation": {"es": "Curaduría", "en": "Curation", "pt": "Curadoria"},
    "tab_responsibles": {"es": "Responsables", "en": "Responsibles", "pt": "Responsáveis"},
    "tab_policies": {"es": "Políticas", "en": "Policies", "pt": "Políticas"},
    "tab_profiler": {"es": "Mis datos", "en": "My data", "pt": "Meus dados"},
    "tab_bi": {"es": "BI & API", "en": "BI & API", "pt": "BI & API"},
    "tab_deliverable": {"es": "Entregable", "en": "Deliverable", "pt": "Entregável"},
    "tab_trace": {"es": "Trazabilidad", "en": "Traceability", "pt": "Rastreabilidade"},
    "tab_survey": {"es": "Relevamiento", "en": "Discovery", "pt": "Levantamento"},
    "tab_meetings": {"es": "Reuniones", "en": "Meetings", "pt": "Reuniões"},
    "tab_clients": {"es": "Empresas", "en": "Companies", "pt": "Empresas"},
    "tab_workspace": {"es": "Proyecto", "en": "Project", "pt": "Projeto"},
    "tab_help": {"es": "Ayuda", "en": "Help", "pt": "Ajuda"},
    "tab_lab": {"es": "Laboratorio", "en": "Lab", "pt": "Laboratório"},
    "tab_dmbok": {"es": "Estándares", "en": "Standards", "pt": "Padrões"},
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
    # Plural aparte: "col_column" es el ENCABEZADO de una tabla (una fila =
    # una columna del dataset, singular correcto). Como MÉTRICA de conteo
    # ("Columnas: 8") el singular queda mal, y es la primera pantalla que ve
    # un prospecto con su propio archivo.
    "col_columns_count": {"es": "Columnas", "en": "Columns", "pt": "Colunas"},
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
    "q_pass": {"es": "🟢 Aprobada", "en": "🟢 Pass", "pt": "🟢 Aprovada"},
    "q_warn": {"es": "🟡 Alerta", "en": "🟡 Warning", "pt": "🟡 Alerta"},
    "q_fail": {"es": "🔴 Falla", "en": "🔴 Fail", "pt": "🔴 Falha"},
    "q_threshold": {"es": "Umbral", "en": "Threshold", "pt": "Limite"},
    "q_affected": {"es": "Filas afectadas", "en": "Affected rows", "pt": "Linhas afetadas"},
    # ---- informe de auditoría del archivo propio (mvdg/file_report.py) ----
    "frep_btn": {"es": "Descargar informe de auditoría (Excel)",
                 "en": "Download audit report (Excel)",
                 "pt": "Baixar relatório de auditoria (Excel)"},
    "frep_caption": {
        "es": "4 hojas listas para entregarle a tu cliente: resumen ejecutivo, perfil por columna, reglas de calidad corridas y plan de corrección. Todo generado localmente — el archivo no sale de tu equipo.",
        "en": "4 sheets ready to hand to your client: executive summary, column profile, executed quality rules and fix plan. All generated locally — the file never leaves your machine.",
        "pt": "4 abas prontas para entregar ao seu cliente: resumo executivo, perfil por coluna, regras de qualidade executadas e plano de correção. Tudo gerado localmente — o arquivo não sai do seu equipamento."},
    "frep_sheet_summary": {"es": "Resumen ejecutivo", "en": "Executive summary", "pt": "Resumo executivo"},
    "frep_sheet_profile": {"es": "Perfil por columna", "en": "Column profile", "pt": "Perfil por coluna"},
    "frep_sheet_quality": {"es": "Reglas de calidad", "en": "Quality rules", "pt": "Regras de qualidade"},
    "frep_sheet_fixes": {"es": "Plan de corrección", "en": "Fix plan", "pt": "Plano de correção"},
    "frep_field": {"es": "Indicador", "en": "Indicator", "pt": "Indicador"},
    "frep_value": {"es": "Valor", "en": "Value", "pt": "Valor"},
    "frep_pii_cols": {"es": "Columnas con posible PII", "en": "Columns with possible PII", "pt": "Colunas com possível PII"},
    "frep_generated": {
        "es": "Generado por MV Data Governance — cada número sale de correr las reglas reales sobre este archivo.",
        "en": "Generated by MV Data Governance — every number comes from running the real rules on this file.",
        "pt": "Gerado por MV Data Governance — cada número sai de executar as regras reais sobre este arquivo."},
    "fix_title": {"es": "Cómo corregir cada falla (sugerencia de la IA)", "en": "How to fix each issue (AI suggestion)", "pt": "Como corrigir cada falha (sugestão da IA)"},
    "fix_note": {
        "es": "Al lado de cada regla en warn o fail: causa probable, qué hacer con las filas ya cargadas y cómo evitar que vuelva a pasar. 100% local — no sale ningún dato de tu equipo para generar esto.",
        "en": "Next to every warn/fail rule: likely cause, what to do with the rows already loaded, and how to prevent it from happening again. 100% local — no data leaves your machine to generate this.",
        "pt": "Ao lado de cada regra em warn ou fail: causa provável, o que fazer com as linhas já carregadas e como evitar que aconteça de novo. 100% local — nenhum dado sai da sua máquina para gerar isto.",
    },
    "fix_none": {"es": "Sin fallas que corregir: todas las reglas pasan.", "en": "Nothing to fix: all rules pass.", "pt": "Nada a corrigir: todas as regras passam."},
    "fix_root": {"es": "Causa probable", "en": "Likely cause", "pt": "Causa provável"},
    "fix_short": {"es": "Corto plazo (las filas ya cargadas)", "en": "Short term (rows already loaded)", "pt": "Curto prazo (linhas já carregadas)"},
    "fix_long": {"es": "Prevención (que no vuelva a pasar)", "en": "Prevention (so it doesn't happen again)", "pt": "Prevenção (para não acontecer de novo)"},
    "fix_owner": {"es": "Asignar a", "en": "Assign to", "pt": "Atribuir a"},
    "fix_local_title": {"es": "Asistencia local (sin conexión)", "en": "Local assistance (offline)", "pt": "Assistência local (sem conexão)"},
    "fix_note_ai": {
        "es": "IA externa conectada: **{provider}** — vas a poder pedir, regla por regla, una sugerencia generada en vivo por ese modelo, además de la local. Solo se manda el metadato de la falla (dataset, columna, regla, cantidad de filas), nunca datos reales.",
        "en": "External AI connected: **{provider}** — you can request, rule by rule, a suggestion generated live by that model, in addition to the local one. Only the failure's metadata is sent (dataset, column, rule, row count), never real data.",
        "pt": "IA externa conectada: **{provider}** — você vai poder pedir, regra por regra, uma sugestão gerada ao vivo por esse modelo, além da local. Só é enviado o metadado da falha (dataset, coluna, regra, quantidade de linhas), nunca dados reais.",
    },
    "fix_ai_button": {"es": "Pedir sugerencia a {provider}", "en": "Ask {provider} for a suggestion", "pt": "Pedir sugestão a {provider}"},
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
    # ------------------------------------------------ curaduría masiva (cu_bulk)
    "cu_bulk_title": {"es": "Validación masiva por caso", "en": "Bulk validation per case", "pt": "Validação em massa por caso"},
    "cu_bulk_intro": {
        "es": "Cuando un responsable ya revisó un caso completo y está de acuerdo con las definiciones tal cual están, puede validarlas todas de una — firmadas con su nombre, cargo y fecha, igual que una por una. Así el entregable llega al 100% de curaduría sin 20 clics.",
        "en": "When a responsible person has reviewed a whole case and agrees with the definitions as they are, they can validate them all at once — signed with their name, role and date, same as one by one. That's how the deliverable reaches 100% curation without 20 clicks.",
        "pt": "Quando um responsável já revisou um caso inteiro e concorda com as definições como estão, pode validá-las todas de uma vez — assinadas com nome, cargo e data, igual a uma por uma. Assim o entregável chega a 100% de curadoria sem 20 cliques.",
    },
    "cu_bulk_pick": {"es": "Caso / dataset", "en": "Case / dataset", "pt": "Caso / dataset"},
    "cu_bulk_btn": {"es": "Validar las {n} definiciones pendientes tal cual", "en": "Validate the {n} pending definitions as-is", "pt": "Validar as {n} definições pendentes como estão"},
    "cu_bulk_done": {"es": "{n} definiciones validadas, firmadas por {name}.", "en": "{n} definitions validated, signed by {name}.", "pt": "{n} definições validadas, assinadas por {name}."},
    "cu_bulk_note": {
        "es": "Esto NO es un atajo para inflar métricas: queda registrado quién validó y cuándo, y cada definición se puede reabrir una por una. Validar en masa sin haber leído es responsabilidad de quien firma — igual que en Purview o Collibra.",
        "en": "This is NOT a shortcut to inflate metrics: who validated and when is recorded, and each definition can be reopened one by one. Bulk-validating without reading is on whoever signs — same as in Purview or Collibra.",
        "pt": "Isto NÃO é um atalho para inflar métricas: fica registrado quem validou e quando, e cada definição pode ser reaberta uma a uma. Validar em massa sem ler é responsabilidade de quem assina — igual ao Purview ou Collibra.",
    },
    # ------------------------------------------- glosario automático desde la base (ga)
    "ga_title": {"es": "Glosario automático desde tu base de datos",
                 "en": "Automatic glossary from your database",
                 "pt": "Glossário automático do seu banco de dados"},
    "ga_intro": {
        "es": "Lee SOLO el esquema (nombres de tablas y columnas — ni una fila de datos) de una conexión guardada en Mis datos y arma un borrador de término por columna. Las abreviaturas típicas se expanden a la palabra completa (`fec_pag` → \"fecha pago\", `cli_id` → \"cliente identificador\") con un diccionario local — sin red, sin inventar: lo que no reconoce queda tal cual. Todo es editable a mano acá abajo antes de guardar, y lo guardado entra a Curaduría como cualquier otra definición.",
        "en": "Reads ONLY the schema (table and column names — not a single row of data) from a connection saved in My data and builds a draft term per column. Typical abbreviations get expanded to the full word (`fec_pag` → \"payment date\", `cli_id` → \"customer identifier\") using a local dictionary — no network, no making things up: whatever it doesn't recognize stays as-is. Everything is hand-editable below before saving, and what you save enters Curation like any other definition.",
        "pt": "Lê APENAS o esquema (nomes de tabelas e colunas — nenhuma linha de dados) de uma conexão salva em Meus dados e monta um rascunho de termo por coluna. As abreviações típicas são expandidas para a palavra completa (`fec_pag` → \"data pagamento\", `cli_id` → \"cliente identificador\") com um dicionário local — sem rede, sem inventar: o que não reconhece fica como está. Tudo é editável à mão abaixo antes de salvar, e o que você salva entra em Curadoria como qualquer outra definição.",
    },
    "ga_no_conn": {
        "es": "Todavía no hay conexiones guardadas — creá una en Mis datos → Base de datos y volvé acá.",
        "en": "No saved connections yet — create one in My data → Database and come back here.",
        "pt": "Ainda não há conexões salvas — crie uma em Meus dados → Banco de dados e volte aqui.",
    },
    "ga_pick_conn": {"es": "Conexión", "en": "Connection", "pt": "Conexão"},
    "ga_generate": {"es": "Generar borrador desde el esquema", "en": "Generate draft from the schema", "pt": "Gerar rascunho do esquema"},
    "ga_generated": {
        "es": "{n} términos generados ({exp} con abreviaturas expandidas a la palabra completa).",
        "en": "{n} terms generated ({exp} with abbreviations expanded to the full word).",
        "pt": "{n} termos gerados ({exp} com abreviações expandidas para a palavra completa).",
    },
    "ga_edit_hint": {
        "es": "Editá cualquier celda de Término o Definición directamente en la tabla (doble clic) antes de guardar.",
        "en": "Edit any Term or Definition cell directly in the table (double-click) before saving.",
        "pt": "Edite qualquer célula de Termo ou Definição diretamente na tabela (duplo clique) antes de salvar.",
    },
    "ga_col_table": {"es": "Tabla (origen)", "en": "Table (source)", "pt": "Tabela (origem)"},
    "ga_col_column": {"es": "Columna (origen)", "en": "Column (source)", "pt": "Coluna (origem)"},
    "ga_save": {"es": "Guardar en el glosario", "en": "Save to the glossary", "pt": "Salvar no glossário"},
    "ga_saved_ok": {"es": "Guardado: {n} término(s).", "en": "Saved: {n} term(s).", "pt": "Salvo: {n} termo(s)."},
    "ga_curation_note": {
        "es": "Los términos guardados aparecen en Curaduría (origen: base de datos) para que un Data Owner/Steward los valide o los reescriba — y en Importado, en BI & API.",
        "en": "Saved terms show up in Curation (origin: database) for a Data Owner/Steward to validate or rewrite — and under Imported, in BI & API.",
        "pt": "Os termos salvos aparecem em Curadoria (origem: banco de dados) para um Data Owner/Steward validar ou reescrever — e em Importado, em BI & API.",
    },
    "ga_empty": {
        "es": "La conexión no devolvió tablas con columnas legibles.",
        "en": "The connection returned no tables with readable columns.",
        "pt": "A conexão não retornou tabelas com colunas legíveis.",
    },
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
    "cu_st_ai": {"es": "Sugerido por IA", "en": "AI-suggested", "pt": "Sugerido por IA"},
    "cu_st_val": {"es": "🟢 Validado", "en": "🟢 Validated", "pt": "🟢 Validado"},
    "cu_st_mod": {"es": "Modificado", "en": "Modified", "pt": "Modificado"},
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
    "cu_action_validar": {"es": "Validar tal cual", "en": "Validate as-is", "pt": "Validar como está"},
    "cu_action_modificar": {"es": "Modificar el texto", "en": "Modify the text", "pt": "Modificar o texto"},
    "cu_new_text": {"es": "Texto oficial (reemplaza al sugerido)", "en": "Official text (replaces the suggested one)", "pt": "Texto oficial (substitui o sugerido)"},
    "cu_resp_name": {"es": "Nombre del responsable", "en": "Responsible person's name", "pt": "Nome do responsável"},
    "cu_resp_role": {"es": "Cargo (ej. Data Owner de Ventas)", "en": "Role (e.g. Sales Data Owner)", "pt": "Cargo (ex. Data Owner de Vendas)"},
    "cu_notes": {"es": "Notas (opcional)", "en": "Notes (optional)", "pt": "Notas (opcional)"},
    "cu_save": {"es": "Guardar veredicto", "en": "Save verdict", "pt": "Salvar veredito"},
    "cu_saved": {"es": "Veredicto guardado.", "en": "Verdict saved.", "pt": "Veredito salvo."},
    "cu_need_name": {"es": "Falta el nombre del responsable.", "en": "The responsible person's name is missing.", "pt": "Falta o nome do responsável."},
    "cu_reset": {"es": "Volver a la sugerencia IA", "en": "Back to the AI suggestion", "pt": "Voltar à sugestão IA"},
    "cu_reset_ok": {"es": "Definición devuelta al estado sugerido por IA.", "en": "Definition returned to AI-suggested state.", "pt": "Definição devolvida ao estado sugerido por IA."},
    "cu_local_note": {
        "es": "Los veredictos se guardan solo en tu equipo (~/.mv_data_governance/curaduria.json) y persisten entre sesiones.",
        "en": "Verdicts are stored only on your machine (~/.mv_data_governance/curaduria.json) and persist between sessions.",
        "pt": "Os vereditos são salvos apenas no seu equipamento (~/.mv_data_governance/curaduria.json) e persistem entre sessões.",
    },
    # ---------------------------------------------------- governance insights
    "gi_title": {"es": "Estado del gobierno (estilo Purview, 100% local)", "en": "Governance estate (Purview-style, 100% local)", "pt": "Estado da governança (estilo Purview, 100% local)"},
    "gi_caption": {
        "es": "No mide la calidad de los datos — mide la salud del GOBIERNO sobre esos datos: cuánto del patrimonio tiene responsable con nombre, clasificación, reglas y definiciones revisadas. Mejora a medida que usás las pestañas Responsables y Curaduría.",
        "en": "It doesn't measure data quality — it measures the health of the GOVERNANCE over that data: how much of the estate has a named responsible, classification, rules and reviewed definitions. It improves as you use the Responsibles and Curation tabs.",
        "pt": "Não mede a qualidade dos dados — mede a saúde da GOVERNANÇA sobre esses dados: quanto do patrimônio tem responsável com nome, classificação, regras e definições revisadas. Melhora à medida que você usa as abas Responsáveis e Curadoria.",
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
        "es": "¿Cómo subir el índice? Asigná personas con nombre y cargo en Responsables (los datasets de ejemplo arrancan con equipos genéricos a propósito) y validá definiciones en Curaduría.",
        "en": "How to raise the index? Assign named people in Responsibles (the sample datasets start with generic teams on purpose) and validate definitions in Curation.",
        "pt": "Como subir o índice? Atribua pessoas com nome e cargo em Responsáveis (os datasets de exemplo começam com equipes genéricas de propósito) e valide definições em Curadoria.",
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
    "rs_src_file": {"es": "Excel / CSV", "en": "Excel / CSV", "pt": "Excel / CSV"},
    "rs_src_photo": {"es": "Foto (IA externa)", "en": "Photo (external AI)", "pt": "Foto (IA externa)"},
    "rs_src_saved": {"es": "Guardado", "en": "Saved", "pt": "Salvo"},
    "rs_upload": {"es": "Subí el organigrama (.xlsx/.csv)", "en": "Upload the org chart (.xlsx/.csv)", "pt": "Envie o organograma (.xlsx/.csv)"},
    "rs_upload_hint": {
        "es": "Alcanza con columnas de nombre, cargo y área (jefe y email son opcionales) — se detectan por el encabezado, en cualquier orden e idioma. ¿La tabla está en una base? Traela por conexión SQL en Mis datos, exportala y subila acá.",
        "en": "Columns for name, role and area are enough (manager and email are optional) — detected by header, in any order and language. Is the table in a database? Bring it via SQL connection in My data, export it and upload it here.",
        "pt": "Bastam colunas de nome, cargo e área (chefe e email são opcionais) — detectadas pelo cabeçalho, em qualquer ordem e idioma. A tabela está num banco? Traga-a por conexão SQL em Meus dados, exporte e envie aqui.",
    },
    "rs_parsed": {"es": "Organigrama leído: {n} personas.", "en": "Org chart read: {n} people.", "pt": "Organograma lido: {n} pessoas."},
    "rs_photo_needs_ai": {
        "es": "Leer una foto requiere la IA externa opcional (tu propia API key de Claude/ChatGPT/Gemini — ver docs/IA_EXTERNA.md). Sin eso, usá el camino Excel/CSV, que es 100% local.",
        "en": "Reading a photo requires the optional external AI (your own Claude/ChatGPT/Gemini API key — see docs/IA_EXTERNA.md). Without it, use the Excel/CSV path, which is 100% local.",
        "pt": "Ler uma foto requer a IA externa opcional (sua própria API key de Claude/ChatGPT/Gemini — veja docs/IA_EXTERNA.md). Sem isso, use o caminho Excel/CSV, que é 100% local.",
    },
    "rs_photo_disclosure": {
        "es": "La foto se envía a {provider} para extraer el texto — es la única función del programa que manda una imagen afuera, y solo cuando vos apretás el botón. Si el organigrama es confidencial, usá el camino Excel/CSV (100% local).",
        "en": "The photo is sent to {provider} to extract the text — it's the only feature in the program that sends an image out, and only when you press the button. If the org chart is confidential, use the Excel/CSV path (100% local).",
        "pt": "A foto é enviada a {provider} para extrair o texto — é a única função do programa que envia uma imagem para fora, e somente quando você aperta o botão. Se o organograma é confidencial, use o caminho Excel/CSV (100% local).",
    },
    "rs_upload_photo": {"es": "Subí la foto del organigrama", "en": "Upload the org chart photo", "pt": "Envie a foto do organograma"},
    "rs_extract_photo": {"es": "Extraer personas de la foto", "en": "Extract people from the photo", "pt": "Extrair pessoas da foto"},
    "rs_photo_failed": {
        "es": "No se pudieron extraer personas de la imagen (falló la llamada o la IA no encontró un organigrama legible).",
        "en": "Couldn't extract people from the image (the call failed or the AI found no readable org chart).",
        "pt": "Não foi possível extrair pessoas da imagem (a chamada falhou ou a IA não encontrou um organograma legível).",
    },
    "rs_none_saved": {"es": "Todavía no hay un organigrama guardado — cargalo por archivo o foto.", "en": "No org chart saved yet — load it from a file or photo.", "pt": "Ainda não há organograma salvo — carregue por arquivo ou foto."},
    "rs_people": {"es": "Personas del organigrama", "en": "People in the org chart", "pt": "Pessoas do organograma"},
    "rs_people_edit_hint": {"es": "Editá celdas, agregá o borrá filas antes de guardar.", "en": "Edit cells, add or remove rows before saving.", "pt": "Edite células, adicione ou remova linhas antes de salvar."},
    "rs_save_org": {"es": "Guardar organigrama", "en": "Save org chart", "pt": "Salvar organograma"},
    "rs_org_saved": {"es": "Organigrama guardado.", "en": "Org chart saved.", "pt": "Organograma salvo."},
    "rs_assignments": {"es": "Responsables por dataset (nombre y cargo)", "en": "Responsibles per dataset (name and role)", "pt": "Responsáveis por dataset (nome e cargo)"},
    "rs_suggest": {"es": "Completar responsables por defecto", "en": "Fill in default responsibles", "pt": "Preencher responsáveis por padrão"},
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
    "rs_save_asg": {"es": "Guardar responsables", "en": "Save responsibles", "pt": "Salvar responsáveis"},
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
    "p_compliant": {"es": "🟢 Cumple", "en": "🟢 Compliant", "pt": "🟢 Conforme"},
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
    "pr_auto_quality": {
        "es": "Catálogo de calidad (automático)",
        "en": "Quality catalog (automatic)",
        "pt": "Catálogo de qualidade (automático)",
    },
    "pr_auto_quality_scope": {
        "es": "Reglas de completitud y unicidad, generadas y evaluadas contra "
              "tu archivo — mismo motor que el resto del programa. Validez, "
              "consistencia, puntualidad y exactitud dependen de reglas de "
              "negocio que no se pueden adivinar; definilas en Glosario o "
              "pedile a tu Data Steward.",
        "en": "Completeness and uniqueness rules, generated and evaluated "
              "against your file — same engine as the rest of the program. "
              "Validity, consistency, timeliness and accuracy depend on "
              "business rules that can't be guessed; define them in "
              "Glossary or ask your Data Steward.",
        "pt": "Regras de completude e unicidade, geradas e avaliadas contra "
              "seu arquivo — mesmo motor do resto do programa. Validade, "
              "consistência, pontualidade e exatidão dependem de regras de "
              "negócio que não podem ser adivinhadas; defina-as em "
              "Glossário ou peça ao seu Data Steward.",
    },
    "pr_auto_quality_none": {
        "es": "El archivo no tiene columnas donde inferir reglas automáticas "
              "(o está vacío). Igual podés definir reglas a mano en Glosario.",
        "en": "The file has no columns to infer automatic rules from (or it's "
              "empty). You can still define rules by hand in Glossary.",
        "pt": "O arquivo não tem colunas para inferir regras automáticas (ou "
              "está vazio). Você ainda pode definir regras manualmente em "
              "Glossário.",
    },
    "pr_suggestions": {"es": "Reglas sugeridas", "en": "Suggested rules", "pt": "Regras sugeridas"},
    "pr_suggestions_note": {
        "es": "Lectura rápida en texto (incluye privacidad). Las de "
              "completitud y unicidad de arriba ya corrieron con puntaje real.",
        "en": "Quick text summary (includes privacy). The completeness and "
              "uniqueness ones above already ran with a real score.",
        "pt": "Leitura rápida em texto (inclui privacidade). As de "
              "completude e unicidade acima já rodaram com pontuação real.",
    },
    "pr_pii_hint": {
        "es": "Posible PII detectada — revisá clasificación y enmascaramiento.",
        "en": "Possible PII detected — review classification and masking.",
        "pt": "Possível PII detectada — revise classificação e mascaramento.",
    },
    "pr_source": {"es": "Fuente de datos", "en": "Data source", "pt": "Fonte de dados"},
    "pr_src_file": {"es": "Archivo (CSV/Excel)", "en": "File (CSV/Excel)", "pt": "Arquivo (CSV/Excel)"},
    "pr_src_db": {"es": "Base de datos", "en": "Database", "pt": "Banco de dados"},
    "pr_src_example": {"es": "Dataset de ejemplo (real)", "en": "Example dataset (real)", "pt": "Dataset de exemplo (real)"},
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
    "db_sqlite_upload": {"es": "Subí el archivo SQLite (.db, .sqlite)",
                         "en": "Upload the SQLite file (.db, .sqlite)",
                         "pt": "Envie o arquivo SQLite (.db, .sqlite)"},
    "db_sqlite_uploaded": {"es": "Archivo cargado", "en": "File loaded",
                           "pt": "Arquivo carregado"},
    "db_sqlite_expander": {"es": "¿Está en esta misma computadora? Escribí la ruta",
                           "en": "Is it on this same computer? Type the path",
                           "pt": "Está neste mesmo computador? Digite o caminho"},
    "db_sqlite_path": {"es": "Ruta del archivo .db/.sqlite", "en": "Path to .db/.sqlite file", "pt": "Caminho do arquivo .db/.sqlite"},
    "db_user": {"es": "Usuario", "en": "User", "pt": "Usuário"},
    "db_password": {"es": "Contraseña", "en": "Password", "pt": "Senha"},
    "db_save_pwd": {"es": "Guardar contraseña (local, ofuscada)", "en": "Save password (local, obfuscated)", "pt": "Salvar senha (local, ofuscada)"},
    "db_test": {"es": "Probar conexión", "en": "Test connection", "pt": "Testar conexão"},
    "db_save": {"es": "Guardar conexión", "en": "Save connection", "pt": "Salvar conexão"},
    "db_saved_ok": {"es": "Conexión guardada.", "en": "Connection saved.", "pt": "Conexão salva."},
    "db_delete": {"es": "Eliminar conexión", "en": "Delete connection", "pt": "Excluir conexão"},
    "db_need_name": {"es": "Poné un nombre para la conexión.", "en": "Enter a name for the connection.", "pt": "Informe um nome para a conexão."},
    "db_pick_table": {"es": "Tabla a traer", "en": "Table to load", "pt": "Tabela para trazer"},
    "db_limit": {"es": "Máximo de filas", "en": "Max rows", "pt": "Máximo de linhas"},
    "db_limit_help": {
        "es": "0 = sin límite: trae la tabla entera. El límite real pasa a "
              "ser la memoria de esta computadora.",
        "en": "0 = no limit: brings the whole table. The real limit becomes "
              "this computer's memory.",
        "pt": "0 = sem limite: traz a tabela inteira. O limite real passa a "
              "ser a memória deste computador.",
    },
    "db_load": {"es": "Traer y perfilar tabla", "en": "Load and profile table", "pt": "Trazer e perfilar tabela"},
    "db_query": {"es": "…o una consulta SQL (SELECT)", "en": "…or a SQL query (SELECT)", "pt": "…ou uma consulta SQL (SELECT)"},
    "db_run_query": {"es": "▶ Ejecutar consulta y perfilar", "en": "▶ Run query and profile", "pt": "▶ Executar consulta e perfilar"},
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
    "bi_download_csv": {"es": "Descargar CSV", "en": "Download CSV", "pt": "Baixar CSV"},
    "bi_download_xlsx": {"es": "Descargar Excel", "en": "Download Excel", "pt": "Baixar Excel"},
    "bi_download_json": {"es": "Descargar JSON", "en": "Download JSON", "pt": "Baixar JSON"},
    "bi_download_parquet": {"es": "Descargar Parquet", "en": "Download Parquet", "pt": "Baixar Parquet"},
    "bi_export_all": {
        "es": "Exportar paquete BI completo (Excel multi-hoja)",
        "en": "Export full BI bundle (multi-sheet Excel)",
        "pt": "Exportar pacote BI completo (Excel multi-abas)",
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
    "mig_title": {"es": "Migración a Purview / Collibra", "en": "Migration to Purview / Collibra", "pt": "Migração para Purview / Collibra"},
    "mig_intro": {
        "es": "Empujá el catálogo, el diccionario y el glosario ya gobernados acá "
              "hacia Purview o Collibra por API. Es un **acelerador, no un "
              "reemplazo**: el programa hace el trabajo pesado (perfilar, reglas de "
              "calidad, glosario, PII, curaduría con responsable) y al final "
              "empuja el resultado — Purview/Collibra siguen siendo la plataforma "
              "que tu equipo audita y usa después. El estado Draft/Approved de "
              "cada término sale de la pestaña Curaduría real, no se inventa.",
        "en": "Push the catalog, dictionary and glossary already governed here "
              "into Purview or Collibra via API. It's an **accelerator, not a "
              "replacement**: the program does the heavy lifting (profiling, "
              "quality rules, glossary, PII, curation with a responsible person) "
              "and pushes the result at the end — Purview/Collibra remain the "
              "platform your team audits and uses afterward. Each term's Draft/"
              "Approved status comes from the real Curation tab, not invented.",
        "pt": "Empurre o catálogo, o dicionário e o glossário já governados aqui "
              "para o Purview ou Collibra via API. É um **acelerador, não um "
              "substituto**: o programa faz o trabalho pesado (perfilamento, "
              "regras de qualidade, glossário, PII, curadoria com responsável) e "
              "no final empurra o resultado — Purview/Collibra continuam sendo a "
              "plataforma que sua equipe audita e usa depois. O status Draft/"
              "Approved de cada termo vem da aba Curadoria real, não é inventado.",
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
        "es": "Credenciales cargadas — el botón de push real está disponible.",
        "en": "Credentials loaded — the real push button is available.",
        "pt": "Credenciais carregadas — o botão de push real está disponível.",
    },
    "mig_preview": {"es": "Previsualizar (sin credenciales)", "en": "Preview (no credentials)", "pt": "Pré-visualizar (sem credenciais)"},
    "mig_push": {"es": "Empujar de verdad", "en": "Push for real", "pt": "Empurrar de verdade"},
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
    "enf_title": {"es": "Enforcement de acceso (genera DDL, no bloquea nada solo)", "en": "Access enforcement (generates DDL, blocks nothing by itself)", "pt": "Enforcement de acesso (gera DDL, não bloqueia nada sozinho)"},
    "enf_intro": {
        "es": "Bloquear una consulta en vivo requiere estar en el camino del dato (un proxy, o Purview dentro de Azure) — este programa NO se hace pasar por eso. Lo que sí hace: te genera el DDL real (GRANT/REVOKE por clasificación + enmascaramiento de columnas PII) a partir de tu catálogo ya gobernado, para que vos (o tu DBA) lo revises y lo corras contra la base. Nunca se conecta a ejecutar nada de esto.",
        "en": "Blocking a live query requires sitting in the data path (a proxy, or Purview inside Azure) — this program does NOT pretend to be that. What it does: generates real DDL (GRANT/REVOKE by classification + PII column masking) from your already-governed catalog, for you (or your DBA) to review and run against the database. It never connects to execute any of this.",
        "pt": "Bloquear uma consulta em tempo real exige estar no caminho do dado (um proxy, ou o Purview dentro do Azure) — este programa NÃO finge ser isso. O que ele faz: gera o DDL real (GRANT/REVOKE por classificação + mascaramento de colunas PII) a partir do seu catálogo já governado, para você (ou seu DBA) revisar e rodar contra o banco. Nunca se conecta para executar nada disso.",
    },
    "enf_engine": {"es": "Motor de base de datos", "en": "Database engine", "pt": "Motor de banco de dados"},
    "enf_roles": {"es": "Roles autorizados por clasificación (uno por línea: clasificación: rol)", "en": "Authorized roles per classification (one per line: classification: role)", "pt": "Papéis autorizados por classificação (um por linha: classificação: papel)"},
    "enf_roles_explain": {
        "es": "**Cómo se completa, línea por línea:** a la izquierda va la **clasificación** de tus datasets "
              "(Confidencial / Interna / PII / Pública — vienen de tu Catálogo y ya están precargadas), y a la "
              "derecha va el **nombre del rol de TU base de datos** que sí puede ver los datasets con esa "
              "clasificación. Un *rol* es un grupo de usuarios que existe adentro de PostgreSQL o SQL Server "
              "(los crea tu DBA — ej.: `analistas_ventas`, `rrhh`, `finanzas`).\n\n"
              "- Ejemplo real: `PII: rrhh` significa \"solo el grupo rrhh puede consultar las tablas con datos personales\".\n"
              "- ¿Querés que dos grupos vean lo Confidencial? Dos líneas: `Confidencial: finanzas` y `Confidencial: gerencia`.\n"
              "- ¿No sabés qué roles existen en tu base? Preguntale a tu DBA, o consultá vos: "
              "`SELECT rolname FROM pg_roles;` (PostgreSQL) / `SELECT name FROM sys.database_principals WHERE type='R';` (SQL Server).\n"
              "- Si todavía no tenés roles, dejá los nombres precargados (`rol_confidencial`, etc.): el script sale "
              "igual y tu DBA solo renombra al aplicarlo. Acordate: esto **no ejecuta nada** — genera el script para revisar.",
        "en": "**How to fill it in, line by line:** the left side is the **classification** of your datasets "
              "(Confidential / Internal / PII / Public — they come from your Catalog and are pre-filled), and the "
              "right side is the **name of the role in YOUR database** that IS allowed to see datasets with that "
              "classification. A *role* is a group of users that exists inside PostgreSQL or SQL Server "
              "(your DBA creates them — e.g. `sales_analysts`, `hr`, `finance`).\n\n"
              "- Real example: `PII: hr` means \"only the hr group can query tables holding personal data\".\n"
              "- Want two groups to see Confidential data? Two lines: `Confidencial: finance` and `Confidencial: management`.\n"
              "- Don't know which roles exist? Ask your DBA, or check yourself: "
              "`SELECT rolname FROM pg_roles;` (PostgreSQL) / `SELECT name FROM sys.database_principals WHERE type='R';` (SQL Server).\n"
              "- No roles yet? Keep the pre-filled names (`rol_confidencial`, etc.): the script still generates and "
              "your DBA just renames when applying it. Remember: this **executes nothing** — it generates a script for review.",
        "pt": "**Como preencher, linha por linha:** à esquerda vai a **classificação** dos seus datasets "
              "(Confidencial / Interna / PII / Pública — vêm do seu Catálogo e já estão pré-preenchidas), e à "
              "direita vai o **nome do papel (role) do SEU banco de dados** que pode ver os datasets com essa "
              "classificação. Um *papel* é um grupo de usuários que existe dentro do PostgreSQL ou SQL Server "
              "(seu DBA os cria — ex.: `analistas_vendas`, `rh`, `financeiro`).\n\n"
              "- Exemplo real: `PII: rh` significa \"só o grupo rh pode consultar as tabelas com dados pessoais\".\n"
              "- Quer dois grupos vendo o Confidencial? Duas linhas: `Confidencial: financeiro` e `Confidencial: gerencia`.\n"
              "- Não sabe quais papéis existem? Pergunte ao seu DBA, ou consulte você mesmo: "
              "`SELECT rolname FROM pg_roles;` (PostgreSQL) / `SELECT name FROM sys.database_principals WHERE type='R';` (SQL Server).\n"
              "- Ainda não tem papéis? Deixe os nomes pré-preenchidos (`rol_confidencial`, etc.): o script sai igual e "
              "seu DBA só renomeia ao aplicar. Lembre: isto **não executa nada** — gera um script para revisão.",
    },
    "enf_roles_help": {
        "es": "Ej: PII: rol_rrhh — el rol que sí puede ver las tablas clasificadas PII. Podés agregar varios roles a la misma clasificación en líneas separadas.",
        "en": "E.g.: PII: rol_rrhh — the role allowed to see PII-classified tables. You can add several roles to the same classification on separate lines.",
        "pt": "Ex: PII: rol_rrhh — o papel que pode ver as tabelas classificadas como PII. Você pode adicionar vários papéis à mesma classificação em linhas separadas.",
    },
    "enf_generate": {"es": "Generar DDL", "en": "Generate DDL", "pt": "Gerar DDL"},
    "enf_grants": {"es": "Sentencias GRANT/REVOKE", "en": "GRANT/REVOKE statements", "pt": "Sentenças GRANT/REVOKE"},
    "enf_masks": {"es": "Sentencias de enmascaramiento", "en": "Masking statements", "pt": "Sentenças de mascaramento"},
    "enf_download": {"es": "Descargar el .sql", "en": "Download the .sql", "pt": "Baixar o .sql"},
    "enf_local_note": {
        "es": "100% local: es texto SQL generado a partir de tu catálogo — el programa nunca abre una conexión para ejecutarlo. Cubre PostgreSQL (Row-Level Security nativo) y SQL Server (Dynamic Data Masking + Row-Level Security nativos).",
        "en": "100% local: it's SQL text generated from your catalog — the program never opens a connection to run it. Covers PostgreSQL (native Row-Level Security) and SQL Server (native Dynamic Data Masking + Row-Level Security).",
        "pt": "100% local: é texto SQL gerado a partir do seu catálogo — o programa nunca abre uma conexão para executá-lo. Cobre PostgreSQL (Row-Level Security nativo) e SQL Server (Dynamic Data Masking + Row-Level Security nativos).",
    },
    # -------------------------------------------------------------- MIP (mip)
    "mip_title": {"es": "Etiquetas de sensibilidad (Microsoft Information Protection)", "en": "Sensitivity labels (Microsoft Information Protection)", "pt": "Rótulos de sensibilidade (Microsoft Information Protection)"},
    "mip_intro": {
        "es": "Una etiqueta MIP es cifrado real embebido en el archivo de Office, atado a la infraestructura de Microsoft — no hay forma de reimplementarla localmente. Este conector llama a la API REAL de Microsoft Graph para aplicar una etiqueta de verdad a un archivo que ya vive en OneDrive/SharePoint, usando la clasificación que este catálogo ya calculó.",
        "en": "An MIP label is real encryption embedded in the Office file, tied to Microsoft's infrastructure — there's no way to reimplement it locally. This connector calls the REAL Microsoft Graph API to apply a real label to a file that already lives in OneDrive/SharePoint, using the classification this catalog already computed.",
        "pt": "Um rótulo MIP é criptografia real embutida no arquivo do Office, atrelada à infraestrutura da Microsoft — não há como reimplementá-lo localmente. Este conector chama a API REAL do Microsoft Graph para aplicar um rótulo de verdade a um arquivo que já vive no OneDrive/SharePoint, usando a classificação que este catálogo já calculou.",
    },
    "mip_scope_note": {
        "es": "Solo aplica a datasets cuyo archivo fuente ya está en OneDrive/SharePoint — una tabla de base de datos o un CSV que nunca pasó por Microsoft 365 no tiene \"etiqueta MIP\" posible (la etiqueta vive en el formato del archivo, no en el dato en abstracto).",
        "en": "Only applies to datasets whose source file already lives in OneDrive/SharePoint — a database table or a CSV that never went through Microsoft 365 has no possible \"MIP label\" (the label lives in the file format, not in the abstract data).",
        "pt": "Só se aplica a datasets cujo arquivo fonte já está no OneDrive/SharePoint — uma tabela de banco de dados ou um CSV que nunca passou pelo Microsoft 365 não tem \"rótulo MIP\" possível (o rótulo vive no formato do arquivo, não no dado em abstrato).",
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
    "mip_preview": {"es": "Previsualizar etiquetas", "en": "Preview labels", "pt": "Pré-visualizar rótulos"},
    "mip_push": {"es": "Aplicar etiquetas reales", "en": "Apply real labels", "pt": "Aplicar rótulos reais"},
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
    "scanall_title": {"es": "Escanear todas las conexiones guardadas", "en": "Scan all saved connections", "pt": "Escanear todas as conexões salvas"},
    "scanall_intro": {
        "es": "Un clic en vez de elegir conexión por conexión: lista las tablas de TODAS tus conexiones guardadas de una vez. Cubre los motores que vos configuraste acá (9 hoy) — no es descubrimiento automático de fuentes nuevas como el escaneo de tenant de Purview, que agrega agentes dentro de Azure y encuentra recursos sin que nadie cargue una conexión a mano.",
        "en": "One click instead of picking connections one by one: lists the tables of ALL your saved connections at once. Covers the engines you configured here (9 today) — it's not automatic discovery of new sources like Purview's tenant scan, which deploys agents inside Azure and finds resources without anyone loading a connection by hand.",
        "pt": "Um clique em vez de escolher conexão por conexão: lista as tabelas de TODAS as suas conexões salvas de uma vez. Cobre os motores que você configurou aqui (9 hoje) — não é descoberta automática de fontes novas como o escaneamento de tenant do Purview, que implanta agentes dentro do Azure e encontra recursos sem que ninguém carregue uma conexão manualmente.",
    },
    "scanall_run": {"es": "▶ Escanear todas ahora", "en": "▶ Scan all now", "pt": "▶ Escanear todas agora"},
    "scanall_tables": {"es": "Tablas encontradas", "en": "Tables found", "pt": "Tabelas encontradas"},
    "scanall_errors": {"es": "Conexiones con error", "en": "Connections with errors", "pt": "Conexões com erro"},
    "scanall_none": {"es": "No hay conexiones guardadas todavía — agregá una en Mis datos.", "en": "No saved connections yet — add one in My data.", "pt": "Ainda não há conexões salvas — adicione uma em Meus dados."},
    "scanall_local_note": {
        "es": "Una conexión caída no frena el escaneo de las demás — el error queda registrado en su fila.",
        "en": "A connection that's down doesn't stop the scan of the rest — the error is recorded in its row.",
        "pt": "Uma conexão fora do ar não interrompe o escaneamento das demais — o erro fica registrado na sua linha.",
    },
    # ------------------------------------------------------- Azure discovery (azd)
    "azd_title": {"es": "Descubrimiento en Azure (Resource Graph)", "en": "Azure discovery (Resource Graph)", "pt": "Descoberta no Azure (Resource Graph)"},
    "azd_intro": {
        "es": "Esto NO es \"convertirse en Purview\" — Purview escanea desplegando agentes dentro de tu infraestructura de Azure. Esto es más chico pero real: con tu service principal (rol Reader, de solo lectura), UNA consulta a la Azure Resource Graph API trae todos los recursos de datos (SQL, Storage, Synapse, Cosmos DB, Databricks...) de toda tu suscripción, sin cargar conexiones una por una. Trae inventario (nombre, tipo, resource group) — no perfila columnas ni corre reglas; para gobernar cada uno de verdad, igual hay que cargarlo como conexión en Mis datos.",
        "en": "This is NOT \"becoming Purview\" — Purview scans by deploying agents inside your Azure infrastructure. This is smaller but real: with your service principal (Reader role, read-only), ONE query to the Azure Resource Graph API brings back all data resources (SQL, Storage, Synapse, Cosmos DB, Databricks...) across your whole subscription, without loading connections one by one. It brings inventory (name, type, resource group) — it doesn't profile columns or run rules; to actually govern each one, you still need to load it as a connection in My data.",
        "pt": "Isso NÃO é \"virar o Purview\" — o Purview varre implantando agentes dentro da sua infraestrutura Azure. Isso é menor mas real: com seu service principal (papel Reader, somente leitura), UMA consulta à Azure Resource Graph API traz todos os recursos de dados (SQL, Storage, Synapse, Cosmos DB, Databricks...) de toda a sua assinatura, sem carregar conexões uma por uma. Traz inventário (nome, tipo, resource group) — não perfila colunas nem roda regras; para governar cada um de verdade, ainda é preciso carregá-lo como conexão em Meus dados.",
    },
    "azd_env": {
        "es": "Sin configurar — cargá `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_SUBSCRIPTION_ID` (service principal con rol Reader sobre la suscripción).",
        "en": "Not configured — set `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_SUBSCRIPTION_ID` (service principal with Reader role on the subscription).",
        "pt": "Não configurado — configure `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_SUBSCRIPTION_ID` (service principal com papel Reader na assinatura).",
    },
    "azd_run": {"es": "Descubrir recursos de datos", "en": "Discover data resources", "pt": "Descobrir recursos de dados"},
    "azd_found": {"es": "Recursos encontrados", "en": "Resources found", "pt": "Recursos encontrados"},
    "azd_none": {"es": "No se encontraron recursos de datos en esta suscripción.", "en": "No data resources found in this subscription.", "pt": "Nenhum recurso de dados encontrado nesta assinatura."},
    "azd_local_note": {
        "es": "Apagado por defecto. Implementado contra Microsoft Learn (Azure Resource Graph REST API); no probado contra una suscripción real. Solo lectura (rol Reader) — nunca modifica nada en tu Azure.",
        "en": "Off by default. Implemented against Microsoft Learn (Azure Resource Graph REST API); not tested against a live subscription. Read-only (Reader role) — never modifies anything in your Azure.",
        "pt": "Desligado por padrão. Implementado contra o Microsoft Learn (Azure Resource Graph REST API); não testado contra uma assinatura real. Somente leitura (papel Reader) — nunca modifica nada no seu Azure.",
    },
    # ---------------------------------------------------------- Collibra pull (cbp)
    "cbp_title": {"es": "Traer de Collibra (conector inverso)", "en": "Pull from Collibra (reverse connector)", "pt": "Trazer do Collibra (conector inverso)"},
    "cbp_intro": {
        "es": "Complemento de Migración: en vez de empujar hacia Collibra, esto TRAE lo que Collibra ya tiene — Business Terms aprobados y assets de tipo Tabla, con su definición — para no tipear de nuevo lo que la empresa ya documentó ahí. No trae asignaciones de Owner/Steward (esa API de Collibra no está documentada con suficiente detalle como para implementarla sin adivinar).",
        "en": "Complement of Migration: instead of pushing to Collibra, this PULLS what Collibra already has — approved Business Terms and Table-type assets, with their definition — so you don't retype what the company already documented there. Doesn't pull Owner/Steward assignments (that Collibra API isn't documented in enough detail to implement without guessing).",
        "pt": "Complemento de Migração: em vez de empurrar para o Collibra, isso TRAZ o que o Collibra já tem — Business Terms aprovados e assets do tipo Tabela, com sua definição — para não digitar de novo o que a empresa já documentou lá. Não traz atribuições de Owner/Steward (essa API do Collibra não está documentada com detalhe suficiente para implementar sem adivinhar).",
    },
    "cbp_env": {
        "es": "Sin configurar — mismas variables que Migración (`COLLIBRA_BASE_URL`, `COLLIBRA_USERNAME`, `COLLIBRA_PASSWORD`, `COLLIBRA_DOMAIN_ID`; `COLLIBRA_TABLE_TYPE_ID` además para traer catálogo).",
        "en": "Not configured — same variables as Migration (`COLLIBRA_BASE_URL`, `COLLIBRA_USERNAME`, `COLLIBRA_PASSWORD`, `COLLIBRA_DOMAIN_ID`; `COLLIBRA_TABLE_TYPE_ID` too, to pull catalog).",
        "pt": "Não configurado — mesmas variáveis que Migração (`COLLIBRA_BASE_URL`, `COLLIBRA_USERNAME`, `COLLIBRA_PASSWORD`, `COLLIBRA_DOMAIN_ID`; `COLLIBRA_TABLE_TYPE_ID` também, para trazer catálogo).",
    },
    "cbp_run": {"es": "Traer de Collibra ahora", "en": "Pull from Collibra now", "pt": "Trazer do Collibra agora"},
    "cbp_terms": {"es": "Términos traídos", "en": "Terms pulled", "pt": "Termos trazidos"},
    "cbp_tables": {"es": "Tablas traídas", "en": "Tables pulled", "pt": "Tabelas trazidas"},
    "cbp_catalog_skipped": {"es": "Catálogo salteado", "en": "Catalog skipped", "pt": "Catálogo pulado"},
    "cbp_download_terms": {"es": "Descargar términos (.csv)", "en": "Download terms (.csv)", "pt": "Baixar termos (.csv)"},
    "cbp_download_tables": {"es": "Descargar tablas (.csv)", "en": "Download tables (.csv)", "pt": "Baixar tabelas (.csv)"},
    "cbp_local_note": {
        "es": "Apagado por defecto. Esto solo LEE de tu instancia de Collibra — no modifica ni borra nada ahí. Lo que se trae queda en esta pantalla; guardarlo en el programa (botón Guardar localmente) es un paso manual, a propósito.",
        "en": "Off by default. This only READS from your Collibra instance — it never modifies or deletes anything there. What's pulled stays on this screen; saving it into the program (Save locally button) is a manual step, on purpose.",
        "pt": "Desligado por padrão. Isso apenas LÊ da sua instância Collibra — nunca modifica ou apaga nada lá. O que é trazido fica nesta tela; salvá-lo no programa (botão Salvar localmente) é um passo manual, de propósito.",
    },
    # ----------------------------------------------------------- Purview pull (pvp)
    "pvp_title": {"es": "Traer de Purview (conector inverso)", "en": "Pull from Purview (reverse connector)", "pt": "Trazer do Purview (conector inverso)"},
    "pvp_intro": {
        "es": "Igual que Traer de Collibra, pero para Purview: trae los términos del glosario \"MV Data Governance\" que ya vive ahí (los que este mismo programa empujó, o los que alguien agregó directo en Purview) — para no perder trabajo hecho del lado de Purview.",
        "en": "Same as Pull from Collibra, but for Purview: pulls the terms of the \"MV Data Governance\" glossary that already lives there (whether this program pushed them, or someone added them directly in Purview) — so work done on the Purview side isn't lost.",
        "pt": "Igual a Trazer do Collibra, mas para o Purview: traz os termos do glossário \"MV Data Governance\" que já vive lá (os que este programa empurrou, ou os que alguém adicionou direto no Purview) — para não perder trabalho feito do lado do Purview.",
    },
    "pvp_env": {
        "es": "Sin configurar — mismas variables que Migración (`PURVIEW_TENANT_ID`, `PURVIEW_CLIENT_ID`, `PURVIEW_CLIENT_SECRET`, `PURVIEW_ACCOUNT_NAME`).",
        "en": "Not configured — same variables as Migration (`PURVIEW_TENANT_ID`, `PURVIEW_CLIENT_ID`, `PURVIEW_CLIENT_SECRET`, `PURVIEW_ACCOUNT_NAME`).",
        "pt": "Não configurado — mesmas variáveis que Migração (`PURVIEW_TENANT_ID`, `PURVIEW_CLIENT_ID`, `PURVIEW_CLIENT_SECRET`, `PURVIEW_ACCOUNT_NAME`).",
    },
    "pvp_run": {"es": "Traer de Purview ahora", "en": "Pull from Purview now", "pt": "Trazer do Purview agora"},
    "pvp_terms": {"es": "Términos traídos", "en": "Terms pulled", "pt": "Termos trazidos"},
    "pvp_download_terms": {"es": "Descargar términos (.csv)", "en": "Download terms (.csv)", "pt": "Baixar termos (.csv)"},
    "pvp_local_note": {
        "es": "Apagado por defecto. Esto solo LEE de tu Purview — no modifica ni borra nada ahí. El catálogo usa la API de Discovery vigente de Microsoft (`/datamap/api/search/query`), distinta de la que usa el resto del conector — ver docs/PURVIEW_COLLIBRA.md.",
        "en": "Off by default. This only READS from your Purview — it never modifies or deletes anything there. Catalog uses Microsoft's current Discovery API (`/datamap/api/search/query`), different from the one the rest of the connector uses — see docs/PURVIEW_COLLIBRA.md.",
        "pt": "Desligado por padrão. Isso apenas LÊ do seu Purview — nunca modifica ou apaga nada lá. O catálogo usa a API de Discovery vigente da Microsoft (`/datamap/api/search/query`), diferente da que o resto do conector usa — veja docs/PURVIEW_COLLIBRA.md.",
    },
    # --------------------------------------------------- importado (persistencia del pull)
    "imp_save": {"es": "Guardar localmente", "en": "Save locally", "pt": "Salvar localmente"},
    "imp_saved_ok": {"es": "Guardado: {n} ítem(s).", "en": "Saved: {n} item(s).", "pt": "Salvo: {n} item(ns)."},
    "imp_title": {"es": "Importado (guardado localmente)", "en": "Imported (saved locally)", "pt": "Importado (salvo localmente)"},
    "imp_intro": {
        "es": "Lo que trajiste de Purview/Collibra y guardaste con — persiste entre sesiones (~/.mv_data_governance/importado.json).",
        "en": "What you pulled from Purview/Collibra and saved with — persists across sessions (~/.mv_data_governance/importado.json).",
        "pt": "O que você trouxe do Purview/Collibra e salvou com — persiste entre sessões (~/.mv_data_governance/importado.json).",
    },
    "imp_curation_note": {
        "es": "Esto no queda aislado: cada término/tabla importado aparece también en Curaduría, con su origen visible, esperando que un Data Owner/Steward lo valide como cualquier otra definición del programa.",
        "en": "This doesn't stay isolated: every imported term/table also shows up in Curation, with its origin visible, waiting for a Data Owner/Steward to validate it like any other definition in the program.",
        "pt": "Isso não fica isolado: cada termo/tabela importado também aparece em Curadoria, com sua origem visível, esperando que um Data Owner/Steward o valide como qualquer outra definição do programa.",
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
    "cl_new": {"es": "Nueva ficha / editar", "en": "New record / edit", "pt": "Nova ficha / editar"},
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
    # etiquetas del estado comercial de la ficha, con su significado entre
    # paréntesis — el valor guardado sigue siendo la clave corta (lead, demo...)
    "cl_st_lead": {
        "es": "lead (interesado, todavía sin demo ni reunión)",
        "en": "lead (interested, no demo or meeting yet)",
        "pt": "lead (interessado, ainda sem demo nem reunião)",
    },
    "cl_st_demo": {
        "es": "demo (ya vio una demostración del programa)",
        "en": "demo (already saw a demo of the program)",
        "pt": "demo (já viu uma demonstração do programa)",
    },
    "cl_st_piloto": {
        "es": "piloto (lo está probando con sus datos, sin pagar aún)",
        "en": "pilot (trying it with their data, not paying yet)",
        "pt": "piloto (testando com seus dados, ainda sem pagar)",
    },
    "cl_st_activo": {
        "es": "activo (cliente pagando / usándolo en serio)",
        "en": "active (paying client / using it for real)",
        "pt": "ativo (cliente pagando / usando de verdade)",
    },
    "cl_st_cerrado": {
        "es": "cerrado (no avanzó o se dio de baja)",
        "en": "closed (didn't move forward or churned)",
        "pt": "fechado (não avançou ou cancelou)",
    },
    "cl_notes": {"es": "Notas", "en": "Notes", "pt": "Notas"},
    "cl_save": {"es": "Guardar ficha", "en": "Save record", "pt": "Salvar ficha"},
    "cl_saved": {"es": "Ficha guardada.", "en": "Record saved.", "pt": "Ficha salva."},
    "cl_need_name": {"es": "Poné al menos el nombre de la empresa.", "en": "Enter at least the company name.", "pt": "Informe pelo menos o nome da empresa."},
    "cl_delete": {"es": "Eliminar ficha", "en": "Delete record", "pt": "Excluir ficha"},
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
        "es": "Primero creá una empresa en la pestaña Empresas: el proyecto "
              "se guarda por cliente.",
        "en": "First create a company in the Companies tab: the project is "
              "saved per client.",
        "pt": "Primeiro crie uma empresa na aba Empresas: o projeto é salvo "
              "por cliente.",
    },
    "ws_pick_client": {"es": "Cliente", "en": "Client", "pt": "Cliente"},
    "ws_summary_stages": {"es": "Etapas guardadas", "en": "Saved stages", "pt": "Etapas salvas"},
    "ws_summary_tables": {"es": "Tablas", "en": "Tables", "pt": "Tabelas"},
    "ws_summary_rows": {"es": "Filas guardadas", "en": "Saved rows", "pt": "Linhas salvas"},
    "ws_summary_updated": {"es": "Última actualización", "en": "Last update", "pt": "Última atualização"},
    "ws_save_title": {"es": "Guardar la etapa actual", "en": "Save the current stage", "pt": "Salvar a etapa atual"},
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
    "ws_save_btn": {"es": "Guardar etapa", "en": "Save stage", "pt": "Salvar etapa"},
    "ws_saved_ok": {"es": "Etapa \"{name}\" guardada ({n} tabla/s).", "en": "Stage \"{name}\" saved ({n} table/s).", "pt": "Etapa \"{name}\" salva ({n} tabela/s)."},
    "ws_need_name": {"es": "Poné un nombre para la etapa.", "en": "Enter a name for the stage.", "pt": "Informe um nome para a etapa."},
    "ws_need_selection": {"es": "Elegí al menos una cosa para guardar.", "en": "Select at least one thing to save.", "pt": "Escolha ao menos uma coisa para salvar."},
    "ws_stages_title": {"es": "Etapas guardadas", "en": "Saved stages", "pt": "Etapas salvas"},
    "ws_no_stages": {"es": "Todavía no guardaste ninguna etapa para este cliente.", "en": "You haven't saved any stage for this client yet.", "pt": "Você ainda não salvou nenhuma etapa para este cliente."},
    "ws_col_table": {"es": "Tabla", "en": "Table", "pt": "Tabela"},
    "ws_reload": {"es": "Ver / descargar", "en": "View / download", "pt": "Ver / baixar"},
    "ws_delete": {"es": "Eliminar etapa", "en": "Delete stage", "pt": "Excluir etapa"},
    "ws_deleted": {"es": "Etapa eliminada.", "en": "Stage deleted.", "pt": "Etapa excluída."},
    "ws_export_title": {"es": "Respaldar / restaurar el proyecto completo", "en": "Back up / restore the whole project", "pt": "Backup / restaurar o projeto completo"},
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
    "ws_export_btn": {"es": "Descargar proyecto (ZIP)", "en": "Download project (ZIP)", "pt": "Baixar projeto (ZIP)"},
    "ws_import_btn": {"es": "Restaurar desde un ZIP", "en": "Restore from a ZIP", "pt": "Restaurar de um ZIP"},
    "ws_import_replace": {"es": "Reemplazar las etapas actuales (en vez de sumar)", "en": "Replace current stages (instead of merging)", "pt": "Substituir as etapas atuais (em vez de somar)"},
    "ws_do_import": {"es": "Importar", "en": "Import", "pt": "Importar"},
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
    "h_auto": {"es": "🟢 Automático", "en": "🟢 Automatic", "pt": "🟢 Automático"},
    "h_partial": {"es": "🟡 Parcial", "en": "🟡 Partial", "pt": "🟡 Parcial"},
    "h_human": {"es": "Requiere personas", "en": "Requires people", "pt": "Requer pessoas"},
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
    "h_pvfaq": {"es": "Purview y Collibra: preguntas frecuentes", "en": "Purview and Collibra: frequently asked questions", "pt": "Purview e Collibra: perguntas frequentes"},
    "h_pvfaq_note": {
        "es": "Las mismas preguntas que hace un cliente o un entrevistador, respondidas sin humo. Detalle técnico completo capacidad por capacidad en `docs/PURVIEW_COLLIBRA.md`.",
        "en": "The same questions a client or interviewer asks, answered plainly. Full capability-by-capability technical detail in `docs/PURVIEW_COLLIBRA.md`.",
        "pt": "As mesmas perguntas que um cliente ou entrevistador faz, respondidas sem rodeios. Detalhe técnico completo capacidade por capacidade em `docs/PURVIEW_COLLIBRA.md`.",
    },
    "h_dmbok_covered": {"es": "🟢 Cubierta", "en": "🟢 Covered", "pt": "🟢 Coberta"},
    "h_dmbok_partial": {"es": "🟡 Parcial", "en": "🟡 Partial", "pt": "🟡 Parcial"},
    "h_dmbok_out": {"es": "Fuera de alcance", "en": "Out of scope", "pt": "Fora de escopo"},
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
    "dk_plain": {"es": "En criollo", "en": "In plain words", "pt": "Em linguagem simples"},
    "dk_tech": {"es": "Técnico", "en": "Technical", "pt": "Técnico"},
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
    "dk_subtab_dmbok": {"es": "DAMA-DMBOK", "en": "DAMA-DMBOK", "pt": "DAMA-DMBOK"},
    "dk_subtab_cobit": {"es": "COBIT 2019", "en": "COBIT 2019", "pt": "COBIT 2019"},
    "dk_subtab_iso": {"es": "ISO/IEC 38505", "en": "ISO/IEC 38505", "pt": "ISO/IEC 38505"},
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
    "lab_plain": {"es": "En criollo", "en": "In plain words", "pt": "Em linguagem simples"},
    "lab_tech": {"es": "Detalle técnico", "en": "Technical detail", "pt": "Detalhe técnico"},
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
    "tab_pbi": {"es": "Power BI", "en": "Power BI", "pt": "Power BI"},
    "pbi_intro": {
        "es": "Gobierná el modelo de Power BI en sí: tablas, columnas, medidas (DAX), "
              "relaciones y RLS — solo estructura, nunca tus filas.",
        "en": "Govern the Power BI model itself: tables, columns, measures (DAX), "
              "relationships and RLS — structure only, never your rows.",
        "pt": "Governe o modelo do Power BI em si: tabelas, colunas, medidas (DAX), "
              "relações e RLS — apenas estrutura, nunca suas linhas.",
    },
    "pbi_secure_note": {
        "es": "Ninguna de las dos opciones sube una sola fila de tus datos: el "
              ".pbit lleva solo la estructura, y del .pbip se lee únicamente el "
              "TMDL. Si vas a usar .pbix, guardalo mejor como .pbit.",
        "en": "Neither option uploads a single row of your data: a .pbit carries "
              "only the structure, and from a .pbip only the TMDL is read. If you "
              "were going to use .pbix, save it as .pbit instead.",
        "pt": "Nenhuma das opções envia uma única linha dos seus dados: o .pbit "
              "leva só a estrutura, e do .pbip lê-se apenas o TMDL. Se você ia "
              "usar .pbix, salve como .pbit.",
    },
    "pbi_source": {"es": "Origen", "en": "Source", "pt": "Origem"},
    "pbi_src_path": {"es": "Escribir una ruta local", "en": "Type a local path",
                     "pt": "Digitar um caminho local"},
    "pbi_src_zip": {"es": "Subir el archivo", "en": "Upload the file",
                    "pt": "Enviar o arquivo"},
    "pbi_path": {"es": "Ruta a la carpeta .pbip o al archivo .pbit",
                 "en": "Path to the .pbip folder or the .pbit file",
                 "pt": "Caminho para a pasta .pbip ou o arquivo .pbit"},
    "pbi_path_hint": {
        "es": "Solo si el archivo está en esta misma computadora. Si no, usá "
              "«Subir el archivo», que funciona siempre.",
        "en": "Only if the file is on this same computer. Otherwise use "
              "\"Upload the file\", which always works.",
        "pt": "Só se o arquivo estiver neste mesmo computador. Caso contrário use "
              "\"Enviar o arquivo\", que funciona sempre.",
    },
    "pbi_zip": {"es": "Archivo de Power BI (.pbit, .pbix o .zip del .pbip)",
                "en": "Power BI file (.pbit, .pbix or the .pbip .zip)",
                "pt": "Arquivo do Power BI (.pbit, .pbix ou o .zip do .pbip)"},
    "pbi_zip_hint": {
        "es": "Lo más simple: en Power BI Desktop, Archivo → Guardar como → "
              "Plantilla de Power BI (.pbit) y subí ese archivo.",
        "en": "Simplest path: in Power BI Desktop, File → Save as → Power BI "
              "Template (.pbit) and upload that file.",
        "pt": "O mais simples: no Power BI Desktop, Arquivo → Salvar como → "
              "Modelo do Power BI (.pbit) e envie esse arquivo.",
    },
    "pbi_load": {"es": "Analizar modelo", "en": "Analyze model", "pt": "Analisar modelo"},
    "pbi_model": {"es": "Modelo", "en": "Model", "pt": "Modelo"},
    "pbi_tables": {"es": "Tablas", "en": "Tables", "pt": "Tabelas"},
    "pbi_measures": {"es": "Medidas", "en": "Measures", "pt": "Medidas"},
    "pbi_columns": {"es": "Columnas", "en": "Columns", "pt": "Colunas"},
    "pbi_roles": {"es": "Roles RLS", "en": "RLS roles", "pt": "Papéis RLS"},
    "pbi_catalog_title": {"es": "Catálogo del modelo", "en": "Model catalog",
                          "pt": "Catálogo do modelo"},
    "pbi_dict_title": {"es": "Columnas del modelo", "en": "Model columns",
                       "pt": "Colunas do modelo"},
    "pbi_measures_title": {"es": "Medidas y DAX (glosario)", "en": "Measures & DAX (glossary)",
                           "pt": "Medidas e DAX (glossário)"},
    "pbi_health_title": {"es": "Salud del modelo", "en": "Model health",
                         "pt": "Saúde do modelo"},
    "pbi_health_overall": {"es": "Índice de modelo", "en": "Model index", "pt": "Índice do modelo"},
    "pbi_lineage_title": {"es": "Linaje del modelo", "en": "Model lineage",
                          "pt": "Linhagem do modelo"},
    "pbi_lineage_hint": {
        "es": "Cadena completa: origen SQL detectado → tabla → dataset (modelo) → reporte.",
        "en": "Full chain: detected SQL source → table → dataset (model) → report.",
        "pt": "Cadeia completa: origem SQL detectada → tabela → dataset (modelo) → relatório.",
    },
    "pbi_sources_title": {"es": "Origen SQL por tabla", "en": "SQL source per table",
                          "pt": "Origem SQL por tabela"},
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
    "pbi_refactor": {"es": "Refactor DAX con {provider}", "en": "Refactor DAX with {provider}",
                     "pt": "Refatorar DAX com {provider}"},
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
    "pbi_mode_offline": {"es": "Proyecto local (.pbip)", "en": "Local project (.pbip)",
                         "pt": "Projeto local (.pbip)"},
    "pbi_mode_tenant": {"es": "Tenant completo (Scanner API)", "en": "Full tenant (Scanner API)",
                        "pt": "Tenant completo (Scanner API)"},
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
    "pbi_tenant_scan": {"es": "Escanear tenant completo", "en": "Scan full tenant",
                        "pt": "Escanear tenant completo"},
    "pbi_datasets": {"es": "Datasets", "en": "Datasets", "pt": "Datasets"},
    "pbi_tenant_pick_dataset": {"es": "Ver medidas del dataset…", "en": "View measures for dataset…",
                                "pt": "Ver medidas do dataset…"},
    "pbi_mode_example": {"es": "Ejemplo incluido", "en": "Bundled example", "pt": "Exemplo incluído"},
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
        "es": "Ilustrativo, no un escaneo real: es el mismo modelo real de arriba, replicado y "
              "re-etiquetado en varios workspaces simulados, para mostrar cómo se ve "
              "ingest_tenant() a escala en una empresa multinacional. Para un escaneo real de tu "
              "propio tenant, usá el modo Tenant completo con tus credenciales.",
        "en": "Illustrative, not a real scan: it's the same real model above, replicated and "
              "relabeled across several simulated workspaces, to show what ingest_tenant() looks "
              "like at multinational scale. For a real scan of your own tenant, use Full tenant "
              "mode with your own credentials.",
        "pt": "Ilustrativo, não um escaneamento real: é o mesmo modelo real acima, replicado e "
              "reetiquetado em vários workspaces simulados, para mostrar como fica o "
              "ingest_tenant() em escala numa multinacional. Para um escaneamento real do seu "
              "próprio tenant, use o modo Tenant completo com suas credenciais.",
    },
    # ---------------------------------------------------------------- Tableau
    "tab_tableau": {"es": "Tableau", "en": "Tableau", "pt": "Tableau"},
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
    "tab_scan": {"es": "Escanear sitio completo", "en": "Scan full site",
                "pt": "Escanear site completo"},
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
    "tab_catalog_title": {"es": "Catálogo de datasources", "en": "Datasource catalog",
                          "pt": "Catálogo de datasources"},
    "tab_health_title": {"es": "Salud del sitio", "en": "Site health", "pt": "Saúde do site"},
    "tab_health_overall": {"es": "Índice del sitio", "en": "Site index", "pt": "Índice do site"},
    "tab_sources_title": {"es": "Origen por datasource", "en": "Source per datasource",
                          "pt": "Origem por datasource"},
    "tab_sources_hint": {
        "es": "Tablas de base de datos detectadas como origen de cada datasource publicado.",
        "en": "Database tables detected as the source of each published datasource.",
        "pt": "Tabelas de banco de dados detectadas como origem de cada datasource publicado.",
    },
    "tab_lineage_title": {"es": "Linaje del sitio", "en": "Site lineage", "pt": "Linhagem do site"},
    "tab_lineage_hint": {
        "es": "Cadena completa: tabla de base de datos → datasource publicado → workbook.",
        "en": "Full chain: database table → published datasource → workbook.",
        "pt": "Cadeia completa: tabela de banco de dados → datasource publicado → workbook.",
    },
    "tab_calc_title": {"es": "Campos calculados (glosario)", "en": "Calculated fields (glossary)",
                       "pt": "Campos calculados (glossário)"},
    "tab_refactor": {"es": "Refactor con {provider}", "en": "Refactor with {provider}",
                     "pt": "Refatorar com {provider}"},
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
    "tab_mode_offline": {"es": "Workbook local (.twb/.twbx)", "en": "Local workbook (.twb/.twbx)",
                         "pt": "Workbook local (.twb/.twbx)"},
    "tab_mode_site": {"es": "Sitio completo (Metadata API)", "en": "Full site (Metadata API)",
                      "pt": "Site completo (Metadata API)"},
    "tab_mode_example": {"es": "Ejemplo incluido", "en": "Bundled example", "pt": "Exemplo incluído"},
    "tab_src_path": {"es": "¿El archivo está en esta misma computadora? Escribí la ruta",
                     "en": "Is the file on this same computer? Type the path",
                     "pt": "O arquivo está neste mesmo computador? Digite o caminho"},
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
        "es": "Un nombre común (\"Ana Costa\") solo no alcanza para marcar un duplicado — "
              "hace falta que además coincida un identificador fuerte (documento, email). Así "
              "se evitan falsos positivos entre personas distintas con el mismo nombre.",
        "en": "A common name (\"Ana Costa\") alone isn't enough to flag a duplicate — a "
              "strong identifier (ID, email) must also match. This avoids false positives "
              "between different people sharing a name.",
        "pt": "Um nome comum (\"Ana Costa\") sozinho não basta para marcar um duplicado — é "
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
    "mdm_run": {"es": "Buscar duplicados", "en": "Find duplicates", "pt": "Buscar duplicados"},
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
    "mdm_golden_title": {"es": "Golden record propuesto", "en": "Proposed golden record",
                         "pt": "Golden record proposto"},

    # ------------------------------------------------- errores accionables
    # Cada uno dice QUE hacer, no solo que fallo. El detalle tecnico
    # (TipoDeError: texto) se muestra aparte, plegado. Ver mvdg/errors.py.
    "err_encoding": {
        "es": "El archivo no está en UTF-8. Abrilo en Excel y guardalo como "
              "«CSV UTF-8 (delimitado por comas)», o exportalo de nuevo eligiendo UTF-8.",
        "en": "The file is not UTF-8. Open it in Excel and save it as "
              "“CSV UTF-8 (comma delimited)”, or export it again choosing UTF-8.",
        "pt": "O arquivo não está em UTF-8. Abra no Excel e salve como "
              "“CSV UTF-8 (delimitado por vírgulas)”, ou exporte novamente escolhendo UTF-8.",
    },
    "err_vacio": {
        "es": "El archivo está vacío o no tiene encabezados. Revisá que la "
              "primera fila tenga los nombres de las columnas.",
        "en": "The file is empty or has no headers. Check that the first row "
              "contains the column names.",
        "pt": "O arquivo está vazio ou não tem cabeçalhos. Verifique se a "
              "primeira linha tem os nomes das colunas.",
    },
    "err_csv_malformado": {
        "es": "El CSV tiene filas con distinta cantidad de columnas, o usa otro "
              "separador. Revisá que todas las filas tengan las mismas columnas "
              "y que el separador sea coma o punto y coma.",
        "en": "The CSV has rows with different column counts, or uses another "
              "separator. Check that every row has the same columns and that the "
              "separator is a comma or semicolon.",
        "pt": "O CSV tem linhas com quantidades diferentes de colunas, ou usa "
              "outro separador. Verifique se todas as linhas têm as mesmas colunas "
              "e se o separador é vírgula ou ponto e vírgula.",
    },
    "err_excel_formato": {
        "es": "No se pudo leer el Excel: el formato no coincide con la extensión. "
              "Abrilo y volvé a guardarlo como .xlsx.",
        "en": "Could not read the Excel file: the format does not match the "
              "extension. Open it and save it again as .xlsx.",
        "pt": "Não foi possível ler o Excel: o formato não corresponde à extensão. "
              "Abra e salve novamente como .xlsx.",
    },
    "err_zip": {
        "es": "El archivo no es un ZIP válido o está incompleto. Volvé a "
              "descargarlo o a exportarlo.",
        "en": "The file is not a valid ZIP or is incomplete. Download or export "
              "it again.",
        "pt": "O arquivo não é um ZIP válido ou está incompleto. Baixe ou exporte "
              "novamente.",
    },
    # --- Power BI: por qué un archivo no se puede leer y qué hacer ---
    "err_pbix_binario": {
        "es": "Este .pbix guarda el modelo en binario (respaldo de Analysis "
              "Services), que no se puede leer sin las librerías de Microsoft. "
              "Abrilo en Power BI Desktop y usá Archivo → Guardar como → "
              "Plantilla de Power BI (.pbit): ese sí trae la estructura y no "
              "lleva ni una fila de tus datos.",
        "en": "This .pbix stores the model in binary (an Analysis Services "
              "backup), which cannot be read without Microsoft's libraries. "
              "Open it in Power BI Desktop and use File → Save as → Power BI "
              "Template (.pbit): that one carries the structure and not a "
              "single row of your data.",
        "pt": "Este .pbix guarda o modelo em binário (backup do Analysis "
              "Services), que não dá para ler sem as bibliotecas da Microsoft. "
              "Abra no Power BI Desktop e use Arquivo → Salvar como → Modelo "
              "do Power BI (.pbit): esse traz a estrutura e nenhuma linha dos "
              "seus dados.",
    },
    "err_pbi_sin_modelo": {
        "es": "El archivo no tiene adentro ningún modelo de Power BI. "
              "¿Es el archivo correcto? Se aceptan .pbit, .pbix, el .zip de un "
              "proyecto .pbip, o la carpeta del proyecto .pbip.",
        "en": "The file contains no Power BI model. Is this the right file? "
              "Accepted: .pbit, .pbix, the .zip of a .pbip project, or the "
              ".pbip project folder.",
        "pt": "O arquivo não contém nenhum modelo do Power BI. É o arquivo "
              "certo? São aceitos .pbit, .pbix, o .zip de um projeto .pbip, "
              "ou a pasta do projeto .pbip.",
    },
    "err_pbi_extension": {
        "es": "Ese formato no es de Power BI. Se aceptan .pbit, .pbix, el .zip "
              "de un proyecto .pbip, o la carpeta del proyecto .pbip.",
        "en": "That format is not a Power BI one. Accepted: .pbit, .pbix, the "
              ".zip of a .pbip project, or the .pbip project folder.",
        "pt": "Esse formato não é do Power BI. São aceitos .pbit, .pbix, o "
              ".zip de um projeto .pbip, ou a pasta do projeto .pbip.",
    },
    "err_json": {
        "es": "El JSON no es válido. Revisá que no falten comas o llaves — "
              "podés validarlo en cualquier verificador de JSON.",
        "en": "The JSON is not valid. Check for missing commas or braces — you "
              "can validate it in any JSON checker.",
        "pt": "O JSON não é válido. Verifique se faltam vírgulas ou chaves — "
              "você pode validá-lo em qualquer verificador de JSON.",
    },
    "err_permiso": {
        "es": "No se pudo acceder al archivo. Si lo tenés abierto en Excel, "
              "cerralo y probá de nuevo.",
        "en": "Could not access the file. If you have it open in Excel, close it "
              "and try again.",
        "pt": "Não foi possível acessar o arquivo. Se estiver aberto no Excel, "
              "feche e tente novamente.",
    },
    "err_no_existe": {
        "es": "No se encontró el archivo. Puede que lo hayan movido o borrado — "
              "volvé a seleccionarlo.",
        "en": "File not found. It may have been moved or deleted — select it again.",
        "pt": "Arquivo não encontrado. Pode ter sido movido ou excluído — "
              "selecione novamente.",
    },
    "err_memoria": {
        "es": "El archivo es demasiado grande para procesarlo entero. Probá con "
              "una muestra, o conectá la base directamente en «Mis datos».",
        "en": "The file is too large to process at once. Try a sample, or connect "
              "the database directly under “My data”.",
        "pt": "O arquivo é grande demais para processar de uma vez. Tente uma "
              "amostra, ou conecte o banco diretamente em “Meus dados”.",
    },
    "err_archivo_generico": {
        "es": "No se pudo leer el archivo. Revisá que sea un CSV o Excel válido "
              "y que no esté abierto en otro programa.",
        "en": "Could not read the file. Check that it is a valid CSV or Excel file "
              "and that it is not open in another program.",
        "pt": "Não foi possível ler o arquivo. Verifique se é um CSV ou Excel "
              "válido e se não está aberto em outro programa.",
    },
    "err_falta_driver": {
        "es": "Falta una dependencia para este formato o motor de base. El detalle "
              "de abajo dice cuál — se instala con «pip install <nombre>».",
        "en": "A dependency for this format or database engine is missing. The "
              "detail below says which one — install it with “pip install <name>”.",
        "pt": "Falta uma dependência para este formato ou motor de banco. O detalhe "
              "abaixo indica qual — instale com “pip install <nome>”.",
    },
    "err_credenciales": {
        "es": "Usuario o contraseña incorrectos. Revisá las credenciales de la "
              "conexión y volvé a probar.",
        "en": "Wrong username or password. Check the connection credentials and "
              "try again.",
        "pt": "Usuário ou senha incorretos. Verifique as credenciais da conexão e "
              "tente novamente.",
    },
    "err_host": {
        "es": "No se pudo alcanzar el servidor. Revisá el host y el puerto, y que "
              "haya red o VPN hacia esa base.",
        "en": "Could not reach the server. Check the host and port, and that you "
              "have network or VPN access to that database.",
        "pt": "Não foi possível alcançar o servidor. Verifique o host e a porta, e "
              "se há rede ou VPN até esse banco.",
    },
    "err_base_datos": {
        "es": "La base rechazó la conexión. Revisá host, puerto, base y permisos "
              "del usuario.",
        "en": "The database refused the connection. Check host, port, database and "
              "user permissions.",
        "pt": "O banco recusou a conexão. Verifique host, porta, base e permissões "
              "do usuário.",
    },
    "err_consulta": {
        "es": "La consulta no se pudo ejecutar. Revisá los nombres de tabla y "
              "columna — el detalle de abajo indica cuál falló.",
        "en": "The query could not run. Check table and column names — the detail "
              "below shows which one failed.",
        "pt": "A consulta não pôde ser executada. Verifique os nomes de tabela e "
              "coluna — o detalhe abaixo indica qual falhou.",
    },
    "err_red": {
        "es": "No hay conexión con el servicio. Revisá tu red o proxy y volvé a "
              "intentar — el resto del programa funciona sin conexión.",
        "en": "No connection to the service. Check your network or proxy and try "
              "again — the rest of the program works offline.",
        "pt": "Sem conexão com o serviço. Verifique sua rede ou proxy e tente "
              "novamente — o resto do programa funciona offline.",
    },
    "err_generico": {
        "es": "No se pudo completar la operación. El detalle técnico está abajo; "
              "si se repite, mandalo junto con lo que estabas haciendo.",
        "en": "The operation could not be completed. The technical detail is below; "
              "if it keeps happening, send it along with what you were doing.",
        "pt": "Não foi possível concluir a operação. O detalhe técnico está abaixo; "
              "se persistir, envie junto com o que você estava fazendo.",
    },
    "err_detalle": {
        "es": "Ver detalle técnico",
        "en": "Show technical detail",
        "pt": "Ver detalhe técnico",
    },

    # ========================================================================
    # Ingeniería de datos automática (mvdg/dataeng.py) — pestaña nueva,
    # gratuita: perfilado avanzado + calidad por 6 dimensiones + claves/joins
    # + tiempo + target/fuga (leakage) + feature engineering + DDL sugerido,
    # sobre un archivo o una base de datos (mvdg/connectors.py).
    #
    # Los mensajes con {placeholders} (qi_*, fuga_*, fx_*) los arma el
    # backend con `.format(**valores)` usando la `lang` pedida — mismo
    # patrón que ya usa `mvdg/profiler.py::suggest_rules`. El resto son
    # etiquetas de interfaz (chrome), usadas por Streamlit y espejadas en
    # `electron/ui/src/i18n.js` para el .exe.
    # ========================================================================
    "de_tab": {"es": "Ingeniería de datos", "en": "Data Engineering", "pt": "Engenharia de dados"},
    "de_titulo": {"es": "Ingeniería de datos automática",
                  "en": "Automatic data engineering",
                  "pt": "Engenharia de dados automática"},
    "de_bajada": {
        "es": "Subí uno o varios archivos, o conectate a tu base de datos. En segundos: "
              "calidad por 6 dimensiones, claves y joins sugeridos, análisis temporal, "
              "detección de fuga contra un target y features listas para modelar.",
        "en": "Upload one or more files, or connect to your database. In seconds: "
              "quality across 6 dimensions, suggested keys and joins, time analysis, "
              "leakage detection against a target, and model-ready features.",
        "pt": "Envie um ou mais arquivos, ou conecte ao seu banco de dados. Em segundos: "
              "qualidade em 6 dimensões, chaves e joins sugeridos, análise temporal, "
              "detecção de vazamento contra um target e features prontas para modelar.",
    },
    # Streamlit reusa el DataFrame que la pestaña "Mis datos" ya cargó (no
    # tiene su propio selector de archivo/base), así que "de_bajada" —
    # pensada para el .exe, que SÍ tiene su propio uploader — quedaba
    # engañosa acá adentro: prometía subir algo que esta sección no pide.
    "de_bajada_streamlit": {
        "es": "Motor completo sobre los mismos datos que ya cargaste arriba: calidad por "
              "6 dimensiones, claves y joins, análisis temporal, fuga contra un target y "
              "features listas para modelar.",
        "en": "The full engine over the same data you already loaded above: quality "
              "across 6 dimensions, keys and joins, time analysis, leakage detection "
              "against a target, and model-ready features.",
        "pt": "O motor completo sobre os mesmos dados que você já carregou acima: "
              "qualidade em 6 dimensões, chaves e joins, análise temporal, vazamento "
              "contra um target e features prontas para modelar.",
    },
    "de_privado": {
        "es": "Los archivos no salen de tu computadora: se leen en memoria y no se guardan "
              "en ningún lado. Una conexión a base de datos usa tus propias credenciales, "
              "en el momento — nunca quedan guardadas salvo que vos lo pidas.",
        "en": "Files never leave your computer: they are read in memory and stored "
              "nowhere. A database connection uses your own credentials, on the spot — "
              "never saved unless you ask for it.",
        "pt": "Os arquivos não saem do seu computador: são lidos na memória e não ficam "
              "guardados em lugar nenhum. Uma conexão de banco de dados usa suas próprias "
              "credenciais, na hora — nunca ficam guardadas a menos que você peça.",
    },

    "de_fuente": {"es": "Fuente de datos", "en": "Data source", "pt": "Fonte de dados"},
    "de_fuente_archivo": {"es": "Archivo", "en": "File", "pt": "Arquivo"},
    "de_fuente_db": {"es": "Base de datos", "en": "Database", "pt": "Banco de dados"},

    "de_elegir_archivos": {"es": "Elegir archivo(s)", "en": "Choose file(s)", "pt": "Escolher arquivo(s)"},
    "de_leyendo": {"es": "Analizando…", "en": "Analyzing…", "pt": "Analisando…"},
    "de_vacio": {"es": "Todavía no analizaste ningún dato.",
                 "en": "You haven't analyzed any data yet.",
                 "pt": "Você ainda não analisou nenhum dado."},
    "de_target": {"es": "Columna objetivo (opcional)", "en": "Target column (optional)",
                  "pt": "Coluna objetivo (opcional)"},
    "de_target_ph": {"es": "ej: pago, churn, resultado", "en": "e.g. paid, churn, outcome",
                     "pt": "ex: pago, churn, resultado"},
    "de_target_ayuda": {
        "es": "Si la indicás, se rankean las variables contra ella y se avisa si alguna "
              "\"predice demasiado bien\" — la forma más común de fuga de información.",
        "en": "If given, variables are ranked against it and you're warned if one "
              "\"predicts too well\" — the most common form of information leakage.",
        "pt": "Se informada, as variáveis são ranqueadas contra ela e avisamos se alguma "
              "\"prevê bem demais\" — a forma mais comum de vazamento de informação.",
    },
    "de_tiempo_col": {"es": "Columna de fecha (opcional)", "en": "Date column (optional)",
                      "pt": "Coluna de data (opcional)"},
    "de_tiempo_col_ph": {"es": "se detecta sola si no la elegís",
                         "en": "auto-detected if you don't pick one",
                         "pt": "detectada sozinha se você não escolher"},
    "de_analizar": {"es": "Analizar", "en": "Analyze", "pt": "Analisar"},
    "de_grande": {"es": "El archivo pasa el tamaño máximo permitido.",
                  "en": "The file is over the maximum allowed size.",
                  "pt": "O arquivo passa do tamanho máximo permitido."},
    "de_malo": {"es": "No se pudo leer alguno de los archivos.",
                "en": "One of the files could not be read.",
                "pt": "Não foi possível ler um dos arquivos."},
    "de_muestreado": {
        "es": "Se analizaron las primeras filas, no todas — el resultado es representativo "
              "pero no exhaustivo.",
        "en": "The first rows were analyzed, not all of them — the result is "
              "representative but not exhaustive.",
        "pt": "Foram analisadas as primeiras linhas, não todas — o resultado é "
              "representativo mas não exaustivo.",
    },

    # --- Conexión a base de datos ------------------------------------------
    "de_db_motor": {"es": "Motor", "en": "Engine", "pt": "Motor"},
    "de_db_host": {"es": "Servidor", "en": "Host", "pt": "Servidor"},
    "de_db_puerto": {"es": "Puerto", "en": "Port", "pt": "Porta"},
    "de_db_base": {"es": "Base de datos", "en": "Database", "pt": "Banco de dados"},
    "de_db_usuario": {"es": "Usuario", "en": "User", "pt": "Usuário"},
    "de_db_clave": {"es": "Contraseña", "en": "Password", "pt": "Senha"},
    "de_db_ruta_sqlite": {"es": "Ruta del archivo .sqlite", "en": "Path to the .sqlite file",
                          "pt": "Caminho do arquivo .sqlite"},
    "de_db_extra": {"es": "Parámetros propios de este motor (JSON)",
                    "en": "Engine-specific parameters (JSON)",
                    "pt": "Parâmetros próprios deste motor (JSON)"},
    "de_db_probar": {"es": "Probar conexión", "en": "Test connection", "pt": "Testar conexão"},
    "de_db_probando": {"es": "Probando…", "en": "Testing…", "pt": "Testando…"},
    "de_db_tabla": {"es": "Tabla", "en": "Table", "pt": "Tabela"},
    "de_db_elegir_tabla": {"es": "Elegí una tabla…", "en": "Pick a table…", "pt": "Escolha uma tabela…"},
    "de_db_cargar_tabla": {"es": "Analizar esta tabla", "en": "Analyze this table",
                           "pt": "Analisar esta tabela"},
    "de_db_o_query": {"es": "…o escribí una consulta (SELECT / WITH)",
                      "en": "…or write a query (SELECT / WITH)",
                      "pt": "…ou escreva uma consulta (SELECT / WITH)"},
    "de_db_query_ph": {"es": "SELECT * FROM ventas WHERE fecha >= '2026-01-01'",
                       "en": "SELECT * FROM sales WHERE date >= '2026-01-01'",
                       "pt": "SELECT * FROM vendas WHERE data >= '2026-01-01'"},
    "de_db_ejecutar_query": {"es": "Analizar el resultado de la consulta",
                             "en": "Analyze the query result",
                             "pt": "Analisar o resultado da consulta"},
    "de_db_limite": {"es": "Límite de filas", "en": "Row limit", "pt": "Limite de linhas"},
    "de_db_sin_tablas": {"es": "La conexión funciona pero no encontramos tablas visibles.",
                         "en": "The connection works but no visible tables were found.",
                         "pt": "A conexão funciona mas não encontramos tabelas visíveis."},
    "de_db_conectar_primero": {"es": "Probá la conexión primero.",
                               "en": "Test the connection first.",
                               "pt": "Teste a conexão primeiro."},
    "de_db_falta_driver": {
        "es": "Este motor necesita un driver que no está instalado en el programa.",
        "en": "This engine needs a driver that isn't installed in the program.",
        "pt": "Este motor precisa de um driver que não está instalado no programa.",
    },

    # --- KPIs y resumen ------------------------------------------------------
    "de_kpi_filas": {"es": "Filas", "en": "Rows", "pt": "Linhas"},
    "de_kpi_columnas": {"es": "Columnas", "en": "Columns", "pt": "Colunas"},
    "de_kpi_score": {"es": "Calidad", "en": "Quality", "pt": "Qualidade"},
    "de_kpi_criticos": {"es": "Problemas críticos", "en": "Critical issues", "pt": "Problemas críticos"},

    "de_dimensiones_titulo": {"es": "Calidad por dimensión", "en": "Quality by dimension",
                              "pt": "Qualidade por dimensão"},
    "dim_completitud": {"es": "Completitud", "en": "Completeness", "pt": "Completude"},
    "dim_unicidad": {"es": "Unicidad", "en": "Uniqueness", "pt": "Unicidade"},
    "dim_consistencia": {"es": "Consistencia", "en": "Consistency", "pt": "Consistência"},
    "dim_validez": {"es": "Validez", "en": "Validity", "pt": "Validade"},
    "dim_utilidad": {"es": "Utilidad", "en": "Usefulness", "pt": "Utilidade"},
    "dim_integridad": {"es": "Integridad", "en": "Integrity", "pt": "Integridade"},

    "de_tipos_titulo": {"es": "Tipos corregidos automáticamente",
                        "en": "Automatically corrected types",
                        "pt": "Tipos corrigidos automaticamente"},
    "de_tipos_col": {"es": "Columna", "en": "Column", "pt": "Coluna"},
    "de_tipos_de": {"es": "Venía como", "en": "Came in as", "pt": "Vinha como"},
    "de_tipos_a": {"es": "Convertido a", "en": "Converted to", "pt": "Convertido para"},
    "tipo_texto": {"es": "texto", "en": "text", "pt": "texto"},
    "tipo_fecha": {"es": "fecha", "en": "date", "pt": "data"},
    "tipo_numerico": {"es": "numérico", "en": "numeric", "pt": "numérico"},
    "tipo_booleano": {"es": "booleano", "en": "boolean", "pt": "booleano"},

    # --- Perfil de columnas ---------------------------------------------------
    "de_perfil_titulo": {"es": "Perfil de columnas", "en": "Column profile", "pt": "Perfil de colunas"},
    "de_perfil_rol": {"es": "Rol", "en": "Role", "pt": "Papel"},
    "de_perfil_nulos": {"es": "Nulos %", "en": "Null %", "pt": "Nulos %"},
    "de_perfil_unicos": {"es": "Únicos", "en": "Unique", "pt": "Únicos"},
    "rol_fecha": {"es": "Fecha", "en": "Date", "pt": "Data"},
    "rol_identificador": {"es": "Identificador", "en": "Identifier", "pt": "Identificador"},
    "rol_clave_foranea": {"es": "Clave foránea", "en": "Foreign key", "pt": "Chave estrangeira"},
    "rol_metrica": {"es": "Métrica", "en": "Metric", "pt": "Métrica"},
    "rol_metrica_monetaria": {"es": "Métrica monetaria", "en": "Monetary metric", "pt": "Métrica monetária"},
    "rol_flag": {"es": "Indicador (0/1)", "en": "Flag (0/1)", "pt": "Indicador (0/1)"},
    "rol_dimension": {"es": "Dimensión", "en": "Dimension", "pt": "Dimensão"},
    "rol_texto_libre": {"es": "Texto libre", "en": "Free text", "pt": "Texto livre"},

    # --- Problemas de calidad (severidad + detalle + acción) -----------------
    "de_issues_titulo": {"es": "Problemas de calidad", "en": "Quality issues", "pt": "Problemas de qualidade"},
    "de_issues_sin": {"es": "Sin problemas críticos detectados.",
                      "en": "No critical issues detected.",
                      "pt": "Nenhum problema crítico detectado."},
    "de_issues_columna": {"es": "Columna", "en": "Column", "pt": "Coluna"},
    "de_issues_severidad": {"es": "Severidad", "en": "Severity", "pt": "Severidade"},
    "de_issues_detalle": {"es": "Detalle", "en": "Detail", "pt": "Detalhe"},
    "de_issues_accion": {"es": "Qué hacer", "en": "What to do", "pt": "O que fazer"},
    "sev_critico": {"es": "CRÍTICO", "en": "CRITICAL", "pt": "CRÍTICO"},
    "sev_alto": {"es": "ALTO", "en": "HIGH", "pt": "ALTO"},
    "sev_medio": {"es": "MEDIO", "en": "MEDIUM", "pt": "MÉDIO"},
    "sev_bajo": {"es": "BAJO", "en": "LOW", "pt": "BAIXO"},

    "qi_duplicados_fila": {"es": "{duplicados} filas duplicadas ({pct}%).",
                           "en": "{duplicados} duplicate rows ({pct}%).",
                           "pt": "{duplicados} linhas duplicadas ({pct}%)."},
    "qi_duplicados_fila_accion": {
        "es": "Definir la clave de negocio y deduplicar con ROW_NUMBER() antes de cargar.",
        "en": "Define the business key and deduplicate with ROW_NUMBER() before loading.",
        "pt": "Definir a chave de negócio e deduplicar com ROW_NUMBER() antes de carregar.",
    },
    "qi_columna_vacia": {"es": "{pct}% de nulos.", "en": "{pct}% null.", "pt": "{pct}% de nulos."},
    "qi_columna_vacia_accion": {
        "es": "Descartarla del modelo o confirmar con el origen si dejó de poblarse.",
        "en": "Drop it from the model or confirm with the source if it stopped being filled.",
        "pt": "Descartar do modelo ou confirmar com a origem se deixou de ser preenchida.",
    },
    "qi_nulos_masivos": {"es": "{pct}% de nulos.", "en": "{pct}% null.", "pt": "{pct}% de nulos."},
    "qi_nulos_masivos_accion": {
        "es": "Imputar con criterio de negocio o tratar \"falta el dato\" como categoría propia.",
        "en": "Impute using business judgment, or treat \"missing\" as its own category.",
        "pt": "Imputar com critério de negócio ou tratar \"falta o dado\" como categoria própria.",
    },
    "qi_nulos": {"es": "{pct}% de nulos.", "en": "{pct}% null.", "pt": "{pct}% de nulos."},
    "qi_nulos_accion": {
        "es": "Documentar el default y agregar un indicador *_faltante.",
        "en": "Document the default and add a *_missing flag.",
        "pt": "Documentar o padrão e adicionar um indicador *_faltante.",
    },
    "qi_constante": {"es": "Un solo valor distinto en toda la columna.",
                     "en": "Only one distinct value in the whole column.",
                     "pt": "Apenas um valor distinto em toda a coluna."},
    "qi_constante_accion": {
        "es": "No aporta información: sacarla del modelo (ocupa espacio y confunde).",
        "en": "Adds no information: drop it from the model (wastes space and confuses).",
        "pt": "Não traz informação: tirar do modelo (ocupa espaço e confunde).",
    },
    "qi_cardinalidad_casi_unica": {"es": "{unicos} valores distintos sobre {filas} filas.",
                                   "en": "{unicos} distinct values over {filas} rows.",
                                   "pt": "{unicos} valores distintos em {filas} linhas."},
    "qi_cardinalidad_casi_unica_accion": {
        "es": "Probable identificador o texto libre: no usar como categoría en un modelo.",
        "en": "Likely an identifier or free text: don't use it as a category in a model.",
        "pt": "Provável identificador ou texto livre: não usar como categoria em um modelo.",
    },
    "qi_montos_negativos": {"es": "{negativos} valores negativos.",
                            "en": "{negativos} negative values.",
                            "pt": "{negativos} valores negativos."},
    "qi_montos_negativos_accion": {
        "es": "Confirmar si son notas de crédito/reversas; si no, es error de origen.",
        "en": "Confirm whether they're credit notes/reversals; if not, it's a source error.",
        "pt": "Confirmar se são notas de crédito/estornos; senão, é erro de origem.",
    },
    "qi_outliers": {"es": "{outliers} fuera de 1,5·IQR ({pct}%).",
                    "en": "{outliers} beyond 1.5·IQR ({pct}%).",
                    "pt": "{outliers} fora de 1,5·IQR ({pct}%)."},
    "qi_outliers_accion": {
        "es": "Winsorizar al p99 para modelos, pero NUNCA borrar filas en el reporte de negocio.",
        "en": "Winsorize at p99 for models, but NEVER drop rows in the business report.",
        "pt": "Winsorizar no p99 para modelos, mas NUNCA apagar linhas no relatório de negócio.",
    },
    "qi_asimetria": {"es": "asimetría = {valor}.", "en": "skewness = {valor}.", "pt": "assimetria = {valor}."},
    "qi_asimetria_accion": {
        "es": "Aplicar log1p si vas a usarla en un modelo lineal.",
        "en": "Apply log1p if you're going to use it in a linear model.",
        "pt": "Aplicar log1p se for usá-la em um modelo linear.",
    },
    "qi_casi_todo_ceros": {"es": "{pct}% en cero.", "en": "{pct}% are zero.", "pt": "{pct}% em zero."},
    "qi_casi_todo_ceros_accion": {
        "es": "Verificar si el cero es \"sin dato\" disfrazado.",
        "en": "Check whether zero is really \"no data\" in disguise.",
        "pt": "Verificar se o zero é \"sem dado\" disfarçado.",
    },
    "qi_nombres_no_aptos_sql": {"es": "{total} columnas con espacios, acentos o símbolos: {lista}.",
                                "en": "{total} columns with spaces, accents or symbols: {lista}.",
                                "pt": "{total} colunas com espaços, acentos ou símbolos: {lista}."},
    "qi_nombres_no_aptos_sql_accion": {
        "es": "Normalizar a snake_case sin acentos antes de escribir en la base.",
        "en": "Normalize to snake_case without accents before writing to the database.",
        "pt": "Normalizar para snake_case sem acentos antes de gravar no banco.",
    },

    # --- Claves y joins --------------------------------------------------------
    "de_claves_titulo": {"es": "Claves detectadas", "en": "Detected keys", "pt": "Chaves detectadas"},
    "de_claves_ninguna": {
        "es": "No se detectó clave primaria. Sin clave no podés deduplicar ni hacer cargas "
              "idempotentes: definila con negocio.",
        "en": "No primary key detected. Without a key you can't deduplicate or do idempotent "
              "loads: define one with the business.",
        "pt": "Nenhuma chave primária detectada. Sem chave você não consegue deduplicar nem "
              "fazer cargas idempotentes: defina-a com o negócio.",
    },
    "de_pk_columna": {"es": "Columna", "en": "Column", "pt": "Coluna"},
    "de_pk_tipo": {"es": "Tipo", "en": "Type", "pt": "Tipo"},
    "de_pk_confianza": {"es": "Confianza", "en": "Confidence", "pt": "Confiança"},
    "pk_simple": {"es": "PK simple", "en": "Simple PK", "pt": "PK simples"},
    "pk_candidata": {"es": "PK candidata", "en": "Candidate PK", "pt": "PK candidata"},
    "pk_compuesta": {"es": "PK compuesta", "en": "Composite PK", "pt": "PK composta"},
    "confianza_alta": {"es": "alta", "en": "high", "pt": "alta"},
    "confianza_media": {"es": "media", "en": "medium", "pt": "média"},

    "de_joins_titulo": {"es": "Relaciones detectadas entre tablas",
                        "en": "Detected relationships between tables",
                        "pt": "Relações detectadas entre tabelas"},
    "de_joins_explicacion": {
        "es": "Detectadas por coincidencia de nombre + solapamiento real de valores. Verificá "
              "la cardinalidad antes de usarlas: un join N:N infla las filas y rompe los totales.",
        "en": "Detected by matching column names + real value overlap. Check the cardinality "
              "before using them: an N:N join inflates rows and breaks totals.",
        "pt": "Detectadas por coincidência de nome + sobreposição real de valores. Verifique a "
              "cardinalidade antes de usá-las: um join N:N infla as linhas e quebra os totais.",
    },
    "de_joins_izquierda": {"es": "Izquierda", "en": "Left", "pt": "Esquerda"},
    "de_joins_derecha": {"es": "Derecha", "en": "Right", "pt": "Direita"},
    "de_joins_columna": {"es": "Columna", "en": "Column", "pt": "Coluna"},
    "de_joins_solape": {"es": "Solape", "en": "Overlap", "pt": "Sobreposição"},
    "de_joins_cardinalidad": {"es": "Cardinalidad", "en": "Cardinality", "pt": "Cardinalidade"},
    "de_joins_riesgo": {"es": "Riesgo", "en": "Risk", "pt": "Risco"},
    "riesgo_alto": {"es": "ALTO — N:N infla filas", "en": "HIGH — N:N inflates rows",
                    "pt": "ALTO — N:N infla linhas"},
    "riesgo_medio": {"es": "MEDIO — validar granularidad", "en": "MEDIUM — validate granularity",
                     "pt": "MÉDIO — validar granularidade"},
    "riesgo_bajo": {"es": "BAJO", "en": "LOW", "pt": "BAIXO"},

    # --- Tiempo ------------------------------------------------------------------
    "de_tiempo_titulo": {"es": "Análisis temporal", "en": "Time analysis", "pt": "Análise temporal"},
    "de_tiempo_desde": {"es": "Desde", "en": "From", "pt": "Desde"},
    "de_tiempo_hasta": {"es": "Hasta", "en": "To", "pt": "Até"},
    "de_tiempo_dias_cubiertos": {"es": "Días con datos", "en": "Days with data", "pt": "Dias com dados"},
    "de_tiempo_dias_faltantes": {"es": "Días faltantes", "en": "Missing days", "pt": "Dias faltantes"},
    "de_tiempo_frescura": {"es": "Frescura (días)", "en": "Freshness (days)", "pt": "Frescor (dias)"},
    "de_tiempo_tendencia": {"es": "Tendencia", "en": "Trend", "pt": "Tendência"},
    "tendencia_creciente": {"es": "creciente", "en": "growing", "pt": "crescente"},
    "tendencia_decreciente": {"es": "decreciente", "en": "declining", "pt": "decrescente"},
    "tendencia_estable": {"es": "estable", "en": "stable", "pt": "estável"},
    "de_tiempo_huecos": {
        "es": "Faltan {dias} días en la serie. Si el proceso corre solo días hábiles es "
              "esperable; si no, hay cargas perdidas.",
        "en": "The series is missing {dias} days. Expected if the process only runs on "
              "business days; otherwise there are missing loads.",
        "pt": "Faltam {dias} dias na série. Esperado se o processo roda só em dias úteis; "
              "senão, há cargas perdidas.",
    },
    "de_tiempo_futuras": {
        "es": "{futuras} fechas en el futuro. Casi siempre es error de carga o de zona horaria.",
        "en": "{futuras} dates in the future. Almost always a load or timezone error.",
        "pt": "{futuras} datas no futuro. Quase sempre é erro de carga ou de fuso horário.",
    },

    # --- Target y fuga (leakage) --------------------------------------------------
    "de_target_titulo": {"es": "Variable objetivo", "en": "Target variable", "pt": "Variável objetivo"},
    "de_target_tasa": {"es": "Tasa de positivos", "en": "Positive rate", "pt": "Taxa de positivos"},
    "de_target_balance": {"es": "Balance", "en": "Balance", "pt": "Balanço"},
    "balance_muy_desbalanceado": {"es": "muy desbalanceado", "en": "very imbalanced", "pt": "muito desbalanceado"},
    "balance_desbalanceado": {"es": "desbalanceado", "en": "imbalanced", "pt": "desbalanceado"},
    "balance_razonable": {"es": "razonable", "en": "reasonable", "pt": "razoável"},

    "de_fuga_titulo": {"es": "Sospecha de fuga de información (leakage)",
                       "en": "Suspected information leakage",
                       "pt": "Suspeita de vazamento de informação"},
    "de_fuga_explicacion": {
        "es": "Estas variables predicen el target demasiado bien, o describen algo posterior "
              "al hecho. Si entrenás con ellas, el modelo va a lucir excelente en test y "
              "fallar en producción.",
        "en": "These variables predict the target too well, or describe something that "
              "happens after the fact. If you train with them, the model will look great "
              "in testing and fail in production.",
        "pt": "Essas variáveis preveem o target bem demais, ou descrevem algo posterior ao "
              "fato. Se você treinar com elas, o modelo vai parecer ótimo no teste e falhar "
              "em produção.",
    },
    "fuga_auc_alto": {"es": "AUC = {auc} — casi perfecta.", "en": "AUC = {auc} — near-perfect.",
                      "pt": "AUC = {auc} — quase perfeita."},
    "fuga_correlacion_alta": {"es": "correlación {corr} con el target.",
                              "en": "{corr} correlation with the target.",
                              "pt": "correlação {corr} com o target."},
    "fuga_mi_alta": {"es": "información mutua {mi} — determina el target.",
                     "en": "mutual information {mi} — determines the target.",
                     "pt": "informação mútua {mi} — determina o target."},
    "fuga_nombre_sospechoso": {
        "es": "el nombre sugiere información posterior al hecho a predecir.",
        "en": "the name suggests information from after the event being predicted.",
        "pt": "o nome sugere informação posterior ao fato a prever.",
    },
    "de_ranking_titulo": {"es": "Variables más asociadas al target",
                          "en": "Variables most associated with the target",
                          "pt": "Variáveis mais associadas ao target"},
    "de_ranking_variable": {"es": "Variable", "en": "Variable", "pt": "Variável"},
    "de_ranking_metrica": {"es": "Métrica", "en": "Metric", "pt": "Métrica"},
    "de_ranking_valor": {"es": "Valor", "en": "Value", "pt": "Valor"},
    "de_ranking_fuerza": {"es": "Fuerza", "en": "Strength", "pt": "Força"},

    # --- Features generadas ---------------------------------------------------------
    "de_features_titulo": {"es": "Features generadas", "en": "Generated features",
                           "pt": "Features geradas"},
    "de_features_feature": {"es": "Feature", "en": "Feature", "pt": "Feature"},
    "de_features_origen": {"es": "Origen", "en": "Source", "pt": "Origem"},
    "de_features_calculo": {"es": "Cálculo", "en": "Calculation", "pt": "Cálculo"},
    "de_features_apto": {"es": "Apta para series temporales", "en": "Safe for time series",
                         "pt": "Apta para séries temporais"},
    "apto_si": {"es": "Sí", "en": "Yes", "pt": "Sim"},
    "apto_cuidado": {"es": "Con cuidado", "en": "With care", "pt": "Com cuidado"},

    "fx_anio": {"es": "Año", "en": "Year", "pt": "Ano"},
    "fx_mes": {"es": "Mes (1-12)", "en": "Month (1-12)", "pt": "Mês (1-12)"},
    "fx_trimestre": {"es": "Trimestre", "en": "Quarter", "pt": "Trimestre"},
    "fx_dia_semana": {"es": "Día de la semana (0 = lunes)", "en": "Day of week (0 = Monday)",
                      "pt": "Dia da semana (0 = segunda)"},
    "fx_es_finde": {"es": "Es sábado o domingo", "en": "Is Saturday or Sunday",
                    "pt": "É sábado ou domingo"},
    "fx_dia_mes": {"es": "Día del mes", "en": "Day of month", "pt": "Dia do mês"},
    "fx_fin_de_mes": {"es": "Es el último día del mes", "en": "Is the last day of the month",
                      "pt": "É o último dia do mês"},
    "fx_mes_seno": {"es": "Codificación cíclica del mes (seno)",
                    "en": "Cyclical month encoding (sine)",
                    "pt": "Codificação cíclica do mês (seno)"},
    "fx_mes_coseno": {"es": "Codificación cíclica del mes (coseno)",
                      "en": "Cyclical month encoding (cosine)",
                      "pt": "Codificação cíclica do mês (cosseno)"},
    "fx_dias_desde_max": {"es": "Días hasta la fecha máxima del dataset",
                          "en": "Days until the dataset's latest date",
                          "pt": "Dias até a data máxima do dataset"},
    "fx_dias_desde_max_cuidado": {
        "es": "recalcular con la fecha de corte real en producción, no con el máximo del dataset.",
        "en": "recompute using the real cutoff date in production, not the dataset's maximum.",
        "pt": "recalcular com a data de corte real em produção, não com o máximo do dataset.",
    },
    "fx_log1p": {"es": "log(1+x), corrige asimetría", "en": "log(1+x), corrects skewness",
                "pt": "log(1+x), corrige assimetria"},
    "fx_flag_faltante": {"es": "1 si el dato falta", "en": "1 if the value is missing",
                         "pt": "1 se o dado falta"},
    "fx_flag_cero": {"es": "1 si vale cero", "en": "1 if it's zero", "pt": "1 se vale zero"},
    "fx_winsorizado": {"es": "Winsorizado entre p1 y p99", "en": "Winsorized between p1 and p99",
                       "pt": "Winsorizado entre p1 e p99"},
    "fx_quintil": {"es": "Quintil (1-5) dentro del dataset", "en": "Quintile (1-5) within the dataset",
                  "pt": "Quintil (1-5) dentro do dataset"},
    "fx_quintil_cuidado": {
        "es": "el corte se calcula con TODO el dataset — recalcularlo solo con train.",
        "en": "the cutoff is computed over the WHOLE dataset — recompute it using train only.",
        "pt": "o corte é calculado com TODO o dataset — recalcular apenas com o train.",
    },
    "fx_ratio": {"es": "Ratio entre dos montos", "en": "Ratio between two amounts",
                "pt": "Razão entre dois valores"},
    "fx_frecuencia_categoria": {"es": "Frecuencia relativa de la categoría",
                                "en": "Relative frequency of the category",
                                "pt": "Frequência relativa da categoria"},
    "fx_frecuencia_categoria_cuidado": {
        "es": "calcular la frecuencia SOLO con los datos de entrenamiento.",
        "en": "compute the frequency using TRAINING data only.",
        "pt": "calcular a frequência SOMENTE com os dados de treinamento.",
    },
    "fx_categoria_rara": {"es": "1 si la categoría tiene menos de 1% de los casos",
                          "en": "1 if the category has under 1% of the cases",
                          "pt": "1 se a categoria tem menos de 1% dos casos"},
    "fx_largo_texto": {"es": "Cantidad de caracteres", "en": "Character count", "pt": "Quantidade de caracteres"},
    "fx_cant_palabras": {"es": "Cantidad de palabras", "en": "Word count", "pt": "Quantidade de palavras"},
    "fx_lag": {"es": "Valor de {periodos} período(s) atrás", "en": "Value from {periodos} period(s) ago",
              "pt": "Valor de {periodos} período(s) atrás"},
    "fx_media_movil": {
        "es": "Media de los últimos {ventana} períodos (con shift, nunca incluye el actual)",
        "en": "Average of the last {ventana} periods (shifted, never includes the current one)",
        "pt": "Média dos últimos {ventana} períodos (com shift, nunca inclui o atual)",
    },
    "fx_variacion_pct": {"es": "Variación % contra el período anterior",
                         "en": "% change vs. the previous period",
                         "pt": "Variação % contra o período anterior"},

    "de_ddl_titulo": {"es": "DDL sugerido", "en": "Suggested DDL", "pt": "DDL sugerido"},

    "de_err_formato": {
        "es": "Formato no soportado. Se aceptan CSV, TSV, Excel, Parquet, JSON, JSONL y SQLite.",
        "en": "Unsupported format. CSV, TSV, Excel, Parquet, JSON, JSONL and SQLite are accepted.",
        "pt": "Formato não suportado. Aceitam-se CSV, TSV, Excel, Parquet, JSON, JSONL e SQLite.",
    },
    "de_err_vacio": {"es": "El archivo está vacío.", "en": "The file is empty.",
                     "pt": "O arquivo está vazio."},
    "de_err_roto": {"es": "No se pudo leer el archivo. ¿Está completo y bien formado?",
                    "en": "The file could not be read. Is it complete and well formed?",
                    "pt": "Não foi possível ler o arquivo. Está completo e bem formado?"},

}


def t(key: str, lang: str = DEFAULT_LANG) -> str:
    """Traduce ``key`` al idioma ``lang`` (cae a español si falta)."""
    entry = _T.get(key)
    if entry is None:
        return key
    return entry.get(lang) or entry[DEFAULT_LANG]


def all_keys() -> list[str]:
    return list(_T.keys())
