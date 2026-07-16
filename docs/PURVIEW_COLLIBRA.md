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
| Escaneo de fuentes | ✅ cientos de conectores gestionados | 🟡 9 motores SQL/cloud + Power BI tenant + Tableau site + archivos, con **escaneo batch de todas tus conexiones guardadas de un clic** (📤 BI & API → 🔎 Escanear todas). Sigue sin ser descubrimiento automático de fuentes nuevas a escala de tenant — ver detalle abajo |
| Detección/clasificación de datos sensibles | ✅ (clasificadores gestionados + etiquetas MIP) | 🟡 detección heurística de PII + clasificación por dataset + **conector real a Microsoft Graph para aplicar etiquetas MIP de verdad** (🏷️ pestaña nueva) — con el límite honesto de que solo aplica a archivos que ya viven en OneDrive/SharePoint, ver detalle abajo |
| MDM / deduplicación | ➖ (Collibra parcial, Purview no) | ✅ pestaña 🔗 MDM con golden record — acá el programa cubre algo que Purview no trae |
| **Enforcement de acceso a datos** (políticas que bloquean consultas) | ✅ Purview (en el stack Azure) | 🟡 **Generador de DDL real** (🔒 pestaña nueva): GRANT/REVOKE por clasificación + enmascaramiento de columnas PII, para PostgreSQL y SQL Server — el programa arma la receta, un DBA (o Purview) la ejecuta. Sigue sin bloquear nada por sí mismo — ver el porqué abajo |
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

## Los tres gaps que se cerraron parcialmente (con el techo explícito)

Estos tres quedaron marcados "fuera de alcance a propósito" en una versión
anterior de este documento. Se construyó lo máximo genuinamente posible de
cada uno — sin fingir ser algo que un programa de escritorio local no
puede ser.

### 1. Enforcement de acceso → generador de DDL (🔒 nueva sección en 📤 BI & API)

**Por qué sigue sin bloquear nada en vivo:** bloquear una consulta exige
estar parado en el camino del dato — un proxy o gateway entre el usuario y
la base, o una plataforma cloud-native como Purview dentro de Azure. Montar
un interceptor de consultas desde un programa de escritorio sería frágil,
peligroso en producción real, y — sobre todo — vendería humo sobre lo que
este programa es.

**Lo que sí se construyó:** `mvdg/enforcement.py` toma el catálogo/
diccionario ya gobernados y genera el **DDL real** — `GRANT`/`REVOKE` por
clasificación, enmascaramiento de columnas PII (Row-Level Security nativo
en PostgreSQL, Dynamic Data Masking nativo en SQL Server) — como texto
SQL para copiar y correr. El módulo **no importa ningún driver de base de
datos ni abre ninguna conexión** (verificado por test: se audita el código
fuente para confirmar que no hay `sqlalchemy`/`.execute(` en ningún lado).
El programa arma la receta; quien tiene las llaves de la base la ejecuta.

### 2. Escaneo de fuentes → batch de todas las conexiones (🔎 en 📤 BI & API)

**Por qué sigue sin ser "cientos de conectores gestionados":** el valor de
Purview ahí es desplegar agentes de escaneo DENTRO de la infraestructura
de Azure del cliente, que descubren recursos nuevos automáticamente sin
que nadie cargue una conexión a mano. Eso es, literalmente, ser
infraestructura cloud — no algo que un programa Python de escritorio deba
intentar ser.

**Lo que sí se construyó (dos niveles):**

- `scan_all_connections()` escanea de un clic TODAS las conexiones que ya
  cargaste en el programa (hoy: 9 motores SQL/cloud), en vez de elegir una
  por vez. Si una conexión está caída, no frena el resto — el error queda
  registrado en su fila. Sigue siendo un batch sobre lo que vos
  conectaste, no descubrimiento autónomo.
