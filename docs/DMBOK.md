# 📘 DAMA-DMBOK · Guía y mapeo con MV Data Governance

## 🇪🇸 Español

### ¿Qué es el DMBOK?

El **DMBOK** (*Data Management Body of Knowledge*) es el estándar de
referencia de la industria en gobierno de datos, publicado por **DAMA
International**. Define **11 áreas de conocimiento** que, juntas, cubren
todo lo que una empresa necesita para gestionar bien sus datos.

MV Data Governance implementa a fondo varias de esas áreas (calidad,
metadatos, linaje, BI, datos maestros) y ayuda parcialmente en otras
(seguridad, arquitectura) — sin pretender cubrir las que son responsabilidad
de otro equipo o herramienta (modelado, almacenamiento, gestión documental).
Esta guía existe para que tanto **quien no es técnico** como **quien sí lo
es** entiendan de qué se trata cada área y qué hace exactamente la
plataforma en cada una.

> **Tutorial completo dentro del programa:** la pestaña **📘 Estándares** trae
> un tutorial interactivo con teoría y tableros: los principios rectores, las
> 11 áreas (con entregables típicos y cobertura), un glosario de conceptos
> clave (dueño vs. steward vs. custodio, MDM, golden record, metadato,
> linaje, POSMAD…), los roles del gobierno de datos, el modelo de madurez
> de 5 niveles y el ciclo de vida del dato — con un radar de cobertura por
> área y el tablero de las 6 dimensiones de calidad medidas en vivo. Todo
> trilingüe (ES/EN/PT).
>
> La misma pestaña **📘 Estándares** trae, en dos sub-pestañas más, la misma
> autoevaluación honesta frente a **COBIT 2019** (los 8 objetivos de
> gobierno/gestión de ISACA relacionados con datos) y **ISO/IEC 38505** (los
> 6 principios de gobierno de datos + el modelo Valor/Riesgo/Restricción).
> Ninguno de los tres es una certificación — son guías de qué cubre la
> plataforma y qué queda en manos de tu organización.

### 🙋 Si no sos técnico

Pensá el DMBOK como una checklist de 11 preguntas que toda empresa debería
poder responder sobre sus datos: ¿quién decide qué? ¿están completos y
correctos? ¿sabemos qué significan? ¿de dónde vienen? ¿alimentan bien los
tableros? ¿están protegidos los datos personales? Esta plataforma responde
automáticamente a la mayoría de esas preguntas con evidencia (números,
alertas, catálogos) en vez de opiniones.

### 🛠️ Si sos técnico

El DMBOK organiza el gobierno de datos en 11 "knowledge areas" con **Data
Governance** en el centro, coordinando a las otras 10. La plataforma
implementa 6 de ellas end-to-end (motor de reglas de calidad sobre 6
dimensiones DAMA, catálogo/diccionario, linaje, conectores SQLAlchemy,
exportación multi-formato, API REST para BI), ofrece cobertura parcial en 3
(seguridad vía detección heurística de PII, glosario como base de datos
maestros/referencia, catálogo+linaje como arquitectura de estado actual) y
deja explícitamente fuera 3 (modelado ER/dimensional, administración de
almacenamiento/infraestructura, gestión documental) por ser responsabilidad
de otras herramientas o equipos.

### Las 11 áreas

