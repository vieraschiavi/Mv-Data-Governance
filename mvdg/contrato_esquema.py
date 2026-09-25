# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Contrato de ESQUEMA por tabla (estilo data contract / dbt).

Complementa a ``contracts.py`` (el contrato de *producto*: reglas, SLA,
consumidores y firma). Acá se fija la forma de la tabla: qué columnas se
esperan, de qué tipo, si aceptan nulos, cuál es la clave y qué valores
se aceptan en las columnas de dominio cerrado. Es lo que un consumidor
necesita para que un cambio del productor no le rompa el tablero en
silencio.

* ``generar_contrato(df, dataset)`` arma el contrato inicial DESDE EL
  PERFILADO real de la tabla (no se inventa nada: lo que el dato muestra hoy
  es la propuesta; el steward la ajusta).
* ``validar_contrato(df, contrato)`` devuelve la lista de violaciones.
* ``a_yaml(contrato)`` lo exporta a YAML (formato dbt-like) sin depender de
  PyYAML: el motor no suma dependencias.
* ``guardar_contrato`` versiona append-only y deja el cambio en el registro
  de cambios de criterio (``steward.registrar_cambio``).
"""
from __future__ import annotations

import json

import pandas as pd

from . import steward
from .profiler import profile_table

TIPOS = ("integer", "number", "boolean", "datetime", "string")
#: Una columna de texto es de "dominio cerrado" si tiene a lo sumo esta
#: cantidad de valores distintos (y se repiten: no es un identificador).
MAX_ACEPTADOS = 12
_F_CONTRATOS = "contratos_esquema.json"


def tipo_de(serie: pd.Series) -> str:
    """Tipo lógico del contrato para una columna de pandas."""
    if pd.api.types.is_bool_dtype(serie):
        return "boolean"
    if pd.api.types.is_integer_dtype(serie):
        return "integer"
    if pd.api.types.is_float_dtype(serie):
        no_nulos = serie.dropna()
        if len(no_nulos) and bool((no_nulos == no_nulos.round()).all()):
            return "integer"       # enteros con nulos: pandas los pasa a float
        return "number"
    if pd.api.types.is_datetime64_any_dtype(serie):
        return "datetime"
    return "string"


def _compatible(esperado: str, real: str) -> bool:
    return esperado == real or (esperado == "number" and real == "integer")


def generar_contrato(df: pd.DataFrame, dataset: str,
                     max_aceptados: int = MAX_ACEPTADOS) -> dict:
    """Contrato inicial desde el perfil de la tabla."""
    perfil = profile_table(df).set_index("column")
    n = len(df)
    columnas = []
    for col in df.columns:
        p = perfil.loc[str(col)]
        tipo = tipo_de(df[col])
        unicos = int(p["unique_values"])
        aceptados = None
        if (tipo == "string" and not bool(p["possible_pii"])
                and 0 < unicos <= max_aceptados and unicos * 2 <= n):
            aceptados = sorted(str(v) for v in df[col].dropna().unique())
        columnas.append({"name": str(col), "type": tipo,
                         "nullable": bool(p["null_pct"] > 0),
                         "key": False, "accepted_values": aceptados})
    candidatas = [c for c in columnas
                  if n and not c["nullable"] and df[c["name"]].nunique() == n]
    if candidatas:
        clave = next((c for c in candidatas if "id" in c["name"].lower()), candidatas[0])
        clave["key"] = True
    return {"dataset": dataset, "version": 0, "origen": "perfilado",
            "columns": columnas}


def validar_contrato(df: pd.DataFrame, contrato: dict) -> list[dict]:
    """Las violaciones del contrato en la tabla, una por hallazgo."""
    ds = contrato.get("dataset", "")
    out: list[dict] = []

    def v(col, check, detalle, filas=0):
        out.append({"dataset": ds, "column": col, "check": check,
                    "detail": detalle, "rows": int(filas)})

    declaradas = {c["name"] for c in contrato.get("columns", [])}
    for extra in [str(c) for c in df.columns if str(c) not in declaradas]:
        v(extra, "columna_no_declarada", "La tabla trae una columna que el contrato no declara.")
    for c in contrato.get("columns", []):
        nombre = c["name"]
        if nombre not in df.columns:
            v(nombre, "columna_faltante", "El contrato la declara y la tabla no la trae.")
            continue
        s = df[nombre]
        real = tipo_de(s)
        if not _compatible(c["type"], real):
            v(nombre, "tipo", f"Se esperaba {c['type']} y llegó {real}.", s.notna().sum())
        nulos = int(s.isna().sum())
        if nulos and (not c.get("nullable", True) or c.get("key")):
            v(nombre, "clave_nula" if c.get("key") else "nulos",
              f"{nulos} nulos en una columna que no los acepta.", nulos)
        if c.get("key"):
            dup = int(s.dropna().duplicated().sum())
            if dup:
                v(nombre, "clave_duplicada", f"{dup} valores repetidos en la clave.", dup)
        aceptados = c.get("accepted_values")
        if aceptados:
            fuera = s.dropna().astype(str)
            fuera = fuera[~fuera.isin([str(a) for a in aceptados])]
            if len(fuera):
                muestra = ", ".join(sorted(fuera.unique())[:5])
                v(nombre, "valor_no_aceptado",
                  f"{len(fuera)} valores fuera del dominio aceptado ({muestra}).", len(fuera))
    return out


def a_yaml(contrato: dict) -> str:
    """YAML estilo dbt ``models:``. Los textos van entre comillas dobles con
    escape JSON, que YAML acepta tal cual: no hace falta PyYAML."""
    q = json.dumps
    lineas = ["version: 2", "models:",
              f"  - name: {q(contrato.get('dataset', ''), ensure_ascii=False)}",
              "    config:",
              "      contract:",
              "        enforced: true",
              "    meta:",
              f"      contract_version: {int(contrato.get('version', 0))}",
              f"      origin: {q(contrato.get('origen', ''), ensure_ascii=False)}",
              "    columns:"]
    for c in contrato.get("columns", []):
        lineas.append(f"      - name: {q(c['name'], ensure_ascii=False)}")
        lineas.append(f"        data_type: {c['type']}")
        pruebas = []
        if not c.get("nullable", True) or c.get("key"):
            pruebas.append("          - not_null")
        if c.get("key"):
            pruebas.append("          - unique")
        if c.get("accepted_values"):
            vals = ", ".join(q(str(a), ensure_ascii=False) for a in c["accepted_values"])
            pruebas += ["          - accepted_values:", f"              values: [{vals}]"]
        if pruebas:
            lineas.append("        data_tests:")
            lineas.extend(pruebas)
    return "\n".join(lineas) + "\n"


# ------------------------------------------------------------- versionado
def _validar_forma(contrato: dict) -> None:
    if not contrato.get("dataset"):
        raise steward.StewardError("contrato", "El contrato necesita el nombre del dataset.")
    nombres = [c.get("name") for c in contrato.get("columns", [])]
    if not nombres or len(nombres) != len(set(nombres)):
        raise steward.StewardError("contrato",
                                   "El contrato necesita columnas, sin nombres repetidos.")
    for c in contrato["columns"]:
        if c.get("type") not in TIPOS:
            raise steward.StewardError("contrato",
                                       f"Tipo inválido en {c.get('name')}: {c.get('type')}")


def historial(dataset: str) -> list[dict]:
    return [r for r in steward.leer_registros(_F_CONTRATOS)
            if r.get("dataset") == dataset]


def contrato_vigente(dataset: str) -> dict | None:
    hist = historial(dataset)
    return hist[-1] if hist else None


def contrato_para(dataset: str, df: pd.DataFrame) -> dict:
    """El vigente si se guardó uno; si no, el generado desde el perfilado."""
    return contrato_vigente(dataset) or generar_contrato(df, dataset)


def resumen(contrato: dict | None) -> str:
    """Una línea legible por columna (para el antes/después de la auditoría)."""
    if not contrato:
        return ""
    partes = []
    for c in contrato.get("columns", []):
        txt = f"{c['name']}:{c['type']}"
        txt += "" if c.get("nullable", True) else " not_null"
        txt += " key" if c.get("key") else ""
        if c.get("accepted_values"):
            txt += " {" + ",".join(map(str, c["accepted_values"])) + "}"
        partes.append(txt)
    return "; ".join(partes)


def guardar_contrato(contrato: dict, quien: str, motivo: str = "",
                     ahora=None) -> dict:
    """Guarda una VERSIÓN nueva del contrato y registra el antes/después."""
    quien = steward._quien(quien)
    _validar_forma(contrato)
    ds = contrato["dataset"]
    previo = contrato_vigente(ds)
    nuevo = {"dataset": ds, "columns": contrato["columns"],
             "version": len(historial(ds)) + 1, "origen": "guardado",
             "guardado_por": quien, "guardado_en": steward._iso(ahora),
             "motivo": (motivo or "").strip()}
    steward.registrar_cambio("contrato", f"contrato:{ds}",
                             resumen(previo) or "(sin contrato)", resumen(nuevo),
                             quien, motivo, ds, ahora)
    return steward.agregar_registro(_F_CONTRATOS, nuevo)


_COLS = ["dataset", "version", "origen", "column", "type", "nullable", "key",
         "accepted_values", "violaciones_tabla"]


def contratos_df(tables: dict) -> pd.DataFrame:
    """Una fila por columna contratada de cada tabla que se pasa, con la
    cantidad de violaciones que la tabla tiene hoy contra su contrato."""
    filas = []
    for ds, df in tables.items():
        if df is None or not len(df.columns):
            continue
        con = contrato_para(ds, df)
        n_viol = len(validar_contrato(df, con))
        for c in con["columns"]:
            filas.append({"dataset": ds, "version": con.get("version", 0),
                          "origen": con.get("origen", ""), "column": c["name"],
                          "type": c["type"], "nullable": bool(c.get("nullable", True)),
                          "key": bool(c.get("key")),
                          "accepted_values": ", ".join(map(str, c.get("accepted_values")
                                                           or [])),
                          "violaciones_tabla": n_viol})
    return pd.DataFrame(filas, columns=_COLS)
