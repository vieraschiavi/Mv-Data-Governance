# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Motor de ingeniería de datos automática.

Perfilado avanzado + calidad por 6 dimensiones + detección de claves y joins
entre tablas + análisis temporal + ranking de variables contra un target con
detección de fuga (leakage) + feature engineering automático anti-leakage +
DDL sugerido — sobre un archivo (CSV/Excel/Parquet/JSON) o una base de datos
SQL vía SQLAlchemy.

Es la versión de motor de `mvdg/profiler.py`, que se queda como el perfil
rápido y liviano (la pestaña "Mis datos"). Este módulo es la version
completa: la pestaña "Ingeniería de datos", gratuita igual que aquella —
mostrarle a alguien lo que el producto hace con SUS datos es lo que después
se compra, no algo que se cobra aparte.

TEXTO DE CARA AL USUARIO: nada de esto arma oraciones en español. Cada
"issue" de calidad, cada motivo de fuga y cada feature generada llevan un
CÓDIGO estable (`qi_nulos_masivos`, `fuga_auc_alto`, `fx_mes_seno`...) y un
diccionario de valores (números, nombres de columna). La traducción a
ES/EN/PT vive en `mvdg/i18n.py`, con la paridad de idiomas que ya cubre el
test de siempre — si esto armara el texto acá, quedaría atado a un idioma.

SIN ESTADO GLOBAL: `autodata.py` (el script del que sale este motor) tenía
un logger módulo-global de acumulaba errores entre etapas — perfecto para un
proceso de línea de comandos que corre una vez y termina, pero un bug real
acá: `bi_api` es un servidor que atiende pedidos concurrentes, y un logger
global mezclaría los errores de un cliente con los de otro. Cada función
devuelve su propio resultado; `analizar_tabla()` junta las advertencias de
SU llamada en una lista local, nunca compartida.

