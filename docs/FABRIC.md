# Microsoft Fabric — conectar, gobernar y dejar el gobierno adentro de Fabric

Para la empresa cuya **arquitectura de datos es Fabric** (Lakehouse y/o
Warehouse) y que mira todo desde **Power BI**.

Hay **dos formas** de usar MV Data Governance con Fabric, y no compiten:
se eligen según de qué lado del tenant esté parado el que gobierna.

| | **A. Desde afuera** (conector) | **B. Desde adentro** (notebook) |
|---|---|---|
| Quién lo usa | El consultor o el analista, desde su PC | El equipo de datos, dentro del workspace |
| Cómo entra | SQL analytics endpoint (TDS 1433) | Notebook de Fabric, con Spark |
| El dato | Sale del tenant hacia la PC | **Nunca sale de Fabric** |
| El resultado | Tablero, Excel, API local del programa | **Tablas del Lakehouse**, que Power BI lee nativo |
| Cuándo conviene | Relevamiento, diagnóstico, trabajo puntual | Gobierno recurrente, ya productivo |

> **Estado de la verificación.** Las dos formas están implementadas contra
> la documentación oficial de Microsoft (verificada el **2026-09-15**), y
> probadas con tests automáticos del lado del programa. **No se probaron en
> vivo contra un tenant real de Fabric**, porque no hay uno en el entorno de
> desarrollo. Es el mismo criterio de honestidad que usamos con Purview,
> Collibra y Tableau: antes de confiar en la conexión, probala contra el
> tenant real con **"Probar conexión"**. Si algo falla, lo más probable es
> que sea uno de los tres permisos de la sección siguiente.

---

## 0. Lo que TI tiene que habilitar (antes de probar nada)

Esto no es opcional y no se puede resolver del lado del programa. Si algo
de esto falta, la conexión falla con un error de login que **no dice** que
el problema es un permiso.

1. **Setting de tenant** — un admin de Fabric tiene que habilitar
   *"Service principals can use Fabric APIs"* (Developer settings).
   Solo hace falta si vas a conectar con un **service principal** (opción
   recomendada para automatización).
2. **Permiso en el workspace** — el usuario o el service principal necesita
   un rol en el workspace (**Contributor** alcanza) o permiso sobre el item
   puntual (Warehouse / SQL analytics endpoint).
3. **Firewall: puerto 1433 saliente, y tratado como MSSQL/TDS.**
   Este es el que más tiempo hace perder en una red corporativa. Fabric usa
   el protocolo de SQL Server sobre el 1433 — **no es HTTPS**. Un firewall
   con inspección por aplicación que asume HTTPS en ese puerto corta la
   conexión aunque el puerto esté abierto. Documentación de Microsoft:
   *"Don't configure SQL connections to Warehouse as HTTPS traffic on port
   1433"*.

---

## A. Desde afuera — el conector

### A.1 De dónde sale cada dato del formulario

En Fabric: abrí el **Warehouse** o el **SQL analytics endpoint** del
Lakehouse → **Settings** → **SQL endpoint** → copiá el **SQL connection
string**.

| Campo del programa | Qué poner | Ejemplo |
|---|---|---|
| Motor | `Microsoft Fabric (Lakehouse / Warehouse)` | |
| Servidor | el SQL connection string, tal cual | `abc123def.datawarehouse.fabric.microsoft.com` |
| Base | el **nombre del item** (Warehouse o Lakehouse) | `AdiumWarehouse` |
| Usuario | el client ID del service principal, o tu mail corporativo | `a1b2…` / `persona@empresa.com` |
| Contraseña | el **secreto** del service principal (vacío si es interactivo) | |
| Parámetros extra | el modo de autenticación (ver abajo) | `{"auth": "service_principal"}` |

> **El nombre del item no es opcional.** Si la base queda vacía, Fabric te
> conecta a `master`, donde no está ninguna tabla del cliente: se ve como
> "conectó pero no hay datos", que es peor que un error.

### A.2 Autenticación: Fabric **no acepta usuario y contraseña de SQL**

Textual de la documentación: *"SQL Authentication isn't supported"*. Solo
Microsoft Entra ID. Por eso Fabric es un motor aparte y no "un SQL Server
más": si cargás usuario y contraseña como si lo fuera, el programa te lo
dice **antes** de intentar conectarse, en vez de dejarte con un error de
login sin explicación.

Los tres modos van en **Parámetros extra**, como JSON:

```json
{"auth": "service_principal"}
```

| `auth` | Cuándo | Usuario | Contraseña |
|---|---|---|---|
| `service_principal` | Automatización, servidor, uso desatendido | client ID | secreto |
| `interactive` | Una persona en su PC, con MFA | su mail corporativo | *(vacía)* |
| `password` | Último recurso — **exige MFA apagado y sin acceso condicional** | mail | contraseña |

Si no ponés `auth`, se deduce: con secreto cargado → `service_principal`;
sin secreto → `interactive`.

### A.3 Requisito del equipo: ODBC Driver 18

