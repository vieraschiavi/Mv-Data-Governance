"""
MV Data Governance · Referencia COBIT 2019 + ISO/IEC 38505 (gobierno de datos).

Mismo espíritu que ``dmbok.py``: no es una certificación ni una auditoría
formal — es una guía de autoevaluación honesta de qué tanto cubre esta
plataforma frente a dos marcos de referencia que las empresas grandes (y sus
áreas de compliance) suelen pedir explícitamente, además de DAMA-DMBOK:

  - **COBIT 2019** (ISACA): marco de gobierno y gestión de TI. Se listan acá
    los objetivos de gobierno/gestión más relacionados con datos (no los 40
    objetivos completos de COBIT, que cubren TODO IT, no solo datos).
  - **ISO/IEC 38505** (partes 1 y 2): aplica los 6 principios de gobierno de
    ISO/IEC 38500 específicamente a los DATOS, más el modelo de evaluación
    Valor/Riesgo/Restricción (VRC) para decisiones sobre datos.

Todo trilingüe (es/en/pt), mismo patrón de ``coverage``: covered | partial |
out, con ``score`` 0-100 para los tableros.
"""
from __future__ import annotations


def _tr(es: str, en: str, pt: str) -> dict:
    return {"es": es, "en": en, "pt": pt}


# ---------------------------------------------------------------------------
# 1. COBIT 2019 — objetivos de gobierno/gestión más relacionados con datos.
#    (De los 40 objetivos de COBIT 2019, que cubren toda la gestión de TI,
#    estos 8 son los que tienen relación directa con gobierno de datos.)
# ---------------------------------------------------------------------------
COBIT_OBJECTIVES: list[dict] = [
    {
        "key": "edm01", "code": "EDM01",
        "name": _tr("Garantizar el marco de gobierno", "Ensured Governance Framework Setting",
                    "Garantir a estrutura de governança"),
        "plain": _tr(
            "Que exista un comité/proceso claro de quién decide sobre los datos, no cada área por su cuenta.",
            "Making sure there's a clear committee/process for who decides on data, not each area on its own.",
            "Garantir que exista um comitê/processo claro sobre quem decide sobre os dados."),
        "tech": _tr(
            "Evaluar, dirigir y monitorear el sistema de gobierno de TI/datos de la empresa: estructura, principios, procesos de decisión.",
            "Evaluate, direct and monitor the enterprise's IT/data governance system: structure, principles, decision processes.",
            "Avaliar, dirigir e monitorar o sistema de governança de TI/dados da empresa: estrutura, princípios, processos de decisão."),
        "deliverables": _tr("Política de datos, catálogo de roles, comité de datos.",
                            "Data policy, role catalog, data committee.",
                            "Política de dados, catálogo de papéis, comitê de dados."),
        "coverage": "covered", "score": 80,
        "note": _tr("Módulo de políticas + catálogo de dueños/stewards + comité (speeches de ayuda).",
                    "Policies module + owner/steward catalog + committee (help speeches).",
                    "Módulo de políticas + catálogo de donos/stewards + comitê (speeches de ajuda)."),
    },
    {
        "key": "apo01", "code": "APO01",
        "name": _tr("Gestionar el marco de gestión de TI", "Managed I&T Management Framework",
                    "Gerenciar a estrutura de gestão de TI"),
        "plain": _tr(
            "Un mapa de quién hace qué en TI y datos, con reglas claras.",
            "A map of who does what in IT and data, with clear rules.",
            "Um mapa de quem faz o quê em TI e dados, com regras claras."),
        "tech": _tr(
            "Aclarar y mantener el gobierno de la organización de gestión de TI: estructura organizativa, roles, responsabilidades, procesos de decisión.",
            "Clarify and maintain the governance of the IT management organization: organizational structure, roles, responsibilities, decision processes.",
            "Esclarecer e manter a governança da organização de gestão de TI: estrutura organizacional, papéis, responsabilidades, processos de decisão."),
        "deliverables": _tr("Roles dueño/steward por dataset; no reemplaza el organigrama completo de TI.",
                            "Owner/steward roles per dataset; doesn't replace the full IT org chart.",
                            "Papéis dono/steward por dataset; não substitui o organograma completo de TI."),
        "coverage": "partial", "score": 55,
        "note": _tr("Cubre el gobierno de datos, no toda la gestión de TI (fuera de alcance).",
                    "Covers data governance, not all of IT management (out of scope).",
                    "Cobre a governança de dados, não toda a gestão de TI (fora de escopo)."),
    },
    {
        "key": "apo11", "code": "APO11",
        "name": _tr("Gestionar la calidad", "Managed Quality", "Gerenciar a qualidade"),
        "plain": _tr(
            "Medir si los datos (y los procesos que los producen) cumplen un estándar de calidad, con evidencia.",
            "Measuring whether data (and the processes producing it) meet a quality standard, with evidence.",
            "Medir se os dados (e os processos que os produzem) atendem a um padrão de qualidade, com evidência."),
        "tech": _tr(
            "Definir y comunicar requisitos de calidad en todos los procesos, procedimientos y activos de la empresa, con controles de calidad continuos.",
            "Define and communicate quality requirements across all enterprise processes, procedures and assets, with continuous quality controls.",
            "Definir e comunicar requisitos de qualidade em todos os processos, procedimentos e ativos da empresa, com controles de qualidade contínuos."),
        "deliverables": _tr("Reglas de calidad con umbral, cuadro de mando, incidencias priorizadas.",
                            "Threshold-based quality rules, scorecard, prioritized issues.",
                            "Regras de qualidade com limiar, painel, incidências priorizadas."),
        "coverage": "covered", "score": 95,
        "note": _tr("Motor de calidad: 36+ reglas / 6 dimensiones, con sugerencia de corrección al lado.",
                    "Quality engine: 36+ rules / 6 dimensions, with a fix suggestion next to each.",
                    "Motor de qualidade: 36+ regras / 6 dimensões, com sugestão de correção ao lado."),
    },
    {
        "key": "apo14", "code": "APO14",
        "name": _tr("Gestionar los datos", "Managed Data", "Gerenciar os dados"),
        "plain": _tr(
            "El objetivo de COBIT 2019 dedicado enteramente a datos: que existan, se entiendan y se usen bien.",
            "COBIT 2019's objective dedicated entirely to data: that it exists, is understood and is used well.",
            "O objetivo do COBIT 2019 dedicado inteiramente a dados: que existam, sejam entendidos e bem usados."),
        "tech": _tr(
            "Lograr que los activos de datos de la empresa se gestionen de forma efectiva a lo largo del ciclo de vida: arquitectura, calidad, seguridad, disponibilidad para el negocio.",
            "Ensure the enterprise's data assets are managed effectively across their lifecycle: architecture, quality, security, business availability.",
            "Garantir que os ativos de dados da empresa sejam geridos efetivamente ao longo do ciclo de vida: arquitetura, qualidade, segurança, disponibilidade para o negócio."),
        "deliverables": _tr("Catálogo, diccionario, calidad, linaje, glosario, exportación a BI.",
                            "Catalog, dictionary, quality, lineage, glossary, BI export.",
                            "Catálogo, dicionário, qualidade, linhagem, glossário, exportação para BI."),
        "coverage": "covered", "score": 85,
        "note": _tr("Es, en esencia, lo que hace todo el programa — el objetivo mejor cubierto.",
                    "This is, in essence, what the whole program does — the best-covered objective.",
                    "É, em essência, o que todo o programa faz — o objetivo mais bem coberto."),
    },
    {
        "key": "bai08", "code": "BAI08",
        "name": _tr("Gestionar el conocimiento", "Managed Knowledge", "Gerenciar o conhecimento"),
        "plain": _tr(
            "Que el significado de los datos y las buenas prácticas queden documentados, no en la cabeza de una persona.",
            "Making sure data meaning and good practices are documented, not just in one person's head.",
            "Garantir que o significado dos dados e as boas práticas fiquem documentados, não só na cabeça de uma pessoa."),
        "tech": _tr(
            "Mantener la disponibilidad de conocimiento relevante, actualizado, validado y confiable para dar soporte a todos los procesos.",
            "Maintain the availability of relevant, current, validated and reliable knowledge to support all processes.",
            "Manter a disponibilidade de conhecimento relevante, atualizado, validado e confiável para apoiar todos os processos."),
        "deliverables": _tr("Glosario de negocio, tutorial DAMA-DMBOK, centro de ayuda con speeches.",
                            "Business glossary, DAMA-DMBOK tutorial, help center with speeches.",
                            "Glossário de negócio, tutorial DAMA-DMBOK, central de ajuda com speeches."),
        "coverage": "covered", "score": 75,
        "note": _tr("Glosario + tutorial + centro de ayuda, siempre generados desde el motor, no manuales sueltos.",
                    "Glossary + tutorial + help center, always engine-generated, not loose manual docs.",
                    "Glossário + tutorial + central de ajuda, sempre gerados do motor, não manuais soltos."),
    },
    {
        "key": "dss05", "code": "DSS05",
        "name": _tr("Gestionar los servicios de seguridad", "Managed Security Services",
                    "Gerenciar os serviços de segurança"),
        "plain": _tr(
            "Saber qué columnas tienen datos sensibles, aunque el control de acceso en sí lo maneje TI.",
            "Knowing which columns hold sensitive data, even though access control itself is handled by IT.",
            "Saber quais colunas têm dados sensíveis, mesmo que o controle de acesso seja gerido pela TI."),
        "tech": _tr(
            "Proteger la información de la empresa para mantener un nivel aceptable de riesgo de seguridad, según la política de seguridad.",
            "Protect enterprise information to maintain an acceptable level of security risk, per the security policy.",
            "Proteger as informações da empresa para manter um nível aceitável de risco de segurança, conforme a política de segurança."),
        "deliverables": _tr("Detección heurística de PII, clasificación de datasets.",
                            "Heuristic PII detection, dataset classification.",
                            "Detecção heurística de PII, classificação de datasets."),
        "coverage": "partial", "score": 40,
        "note": _tr("Detecta y clasifica; no aplica cifrado/enmascaramiento ni controles de acceso activos.",
                    "Detects and classifies; doesn't apply encryption/masking or active access controls.",
                    "Detecta e classifica; não aplica criptografia/mascaramento nem controles de acesso ativos."),
    },
    {
        "key": "mea03", "code": "MEA03",
        "name": _tr("Gestionar el cumplimiento normativo", "Managed Compliance With External Requirements",
                    "Gerenciar a conformidade com requisitos externos"),
        "plain": _tr(
            "Poder mostrar evidencia de que las reglas propias se cumplen — no garantiza cumplir leyes externas específicas.",
            "Being able to show evidence that your own rules are being met — doesn't guarantee compliance with specific external laws.",
            "Poder mostrar evidência de que as próprias regras são cumpridas — não garante conformidade com leis externas específicas."),
        "tech": _tr(
            "Evaluar que los procesos de TI cumplan las leyes, regulaciones y requisitos contractuales, con evidencia auditable.",
            "Evaluate that IT processes comply with laws, regulations and contractual requirements, with auditable evidence.",
            "Avaliar se os processos de TI cumprem leis, regulamentos e requisitos contratuais, com evidência auditável."),
        "deliverables": _tr("Políticas verificadas automáticamente contra catálogo y reglas (evidencia, no checkboxes).",
                            "Policies automatically verified against catalog and rules (evidence, not checkboxes).",
                            "Políticas verificadas automaticamente contra catálogo e regras (evidência, não checkboxes)."),
        "coverage": "partial", "score": 45,
        "note": _tr("Verifica políticas propias con evidencia; no mapea a GDPR/LGPD/SOX específicos.",
                    "Verifies your own policies with evidence; doesn't map to specific GDPR/LGPD/SOX.",
                    "Verifica políticas próprias com evidência; não mapeia para GDPR/LGPD/SOX específicos."),
    },
    {
        "key": "mea04", "code": "MEA04",
        "name": _tr("Gestionar el aseguramiento", "Managed Assurance", "Gerenciar a garantia"),
        "plain": _tr(
            "Un chequeo automático de que todo el programa funciona como dice — no una auditoría externa de negocio.",
            "An automatic check that the whole program works as claimed — not an external business audit.",
            "Uma verificação automática de que todo o programa funciona como afirma — não uma auditoria externa de negócio."),
        "tech": _tr(
            "Planificar, definir el alcance y ejecutar iniciativas de aseguramiento, aprovechando resultados para obtener confianza y comunicar a las partes interesadas.",
            "Plan, scope and execute assurance initiatives, leveraging results to gain confidence and communicate to stakeholders.",
            "Planejar, definir escopo e executar iniciativas de garantia, aproveitando resultados para obter confiança e comunicar às partes interessadas."),
        "deliverables": _tr("Auto-diagnóstico (`python -m mvdg.selfcheck`, 24 chequeos automáticos).",
                            "Self-check (`python -m mvdg.selfcheck`, 24 automated checks).",
                            "Autodiagnóstico (`python -m mvdg.selfcheck`, 24 verificações automáticas)."),
        "coverage": "partial", "score": 50,
        "note": _tr("Aseguramiento técnico automático del programa; no reemplaza una auditoría de negocio.",
                    "Automatic technical assurance of the program; doesn't replace a business audit.",
                    "Garantia técnica automática do programa; não substitui uma auditoria de negócio."),
    },
]


