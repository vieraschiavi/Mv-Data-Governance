"""
MV Data Governance · Proyecto por cliente (etapas de trabajo persistentes).

Hasta acá, la ficha de cada empresa (``mvdg/clients.py``) guardaba solo los
datos de contacto/BI/madurez. El trabajo de gobierno en sí — el dataset que
cargaste y perfilaste, el reporte de duplicados/MDM, el escaneo de Power BI o
Tableau, el paquete de tablas para BI — vivía únicamente en memoria y se
perdía al cerrar el programa o al recargar la página.

Este módulo agrega un **proyecto por cliente**: cada cliente tiene su propia
carpeta en disco, y dentro guarda **etapas** — cada etapa es una foto con
nombre de una o más tablas (DataFrames) más notas y metadatos. Así podés ir
guardando cada paso del trabajo (catalogar, medir, deduplicar, escanear el
modelo de BI…) sin perder nada, y volver a abrirlo cuando quieras.

Todo es 100% local, en el equipo del usuario:

    <data_dir>/clientes/<client_id>/etapas/<stage_id>/
        manifest.json          ← nombre, tipo, notas, fecha, tablas, meta
        <tabla>.parquet|.csv   ← una por cada DataFrame de la etapa

``data_dir`` es ``~/.mv_data_governance`` (o ``MVDG_DATA_DIR``), la misma
carpeta donde ya viven las fichas de clientes y las conexiones.

Además, todo el proyecto de un cliente se puede exportar a un ZIP (para
respaldarlo o llevarlo a otra máquina) e importar de vuelta — no se pierde
nada aunque cambies de equipo.
"""
from __future__ import annotations

import io
import json
import os
import re
import shutil
import uuid
import zipfile
from datetime import datetime, timezone

import pandas as pd

from .clients import data_dir  # reutiliza ~/.mv_data_governance

_MANIFEST = "manifest.json"
_SAFE_RE = re.compile(r"[^A-Za-z0-9_.-]+")


def _now() -> str:
    # microsegundos: así dos etapas guardadas en el mismo segundo conservan
    # un orden estable (la más nueva primero) al listarlas.
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _safe_name(name: str) -> str:
    """Nombre de tabla -> nombre de archivo seguro (sin barras ni raros)."""
    slug = _SAFE_RE.sub("_", str(name).strip()) or "tabla"
    return slug[:80]


# ------------------------------------------------------------- rutas en disco
def clients_root() -> str:
    d = os.path.join(data_dir(), "clientes")
    os.makedirs(d, exist_ok=True)
    return d


def client_root(client_id: str) -> str:
    if not client_id:
        raise ValueError("client_id vacío")
    d = os.path.join(clients_root(), _safe_name(client_id))
    os.makedirs(d, exist_ok=True)
    return d


def _stages_root(client_id: str) -> str:
    d = os.path.join(client_root(client_id), "etapas")
    os.makedirs(d, exist_ok=True)
    return d


def _stage_dir(client_id: str, stage_id: str) -> str:
    return os.path.join(_stages_root(client_id), _safe_name(stage_id))


# -------------------------------------------------------- serializar tablas
def _write_table(directory: str, name: str, df: pd.DataFrame) -> dict:
    """Guarda un DataFrame en la carpeta de la etapa. Prefiere Parquet
    (preserva tipos); si falta el motor, cae a CSV. Devuelve la entrada de
    manifiesto para esa tabla."""
    base = _safe_name(name)
    # evita colisiones si dos tablas quedan con el mismo nombre seguro
    fn_parquet = f"{base}.parquet"
    try:
        df.to_parquet(os.path.join(directory, fn_parquet), index=False)
        fmt, filename = "parquet", fn_parquet
    except Exception:  # noqa: BLE001 - sin pyarrow/fastparquet -> CSV
        fn_csv = f"{base}.csv"
        df.to_csv(os.path.join(directory, fn_csv), index=False)
        fmt, filename = "csv", fn_csv
    return {"name": name, "file": filename, "format": fmt,
            "rows": int(len(df)), "cols": int(df.shape[1])}


def _read_table(directory: str, entry: dict) -> pd.DataFrame:
    path = os.path.join(directory, entry["file"])
    if entry.get("format") == "csv" or path.lower().endswith(".csv"):
        return pd.read_csv(path)
    return pd.read_parquet(path)


