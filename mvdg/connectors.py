# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Conectores directos a bases de datos.

Además de CSV/Excel, MV Data Governance se conecta directo a cualquier base de
datos vía SQLAlchemy: PostgreSQL, MySQL/MariaDB, SQL Server, Oracle, SQLite,
y los data warehouse/lake de nube más usados — Snowflake, Google BigQuery,
Databricks SQL Warehouse, Azure Synapse (SQL pool, vía el mismo driver que
SQL Server, con el que es compatible por protocolo) y Microsoft Fabric
(Lakehouse SQL analytics endpoint y Warehouse, con Entra ID — ver la sección
"Microsoft Fabric" más abajo, que NO es un SQL Server más). El usuario carga
servidor, puerto, base, usuario y contraseña (o los parámetros que
correspondan a cada nube — ver ``extra`` más abajo), prueba la conexión,
lista las tablas y trae una tabla (o el resultado de una consulta) al mismo
motor de gobierno que usa para archivos.

Las conexiones se guardan en disco y persisten entre sesiones:
    ~/.mv_data_governance/conexiones.json
La contraseña (o el token de acceso, según el motor) se guarda solo si el
usuario lo pide. Es un almacenamiento LOCAL, en el equipo del usuario —
igual que cualquier cliente de base de datos de escritorio.

Cómo se protege la contraseña guardada: se intenta primero el keyring del
sistema operativo (Windows Credential Manager, macOS Keychain, o el Secret
Service de Linux vía D-Bus si hay sesión de escritorio) — ahí queda cifrada
por el propio SO, este programa nunca ve ni maneja la clave de cifrado. Si
no hay keyring disponible o utilizable (típico en un servidor Linux
headless sin sesión de escritorio, o en modo servidor) se cae, con aviso
explícito y sin romper el guardado, a una ofuscación local en base64 — que
NO es cifrado real, solo evita que la contraseña quede a simple vista en el
archivo. Cada conexión guardada registra con cuál de los dos quedó
protegida (``secret_backend``), así la interfaz nunca finge más seguridad
de la que realmente hay.

