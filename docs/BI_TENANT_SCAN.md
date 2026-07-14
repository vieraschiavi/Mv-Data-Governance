# 🌐 Escaneo completo de tenant/sitio — Power BI y Tableau

Además del camino offline (`.pbip` local para Power BI), el programa puede
escanear **todo tu tenant de Power BI** o **todo tu sitio de Tableau** de una
sola vez, vía las APIs oficiales de administración de cada herramienta. Es
**opcional y apagado por defecto**: solo se activa si vos configurás tus
propias credenciales como variables de entorno.

## Reglas de diseño (no negociables, mismas que `docs/IA_EXTERNA.md`)

- **Apagado por defecto.** Sin las variables de entorno cargadas, la pestaña
  muestra un aviso y no hace ninguna llamada — ni siquiera intenta conectarse.
- **Las credenciales las creás y las cargás vos**, como variable de entorno
  en tu propia máquina o servidor. El programa nunca las pide en pantalla,
  nunca las guarda en disco, nunca las manda a ningún lado más que a la API
  oficial de Microsoft/Tableau que corresponde.
  **Nunca las pegues en el chat conmigo ni las subas al repositorio.**
- **Solo se trae metadata** (nombres de datasets/workbooks, columnas,
  medidas/campos calculados con su expresión, relaciones, roles, linaje) —
  **nunca filas de datos reales**. Ni la Scanner API de Power BI ni la
  Metadata API de Tableau devuelven datos de las tablas, por diseño de esas
  APIs.
- Implementado con la librería estándar de Python (`urllib`) — no agrega
  ninguna dependencia nueva al proyecto.

---

## Power BI — Scanner API (tenant completo)

### 1. Variables de entorno

| Variable | Qué es |
|---|---|
| `POWERBI_TENANT_ID` | ID del tenant de Azure AD (Directory ID). |
| `POWERBI_CLIENT_ID` | Application (client) ID del service principal. |
| `POWERBI_CLIENT_SECRET` | Client secret del service principal. **Nunca lo compartas ni lo pegues en el chat.** |

### 2. Cómo crear el service principal

1. En **Azure Portal → Microsoft Entra ID → Registros de aplicaciones**,
   creá una aplicación nueva (o usá una existente). Copiá el **Application
   (client) ID** y el **Directory (tenant) ID**.
2. En **Certificados y secretos**, generá un **Client secret** nuevo y
   copiá su valor (solo se muestra una vez).
3. En el **Panel de administración de Power BI** (powerbi.com → Configuración
   → Portal de administración → Configuración del inquilino), habilitá:
   - **"Permitir que las entidades de servicio usen las API de administrador
     de solo lectura de Power BI"** — agregá el grupo de seguridad que
     contiene tu service principal.
   - (Opcional, recomendado) **"Mejorar las respuestas de las API de
     administrador con metadatos detallados"** y su equivalente para
     DAX/mashup — así el scan trae también las expresiones M (necesarias
     para detectar el origen SQL de cada tabla).
4. Cargá las 3 variables de entorno (paso 1) donde corras el programa.

### 3. Qué hace el escaneo

En la pestaña **🔷 Power BI → 🌐 Tenant completo**, al hacer clic en
"Escanear tenant completo":

1. Pide un token OAuth2 (client credentials) contra Azure AD.
2. Lista todos los workspaces activos del tenant (`admin/groups`).
3. Pide el scan (`admin/workspaces/getInfo`) con linaje, esquema y
   expresiones habilitadas, en lotes de hasta 100 workspaces.
4. Espera a que cada lote termine (`scanStatus`) y trae el resultado
   (`scanResult`).
5. Normaliza cada dataset encontrado a un modelo — catálogo, columnas,
   medidas (DAX), relaciones, roles RLS, reportes, y el origen SQL detectado
   en la expresión M de cada tabla (mismo mecanismo que el camino offline).

> Yo (Claude) no puedo crear tu service principal ni acceder a tu tenant de
> Power BI — es un paso que hacés vos directamente en Azure Portal y en el
> panel de administración de Power BI. El código ya está listo del lado del
> programa para usarlo apenas cargues las variables.

---

## Tableau — Metadata API (sitio completo)

### 1. Variables de entorno

| Variable | Qué es |
|---|---|
| `TABLEAU_SERVER_URL` | URL de tu servidor/pod, ej. `https://10ax.online.tableau.com` o `https://tableau.tuempresa.com`. |
| `TABLEAU_TOKEN_NAME` | Nombre del Personal Access Token (PAT). |
| `TABLEAU_TOKEN_SECRET` | Secreto del PAT. **Nunca lo compartas ni lo pegues en el chat.** |
| `TABLEAU_SITE` | (Opcional) content URL del sitio, si no es el sitio por defecto. |

### 2. Cómo crear el Personal Access Token

1. En Tableau Server/Cloud, andá a tu **Configuración de cuenta** →
   **Personal Access Tokens** → **Crear token nuevo**.
2. Ponele un nombre (ej. `mv-data-governance`) y copiá el **secreto** que se
   muestra — solo se ve una vez.
3. Cargá las 3-4 variables de entorno (paso 1) donde corras el programa.

### 3. Qué hace el escaneo

En la pestaña **📊 Tableau**, al hacer clic en "Escanear sitio completo":

1. Inicia sesión (REST API) con el PAT.
2. Consulta la **Metadata API** (GraphQL) del sitio: todos los workbooks,
   sus datasources publicados, los campos de cada datasource (con la
   fórmula de los calculados) y las tablas de base de datos de las que
   salen.
3. Cierra la sesión (best-effort: si falla, no rompe el escaneo).
4. Normaliza todo a catálogo, diccionario, glosario (cada campo calculado =
   término), linaje (tabla BD → datasource → workbook) y 4 reglas de salud
   del sitio.

> Igual que con Power BI: yo no puedo crear tu Personal Access Token ni
> acceder a tu servidor de Tableau — lo hacés vos directamente en tu cuenta
> de Tableau. El código ya está listo para usarlo apenas cargues las
> variables.

### Nota sobre el esquema de la Metadata API

La consulta GraphQL que usa el programa sigue el esquema publicado por
Tableau (`workbooks → upstreamDatasources → fields/upstreamTables`). No se
probó contra un sitio real de Tableau en el desarrollo de esta función —
está cubierta con tests que simulan la respuesta de la API, pero si tu
versión de Tableau Server difiere en algún campo, puede necesitar un ajuste
puntual en `mvdg/tableau_meta.py` (`_GRAPHQL_QUERY`).

---

## Refactor de medidas/cálculos con IA (opcional, sobre lo opcional)

Con **cualquiera** de los dos escaneos cargados, si además tenés configurada
tu API key de IA externa (`docs/IA_EXTERNA.md` — Claude/ChatGPT/Gemini),
cada medida DAX o campo calculado de Tableau trae un botón para pedirle a
la IA que la audite y proponga una versión mejorada. Se manda solo la
expresión (DAX o fórmula de Tableau) — nunca datos.

## Verificación

`python -m mvdg.selfcheck` incluye dos chequeos ("Power BI tenant-wide" y
"Tableau Metadata API") que confirman, con un transporte HTTP simulado, que
sin credenciales el comportamiento es apagado por defecto y que con
credenciales el flujo completo (autenticación → escaneo → normalización)
funciona de punta a punta.
