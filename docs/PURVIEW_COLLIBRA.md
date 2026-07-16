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

---

## Parte 2 — Conector de migración: acelerador, no reemplazo

Este programa puede **empujar** el catálogo, el diccionario y el glosario
ya gobernados hacia Purview o Collibra por API (pestaña 📤 BI & API →
🔀 Migración). El criterio de diseño, para que quede explícito y no sea
accidental:

> Tu programa hace el trabajo pesado (perfilar, correr las reglas de
> calidad, generar el glosario, detectar PII, curar las definiciones con
> un responsable real) y al final empuja el resultado a Purview/Collibra
> por API, que siguen siendo la plataforma que el cliente audita y usa
> después de que el consultor se va. **Nunca al revés**: si el cliente ve
> "Purview" pero todo el trabajo real vive en este programa y nadie de su
> equipo puede repetir el proceso sin vos, eso rompe el principio más
> básico de gobernanza que este mismo programa promueve — sostenibilidad
> sin depender de una persona. El flujo tiene que quedar documentado y
> repetible por cualquiera del equipo del cliente, no ser una caja negra.

### Qué se empuja, y de dónde sale cada dato

| Va a Purview/Collibra como… | Sale de… |
|---|---|
| Entidad Tabla (`rdbms_table` / asset "Tabla") | 📚 Catálogo — un dataset gobernado |
| Entidad Columna (`rdbms_column` / asset "Columna") | 📚 Diccionario de columnas |
| Término de glosario, estado **Draft** | Definición pre-establecida por IA, **sin revisar** |
| Término de glosario, estado **Approved** | Definición **validada o modificada por un Data Owner/Steward real** en 🖊️ Curaduría |
| Clasificación de dato sensible (PII) | Columnas marcadas `pii=True` en el diccionario |

El estado Draft/Approved en Purview, y en general qué está "gobernado de
verdad", refleja tu curaduría real — no se inventa nada del lado del
conector.

### Cómo probarlo sin arriesgar nada

El botón **👁️ Previsualizar** arma exactamente el payload que se
mandaría — cuántas entidades, cuántos términos, con qué estado y qué
clasificación — **sin ninguna credencial cargada y sin tocar la red**. Es
el modo recomendado para revisar antes de conectar contra un
tenant/instancia real.

### Microsoft Purview

1. Creá un service principal (mismos pasos que para el escaneo de tenant
   de Power BI — ver `docs/BI_TENANT_SCAN.md`), y asignale el rol **Data
   Curator** sobre la colección de Purview que vas a usar (Purview
   governance portal → Data Map → Collections → tu colección → Role
   assignments).
2. Cargá las variables de entorno: `PURVIEW_TENANT_ID`, `PURVIEW_CLIENT_ID`,
   `PURVIEW_CLIENT_SECRET`, `PURVIEW_ACCOUNT_NAME` (el nombre corto de tu
   cuenta de Purview, sin el dominio).
3. Si tu organización usa el "nuevo portal" de Purview
   (`api.purview-service.microsoft.com`) en vez del clásico
   (`{cuenta}.purview.azure.com`), fijá `PURVIEW_API_BASE` con la URL base
   que corresponda.
4. ¿No tenés todavía una cuenta de Purview para probar? Microsoft ofrece
   una **versión gratis de Purview Governance** si tu organización ya usa
   Azure/Microsoft 365 — alcanza y sobra para probar este conector contra
   una colección de prueba antes de usarlo con un cliente real.

### Collibra

Acá hay una diferencia real con Purview: el modelo de datos de Collibra
(Communities → Domains → Assets → Attributes) es **configurable por
instancia** — no hay forma de adivinar los IDs desde afuera.

1. Cargá `COLLIBRA_BASE_URL`, `COLLIBRA_USERNAME`, `COLLIBRA_PASSWORD` (un
   usuario de servicio con permiso de creación de assets).
2. Sacá el `COLLIBRA_DOMAIN_ID` de tu instancia (Settings → Domains, o la
   URL al entrar al dominio de destino) — **obligatorio**, no tiene
   default posible.
3. Para empujar catálogo/diccionario, además necesitás
   `COLLIBRA_TABLE_TYPE_ID` y `COLLIBRA_COLUMN_TYPE_ID` — los IDs de tipo
   de asset "Tabla"/"Columna" de tu Operating Model (Data Dictionary o el
   que uses). Se sacan navegando a ese tipo de asset en Collibra y
   mirando su ID en la URL o vía la API `/assetTypes`.
4. Para el glosario, `COLLIBRA_TERM_TYPE_ID` tiene un default razonable
   (el UUID de "Business Term" del modelo de fábrica de Collibra,
   documentado por Collibra mismo) — funciona en la mayoría de las
   instancias sin tocar nada, pero es sobreescribible si tu modelo usa
   otro tipo.
5. A diferencia de Purview, Collibra **no** ofrece un entorno de prueba de
   autoservicio gratuito — la práctica real depende de que un cliente o
   empleador te dé acceso a una instancia.

### Honestidad sobre lo que está verificado

Implementado contra la documentación oficial de Microsoft Learn (Purview,
API basada en Apache Atlas) y del Collibra Developer Portal, revisada el
2026-07-15 — cada endpoint y forma de payload usado acá está sacado de esa
documentación, no inventado. **Ninguno de los dos conectores se probó
contra un tenant/instancia real** (no hay uno disponible en este entorno
de desarrollo). Antes de usarlo con un cliente: probá primero con
`dry_run` (el botón Previsualizar) y después contra una colección/dominio
de prueba, nunca directo a producción.

### Verificación

`python -m mvdg.selfcheck` incluye el chequeo **"Migración a
Purview/Collibra"**, que confirma que ambos conectores están apagados por
defecto sin credenciales, y que el modo dry-run arma correctamente el
payload completo (entidades, términos, clasificaciones PII) sin tocar la
red. Los tests (`tests/test_core.py`) además simulan el transporte HTTP
end-to-end para validar la forma exacta de cada request contra lo
documentado, incluyendo el caso donde el estado de un término refleja una
curaduría real (validado por un Data Owner) vs. una sugerencia de IA sin
revisar.