| # | Área | Cobertura | Qué hace la plataforma |
|---|---|---|---|
| 1 | Gobierno de datos | ✅ Cubierta | Políticas, comité, speeches para lograr sponsors y dueños |
| 2 | Calidad de datos | ✅ Cubierta | 17 reglas / 6 dimensiones DAMA, 100% automático |
| 3 | Gestión de metadatos | ✅ Cubierta | Catálogo de datasets + diccionario de columnas |
| 4 | Linaje e integración | ✅ Cubierta | Mapa de linaje + conectores a bases + exportación multi-formato |
| 5 | Data warehousing y BI | ✅ Cubierta | API REST (9 tablas) + bundle .xlsx para Power BI/Tableau/Qlik/etc. |
| 6 | Datos maestros y de referencia | ✅ Cubierta | Glosario + motor de deduplicación por reglas ponderadas (pestaña 🔗 MDM), con golden record propuesto |
| 7 | Seguridad de datos | 🟡 Parcial | Detección heurística de PII; el control de accesos lo define TI |
| 8 | Arquitectura de datos | 🟡 Parcial | Documenta el estado actual; no diseña el estado objetivo |
| 9 | Modelado y diseño | ⬜ Fuera de alcance | Perfila esquemas existentes, no es herramienta de modelado |
| 10 | Almacenamiento y operaciones | ⬜ Fuera de alcance | Se conecta en lectura; no administra infraestructura |
| 11 | Gestión documental | ⬜ Fuera de alcance | Trabaja con datos estructurados (tablas), no documentos |

> El detalle completo de cada área (explicación en criollo + técnica) está
> en `mvdg/help_center.py` (`DMBOK_AREAS`) y se renderiza en vivo, en los 3
> idiomas, dentro de la pestaña Ayuda del programa.

---

## 🇬🇧 English

### What is the DMBOK?

The **DMBOK** (*Data Management Body of Knowledge*) is the industry
reference standard for data governance, published by **DAMA
International**. It defines **11 knowledge areas** that together cover
everything a company needs to properly manage its data.

MV Data Governance fully implements several of those areas (quality,
metadata, lineage, BI, master data) and partially helps with others
(security, architecture) — without claiming to cover the ones that belong to
another team or tool (modeling, storage, document management). This guide
exists so that both **non-technical** and **technical** readers understand
what each area is about and exactly what the platform does for it. The same
content is available inside the program, under the **Help → "DAMA-DMBOK
framework"** tab.

### 🙋 If you're not technical

Think of the DMBOK as a checklist of 11 questions every company should be
able to answer about its data: who decides what? is it complete and
correct? do we know what it means? where does it come from? does it feed
the dashboards properly? is personal data protected? This platform answers
most of those questions automatically, with evidence (numbers, alerts,
catalogs) instead of opinions.

### 🛠️ If you're technical

The DMBOK organizes data governance into 11 knowledge areas with **Data
Governance** at the center, coordinating the other 10. The platform
implements 6 of them end-to-end (a rule engine across 6 DAMA quality
dimensions, catalog/dictionary, lineage, SQLAlchemy connectors, multi-format
export, a REST API for BI), offers partial coverage in 3 (security via
heuristic PII detection, glossary as a reference/master-data base,
catalog+lineage as current-state architecture) and explicitly leaves 3 out
(ER/dimensional modeling, storage/infrastructure administration, document
management) since those belong to other tools or teams.

### The 11 areas

| # | Area | Coverage | What the platform does |
|---|---|---|---|
| 1 | Data Governance | ✅ Covered | Policies, committee, speeches to win sponsors and owners |
| 2 | Data Quality | ✅ Covered | 17 rules / 6 DAMA dimensions, 100% automatic |
| 3 | Metadata Management | ✅ Covered | Dataset catalog + column dictionary |
| 4 | Data Integration & Lineage | ✅ Covered | Lineage map + database connectors + multi-format export |
| 5 | Data Warehousing & BI | ✅ Covered | REST API (9 tables) + .xlsx bundle for Power BI/Tableau/Qlik/etc. |
| 6 | Reference & Master Data | ✅ Covered | Glossary + weighted-rule deduplication engine (🔗 MDM tab), with a proposed golden record |
| 7 | Data Security | 🟡 Partial | Heuristic PII detection; access control is defined by IT |
| 8 | Data Architecture | 🟡 Partial | Documents the current state; doesn't design the target state |
| 9 | Data Modeling & Design | ⬜ Out of scope | Profiles existing schemas, not a modeling tool |
| 10 | Data Storage & Operations | ⬜ Out of scope | Connects read-only; doesn't manage infrastructure |
| 11 | Documents & Content Mgmt | ⬜ Out of scope | Works with structured data (tables), not documents |

