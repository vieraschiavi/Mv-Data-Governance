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