FUENTE DE DATOS: este módulo no sabe ni le importa de dónde salió el
DataFrame. Un archivo subido llega por `leer_archivo_bytes()` acá mismo;
una base de datos SQL ya tenía su propio motor completo — 9 motores,
Snowflake/BigQuery/Databricks incluidos, contraseña protegida con el
keyring del sistema operativo — en `mvdg/connectors.py`
(`test_connection`/`list_tables`/`load_table`/`run_query`), usado hoy desde
la pestaña Perfilador de Streamlit. Escribir un conector SQL nuevo acá
hubiera sido la misma duplicación que ya le costó caro a este proyecto una
vez: dos motores para "la misma" cosa que se desincronizan sin que nadie se
entere. Lo que faltaba — y lo que agrega esta entrega — es tender ESE
conector hasta `bi_api` (el `.exe`), que hoy solo sube archivos.
"""
from __future__ import annotations

import io
import math
import os
import re

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# Límites — este motor corre DENTRO de un pedido HTTP con tiempo de espera
# real del lado del cliente, a diferencia del script de línea de comandos
# que lo origina. Sin topes, una tabla enorme se lleva puesta la memoria del
# proceso (o del Python embebido del .exe) y deja al programa sin responder.
# --------------------------------------------------------------------------
TOPE_FILAS = 200_000
MUESTRA_SQL_DEFECTO = 50_000
MAX_TABLAS_MULTIPLES = 12
MAX_TABLAS_ESQUEMA_SQL = 15


def _num(x):
    """Valor numérico "limpio" para exportar a JSON — sin NaN/Inf, sin numpy."""
    try:
        if x is None:
            return None
        f = float(x)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except Exception:
        return None


def slug(txt, maxlen=45):
    """Nombre apto para SQL/parquet: solo [0-9A-Za-z_], sin acentos ni espacios."""
    s = re.sub(r"[^0-9A-Za-z_]+", "_", str(txt)).strip("_")
    return (s[:maxlen] or "tabla")


# ============================================================================
# 1. CARGA — archivo
# ============================================================================
EXT_TABULAR = {".csv", ".tsv", ".txt", ".xlsx", ".xlsm", ".xls",
               ".parquet", ".json", ".jsonl", ".ndjson"}
EXT_SQLITE = {".db", ".sqlite", ".sqlite3", ".db3"}
EXT_SOPORTADAS = EXT_TABULAR | EXT_SQLITE


def leer_csv_bytes(datos: bytes, sep=None, encoding=None, muestra=None) -> pd.DataFrame:
    """CSV robusto: prueba separadores y encodings hasta que uno funcione.

    Un archivo real llega con quien-sabe-qué separador y encoding — pedirle
    a la persona que los adivine antes de subir el archivo es fricción que
    no hace falta; probar unas pocas combinaciones conocidas cuesta
    milisegundos y cubre el 99% de los CSV que existen.
    """
    seps = [sep] if sep else [None, ";", ",", "\t", "|"]
    encs = [encoding] if encoding else ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    ultimo = None
    for e in encs:
        for s in seps:
            try:
                df = pd.read_csv(io.BytesIO(datos), sep=s, encoding=e, nrows=muestra,
                                 engine="python", on_bad_lines="skip")
                if df.shape[1] == 1 and s in (None, ","):
                    ultimo = df
                    continue  # probablemente el separador está mal
                return df
            except Exception as exc:
                ultimo = exc
    if isinstance(ultimo, pd.DataFrame):
        return ultimo
    raise RuntimeError(f"No se pudo leer el CSV: {ultimo}")


def leer_archivo_bytes(nombre: str, datos: bytes, hoja=None, muestra=None,
                       sep=None, encoding=None) -> dict[str, pd.DataFrame]:
    """Devuelve {nombre_tabla: DataFrame} a partir de los bytes de un archivo subido."""
    ext = os.path.splitext(nombre)[1].lower()
    if ext not in EXT_SOPORTADAS:
        raise RuntimeError(f"Extensión no soportada: {ext}")

    if ext in (".csv", ".tsv", ".txt"):
        return {nombre: leer_csv_bytes(datos, sep, encoding, muestra)}
    if ext in (".xlsx", ".xlsm", ".xls"):
        hojas = pd.read_excel(io.BytesIO(datos), sheet_name=hoja if hoja else None,
                              nrows=muestra)
        if isinstance(hojas, pd.DataFrame):
            return {hoja or nombre: hojas}
        return dict(hojas.items())
    if ext == ".parquet":
        df = pd.read_parquet(io.BytesIO(datos))
        return {nombre: df.head(muestra) if muestra else df}
    if ext == ".json":
        try:
            df = pd.read_json(io.BytesIO(datos))
        except Exception:
            df = pd.read_json(io.BytesIO(datos), lines=True)
        return {nombre: df.head(muestra) if muestra else df}
    if ext in (".jsonl", ".ndjson"):
        df = pd.read_json(io.BytesIO(datos), lines=True)
        return {nombre: df.head(muestra) if muestra else df}
    if ext in EXT_SQLITE:
        return _leer_sqlite_bytes(datos, muestra=muestra)
    raise RuntimeError(f"Extensión no soportada: {ext}")  # pragma: no cover


def _leer_sqlite_bytes(datos: bytes, tabla=None, muestra=None) -> dict[str, pd.DataFrame]:
    """SQLite es un archivo, no una conexión: llega como bytes subidos, no
    como URL — evita el riesgo de que una URL sqlite:/// apunte a un archivo
    del servidor que no es el que la persona quiso compartir."""
    import sqlite3
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".sqlite") as tmp:
        tmp.write(datos)
        tmp.flush()
        cx = sqlite3.connect(tmp.name)
        try:
            tablas = pd.read_sql_query(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%'", cx)["name"].tolist()
            if tabla:
                tablas = [t for t in tablas if t.lower() == str(tabla).lower()] or [tabla]
            out = {}
            for t in tablas[:MAX_TABLAS_MULTIPLES]:
                lim = f" LIMIT {int(muestra)}" if muestra else ""
                out[t] = pd.read_sql_query(f'SELECT * FROM "{t}"{lim}', cx)
            return out
        finally:
            cx.close()


# ============================================================================
# 2. TIPADO
# ============================================================================
PAT_FECHA = re.compile(r"(fec|fch|date|dt_|_dt|fecha|periodo|mes|alta|baja|vto|venc)", re.I)
PAT_ID = re.compile(r"(^id|_id$|codigo|cod_|nro|numero|documento|c[eé]dula|ruc|cuit|clave|key)", re.I)
PAT_MONTO = re.compile(r"(monto|importe|saldo|valor|precio|total|deuda|cobrad|pagad|amount|revenue)", re.I)


def _a_numero(serie: pd.Series) -> pd.Series:
    """Convierte texto tipo '1.234,56' o '$ 1,234.56' a numérico."""
    s = serie.astype("string").str.strip()
    s = s.str.replace(r"[^\d,.\-]", "", regex=True)
    con_coma = s.str.contains(",", na=False).mean()
    con_punto = s.str.contains(r"\.", na=False).mean()
    if con_coma > 0.3 and con_punto > 0.3:          # 1.234,56 -> es-UY
        s = s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    elif con_coma > 0.3:
        s = s.str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")


def _a_fecha(serie: pd.Series) -> pd.Series:
    for kwargs in ({"format": "mixed", "dayfirst": True}, {"dayfirst": True}, {}):
        try:
            return pd.to_datetime(serie, errors="coerce", **kwargs)
        except Exception:
            continue
    return pd.Series([pd.NaT] * len(serie), index=serie.index)


def tipar(df: pd.DataFrame) -> tuple[pd.DataFrame, list[tuple[str, str, str]]]:
    """Convierte columnas mal tipadas. Devuelve (df_tipado, [(columna, de, a)])."""
    df = df.copy()
    cambios = []
    for c in df.columns:
        s = df[c]
        if pd.api.types.is_numeric_dtype(s) or pd.api.types.is_datetime64_any_dtype(s):
            continue
        no_nulos = s.dropna()
        if no_nulos.empty:
            continue
        muestra = no_nulos.astype(str).head(2000)

        vals = set(muestra.str.strip().str.lower().unique())
        if vals and vals <= {"si", "sí", "no", "true", "false", "s", "n", "1", "0", "y", "yes"}:
            mapa = {"si": 1, "sí": 1, "s": 1, "true": 1, "y": 1, "yes": 1, "1": 1,
                    "no": 0, "n": 0, "false": 0, "0": 0}
            df[c] = s.astype(str).str.strip().str.lower().map(mapa)
            cambios.append((str(c), "texto", "booleano"))
            continue

        parece_fecha = bool(PAT_FECHA.search(str(c))) or bool(
            muestra.str.match(r"^\s*\d{2,4}[-/.]\d{1,2}[-/.]\d{1,4}").mean() > 0.7)
        if parece_fecha:
            conv = _a_fecha(s)
            if conv.notna().mean() > 0.8:
                df[c] = conv
                cambios.append((str(c), "texto", "fecha"))
                continue

        ceros_izq = muestra.str.match(r"^0\d+$").mean() > 0.1
        parece_numero = muestra.str.match(
            r"^\s*[-+]?\s*[$€US\s]{0,4}\s*\d[\d.,]*\s*%?\s*$").mean() > 0.85
        if not ceros_izq and parece_numero:
            conv = _a_numero(s)
            if conv.notna().mean() > 0.85 and conv.notna().sum() > 0:
                df[c] = conv
                cambios.append((str(c), "texto", "numerico"))
                continue

        if s.nunique(dropna=True) <= max(50, len(s) * 0.02):
            try:
                df[c] = s.astype("category")
            except Exception:
                pass
    return df, cambios


def rol_columna(nombre, serie: pd.Series) -> str:
    """Clasifica el rol de negocio de la columna. Devuelve un código estable
    (no una etiqueta en español) — la interfaz lo traduce con `rol_<codigo>`."""
    n = str(nombre)
    if pd.api.types.is_datetime64_any_dtype(serie):
        return "fecha"
    if PAT_ID.search(n) and serie.nunique(dropna=True) > max(20, len(serie) * 0.5):
        return "identificador"
    if PAT_ID.search(n):
        return "clave_foranea"
    if pd.api.types.is_numeric_dtype(serie):
        if PAT_MONTO.search(n):
            return "metrica_monetaria"
        if serie.dropna().isin([0, 1]).all() and serie.nunique(dropna=True) <= 2:
            return "flag"
        return "metrica"
    if serie.nunique(dropna=True) <= 50:
        return "dimension"
    return "texto_libre"


# ============================================================================
# 3. PERFILADO AVANZADO
# ============================================================================
def perfilar_avanzado(df: pd.DataFrame) -> dict:
    filas = len(df)
    cols = []
    for c in df.columns:
        s = df[c]
        nn = int(s.notna().sum())
        nulos = filas - nn
        uniq = int(s.nunique(dropna=True))
        info = {
            "columna": str(c),
            "dtype": str(s.dtype),
            "rol": rol_columna(c, s),
            "nulos": nulos,
            "nulos_pct": round((nulos / filas * 100) if filas else 0.0, 2),
            "unicos": uniq,
            "unicos_pct": round((uniq / nn * 100) if nn else 0.0, 2),
        }
        try:
            if pd.api.types.is_numeric_dtype(s) and nn:
                d = s.dropna().astype(float)
                q1, q3 = float(d.quantile(0.25)), float(d.quantile(0.75))
                iqr = q3 - q1
                lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                info.update({
                    "min": _num(d.min()), "p25": _num(q1), "mediana": _num(d.median()),
                    "p75": _num(q3), "p95": _num(d.quantile(0.95)), "max": _num(d.max()),
                    "media": _num(d.mean()), "desvio": _num(d.std()) if nn > 1 else 0.0,
                    "ceros": int((d == 0).sum()), "negativos": int((d < 0).sum()),
                    "outliers_iqr": int(((d < lo) | (d > hi)).sum()),
                    "asimetria": _num(d.skew()) if nn > 2 else 0.0,
                })
            elif pd.api.types.is_datetime64_any_dtype(s) and nn:
                d = s.dropna()
                info.update({"min": str(d.min()), "max": str(d.max()),
                            "rango_dias": int((d.max() - d.min()).days)})
            else:
                top = s.astype("string").value_counts(dropna=True).head(5)
                info["top_valores"] = [(str(k), int(v)) for k, v in top.items()]
        except Exception:
            pass
        cols.append(info)
    return {"filas": filas, "columnas": len(df.columns), "detalle": cols}


# ============================================================================
# 4. CALIDAD — issues LANGUAGE-NEUTRAL (codigo + valores)
# ============================================================================
SEVERIDAD_ORDEN = {"critico": 3, "alto": 2, "medio": 1, "bajo": 0}


def calidad(df: pd.DataFrame, prof: dict) -> dict:
    filas = max(prof["filas"], 1)
    issues = []

    def add(sev, codigo, columna, valores=None):
        issues.append({"severidad": sev, "codigo": codigo, "columna": columna,
                       "valores": valores or {}})

    try:
        dup = int(df.duplicated().sum())
        if dup:
            add("critico" if dup / filas > 0.05 else "alto", "duplicados_fila", None,
                {"duplicados": dup, "pct": round(dup / filas * 100, 2)})
    except Exception:
        pass

    for c in prof["detalle"]:
        n, nulp = c["columna"], c["nulos_pct"]
        if nulp >= 95:
            add("critico", "columna_vacia", n, {"pct": nulp})
        elif nulp >= 40:
            add("alto", "nulos_masivos", n, {"pct": nulp})
        elif nulp >= 5:
            add("medio", "nulos", n, {"pct": nulp})

        if c["unicos"] == 1 and c["nulos"] < filas:
            add("medio", "constante", n)

        if c["rol"] in ("dimension", "texto_libre") and c["unicos"] > filas * 0.9 and filas > 100:
            add("medio", "cardinalidad_casi_unica", n,
                {"unicos": c["unicos"], "filas": filas})

        if c.get("negativos", 0) and c["rol"] == "metrica_monetaria":
            add("alto", "montos_negativos", n, {"negativos": c["negativos"]})

        if c.get("outliers_iqr", 0) and c.get("outliers_iqr", 0) / filas > 0.05:
            add("medio", "outliers", n,
                {"outliers": c["outliers_iqr"], "pct": round(c["outliers_iqr"] / filas * 100, 2)})

        if abs(c.get("asimetria", 0) or 0) > 3:
            add("bajo", "asimetria", n, {"valor": round(c["asimetria"], 2)})

        if c.get("ceros", 0) and c.get("ceros", 0) / filas > 0.9:
            add("medio", "casi_todo_ceros", n, {"pct": round(c["ceros"] / filas * 100, 2)})

    malos = [str(c) for c in df.columns
             if re.search(r"[^0-9A-Za-z_]", str(c)) or str(c)[:1].isdigit()]
    if malos:
        add("medio", "nombres_no_aptos_sql", None, {"columnas": malos[:8], "total": len(malos)})

    orden = sorted(issues, key=lambda i: -SEVERIDAD_ORDEN[i["severidad"]])

    completitud = 100 - float(np.mean([c["nulos_pct"] for c in prof["detalle"]] or [0]))
    try:
        unicidad = 100 - (df.duplicated().sum() / filas * 100)
    except Exception:
        unicidad = 100.0
    consistencia = 100 - min(100, len(malos) / max(len(df.columns), 1) * 100)
    n_out = sum(c.get("outliers_iqr", 0) for c in prof["detalle"])
    validez = 100 - min(100, n_out / max(filas * max(len(df.columns), 1), 1) * 100 * 10)
    n_const = sum(1 for c in prof["detalle"] if c["unicos"] <= 1)
    utilidad = 100 - min(100, n_const / max(len(df.columns), 1) * 100)
    criticos = sum(1 for i in issues if i["severidad"] == "critico")
    integridad = max(0.0, 100 - criticos * 15)

    dims = {"completitud": completitud, "unicidad": unicidad, "consistencia": consistencia,
            "validez": validez, "utilidad": utilidad, "integridad": integridad}
    score = float(np.mean(list(dims.values())))
    return {"score": round(score, 1),
            "dimensiones": {k: round(v, 1) for k, v in dims.items()},
            "issues": orden}


# ============================================================================
# 5. CLAVES Y JOINS
# ============================================================================
def claves(df: pd.DataFrame, prof: dict, nombre: str) -> dict:
    filas = max(len(df), 1)
    pks, fks = [], []
    for c in prof["detalle"]:
        col = c["columna"]
        if c["nulos"] == 0 and c["unicos"] == filas and filas > 1:
            pks.append({"columna": col, "tipo": "simple", "confianza": "alta"})
        elif c["unicos"] >= filas * 0.98 and c["nulos_pct"] < 1 and filas > 50:
            pks.append({"columna": col, "tipo": "candidata", "confianza": "media"})
        if c["rol"] in ("clave_foranea", "identificador") and c["unicos"] < filas * 0.9:
            fks.append(col)

    if not pks and filas > 1:
        cands = [c["columna"] for c in prof["detalle"]
                 if c["rol"] in ("clave_foranea", "identificador", "dimension", "fecha")][:6]
        for i in range(len(cands)):
            for j in range(i + 1, len(cands)):
                try:
                    if not df.duplicated(subset=[cands[i], cands[j]]).any():
                        pks.append({"columna": f"{cands[i]} + {cands[j]}",
                                    "tipo": "compuesta", "confianza": "media"})
                        break
                except Exception:
                    continue
            if pks:
                break
    return {"tabla": nombre, "pk": pks, "fk_candidatas": fks}


def joins_sugeridos(tablas: dict[str, pd.DataFrame]) -> list[dict]:
    """Joins entre tablas, por nombre de columna + solapamiento real de valores."""
    sug = []
    nombres = list(tablas.keys())
    for i in range(len(nombres)):
        for j in range(i + 1, len(nombres)):
            a, b = nombres[i], nombres[j]
            da, db = tablas[a], tablas[b]
            comunes = [c for c in da.columns if c in db.columns]
            for c in comunes:
                try:
                    va = set(da[c].dropna().astype(str).unique()[:20000])
                    vb = set(db[c].dropna().astype(str).unique()[:20000])
                    if not va or not vb:
                        continue
                    solape = len(va & vb) / min(len(va), len(vb)) * 100
                    if solape < 20:
                        continue
                    ua, ub = da[c].is_unique, db[c].is_unique
                    card = "1:1" if (ua and ub) else ("1:N" if ua else ("N:1" if ub else "N:N"))
                    sug.append({
                        "izquierda": a, "derecha": b, "columna": str(c),
                        "solape_pct": round(solape, 1), "cardinalidad": card,
                        "riesgo": "alto" if card == "N:N" else ("medio" if solape < 80 else "bajo"),
                        "sql": (f"SELECT a.*, b.*\nFROM {slug(a)} a\n"
                                f"LEFT JOIN {slug(b)} b ON a.{c} = b.{c};"),
                    })
                except Exception:
                    continue
    return sorted(sug, key=lambda s: -s["solape_pct"])[:25]


# ============================================================================
# 6. TIEMPO
# ============================================================================
def analisis_tiempo(df: pd.DataFrame, prof: dict, columna_tiempo=None) -> dict | None:
    fechas = [c["columna"] for c in prof["detalle"] if c["rol"] == "fecha"]
    col = columna_tiempo if (columna_tiempo and columna_tiempo in df.columns) else (
        fechas[0] if fechas else None)
    if not col:
        return None
    s = pd.to_datetime(df[col], errors="coerce").dropna()
    if s.empty:
        return None
    diario = s.dt.floor("D").value_counts().sort_index()
    idx = pd.date_range(diario.index.min(), diario.index.max(), freq="D")
    faltantes = idx.difference(diario.index)
    mensual = s.dt.to_period("M").value_counts().sort_index()
    serie_m = [(str(k), int(v)) for k, v in mensual.items()]
    tendencia = None
    if len(mensual) >= 4:
        y = mensual.values.astype(float)
        x = np.arange(len(y))
        b = np.polyfit(x, y, 1)[0]
        tendencia = ("creciente" if b > y.mean() * 0.02 else
                     "decreciente" if b < -y.mean() * 0.02 else "estable")
    return {
        "columna": col, "desde": str(s.min()), "hasta": str(s.max()),
        "dias_cubiertos": int(diario.shape[0]), "dias_rango": int(len(idx)),
        "dias_faltantes": int(len(faltantes)),
        "primeros_faltantes": [str(d.date()) for d in faltantes[:12]],
        "frescura_dias": int((pd.Timestamp.now().normalize() - s.max().normalize()).days),
        "serie_mensual": serie_m[-24:], "tendencia": tendencia,
        "futuras": int((s > pd.Timestamp.now()).sum()),
    }


# ============================================================================
# 7. TARGET Y FUGA (leakage)
# ============================================================================
def _auc_rank(x, y):
    m = pd.notna(x) & pd.notna(y)
    x, y = np.asarray(x)[m], np.asarray(y)[m]
    npos, nneg = int((y == 1).sum()), int((y == 0).sum())
    if npos == 0 or nneg == 0:
        return None
    r = pd.Series(x).rank().values
    return float((r[y == 1].sum() - npos * (npos + 1) / 2) / (npos * nneg))


def _mi_normalizada(a, b, bins=10):
    def disc(s):
        s = pd.Series(s)
        if pd.api.types.is_numeric_dtype(s) and s.nunique() > bins:
            return pd.qcut(s, bins, duplicates="drop", labels=False)
        return s.astype("string")
    da, db = disc(a), disc(b)
    m = da.notna() & db.notna()
    if m.sum() < 20:
        return None
    tab = pd.crosstab(da[m], db[m]).values.astype(float)
    p = tab / tab.sum()
    pa, pb = p.sum(1, keepdims=True), p.sum(0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        mi = np.nansum(p * np.log2(p / (pa * pb)))
    ha = -np.nansum(pa * np.log2(pa))
    hb = -np.nansum(pb * np.log2(pb))
    den = min(ha, hb)
    return float(mi / den) if den > 0 else None


def analisis_target(df: pd.DataFrame, target: str) -> dict:
    if target not in df.columns:
        return {"error": "columna_inexistente"}
    y = df[target]
    binario = (pd.api.types.is_numeric_dtype(y) and y.dropna().isin([0, 1]).all()
               and y.nunique(dropna=True) == 2)
    tipo = "binario" if binario else ("numerico" if pd.api.types.is_numeric_dtype(y)
                                      else "categorico")
    res = {"target": target, "tipo": tipo, "nulos_pct": round(float(y.isna().mean() * 100), 2)}
    if binario:
        tasa = float(y.mean() * 100)
        res["tasa_positivos_pct"] = round(tasa, 2)
        res["balance"] = ("muy_desbalanceado" if tasa < 5 or tasa > 95
                          else "desbalanceado" if tasa < 20 or tasa > 80 else "razonable")
    elif tipo == "numerico":
        d = y.dropna().astype(float)
        res.update({"media": _num(d.mean()), "mediana": _num(d.median()),
                    "min": _num(d.min()), "max": _num(d.max())})

    ranking, fugas = [], []
    for c in df.columns:
        if str(c) == str(target):
            continue
        s = df[c]
        try:
            if binario and pd.api.types.is_numeric_dtype(s):
                a = _auc_rank(s, y)
                if a is None:
                    continue
                fuerza = abs(a - 0.5) * 2
                ranking.append({"variable": str(c), "metrica": "AUC",
                                "valor": round(a, 4), "fuerza": round(fuerza, 4)})
                if a > 0.985 or a < 0.015:
                    fugas.append({"variable": str(c), "codigo": "fuga_auc_alto",
                                  "valores": {"auc": round(a, 3)}, "riesgo": "critico"})
            elif pd.api.types.is_numeric_dtype(s) and pd.api.types.is_numeric_dtype(y):
                r = float(pd.Series(s).corr(pd.Series(y), method="spearman"))
                if pd.isna(r):
                    continue
                ranking.append({"variable": str(c), "metrica": "spearman",
                                "valor": round(r, 4), "fuerza": round(abs(r), 4)})
                if abs(r) > 0.98:
                    fugas.append({"variable": str(c), "codigo": "fuga_correlacion_alta",
                                  "valores": {"corr": round(r, 3)}, "riesgo": "critico"})
            else:
                mi = _mi_normalizada(s, y)
                if mi is None:
                    continue
                ranking.append({"variable": str(c), "metrica": "im_norm",
                                "valor": round(mi, 4), "fuerza": round(mi, 4)})
                if mi > 0.95:
                    fugas.append({"variable": str(c), "codigo": "fuga_mi_alta",
                                  "valores": {"mi": round(mi, 3)}, "riesgo": "critico"})
        except Exception:
            continue

        if re.search(r"(result|resultad|final|cerrad|pagad|cobrad|churn|baja|estado_fin|post_)",
                     str(c), re.I) and str(c) != str(target):
            fugas.append({"variable": str(c), "codigo": "fuga_nombre_sospechoso",
                          "valores": {}, "riesgo": "revisar"})

    ranking.sort(key=lambda r: -r["fuerza"])
    vistas, limpio = set(), []
    for f in fugas:
        k = (f["variable"], f["riesgo"])
        if k not in vistas:
            vistas.add(k)
            limpio.append(f)
    res["ranking"] = ranking[:30]
    res["fugas"] = limpio[:20]
    return res


# ============================================================================
# 8. FEATURE ENGINEERING AUTOMÁTICO (anti-leakage)
# ============================================================================
def _fx_fecha(df, fechas, add):
    for c in fechas[:5]:
        s = pd.to_datetime(df[c], errors="coerce")
        b = slug(c, 20)
        add(f"{b}_anio", s.dt.year, c, "fx_anio")
        add(f"{b}_mes", s.dt.month, c, "fx_mes")
        add(f"{b}_trimestre", s.dt.quarter, c, "fx_trimestre")
        add(f"{b}_dia_semana", s.dt.dayofweek, c, "fx_dia_semana")
        add(f"{b}_es_finde", (s.dt.dayofweek >= 5).astype("Int8"), c, "fx_es_finde")
        add(f"{b}_dia_mes", s.dt.day, c, "fx_dia_mes")
        add(f"{b}_fin_de_mes", s.dt.is_month_end.astype("Int8"), c, "fx_fin_de_mes")
        add(f"{b}_mes_seno", np.sin(2 * np.pi * s.dt.month / 12), c, "fx_mes_seno")
        add(f"{b}_mes_coseno", np.cos(2 * np.pi * s.dt.month / 12), c, "fx_mes_coseno")
        ref = s.max()
        if pd.notna(ref):
            add(f"{b}_dias_desde_max", (ref - s).dt.days, c, "fx_dias_desde_max",
                apto_series="cuidado")


def _fx_numericas(df, nums, add):
    for c in nums[:25]:
        s = pd.to_numeric(df[c], errors="coerce")
        b = slug(c, 20)
        if s.notna().sum() < 5:
            continue
        if (s.dropna() >= 0).all() and abs(float(s.skew() or 0)) > 1.5:
            add(f"{b}_log1p", np.log1p(s), c, "fx_log1p")
        if s.isna().any():
            add(f"{b}_faltante", s.isna().astype("Int8"), c, "fx_flag_faltante")
        if (s == 0).mean() > 0.05:
            add(f"{b}_es_cero", (s == 0).astype("Int8"), c, "fx_flag_cero")
        try:
            p1, p99 = s.quantile(0.01), s.quantile(0.99)
            if p1 != p99:
                add(f"{b}_wins", s.clip(p1, p99), c, "fx_winsorizado")
                add(f"{b}_quintil", pd.qcut(s, 5, labels=False, duplicates="drop"), c,
                    "fx_quintil", apto_series="cuidado")
        except Exception:
            pass


def _fx_ratios_monetarios(df, prof, add):
    montos = [c["columna"] for c in prof["detalle"] if c["rol"] == "metrica_monetaria"][:4]
    for i in range(len(montos)):
        for j in range(len(montos)):
            if i == j:
                continue
            a, b_ = montos[i], montos[j]
            den = pd.to_numeric(df[b_], errors="coerce").replace(0, np.nan)
            add(f"ratio_{slug(a,14)}_sobre_{slug(b_,14)}",
                pd.to_numeric(df[a], errors="coerce") / den,
                f"{a} / {b_}", "fx_ratio")


def _fx_categoricas_y_texto(df, cats, textos, add):
    for c in cats[:15]:
        s = df[c].astype("string")
        b = slug(c, 20)
        frec = s.map(s.value_counts(normalize=True))
        add(f"{b}_frecuencia", frec, c, "fx_frecuencia_categoria", apto_series="cuidado")
        add(f"{b}_es_raro", (frec < 0.01).astype("Int8"), c, "fx_categoria_rara")

    for c in textos[:5]:
        s = df[c].astype("string")
        b = slug(c, 20)
        add(f"{b}_largo", s.str.len(), c, "fx_largo_texto")
        add(f"{b}_palabras", s.str.count(r"\s+") + 1, c, "fx_cant_palabras")


def _fx_series_temporales(df, fechas, nums, columna_tiempo, claves_grupo, target, add):
    """Lags, medias móviles y variación % — SIEMPRE con `shift(1)`: sin ese
    corrimiento, una "media móvil de los últimos 3 períodos" incluiría el
    período actual, el mismo que se está tratando de predecir. Es la forma
    más común de fuga (leakage) en series temporales.
    """
    tcol = columna_tiempo if (columna_tiempo and columna_tiempo in df.columns) else (
        fechas[0] if fechas else None)
    objetivos = ([target] if (target and target in df.columns and
                              pd.api.types.is_numeric_dtype(df[target])) else nums[:3])
    if not (tcol and objetivos):
        return
    base = df[[tcol]].copy()
    base[tcol] = pd.to_datetime(base[tcol], errors="coerce")
    gk = [g for g in (claves_grupo or []) if g in df.columns]
    orden = df.assign(**{tcol: base[tcol]}).sort_values(gk + [tcol] if gk else [tcol])
    for c in objetivos:
        if c not in df.columns:
            continue
        s = pd.to_numeric(orden[c], errors="coerce")
        b = slug(c, 18)
        g = orden.groupby(gk, observed=True)[c] if gk else None
        for lag in (1, 3, 12):
            v = (g.shift(lag) if g is not None else s.shift(lag))
            add(f"{b}_lag{lag}", pd.Series(v).reindex(df.index), c, "fx_lag",
                {"periodos": lag, "agrupado": bool(gk)})
        for w in (3, 6):
            if g is not None:
                v = g.transform(lambda z, w=w: z.shift(1).rolling(w, min_periods=1).mean())
            else:
                v = s.shift(1).rolling(w, min_periods=1).mean()
            add(f"{b}_media_movil{w}", pd.Series(v).reindex(df.index), c,
                "fx_media_movil", {"ventana": w})
        v = (g.shift(1) if g is not None else s.shift(1))
        prev = pd.Series(v).reindex(df.index)
        add(f"{b}_var_vs_anterior",
            (pd.to_numeric(df[c], errors="coerce") - prev) / prev.replace(0, np.nan),
            c, "fx_variacion_pct")


def generar_features(df: pd.DataFrame, prof: dict, columna_tiempo=None,
                     claves_grupo=None, target=None, tope=200
                     ) -> tuple[pd.DataFrame, list[dict]]:
    """Devuelve (DataFrame de features, diccionario [{feature, origen, codigo,
    parametros, apto_series_temporales}])."""
    out = pd.DataFrame(index=df.index)
    dicc = []

    def add(nombre, serie, origen, codigo, parametros=None, apto_series="si"):
        if len(dicc) >= tope:
            return
        try:
            out[nombre] = serie
            dicc.append({"feature": nombre, "origen": origen, "codigo": codigo,
                         "parametros": parametros or {}, "apto_series_temporales": apto_series})
        except Exception:
            pass

    fechas = [c["columna"] for c in prof["detalle"] if c["rol"] == "fecha"]
    nums = [c["columna"] for c in prof["detalle"]
            if c["rol"] in ("metrica", "metrica_monetaria") and c["columna"] != target]
    cats = [c["columna"] for c in prof["detalle"] if c["rol"] == "dimension"]
    textos = [c["columna"] for c in prof["detalle"] if c["rol"] == "texto_libre"]

    _fx_fecha(df, fechas, add)
    _fx_numericas(df, nums, add)
    _fx_ratios_monetarios(df, prof, add)
    _fx_categoricas_y_texto(df, cats, textos, add)
    _fx_series_temporales(df, fechas, nums, columna_tiempo, claves_grupo, target, add)

    out = out.loc[:, ~out.columns.duplicated()]
    return out, dicc


# ============================================================================
# 9. DDL SQL sugerido
# ============================================================================
TIPO_SQL = {"int64": "BIGINT", "Int64": "BIGINT", "int32": "INT", "Int8": "TINYINT",
            "float64": "DECIMAL(18,4)", "float32": "DECIMAL(18,4)", "bool": "BIT"}


def generar_ddl(nombre: str, prof: dict, ks: dict) -> str:
    lineas = [f"-- Tabla sugerida a partir del perfilado de '{nombre}'",
              f"CREATE TABLE {slug(nombre)} ("]
    campos = []
    for c in prof["detalle"]:
        col, dt = slug(c["columna"], 60), c["dtype"]
        if "datetime" in dt:
            tipo = "DATETIME2"
        elif dt in TIPO_SQL:
            tipo = TIPO_SQL[dt]
        elif "int" in dt.lower():
            tipo = "BIGINT"
        elif "float" in dt.lower():
            tipo = "DECIMAL(18,4)"
        else:
            tipo = "NVARCHAR(400)"
        nn = "NOT NULL" if c["nulos"] == 0 else "NULL"
        campos.append(f"    {col:<40} {tipo:<16} {nn}")
    lineas.append(",\n".join(campos))
    pk = [k for k in ks["pk"] if k["confianza"] == "alta"]
    if pk:
        lineas.append(f"    ,CONSTRAINT PK_{slug(nombre,25)} PRIMARY KEY ({slug(pk[0]['columna'],60)})")
    lineas.append(");")
    return "\n".join(lineas)


# ============================================================================
# ORQUESTADOR
# ============================================================================
def _etapa(nombre, fn, *args, **kwargs):
    """Ejecuta una etapa; si falla, se registra y el resto sigue — el
    perfilado no se cae entero porque una sola columna rara rompe el cálculo
    de asimetría."""
    try:
        return fn(*args, **kwargs), None
    except Exception as exc:
        return None, f"{nombre}: {type(exc).__name__}: {exc}"


def analizar_tabla(nombre: str, df: pd.DataFrame, *, target=None, columna_tiempo=None,
                   claves_grupo=None, con_features=True, muestra=None) -> dict:
    """Corre las 8 etapas sobre una tabla. Nunca lanza — cada etapa que falla
    queda listada en `advertencias` y el resto del análisis sigue.
    """
    advertencias = []
    filas_originales = len(df)
    if muestra and len(df) > muestra:
        df = df.head(muestra)
    elif len(df) > TOPE_FILAS:
        df = df.head(TOPE_FILAS)

    df2, err = _etapa("tipado", tipar, df)
    if err:
        advertencias.append(err)
        df2, cambios = df, []
    else:
        df2, cambios = df2

    prof, err = _etapa("perfilado", perfilar_avanzado, df2)
    if err:
        advertencias.append(err)
        prof = {"filas": len(df2), "columnas": df2.shape[1], "detalle": []}

    cal, err = _etapa("calidad", calidad, df2, prof)
    if err:
        advertencias.append(err)
        cal = {"score": 0, "dimensiones": {}, "issues": []}

    ks, err = _etapa("claves", claves, df2, prof, nombre)
    if err:
        advertencias.append(err)
        ks = {"tabla": nombre, "pk": [], "fk_candidatas": []}

    tiempo, err = _etapa("tiempo", analisis_tiempo, df2, prof, columna_tiempo)
    if err:
        advertencias.append(err)

    objetivo = None
    if target and target in df2.columns:
        objetivo, err = _etapa("target", analisis_target, df2, target)
        if err:
            advertencias.append(err)

    dicc_features = []
    if con_features:
        res, err = _etapa("features", generar_features, df2, prof, columna_tiempo,
                          claves_grupo, target)
        if err:
            advertencias.append(err)
        elif res:
            _, dicc_features = res

    sql, err = _etapa("ddl", generar_ddl, nombre, prof, ks)
    if err:
        advertencias.append(err)
        sql = None

    return {
        "tabla": nombre, "filas_originales": filas_originales,
        "muestreado": filas_originales > len(df2),
        "perfil": prof, "calidad": cal, "claves": ks, "tiempo": tiempo,
        "target": objetivo, "dicc_features": dicc_features,
        "cambios_tipo": cambios, "ddl": sql, "advertencias": advertencias,
    }


# ============================================================================
# 10. TRADUCCIÓN — de códigos language-neutral a texto ES/EN/PT
# ============================================================================
# Vive acá, en el motor, y no en `bi_api` ni en `app/app.py`: Streamlit y el
# .exe consumen el MISMO `analizar_tabla()` y necesitan el MISMO texto para
# los mismos códigos. Tenerlo en dos lugares (uno por interfaz) es el tipo de
# duplicación que ya salió cara en este proyecto — mismo espíritu que
# `mvdg/profiler.py::suggest_rules`, solo que acá el vocabulario es lo
# bastante grande (issues, fuga, features) como para vivir en `mvdg/i18n.py`
# en vez de un dict inline.


def traducir_issue(issue: dict, lang: str) -> dict:
    from .i18n import t
    codigo = issue["codigo"]
    valores = dict(issue.get("valores") or {})
    if codigo == "nombres_no_aptos_sql" and "columnas" in valores:
        valores["lista"] = ", ".join(valores["columnas"])
    try:
        detalle = t(f"qi_{codigo}", lang).format(**valores)
    except (KeyError, IndexError):
        detalle = t(f"qi_{codigo}", lang)
    return {
        "severidad": issue["severidad"],
        "severidad_texto": t(f"sev_{issue['severidad']}", lang),
        "codigo": codigo,
        "columna": issue.get("columna"),
        "detalle": detalle,
        "accion": t(f"qi_{codigo}_accion", lang),
    }


def traducir_perfil(perfil: dict, lang: str) -> dict:
    from .i18n import t
    detalle = [{**c, "rol_texto": t(f"rol_{c['rol']}", lang)} for c in perfil.get("detalle", [])]
    return {**perfil, "detalle": detalle}


def traducir_claves(ks: dict, lang: str) -> dict:
    from .i18n import t
    pk = [{**k, "tipo_texto": t(f"pk_{k['tipo']}", lang),
          "confianza_texto": t(f"confianza_{k['confianza']}", lang)}
          for k in ks.get("pk", [])]
    return {**ks, "pk": pk}


def traducir_joins(joins: list, lang: str) -> list:
    from .i18n import t
    return [{**j, "riesgo_texto": t(f"riesgo_{j['riesgo']}", lang)} for j in joins]


def traducir_tiempo(tiempo: dict | None, lang: str) -> dict | None:
    if not tiempo:
        return tiempo
    from .i18n import t
    out = dict(tiempo)
    if tiempo.get("tendencia"):
        out["tendencia_texto"] = t(f"tendencia_{tiempo['tendencia']}", lang)
    if tiempo.get("dias_faltantes"):
        out["huecos_texto"] = t("de_tiempo_huecos", lang).format(dias=tiempo["dias_faltantes"])
    if tiempo.get("futuras"):
        out["futuras_texto"] = t("de_tiempo_futuras", lang).format(futuras=tiempo["futuras"])
    return out


def traducir_target(objetivo: dict | None, lang: str) -> dict | None:
    if not objetivo or objetivo.get("error"):
        return objetivo
    from .i18n import t
    out = dict(objetivo)
    if objetivo.get("balance"):
        out["balance_texto"] = t(f"balance_{objetivo['balance']}", lang)
    fugas = []
    for f in objetivo.get("fugas", []):
        try:
            texto = t(f["codigo"], lang).format(**(f.get("valores") or {}))
        except (KeyError, IndexError):
            texto = t(f["codigo"], lang)
        fugas.append({**f, "texto": texto})
    out["fugas"] = fugas
    return out


def traducir_features(dicc: list, lang: str) -> list:
    """Traduce cada feature generada. Los códigos `fx_lag` y `fx_media_movil`
    llevan placeholders ({periodos}/{ventana}) que se llenan con los propios
    `parametros` de la feature — sin esto quedaban literalmente "{periodos}
    período(s) atrás" en la pantalla en vez del número real."""
    from .i18n import t
    out = []
    for f in dicc:
        f2 = dict(f)
        params = f.get("parametros") or {}
        try:
            f2["etiqueta"] = t(f["codigo"], lang).format(**params)
        except (KeyError, IndexError):
            f2["etiqueta"] = t(f["codigo"], lang)
        if f.get("apto_series_temporales") == "cuidado":
            clave_cuidado = f"{f['codigo']}_cuidado"
            texto_cuidado = t(clave_cuidado, lang)
            if texto_cuidado != clave_cuidado:  # existe una advertencia específica
                f2["cuidado_texto"] = texto_cuidado
        out.append(f2)
    return out