---

## 🇧🇷 Português

### O que é o DMBOK?

O **DMBOK** (*Data Management Body of Knowledge*) é o padrão de referência
da indústria em governança de dados, publicado pela **DAMA International**.
Define **11 áreas de conhecimento** que, juntas, cobrem tudo o que uma
empresa precisa para gerenciar bem seus dados.

O MV Data Governance implementa a fundo várias dessas áreas (qualidade,
metadados, linhagem, BI, dados mestres) e ajuda parcialmente em outras
(segurança, arquitetura) — sem pretender cobrir as que são responsabilidade de
outra equipe ou ferramenta (modelagem, armazenamento, gestão documental).
Este guia existe para que tanto **quem não é técnico** quanto **quem é**
entendam do que se trata cada área e o que exatamente a plataforma faz em
cada uma. O mesmo conteúdo está disponível dentro do programa, na aba
**Ajuda → "Marco DAMA-DMBOK"**.

### 🙋 Se você não é técnico

Pense no DMBOK como uma checklist de 11 perguntas que toda empresa deveria
conseguir responder sobre seus dados: quem decide o quê? estão completos e
corretos? sabemos o que significam? de onde vêm? alimentam bem os painéis?
os dados pessoais estão protegidos? Esta plataforma responde
automaticamente à maioria dessas perguntas com evidências (números,
alertas, catálogos) em vez de opiniões.

### 🛠️ Se você é técnico

O DMBOK organiza a governança de dados em 11 "knowledge areas" com **Data
Governance** no centro, coordenando as outras 10. A plataforma implementa 6
delas de ponta a ponta (motor de regras sobre 6 dimensões DAMA de
qualidade, catálogo/dicionário, linhagem, conectores SQLAlchemy, exportação
multi-formato, API REST para BI), oferece cobertura parcial em 3 (segurança
via detecção heurística de PII, glossário como base de dados
mestres/referência, catálogo+linhagem como arquitetura do estado atual) e
deixa explicitamente de fora 3 (modelagem ER/dimensional, administração de
armazenamento/infraestrutura, gestão documental) por serem responsabilidade
de outras ferramentas ou equipes.

### As 11 áreas

| # | Área | Cobertura | O que a plataforma faz |
|---|---|---|---|
| 1 | Governança de dados | ✅ Coberta | Políticas, comitê, speeches para conseguir patrocinadores e donos |
| 2 | Qualidade de dados | ✅ Coberta | 17 regras / 6 dimensões DAMA, 100% automático |
| 3 | Gestão de metadados | ✅ Coberta | Catálogo de datasets + dicionário de colunas |
| 4 | Integração e linhagem | ✅ Coberta | Mapa de linhagem + conectores a bancos + exportação multi-formato |
| 5 | Data warehousing e BI | ✅ Coberta | API REST (9 tabelas) + pacote .xlsx para Power BI/Tableau/Qlik/etc. |
| 6 | Dados mestres e de referência | ✅ Coberta | Glossário + motor de deduplicação por regras ponderadas (aba 🔗 MDM), com golden record proposto |
| 7 | Segurança de dados | 🟡 Parcial | Detecção heurística de PII; o controle de acesso é definido por TI |
| 8 | Arquitetura de dados | 🟡 Parcial | Documenta o estado atual; não desenha o estado alvo |
| 9 | Modelagem e desenho | ⬜ Fora de escopo | Perfila esquemas existentes, não é ferramenta de modelagem |
| 10 | Armazenamento e operações | ⬜ Fora de escopo | Conecta em leitura; não administra infraestrutura |
| 11 | Gestão documental | ⬜ Fora de escopo | Trabalha com dados estruturados (tabelas), não documentos |
