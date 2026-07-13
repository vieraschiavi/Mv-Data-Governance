"""
MV Data Governance · Tutorial DAMA-DMBOK completo (teoría + dashboards).

Contenido estructurado del marco DAMA-DMBOK (Data Management Body of Knowledge,
DAMA International) para el tab "DMBOK" del programa: las 11 áreas de
conocimiento, los principios rectores, un glosario de conceptos clave, los
roles del gobierno de datos, el modelo de madurez y el ciclo de vida del dato
(POSMAD). Todo trilingüe (es/en/pt) y explicado en criollo + técnico, con datos
para renderizar tableros (radar de cobertura, madurez, dimensiones de calidad).

El objetivo es doble: que el usuario entienda el proceso de gobierno de datos y
que la herramienta demuestre, con honestidad, qué parte del estándar cubre.
"""
from __future__ import annotations


def _tr(es: str, en: str, pt: str) -> dict:
    return {"es": es, "en": en, "pt": pt}


# ---------------------------------------------------------------------------
# 1. Las 11 áreas de conocimiento (la "Rueda DAMA"). Gobierno de datos en el
#    centro, coordinando a las otras 10. coverage: covered | partial | out.
#    score = qué tanto la plataforma cubre el área (0-100), para el radar.
# ---------------------------------------------------------------------------
AREAS: list[dict] = [
    {
        "key": "governance", "n": 1,
        "area": _tr("Gobierno de datos", "Data Governance", "Governança de dados"),
        "plain": _tr(
            "El área central: quién decide qué sobre los datos y cómo se ponen de acuerdo.",
            "The central area: who decides what about data and how they agree.",
            "A área central: quem decide o quê sobre os dados e como concordam."),
        "tech": _tr(
            "Ejercicio de autoridad y control (planificación, monitoreo y aplicación) sobre la gestión de los activos de datos. Define roles, políticas, estándares y el comité de datos que ordena a las otras 10 áreas.",
            "Exercise of authority and control (planning, monitoring, enforcement) over the management of data assets. Defines roles, policies, standards and the data committee that orchestrates the other 10 areas.",
            "Exercício de autoridade e controle (planejamento, monitoramento e aplicação) sobre a gestão dos ativos de dados. Define papéis, políticas, padrões e o comitê de dados que organiza as outras 10 áreas."),
        "deliverables": _tr(
            "Política de datos, catálogo de roles (dueños/stewards), acta del comité, glosario aprobado.",
            "Data policy, role catalog (owners/stewards), committee charter, approved glossary.",
            "Política de dados, catálogo de papéis (donos/stewards), ata do comitê, glossário aprovado."),
        "coverage": "covered", "score": 85,
        "note": _tr("Módulo de políticas + comité + speeches para lograr sponsors y dueños.",
                    "Policies module + committee + speeches to win sponsors and owners.",
                    "Módulo de políticas + comitê + speeches para conseguir patrocinadores e donos."),
    },
    {
        "key": "quality", "n": 2,
        "area": _tr("Calidad de datos", "Data Quality", "Qualidade de dados"),
        "plain": _tr(
            "Medir si los datos están completos, correctos y actualizados, con un semáforo simple.",
            "Measuring whether data is complete, correct and up to date, with a simple traffic light.",
            "Medir se os dados estão completos, corretos e atualizados, com um semáforo simples."),
        "tech": _tr(
            "Planificación e implementación de técnicas de control para medir, evaluar y mejorar la aptitud de los datos para el uso. En DAMA, 6 dimensiones: completitud, unicidad, validez, consistencia, actualidad (timeliness) y exactitud.",
            "Planning and implementing control techniques to measure, assess and improve data fitness for use. In DAMA, 6 dimensions: completeness, uniqueness, validity, consistency, timeliness and accuracy.",
            "Planejamento e implementação de técnicas de controle para medir, avaliar e melhorar a aptidão dos dados para uso. No DAMA, 6 dimensões: completude, unicidade, validade, consistência, atualidade e exatidão."),
        "deliverables": _tr(
            "Reglas de calidad, cuadro de mando (índice por dimensión), incidencias priorizadas, SLA de datos.",
            "Quality rules, scorecard (index by dimension), prioritized issues, data SLAs.",
            "Regras de qualidade, painel (índice por dimensão), incidências priorizadas, SLAs de dados."),
        "coverage": "covered", "score": 95,
        "note": _tr("Motor de calidad: 17 reglas / 6 dimensiones, 100% automático.",
                    "Quality engine: 17 rules / 6 dimensions, 100% automatic.",
                    "Motor de qualidade: 17 regras / 6 dimensões, 100% automático."),
    },
    {
        "key": "metadata", "n": 3,
        "area": _tr("Gestión de metadatos", "Metadata Management", "Gestão de metadados"),
        "plain": _tr(
            "Un catálogo de 'qué datos existen, dónde viven y qué significan', en vez de saberlo de memoria.",
            "A catalog of 'what data exists, where it lives and what it means', instead of keeping it in your head.",
            "Um catálogo de 'quais dados existem, onde vivem e o que significam', em vez de saber de cabeça."),
        "tech": _tr(
            "Metadatos de negocio (definiciones, dueños), técnicos (esquemas, tipos) y operacionales (linaje de ejecución, frescura). Catálogo + diccionario de datos.",
            "Business metadata (definitions, owners), technical (schemas, types) and operational (run lineage, freshness). Catalog + data dictionary.",
            "Metadados de negócio (definições, donos), técnicos (esquemas, tipos) e operacionais (linhagem de execução, atualidade). Catálogo + dicionário de dados."),
        "deliverables": _tr(
            "Catálogo de datasets, diccionario de columnas, clasificación (PII), etiquetas de dominio.",
            "Dataset catalog, column dictionary, classification (PII), domain tags.",
            "Catálogo de datasets, dicionário de colunas, classificação (PII), etiquetas de domínio."),
        "coverage": "covered", "score": 90,
        "note": _tr("Catálogo de datasets + diccionario de columnas, generados solos.",
                    "Dataset catalog + column dictionary, auto-generated.",
                    "Catálogo de datasets + dicionário de colunas, gerados sozinhos."),
    },
    {
        "key": "integration", "n": 4,
        "area": _tr("Integración y linaje", "Data Integration & Lineage", "Integração e linhagem"),
        "plain": _tr(
            "Rastrear de dónde vino un dato y a dónde va, y conectar con tus bases y BI.",
            "Trace where data came from and where it goes, and connect to your databases and BI.",
            "Rastrear de onde veio um dado e para onde vai, e conectar com seus bancos e BI."),
        "tech": _tr(
            "Movimiento y consolidación de datos (ETL/ELT, batch, streaming, virtualización) y trazabilidad origen→transformación→destino. Linaje técnico y de negocio.",
            "Data movement and consolidation (ETL/ELT, batch, streaming, virtualization) and source→transformation→target traceability. Technical and business lineage.",
            "Movimento e consolidação de dados (ETL/ELT, batch, streaming, virtualização) e rastreabilidade origem→transformação→destino. Linhagem técnica e de negócio."),
        "deliverables": _tr(
            "Mapa de linaje, conectores a fuentes, tablas exportables, documentación de flujos.",
            "Lineage map, source connectors, exportable tables, flow documentation.",
            "Mapa de linhagem, conectores a fontes, tabelas exportáveis, documentação de fluxos."),
        "coverage": "covered", "score": 80,
        "note": _tr("Mapa de linaje + conectores SQL + exportación multi-formato.",
                    "Lineage map + SQL connectors + multi-format export.",
                    "Mapa de linhagem + conectores SQL + exportação multi-formato."),
    },
    {
        "key": "warehousing", "n": 5,
        "area": _tr("Data warehousing y BI", "Data Warehousing & BI", "Data warehousing e BI"),
        "plain": _tr(
            "Que los tableros (Power BI, Tableau…) usen datos ya medidos y confiables.",
            "Ensuring dashboards (Power BI, Tableau…) use already-measured, trustworthy data.",
            "Que os painéis (Power BI, Tableau…) usem dados já medidos e confiáveis."),
        "tech": _tr(
            "Diseño y operación de almacenes/marts analíticos y entrega de datos para reporting y análisis. Modelado dimensional, capa semántica, publicación a BI.",
            "Design and operation of analytical warehouses/marts and delivery of data for reporting and analysis. Dimensional modeling, semantic layer, BI publishing.",
            "Projeto e operação de armazéns/marts analíticos e entrega de dados para reporting e análise. Modelagem dimensional, camada semântica, publicação para BI."),
        "deliverables": _tr(
            "API REST de gobierno, bundle .xlsx multi-hoja, tablas curadas para BI.",
            "Governance REST API, multi-sheet .xlsx bundle, curated tables for BI.",
            "API REST de governança, pacote .xlsx multi-aba, tabelas curadas para BI."),
        "coverage": "covered", "score": 82,
        "note": _tr("API REST (9 tablas) + bundle .xlsx para cualquier BI.",
                    "REST API (9 tables) + .xlsx bundle for any BI.",
                    "API REST (9 tabelas) + pacote .xlsx para qualquer BI."),
    },
    {
        "key": "masterdata", "n": 6,
        "area": _tr("Datos maestros y de referencia", "Reference & Master Data", "Dados mestres e de referência"),
        "plain": _tr(
            "Que 'cliente activo' o 'producto' signifiquen lo mismo en toda la empresa.",
            "Making 'active customer' or 'product' mean the same thing across the whole company.",
            "Que 'cliente ativo' ou 'produto' signifiquem o mesmo em toda a empresa."),
        "tech": _tr(
            "Gestión de datos maestros (MDM: entidades núcleo como cliente/producto, con un 'golden record' único) y datos de referencia (listas/códigos oficiales). Deduplicación, matching, versionado.",
            "Master data management (MDM: core entities like customer/product, with a single 'golden record') and reference data (official lists/codes). Deduplication, matching, versioning.",
            "Gestão de dados mestres (MDM: entidades núcleo como cliente/produto, com um 'golden record' único) e dados de referência (listas/códigos oficiais). Deduplicação, matching, versionamento."),
        "deliverables": _tr(
            "Glosario de negocio, definiciones oficiales, dominios de valores permitidos.",
            "Business glossary, official definitions, allowed-value domains.",
            "Glossário de negócio, definições oficiais, domínios de valores permitidos."),
        "coverage": "partial", "score": 45,
        "note": _tr("Glosario de definiciones; sin motor de deduplicación/MDM de registros.",
                    "Glossary of definitions; no record deduplication/MDM engine.",
                    "Glossário de definições; sem motor de deduplicação/MDM de registros."),
    },
    {
        "key": "security", "n": 7,
        "area": _tr("Seguridad de datos", "Data Security", "Segurança de dados"),
        "plain": _tr(
            "Saber qué columnas tienen datos personales (nombres, emails, documentos) para protegerlas.",
            "Knowing which columns hold personal data (names, emails, IDs) to protect them.",
            "Saber quais colunas têm dados pessoais (nomes, e-mails, documentos) para protegê-las."),
        "tech": _tr(
            "Definición y aplicación de políticas de acceso, clasificación de sensibilidad, enmascaramiento/cifrado y cumplimiento (GDPR, LGPD, HIPAA). Principio de mínimo privilegio.",
            "Definition and enforcement of access policies, sensitivity classification, masking/encryption and compliance (GDPR, LGPD, HIPAA). Least-privilege principle.",
            "Definição e aplicação de políticas de acesso, classificação de sensibilidade, mascaramento/criptografia e conformidade (GDPR, LGPD, HIPAA). Princípio do menor privilégio."),
        "deliverables": _tr(
            "Clasificación de PII, matriz de accesos (por TI), reglas de enmascaramiento.",
            "PII classification, access matrix (by IT), masking rules.",
            "Classificação de PII, matriz de acessos (por TI), regras de mascaramento."),
        "coverage": "partial", "score": 40,
        "note": _tr("Detección heurística de PII; el control de accesos lo define TI.",
                    "Heuristic PII detection; access control is defined by IT.",
                    "Detecção heurística de PII; o controle de acesso é definido por TI."),
    },
    {
        "key": "architecture", "n": 8,
        "area": _tr("Arquitectura de datos", "Data Architecture", "Arquitetura de dados"),
        "plain": _tr(
            "Un mapa de cómo están organizados los datos de la empresa hoy.",
            "A map of how the company's data is organized today.",
            "Um mapa de como os dados da empresa estão organizados hoje."),
        "tech": _tr(
            "Especificación de la estructura de datos empresarial: modelos de alto nivel, estándares y el plano (blueprint) que alinea los datos con la estrategia. Estado actual (as-is) y objetivo (to-be).",
            "Specification of enterprise data structure: high-level models, standards and the blueprint aligning data with strategy. Current (as-is) and target (to-be) state.",
            "Especificação da estrutura de dados empresarial: modelos de alto nível, padrões e o blueprint que alinha os dados à estratégia. Estado atual (as-is) e alvo (to-be)."),
        "deliverables": _tr(
            "Inventario de dominios, mapa de estado actual (catálogo + linaje).",
            "Domain inventory, current-state map (catalog + lineage).",
            "Inventário de domínios, mapa do estado atual (catálogo + linhagem)."),
        "coverage": "partial", "score": 40,
        "note": _tr("Documenta el estado actual; no diseña el estado objetivo.",
                    "Documents the current state; doesn't design the target state.",
                    "Documenta o estado atual; não desenha o estado alvo."),
    },
    {
        "key": "modeling", "n": 9,
        "area": _tr("Modelado y diseño", "Data Modeling & Design", "Modelagem e desenho"),
        "plain": _tr(
            "Diseñar cómo se estructuran las tablas de un sistema nuevo.",
            "Designing how the tables of a new system are structured.",
            "Desenhar como as tabelas de um sistema novo são estruturadas."),
        "tech": _tr(
            "Descubrir, documentar y diseñar los requisitos de datos: modelos conceptual, lógico y físico (entidad-relación, dimensional). No es lo que hace esta plataforma (perfila esquemas existentes).",
            "Discovering, documenting and designing data requirements: conceptual, logical and physical models (entity-relationship, dimensional). Not what this platform does (it profiles existing schemas).",
            "Descobrir, documentar e desenhar os requisitos de dados: modelos conceitual, lógico e físico (entidade-relacionamento, dimensional). Não é o que esta plataforma faz (perfila esquemas existentes)."),
        "deliverables": _tr(
            "Modelos ER/dimensionales (herramienta externa); acá: perfilado de esquemas existentes.",
            "ER/dimensional models (external tool); here: profiling of existing schemas.",
            "Modelos ER/dimensionais (ferramenta externa); aqui: perfilamento de esquemas existentes."),
        "coverage": "out", "score": 15,
        "note": _tr("Perfila esquemas existentes; no es herramienta de modelado.",
                    "Profiles existing schemas; not a modeling tool.",
                    "Perfila esquemas existentes; não é ferramenta de modelagem."),
    },
    {
        "key": "storage", "n": 10,
        "area": _tr("Almacenamiento y operaciones", "Data Storage & Operations", "Armazenamento e operações"),
        "plain": _tr(
            "Administrar los servidores y bases de datos donde vive la información.",
            "Managing the servers and databases where information lives.",
            "Administrar os servidores e bancos de dados onde a informação vive."),
        "tech": _tr(
            "Diseño, implementación y soporte del almacenamiento: administración de bases (DBA), backups, alta disponibilidad, tuning, retención. Responsabilidad del equipo de infraestructura.",
            "Design, implementation and support of storage: database administration (DBA), backups, high availability, tuning, retention. Infrastructure team's responsibility.",
            "Projeto, implementação e suporte do armazenamento: administração de bancos (DBA), backups, alta disponibilidade, tuning, retenção. Responsabilidade da equipe de infraestrutura."),
        "deliverables": _tr(
            "Backups, políticas de retención, tuning (equipo DBA); acá: conexión de solo lectura.",
            "Backups, retention policies, tuning (DBA team); here: read-only connection.",
            "Backups, políticas de retenção, tuning (equipe DBA); aqui: conexão somente leitura."),
        "coverage": "out", "score": 15,
        "note": _tr("Se conecta en lectura; no administra infraestructura.",
                    "Connects read-only; doesn't manage infrastructure.",
                    "Conecta em leitura; não administra infraestrutura."),
    },
    {
        "key": "documents", "n": 11,
        "area": _tr("Gestión documental y de contenido", "Documents & Content", "Gestão documental e de conteúdo"),
        "plain": _tr(
            "Organizar documentos, PDFs y archivos no estructurados (más allá de tablas).",
            "Organizing documents, PDFs and unstructured files (beyond tables).",
            "Organizar documentos, PDFs e arquivos não estruturados (além de tabelas)."),
        "tech": _tr(
            "Gestión del ciclo de vida de datos no estructurados y contenido (documentos, correos, multimedia): captura, indexación, retención, e-discovery. Fuera del alcance: la plataforma trabaja datos estructurados.",
            "Lifecycle management of unstructured data and content (documents, emails, media): capture, indexing, retention, e-discovery. Out of scope: the platform handles structured data.",
            "Gestão do ciclo de vida de dados não estruturados e conteúdo (documentos, e-mails, mídia): captura, indexação, retenção, e-discovery. Fora de escopo: a plataforma trabalha dados estruturados."),
        "deliverables": _tr(
            "Gestor documental (SharePoint, etc.); acá: no aplica (datos estructurados).",
            "Document manager (SharePoint, etc.); here: not applicable (structured data).",
            "Gestor documental (SharePoint, etc.); aqui: não se aplica (dados estruturados)."),
        "coverage": "out", "score": 10,
        "note": _tr("Trabaja con datos estructurados (tablas), no documentos.",
                    "Works with structured data (tables), not documents.",
                    "Trabalha com dados estruturados (tabelas), não documentos."),
    },
]


