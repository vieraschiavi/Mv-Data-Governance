# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Registros de Compliance gobernados por ficha.

Hay registros que no son datos de negocio sino **declaraciones**: cada
colaborador declara algo sobre sí mismo en el sistema de Recursos Humanos,
y la organización responde con eso ante un contrato o una auditoría. Dos
son típicos de la industria farmacéutica:

* **Declaración de conflictos de interés** — anual, y además cada vez que
  cambia algo relevante. Todas las preguntas son obligatorias; si una
  respuesta es afirmativa, el detalle también. El campo de fecha de
  vigencia NO se toca: indica cuándo se actualizó la declaración.
* **Registro de vínculo con licenciantes** — quién trabaja en tareas
  asociadas a los acuerdos de licencia/distribución, con qué licenciante
  y desde cuándo. Hay áreas y posiciones que DEBEN declarar su vínculo; el
  resto declara «ninguno»; algunos perfiles (el personal operativo de
  planta, por ejemplo) están exentos.

Lo que se le pide al gobierno de datos es que **quede todo muy claro**:
qué es cada registro, quién lo debe completar, cada cuánto, qué campos
tiene y qué NO se modifica (la **ficha**), y cuando haya acceso a la
fuente, **quién no cumple y qué hay que pedirle** (los **hallazgos**).

Qué hace este módulo:

* ``ficha(tipo, perfil)`` — la ficha del registro, campo por campo.
* ``validar_coi`` / ``validar_licenciantes`` — corren las reglas sobre el
  export del sistema de RR. HH. (y sobre el maestro de colaboradores para
  medir cobertura) y devuelven los hallazgos por colaborador y los
  resultados en el MISMO formato que el motor de calidad, así la cola de
  incidentes del steward los toma sin nada especial.
* ``perfil_activo()`` — la metodología de la organización: áreas y
  posiciones obligadas, exentos, valores especiales del listado, sistema
  fuente, periodicidad. **Se carga desde un archivo local**, no está
  escrita acá: la metodología de un cliente es suya y este repositorio es
  público. Sin perfil, se usa uno genérico que lo dice.

