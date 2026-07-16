"""
MV Data Governance · Centro de ayuda: qué se automatiza y qué no,
y speeches de IA para lograr la parte no automatizable.

El gobierno de datos tiene dos mitades. La técnica (medir calidad, perfilar,
exportar, alertar) la automatiza esta plataforma. La organizacional (que un
gerente acepte ser dueño de un dato, que el negocio acuerde una definición,
que TI corrija en origen) NO es automatizable por ningún software — se logra
hablando con personas. Para cerrar ese círculo, este módulo trae guiones
("speeches") listos para usar en cada conversación, en los tres idiomas.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Matriz de automatización: qué hace la plataforma sola, qué es parcial y qué
# requiere personas. level: "auto" | "partial" | "human". Cuando es parcial o
# humano, speech_id apunta al guion que resuelve esa parte.
# ---------------------------------------------------------------------------
AUTOMATION: list[dict] = [
    {
        "area": {"es": "Perfilado y medición de calidad (6 dimensiones)",
                 "en": "Profiling and quality measurement (6 dimensions)",
                 "pt": "Perfilamento e medição de qualidade (6 dimensões)"},
        "level": "auto",
        "detail": {"es": "Las 17 reglas corren solas contra los datos: nulos, duplicados, formatos, FKs, frescura. Sin intervención humana.",
                   "en": "All 17 rules run on their own against the data: nulls, duplicates, formats, FKs, freshness. No human intervention.",
                   "pt": "As 17 regras rodam sozinhas contra os dados: nulos, duplicados, formatos, FKs, atualidade. Sem intervenção humana."},
        "speech_id": None,
    },
    {
        "area": {"es": "Exportación a BI y API REST",
                 "en": "BI export and REST API",
                 "pt": "Exportação para BI e API REST"},
        "level": "auto",
        "detail": {"es": "CSV/Excel/JSON/Parquet y 9 tablas por API para Power BI, Tableau, Looker, MicroStrategy, Qlik, Excel. 100% automático.",
                   "en": "CSV/Excel/JSON/Parquet plus 9 API tables for Power BI, Tableau, Looker, MicroStrategy, Qlik, Excel. 100% automatic.",
                   "pt": "CSV/Excel/JSON/Parquet e 9 tabelas via API para Power BI, Tableau, Looker, MicroStrategy, Qlik, Excel. 100% automático."},
        "speech_id": None,
    },
    {
        "area": {"es": "Detección de PII y esquema técnico",
                 "en": "PII detection and technical schema",
                 "pt": "Detecção de PII e esquema técnico"},
        "level": "partial",
        "detail": {"es": "La plataforma detecta PII y tipos por heurística; una persona debe CONFIRMAR la clasificación y decidir el enmascaramiento.",
                   "en": "The platform detects PII and types heuristically; a person must CONFIRM the classification and decide on masking.",
                   "pt": "A plataforma detecta PII e tipos por heurística; uma pessoa deve CONFIRMAR a classificação e decidir o mascaramento."},
        "speech_id": "ti",
    },
    {
        "area": {"es": "Linaje de datos",
                 "en": "Data lineage",
                 "pt": "Linhagem de dados"},
        "level": "partial",
        "detail": {"es": "El linaje técnico (tablas, pipelines) se releva de los sistemas; los procesos manuales (planillas, correos) hay que declararlos con la gente que los opera.",
                   "en": "Technical lineage (tables, pipelines) is harvested from systems; manual processes (spreadsheets, emails) must be declared with the people who run them.",
                   "pt": "A linhagem técnica (tabelas, pipelines) é coletada dos sistemas; processos manuais (planilhas, e-mails) precisam ser declarados com quem os opera."},
        "speech_id": "ti",
    },
    {
        "area": {"es": "Asignación de dueños y stewards",
                 "en": "Assigning owners and stewards",
                 "pt": "Atribuição de donos e stewards"},
        "level": "human",
        "detail": {"es": "Ningún software puede obligar a un gerente a hacerse responsable de un dato: es una decisión organizacional. Se logra con la conversación correcta.",
                   "en": "No software can make a manager take responsibility for data: it is an organizational decision. It is achieved with the right conversation.",
                   "pt": "Nenhum software pode obrigar um gerente a se responsabilizar por um dado: é uma decisão organizacional. Consegue-se com a conversa certa."},
        "speech_id": "duenos",
    },
    {
        "area": {"es": "Definiciones oficiales del glosario",
                 "en": "Official glossary definitions",
                 "pt": "Definições oficiais do glossário"},
        "level": "human",
        "detail": {"es": "Qué es un 'cliente activo' o un 'ingreso' lo acuerda el negocio, no un algoritmo. La plataforma registra y publica el acuerdo.",
                   "en": "What an 'active customer' or 'revenue' means is agreed by the business, not by an algorithm. The platform records and publishes the agreement.",
                   "pt": "O que é um 'cliente ativo' ou uma 'receita' é acordado pelo negócio, não por um algoritmo. A plataforma registra e publica o acordo."},
        "speech_id": "comite",
    },
    {
        "area": {"es": "Corrección de datos en origen",
                 "en": "Fixing data at the source",
                 "pt": "Correção de dados na origem"},
        "level": "human",
        "detail": {"es": "La plataforma detecta el error y a quién asignarlo; arreglar el sistema o el proceso que lo genera lo hace el equipo dueño de ese origen.",
                   "en": "The platform detects the error and who to assign it to; fixing the system or process that produces it is done by the team owning that source.",
                   "pt": "A plataforma detecta o erro e a quem atribuí-lo; corrigir o sistema ou processo que o gera é feito pela equipe dona daquela origem."},
        "speech_id": "origen",
    },
    {
        "area": {"es": "Patrocinio y adopción cultural",
                 "en": "Sponsorship and cultural adoption",
                 "pt": "Patrocínio e adoção cultural"},
        "level": "human",
        "detail": {"es": "Sin un sponsor de dirección y un comité que se reúna, el gobierno muere en un Excel. Eso se consigue vendiendo el valor, no instalando software.",
                   "en": "Without an executive sponsor and a committee that actually meets, governance dies in a spreadsheet. That is won by selling the value, not installing software.",
                   "pt": "Sem um patrocinador executivo e um comitê que se reúna, a governança morre numa planilha. Isso se conquista vendendo o valor, não instalando software."},
        "speech_id": "direccion",
    },
]

# ---------------------------------------------------------------------------
# Speeches IA: guiones listos para copiar/decir, uno por conversación crítica.
# Cierran el círculo: todo lo que la plataforma no puede automatizar tiene un
# guion que explica cómo lograrlo con personas.
# ---------------------------------------------------------------------------
SPEECHES: list[dict] = [
    {
        "speech_id": "direccion",
        "title": {"es": "Speech para la dirección (conseguir sponsor)",
                  "en": "Speech for executives (winning a sponsor)",
                  "pt": "Speech para a diretoria (conseguir patrocinador)"},
        "audience": {"es": "Gerencia general / directorio",
                     "en": "C-level / board",
                     "pt": "Diretoria / conselho"},
        "text": {
            "es": "«Hoy cada área tiene su propio número para la misma pregunta: ventas dice una cosa, finanzas otra, y cada reunión empieza discutiendo cuál planilla es la buena. Eso tiene un costo: decisiones lentas y errores caros.\n\n"
                  "Les propongo cerrar ese problema con gobierno de datos. La parte técnica ya está resuelta y automatizada: esta plataforma mide la calidad en 6 dimensiones, mantiene el catálogo y alimenta directamente el Power BI/Tableau que ya usamos.\n\n"
                  "Lo único que necesito de ustedes son dos cosas: un sponsor de esta mesa que respalde la iniciativa, y 30 minutos por mes para el comité de datos. Con eso, en 90 días tienen un tablero con UNA versión de la verdad y un semáforo de calidad que muestra exactamente dónde se pierde plata por datos malos.»",
            "en": "“Today every department has its own number for the same question: sales says one thing, finance another, and every meeting starts by arguing over which spreadsheet is right. That has a cost: slow decisions and expensive mistakes.\n\n"
                  "I propose we close that gap with data governance. The technical half is already solved and automated: this platform measures quality across 6 dimensions, keeps the catalog and feeds the Power BI/Tableau we already use.\n\n"
                  "I only need two things from this table: a sponsor to back the initiative, and 30 minutes a month for the data committee. With that, in 90 days you get a dashboard with ONE version of the truth and a quality traffic light showing exactly where bad data is costing us money.”",
            "pt": "“Hoje cada área tem seu próprio número para a mesma pergunta: vendas diz uma coisa, finanças outra, e toda reunião começa discutindo qual planilha é a certa. Isso tem um custo: decisões lentas e erros caros.\n\n"
                  "Proponho fechar esse problema com governança de dados. A parte técnica já está resolvida e automatizada: esta plataforma mede a qualidade em 6 dimensões, mantém o catálogo e alimenta diretamente o Power BI/Tableau que já usamos.\n\n"
                  "Só preciso de duas coisas desta mesa: um patrocinador que respalde a iniciativa e 30 minutos por mês para o comitê de dados. Com isso, em 90 dias vocês têm um painel com UMA versão da verdade e um semáforo de qualidade mostrando exatamente onde dados ruins custam dinheiro.”",
        },
    },
    {
        "speech_id": "duenos",
        "title": {"es": "Speech para dueños de datos (aceptar la responsabilidad)",
                  "en": "Speech for data owners (accepting ownership)",
                  "pt": "Speech para donos de dados (aceitar a responsabilidade)"},
        "audience": {"es": "Gerentes de área (comercial, finanzas, operaciones)",
                     "en": "Department managers (sales, finance, operations)",
                     "pt": "Gerentes de área (comercial, finanças, operações)"},
        "text": {
            "es": "«No vengo a darte más trabajo: vengo a darte control sobre un dato que ya es tuyo. Los reportes de clientes salen de TU operación, y cuando están mal, la que queda mal en el directorio es tu área.\n\n"
                  "Ser dueño del dato significa tres cosas concretas, y ninguna es técnica: decidir qué significa el dato (la definición oficial), decidir quién puede verlo, y priorizar qué error se corrige primero. El trabajo técnico —medir, detectar, avisar— lo hace la plataforma sola: te llega una alerta con el problema ya identificado y las filas exactas afectadas.\n\n"
                  "Son 15 minutos por semana. A cambio, tus números dejan de discutirse en las reuniones: se discuten las decisiones.»",
            "en": "“I'm not here to give you more work: I'm here to give you control over data that is already yours. Customer reports come out of YOUR operation, and when they're wrong, it's your department that looks bad in the boardroom.\n\n"
                  "Owning the data means three concrete things, none of them technical: deciding what the data means (the official definition), deciding who can see it, and prioritizing which error gets fixed first. The technical work — measuring, detecting, alerting — the platform does on its own: you get an alert with the problem already identified and the exact rows affected.\n\n"
                  "It's 15 minutes a week. In exchange, your numbers stop being argued about in meetings — the decisions do.”",
            "pt": "“Não vim te dar mais trabalho: vim te dar controle sobre um dado que já é seu. Os relatórios de clientes saem da SUA operação, e quando estão errados, é a sua área que fica mal na diretoria.\n\n"
                  "Ser dono do dado significa três coisas concretas, nenhuma técnica: decidir o que o dado significa (a definição oficial), decidir quem pode vê-lo e priorizar qual erro se corrige primeiro. O trabalho técnico — medir, detectar, avisar — a plataforma faz sozinha: chega um alerta com o problema já identificado e as linhas exatas afetadas.\n\n"
                  "São 15 minutos por semana. Em troca, seus números deixam de ser discutidos nas reuniões — discutem-se as decisões.”",
        },
    },
    {
        "speech_id": "ti",
        "title": {"es": "Speech para TI (accesos, PII y despliegue)",
                  "en": "Speech for IT (access, PII and deployment)",
                  "pt": "Speech para TI (acessos, PII e implantação)"},
        "audience": {"es": "Gerencia de TI / seguridad informática",
                     "en": "IT management / information security",
                     "pt": "Gerência de TI / segurança da informação"},
        "text": {
            "es": "«Tres puntos y me voy: despliegue, datos personales y linaje.\n\n"
                  "Despliegue: la plataforma se adapta a tu política, no al revés. Si permiten instalar software, va el instalador .exe firmado (Opción A). Si no permiten .exe pero hay Python, va la versión portable .bat que corre en la carpeta del usuario sin tocar el sistema (Opción B). Si no permiten nada local, corre 100% web en un servidor de ustedes. Nada sale a internet: todo es local.\n\n"
                  "PII: la plataforma ya detectó qué columnas parecen datos personales. Necesito 30 minutos con ustedes para confirmar esa clasificación y definir el enmascaramiento, porque esa decisión es de seguridad, no de un algoritmo.\n\n"
                  "Linaje: los pipelines los leemos de los sistemas; solo necesito que me digan qué procesos manuales existen (planillas, cargas a mano) para declararlos y que el mapa quede completo.»",
            "en": "“Three points and I'm gone: deployment, personal data and lineage.\n\n"
                  "Deployment: the platform adapts to your policy, not the other way around. If installing software is allowed, we use the signed .exe installer (Option A). If .exe is blocked but Python is available, we use the portable .bat version that runs in the user's folder without touching the system (Option B). If nothing local is allowed, it runs 100% web on your own server. Nothing goes to the internet: everything is local.\n\n"
                  "PII: the platform has already detected which columns look like personal data. I need 30 minutes with you to confirm that classification and define masking, because that decision belongs to security, not to an algorithm.\n\n"
                  "Lineage: pipelines we read from the systems; I just need you to tell me which manual processes exist (spreadsheets, manual loads) so we can declare them and complete the map.”",
            "pt": "“Três pontos e vou embora: implantação, dados pessoais e linhagem.\n\n"
                  "Implantação: a plataforma se adapta à sua política, não o contrário. Se instalar software é permitido, vai o instalador .exe assinado (Opção A). Se .exe é bloqueado mas há Python, vai a versão portátil .bat que roda na pasta do usuário sem tocar no sistema (Opção B). Se nada local é permitido, roda 100% web num servidor de vocês. Nada sai para a internet: tudo é local.\n\n"
                  "PII: a plataforma já detectou quais colunas parecem dados pessoais. Preciso de 30 minutos com vocês para confirmar essa classificação e definir o mascaramento, porque essa decisão é de segurança, não de um algoritmo.\n\n"
                  "Linhagem: os pipelines lemos dos sistemas; só preciso que me digam quais processos manuais existem (planilhas, cargas manuais) para declará-los e completar o mapa.”",
        },
    },
    {
        "speech_id": "comite",
        "title": {"es": "Speech para el comité de datos (acordar definiciones)",
                  "en": "Speech for the data committee (agreeing on definitions)",
                  "pt": "Speech para o comitê de dados (acordar definições)"},
        "audience": {"es": "Comité de gobierno de datos (negocio + TI)",
                     "en": "Data governance committee (business + IT)",
                     "pt": "Comitê de governança de dados (negócio + TI)"},
        "text": {
            "es": "«La regla de esta mesa es una sola: de acá sale UNA definición por término, con un dueño y una fecha.\n\n"
                  "Hoy 'cliente activo' significa tres cosas distintas en tres reportes distintos. No hay definición correcta o incorrecta: hay una definición ACORDADA o un problema eterno. Ustedes son las únicas personas de la empresa que pueden tomar este acuerdo — ningún software puede hacerlo.\n\n"
                  "El mecanismo: propongo una definición borrador, la discutimos 10 minutos máximo, el dueño del término decide, y queda publicada en el glosario en los tres idiomas. Desde ese momento, todos los tableros de BI usan esa definición, y quien necesite cambiarla viene a este comité.\n\n"
                  "Hoy traigo cinco términos. En cinco reuniones cerramos el glosario core de la empresa.»",
            "en": "“This table has a single rule: ONE definition per term leaves this room, with an owner and a date.\n\n"
                  "Today 'active customer' means three different things in three different reports. There is no right or wrong definition: there is an AGREED definition or an eternal problem. You are the only people in the company who can make this agreement — no software can.\n\n"
                  "The mechanism: I bring a draft definition, we discuss it for 10 minutes max, the term's owner decides, and it gets published in the glossary in all three languages. From that moment on, every BI dashboard uses that definition, and whoever needs to change it comes to this committee.\n\n"
                  "Today I bring five terms. In five meetings we close the company's core glossary.”",
            "pt": "“Esta mesa tem uma única regra: daqui sai UMA definição por termo, com um dono e uma data.\n\n"
                  "Hoje 'cliente ativo' significa três coisas diferentes em três relatórios diferentes. Não existe definição certa ou errada: existe definição ACORDADA ou problema eterno. Vocês são as únicas pessoas da empresa que podem fazer esse acordo — nenhum software pode.\n\n"
                  "O mecanismo: trago uma definição rascunho, discutimos por 10 minutos no máximo, o dono do termo decide, e ela é publicada no glossário nos três idiomas. A partir daí, todos os painéis de BI usam essa definição, e quem precisar mudá-la vem a este comitê.\n\n"
                  "Hoje trago cinco termos. Em cinco reuniões fechamos o glossário core da empresa.”",
        },
    },
    {
        "speech_id": "origen",
        "title": {"es": "Speech para corregir datos en origen",
                  "en": "Speech for fixing data at the source",
                  "pt": "Speech para corrigir dados na origem"},
        "audience": {"es": "Equipo que opera el sistema origen (CRM, ERP, POS)",
                     "en": "Team operating the source system (CRM, ERP, POS)",
                     "pt": "Equipe que opera o sistema de origem (CRM, ERP, POS)"},
        "text": {
            "es": "«No vengo a auditarlos: vengo a que dejen de cargar lo mismo dos veces.\n\n"
                  "La plataforma detectó que el 4% de los emails de clientes entra vacío o mal escrito. Eso no es un problema de ustedes: es un problema del formulario, que lo permite. Cada email malo después significa una llamada que no sale, un reclamo que no llega, y alguien de ustedes re-trabajando la ficha.\n\n"
                  "Propongo arreglarlo donde nace: validación en el campo del formulario (media hora de un desarrollador) y una lista desplegable donde hoy hay texto libre. La plataforma va a seguir midiendo; si la regla de emails pasa de 96 a 100, el mérito es de este equipo y así lo va a mostrar el tablero.\n\n"
                  "¿Qué necesitan de mí para hacerlo esta semana?»",
            "en": "“I'm not here to audit you: I'm here so you stop entering the same thing twice.\n\n"
                  "The platform detected that 4% of customer emails come in empty or misspelled. That's not your problem: it's the form's problem, because it allows it. Every bad email later means a call that doesn't go out, a claim that never arrives, and someone on your team reworking the record.\n\n"
                  "I propose fixing it where it's born: validation on the form field (half an hour of developer time) and a dropdown where today there's free text. The platform will keep measuring; if the email rule goes from 96 to 100, the credit belongs to this team and the dashboard will show it.\n\n"
                  "What do you need from me to do it this week?”",
            "pt": "“Não vim auditar vocês: vim para que parem de digitar a mesma coisa duas vezes.\n\n"
                  "A plataforma detectou que 4% dos e-mails de clientes entram vazios ou errados. Isso não é problema de vocês: é problema do formulário, que permite. Cada e-mail ruim depois vira uma ligação que não sai, uma cobrança que não chega, e alguém de vocês retrabalhando o cadastro.\n\n"
                  "Proponho corrigir onde nasce: validação no campo do formulário (meia hora de um desenvolvedor) e uma lista suspensa onde hoje há texto livre. A plataforma vai continuar medindo; se a regra de e-mails passar de 96 para 100, o mérito é desta equipe e o painel vai mostrar isso.\n\n"
                  "O que vocês precisam de mim para fazer isso esta semana?”",
        },
    },
]



def automation_rows(lang: str = "es") -> list[dict]:
    """Matriz de automatización resuelta al idioma pedido."""
    return [{
        "area": a["area"].get(lang, a["area"]["es"]),
        "level": a["level"],
        "detail": a["detail"].get(lang, a["detail"]["es"]),
        "speech_id": a["speech_id"],
    } for a in AUTOMATION]


def speeches(lang: str = "es") -> list[dict]:
    """Speeches resueltos al idioma pedido."""
    return [{
        "speech_id": s["speech_id"],
        "title": s["title"].get(lang, s["title"]["es"]),
        "audience": s["audience"].get(lang, s["audience"]["es"]),
        "text": s["text"].get(lang, s["text"]["es"]),
    } for s in SPEECHES]


# ---------------------------------------------------------------------------
# FAQ: Purview / Collibra — mismas preguntas que un cliente/entrevistador
# hace en la práctica, respondidas sin humo (ver docs/PURVIEW_COLLIBRA.md
# para el detalle técnico completo, capacidad por capacidad).
# ---------------------------------------------------------------------------
def _d(es: str, en: str, pt: str) -> dict:
    return {"es": es, "en": en, "pt": pt}


PURVIEW_COLLIBRA_FAQ: list[dict] = [
    {
        "q": _d("¿Purview automatiza algo parecido a este programa?",
               "Does Purview automate something like this program?",
               "O Purview automatiza algo parecido a este programa?"),
        "a": _d(
            "Solo una parte, y no la más difícil. Purview automatiza el **descubrimiento a "
            "escala**: despliega agentes de escaneo dentro de tu infraestructura de Azure que "
            "encuentran automáticamente qué bases/archivos/reportes existen, sin que nadie los "
            "cargue a mano. Pero Purview **no trae motor de reglas de calidad, no tiene "
            "deduplicación/MDM nativo, y no calcula nada por su cuenta** — solo cataloga lo que "
            "encuentra y lo etiqueta con lo que vos (o alguien) le dice.",
            "Only part of it, and not the hardest part. Purview automates **discovery at "
            "scale**: it deploys scanning agents inside your Azure infrastructure that "
            "automatically find what databases/files/reports exist, without anyone loading "
            "them by hand. But Purview **doesn't ship a quality-rule engine, has no native "
            "deduplication/MDM, and computes nothing on its own** — it only catalogs what it "
            "finds and tags it with whatever you (or someone) tells it.",
            "Só uma parte, e não a mais difícil. O Purview automatiza a **descoberta em "
            "escala**: implanta agentes de varredura dentro da sua infraestrutura Azure que "
            "encontram automaticamente quais bancos/arquivos/relatórios existem, sem que "
            "ninguém os carregue manualmente. Mas o Purview **não traz motor de regras de "
            "qualidade, não tem deduplicação/MDM nativo, e não calcula nada por conta própria** "
            "— só cataloga o que encontra e o rotula com o que você (ou alguém) disser."),
    },
    {
        "q": _d("¿Lo útil es mi programa, y después espejarlo a Purview para que quede registrado ahí?",
               "Is the useful part my program, then mirroring it to Purview so it's registered there?",
               "O útil é meu programa, e depois espelhá-lo no Purview para ficar registrado lá?"),
        "a": _d(
            "Exactamente ese es el patrón que implementa el conector de migración (pestaña 🔀). "
            "Tu programa hace el trabajo pesado — perfilar, correr reglas de calidad, generar y "
            "curar el glosario con un responsable real, detectar PII — y al final **empuja el "
            "resultado a Purview por API**, que queda como el catálogo que audita y busca **toda "
            "la empresa**, no solo vos. Ninguno reemplaza al otro: Purview sin ese trabajo previo "
            "es un inventario vacío de insights; tu programa sin Purview es insight sin un lugar "
            "central donde el resto de la empresa lo vea después de que el consultor se va.",
            "That's exactly the pattern the migration connector implements (🔀 tab). Your "
            "program does the heavy lifting — profiling, running quality rules, generating and "
            "curating the glossary with a real responsible person, detecting PII — and at the "
            "end **pushes the result to Purview via API**, which becomes the catalog **the whole "
            "company** audits and searches, not just you. Neither replaces the other: Purview "
            "without that prior work is an empty inventory of insights; your program without "
            "Purview is insight with no central place for the rest of the company to see it "
            "after the consultant leaves.",
            "É exatamente esse o padrão que o conector de migração implementa (aba 🔀). Seu "
            "programa faz o trabalho pesado — perfilamento, execução de regras de qualidade, "
            "geração e curadoria do glossário com um responsável real, detecção de PII — e no "
            "final **empurra o resultado para o Purview via API**, que fica como o catálogo que "
            "**toda a empresa** audita e busca, não só você. Nenhum substitui o outro: o Purview "
            "sem esse trabalho prévio é um inventário vazio de insights; seu programa sem o "
            "Purview é insight sem um lugar central onde o resto da empresa o veja depois que o "
            "consultor sai."),
    },
    {
        "q": _d("¿Para qué sirve Collibra, y en qué se parece/diferencia de Purview?",
               "What is Collibra for, and how is it similar to / different from Purview?",
               "Para que serve o Collibra, e no que se parece/diferencia do Purview?"),
        "a": _d(
            "Collibra es el mismo tipo de plataforma que Purview — catálogo + glosario + calidad "
            "+ stewardship a escala enterprise — pero **no depende de Azure**: funciona "
            "multi-nube y on-premise. Su diferencial fuerte es el **motor de workflows de "
            "aprobación** (un término de glosario pasa por un flujo formal de revisión con "
            "varios roles firmando antes de quedar oficial). Empresas grandes que no quieren "
            "atarse al ecosistema Microsoft suelen elegir Collibra por eso. Similitudes con "
            "Purview: catálogo de datasets/columnas, glosario de negocio, clasificación de "
            "sensibles, linaje — las mismas preguntas de fondo (¿qué datos hay, qué significan, "
            "son sensibles, de dónde vienen?).",
            "Collibra is the same type of platform as Purview — catalog + glossary + quality + "
            "stewardship at enterprise scale — but it **doesn't depend on Azure**: it works "
            "multi-cloud and on-premise. Its strong differentiator is the **approval workflow "
            "engine** (a glossary term goes through a formal review flow with several roles "
            "signing off before it becomes official). Large companies that don't want to be "
            "locked into the Microsoft ecosystem often choose Collibra for that. Similarities "
            "with Purview: dataset/column catalog, business glossary, sensitive-data "
            "classification, lineage — the same underlying questions (what data exists, what "
            "does it mean, is it sensitive, where did it come from?).",
            "O Collibra é o mesmo tipo de plataforma que o Purview — catálogo + glossário + "
            "qualidade + stewardship em escala enterprise — mas **não depende do Azure**: "
            "funciona multi-nuvem e on-premise. Seu diferencial forte é o **motor de workflows "
            "de aprovação** (um termo de glossário passa por um fluxo formal de revisão com "
            "vários papéis assinando antes de ficar oficial). Empresas grandes que não querem se "
            "prender ao ecossistema Microsoft costumam escolher o Collibra por isso. "
            "Semelhanças com o Purview: catálogo de datasets/colunas, glossário de negócio, "
            "classificação de sensíveis, linhagem — as mesmas perguntas de fundo (que dados "
            "existem, o que significam, são sensíveis, de onde vêm?)."),
    },
    {
        "q": _d("¿Mi programa migra a Collibra por API también?",
               "Does my program also migrate to Collibra via API?",
               "Meu programa também migra para o Collibra via API?"),
        "a": _d(
            "Sí, en las dos direcciones. **Empuja** (tu programa → Collibra): catálogo, "
            "diccionario y glosario, mismo patrón acelerador que Purview — pestaña 🔀 Migración. "
            "**Trae** (Collibra → tu programa): assets de tipo Tabla y Business Terms ya "
            "aprobados, con su definición — para no volver a tipear a mano lo que la empresa ya "
            "documentó ahí. Lo que el conector de traída NO trae, a propósito: las asignaciones "
            "de Owner/Steward de Collibra — esa API existe pero no encontré su forma exacta "
            "documentada con suficiente detalle como para implementarla sin adivinar, y adivinar "
            "un endpoint es justo lo que este programa se propuso no hacer nunca.",
            "Yes, in both directions. **Push** (your program → Collibra): catalog, dictionary "
            "and glossary, same accelerator pattern as Purview — 🔀 Migration tab. **Pull** "
            "(Collibra → your program): Table-type assets and already-approved Business Terms, "
            "with their definition — so you don't retype by hand what the company already "
            "documented there. What the pull connector deliberately does NOT bring in: "
            "Collibra's Owner/Steward assignments — that API exists but I couldn't find its "
            "exact shape documented in enough detail to implement it without guessing, and "
            "guessing an endpoint is exactly what this program set out to never do.",
            "Sim, nas duas direções. **Empurra** (seu programa → Collibra): catálogo, "
            "dicionário e glossário, mesmo padrão acelerador do Purview — aba 🔀 Migração. "
            "**Traz** (Collibra → seu programa): assets do tipo Tabela e Business Terms já "
            "aprovados, com sua definição — para não digitar de novo o que a empresa já "
            "documentou lá. O que o conector de trazer NÃO traz, de propósito: as atribuições de "
            "Owner/Steward do Collibra — essa API existe mas não encontrei sua forma exata "
            "documentada com detalhe suficiente para implementá-la sem adivinhar, e adivinhar um "
            "endpoint é justamente o que este programa se propôs a nunca fazer."),
    },
    {
        "q": _d("¿Cuál es mejor, Purview, Collibra o este programa?",
               "Which is better — Purview, Collibra, or this program?",
               "Qual é melhor — Purview, Collibra ou este programa?"),
        "a": _d(
            "Ninguno es \"mejor\" en abstracto — resuelven problemas distintos. Para una empresa "
            "grande ya en Azure con cientos de fuentes, el descubrimiento a escala de Purview "
            "vale la pena igual. Pero ese escaneo solo te dice qué existe — no te dice si tus "
            "datos son buenos (duplicados, huecos de PII, definiciones de negocio inconsistentes) "
            "a menos que algo como este programa haga ese trabajo, ya sea de forma independiente "
            "o como acelerador que alimenta a Purview/Collibra (que es exactamente lo que hace "
            "el conector de migración). El techo de cada capacidad de este programa vs. Purview/"
            "Collibra está documentado sin vueltas en docs/PURVIEW_COLLIBRA.md — pestaña 📘 "
            "Estándares y este mismo menú.",
            "Neither is \"better\" in the abstract — they solve different problems. For a large "
            "company already on Azure with hundreds of sources, Purview's discovery at scale is "
            "worth it regardless. But that scan alone only tells you what exists — it won't tell "
            "you whether your data is good (duplicates, PII gaps, inconsistent business "
            "definitions) unless something like this program does that work, either "
            "independently or as an accelerator feeding Purview/Collibra (exactly what the "
            "migration connector does). Every capability's ceiling vs. Purview/Collibra is "
            "documented plainly in docs/PURVIEW_COLLIBRA.md — 📘 Standards tab and this same menu.",
            "Nenhum é \"melhor\" em abstrato — resolvem problemas diferentes. Para uma empresa "
            "grande já no Azure com centenas de fontes, a descoberta em escala do Purview vale a "
            "pena de qualquer forma. Mas essa varredura só diz o que existe — não diz se seus "
            "dados são bons (duplicados, lacunas de PII, definições de negócio inconsistentes) a "
            "menos que algo como este programa faça esse trabalho, seja de forma independente ou "
            "como acelerador que alimenta o Purview/Collibra (exatamente o que o conector de "
            "migração faz). O teto de cada capacidade deste programa vs. Purview/Collibra está "
            "documentado sem rodeios em docs/PURVIEW_COLLIBRA.md — aba 📘 Padrões e este mesmo "
            "menu."),
    },
]


def purview_collibra_faq(lang: str = "es") -> list[dict]:
    """FAQ resuelto al idioma pedido."""
    return [{"q": item["q"].get(lang, item["q"]["es"]),
            "a": item["a"].get(lang, item["a"]["es"])} for item in PURVIEW_COLLIBRA_FAQ]