# ---------------------------------------------------------------------------
# 2. Principios rectores del gobierno de datos (DAMA).
# ---------------------------------------------------------------------------
PRINCIPLES: list[dict] = [
    {"title": _tr("El dato es un activo", "Data is an asset", "O dado é um ativo"),
     "text": _tr(
         "Los datos tienen valor y un costo; se gestionan con la misma disciplina que el dinero o el personal.",
         "Data has value and cost; it is managed with the same discipline as money or people.",
         "Os dados têm valor e custo; são geridos com a mesma disciplina que dinheiro ou pessoal.")},
    {"title": _tr("Dueño de negocio, no de TI", "Business-owned, not IT-owned", "Dono de negócio, não de TI"),
     "text": _tr(
         "El significado y las reglas del dato los define el negocio; TI provee la plataforma. El gobierno es una responsabilidad compartida.",
         "The meaning and rules of data are defined by the business; IT provides the platform. Governance is a shared responsibility.",
         "O significado e as regras do dado são definidos pelo negócio; TI provê a plataforma. A governança é responsabilidade compartilhada.")},
    {"title": _tr("Basado en evidencia", "Evidence-based", "Baseado em evidência"),
     "text": _tr(
         "Las decisiones sobre datos se toman con métricas (calidad, cobertura, incidencias), no con opiniones.",
         "Data decisions are made with metrics (quality, coverage, issues), not opinions.",
         "As decisões sobre dados são tomadas com métricas (qualidade, cobertura, incidências), não opiniões.")},
    {"title": _tr("Administración (stewardship)", "Stewardship", "Curadoria (stewardship)"),
     "text": _tr(
         "Cada dato crítico tiene un responsable nombrado que cuida su calidad y significado en el tiempo.",
         "Every critical data element has a named steward who cares for its quality and meaning over time.",
         "Cada dado crítico tem um responsável nomeado que cuida da sua qualidade e significado ao longo do tempo.")},
    {"title": _tr("Corregir en el origen", "Fix at the source", "Corrigir na origem"),
     "text": _tr(
         "El error se arregla donde nace (el sistema o proceso que lo genera), no parcheando el reporte final.",
         "An error is fixed where it originates (the system or process that produces it), not by patching the final report.",
         "O erro é corrigido onde nasce (o sistema ou processo que o gera), não remendando o relatório final.")},
    {"title": _tr("Gestión del ciclo de vida", "Lifecycle management", "Gestão do ciclo de vida"),
     "text": _tr(
         "El dato se gobierna desde que se crea hasta que se archiva o borra (POSMAD), no solo cuando se usa.",
         "Data is governed from creation to archival or deletion (POSMAD), not only when used.",
         "O dado é governado desde a criação até o arquivamento ou exclusão (POSMAD), não só quando usado.")},
]