Honestidad: lo que no se puede medir no se inventa. Sin maestro de
colaboradores no hay cobertura (se dice «no medible», no 100 %); sin la
columna de fecha de vigencia, la regla que la controla queda sin medir.
"""
from __future__ import annotations

import copy
import json
import os
import re
import unicodedata
from datetime import datetime

import pandas as pd

from .i18n import t
from .paths import data_dir

TIPOS = ("coi", "licenciantes")
DATASET = {"coi": "registro_conflictos_interes",
           "licenciantes": "registro_licenciantes"}
ARCHIVO_PERFIL = "perfil_compliance.json"
ENV_PERFIL = "MVDG_PERFIL_COMPLIANCE"

#: Un registro de Compliance se exige completo: el umbral por defecto es
#: 100 %. Entre el umbral y 5 puntos debajo, «warn».
UMBRAL = 100.0
MARGEN_WARN = 5.0

#: Perfil genérico: sin nada propio de ninguna organización. Las áreas son
#: un EJEMPLO para que la demo muestre la regla de cobertura, y así lo dice.
PERFIL_GENERICO: dict = {
    "organizacion": "",
    "sistema_fuente": "",
    "dueno": "Compliance",
    "generico": True,
    "coi": {
        "periodicidad_meses": 12,
        "campo_vigencia_no_modificar": "¿Cuándo deben entrar en vigor estos cambios?",
    },
    "licenciantes": {
        "areas_obligadas": [
            {"area": "Comercial", "posiciones": ["*"]},
            {"area": "Legales", "posiciones": ["*"]},
            {"area": "Finanzas", "posiciones": ["Gerente"]},
        ],
        "exentos": ["operativo"],
        "valor_todos": "TODOS",
        "valor_ninguno": "Ninguno",
        "sinonimos_ninguno": ["ninguno", "declaro no tener", "sin relacionamiento",
                              "no tengo"],
        "licenciantes": [],
        "fecha_fin_default": "",
        "campo_vigencia_no_modificar": "¿Cuándo deben entrar en vigor estos cambios?",
    },
}


# ---------------------------------------------------------------------------
# El perfil de la organización
# ---------------------------------------------------------------------------
def _ruta_perfil() -> str:
    return os.environ.get(ENV_PERFIL) or os.path.join(data_dir(), ARCHIVO_PERFIL)


def _fusionar(base: dict, extra: dict) -> dict:
    salida = copy.deepcopy(base)
    for k, v in (extra or {}).items():
        if isinstance(v, dict) and isinstance(salida.get(k), dict):
            salida[k] = _fusionar(salida[k], v)
        else:
            salida[k] = v
    return salida


def validar_perfil(perfil: dict) -> list[str]:
    """Los problemas de un perfil (vacío = sirve)."""
    problemas = []
    if not isinstance(perfil, dict):
        return ["el perfil no es un objeto JSON"]
    lic = perfil.get("licenciantes", {})
    for i, a in enumerate(lic.get("areas_obligadas", []) or []):
        if not isinstance(a, dict) or not str(a.get("area", "")).strip():
            problemas.append(f"areas_obligadas[{i}] sin «area»")
        elif not isinstance(a.get("posiciones", ["*"]), list):
            problemas.append(f"areas_obligadas[{i}].posiciones no es una lista")
    per = perfil.get("coi", {}).get("periodicidad_meses", 12)
    if not isinstance(per, int) or per <= 0:
        problemas.append("coi.periodicidad_meses tiene que ser un entero > 0")
    return problemas


def perfil_activo() -> dict:
    """El perfil vigente: el archivo local si existe y es válido, si no el
    genérico. Nunca rompe: un archivo roto cae al genérico y lo dice en
    ``perfil["aviso"]``."""
    ruta = _ruta_perfil()
    if not os.path.exists(ruta):
        return copy.deepcopy(PERFIL_GENERICO)
    try:
        with open(ruta, encoding="utf-8") as fh:
            propio = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        p = copy.deepcopy(PERFIL_GENERICO)
        p["aviso"] = f"{ruta}: {exc}"
        return p
    problemas = validar_perfil(propio)
    if problemas:
        p = copy.deepcopy(PERFIL_GENERICO)
        p["aviso"] = f"{ruta}: " + "; ".join(problemas)
        return p
    p = _fusionar(PERFIL_GENERICO, propio)
    p["generico"] = False
    return p


def guardar_perfil(perfil: dict) -> str:
    """Guarda el perfil en la carpeta local de datos (nunca en el repo)."""
    problemas = validar_perfil(perfil)
    if problemas:
        raise ValueError("; ".join(problemas))
    ruta = os.path.join(data_dir(), ARCHIVO_PERFIL)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as fh:
        json.dump(perfil, fh, ensure_ascii=False, indent=2)
    return ruta


# ---------------------------------------------------------------------------
# Normalización y mapeo de columnas del export
# ---------------------------------------------------------------------------
def _n(texto) -> str:
    """Minúsculas, sin acentos y sin espacios de más."""
    s = unicodedata.normalize("NFKD", str(texto or "")).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s.strip().lower())


_SINONIMOS = {
    "colaborador": ("colaborador", "empleado", "id empleado", "id_empleado",
                    "legajo", "user id", "userid", "usuario", "person id",
                    "employee id", "matricula", "codigo"),
    "area": ("area", "departamento", "department", "gerencia", "division"),
    "posicion": ("posicion", "puesto", "cargo", "position", "job title", "rol"),
    "fecha_registro": ("fecha registro", "fecha de registro", "fecha de carga",
                       "fecha declaracion", "fecha de la declaracion",
                       "ultima modificacion", "created", "fecha alta registro",
                       "fecha_registro", "registrado"),
    "fecha_vigencia": ("cuando deben entrar en vigor", "fecha de vigencia",
                       "fecha vigencia", "effective date", "fecha efectiva",
                       "vigencia", "fecha_vigencia"),
    "licenciante": ("licenciante", "nombre del licenciante", "licensor",
                    "licenciantes"),
    "fecha_inicio": ("fecha de inicio", "fecha inicio", "inicio", "start date",
                     "fecha_inicio"),
    "fecha_fin": ("fecha de fin", "fecha fin", "fin", "end date", "fecha_fin"),
    "exento": ("exento", "personal operativo", "operativo", "tipo de personal",
               "tipo colaborador"),
    "activo": ("activo", "estado", "status", "vigente"),
}

_SI = {"si", "sí", "yes", "sim", "s", "y", "true", "1", "verdadero"}
_NO = {"no", "n", "false", "0", "falso", "nao", "não"}


def mapear(df: pd.DataFrame, campos: tuple[str, ...]) -> dict[str, str | None]:
    """Qué columna del export es cada campo, por nombre (sin acentos ni
    mayúsculas). Lo que no se encuentra queda en None y se dice."""
    cols = {_n(c): c for c in df.columns}
    salida: dict[str, str | None] = {}
    for campo in campos:
        encontrado = None
        for sin in _SINONIMOS.get(campo, (campo,)):
            for nc, c in cols.items():
                if nc == sin or nc.startswith(sin) or sin in nc:
                    encontrado = c
                    break
            if encontrado:
                break
        salida[campo] = encontrado
    return salida


#: «Sin fin»: el último día que pandas 2 puede representar sin desbordar.
FECHA_SIN_FIN = "2262-04-11"
_ANIO_TOPE = 2262


def _sin_fin(v):
    """Un año más allá del tope de pandas (9999-12-31, 31/12/9999) es «sin
    fin»: se reemplaza por `FECHA_SIN_FIN` antes de parsear."""
    if isinstance(v, str):
        m = re.search(r"(?<!\d)(\d{4})(?!\d)", v)
        if m and int(m.group(1)) > _ANIO_TOPE:
            return FECHA_SIN_FIN
    return v


def _fecha(serie: pd.Series) -> pd.Series:
    """ISO primero (2026-09-10) y después día/mes/año (10/09/2026), que es
    como exporta un sistema configurado en español. Con `dayfirst=True`
    sobre todo, pandas daba vuelta día y mes de las fechas ISO y las
    declaraciones salían vencidas sin estarlo.

    «Sin fecha de fin» suele venir como 9999-12-31, que en pandas 2 queda
    fuera del rango de Timestamp y se volvía NaT: la regla de la fecha de
    fin no se medía. Todo año posterior al tope se fija en `FECHA_SIN_FIN`,
    igual en los datos y en el valor por defecto, así se comparan bien."""
    serie = pd.Series(serie).astype("object").map(_sin_fin)
    iso = pd.to_datetime(serie, errors="coerce", format="ISO8601")
    resto = serie[iso.isna()]
    if len(resto):
        iso = iso.fillna(pd.to_datetime(resto, errors="coerce", dayfirst=True,
                                        format="mixed"))
    return iso


def _vacio(v) -> bool:
    return v is None or (isinstance(v, float) and pd.isna(v)) or not str(v).strip() \
        or str(v).strip().lower() in ("nan", "none", "nat")


def columnas_si_no(df: pd.DataFrame, excluir=()) -> list[str]:
    """Las columnas que son preguntas de Sí/No (todo lo lleno es sí o no)."""
    salida = []
    for c in df.columns:
        if c in excluir:
            continue
        llenos = [_n(v) for v in df[c] if not _vacio(v)]
        if llenos and all(v in _SI | _NO for v in llenos):
            salida.append(c)
    return salida


def columnas_detalle(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns
            if re.search(r"detalle|adicional|especifi|describ|cual|comentario|details",
                         _n(c))]


# ---------------------------------------------------------------------------
# Resultado común
# ---------------------------------------------------------------------------
def _resultado(tipo: str, regla: str, dimension: str, total: int, fallan: int,
               lang: str, columna: str = "", medible: bool = True) -> dict:
    score = 100.0 if total == 0 else round(100.0 * (total - fallan) / total, 2)
    if not medible:
        status = "warn"
    elif score >= UMBRAL:
        status = "pass"
    elif score >= UMBRAL - MARGEN_WARN:
        status = "warn"
    else:
        status = "fail"
    return {"dataset": DATASET[tipo], "rule_id": regla, "column": columna,
            "dimension": dimension, "description": t(f"cmp_r_{regla}", lang),
            "score": score if medible else 0.0, "threshold": UMBRAL,
            "status": status, "evaluados": total, "incumplen": fallan,
            "medible": medible}


def _hallazgo(tipo, regla, dimension, colaborador, detalle, lang,
              severidad="alta") -> dict:
    return {"registro": t(f"cmp_{tipo}_nombre", lang), "regla": regla,
            "dimension": dimension, "severidad": severidad,
            "colaborador": str(colaborador), "detalle": detalle,
            "accion": t(f"cmp_a_{regla}", lang)}


class _Acum:
    """Lo que junta una validación: resultados, hallazgos y notas."""

    def __init__(self, tipo: str, lang: str):
        self.tipo, self.lang = tipo, lang
        self.res: list[dict] = []
        self.hall: list[dict] = []
        self.notas: list[str] = []

    def regla(self, regla, dimension, total, fallan, medible=True):
        self.res.append(_resultado(self.tipo, regla, dimension, total, fallan,
                                   self.lang, medible=medible))

    def no_medible(self, regla, dimension, nota_clave=None):
        self.regla(regla, dimension, 0, 0, medible=False)
        if nota_clave:
            self.notas.append(t(nota_clave, self.lang))

    def hallazgo(self, regla, dimension, colaborador, clave, severidad="alta", **datos):
        self.hall.append(_hallazgo(self.tipo, regla, dimension, colaborador,
                                   t(clave, self.lang).format(**datos), self.lang,
                                   severidad))

    def salida(self, mapeo, **extra) -> dict:
        return {"resultados": pd.DataFrame(self.res),
                "hallazgos": pd.DataFrame(self.hall),
                "mapeo": mapeo, "notas": self.notas, **extra}


_INACTIVO = {"no", "inactivo", "baja", "false", "0"}


def _activos(maestro: pd.DataFrame, col_activo: str | None) -> pd.DataFrame:
    if not col_activo:
        return maestro
    return maestro[~maestro[col_activo].map(_n).isin(_INACTIVO)]


def _vigencia_tocada(ac: _Acum, regla: str, df: pd.DataFrame, fr, fv) -> None:
    """La fecha de vigencia tiene que ser la del registro: si no, alguien
    tocó el campo que el instructivo dice que NO se toca."""
    distintas = (fv.dt.normalize() != fr.dt.normalize()) & fv.notna() & fr.notna()
    ac.regla(regla, "consistency", len(df), int(distintas.sum()))
    for i in df.index[distintas]:
        ac.hallazgo(regla, "consistency", df.at[i, "_col"], "cmp_d_vigencia_modificada",
                    "media", vig=fv[i].date(), reg=fr[i].date())


# ---------------------------------------------------------------------------
# Declaración de conflictos de interés
# ---------------------------------------------------------------------------
def _coi_cobertura(ac: _Acum, df, fr, maestro, meses: int, corte) -> None:
    """COI-01 · cada colaborador activo del maestro declaró en el período."""
    if maestro is None or not len(maestro):
        ac.no_medible("COI-01", "completeness", "cmp_nota_sin_maestro")
        return
    mm = mapear(maestro, ("colaborador", "activo", "exento"))
    if not mm["colaborador"]:
        ac.no_medible("COI-01", "completeness", "cmp_nota_sin_maestro")
        return
    ids = set(_activos(maestro, mm["activo"])[mm["colaborador"]].astype(str).str.strip())
    del_periodo = df
    if fr is not None:
        del_periodo = df[(fr >= corte - pd.DateOffset(months=meses)) & (fr <= corte)]
    faltan = sorted(ids - set(del_periodo["_col"]))
    ac.regla("COI-01", "completeness", len(ids), len(faltan))
    for c in faltan:
        ac.hallazgo("COI-01", "completeness", c, "cmp_d_sin_declaracion", meses=meses)


def _coi_preguntas(ac: _Acum, df, preguntas: list, detalles: list) -> None:
    """COI-02 · todo respondido; COI-03 · un Sí trae su detalle."""
    if not preguntas:
        ac.notas.append(t("cmp_nota_sin_preguntas", ac.lang))
        return
    vacias = df[preguntas].apply(lambda f: [p for p, v in f.items() if _vacio(v)], axis=1)
    malas = vacias[vacias.map(len) > 0]
    ac.regla("COI-02", "completeness", len(df), len(malas))
    for i, faltan in malas.items():
        ac.hallazgo("COI-02", "completeness", df.at[i, "_col"], "cmp_d_preguntas_vacias",
                    n=len(faltan), cuales=", ".join(map(str, faltan[:3])))
    if not detalles:
        ac.no_medible("COI-03", "validity", "cmp_nota_sin_detalle")
        return
    si = df[preguntas].apply(lambda f: any(_n(v) in _SI for v in f), axis=1)
    sin_det = si & df[detalles].apply(lambda f: all(_vacio(v) for v in f), axis=1)
    ac.regla("COI-03", "validity", int(si.sum()), int(sin_det.sum()))
    for i in df.index[sin_det]:
        ac.hallazgo("COI-03", "validity", df.at[i, "_col"], "cmp_d_si_sin_detalle")


def _coi_fechas(ac: _Acum, df, fr, fv, meses: int, corte) -> None:
    """COI-04 · vigencia intacta; COI-05 · la última declaración vigente."""
    if fr is not None and fv is not None:
        _vigencia_tocada(ac, "COI-04", df, fr, fv)
    else:
        ac.no_medible("COI-04", "consistency", "cmp_nota_sin_fechas")
    if fr is None:
        return
    ultima = df.assign(_fr=fr).groupby("_col")["_fr"].max()
    vencidas = ultima[(ultima < corte - pd.DateOffset(months=meses)) | ultima.isna()]
    ac.regla("COI-05", "timeliness", len(ultima), len(vencidas))
    for c, f in vencidas.items():
        ac.hallazgo("COI-05", "timeliness", c, "cmp_d_vencida",
                    fecha="—" if pd.isna(f) else f.date(), meses=meses)


def _duplicados(ac: _Acum, regla: str, df, clave: list) -> None:
    dup = df.duplicated(clave, keep="first")
    ac.regla(regla, "uniqueness", len(df), int(dup.sum()))
    for i in df.index[dup]:
        ac.hallazgo(regla, "uniqueness", df.at[i, "_col"], "cmp_d_duplicado", "baja")


def validar_coi(registros: pd.DataFrame, maestro: pd.DataFrame | None = None,
                perfil: dict | None = None, corte=None,
                lang: str = "es") -> dict:
    """Las reglas de la declaración sobre el export del sistema.

    Devuelve ``{"resultados": DataFrame (formato calidad), "hallazgos":
    DataFrame (uno por colaborador y regla), "mapeo": dict, "notas": list}``.
    """
    perfil = perfil or perfil_activo()
    corte = pd.Timestamp(corte or datetime.now()).normalize()
    meses = int(perfil.get("coi", {}).get("periodicidad_meses", 12))
    mapeo = mapear(registros, ("colaborador", "fecha_registro", "fecha_vigencia"))
    ac = _Acum("coi", lang)
    if mapeo["colaborador"] is None:
        ac.notas.append(t("cmp_nota_sin_colaborador", lang))
        return ac.salida(mapeo)
    df = registros.copy()
    df["_col"] = df[mapeo["colaborador"]].astype(str).str.strip()
    fr = _fecha(df[mapeo["fecha_registro"]]) if mapeo["fecha_registro"] else None
    fv = _fecha(df[mapeo["fecha_vigencia"]]) if mapeo["fecha_vigencia"] else None
    preguntas = columnas_si_no(df, {c for c in mapeo.values() if c})
    detalles = columnas_detalle(df)
    _coi_cobertura(ac, df, fr, maestro, meses, corte)
    _coi_preguntas(ac, df, preguntas, detalles)
    _coi_fechas(ac, df, fr, fv, meses, corte)
    _duplicados(ac, "COI-06", df,
                ["_col"] + ([mapeo["fecha_registro"]] if mapeo["fecha_registro"] else []))
    return ac.salida(mapeo, preguntas=preguntas, detalles=detalles)


# ---------------------------------------------------------------------------
# Registro de vínculo con licenciantes
# ---------------------------------------------------------------------------
def es_obligado(area, posicion, perfil: dict) -> bool:
    """Si esa área y posición deben declarar su vínculo según el perfil.

    Una posición «*» es «todo el equipo». Si no, basta que el texto de la
    posición contenga alguna de las del perfil («Gerente de Planta» entra
    por «Gerente»), comparando sin acentos ni mayúsculas."""
    a, p = _n(area), _n(posicion)
    for regla in perfil.get("licenciantes", {}).get("areas_obligadas", []):
        if _n(regla.get("area")) != a:
            continue
        posiciones = regla.get("posiciones", ["*"]) or ["*"]
        if "*" in posiciones or any(_n(x) and _n(x) in p for x in posiciones):
            return True
    return False


def _es_exento(fila: dict, mm: dict, perfil: dict) -> bool:
    exentos = [_n(x) for x in perfil.get("licenciantes", {}).get("exentos", [])]
    textos = [_n(fila.get(mm[c])) for c in ("exento", "posicion", "area") if mm.get(c)]
    if mm.get("exento") and _n(fila.get(mm["exento"])) in _SI:
        return True
    return any(e and e in txt for e in exentos for txt in textos)


def _es_ninguno(valor, perfil: dict) -> bool:
    v = _n(valor)
    lic = perfil.get("licenciantes", {})
    return v == _n(lic.get("valor_ninguno")) or any(
        s and s in v for s in map(_n, lic.get("sinonimos_ninguno", [])))


def _clasificar_maestro(maestro, mm: dict, perfil: dict) -> pd.DataFrame:
    """El maestro activo con dos marcas: exento y obligado."""
    m = _activos(maestro, mm["activo"]).copy()
    m["_col"] = m[mm["colaborador"]].astype(str).str.strip()
    filas = m.to_dict("records")
    m["_exento"] = [_es_exento(f, mm, perfil) for f in filas]
    m["_obligado"] = [
        (not ex) and es_obligado(f.get(mm["area"]),
                                 f.get(mm["posicion"]) if mm["posicion"] else "", perfil)
        for f, ex in zip(filas, m["_exento"], strict=False)]
    return m


def _lic_cobertura(ac: _Acum, df, maestro, perfil: dict) -> None:
    """LIC-01 obligados registrados · LIC-02 obligado «sin vínculo» ·
    LIC-03 el resto declaró (aunque sea «ninguno»)."""
    if maestro is None or not len(maestro):
        ac.no_medible("LIC-01", "completeness")
        ac.no_medible("LIC-03", "completeness", "cmp_nota_sin_maestro")
        return
    mm = mapear(maestro, ("colaborador", "area", "posicion", "exento", "activo"))
    if not (mm["colaborador"] and mm["area"]):
        ac.notas.append(t("cmp_nota_maestro_sin_area", ac.lang))
        return
    m = _clasificar_maestro(maestro, mm, perfil)
    registrados = set(df["_col"])
    obligados = m[m["_obligado"]]
    sin_o = obligados[~obligados["_col"].isin(registrados)]
    ac.regla("LIC-01", "completeness", len(obligados), len(sin_o))
    for f in sin_o.to_dict("records"):
        ac.hallazgo("LIC-01", "completeness", f["_col"], "cmp_d_obligado_sin_registro",
                    "critica", area=f.get(mm["area"], ""),
                    pos=f.get(mm["posicion"], "") if mm["posicion"] else "")
    solo_ninguno = {c for c, g in df.groupby("_col") if g["_ninguno"].all()}
    o_ninguno = obligados[obligados["_col"].isin(solo_ninguno)]
    ac.regla("LIC-02", "consistency", int(obligados["_col"].isin(registrados).sum()),
             len(o_ninguno))
    for f in o_ninguno.to_dict("records"):
        ac.hallazgo("LIC-02", "consistency", f["_col"], "cmp_d_obligado_ninguno", "media",
                    area=f.get(mm["area"], ""))
    resto = m[~m["_obligado"] & ~m["_exento"]]
    sin_r = resto[~resto["_col"].isin(registrados)]
    ac.regla("LIC-03", "completeness", len(resto), len(sin_r))
    for f in sin_r.to_dict("records"):
        ac.hallazgo("LIC-03", "completeness", f["_col"], "cmp_d_resto_sin_registro", "media")
    if int(m["_exento"].sum()):
        ac.notas.append(t("cmp_nota_exentos", ac.lang).format(n=int(m["_exento"].sum())))


def _lic_valores(ac: _Acum, df, lic_cfg: dict) -> None:
    """LIC-04 licenciante válido · LIC-05 «TODOS»/«ninguno» sin mezclar."""
    permitidos = {_n(x) for x in lic_cfg.get("licenciantes", [])}
    especiales = {_n(lic_cfg.get("valor_todos"))}

    def invalido(fila) -> bool:
        v = fila["_lic"]
        if _vacio(v):
            return True
        if fila["_ninguno"] or _n(v) in especiales:
            return False
        return bool(permitidos) and _n(v) not in permitidos
    inval = df.apply(invalido, axis=1)
    ac.regla("LIC-04", "validity", len(df), int(inval.sum()))
    for i in df.index[inval]:
        ac.hallazgo("LIC-04", "validity", df.at[i, "_col"], "cmp_d_licenciante_invalido",
                    valor=df.at[i, "_lic"] or "—")
    if not permitidos:
        ac.notas.append(t("cmp_nota_sin_listado", ac.lang))
    mezclas = [c for c, g in df.groupby("_col")
               if len(g) > 1 and (g["_todos"].any() or g["_ninguno"].any())]
    ac.regla("LIC-05", "consistency", df["_col"].nunique(), len(mezclas))
    for c in mezclas:
        ac.hallazgo("LIC-05", "consistency", c, "cmp_d_mezcla", "media")


def _lic_fechas(ac: _Acum, df, mapeo: dict, lic_cfg: dict, corte) -> None:
    """LIC-06 inicio cargado · LIC-07 fin por defecto intacto · LIC-08
    vigencia intacta."""
    if mapeo["fecha_inicio"]:
        fi = _fecha(df[mapeo["fecha_inicio"]])
        mal = (~df["_ninguno"]) & (fi.isna() | (fi > corte))
        ac.regla("LIC-06", "validity", int((~df["_ninguno"]).sum()), int(mal.sum()))
        for i in df.index[mal]:
            ac.hallazgo("LIC-06", "validity", df.at[i, "_col"], "cmp_d_inicio", "media")
    ff = _fecha(df[mapeo["fecha_fin"]]) if mapeo["fecha_fin"] else None
    if ff is not None and ff.notna().any():
        default = lic_cfg.get("fecha_fin_default") or ""
        valor_def = _fecha(pd.Series([default])).iloc[0] if default else ff.mode().iloc[0]
        if not default:
            ac.notas.append(t("cmp_nota_fin_moda", ac.lang).format(fecha=valor_def.date()))
        modificada = ff.notna() & (ff != valor_def)
        ac.regla("LIC-07", "consistency", len(df), int(modificada.sum()))
        for i in df.index[modificada]:
            ac.hallazgo("LIC-07", "consistency", df.at[i, "_col"], "cmp_d_fin", "baja",
                        fecha=ff[i].date(), defecto=valor_def.date())
    if mapeo["fecha_registro"] and mapeo["fecha_vigencia"]:
        _vigencia_tocada(ac, "LIC-08", df, _fecha(df[mapeo["fecha_registro"]]),
                         _fecha(df[mapeo["fecha_vigencia"]]))


def validar_licenciantes(registros: pd.DataFrame,
                         maestro: pd.DataFrame | None = None,
                         perfil: dict | None = None, corte=None,
                         lang: str = "es") -> dict:
    """Las reglas del registro de licenciantes sobre el export del sistema."""
    perfil = perfil or perfil_activo()
    lic_cfg = perfil.get("licenciantes", {})
    corte = pd.Timestamp(corte or datetime.now()).normalize()
    mapeo = mapear(registros, ("colaborador", "licenciante", "fecha_inicio",
                               "fecha_fin", "fecha_registro", "fecha_vigencia"))
    ac = _Acum("licenciantes", lang)
    col_c, col_l = mapeo["colaborador"], mapeo["licenciante"]
    if col_c is None or col_l is None:
        ac.notas.append(t("cmp_nota_sin_colaborador", lang))
        return ac.salida(mapeo)
    df = registros.copy()
    df["_col"] = df[col_c].astype(str).str.strip()
    df["_lic"] = df[col_l].astype(str).str.strip()
    df["_ninguno"] = df[col_l].map(lambda v: _es_ninguno(v, perfil))
    df["_todos"] = df[col_l].map(lambda v: _n(v) == _n(lic_cfg.get("valor_todos")))
    _lic_cobertura(ac, df, maestro, perfil)
    _lic_valores(ac, df, lic_cfg)
    _lic_fechas(ac, df, mapeo, lic_cfg, corte)
    _duplicados(ac, "LIC-09", df, ["_col", "_lic"])
    return ac.salida(mapeo)


# ---------------------------------------------------------------------------
# La ficha
# ---------------------------------------------------------------------------
REGLAS = {
    "coi": ("COI-01", "COI-02", "COI-03", "COI-04", "COI-05", "COI-06"),
    "licenciantes": ("LIC-01", "LIC-02", "LIC-03", "LIC-04", "LIC-05", "LIC-06",
                     "LIC-07", "LIC-08", "LIC-09"),
}


def _texto_areas(perfil: dict, lang: str) -> str:
    partes = []
    for a in perfil.get("licenciantes", {}).get("areas_obligadas", []):
        pos = a.get("posiciones", ["*"]) or ["*"]
        detalle = t("cmp_todo_equipo", lang) if "*" in pos else "; ".join(pos)
        if a.get("nota"):
            detalle += f" ({a['nota']})"
        partes.append(f"{a['area']}: {detalle}")
    return " · ".join(partes) or "—"


def ficha(tipo: str, perfil: dict | None = None, lang: str = "es") -> pd.DataFrame:
    """La ficha del registro, campo por campo, lista para mostrar y exportar."""
    if tipo not in TIPOS:
        raise ValueError(f"tipo desconocido: {tipo}")
    perfil = perfil or perfil_activo()
    sistema = perfil.get("sistema_fuente") or t("cmp_sin_definir", lang)
    cfg = perfil.get(tipo, {})
    filas = [
        (t("cmp_f_registro", lang), t(f"cmp_{tipo}_nombre", lang)),
        (t("cmp_f_dataset", lang), DATASET[tipo]),
        (t("cmp_f_proposito", lang), t(f"cmp_{tipo}_proposito", lang)),
        (t("cmp_f_sistema", lang), sistema),
        (t("cmp_f_dueno", lang), perfil.get("dueno") or "Compliance"),
        (t("cmp_f_quien", lang), t(f"cmp_{tipo}_quien", lang)),
    ]
    if tipo == "coi":
        filas.append((t("cmp_f_periodicidad", lang), t("cmp_coi_periodicidad", lang)
                      .format(meses=cfg.get("periodicidad_meses", 12))))
    else:
        filas += [
            (t("cmp_f_obligados", lang), _texto_areas(perfil, lang)),
            (t("cmp_f_resto", lang), t("cmp_lic_resto", lang).format(
                ninguno=cfg.get("valor_ninguno", "Ninguno"))),
            (t("cmp_f_exentos", lang), ", ".join(cfg.get("exentos", [])) or "—"),
            (t("cmp_f_valores", lang), t("cmp_lic_valores", lang).format(
                todos=cfg.get("valor_todos", "TODOS"),
                ninguno=cfg.get("valor_ninguno", "Ninguno"))),
            (t("cmp_f_periodicidad", lang), t("cmp_lic_periodicidad", lang)),
        ]
    # Cómo se completa en el sistema, paso a paso, si el perfil lo trae: es
    # el instructivo de la organización, no algo que el programa sepa.
    pasos = cfg.get("pasos") or []
    if pasos:
        filas.append((t("cmp_f_pasos", lang),
                      " → ".join(f"{i}. {p}" for i, p in enumerate(pasos, 1))))
    filas += [
        (t("cmp_f_campos", lang), t(f"cmp_{tipo}_campos", lang)),
        (t("cmp_f_no_modificar", lang), t(f"cmp_{tipo}_no_modificar", lang).format(
            campo=cfg.get("campo_vigencia_no_modificar", ""))),
        (t("cmp_f_riesgo", lang), t(f"cmp_{tipo}_riesgo", lang)),
        (t("cmp_f_reglas", lang), " · ".join(
            f"{r} {t(f'cmp_r_{r}', lang)}" for r in REGLAS[tipo])),
        (t("cmp_f_fuente_perfil", lang),
         t("cmp_perfil_generico", lang) if perfil.get("generico")
         else t("cmp_perfil_propio", lang).format(org=perfil.get("organizacion") or "—")),
    ]
    return pd.DataFrame(filas, columns=[t("cmp_col_campo", lang), t("cmp_col_valor", lang)])


def reglas_df(tipo: str, lang: str = "es") -> pd.DataFrame:
    """Cada regla con qué controla y qué acción dispara."""
    return pd.DataFrame([{"regla": r, "control": t(f"cmp_r_{r}", lang),
                          "accion": t(f"cmp_a_{r}", lang)} for r in REGLAS[tipo]])


def resumen(resultado: dict) -> dict:
    """KPIs para la cabecera: reglas que cumplen y colaboradores a contactar."""
    r = resultado.get("resultados", pd.DataFrame())
    h = resultado.get("hallazgos", pd.DataFrame())
    medibles = r[r["medible"]] if len(r) else r
    return {
        "reglas": int(len(r)),
        "reglas_ok": int((medibles["status"] == "pass").sum()) if len(medibles) else 0,
        "no_medibles": int((~r["medible"]).sum()) if len(r) else 0,
        "colaboradores_a_contactar": int(h["colaborador"].nunique()) if len(h) else 0,
        "hallazgos": int(len(h)),
    }


# ---------------------------------------------------------------------------
# Demo 100 % sintética
# ---------------------------------------------------------------------------
def demo(corte=None) -> dict[str, pd.DataFrame]:
    """Maestro y exports sintéticos con defectos inyectados a propósito.

    Nombres de colaborador inventados (C001…), ningún dato real. Cada
    defecto está para que una regla tenga algo que mostrar.
    """
    corte = pd.Timestamp(corte or "2026-09-30")
    areas = [("Comercial", "Representante"), ("Comercial", "Gerente de Producto"),
             ("Legales", "Abogado"), ("Finanzas", "Gerente"), ("Finanzas", "Analista"),
             ("IT", "Soporte"), ("Planta", "Operativo"), ("Marketing", "Analista")]
    filas = []
    for i in range(1, 41):
        area, pos = areas[i % len(areas)]
        filas.append({"Colaborador": f"C{i:03d}", "Área": area, "Posición": pos,
                      "Activo": "No" if i == 40 else "Sí"})
    maestro = pd.DataFrame(filas)

    coi = []
    for i in range(1, 38):                                 # 38 y 39 no declararon
        reg = corte - pd.Timedelta(days=20 + i * 3)
        if i == 5:
            reg = corte - pd.Timedelta(days=500)           # vencida
        f = {"Colaborador": f"C{i:03d}", "Fecha registro": reg.date().isoformat(),
             "¿Cuándo deben entrar en vigor estos cambios?": reg.date().isoformat(),
             "¿Tiene participación en empresas del sector?": "No",
             "¿Tiene familiares en proveedores o clientes?": "No",
             "¿Recibe ingresos de terceros vinculados?": "No",
             "Detalle": ""}
        if i == 7:
            f["¿Tiene familiares en proveedores o clientes?"] = "Sí"   # sin detalle
        if i == 9:
            f["¿Tiene familiares en proveedores o clientes?"] = "Sí"
            f["Detalle"] = "Primo en distribuidora"
        if i == 11:
            f["¿Recibe ingresos de terceros vinculados?"] = ""         # sin responder
        if i == 13:
            f["¿Cuándo deben entrar en vigor estos cambios?"] = "2026-01-01"  # tocada
        coi.append(f)
    coi.append(dict(coi[2]))                                # duplicado de C003
    lic = []
    for fila in filas[:36]:
        c, area, pos = fila["Colaborador"], fila["Área"], fila["Posición"]
        if c in ("C002", "C010"):                           # obligados sin registro
            continue
        inicio = (corte - pd.Timedelta(days=90)).date().isoformat()
        base = {"Colaborador": c, "Fecha de inicio": inicio,
                "Fecha de fin": "9999-12-31", "Fecha registro": inicio,
                "¿Cuándo deben entrar en vigor estos cambios?": inicio}
        if area == "Comercial":
            lic.append({**base, "Nombre del licenciante": "Licenciante A"})
            if c == "C009":
                lic.append({**base, "Nombre del licenciante": "TODOS"})   # mezcla
        elif area == "Legales":
            lic.append({**base, "Nombre del licenciante": "TODOS"})
        elif area == "Finanzas" and pos == "Gerente":
            lic.append({**base, "Nombre del licenciante":
                        "Declaro no tener relacionamiento con Licenciantes"})
        elif area == "Planta":
            continue                                        # exentos
        else:
            lic.append({**base, "Nombre del licenciante": "Ninguno"})
    lic[0]["Fecha de fin"] = "2026-06-30"                   # fin tocada
    lic[1]["Nombre del licenciante"] = ""                   # vacío
    return {"maestro": maestro, "coi": pd.DataFrame(coi),
            "licenciantes": pd.DataFrame(lic)}


# ---------------------------------------------------------------------------
# Exportar: una sola planilla que se pueda mandar a Compliance
# ---------------------------------------------------------------------------
def a_excel(tipo: str, resultado: dict | None, perfil: dict | None = None,
            lang: str = "es") -> bytes:
    """Ficha, reglas, resultados y hallazgos del registro, en un Excel.

    Es el entregable que se manda: la ficha arriba dice qué es el registro
    y qué no se toca, y la hoja de hallazgos dice a quién pedirle qué."""
    import io

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        ficha(tipo, perfil, lang).to_excel(xw, sheet_name="Ficha", index=False)
        reglas_df(tipo, lang).to_excel(xw, sheet_name="Reglas", index=False)
        if resultado:
            r = resultado.get("resultados", pd.DataFrame())
            if len(r):
                r.drop(columns=[c for c in ("dataset",) if c in r.columns]) \
                    .to_excel(xw, sheet_name="Resultados", index=False)
            h = resultado.get("hallazgos", pd.DataFrame())
            (h if len(h) else pd.DataFrame(
                [{"detalle": t("cmp_sin_hallazgos", lang)}])) \
                .to_excel(xw, sheet_name="Hallazgos", index=False)
            notas = resultado.get("notas") or []
            if notas:
                pd.DataFrame({"nota": notas}).to_excel(xw, sheet_name="Notas",
                                                      index=False)
    return buf.getvalue()


def ficha_steward(tipo: str, perfil: dict | None = None) -> dict:
    """La ficha de steward del registro, para que la cola de incidentes
    abra un incidente por cada regla que falla (ver `steward`).

    Dueño: el del perfil (Compliance por defecto). Criticidad alta y PII:
    son declaraciones personales de los colaboradores."""
    from . import steward

    perfil = perfil or perfil_activo()
    base = steward.ficha_base({"dataset": DATASET[tipo],
                               "owner": perfil.get("dueno") or "Compliance",
                               "steward": perfil.get("dueno") or "Compliance",
                               "domain": "Compliance", "classification": "PII"})
    base["criticidad"] = "alta"
    return base