- `mvdg/azure_discovery.py` (☁️ en 📤 BI & API) da un paso más real hacia
  el descubrimiento: con tu service principal (rol **Reader**, de solo
  lectura), **una sola consulta** a la **Azure Resource Graph API** trae
  todos los recursos de datos — SQL Database, Storage Account, Synapse,
  Cosmos DB, Data Factory, Azure MySQL/PostgreSQL, Databricks — de **toda
  tu suscripción**, sin desplegar ningún agente ni cargar nada a mano. No
  es "convertirse en Purview" (sigue siendo una consulta bajo demanda, no
  un agente persistente que vigila el tenant en continuo, y no cruza
  management groups por defecto), pero es un salto real: de "lo que vos
  cargaste" a "lo que existe en tu suscripción de Azure".

### 3. Etiquetas de sensibilidad → conector real a Microsoft Graph (🏷️ en 📤 BI & API)

**Por qué sigue teniendo un límite real:** una etiqueta MIP no es texto —
es cifrado y Rights Management embebidos en el propio archivo de Office,
atados a la infraestructura de Azure Information Protection de Microsoft.
No hay forma de reimplementar eso localmente, en este programa ni en
ningún otro fuera del ecosistema Microsoft.

**Lo que sí se construyó:** `mvdg/mip_labels.py` llama a la Microsoft
Graph API **real** (`assignSensitivityLabel`, documentada en Microsoft
Learn) para aplicar una etiqueta de verdad a un archivo que ya vive en
OneDrive/SharePoint, eligiendo la etiqueta según la clasificación que este
catálogo ya calculó — y **siempre resuelta contra la lista real de
etiquetas configuradas en tu tenant**, nunca un id inventado. El límite
honesto: solo funciona para datasets cuyo archivo fuente ya está en
Microsoft 365 (una tabla de PostgreSQL no tiene "etiqueta MIP" posible,
porque la etiqueta vive en el formato del archivo, no en el dato en
abstracto) — esos datasets se listan aparte, explícitamente.

---

**English (summary):** honest comparison with Purview/Collibra. Covered
equally: catalog, glossary, curation workflow (🖊️), stewardship assignment
(👥), governance insights (🏛️), quality, lineage for connected sources, MDM
(which Purview lacks). Partially covered, each with an explicit ceiling:
source scanning (batch scan of all your saved connections vs. hundreds of
cloud-managed connectors), sensitive-data classification (heuristic PII +
a real Microsoft Graph connector that applies genuine MIP labels to files
already in OneDrive/SharePoint — can't apply to a database table, since
the label lives in the file format), access enforcement (generates real
GRANT/REVOKE + masking DDL for PostgreSQL/SQL Server — never executes it,
since blocking a live query requires sitting in the data path). Still
deliberately out of scope: data sharing contracts (enterprise data-mesh
territory). The trade-off: 100% local, zero telemetry, runs on a laptop.

**Português (resumo):** comparação honesta com Purview/Collibra. Coberto
igual: catálogo, glossário, workflow de curadoria (🖊️), atribuição de
stewardship (👥), insights de governança (🏛️), qualidade, linhagem das
fontes conectadas, MDM (que o Purview não tem). Parcialmente coberto, cada
um com um teto explícito: varredura de fontes (escaneamento em lote de
todas as suas conexões salvas vs. centenas de conectores gerenciados na
nuvem), classificação de dados sensíveis (PII heurística + um conector
real ao Microsoft Graph que aplica rótulos MIP verdadeiros a arquivos já
no OneDrive/SharePoint — não se aplica a uma tabela de banco, pois o
rótulo vive no formato do arquivo), enforcement de acesso (gera DDL real
de GRANT/REVOKE + mascaramento para PostgreSQL/SQL Server — nunca o
executa, já que bloquear uma consulta em tempo real exige estar no
caminho do dado). Ainda fora de escopo de propósito: contratos de
compartilhamento de dados (território enterprise de data mesh). A
contrapartida: 100% local, zero telemetria, roda num laptop.

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