Hace falta el **Microsoft ODBC Driver 18 for SQL Server** (el 17 no tiene
los modos de Entra ID) y el paquete `pyodbc`:

```
pip install pyodbc
```

---

## B. Desde adentro — el notebook de Fabric

La forma que deja el gobierno **donde la organización ya mira**: las 9
tablas de gobierno quedan como **tablas del Lakehouse**, así que Power BI
las consume nativo (DirectLake) sin exportar ni copiar nada, y el dato
nunca sale del tenant.

En un notebook con un **Lakehouse por defecto** asignado (el panel de la
izquierda, el ícono de pin):

```python
%pip install mvdg          # o subí el paquete al entorno del workspace

from mvdg import fabric
r = fabric.gobernar_lakehouse()

print(r["tablas_leidas"])   # {"FactVentas": 120000, "DimCliente": 4300}
print(r["muestreadas"])     # {} = se gobernó sobre las tablas COMPLETAS
print(r["escritas"])        # gobierno_catalog, gobierno_quality_results, ...
```

Eso lee las tablas del Lakehouse, corre el motor de gobierno (catálogo,
diccionario, calidad por las 6 dimensiones DAMA, linaje, políticas y KPIs)
y escribe **9 tablas Delta** con el prefijo `gobierno_`.

### Lo que conviene saber antes de correrlo en producción

- **Mirá antes de publicar.** `fabric.gobernar_lakehouse(escribir=False)`
  devuelve las tablas sin tocar el Lakehouse.
- **Solo tus datos.** Lo que se escribe contiene **exclusivamente** las
  tablas del Lakehouse: ni una fila de los datasets de demostración del
  programa. Un índice de calidad calculado sobre defectos sintéticos no
  sería tu calidad.
- **Sin tope por defecto.** Cada tabla se lee entera; el límite real es la
  memoria del cluster. Si pedís un tope (`muestra=100_000`) y alguna tabla
  se corta, aparece en `r["muestreadas"]` y su total real en
  `r["filas_totales"]` — un perfil parcial nunca se presenta como si fuera
  el total.
- **`overwrite` es el modo por defecto**, así que cada corrida reemplaza el
  gobierno anterior. Es lo que se quiere para una foto vigente; si querés
  histórico, cambiá el prefijo por corrida
  (`prefijo=f"gobierno_{fecha}_"`).
- **Elegir tablas:** `fabric.gobernar_lakehouse(nombres=["FactVentas"])`.

### Después: el tablero

Las tablas `gobierno_*` quedan en el Lakehouse como cualquier otra. Desde
Power BI se conectan igual que el resto del modelo. Las de más uso directo
en un tablero ejecutivo son `gobierno_kpis` (índice de calidad y conteo de
reglas), `gobierno_quality_by_dimension` (las 6 dimensiones DAMA) y
`gobierno_catalog`.

---

## C. La IA de la empresa (Azure OpenAI)

Las sugerencias de corrección del programa son **locales por defecto** y no
mandan nada afuera. Si la empresa ya tiene su propio recurso de **Azure
OpenAI**, se puede usar ese —con lo cual el prompt tampoco sale del tenant—
configurando tres variables:

```
AZURE_OPENAI_API_KEY=<la key del recurso>
AZURE_OPENAI_ENDPOINT=https://<recurso>.openai.azure.com
MVDG_AI_MODEL_AZURE=<nombre del deployment>
```

El **deployment** es el nombre que le puso quien lo creó en Azure, que no
tiene por qué coincidir con el del modelo. Opcional:
`AZURE_OPENAI_API_VERSION` (por defecto `2024-10-21`) si el recurso está
fijado a otra versión.

Aun así, al proveedor solo se le manda **metadato de la falla** (dataset,
columna, dimensión, descripción de la regla, cantidad de filas afectadas):
nunca filas de datos reales.

---

## Resolución de problemas

| Síntoma | Causa más probable |
|---|---|
| `Login failed for user '<token-identified principal>'` | Falta el permiso en el workspace, o el nombre del item (base) no existe |
| Se queda colgado y corta a los 20 s | Firewall: 1433 cerrado, o tratado como HTTPS en vez de MSSQL/TDS |
| `Falta el driver de base de datos` | Falta `pip install pyodbc` o el ODBC Driver 18 |
| El programa rechaza la conexión antes de intentar | Cargaste autenticación SQL: Fabric solo acepta Entra ID (ver A.2) |
| Conectó pero no aparece ninguna tabla | La base quedó vacía y estás en `master` (ver A.1) |
| `No se leyó ninguna fila del Lakehouse` (notebook) | El notebook no tiene Lakehouse por defecto asignado |

## Referencias

- [Connectivity to Fabric Data Warehouse](https://learn.microsoft.com/fabric/data-warehouse/connectivity)
- [Microsoft Entra authentication in Fabric Data Warehouse](https://learn.microsoft.com/fabric/data-warehouse/entra-id-authentication)
- [How to connect to Fabric Data Warehouse](https://learn.microsoft.com/fabric/data-warehouse/how-to-connect)
