"""
MV Data Governance · Descubrimiento de fuentes de datos en Azure (Resource Graph).

Honestidad de escala (léase antes de usar): esto NO es "convertirse en
Purview". Lo que hace Purview a escala tenant es desplegar agentes de
escaneo DENTRO de la infraestructura de Azure del cliente, que recorren
todo el estado continuamente — eso es, literalmente, ser infraestructura
cloud. Este módulo hace algo más chico pero genuinamente real: con el
service principal del usuario (rol **Reader**, de solo lectura), hace
**una consulta** a la Azure Resource Graph API que devuelve de una vez
**todos los recursos de datos de toda la suscripción** — SQL Database,
Storage Account, Synapse, Cosmos DB, Data Factory — sin que nadie los
cargue a mano uno por uno.

Lo que esto SÍ resuelve: pasar de "escaneo batch de las conexiones que vos
cargaste" (`connectors.scan_all_connections`) a "inventario real de lo que
existe en tu suscripción de Azure", sin desplegar nada.

Lo que esto NO resuelve (y por qué): esta consulta devuelve el
**inventario** (nombre, tipo, resource group, ubicación) — no perfila
columnas, no corre reglas de calidad, no trae datos. Para gobernar de
verdad cada base descubierta, igual hay que cargarla como conexión en
🔎 Mis datos (con sus credenciales, que el usuario administra) — este
módulo le ahorra el paso de "¿qué bases tengo, en qué resource groups?".
Tampoco cruza tenants ni management groups por defecto (una suscripción a
la vez, explícito) ni corre en segundo plano — es una consulta bajo
demanda, no un agente persistente.

Apagado por defecto. Service principal propio del usuario (rol Reader
sobre la suscripción a inventariar): ``AZURE_TENANT_ID``,
``AZURE_CLIENT_ID``, ``AZURE_CLIENT_SECRET``, ``AZURE_SUBSCRIPTION_ID``.

Implementado contra Microsoft Learn (Azure Resource Graph REST API,
api-version 2022-10-01, verificado 2026-07-16). NO se probó contra una
suscripción real de Azure (no disponible en este entorno de desarrollo).
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

import pandas as pd

_TIMEOUT = 30
_ENV = ("AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "AZURE_SUBSCRIPTION_ID")
_ARG_URL = "https://management.azure.com/providers/Microsoft.ResourceGraph/resources?api-version=2022-10-01"
_MAX_PAGES = 20  # ~10.000 recursos con paginación de 500 — de sobra para inventariar

# tipos de recurso de Azure relacionados con datos que tiene sentido
# ofrecer como "conexión candidata" en 🔎 Mis datos.
DATA_RESOURCE_TYPES = {
    "microsoft.sql/servers/databases": "Azure SQL Database",
    "microsoft.sql/servers": "Azure SQL Server (instancia)",
    "microsoft.storage/storageaccounts": "Storage Account",
    "microsoft.synapse/workspaces": "Synapse Workspace",
    "microsoft.documentdb/databaseaccounts": "Cosmos DB",
    "microsoft.datafactory/factories": "Data Factory",
    "microsoft.dbformysql/flexibleservers": "Azure MySQL",
    "microsoft.dbforpostgresql/flexibleservers": "Azure PostgreSQL",
    "microsoft.databricks/workspaces": "Databricks Workspace",
}


def configured() -> bool:
    return all(os.environ.get(v) for v in _ENV)


def _get_token() -> str:
    tenant = os.environ["AZURE_TENANT_ID"]
    url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    form = {"grant_type": "client_credentials", "client_id": os.environ["AZURE_CLIENT_ID"],
            "client_secret": os.environ["AZURE_CLIENT_SECRET"],
            "scope": "https://management.azure.com/.default"}
    data = urllib.parse.urlencode(form).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))["access_token"]


def _http_json(url: str, headers: dict, body: dict) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def build_query() -> str:
    """KQL: todos los recursos cuyo tipo está en DATA_RESOURCE_TYPES, con
    los campos que importan para armar una conexión candidata."""
    types = ", ".join(f"'{t}'" for t in DATA_RESOURCE_TYPES)
    return (f"Resources | where type in~ ({types}) "
           "| project name, type, resourceGroup, location, subscriptionId, id "
           "| order by type asc, name asc")


def discover_data_resources(token: str | None = None) -> pd.DataFrame:
    """Una consulta (con paginación vía $skipToken si hace falta) que
    devuelve el inventario de recursos de datos de toda la suscripción."""
    if not configured():
        raise RuntimeError("Azure Discovery no configurado — faltan variables de entorno.")
    token = token or _get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
    query = build_query()
    rows, skip_token, pages = [], None, 0
    while pages < _MAX_PAGES:
        body = {"subscriptions": [subscription_id], "query": query}
        if skip_token:
            body["options"] = {"$skipToken": skip_token}
        result = _http_json(_ARG_URL, headers, body)
        rows.extend(result.get("data", []))
        skip_token = result.get("$skipToken")
        pages += 1
        if not skip_token:
            break
    df = pd.DataFrame(rows, columns=["name", "type", "resourceGroup", "location",
                                     "subscriptionId", "id"])
    if len(df):
        df["category"] = df["type"].map(DATA_RESOURCE_TYPES).fillna(df["type"])
        df = df[["category", "name", "resourceGroup", "location", "type", "id"]]
    return df


def suggest_connection_profile(row: dict) -> dict | None:
    """De una fila descubierta, arma el esqueleto de perfil de conexión
    para 🔎 Mis datos (sin credenciales — esas las carga el usuario a
    mano, nunca se derivan de Resource Graph). None si el tipo no mapea a
    un motor de los que el programa conecta hoy."""
    t = row.get("type", "").lower()
    name = row.get("name", "")
    if t == "microsoft.sql/servers/databases" or t == "microsoft.sql/servers":
        return {"engine": "sqlserver", "name": name,
               "host": f"{name.split('/')[0]}.database.windows.net", "database": ""}
    if t == "microsoft.dbforpostgresql/flexibleservers":
        return {"engine": "postgresql", "name": name, "host": f"{name}.postgres.database.azure.com"}
    if t == "microsoft.dbformysql/flexibleservers":
        return {"engine": "mysql", "name": name, "host": f"{name}.mysql.database.azure.com"}
    if t == "microsoft.synapse/workspaces":
        return {"engine": "synapse", "name": name, "host": f"{name}.sql.azuresynapse.net"}
    if t == "microsoft.databricks/workspaces":
        return {"engine": "databricks", "name": name, "extra": {"server_hostname": ""}}
    return None