# ---------------------------------------------------------------------------
# 2. ISO/IEC 38505 — los 6 principios de gobierno de ISO/IEC 38500,
#    aplicados específicamente a datos (38505-1), + evaluación honesta.
# ---------------------------------------------------------------------------
ISO_PRINCIPLES: list[dict] = [
    {
        "key": "responsibility",
        "name": _tr("Responsabilidad", "Responsibility", "Responsabilidade"),
        "text": _tr(
            "Cada decisión sobre datos tiene un responsable claro (individuo o grupo), con autoridad y recursos para cumplirla.",
            "Every data decision has a clear responsible party (individual or group), with the authority and resources to carry it out.",
            "Cada decisão sobre dados tem um responsável claro (indivíduo ou grupo), com autoridade e recursos para cumpri-la."),
        "coverage": "covered", "score": 85,
        "note": _tr("Catálogo con dueño/steward por dataset — la responsabilidad queda escrita, no implícita.",
                    "Catalog with owner/steward per dataset — responsibility is written down, not implied.",
                    "Catálogo com dono/steward por dataset — a responsabilidade fica escrita, não implícita."),
    },
    {
        "key": "strategy",
        "name": _tr("Estrategia", "Strategy", "Estratégia"),
        "text": _tr(
            "El uso de los datos se planifica alineado a los objetivos actuales y futuros del negocio, no solo a lo técnico.",
            "Data use is planned in alignment with current and future business objectives, not just technical concerns.",
            "O uso dos dados é planejado alinhado aos objetivos atuais e futuros do negócio, não só ao técnico."),
        "coverage": "partial", "score": 50,
        "note": _tr("El Laboratorio conecta calidad con impacto de negocio; no arma un plan estratégico de datos.",
                    "The Lab connects quality to business impact; doesn't produce a strategic data plan.",
                    "O Laboratório conecta qualidade com impacto de negócio; não monta um plano estratégico de dados."),
    },
    {
        "key": "acquisition",
        "name": _tr("Adquisición", "Acquisition", "Aquisição"),
        "text": _tr(
            "Los datos (y los sistemas que los generan) se adquieren o construyen con las condiciones adecuadas de calidad, costo y riesgo.",
            "Data (and the systems that generate it) is acquired or built with the right conditions of quality, cost and risk.",
            "Os dados (e os sistemas que os geram) são adquiridos ou construídos com as condições adequadas de qualidade, custo e risco."),
        "coverage": "partial", "score": 40,
        "note": _tr("Conectores a bases y BI existentes; no evalúa la adquisición de sistemas nuevos.",
                    "Connectors to existing databases and BI; doesn't assess the acquisition of new systems.",
                    "Conectores a bancos e BI existentes; não avalia a aquisição de sistemas novos."),
    },
    {
        "key": "performance",
        "name": _tr("Desempeño", "Performance", "Desempenho"),
        "text": _tr(
            "Los datos cumplen los propósitos para los que existen: disponibles, con la calidad y continuidad que el negocio necesita.",
            "Data fulfills the purposes it exists for: available, with the quality and continuity the business needs.",
            "Os dados cumprem os propósitos para os quais existem: disponíveis, com a qualidade e continuidade que o negócio precisa."),
        "coverage": "covered", "score": 90,
        "note": _tr("Es el núcleo del programa: índice de calidad medido en vivo, con umbral y estado por regla.",
                    "This is the program's core: a live-measured quality index, with threshold and status per rule.",
                    "É o núcleo do programa: índice de qualidade medido ao vivo, com limiar e status por regra."),
    },
    {
        "key": "conformance",
        "name": _tr("Conformidad", "Conformance", "Conformidade"),
        "text": _tr(
            "El uso de los datos cumple leyes, regulaciones y políticas internas — con evidencia verificable, no una declaración.",
            "Data use complies with laws, regulations and internal policies — with verifiable evidence, not a declaration.",
            "O uso dos dados cumpre leis, regulamentos e políticas internas — com evidência verificável, não uma declaração."),
        "coverage": "partial", "score": 55,
        "note": _tr("Políticas propias verificadas con evidencia; el mapeo a leyes específicas lo define la empresa.",
                    "Own policies verified with evidence; mapping to specific laws is defined by the company.",
                    "Políticas próprias verificadas com evidência; o mapeamento para leis específicas é definido pela empresa."),
    },
    {
        "key": "human",
        "name": _tr("Comportamiento humano", "Human Behaviour", "Comportamento humano"),
        "text": _tr(
            "Las políticas y procesos de datos respetan las necesidades humanas actuales y futuras de todos los involucrados.",
            "Data policies and processes respect the current and future human needs of everyone involved.",
            "As políticas e processos de dados respeitam as necessidades humanas atuais e futuras de todos os envolvidos."),
        "coverage": "partial", "score": 45,
        "note": _tr("Speeches de ayuda pensados por audiencia (dirección, TI, dueños); no mide adopción real.",
                    "Help speeches tailored by audience (leadership, IT, owners); doesn't measure real adoption.",
                    "Speeches de ajuda pensados por público (direção, TI, donos); não mede adoção real."),
    },
]

