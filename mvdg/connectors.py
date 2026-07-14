"""
MV Data Governance · Conectores directos a bases de datos.

Además de CSV/Excel, MV Data Governance se conecta directo a cualquier base de
datos vía SQLAlchemy: PostgreSQL, MySQL/MariaDB, SQL Server, Oracle, SQLite,
y los data warehouse/lake de nube más usados — Snowflake, Google BigQuery,
Databricks SQL Warehouse y Azure Synapse (SQL pool, vía el mismo driver que
SQL Server, con el que es compatible por protocolo). El usuario carga
servidor, puerto, base, usuario y contraseña (o los parámetros que
correspondan a cada nube — ver ``extra`` más abajo), prueba la conexión,
lista las tablas y trae una tabla (o el resultado de una consulta) al mismo
motor de gobierno que usa para archivos.

Las conexiones se guardan en disco y persisten entre sesiones:
    ~/.mv_data_governance/conexiones.json
La contraseña (o el token de acceso, según el motor) se guarda solo si el
usuario lo pide, ofuscada (no en texto plano a simple vista). Es un
almacenamiento LOCAL, en el equipo del usuario — igual que cualquier
cliente de base de datos de escritorio.

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
    "snowflake": {"label": "Snowflake", "driver": "snowflake",
                 "port": None, "pip": "snowflake-sqlalchemy"},
    "bigquery": {"label": "Google BigQuery", "driver": "bigquery",
                "port": None, "pip": "sqlalchemy-bigquery"},
    "databricks": {"label": "Databricks SQL Warehouse", "driver": "databricks",
                   "port": None, "pip": "databricks-sqlalchemy"},
}

# motores cuya conexión no sigue el modelo host+puerto+usuario+contraseña —
# usan ``profile["extra"]`` (dict) para sus parámetros propios.
CLOUD_ENGINES = ("snowflake", "bigquery", "databricks")

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
}

MAX_ROWS = 100_000  # tope de seguridad al traer una tabla


def _file() -> str:
    return os.path.join(data_dir(), "conexiones.json")


def _obfuscate(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def _deobfuscate(text: str) -> str:
    try:
        return base64.b64decode(text.encode("ascii")).decode("utf-8")
    except Exception:
        return ""


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
    """Crea o actualiza una conexión guardada (por ``conn_id``)."""
    conns = load_connections()
    cid = profile.get("conn_id") or uuid.uuid4().hex[:12]
    stored = {
        "conn_id": cid,
        "name": profile.get("name", "").strip(),
        "engine": profile.get("engine", "postgresql"),
        "host": profile.get("host", "").strip(),
        "port": profile.get("port"),
        "database": profile.get("database", "").strip(),
        "user": profile.get("user", "").strip(),
        "save_password": bool(save_password),
        "password_enc": _obfuscate(profile.get("password", "")) if save_password else "",
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
    _write(rest)
    return True


def stored_password(profile: dict) -> str:
    """Contraseña guardada (desofuscada) de una conexión persistida."""
    return _deobfuscate(profile.get("password_enc", "")) if profile.get("save_password") else ""


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

    return URL.create(
        eng["driver"],
        username=profile.get("user") or None,
        password=pwd or None,
        host=profile.get("host") or None,
        port=int(profile["port"]) if profile.get("port") else eng["port"],
        database=profile.get("database") or None,
    )


def _engine(profile: dict, password: str | None = None):
    from sqlalchemy import create_engine
    kwargs = {"pool_pre_ping": True}
    if profile.get("engine") == "bigquery":
        creds = (profile.get("extra") or {}).get("credentials_path")
        if creds:
            kwargs["credentials_path"] = creds
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


def load_table(profile: dict, table: str, limit: int = 10_000,
               password: str | None = None) -> pd.DataFrame:
    """Trae una tabla a un DataFrame (con tope de filas)."""
    limit = max(1, min(int(limit), MAX_ROWS))
    eng = _engine(profile, password)
    if "." in table:
        schema, name = table.split(".", 1)
        ref = f"{schema}.{name}"
    elif profile["engine"] == "mysql":
        ref = f"`{table}`"
    else:
        ref = f'"{table}"'
    return pd.read_sql(f"SELECT * FROM {ref}", eng).head(limit)


def run_query(profile: dict, sql: str, limit: int = 10_000,
              password: str | None = None) -> pd.DataFrame:
    """Ejecuta una consulta SELECT y devuelve el resultado (con tope)."""
    if not sql.strip().lower().startswith(("select", "with")):
        raise ValueError("Solo se permiten consultas de lectura (SELECT / WITH).")
    limit = max(1, min(int(limit), MAX_ROWS))
    return pd.read_sql(sql, _engine(profile, password)).head(limit)