Sobre Snowflake / BigQuery / Databricks: a diferencia de los motores SQL
"clásicos", estos tres NO usan el modelo simple host+puerto+usuario+
contraseña — cada uno tiene su propio esquema de conexión (cuenta +
warehouse en Snowflake, proyecto + credenciales de service account en
BigQuery, hostname + HTTP path + token en Databricks). En vez de armar un
formulario distinto por cada uno, esos parámetros extra se cargan como un
dict (``profile["extra"]``) — en la interfaz, un campo de texto en formato
JSON. Implementado contra el dialecto SQLAlchemy oficial y documentado de
cada proveedor (``snowflake-sqlalchemy``, ``sqlalchemy-bigquery``,
``databricks-sqlalchemy``) — igual que con la Metadata API de Tableau, esto
NO se probó contra una cuenta real de ninguna de las tres nubes (no
disponible en este entorno de desarrollo); antes de confiar en un motor
nuevo, usá el botón "Probar conexión" contra tu cuenta real.
"""
from __future__ import annotations

import base64
import json
import os
import re
import uuid

import pandas as pd

from .clients import data_dir  # reutiliza ~/.mv_data_governance

# motor -> etiqueta, driver SQLAlchemy, puerto por defecto, paquete pip del driver
ENGINES: dict[str, dict] = {
    "postgresql": {"label": "PostgreSQL", "driver": "postgresql+psycopg2",
                   "port": 5432, "pip": "psycopg2-binary"},
    "mysql": {"label": "MySQL / MariaDB", "driver": "mysql+pymysql",
              "port": 3306, "pip": "pymysql"},
    "sqlserver": {"label": "SQL Server", "driver": "mssql+pyodbc",
                  "port": 1433, "pip": "pyodbc"},
    "oracle": {"label": "Oracle", "driver": "oracle+oracledb",
               "port": 1521, "pip": "oracledb"},
    "sqlite": {"label": "SQLite (archivo)", "driver": "sqlite",
               "port": None, "pip": None},
    "synapse": {"label": "Azure Synapse (SQL pool)", "driver": "mssql+pyodbc",
               "port": 1433, "pip": "pyodbc"},
    "fabric": {"label": "Microsoft Fabric (Lakehouse / Warehouse)",
               "driver": "mssql+pyodbc", "port": 1433, "pip": "pyodbc"},
    "snowflake": {"label": "Snowflake", "driver": "snowflake",
                 "port": None, "pip": "snowflake-sqlalchemy"},
    "bigquery": {"label": "Google BigQuery", "driver": "bigquery",
                "port": None, "pip": "sqlalchemy-bigquery"},
    "databricks": {"label": "Databricks SQL Warehouse", "driver": "databricks",
                   "port": None, "pip": "databricks-sqlalchemy"},
}

# motores cuya conexión no sigue el modelo host+puerto+usuario+contraseña —
# usan ``profile["extra"]`` (dict) para sus parámetros propios.
#
# Fabric entra acá aunque hable TDS como SQL Server: el puerto es fijo (1433,
# no se elige) y el MODO DE AUTENTICACIÓN es un parámetro más, porque Fabric
# no acepta usuario+contraseña de SQL. Al estar en esta lista, el formulario
# de Mis datos ya muestra host + base + usuario + secreto + el JSON de
# ``extra`` — que es exactamente lo que Fabric pide — sin tocar la UI.
CLOUD_ENGINES = ("snowflake", "bigquery", "databricks", "fabric")

# ejemplo de "extra" por motor cloud, para mostrar como placeholder en la UI
# y en la documentación — no son valores reales.
EXTRA_EXAMPLE: dict[str, dict] = {
    "snowflake": {"account": "xy12345.us-east-1", "warehouse": "COMPUTE_WH",
                 "role": "SYSADMIN", "schema": "PUBLIC"},
    "bigquery": {"project": "mi-proyecto-gcp", "dataset": "mi_dataset",
                "credentials_path": "/ruta/a/service-account.json"},
    "databricks": {"server_hostname": "adb-1234567890.azuredatabricks.net",
                   "http_path": "/sql/1.0/warehouses/abc123", "catalog": "main",
                   "schema": "default"},
    "fabric": {"auth": "service_principal", "tenant_id": "00000000-0000-0000-0000-000000000000"},
}

# Tope POR DEFECTO al traer una tabla: 0 = SIN TOPE, se trae la tabla
# entera. Historia: primero fue un máximo duro de 100.000 (quien tenía tres
# millones de filas gobernaba un pedazo sin saberlo), después un default de
# 100.000 que se podía subir. Pedido del dueño: "sin límite de tamaño cada
# módulo". El límite real pasa a ser la memoria de la máquina. Quien quiera
# un tope lo pide explícito, y si recorta, ``aviso_recorte`` da el total
# real (COUNT) para que nunca haya un recorte mudo.
MAX_ROWS = 0


def _file() -> str:
    return os.path.join(data_dir(), "conexiones.json")


def _obfuscate(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def _deobfuscate(text: str) -> str:
    try:
        return base64.b64decode(text.encode("ascii")).decode("utf-8")
    except Exception:
        return ""


# ------------------------------------------------------------ keyring del SO
_KEYRING_SERVICE = "mv_data_governance"
_keyring_ok_cache: bool | None = None


def _keyring_usable() -> bool:
    """¿El keyring del sistema operativo funciona de verdad acá? Se prueba
    una vez por proceso (set + get + delete de una clave descartable) y se
    cachea el resultado.

    El except es a propósito ``except BaseException`` y no ``except
    Exception``: en un Linux headless sin backend de secretos, el binding
    de 'cryptography' que usa el backend SecretService puede levantar un
    ``pyo3_runtime.PanicException`` — que en pyo3 NO hereda de Exception.
    Si no se ataja acá, el programa se caería solo por no tener keyring
    del SO disponible, algo que tiene que ser opcional y nunca fatal."""
    global _keyring_ok_cache
    if _keyring_ok_cache is not None:
        return _keyring_ok_cache
    try:
        import keyring
        probe_user = "__mvdg_probe__"
        keyring.set_password(_KEYRING_SERVICE, probe_user, "ok")
        ok = keyring.get_password(_KEYRING_SERVICE, probe_user) == "ok"
        try:
            keyring.delete_password(_KEYRING_SERVICE, probe_user)
        except Exception:
            pass
        _keyring_ok_cache = ok
    except BaseException:
        _keyring_ok_cache = False
    return _keyring_ok_cache


def _keyring_set(conn_id: str, secret: str) -> bool:
    """Intenta guardar en el keyring del SO. Devuelve si funcionó."""
    if not _keyring_usable():
        return False
    try:
        import keyring
        keyring.set_password(_KEYRING_SERVICE, conn_id, secret)
        return True
    except BaseException:
        return False


def _keyring_get(conn_id: str) -> str:
    if not _keyring_usable():
        return ""
    try:
        import keyring
        return keyring.get_password(_KEYRING_SERVICE, conn_id) or ""
    except BaseException:
        return ""


def _keyring_delete(conn_id: str) -> None:
    if not _keyring_usable():
        return
    try:
        import keyring
        keyring.delete_password(_KEYRING_SERVICE, conn_id)
    except Exception:
        pass


# ------------------------------------------------------------- persistencia
def load_connections() -> list[dict]:
    path = _file()
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _write(conns: list[dict]) -> None:
    tmp = _file() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(conns, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, _file())


def save_connection(profile: dict, save_password: bool = True) -> dict:
    """Crea o actualiza una conexión guardada (por ``conn_id``).

    La contraseña intenta guardarse en el keyring del sistema operativo
    primero; si no está disponible, cae a la ofuscación base64 local. El
    campo ``secret_backend`` deja registrado con cuál quedó, para que la
    interfaz lo muestre tal cual es (nunca "cifrado" si en realidad es
    solo ofuscado)."""
    conns = load_connections()
    cid = profile.get("conn_id") or uuid.uuid4().hex[:12]
    password = profile.get("password", "")
    secret_backend = ""
    password_enc = ""
    if save_password and password:
        if _keyring_set(cid, password):
            secret_backend = "keyring"
        else:
            password_enc = _obfuscate(password)
            secret_backend = "obfuscated"
    elif not save_password:
        # se pide NO guardar contraseña: limpiamos cualquier resto previo
        # (de una edición anterior con save_password=True) del keyring.
        _keyring_delete(cid)
    stored = {
        "conn_id": cid,
        "name": profile.get("name", "").strip(),
        "engine": profile.get("engine", "postgresql"),
        "host": profile.get("host", "").strip(),
        "port": profile.get("port"),
        "database": profile.get("database", "").strip(),
        "user": profile.get("user", "").strip(),
        "save_password": bool(save_password),
        "password_enc": password_enc,
        "secret_backend": secret_backend,
        "extra": profile.get("extra") or {},
    }
    for i, c in enumerate(conns):
        if c.get("conn_id") == cid:
            conns[i] = stored
            _write(conns)
            return stored
    conns.append(stored)
    _write(conns)
    return stored


def delete_connection(conn_id: str) -> bool:
    conns = load_connections()
    rest = [c for c in conns if c.get("conn_id") != conn_id]
    if len(rest) == len(conns):
        return False
    _keyring_delete(conn_id)
    _write(rest)
    return True


def stored_password(profile: dict) -> str:
    """Contraseña guardada de una conexión persistida — del keyring del SO
    si quedó ahí, o desofuscada del campo base64 si ese fue el respaldo
    usado al guardarla (compatibilidad con conexiones guardadas antes de
    tener soporte de keyring, que no tienen ``secret_backend``)."""
    if not profile.get("save_password"):
        return ""
    backend = profile.get("secret_backend") or "obfuscated"
    if backend == "keyring":
        return _keyring_get(profile.get("conn_id", ""))
    return _deobfuscate(profile.get("password_enc", ""))


def secret_backend_label(profile: dict) -> str:
    """Para mostrar en la interfaz cómo quedó protegida esta contraseña —
    nunca decimos "cifrado" cuando en realidad es solo ofuscación."""
    if not profile.get("save_password"):
        return "none"
    return profile.get("secret_backend") or "obfuscated"


# ----------------------------------------------------------- Microsoft Fabric
# Fabric (Lakehouse SQL analytics endpoint y Warehouse) habla el MISMO
# protocolo que SQL Server —TDS sobre el puerto 1433— pero con una diferencia
# que rompe todo si se la ignora:
#
#   FABRIC NO ACEPTA AUTENTICACIÓN SQL. Ni usuario+contraseña de base, ni
#   nada que no sea Microsoft Entra ID.
#
# Textual de la documentación ("Considerations and limitations"): «SQL
# Authentication isn't supported». Por eso este motor va aparte de
# "sqlserver" en vez de reusarlo: alguien que cargue el host de Fabric como
# si fuera SQL Server carga usuario y contraseña, y recibe un error de login
# que no dice en ningún lado que el problema es el MODO de autenticación.
# Acá se elige el modo explícitamente y, si falta, se explica por qué.
#
# Los tres modos y el nombre EXACTO que espera el driver salen de la tabla
# de "Microsoft Entra Authentication in Fabric Data Warehouse" (ODBC):
#   DRIVER={ODBC Driver 18 for SQL Server};SERVER=<conn string>;
#   DATABASE=<DBName>;UID=<Client_ID@domain>;PWD=<Secret>;
#   Authentication=ActiveDirectoryServicePrincipal
#
# Verificado contra Microsoft Learn el 2026-09-15 (docs actualizadas el
# 2026-09-09) — mismo criterio de honestidad que Purview/Collibra/Tableau:
# está implementado según la documentación oficial, NO probado en vivo
# contra un tenant real de Fabric (no hay uno en este entorno). Antes de
# confiar en él, usá "Probar conexión" contra el tenant del cliente.
_FABRIC_AUTH = {
    "service_principal": "ActiveDirectoryServicePrincipal",
    "interactive": "ActiveDirectoryInteractive",
    "password": "ActiveDirectoryPassword",
}
# "Only ODBC 18 or higher versions are supported" — los modos de Entra ID
# de arriba no existen en el Driver 17.
FABRIC_ODBC_DRIVER = "ODBC Driver 18 for SQL Server"
FABRIC_HOST_SUFFIX = "datawarehouse.fabric.microsoft.com"
FABRIC_PORT = 1433


def _fabric_host(host: str) -> str:
    """El "SQL connection string" que da el portal de Fabric, normalizado.

    El portal lo da pelado (``<guid>.datawarehouse.fabric.microsoft.com``),
    pero se copia y pega también desde SSMS o desde un ejemplo de la doc,
    donde aparece como ``tcp:<host>,1433``. Las dos formas describen el
    mismo servidor; sin limpiarlas, el driver intenta resolver un host que
    incluye el prefijo y devuelve un error de red que no se parece en nada
    a "pegaste el puerto adentro del nombre"."""
    limpio = (host or "").strip()
    if limpio.lower().startswith("tcp:"):
        limpio = limpio[4:]
    if "," in limpio:                      # "host,1433" -> "host"
        limpio = limpio.split(",", 1)[0]
    return limpio.strip().rstrip("/")


def _fabric_url(profile: dict, pwd: str | None, extra: dict):
    from sqlalchemy.engine import URL

    modo = str(extra.get("auth") or "").strip().lower()
    if not modo:
        # Sin modo elegido se deduce del dato que haya: con secreto cargado,
        # lo normal es un service principal (automatización); sin secreto,
        # solo puede ser interactivo (el navegador pide las credenciales).
        modo = "service_principal" if pwd else "interactive"
    if modo not in _FABRIC_AUTH:
        raise ValueError(
            "Modo de autenticación no válido para Microsoft Fabric: "
            f"{modo!r}. Fabric NO acepta autenticación SQL (usuario y "
            "contraseña de base de datos): solo Microsoft Entra ID. Poné "
            f'"auth" en uno de {sorted(_FABRIC_AUTH)} dentro de los '
            "parámetros extra de la conexión.")

    host = _fabric_host(profile.get("host", ""))
    query = {
        "driver": FABRIC_ODBC_DRIVER,
        "Authentication": _FABRIC_AUTH[modo],
        "Encrypt": "yes",
        "TrustServerCertificate": "no",
    }
    # El modo interactivo abre el diálogo de Entra (con MFA si el tenant lo
    # exige): mandar una contraseña ahí no aporta nada y deja un secreto
    # viajando de más.
    secreto = None if modo == "interactive" else (pwd or None)
    return URL.create(
        "mssql+pyodbc",
        username=profile.get("user") or None,
        password=secreto,
        host=host or None,
        port=FABRIC_PORT,
        # El nombre del item (warehouse o lakehouse) es el "Initial Catalog".
        # Sin él, Fabric conecta a `master`, donde no están las tablas del
        # cliente y no se puede crear nada — se ve como "conectó pero no hay
        # datos", que es peor que un error.
        database=profile.get("database") or None,
        query=query,
    )


# -------------------------------------------------------------------- URL
def build_url(profile: dict, password: str | None = None):
    """Arma la URL SQLAlchemy. Para SQLite, ``database`` es la ruta al archivo.

    Snowflake/BigQuery/Databricks no siguen el modelo host+puerto+usuario+
    contraseña — leen sus parámetros propios de ``profile["extra"]`` (ver
    ``EXTRA_EXAMPLE`` para la forma esperada de cada uno)."""
    from sqlalchemy.engine import URL

    engine_key = profile.get("engine")
    eng = ENGINES.get(engine_key)
    if eng is None:
        raise ValueError(f"Motor desconocido: {engine_key}")
    if engine_key == "sqlite":
        return f"sqlite:///{profile.get('database', '')}"

    pwd = password if password is not None else stored_password(profile)
    extra = profile.get("extra") or {}

    if engine_key == "snowflake":
        query = {k: v for k, v in (("warehouse", extra.get("warehouse")),
                                   ("role", extra.get("role"))) if v}
        database = profile.get("database") or None
        schema = extra.get("schema")
        db_part = f"{database}/{schema}" if database and schema else database
        return URL.create("snowflake", username=profile.get("user") or None,
                          password=pwd or None, host=extra.get("account") or None,
                          database=db_part, query=query)

    if engine_key == "bigquery":
        # bigquery://project/dataset — la autenticación va aparte, vía
        # GOOGLE_APPLICATION_CREDENTIALS o credentials_path en create_engine().
        project = extra.get("project") or profile.get("database") or ""
        dataset = extra.get("dataset") or ""
        return f"bigquery://{project}/{dataset}" if dataset else f"bigquery://{project}"

    if engine_key == "databricks":
        query = {"http_path": extra.get("http_path", "")}
        for k in ("catalog", "schema"):
            if extra.get(k):
                query[k] = extra[k]
        return URL.create("databricks", username="token", password=pwd or None,
                          host=extra.get("server_hostname") or profile.get("host") or None,
                          query=query)

    if engine_key == "fabric":
        return _fabric_url(profile, pwd, extra)

    return URL.create(
        eng["driver"],
        username=profile.get("user") or None,
        password=pwd or None,
        host=profile.get("host") or None,
        port=int(profile["port"]) if profile.get("port") else eng["port"],
        database=profile.get("database") or None,
    )


# Timeout de conexión (segundos) por familia de driver -- todos los
# conectores HTTP del motor (Purview, Collibra, Azure, Tableau, Power BI,
# IA) ya tienen el suyo; este era el único que corría sin ninguno. Un host
# inalcanzable con firewall silencioso (típico en una red corporativa)
# colgaba el hilo indefinidamente al "Probar conexión" en vez de fallar
# con un mensaje. Cada driver usa su propio nombre de parámetro -- se
# verificó cada uno instalando el paquete real, no de memoria.
_TIMEOUT_SEGUNDOS = 20
_CONNECT_ARGS_POR_MOTOR = {
    "postgresql": {"connect_timeout": _TIMEOUT_SEGUNDOS},   # libpq estándar
    "mysql": {"connect_timeout": _TIMEOUT_SEGUNDOS},         # pymysql
    "sqlserver": {"timeout": _TIMEOUT_SEGUNDOS},             # pyodbc (login timeout)
    "synapse": {"timeout": _TIMEOUT_SEGUNDOS},               # mismo driver que sqlserver
    "fabric": {"timeout": _TIMEOUT_SEGUNDOS},                # pyodbc, igual que sqlserver
    "oracle": {"tcp_connect_timeout": _TIMEOUT_SEGUNDOS},    # python-oracledb
    # sqlite: sin red, no aplica. snowflake/bigquery/databricks: SDKs
    # propios con su propia autenticación -- forzar connect_args acá
    # arriesga romper esos dialectos por un kwarg que no esperan.
}


def _engine(profile: dict, password: str | None = None):
    from sqlalchemy import create_engine
    kwargs = {"pool_pre_ping": True}
    motor = profile.get("engine")
    if motor == "bigquery":
        creds = (profile.get("extra") or {}).get("credentials_path")
        if creds:
            kwargs["credentials_path"] = creds
    connect_args = _CONNECT_ARGS_POR_MOTOR.get(motor)
    if connect_args:
        kwargs["connect_args"] = connect_args
    return create_engine(build_url(profile, password), **kwargs)


# --------------------------------------------------------------- operaciones
def test_connection(profile: dict, password: str | None = None) -> tuple[bool, str]:
    """Devuelve (ok, mensaje). No lanza: reporta el error como texto."""
    try:
        from sqlalchemy import text
    except ImportError:
        return False, "SQLAlchemy no está instalado (pip install sqlalchemy)."
    try:
        eng = _engine(profile, password)
        with eng.connect() as con:
            con.execute(text("SELECT 1"))
        return True, "Conexión exitosa."
    except ModuleNotFoundError as exc:
        pip = ENGINES.get(profile.get("engine"), {}).get("pip")
        extra = f" Instalá el driver: pip install {pip}." if pip else ""
        return False, f"Falta el driver de base de datos.{extra} ({exc})"
    except Exception as exc:  # noqa: BLE001 - queremos el mensaje al usuario
        return False, f"{type(exc).__name__}: {exc}"


def list_tables(profile: dict, password: str | None = None) -> list[str]:
    from sqlalchemy import inspect
    insp = inspect(_engine(profile, password))
    tables = list(insp.get_table_names())
    try:
        for schema in insp.get_schema_names():
            if schema in ("information_schema", "pg_catalog", "sys"):
                continue
            for t in insp.get_table_names(schema=schema):
                q = f"{schema}.{t}"
                if q not in tables and t not in tables:
                    tables.append(q)
    except Exception:
        pass
    return tables


def list_columns(profile: dict, table: str, password: str | None = None) -> list[str]:
    """Nombres de columnas de una tabla, SOLO metadata (no trae ni una fila
    de datos) — para armar glosario/diccionario desde el esquema sin tocar
    el contenido. Acepta "tabla" o "schema.tabla" (como ``list_tables``)."""
    from sqlalchemy import inspect
    insp = inspect(_engine(profile, password))
    if "." in table:
        schema, name = table.split(".", 1)
        cols = insp.get_columns(name, schema=schema)
    else:
        cols = insp.get_columns(table)
    return [c["name"] for c in cols]


def _leer_sql(sql: str, eng, limit: int) -> pd.DataFrame:
    """Ejecuta la consulta trayendo COMO MUCHO ``limit`` filas (0 = todas).

    El bug que cierra: antes esto era ``pd.read_sql(sql, eng).head(limit)``.
    O sea que traía la tabla ENTERA a memoria y recién después recortaba —
    el tope no protegía nada, solo decidía cuánto se mostraba. Sobre una
    tabla de diez millones de filas, pedir "las primeras mil" se llevaba
    las diez millones puestas primero.

    Con ``chunksize`` el driver usa un cursor del lado del servidor y se
    corta apenas se juntan las filas pedidas: nunca entra a memoria más de
    lo necesario, y funciona igual en los nueve motores soportados sin
    escribir un LIMIT/TOP/FETCH FIRST distinto para cada dialecto.
    """
    if limit <= 0:
        return pd.read_sql(sql, eng)
    trozos, total = [], 0
    for trozo in pd.read_sql(sql, eng, chunksize=min(limit, 50_000)):
        trozos.append(trozo)
        total += len(trozo)
        if total >= limit:
            break
    if not trozos:
        return pd.read_sql(sql, eng).head(0)   # DataFrame vacío CON columnas
    return pd.concat(trozos, ignore_index=True).head(limit)


def _quote_ident(eng, name: str) -> str:
    """Cita un identificador (tabla, columna) con las reglas del motor
    REAL, vía el preparer de SQLAlchemy -- no un f-string a mano.

    Esto es lo que cierra una inyección real: antes, un nombre de tabla
    con un punto (p.ej. ``"public.clientes; DROP TABLE clientes;--"``,
    que puede llegar tal cual desde /api/ingenieria/sql/analizar) se
    partía en schema/nombre y se pegaba SIN comillas en el SQL. El
    preparer conoce el caracter de cita de cada uno de los 9 motores
    soportados y duplica/escapa cualquier comilla embebida en el nombre
    real -- que un f-string nunca hacía."""
    return eng.dialect.identifier_preparer.quote(name)


def _ref_tabla(eng, table: str) -> str:
    if "." in table:
        schema, name = table.split(".", 1)
        return f"{_quote_ident(eng, schema)}.{_quote_ident(eng, name)}"
    return _quote_ident(eng, table)


def _tope(limit) -> int:
    """``None``/0/negativo = sin tope (0). Cualquier otro número, tal cual."""
    return max(0, int(limit or 0))


def load_table(profile: dict, table: str, limit: int | None = MAX_ROWS,
               password: str | None = None) -> pd.DataFrame:
    """Trae una tabla a un DataFrame. Por defecto (y con ``limit`` 0 o
    ``None``) trae la tabla ENTERA: no hay tope de filas."""
    eng = _engine(profile, password)
    return _leer_sql(f"SELECT * FROM {_ref_tabla(eng, table)}", eng, _tope(limit))


# Palabras de escritura/DDL que NO tienen que aparecer en una consulta que
# se dice de solo lectura. Es una lista negra, no un parser SQL real -- no
# reemplaza que la conexión que configura el cliente use un usuario de
# base de datos de SOLO LECTURA (recomendado en docs/BI_INTEGRATION.md);
# esto achica la superficie de ataque, no la cierra del todo. \b evita
# falsos positivos contra columnas como "created_at"/"delete_flag" (el
# guion bajo es caracter de palabra, así que no hay borde ahí), a costa de
# poder rechazar una consulta legitima si el texto buscado dentro de un
# literal contiene una de estas palabras (p.ej. WHERE texto LIKE '%into%')
# -- un falso rechazo es mucho mejor que dejar pasar un DELETE.
_PALABRAS_DE_ESCRITURA = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|create|grant|revoke|"
    r"exec|execute|merge|call|into)\b", re.IGNORECASE)


def _validar_lectura(sql: str) -> str:
    """Devuelve la consulta limpia (sin ``;`` final) o lanza ValueError si no
    es de solo lectura. Ver ``run_query``."""
    limpio = sql.strip()
    if not limpio.lower().startswith(("select", "with")):
        raise ValueError("Solo se permiten consultas de lectura (SELECT / WITH).")
    sin_punto_final = limpio[:-1].strip() if limpio.endswith(";") else limpio
    if ";" in sin_punto_final:
        raise ValueError("No se permite más de una sentencia por consulta.")
    if _PALABRAS_DE_ESCRITURA.search(limpio):
        raise ValueError("Solo se permiten consultas de lectura (SELECT / WITH).")
    return sin_punto_final


def run_query(profile: dict, sql: str, limit: int | None = MAX_ROWS,
              password: str | None = None) -> pd.DataFrame:
    """Ejecuta una consulta SELECT/WITH de solo lectura. Por defecto (y con
    ``limit`` 0 o ``None``) devuelve TODAS las filas.

    El chequeo de antes (¿"empieza con select o with"?) no alcanza: un CTE
    de escritura -- ``WITH x AS (DELETE FROM t RETURNING *) SELECT * FROM
    x`` -- empieza con "with" y borra datos igual. Ahora se rechaza
    cualquier palabra de escritura en TODA la consulta (no solo el
    inicio) y cualquier sentencia apilada con ";"."""
    limpio = _validar_lectura(sql)
    return _leer_sql(limpio, _engine(profile, password), _tope(limit))


def total_filas(profile: dict, *, table: str | None = None, sql: str | None = None,
                password: str | None = None) -> int:
    """Cuántas filas tiene de verdad la tabla (o el resultado de la consulta):
    un ``COUNT(*)`` del lado del motor, sin traer los datos.

    La consulta pasa por la MISMA validación de solo lectura que
    ``run_query`` antes de envolverse en el COUNT. El alias de la subconsulta
    va sin ``AS`` porque Oracle no lo acepta en un alias de tabla."""
    eng = _engine(profile, password)
    if table:
        conteo = f"SELECT COUNT(*) FROM {_ref_tabla(eng, table)}"
    elif sql:
        conteo = f"SELECT COUNT(*) FROM ({_validar_lectura(sql)}) mvdg_conteo"
    else:
        raise ValueError("Falta la tabla o la consulta a contar.")
    return int(pd.read_sql(conteo, eng).iloc[0, 0])


def aviso_recorte(profile: dict, df: pd.DataFrame, limit: int | None, *,
                  table: str | None = None, sql: str | None = None,
                  password: str | None = None) -> int | None:
    """Si un tope ELEGIDO recortó el resultado, devuelve el total real de
    filas (COUNT) para avisarlo; si no hubo recorte, ``None``.

    Sin tope nunca hay recorte, así que ni se cuenta. Con tope, solo se
    cuenta cuando vinieron exactamente ``limit`` filas — si vinieron menos,
    la tabla ya estaba entera."""
    tope = _tope(limit)
    if not tope or len(df) < tope:
        return None
    total = total_filas(profile, table=table, sql=sql, password=password)
    return total if total > len(df) else None


def purview_qualified_name(profile: dict, table: str) -> str | None:
    """QualifiedName real que el scanner NATIVO de Purview le asignaría a
    esta tabla — para que un push de este programa se fusione con lo que
    Purview ya haya escaneado de la misma fuente, en vez de crear un
    catálogo paralelo con un identificador inventado (``mvdg://...``).

    Solo cubre **Azure SQL Database** (host terminado en
    ``.database.windows.net``): es el único motor para el que Microsoft
    Learn publica el formato exacto de qualifiedName —
    ``mssql://{host}/{database}/{schema}/{table}`` — confirmado con un
    ejemplo antes/después en "Asset normalization in Microsoft Purview
    Data Map" (learn.microsoft.com/purview/data-gov-classic-asset-normalization).
    Para SQL Server on-premises, PostgreSQL, MySQL y el resto de los
    motores: Purview tiene scanners nativos propios, pero Microsoft NO
    publica el formato de qualifiedName que les asignan — devolver algo
    inventado ahí generaría exactamente el catálogo fantasma que esto
    busca evitar, así que se devuelve ``None`` (usa el identificador
    sintético ``mvdg://`` como respaldo).

    ``table`` acepta "tabla" o "schema.tabla" (el formato que devuelve
    ``list_tables()``); sin schema se asume "dbo" (default de SQL Server/
    Azure SQL)."""
    host = (profile.get("host") or "").strip().lower()
    database = (profile.get("database") or "").strip()
    if not host.endswith(".database.windows.net") or not database:
        return None
    if "." in table:
        schema, name = table.split(".", 1)
    else:
        schema, name = "dbo", table
    return f"mssql://{host}/{database}/{schema}/{name}"


def scan_all_connections() -> pd.DataFrame:
    """Escanea TODAS las conexiones guardadas de una sola vez (en vez de
    elegir una por vez y listar sus tablas a mano) — un dataframe con
    conexión, motor y cada tabla encontrada, o el error si esa conexión en
    particular falló (una conexión caída no frena el resto).

    Esto es honesto sobre su alcance: cubre los motores que el usuario ya
    configuró en el programa (hoy: 9 — PostgreSQL/MySQL/SQL Server/Oracle/
    SQLite/Synapse/Snowflake/BigQuery/Databricks), no "cientos de
    conectores gestionados" de un catálogo cloud como Purview, que
    despliega agentes de escaneo dentro de la infraestructura del cliente
    y agrega automáticamente cualquier recurso nuevo del tenant sin que
    nadie cargue una conexión a mano. Acá el universo lo define lo que el
    usuario conectó — es un batch sobre eso, no un descubrimiento
    autónomo de fuentes nuevas."""
    rows = []
    for conn in load_connections():
        engine_label = ENGINES.get(conn.get("engine"), {}).get("label", conn.get("engine"))
        try:
            tables = list_tables(conn, password=stored_password(conn))
            for t in tables:
                rows.append({"conn_id": conn.get("conn_id"), "name": conn.get("name"),
                            "engine": engine_label, "table": t, "error": None})
            if not tables:
                rows.append({"conn_id": conn.get("conn_id"), "name": conn.get("name"),
                            "engine": engine_label, "table": None, "error": None})
        except Exception as exc:  # noqa: BLE001 - una conexión caída no frena el resto
            rows.append({"conn_id": conn.get("conn_id"), "name": conn.get("name"),
                        "engine": engine_label, "table": None, "error": str(exc)})
    return pd.DataFrame(rows, columns=["conn_id", "name", "engine", "table", "error"])