# ---------------------------------------------------------------------------
# 3. Modelo Valor / Riesgo / Restricción (VRC) de ISO/IEC 38505-1 — cómo se
#    evalúa una decisión de datos bajo este estándar.
# ---------------------------------------------------------------------------
ISO_VRC: list[dict] = [
    {"dim": _tr("Valor (Value)", "Value", "Valor"),
     "text": _tr(
         "Qué beneficio genera el dato para el negocio (mejores decisiones, nuevos ingresos, eficiencia).",
         "What benefit the data creates for the business (better decisions, new revenue, efficiency).",
         "Que benefício o dado gera para o negócio (melhores decisões, nova receita, eficiência)."),
     "mapped": _tr("Índice de calidad + catálogo: qué tan confiable y encontrable es cada dataset.",
                   "Quality index + catalog: how trustworthy and findable each dataset is.",
                   "Índice de qualidade + catálogo: quão confiável e localizável é cada dataset.")},
    {"dim": _tr("Riesgo (Risk)", "Risk", "Risco"),
     "text": _tr(
         "Qué puede salir mal si el dato está mal gobernado (decisiones erróneas, multas, filtraciones).",
         "What can go wrong if the data is poorly governed (wrong decisions, fines, leaks).",
         "O que pode dar errado se o dado for mal governado (decisões erradas, multas, vazamentos)."),
     "mapped": _tr("PII detectada + clasificación + reglas en fail: dónde está el riesgo real, medido.",
                   "Detected PII + classification + failing rules: where the real, measured risk is.",
                   "PII detectada + classificação + regras em fail: onde está o risco real, medido.")},
    {"dim": _tr("Restricción (Constraint)", "Constraint", "Restrição"),
     "text": _tr(
         "Qué límites existen (presupuesto, legales, técnicos) para cómo se puede gobernar ese dato.",
         "What limits exist (budget, legal, technical) on how that data can be governed.",
         "Que limites existem (orçamento, legais, técnicos) para como aquele dado pode ser governado."),
     "mapped": _tr("Restricción de TI (Opción A/B en Empresas) y modo offline: se adapta a lo que el cliente puede.",
                   "IT restriction (Option A/B in Companies) and offline mode: adapts to what the client can do.",
                   "Restrição de TI (Opção A/B em Empresas) e modo offline: adapta-se ao que o cliente pode.")},
]