# ---------------------------------------------------------------------------
# 3. Conceptos clave (glosario del estándar). category agrupa en el UI.
# ---------------------------------------------------------------------------
CONCEPTS: list[dict] = [
    {"term": _tr("Dueño del dato (Data Owner)", "Data Owner", "Dono do dado (Data Owner)"),
     "cat": _tr("Roles", "Roles", "Papéis"),
     "def": _tr(
         "Ejecutivo de negocio responsable de un dominio de datos: decide su definición, quién accede y qué se corrige primero. Rinde cuentas (accountable).",
         "Business executive accountable for a data domain: decides its definition, who can access it and what gets fixed first.",
         "Executivo de negócio responsável por um domínio de dados: decide sua definição, quem acessa e o que se corrige primeiro.")},
    {"term": _tr("Steward de datos", "Data Steward", "Steward de dados"),
     "cat": _tr("Roles", "Roles", "Papéis"),
     "def": _tr(
         "Persona operativa que cuida el dato día a día: cura definiciones, atiende incidencias de calidad y mantiene el metadato. Ejecuta (responsible).",
         "Operational person who cares for data day to day: curates definitions, handles quality issues and maintains metadata.",
         "Pessoa operacional que cuida do dado no dia a dia: cura definições, atende incidências de qualidade e mantém o metadado.")},
    {"term": _tr("Custodio (Data Custodian)", "Data Custodian", "Custodiante (Data Custodian)"),
     "cat": _tr("Roles", "Roles", "Papéis"),
     "def": _tr(
         "Rol técnico (TI/DBA) que almacena y protege el dato según las reglas que fijan dueño y steward. No decide el significado.",
         "Technical role (IT/DBA) that stores and protects data per the rules set by owner and steward. Does not decide meaning.",
         "Papel técnico (TI/DBA) que armazena e protege o dado conforme regras do dono e steward. Não decide o significado.")},
    {"term": _tr("Metadato", "Metadata", "Metadado"),
     "cat": _tr("Metadatos", "Metadata", "Metadados"),
     "def": _tr(
         "'Datos sobre los datos'. De negocio (definición, dueño), técnico (tipo, esquema) y operacional (frescura, linaje de ejecución).",
         "'Data about data'. Business (definition, owner), technical (type, schema) and operational (freshness, run lineage).",
         "'Dados sobre os dados'. De negócio (definição, dono), técnico (tipo, esquema) e operacional (atualidade, linhagem de execução).")},
    {"term": _tr("Datos maestros (MDM)", "Master Data (MDM)", "Dados mestres (MDM)"),
     "cat": _tr("Datos", "Data", "Dados"),
     "def": _tr(
         "Entidades núcleo del negocio (cliente, producto, proveedor). El MDM consolida duplicados en un 'golden record' único y confiable.",
         "Core business entities (customer, product, supplier). MDM consolidates duplicates into a single trusted 'golden record'.",
         "Entidades núcleo do negócio (cliente, produto, fornecedor). O MDM consolida duplicados num 'golden record' único e confiável.")},
    {"term": _tr("Datos de referencia", "Reference Data", "Dados de referência"),
     "cat": _tr("Datos", "Data", "Dados"),
     "def": _tr(
         "Listas y códigos oficiales que clasifican otros datos (países ISO, monedas, estados). Cambian poco y deben ser únicos en la empresa.",
         "Official lists and codes that classify other data (ISO countries, currencies, statuses). Change rarely and must be enterprise-unique.",
         "Listas e códigos oficiais que classificam outros dados (países ISO, moedas, status). Mudam pouco e devem ser únicos na empresa.")},
    {"term": _tr("Golden record", "Golden record", "Golden record"),
     "cat": _tr("Datos", "Data", "Dados"),
     "def": _tr(
         "La versión única, completa y correcta de una entidad, obtenida al unificar y limpiar registros de varios sistemas.",
         "The single, complete and correct version of an entity, obtained by unifying and cleaning records from several systems.",
         "A versão única, completa e correta de uma entidade, obtida ao unificar e limpar registros de vários sistemas.")},
    {"term": _tr("Linaje de datos", "Data Lineage", "Linhagem de dados"),
     "cat": _tr("Metadatos", "Metadata", "Metadados"),
     "def": _tr(
         "El recorrido del dato de origen a destino (fuente→transformación→BI). Permite auditar y saber a qué afecta un cambio (análisis de impacto).",
         "The data's path from source to target (source→transformation→BI). Enables auditing and impact analysis of changes.",
         "O caminho do dado da origem ao destino (fonte→transformação→BI). Permite auditar e analisar o impacto de mudanças.")},
    {"term": _tr("Política / estándar / procedimiento", "Policy / standard / procedure", "Política / padrão / procedimento"),
     "cat": _tr("Gobierno", "Governance", "Governança"),
     "def": _tr(
         "Política = qué se exige y por qué; estándar = la regla medible; procedimiento = el paso a paso para cumplirla. Jerarquía del gobierno.",
         "Policy = what is required and why; standard = the measurable rule; procedure = the step-by-step to comply. Governance hierarchy.",
         "Política = o que se exige e por quê; padrão = a regra mensurável; procedimento = o passo a passo para cumprir. Hierarquia da governança.")},
    {"term": _tr("Dato crítico (CDE)", "Critical Data Element (CDE)", "Dado crítico (CDE)"),
     "cat": _tr("Gobierno", "Governance", "Governança"),
     "def": _tr(
         "El dato del que dependen decisiones o cumplimiento (p. ej. ingreso, saldo, PII). Se gobierna primero: no todo el dato es igual de importante.",
         "Data on which decisions or compliance depend (e.g. revenue, balance, PII). Governed first: not all data is equally important.",
         "Dado do qual dependem decisões ou conformidade (ex.: receita, saldo, PII). Governado primeiro: nem todo dado é igualmente importante.")},
    {"term": _tr("PII / datos personales", "PII / personal data", "PII / dados pessoais"),
     "cat": _tr("Seguridad", "Security", "Segurança"),
     "def": _tr(
         "Información que identifica a una persona (nombre, documento, email). Regulada por GDPR/LGPD: exige clasificación, control de acceso y a veces enmascaramiento.",
         "Information that identifies a person (name, ID, email). Regulated by GDPR/LGPD: requires classification, access control and sometimes masking.",
         "Informação que identifica uma pessoa (nome, documento, e-mail). Regulada por GDPR/LGPD: exige classificação, controle de acesso e às vezes mascaramento.")},
    {"term": _tr("Las 6 dimensiones de calidad", "The 6 quality dimensions", "As 6 dimensões de qualidade"),
     "cat": _tr("Calidad", "Quality", "Qualidade"),
     "def": _tr(
         "Completitud (sin vacíos), unicidad (sin duplicados), validez (formato correcto), consistencia (coherente entre sistemas), actualidad (a tiempo) y exactitud (refleja la realidad).",
         "Completeness (no gaps), uniqueness (no duplicates), validity (correct format), consistency (coherent across systems), timeliness (on time) and accuracy (reflects reality).",
         "Completude (sem vazios), unicidade (sem duplicados), validade (formato correto), consistência (coerente entre sistemas), atualidade (no prazo) e exatidão (reflete a realidade).")},
    {"term": _tr("Ciclo de vida (POSMAD)", "Lifecycle (POSMAD)", "Ciclo de vida (POSMAD)"),
     "cat": _tr("Gobierno", "Governance", "Governança"),
     "def": _tr(
         "Las fases del dato: Planificar, Obtener, Almacenar, Mantener, Aplicar y Disponer (Plan, Obtain, Store, Maintain, Apply, Dispose).",
         "The data phases: Plan, Obtain, Store, Maintain, Apply and Dispose.",
         "As fases do dado: Planejar, Obter, Armazenar, Manter, Aplicar e Descartar.")},
    {"term": _tr("Catálogo de datos", "Data Catalog", "Catálogo de dados"),
     "cat": _tr("Metadatos", "Metadata", "Metadados"),
     "def": _tr(
         "Inventario buscable de los datos de la empresa con su significado, dueño, calidad y ubicación. La 'góndola' donde el negocio encuentra datos confiables.",
         "Searchable inventory of the company's data with meaning, owner, quality and location. The 'shelf' where the business finds trustworthy data.",
         "Inventário pesquisável dos dados da empresa com significado, dono, qualidade e localização. A 'prateleira' onde o negócio encontra dados confiáveis.")},
]