### Collibra en las dos direcciones: push y pull

La migración con Collibra no es de una sola vía. Además de empujar (arriba),
la pestaña **⬇️ Traer de Collibra** (en 📤 BI & API, `mvdg/collibra_pull.py`)
hace el camino inverso: lee tu instancia y trae **Business Terms ya
aprobados** (con su Definición) y **assets de tipo Tabla** (con la suya),
para no volver a tipear a mano lo que la empresa ya documentó en Collibra.
Mismas variables de entorno que el push.

**Límite explícito, y por qué es así:** el conector de traída NO trae las
asignaciones de Owner/Steward de Collibra (el recurso "Responsibility" de
su API). Esa API existe, pero no encontré su forma exacta de request/
response documentada públicamente con el detalle suficiente como para
implementarla con la misma confianza que el resto de este proyecto —
cada endpoint usado en `purview_export.py`, `collibra_export.py`,
`mip_labels.py` y `azure_discovery.py` está sacado de una página de
Microsoft Learn o del Collibra Developer Portal con ejemplos de request/
response reales. Para "Responsibility" no encontré esa misma calidad de
fuente pública, y adivinar un endpoint es exactamente lo que este
proyecto se propuso no hacer nunca. La Swagger UI de tu propia instancia
(`https://tu-instancia.collibra.com/rest/2.0/ui`) tiene la especificación
exacta de tu versión — es la vía correcta para completar esto con
confianza, no adivinando desde afuera.

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

### Verificación de los tres gaps parcialmente cerrados

`python -m mvdg.selfcheck` incluye tres chequeos dedicados:

- **"Enforcement de acceso"**: confirma que `enforcement.py` genera GRANT/
  REVOKE + DDL de enmascaramiento para PostgreSQL y SQL Server, y que el
  código fuente del módulo no importa ningún driver de base de datos ni
  usa `.execute(` en ningún lado — no hay ningún camino posible para que
  ejecute algo por accidente.
- **"Etiquetas MIP"**: confirma que está apagado por defecto (sin
  credenciales, `list_labels()` devuelve `[]` sin intentar conectarse), y
  que los datasets sin archivo mapeado en OneDrive/SharePoint quedan
  listados explícitamente, nunca salteados en silencio. Un test de
  integración levanta un servidor HTTP local que responde exactamente
  como documenta Microsoft Graph, y corre el conector real contra él (con
  sockets HTTP de verdad — mismo patrón que la simulación de Purview/
  Collibra) para confirmar que arma bien la codificación de sharing URL,
  el token y el payload de `assignSensitivityLabel`.
- **"Escaneo batch de todas las conexiones"**: confirma con una conexión
  real (SQLite) que funciona, y otra rota a propósito, que una conexión
  caída no frena el escaneo de las demás.

## Parte 3 — Ronda de correcciones y profundización (2026-07-16)

Una auditoría externa (pedida explícitamente por el usuario) revisó el
conector de migración y encontró bugs reales y gaps genuinos. Esta sección
documenta qué se corrigió, qué se construyó de nuevo, y — con el mismo
criterio de todo este documento — qué techo sigue existiendo y por qué.

### Bugs corregidos

- **Clasificación de teléfono mal mapeada**: `phone`/`telefono` caía en
  `MICROSOFT.PERSONAL.IPADDRESS` (copiar y pegar). Corregido a
  `MICROSOFT.PERSONAL.US.PHONE_NUMBER` — con una salvedad honesta: existe
  la clasificación de sistema "U.S. phone number" en Purview, pero
  Microsoft Learn no publica el string técnico exacto en ninguna página
  (solo el nombre visible), así que a diferencia del resto de este
  diccionario, este valor concreto **no está confirmado carácter por
  carácter**. Antes de depender de esto en producción: `GET
  {endpoint}/catalog/api/atlas/v2/types/typedefs` contra tu propio tenant
  y confirmá el `classificationDef` real. `ip_address` (una columna que
  de verdad es una IP) sí usa `MICROSOFT.PERSONAL.IPADDRESS` correctamente.
