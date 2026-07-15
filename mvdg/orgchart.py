"""
MV Data Governance · Organigrama → responsables de datos por defecto.

El problema que resuelve: asignar Data Owner y Data Steward a cada dataset
suele arrancar de una planilla de RRHH o de un organigrama. Este módulo:

1. **Lee el organigrama** desde Excel/CSV (o desde cualquier tabla traída
   por conexión SQL en 🔎 Mis datos), detectando las columnas por sus
   encabezados en ES/EN/PT (nombre, cargo, área, jefe, email) aunque vengan
   con otros nombres o en otro orden. Para organigramas en **foto/imagen**,
   la extracción usa la IA externa opcional (tu propia API key, opt-in) —
   ver ``ai_provider.ai_parse_orgchart_image``.
2. **Sugiere responsables por defecto** para cada dataset del programa
   (demo + ejemplos): el Data Owner es la persona de mayor jerarquía del
   área que mejor matchea el dominio del dataset, y el Data Steward la
   siguiente persona de esa área. Es una recomendación heurística local
   (mismo espíritu que el resto del producto: primero la IA propone,
   después el responsable humano valida o corrige).
3. **Todo es editable y se guarda** en el equipo del usuario:
   ~/.mv_data_governance/organigrama.json (las personas) y
   responsables.json (las asignaciones por dataset, con su estado:
   sugerido vs. editado).
"""
from __future__ import annotations

import json
import os
import unicodedata

import pandas as pd

from .clients import data_dir

# ------------------------------------------------- detección de encabezados
# sinónimos ES/EN/PT (sin acentos, lowercase) -> campo canónico
_HEADER_SYNONYMS = {
    "nombre": ("nombre", "name", "nome", "empleado", "employee", "funcionario",
               "persona", "person", "full name", "nombre completo", "nome completo"),
    "cargo": ("cargo", "title", "puesto", "rol", "role", "job title", "posicion",
              "position", "funcion", "function", "funcao", "titulo"),
    "area": ("area", "departamento", "department", "dept", "sector", "gerencia",
             "direccion", "division", "unidad", "unit", "equipo", "team", "setor"),
    "reporta_a": ("jefe", "manager", "reporta a", "reporta", "reports to",
                  "reporte", "supervisor", "gestor", "chefe", "lider", "leader",
                  "jefe directo", "line manager"),
    "email": ("email", "e-mail", "correo", "mail", "correo electronico"),
}

_REQUIRED = ("nombre", "cargo", "area")


def _norm(text: str) -> str:
    """lowercase + sin acentos, para comparar encabezados y áreas."""
    text = unicodedata.normalize("NFKD", str(text))
    return "".join(c for c in text if not unicodedata.combining(c)).lower().strip()


def map_columns(df: pd.DataFrame) -> dict[str, str]:
    """Detecta qué columna del archivo corresponde a cada campo canónico.
    Devuelve {campo: nombre_de_columna_original}."""
    mapping: dict[str, str] = {}
    for col in df.columns:
        n = _norm(col)
        for field, synonyms in _HEADER_SYNONYMS.items():
            if field not in mapping and (n in synonyms or any(s == n for s in synonyms)):
                mapping[field] = col
                break
    return mapping