# ---------------------------------------------------------------------------
# 4. Modelo de madurez del gobierno de datos (basado en CMMI/DAMA, 5 niveles).
# ---------------------------------------------------------------------------
MATURITY: list[dict] = [
    {"level": 1, "name": _tr("Inicial", "Initial", "Inicial"),
     "desc": _tr("Sin proceso: cada área con su planilla, definiciones en conflicto, calidad no medida.",
                 "No process: each area with its spreadsheet, conflicting definitions, quality unmeasured.",
                 "Sem processo: cada área com sua planilha, definições em conflito, qualidade não medida.")},
    {"level": 2, "name": _tr("Repetible", "Repeatable", "Repetível"),
     "desc": _tr("Algunas prácticas se repiten por personas clave, pero sin estándar ni herramienta común.",
                 "Some practices repeat via key people, but with no standard or common tool.",
                 "Algumas práticas se repetem por pessoas-chave, mas sem padrão ou ferramenta comum.")},
    {"level": 3, "name": _tr("Definido", "Defined", "Definido"),
     "desc": _tr("Roles, políticas y catálogo formalizados; la calidad se mide y hay un comité que decide.",
                 "Roles, policies and catalog formalized; quality is measured and a committee decides.",
                 "Papéis, políticas e catálogo formalizados; a qualidade é medida e há um comitê que decide.")},
    {"level": 4, "name": _tr("Gestionado", "Managed", "Gerenciado"),
     "desc": _tr("Métricas y SLAs de datos; la calidad se monitorea con umbrales y alertas; mejora continua.",
                 "Data metrics and SLAs; quality monitored with thresholds and alerts; continuous improvement.",
                 "Métricas e SLAs de dados; qualidade monitorada com limiares e alertas; melhoria contínua.")},
    {"level": 5, "name": _tr("Optimizado", "Optimized", "Otimizado"),
     "desc": _tr("El gobierno es parte de la cultura; los datos son un activo estratégico y auto-servido con confianza.",
                 "Governance is part of the culture; data is a strategic, self-served, trusted asset.",
                 "A governança faz parte da cultura; os dados são um ativo estratégico, autosserviço e confiável.")},
]