def traducir_cambios_tipo(cambios: list, lang: str) -> list:
    from .i18n import t
    return [{"columna": c, "de": t(f"tipo_{de}", lang), "a": t(f"tipo_{a}", lang)}
            for c, de, a in cambios]


def traducir_resultado(resultado: dict, lang: str) -> dict:
    """Traduce el resultado language-neutral de `analizar_tabla()`.

    Agrega texto (*_texto, etiqueta, detalle, accion) sin sacar los códigos
    crudos, por si la interfaz los necesita para íconos o para agrupar.
    """
    from .i18n import t
    cal = resultado["calidad"]
    return {
        **resultado,
        "perfil": traducir_perfil(resultado["perfil"], lang),
        "calidad": {
            **cal,
            "dimensiones_texto": {k: t(f"dim_{k}", lang) for k in cal["dimensiones"]},
            "issues": [traducir_issue(i, lang) for i in cal["issues"]],
        },
        "claves": traducir_claves(resultado["claves"], lang),
        "tiempo": traducir_tiempo(resultado["tiempo"], lang),
        "target": traducir_target(resultado["target"], lang),
        "dicc_features": traducir_features(resultado["dicc_features"], lang),
        "cambios_tipo": traducir_cambios_tipo(resultado["cambios_tipo"], lang),
    }