_COVERAGE_SCORE_LABEL = {"covered": 3, "partial": 2, "out": 1}


def _resolve(items: list[dict], lang: str) -> list[dict]:
    out = []
    for it in items:
        row = {}
        for k, v in it.items():
            row[k] = v.get(lang, v.get("es")) if isinstance(v, dict) and "es" in v else v
        out.append(row)
    return out


def cobit_objectives(lang: str = "es") -> list[dict]:
    return _resolve(COBIT_OBJECTIVES, lang)


def iso_principles(lang: str = "es") -> list[dict]:
    return _resolve(ISO_PRINCIPLES, lang)


def iso_vrc(lang: str = "es") -> list[dict]:
    return _resolve(ISO_VRC, lang)


def cobit_coverage_summary() -> dict:
    out = {"covered": 0, "partial": 0, "out": 0}
    for o in COBIT_OBJECTIVES:
        out[o["coverage"]] += 1
    return out


def iso_coverage_summary() -> dict:
    out = {"covered": 0, "partial": 0, "out": 0}
    for p in ISO_PRINCIPLES:
        out[p["coverage"]] += 1
    return out


def cobit_coverage_scores(lang: str = "es") -> list[tuple[str, int]]:
    return [(f"{o['code']} · {o['name'].get(lang, o['name']['es'])}", o["score"])
           for o in COBIT_OBJECTIVES]


def iso_coverage_scores(lang: str = "es") -> list[tuple[str, int]]:
    return [(p["name"].get(lang, p["name"]["es"]), p["score"]) for p in ISO_PRINCIPLES]