# ------------------------------------------------------------------ etapas
def save_stage(client_id: str, name: str, tables: dict[str, pd.DataFrame],
               kind: str = "general", notes: str = "",
               meta: dict | None = None, stage_id: str | None = None) -> dict:
    """Guarda (o reemplaza, si se pasa ``stage_id``) una etapa de trabajo del
    cliente con sus tablas. Devuelve el manifiesto persistido."""
    if not name or not name.strip():
        raise ValueError("La etapa necesita un nombre.")
    df_tables = {k: v for k, v in (tables or {}).items()
                 if isinstance(v, pd.DataFrame) and not v.empty}
    if not df_tables:
        raise ValueError("La etapa no tiene ninguna tabla para guardar.")

    sid = stage_id or uuid.uuid4().hex[:12]
    directory = _stage_dir(client_id, sid)
    if os.path.isdir(directory):  # reemplazo: limpiar la anterior
        shutil.rmtree(directory)
    os.makedirs(directory, exist_ok=True)

    table_entries = [_write_table(directory, tname, tdf)
                     for tname, tdf in df_tables.items()]
    manifest = {
        "stage_id": sid,
        "client_id": client_id,
        "name": name.strip(),
        "kind": kind,
        "notes": (notes or "").strip(),
        "meta": meta or {},
        "tables": table_entries,
        "created_at": _now(),
    }
    with open(os.path.join(directory, _MANIFEST), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    return manifest


def list_stages(client_id: str) -> list[dict]:
    """Manifiestos de todas las etapas del cliente, de la más nueva a la más
    vieja. No carga las tablas (solo los metadatos)."""
    root = _stages_root(client_id)
    out: list[dict] = []
    for entry in os.listdir(root):
        mpath = os.path.join(root, entry, _MANIFEST)
        if not os.path.isfile(mpath):
            continue
        try:
            with open(mpath, encoding="utf-8") as fh:
                out.append(json.load(fh))
        except (json.JSONDecodeError, OSError):
            continue
    out.sort(key=lambda m: m.get("created_at", ""), reverse=True)
    return out


def load_stage(client_id: str, stage_id: str) -> dict:
    """Manifiesto + las tablas (DataFrames) de una etapa, listas para usar."""
    directory = _stage_dir(client_id, stage_id)
    mpath = os.path.join(directory, _MANIFEST)
    if not os.path.isfile(mpath):
        raise FileNotFoundError(f"No existe la etapa {stage_id}.")
    with open(mpath, encoding="utf-8") as fh:
        manifest = json.load(fh)
    tables = {e["name"]: _read_table(directory, e)
              for e in manifest.get("tables", [])}
    return {**manifest, "loaded_tables": tables}


def delete_stage(client_id: str, stage_id: str) -> bool:
    directory = _stage_dir(client_id, stage_id)
    if not os.path.isdir(directory):
        return False
    shutil.rmtree(directory)
    return True


def project_summary(client_id: str) -> dict:
    """Resumen del proyecto del cliente: cuántas etapas, cuántas tablas y
    filas guardadas en total, y cuándo se actualizó por última vez."""
    stages = list_stages(client_id)
    n_tables = sum(len(m.get("tables", [])) for m in stages)
    n_rows = sum(int(e.get("rows", 0))
                 for m in stages for e in m.get("tables", []))
    return {
        "stages": len(stages),
        "tables": n_tables,
        "rows": n_rows,
        "updated_at": stages[0]["created_at"] if stages else "",
    }


# --------------------------------------------------- exportar / importar ZIP
def export_project(client_id: str) -> bytes:
    """Todo el proyecto del cliente (todas las etapas y sus tablas) en un
    único ZIP en memoria, listo para descargar y respaldar."""
    root = client_root(client_id)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for dirpath, _dirs, files in os.walk(root):
            for f in files:
                full = os.path.join(dirpath, f)
                arc = os.path.relpath(full, root)
                zf.write(full, arc)
    return buf.getvalue()


def import_project(client_id: str, zip_bytes: bytes,
                   replace: bool = False) -> int:
    """Restaura un proyecto desde un ZIP generado por ``export_project``.
    Devuelve cuántas etapas quedaron en el proyecto tras importar. Si
    ``replace`` es True, borra las etapas actuales antes de importar."""
    root = client_root(client_id)
    if replace:
        stages_root = os.path.join(root, "etapas")
        if os.path.isdir(stages_root):
            shutil.rmtree(stages_root)
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for member in zf.namelist():
            # anti path-traversal: nunca escribir fuera de root
            target = os.path.normpath(os.path.join(root, member))
            if not target.startswith(os.path.abspath(root) + os.sep) \
                    and target != os.path.abspath(root):
                continue
            if member.endswith("/"):
                os.makedirs(target, exist_ok=True)
                continue
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with zf.open(member) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)
    return len(list_stages(client_id))


def delete_project(client_id: str) -> bool:
    """Borra por completo el proyecto de un cliente (todas sus etapas)."""
    root = os.path.join(clients_root(), _safe_name(client_id))
    if not os.path.isdir(root):
        return False
    shutil.rmtree(root)
    return True
