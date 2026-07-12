"""
MV Data Governance · Conectores directos a bases de datos.

Además de CSV/Excel, MV Data Governance se conecta directo a cualquier base de
datos vía SQLAlchemy: PostgreSQL, MySQL/MariaDB, SQL Server, Oracle y SQLite.
El usuario carga servidor, puerto, base, usuario y contraseña, prueba la
conexión, lista las tablas y trae una tabla (o el resultado de una consulta)
al mismo motor de gobierno que usa para archivos.

Las conexiones se guardan en disco y persisten entre sesiones:
    ~/.mv_data_governance/conexiones.json
La contraseña se guarda solo si el usuario lo pide, ofuscada (no en texto
plano a simple vista). Es un almacenamiento LOCAL, en el equipo del usuario —
igual que cualquier cliente de base de datos de escritorio.
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
    """Arma la URL SQLAlchemy. Para SQLite, ``database`` es la ruta al archivo."""
    from sqlalchemy.engine import URL

    eng = ENGINES.get(profile.get("engine"))
    if eng is None:
        raise ValueError(f"Motor desconocido: {profile.get('engine')}")
    if profile["engine"] == "sqlite":
        return f"sqlite:///{profile.get('database', '')}"
    pwd = password if password is not None else stored_password(profile)
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
    return create_engine(build_url(profile, password), pool_pre_ping=True)


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
