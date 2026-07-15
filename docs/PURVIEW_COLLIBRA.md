# 🏛️ MV Data Governance vs. Microsoft Purview / Collibra — comparación honesta

Purview y Collibra son las dos plataformas de gobierno de datos de
referencia a escala enterprise. Esta página responde una pregunta directa:
**¿qué tienen ellas que este programa no tenga — y qué hicimos al respecto?**

La regla de esta comparación es la misma de todo el producto: sin humo.
Donde cubrimos lo mismo, se dice; donde cubrimos una versión más simple, se
dice; donde no llegamos (y no tiene sentido llegar en una herramienta
local-first para PyMEs), también se dice.

## Tabla de capacidades

| Capacidad | Purview / Collibra | MV Data Governance |
|---|---|---|
| Catálogo de datos con dueño/steward/clasificación | ✅ | ✅ pestañas 📚 Catálogo + 🔎 Mis datos |
| Glosario de negocio | ✅ | ✅ pestaña 📖 Glosario, trilingüe |
| **Workflow de curaduría/aprobación de definiciones** | ✅ (flujos de aprobación) | ✅ pestaña 🖊️ **Curaduría**: todo pre-establecido por IA → el Data Owner/Steward valida o modifica, con nombre, cargo, fecha y notas |
| **Asignación de responsables (stewardship)** | ✅ (roles por asset) | ✅ pestaña 👥 **Responsables**: organigrama (Excel/CSV/SQL/foto) → owner+steward por defecto por dataset, editable |
| **Insights del estado del gobierno** | ✅ ("Data Estate Insights") | ✅ Panorama → 🏛️ **Estado del gobierno**: índice 0-100 con 5 coberturas (owner nombrado, steward, clasificación, reglas, curaduría) |
| Calidad de datos con reglas y umbrales | ✅ (DQ modules) | ✅ pestaña ✅ Calidad: 6 dimensiones DAMA + remediación IA |
| Linaje | ✅ multi-sistema automático | ✅ pestaña 🧬 Linaje + linaje real SQL→tabla→dataset→reporte para Power BI/Tableau. Lo que NO hay: descubrimiento automático de linaje entre decenas de sistemas — acá el linaje sale de las fuentes que conectás |
| Escaneo de fuentes | ✅ cientos de conectores gestionados | 🟡 9 motores SQL/cloud (PostgreSQL…Snowflake/BigQuery/Databricks/Synapse) + Power BI tenant + Tableau site + archivos. Suficiente para una PyME; un tenant enterprise multi-nube con cientos de fuentes es territorio Purview |
| Detección/clasificación de datos sensibles | ✅ (clasificadores gestionados + etiquetas MIP) | 🟡 detección heurística de PII + clasificación por dataset (Pública/Interna/Confidencial/PII). Lo que NO hay: etiquetas de sensibilidad aplicadas al documento/columna que viajen con el dato (eso requiere la integración Microsoft Information Protection) |
| MDM / deduplicación | ➖ (Collibra parcial, Purview no) | ✅ pestaña 🔗 MDM con golden record — acá el programa cubre algo que Purview no trae |
| **Enforcement de acceso a datos** (políticas que bloquean consultas) | ✅ Purview (en el stack Azure) | ❌ **Fuera de alcance a propósito**: para bloquear un acceso hay que estar en el camino del dato (proxy/gateway). Este programa audita y documenta en modo lectura; el enforcement es de la base/warehouse o de herramientas como Purview dentro de Azure |
| Data sharing / contratos de datos | ✅ | ❌ Fuera de alcance: aplica a organizaciones que publican datos entre unidades/empresas |
| Precio y despliegue | Suscripción cloud, por capacidad; requiere tenant/infra | Licencia única o suscripción chica; corre en una notebook, sin nube, sin telemetría |

## Lo que este programa cubre y ellas no (o no igual)

- **100% local y sin telemetría** — entra donde la política de privacidad
  no deja entrar a un SaaS. Purview vive en Azure; Collibra en su cloud.
- **Golden record / deduplicación (MDM)** integrada al mismo flujo.
- **Trilingüe de punta a punta** (ES/EN/PT), pensado para equipos
  latinoamericanos.
- **La IA propone, el humano decide, y queda registrado** — el mismo
  patrón en Curaduría, Responsables, reglas sugeridas y remediación.

## Lo que falta a propósito (y por qué)

1. **Enforcement de acceso**: bloquear consultas exige interponerse entre
   el usuario y la base. Un producto de escritorio no debe hacer eso — y
   simularlo sería vender humo. Se documenta qué política se incumple
   (pestaña 🛡️), y el bloqueo se implementa en la base/warehouse.
2. **Escaneo automático de cientos de fuentes gestionadas**: el valor de
   Purview ahí es su parque de conectores cloud administrados. Este
   programa cubre los 9 motores + BI más comunes; agregar conectores es
   incremental según lo pidan los clientes.
3. **Etiquetas de sensibilidad que viajan con el dato** (MIP): son un
   feature del ecosistema Microsoft 365, no replicable desde afuera.

---

**English (summary):** honest comparison with Purview/Collibra. Covered
equally: catalog, glossary, curation workflow (🖊️), stewardship assignment
(👥), governance insights (🏛️), quality, lineage for connected sources, MDM
(which Purview lacks). Partially: source scanning (9 engines + BI vs.
hundreds of managed connectors), sensitive-data classification (heuristic
PII vs. managed classifiers + MIP labels). Deliberately out of scope:
access enforcement (requires sitting in the data path), data sharing
contracts, MIP labels. The trade-off: 100% local, zero telemetry, runs on a
laptop.

**Português (resumo):** comparação honesta com Purview/Collibra. Coberto
igual: catálogo, glossário, workflow de curadoria (🖊️), atribuição de
stewardship (👥), insights de governança (🏛️), qualidade, linhagem das
fontes conectadas, MDM (que o Purview não tem). Parcial: varredura de
fontes (9 motores + BI vs. centenas de conectores gerenciados),
classificação de dados sensíveis (PII heurística vs. classificadores
gerenciados + rótulos MIP). Fora de escopo de propósito: enforcement de
acesso (exige estar no caminho do dado), contratos de compartilhamento,
rótulos MIP. A contrapartida: 100% local, zero telemetria, roda num laptop.