- **Columnas huérfanas en Purview**: las entidades `rdbms_column` no
  llevaban relación a su `rdbms_table` — la pestaña "Schema" de la tabla
  quedaba vacía. Corregido con `relationshipAttributes.table`, el nombre
  de atributo real que define Apache Atlas para esa relación (verificado
  contra el typedef oficial `2010-rdbms_model.json` del repo de Apache
  Atlas, y contra el tutorial de lineage de Microsoft Learn para el par
  análogo `hive_column`/`hive_table`).
- **Un segundo push del glosario a Purview fallaba**: `POST
  glossary/term` devuelve 409 si el término ya existe por nombre — un
  re-push completo abortaba a mitad de camino. Ahora `push_glossary`
  primero lista los términos existentes del glosario (`GET
  glossary/{guid}/terms`) y actualiza (`PUT glossary/term/{guid}`) los
  que coinciden por nombre; solo los nuevos usan `POST`. Idempotente de
  verdad, no solo en la happy path.

### Gap más grande cerrado: pull desde Purview (antes solo existía para Collibra)

`mvdg/purview_pull.py` (nuevo) trae de vuelta lo que ya está en Purview,
espejo de `collibra_pull.py`:

- **Glosario**: `GET .../catalog/api/atlas/v2/glossary` + `GET
  .../glossary/{guid}/terms` — mismos endpoints clásicos que usa el push.
- **Catálogo** (tablas ya registradas): acá hubo una sorpresa al
  verificar — el endpoint de discovery/search clásico bajo
  `/catalog/api/...` **ya no está documentado por Microsoft como un
  recurso propio** (su página de referencia redirige permanentemente a la
  de `/datamap/...`). Para esto puntual, `pull_catalog()` usa la API de
  Discovery vigente hoy: `POST /datamap/api/search/query`, con un
  envoltorio de respuesta distinto (`{"value": [...], "continuationToken":
  ...}`, no el de Atlas) y paginación por cursor en vez de offset. El
  resto del conector (`entity/bulk`, `glossary`) sigue funcionando bajo
  `/catalog/...` sin problema — es solo la búsqueda la que migró de raíz.

**Sigue sin traer**: asignaciones de owner/steward (Purview no expone eso
por Atlas de forma directa) — mismo criterio de honestidad que con
Collibra Responsibility.

### El pull ahora persiste (antes era solo un visor)

Antes, tanto `collibra_pull` como el nuevo `purview_pull` mostraban lo
traído en pantalla (o lo dejaban bajar como CSV) pero no quedaba guardado
en el programa — cerrabas la sesión y había que volver a traerlo todo.

`mvdg/imported.py` (nuevo) guarda lo traído en
`~/.mv_data_governance/importado.json` (mismo patrón que
`curation.py`/`connectors.py`), con un botón **💾 Guardar localmente** en
cada sección de pull. Más importante que el archivo: **lo importado entra
al mismo circuito de gobierno que todo lo demás** — cada término/tabla
guardado aparece en 🖊️ Curaduría, con su origen visible ("⬇️ purview" /
"⬇️ collibra"), como cualquier otra definición pre-establecida esperando
que un Data Owner/Steward la valide. No se lo mete a la fuerza en el
catálogo/glosario de demo (que es un modelo fijo pensado para 4 datasets
sintéticos) — es su propia colección visible, exportable, y con el mismo
tratamiento de responsable.

### qualifiedNames reales (Azure SQL Database) — merge en vez de catálogo fantasma

Antes, TODO dataset se empujaba con un qualifiedName sintético
(`mvdg://dataset`) — Purview lo trata como una entidad totalmente nueva,
sin relación con lo que un scanner nativo ya haya indexado de esa misma
tabla física. Se investigó qué formato de qualifiedName usa cada scanner
nativo de Purview, y el resultado fue desparejo a propósito:

