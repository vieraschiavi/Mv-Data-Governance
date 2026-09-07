# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Perfilador de datos del usuario.

Recibe cualquier DataFrame (CSV/Excel subido por el usuario) y devuelve un
perfil por columna, detección heurística de PII y sugerencias de reglas de
calidad — el primer paso para incorporar un dataset propio al gobierno.
"""
from __future__ import annotations

import re

import pandas as pd

# ---------------------------------------------------------------------------
# Detección de PII por nombre de columna
# ---------------------------------------------------------------------------
# Se mira en dos pasadas y no en una sola regex:
#
#   1) TOKENS EXACTOS — el nombre se parte por los separadores que se usan de
#      verdad (`ci_cliente`, `nro-documento`, `Fecha Nacimiento`) y cada
#      pedazo se compara entero. Es lo que hace falta para las siglas: con una
#      regex de subcadena, `ci` matchea adentro de «precio» y `ip` adentro de
#      «equipo», así que había que ponerles `\b`… y `\b` no corta antes de un
#      guión bajo, porque `_` es carácter de palabra. Resultado: `ci\b` no
#      encontraba `ci_cliente`, que es exactamente como se llama la columna en
#      media base uruguaya.
#
#   2) SUBCADENAS — para las palabras largas, donde no hay ambigüedad
#      (`email_corporativo`, `telefono2`).
#
# Lo que faltaba, y por qué importa acá: `cédula` y `apellido` no se detectaban.
# Este producto se vende en Uruguay, donde «cédula» es LA columna de PII más
# común que hay, y un apellido identifica a una persona igual que un nombre.
# Un informe de cumplimiento que no las marca no está incompleto: está
# equivocado, y el cliente lo firma creyendo que revisó.
_PII_TOKENS = frozenset({
    # documentos de identidad de la región
    "ci", "cedula", "cédula", "doc", "documento", "dni", "rut", "ruc", "rfc",
    "nit", "cuit", "cuil", "cpf", "curp", "nif", "pasaporte", "passport",
    # contacto
    "mail", "email", "correo", "tel", "telefono", "teléfono", "celular",
    "movil", "móvil", "whatsapp",
    # persona
    "nombre", "nombres", "apellido", "apellidos", "sobrenome", "name",
    # ubicación
    "direccion", "dirección", "domicilio", "address", "endereco", "endereço",
    # instrumentos financieros y de red (personales bajo GDPR/LGPD)
    "iban", "cbu", "cvu", "tarjeta", "ip",
})
_PII_SUBSTR = re.compile(
    r"(e-mail|email|correo|phone|tel[eé]fono|celular|whatsapp|documento|"
    r"c[eé]dula|apellido|sobrenome|pasaporte|passport|name|nombre|nome|"
    r"address|direcci[oó]n|domicilio|endere[cç]o|birth|nacimiento|nascimento|"
    r"tarjeta|credit_card|creditcard)", re.IGNORECASE)
_SEPARADORES = re.compile(r"[^0-9a-záéíóúñüàâãêôç]+", re.IGNORECASE)


def _es_pii_por_nombre(col: str) -> bool:
    """¿El nombre de la columna delata datos personales?"""
    nombre = str(col).strip().lower()
    if _PII_SUBSTR.search(nombre):
        return True
    # `telefono2`, `doc1`: el número pegado al final es parte del nombre, no
    # un token aparte, así que se saca antes de comparar.
    piezas = (re.sub(r"\d+$", "", p) for p in _SEPARADORES.split(nombre) if p)
    return any(p in _PII_TOKENS for p in piezas)


_EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.]+$")


def profile_table(df: pd.DataFrame) -> pd.DataFrame:
    """Perfil por columna: tipo, % nulos, únicos, ejemplo y flag de PII."""
    rows = []
    n = len(df)
    for col in df.columns:
        s = df[col]
        non_null = s.dropna()
        sample = str(non_null.iloc[0]) if len(non_null) else ""
        looks_email = bool(len(non_null)) and bool(
            non_null.astype(str).head(50).str.match(_EMAIL_RE).mean() > 0.5)
        rows.append({
            "column": str(col),
            "dtype": str(s.dtype),
            "null_pct": round(100.0 * s.isna().sum() / n, 2) if n else 0.0,
            "unique_values": int(s.nunique(dropna=True)),
            "sample": sample[:40],
            "possible_pii": _es_pii_por_nombre(col) or looks_email,
        })
    return pd.DataFrame(rows)


def summary(df: pd.DataFrame) -> dict:
    n = len(df)
    return {
        "rows": n,
        "columns": int(df.shape[1]),
        "duplicate_rows": int(df.duplicated().sum()),
        "null_cells_pct": round(100.0 * df.isna().sum().sum() / max(1, n * max(1, df.shape[1])), 2),
        "pii_columns": int(profile_table(df)["possible_pii"].sum()) if n else 0,
    }


def suggest_rules(df: pd.DataFrame, lang: str = "es") -> list[str]:
    """Sugerencias de reglas en el idioma pedido, a partir del perfil."""
    msg = {
        "not_null": {
            "es": "Completitud: exigir no-nulos en «{c}» ({p}% nulos hoy).",
            "en": "Completeness: require non-null in “{c}” ({p}% nulls today).",
            "pt": "Completude: exigir não-nulos em “{c}” ({p}% nulos hoje).",
        },
        "unique": {
            "es": "Unicidad: «{c}» parece clave — exigir valores únicos.",
            "en": "Uniqueness: “{c}” looks like a key — enforce unique values.",
            "pt": "Unicidade: “{c}” parece chave — exigir valores únicos.",
        },
        "pii": {
            "es": "Privacidad: clasificar «{c}» como PII y definir enmascaramiento.",
            "en": "Privacy: classify “{c}” as PII and define masking.",
            "pt": "Privacidade: classificar “{c}” como PII e definir mascaramento.",
        },
        "dupes": {
            "es": "Unicidad: eliminar {d} filas duplicadas exactas.",
            "en": "Uniqueness: remove {d} exact duplicate rows.",
            "pt": "Unicidade: remover {d} linhas duplicadas exatas.",
        },
    }
    prof = profile_table(df)
    out: list[str] = []
    n = len(df)
    for _, r in prof.iterrows():
        if 0 < r["null_pct"] <= 20:
            out.append(msg["not_null"][lang].format(c=r["column"], p=r["null_pct"]))
        if n > 1 and r["unique_values"] == n and r["null_pct"] == 0:
            out.append(msg["unique"][lang].format(c=r["column"]))
        if r["possible_pii"]:
            out.append(msg["pii"][lang].format(c=r["column"]))
    d = int(df.duplicated().sum())
    if d:
        out.append(msg["dupes"][lang].format(d=d))
    return out[:12]
