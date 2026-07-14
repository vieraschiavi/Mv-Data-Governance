# ☁️ Conectores a data warehouse / lake de nube — Snowflake, BigQuery, Databricks, Synapse

Además de los 4 motores de base de datos "clásicos" (PostgreSQL, MySQL,
SQL Server, Oracle) y SQLite, la pestaña **🔎 Mis datos → Base de datos**
se conecta directo a los data warehouse/lake de nube más usados en
gobierno de datos empresarial: **Snowflake**, **Google BigQuery**,
**Databricks SQL Warehouse** y **Azure Synapse Analytics** (SQL pool).

## Reglas de diseño (no negociables, mismas que `docs/BI_TENANT_SCAN.md`)

- **Las credenciales las cargás vos**, en un formulario que se guarda
  **solo en tu equipo** (`~/.mv_data_governance/conexiones.json`), igual
  que con los motores clásicos. El programa nunca manda tus credenciales a
  ningún lado más que al warehouse que vos elegiste.
  **Nunca las pegues en el chat conmigo.**
- Implementado contra el **dialecto SQLAlchemy oficial y documentado** de
  cada proveedor (`snowflake-sqlalchemy`, `sqlalchemy-bigquery`,
  `databricks-sqlalchemy`) — **no probado contra una cuenta real** de
  ninguna de las tres nubes (no hay credenciales de prueba disponibles en
  este entorno de desarrollo). Antes de confiar en un motor nuevo, usá el
  botón **"🔌 Probar conexión"** contra tu cuenta real; si algo no conecta,
  es la primera señal de que el dialecto necesita un ajuste puntual.
- Los drivers (`pip install ...`) **no vienen instalados por defecto** —
  se instalan solo si vas a usar ese motor en particular, para no inflar
  el paquete base con dependencias que la mayoría no necesita.

---

## Por qué estos 3 no usan servidor + puerto + usuario + contraseña

Los 5 motores clásicos comparten el mismo modelo de conexión
(host, puerto, base, usuario, contraseña). Snowflake, BigQuery y Databricks
**no** — cada uno tiene su propio esquema:

| Motor | Se identifica por | No por |
|---|---|---|
| **Snowflake** | cuenta (`xy12345.us-east-1`) + warehouse + rol | host/puerto tradicional |
| **BigQuery** | proyecto GCP + dataset + credenciales de service account | usuario/contraseña |
| **Databricks** | hostname del workspace + HTTP path del SQL Warehouse + token | usuario/contraseña (el token hace de ambos) |

En vez de armar un formulario distinto para cada uno, esos parámetros
propios se cargan como un **campo de texto en formato JSON** (`extra`) que
aparece en el formulario apenas elegís uno de estos 3 motores. El programa
te muestra un ejemplo de la forma esperada como ayuda.

**Azure Synapse** es la excepción: su SQL pool (dedicado o serverless) es
**compatible por protocolo con SQL Server**, así que reutiliza el mismo
driver (`mssql+pyodbc`) y el modelo clásico de servidor+puerto+usuario+
contraseña — no necesita `extra`.

---

## Snowflake

| Campo del formulario | Va a parar a |
|---|---|
| Usuario / Contraseña | login de Snowflake |
| Base de datos | nombre de la base |
| `extra` (JSON) | `account`, `warehouse`, `role`, `schema` |

```json
{"account": "xy12345.us-east-1", "warehouse": "COMPUTE_WH", "role": "SYSADMIN", "schema": "PUBLIC"}
```

Driver: `pip install snowflake-sqlalchemy`

## Google BigQuery

BigQuery no usa usuario/contraseña — se autentica con **Application
Default Credentials** (si ya corriste `gcloud auth application-default
login` en tu máquina) o con la ruta a un archivo de **service account**
JSON.

| Campo del formulario | Va a parar a |
|---|---|
| `extra` (JSON) | `project`, `dataset`, `credentials_path` (opcional) |

```json
{"project": "mi-proyecto-gcp", "dataset": "mi_dataset", "credentials_path": "/ruta/a/service-account.json"}
```

Si omitís `credentials_path`, usa las Application Default Credentials del
entorno. **El archivo de service account nunca se sube a ningún lado** —
se lee localmente desde la ruta que indiques, en tu propio equipo.

Driver: `pip install sqlalchemy-bigquery`

## Databricks SQL Warehouse

| Campo del formulario | Va a parar a |
|---|---|
| Contraseña | el **Personal Access Token** (Databricks lo trata como password) |
| `extra` (JSON) | `server_hostname`, `http_path`, `catalog`, `schema` |

```json
{"server_hostname": "adb-1234567890.azuredatabricks.net", "http_path": "/sql/1.0/warehouses/abc123", "catalog": "main", "schema": "default"}
```

El PAT se creá en Databricks: **Configuración de usuario → Developer →
Access tokens → Generate new token**. El `http_path` lo copiás del SQL
Warehouse: **SQL Warehouses → tu warehouse → Connection details**.

Driver: `pip install databricks-sqlalchemy`

## Azure Synapse Analytics

Mismo formulario que SQL Server clásico — servidor
(`tuworkspace.sql.azuresynapse.net`), puerto `1433`, base, usuario y
contraseña (o Azure AD, si tu driver ODBC está configurado para eso).

Driver: `pip install pyodbc` (el mismo que SQL Server)

---

## Qué pasa una vez conectado

Igual que con los motores clásicos: **"🔌 Probar conexión"** valida
credenciales con un `SELECT 1`, y una vez guardada la conexión el programa
lista las tablas/esquemas disponibles y te deja **traer una tabla o el
resultado de una consulta SELECT** al mismo motor de perfilado, detección
de duplicados y sugerencia de reglas que usa para archivos CSV/Excel — el
warehouse de nube se gobierna exactamente igual que un archivo subido a
mano.

## Por qué no hay un "ejemplo incluido" para este módulo

A diferencia de Power BI o Tableau (donde pude incluir un modelo real
descargado con licencia MIT, o escribir un archivo de ejemplo offline),
los data warehouse de nube **solo existen como una conexión en vivo** a tu
cuenta — no hay un archivo portable que represente "un Snowflake" o "un
BigQuery" de la misma forma que un `.pbip` o un `.twb`. Por eso este
módulo no trae modo ejemplo: la única forma de probarlo es contra tu
propia cuenta de nube.

## Verificación

`python -m mvdg.selfcheck` incluye el chequeo **"Conectores a base de
datos (SQL + cloud DW/lake)"**, que confirma que los 9 motores están
registrados (5 clásicos + SQLite + Synapse + los 3 de nube) y que
`build_url()` arma una URL SQLAlchemy sintácticamente correcta para cada
uno de los 3 motores de nube a partir de un `extra` de ejemplo — sin
conectarse a ninguna cuenta real.