def parse_org_table(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza una tabla de organigrama al esquema canónico
    (nombre, cargo, area, reporta_a, email). Levanta ValueError si faltan
    las columnas mínimas (nombre, cargo, área)."""
    mapping = map_columns(df)
    missing = [f for f in _REQUIRED if f not in mapping]
    if missing:
        raise ValueError(
            "No se detectaron las columnas: " + ", ".join(missing) +
            ". El archivo debe tener al menos nombre, cargo y área "
            "(en ES, EN o PT; el orden no importa).")
    out = pd.DataFrame({
        "nombre": df[mapping["nombre"]].astype(str).str.strip(),
        "cargo": df[mapping["cargo"]].astype(str).str.strip(),
        "area": df[mapping["area"]].astype(str).str.strip(),
        "reporta_a": (df[mapping["reporta_a"]].astype(str).str.strip()
                      if "reporta_a" in mapping else ""),
        "email": (df[mapping["email"]].astype(str).str.strip()
                  if "email" in mapping else ""),
    })
    out = out[out["nombre"].str.len() > 0].reset_index(drop=True)
    return out


# --------------------------------------------------- jerarquía y matching
# palabras de cargo -> nivel (5 = más alto). Sin acentos, se matchea por
# "contiene" sobre el cargo normalizado.
_SENIORITY = [
    (5, ("ceo", "cfo", "coo", "cio", "cdo", "presidente", "president",
         "director", "diretor", "vp", "vice", "chief", "head")),
    (4, ("gerente", "manager", "gestor")),
    (3, ("jefe", "lead", "lider", "leader", "chefe", "responsable")),
    (2, ("coordinador", "coordinator", "coordenador", "supervisor",
         "encargado", "encarregado")),
]


def seniority(cargo: str) -> int:
    c = _norm(cargo)
    for level, words in _SENIORITY:
        if any(w in c for w in words):
            return level
    return 1


# dominio de cada dataset -> palabras clave de área (sin acentos)
_DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "dim_customers": ("comercial", "ventas", "vendas", "sales", "crm", "clientes", "customer"),
    "dim_products": ("producto", "product", "produto", "comercial", "catalogo"),
    "fct_sales": ("ventas", "vendas", "sales", "comercial"),
    "fct_payments": ("finanzas", "financas", "finance", "tesoreria", "contabilidad",
                     "contabilidade", "pagos", "payments"),
    "rotulado_alimentos": ("calidad", "qualidade", "quality", "regulatorio", "regulatory",
                           "cumplimiento", "compliance", "legal", "bromatolog"),
    "cafe_sales_kaggle": ("ventas", "vendas", "sales", "comercial", "operaciones",
                          "operations", "operacoes", "retail"),
    "bank_marketing_uci": ("marketing", "campanas", "campanhas", "campaigns", "comercial"),
    "medicamentos_openfda": ("regulatorio", "regulatory", "farmacovigilancia",
                             "pharmacovigilance", "calidad", "qualidade", "quality",
                             "asuntos regulatorios", "medica", "medical"),
}

# área que hace de fallback cuando ningún área matchea el dominio
_DATA_TEAM_KEYWORDS = ("datos", "data", "bi", "analitica", "analytics", "ti",
                       "it", "sistemas", "tecnologia", "tecnologia")


def _people_in_area(org: pd.DataFrame, keywords: tuple[str, ...]) -> pd.DataFrame:
    mask = org["area"].map(lambda a: any(k in _norm(a) for k in keywords))
    return org[mask]


def datasets_catalog() -> list[dict]:
    """Todos los datasets del programa (demo + ejemplos) con su dominio."""
    from . import samples
    from .catalog import _DATASETS
    items = [{"dataset": d["dataset"], "domain": d["domain"]["es"]}
             for d in _DATASETS]
    items += [{"dataset": k, "domain": s["domain"]["es"]}
              for k, s in samples.SAMPLES.items()]
    return items


def suggest_assignments(org: pd.DataFrame) -> pd.DataFrame:
    """Para cada dataset del programa, propone Data Owner (mayor jerarquía
    del área que matchea el dominio) y Data Steward (siguiente persona de
    esa área). Devuelve un DataFrame editable; el estado queda 'sugerido'
    hasta que el usuario lo edite y guarde."""
    rows = []
    for item in datasets_catalog():
        ds = item["dataset"]
        keywords = _DOMAIN_KEYWORDS.get(ds, ())
        # las keywords van en orden de prioridad: la primera que matchea un
        # área gana (ej. para bank_marketing, "marketing" le gana a "comercial")
        pool = org.iloc[0:0]
        matched = "dominio"
        for kw in keywords:
            pool = _people_in_area(org, (kw,))
            if not pool.empty:
                break
        if pool.empty:
            pool = _people_in_area(org, _DATA_TEAM_KEYWORDS)
            matched = "equipo de datos"
        if pool.empty:
            pool = org
            matched = "jerarquía general"
        ranked = pool.assign(_s=pool["cargo"].map(seniority)).sort_values(
            ["_s", "nombre"], ascending=[False, True])
        owner = ranked.iloc[0]
        steward = ranked.iloc[1] if len(ranked) > 1 else ranked.iloc[0]
        rows.append({
            "dataset": ds, "domain": item["domain"],
            "owner_name": owner["nombre"], "owner_role": owner["cargo"],
            "steward_name": steward["nombre"], "steward_role": steward["cargo"],
            "match": matched, "estado": "sugerido",
        })
    return pd.DataFrame(rows)


# ------------------------------------------------------------- persistencia
def _org_file() -> str:
    return os.path.join(data_dir(), "organigrama.json")


def _asg_file() -> str:
    return os.path.join(data_dir(), "responsables.json")


def save_org(org: pd.DataFrame) -> None:
    tmp = _org_file() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(org.to_dict("records"), fh, ensure_ascii=False, indent=2)
    os.replace(tmp, _org_file())


def load_org() -> pd.DataFrame | None:
    path = _org_file()
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        return pd.DataFrame(data) if data else None
    except (json.JSONDecodeError, OSError):
        return None


def save_assignments(df: pd.DataFrame) -> None:
    tmp = _asg_file() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(df.to_dict("records"), fh, ensure_ascii=False, indent=2)
    os.replace(tmp, _asg_file())


def load_assignments() -> pd.DataFrame | None:
    path = _asg_file()
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        return pd.DataFrame(data) if data else None
    except (json.JSONDecodeError, OSError):
        return None