# ---------------------------------------------------------------------------
# 5. Ciclo de vida del dato (POSMAD).
# ---------------------------------------------------------------------------
LIFECYCLE: list[dict] = [
    {"phase": _tr("Planificar", "Plan", "Planejar"),
     "desc": _tr("Definir qué dato se necesita, su significado y sus reglas antes de crearlo.",
                 "Define what data is needed, its meaning and rules before creating it.",
                 "Definir qual dado é necessário, seu significado e regras antes de criá-lo.")},
    {"phase": _tr("Obtener", "Obtain", "Obter"),
     "desc": _tr("Capturar o adquirir el dato con validación en el origen (formularios, integraciones).",
                 "Capture or acquire data with validation at the source (forms, integrations).",
                 "Capturar ou adquirir o dado com validação na origem (formulários, integrações).")},
    {"phase": _tr("Almacenar", "Store", "Armazenar"),
     "desc": _tr("Guardarlo de forma segura y accesible (bases, warehouse), con clasificación.",
                 "Store it securely and accessibly (databases, warehouse), with classification.",
                 "Guardá-lo de forma segura e acessível (bancos, warehouse), com classificação.")},
    {"phase": _tr("Mantener", "Maintain", "Manter"),
     "desc": _tr("Actualizar, deduplicar y corregir en el origen; mantener metadato y calidad.",
                 "Update, deduplicate and fix at the source; maintain metadata and quality.",
                 "Atualizar, deduplicar e corrigir na origem; manter metadado e qualidade.")},
    {"phase": _tr("Aplicar", "Apply", "Aplicar"),
     "desc": _tr("Usar el dato en reportes, BI, IA y decisiones — el momento donde genera valor.",
                 "Use data in reports, BI, AI and decisions — where it creates value.",
                 "Usar o dado em relatórios, BI, IA e decisões — onde gera valor.")},
    {"phase": _tr("Disponer", "Dispose", "Descartar"),
     "desc": _tr("Archivar o borrar según retención legal cuando ya no se necesita (LGPD/GDPR).",
                 "Archive or delete per legal retention when no longer needed (LGPD/GDPR).",
                 "Arquivar ou excluir conforme retenção legal quando não for mais necessário (LGPD/GDPR).")},
]