- **Azure SQL Database**: formato **confirmado** —
  `mssql://{server}.database.windows.net/{database}/{schema}/{table}` —
  verificado con un ejemplo antes/después real en "Asset normalization in
  Microsoft Purview Data Map" (Microsoft Learn). `connectors.
  purview_qualified_name(profile, table)` lo arma solo cuando el host de
  tu conexión guardada termina en `.database.windows.net`.
- **SQL Server on-premises, PostgreSQL, MySQL**: Purview tiene scanners
  nativos propios para todos estos, pero Microsoft **no publica** el
  formato exacto de qualifiedName que les asignan (se verificó
  explícitamente: ni el connector doc de on-prem SQL Server ni el de
  PostgreSQL/MySQL lo mencionan). Inventar un patrón acá generaría
  exactamente el catálogo fantasma que esto busca evitar — así que para
  estos motores se sigue usando el identificador sintético. `push_all` y
  `push_catalog` aceptan un `qualified_name_map` opcional; sin él (el
  default), el comportamiento es idéntico al de antes.

### Robustez de red

Antes, un solo error HTTP a mitad de un push (un término, una entidad, un
lote) abortaba TODO sin ningún resumen de qué sí y qué no se mandó.

- **Purview**: `entity/bulk` ahora se banda en lotes de 500 entidades; si
  un lote falla, el resto se sigue mandando igual (el fallo queda en
  `failed_batches`). El push del glosario y las clasificaciones PII
  reportan cada término/request que falló en `failed`, sin frenar el
  resto. `_http_json` reintenta automáticamente ante 429 (Too Many
  Requests) con backoff — respeta el header `Retry-After` si Purview lo
  manda, y si no, backoff exponencial (hasta 3 reintentos).
- **Collibra**: `_push_assets` aplica el mismo criterio — cada asset/
  atributo/relación que falla queda registrado en `failed` (con el nombre
  y el error) sin abortar el resto del catálogo o el glosario.

### Relación columna→tabla en Collibra (opcional, sin adivinar el typeId)

Igual que Purview, las columnas de Collibra quedaban sueltas del dominio,
sin relación explícita a su tabla. Se agregó la creación de esa relación
vía `POST /rest/2.0/relations` (`{sourceId, targetId, typeId}` —
confirmado contra el OpenAPI del Collibra Developer Portal), pero **solo
si** se configura `COLLIBRA_COLUMN_TABLE_RELATION_TYPE_ID`: ese typeId (el
de la relación "Column is part of Table") depende del Operating Model de
cada instancia y Collibra no publica un UUID de fábrica para adivinarlo —
mismo criterio que `COLLIBRA_TABLE_TYPE_ID`/`COLLIBRA_COLUMN_TYPE_ID`. Sin
la variable, el push funciona exactamente igual que antes (sin regresión).

### Simetría de estados: Collibra también recibe Candidate/Accepted

Antes, Purview recibía Draft/Approved reflejando la curaduría real, pero
Collibra no recibía ningún status — quedaba con el default de la
instancia. Ahora `build_term_payloads` manda `statusId`: **Candidate**
(`00000000-0000-0000-0000-000000005008`, el status inicial de todo asset
nuevo en Collibra) para lo sin revisar, **Accepted**
(`00000000-0000-0000-0000-000000005009`, el que ponen los stewards al
aprobar) para lo validado/modificado en 🖊️ Curaduría. Ambos son UUIDs
out-of-the-box documentados por el Collibra Product Resource Center
("Out-of-the-box statuses") — fijos en toda instancia, igual que
`DEFINITION_ATTRIBUTE_TYPE_ID` — y overridables
(`COLLIBRA_CANDIDATE_STATUS_ID`/`COLLIBRA_ACCEPTED_STATUS_ID`) para
instancias con un modelo de statuses distinto.

### Seguridad: contraseñas y login del modo servidor

Dos hallazgos reales de una revisión de seguridad, y lo que se hizo:

- **Contraseñas de conexión guardadas solo en base64**: eso es
  ofuscación, no cifrado — cualquiera con el archivo `conexiones.json`
  puede leerlas. Ahora `mvdg/connectors.py` intenta primero el **keyring
  del sistema operativo** (Windows Credential Manager, macOS Keychain,
  Secret Service de Linux) — ahí la contraseña queda cifrada por el
  propio SO, y el JSON solo guarda una referencia (`secret_backend:
  "keyring"`). Si no hay keyring disponible o utilizable (típico en un
  servidor Linux headless, o en un backend roto — se probó explícitamente
  contra un entorno sin él) cae, con aviso explícito y sin romper el
  guardado, a la ofuscación base64 de antes (`secret_backend:
  "obfuscated"`) — la interfaz nunca finge más seguridad de la que
  realmente hay.
- **Modo servidor sin login**: la lista de "servidores autorizados"
  decide en qué MÁQUINA puede arrancar el programa, no QUIÉN puede entrar
  una vez que ya está arriba — con la lista sola, cualquiera que llegue a
  `host:puerto` en la red de la empresa entraba sin contraseña. Ahora, si
  se define `MVDG_SERVER_PASSWORD`, el modo servidor pide esa contraseña
  compartida antes de mostrar el dashboard (comparación en tiempo
  constante, `hmac.compare_digest`). Sin la variable, el servidor sigue
  funcionando como antes (abierto), con el mismo aviso explícito que ya
  existía para "sin lista de hosts autorizados".

### El techo del glosario clásico de Purview (Unified Catalog)

Advertencia de la auditoría, documentada acá porque es real: los términos
que este conector empuja/trae viajan por la API del **glosario "clásico"**
de Atlas (`/catalog/api/atlas/v2/glossary`). Microsoft está moviendo la
gestión de glosario de negocio hacia el **Unified Catalog** (governance
domains) del portal nuevo de Purview — una API distinta, con su propio
modelo de dominios de gobierno. El override `PURVIEW_API_BASE` (para
instalaciones que ya usan `api.purview-service.microsoft.com` en vez del
`{cuenta}.purview.azure.com` clásico) ya anticipa parte de este cambio de
raíz, pero el glosario clásico sigue siendo la superficie soportada hoy —
si tu organización ya migró por completo al Unified Catalog, confirmá con
tu equipo de Purview si el glosario clásico sigue siendo el destino
correcto antes de depender de este conector en producción.

### Lo que sigue sin poder verificarse (honestidad, no ausencia de esfuerzo)

Ninguno de los dos conectores (push ni pull, Purview ni Collibra) se
probó contra un tenant/instancia real — sigue sin haber uno disponible en
este entorno de desarrollo. Cada endpoint nuevo de esta ronda se verificó
contra documentación oficial (Microsoft Learn, Apache Atlas GitHub,
Collibra Developer Portal, Collibra Product Resource Center) con
ejemplos de request/response reales — no se inventó ningún payload — pero
eso no reemplaza una prueba contra un tenant de verdad. Antes de un push
real: `dry_run=True` primero, después contra una colección/dominio de
prueba, nunca directo a producción.

### Verificación de esta ronda

`tests/test_core.py` suma ~35 tests nuevos: roundtrip HTTP real (servidor
local) para `purview_pull`, persistencia + integración a Curaduría de lo
importado, keyring con fallback (probado explícitamente contra un backend
roto), `purview_qualified_name` para Azure SQL y su ausencia deliberada
para todo lo demás, login del modo servidor, batching + reintento 429 +
aislamiento de fallos por ítem en ambos conectores, y la simetría de
estados en Collibra. `python -m mvdg.selfcheck` suma 4 chequeos nuevos
(40/40 en total).
