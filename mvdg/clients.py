"""
MV Data Governance · Fichas de empresas clientes (persistentes).

CRM liviano de gobierno de datos: cada ficha guarda la empresa, el contacto,
su BI, sus restricciones de TI (deciden si conviene la Opción A instalador
.exe o la Opción B portable .bat), la madurez de gobierno y notas.

Las fichas se guardan en disco (JSON) y sobreviven al cierre del programa, en
la carpeta que decide ``data_dir()`` — ver ahí la prioridad exacta.
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime, timezone

import pandas as pd

BI_TOOLS = ["Power BI", "Tableau", "Looker", "MicroStrategy", "Qlik", "Excel"]
IT_RESTRICTIONS = ["exe_ok", "no_exe_python_ok", "solo_web"]
STATUSES = ["lead", "demo", "piloto", "activo", "cerrado"]


def data_dir() -> str:
    """Carpeta donde vive TODO lo persistente (clientes, curaduría, licencia,
    conexiones, importado, organigrama - un solo directorio para todo eso).

    Prioridad:
    1. ``MVDG_DATA_DIR`` explícita: control manual, gana siempre.
    2. Instalación empaquetada (el .exe de Inno Setup, ``sys.frozen``): una
       carpeta ``Data`` AL LADO del ejecutable. Así lo que el usuario eligió
       en "Seleccionar carpeta de destino" del instalador (C:, D:, un
       pendrive) es también donde quedan sus datos - no una carpeta aparte
       en el perfil de Windows, que casi siempre vive en C: aunque el
       programa se haya instalado en otro disco a propósito.
    3. Todo lo demás (portable .bat, corriendo desde código fuente):
       ``~/.mv_data_governance``. Ahí no hay una carpeta de instalación fija
       a la cual atarse - el usuario puede mover la carpeta del programa
       libremente sin que sus datos queden huérfanos en otro lado.
    """
    override = os.environ.get("MVDG_DATA_DIR")
    if override:
        d = override
    elif getattr(sys, "frozen", False):
        d = os.path.join(os.path.dirname(sys.executable), "Data")
    else:
        d = os.path.join(os.path.expanduser("~"), ".mv_data_governance")
    os.makedirs(d, exist_ok=True)
    return d


def _file() -> str:
    return os.path.join(data_dir(), "clientes.json")


def load_clients() -> list[dict]:
    """Todas las fichas guardadas (lista vacía si aún no hay archivo)."""
    path = _file()
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _write(clients: list[dict]) -> None:
    tmp = _file() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(clients, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, _file())


def save_client(record: dict) -> dict:
    """Crea o actualiza una ficha (por ``client_id``) y persiste a disco."""
    clients = load_clients()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    cid = record.get("client_id") or uuid.uuid4().hex[:12]
    record = {**record, "client_id": cid, "updated_at": now}
    for i, c in enumerate(clients):
        if c.get("client_id") == cid:
            record.setdefault("created_at", c.get("created_at", now))
            clients[i] = {**c, **record}
            _write(clients)
            return clients[i]
    record.setdefault("created_at", now)
    clients.append(record)
    _write(clients)
    return record


def delete_client(client_id: str) -> bool:
    clients = load_clients()
    remaining = [c for c in clients if c.get("client_id") != client_id]
    if len(remaining) == len(clients):
        return False
    _write(remaining)
    return True


def clients_df() -> pd.DataFrame:
    """Fichas como DataFrame (columnas estables aunque no haya datos)."""
    cols = ["client_id", "company", "country", "industry", "contact_name",
            "contact_email", "bi_tools", "it_restriction", "recommended_pack",
            "maturity", "status", "notes", "created_at", "updated_at"]
    clients = load_clients()
    if not clients:
        return pd.DataFrame(columns=cols)
    df = pd.DataFrame(clients)
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    return df[cols]


def recommended_pack(it_restriction: str) -> str:
    """Qué paquete de distribución conviene según la restricción de TI:
    A = instalador .exe · B = portable .bat · Web = despliegue en servidor."""
    return {
        "exe_ok": "A",
        "no_exe_python_ok": "B",
        "solo_web": "Web",
    }.get(it_restriction, "B")