_COVERAGE_SCORE_LABEL = {"covered": 3, "partial": 2, "out": 1}


def _resolve(items: list[dict], lang: str, keys: tuple[str, ...]) -> list[dict]:
    out = []
    for it in items:
        row = {}
        for k, v in it.items():
            row[k] = v.get(lang, v.get("es")) if isinstance(v, dict) and "es" in v else v
        out.append(row)
    return out


def areas(lang: str = "es") -> list[dict]:
    return _resolve(AREAS, lang, ())


def principles(lang: str = "es") -> list[dict]:
    return _resolve(PRINCIPLES, lang, ())


def concepts(lang: str = "es") -> list[dict]:
    return _resolve(CONCEPTS, lang, ())


def roles(lang: str = "es") -> list[dict]:
    """Los conceptos de la categoría Roles, para la tabla de roles."""
    cat_roles = {"es": "Roles", "en": "Roles", "pt": "Papéis"}[lang if lang in ("es", "en", "pt") else "es"]
    return [c for c in concepts(lang) if c["cat"] == cat_roles]


def maturity(lang: str = "es") -> list[dict]:
    return _resolve(MATURITY, lang, ())


def lifecycle(lang: str = "es") -> list[dict]:
    return _resolve(LIFECYCLE, lang, ())


def coverage_summary() -> dict:
    """Cuenta de áreas por nivel de cobertura, para KPIs."""
    out = {"covered": 0, "partial": 0, "out": 0}
    for a in AREAS:
        out[a["coverage"]] += 1
    return out


def coverage_scores(lang: str = "es") -> list[tuple[str, int]]:
    """(nombre de área, score 0-100) para el radar de cobertura."""
    return [(a["area"].get(lang, a["area"]["es"]), a["score"]) for a in AREAS]
