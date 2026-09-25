# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · El espacio del Data Steward.

Lo que un Data Steward necesita para trabajar TODOS los días, en un solo
lugar y sin salir del motor (se importa y se prueba sin Streamlit):

* **Ficha de steward** por dataset: dueño de negocio, data steward,
  custodio técnico, dominio, criticidad, SLA de frescura (horas), SLA de
  calidad (umbral por cada una de las 6 dimensiones), sensibilidad (PII,
  confidencial) y estado de certificación
  (borrador → en revisión → certificado → deprecado) con quién y cuándo.
* **Cola de incidentes de calidad**: cada regla que falla abre un incidente
  con severidad, responsable (el steward del dataset), estado, fecha y SLA
  de resolución. Si la regla vuelve a pasar, el incidente se cierra solo
  (y queda registrado quién lo cerró: el sistema).
* **Registro de cambios de criterio** (auditoría): cada vez que cambia una
  regla/umbral de calidad, una definición del glosario, un contrato o la
  certificación, queda una entrada con antes/después, quién, cuándo y por qué.
* **Tablero**: mis datasets, pendientes de certificación, incidentes
  abiertos, datasets sin dueño y vencimientos de SLA.

Persistencia local y APPEND-ONLY (mismo directorio que el resto,
``data_dir()``): nada se pisa. Una ficha nueva es una VERSIÓN nueva; un
cambio de estado de un incidente es un EVENTO nuevo; el estado vigente es
siempre el último. Así el historial completo queda disponible para una
auditoría — que es justamente lo que se le pide a un steward.

Honestidad de los datos: lo que no se sabe no se inventa. Un dataset sin
dueño en el catálogo figura "sin dueño" hasta que alguien lo asigne; un
refresco que no se puede traducir a horas deja el SLA de frescura en 0
("sin definir") en vez de inventar un número.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone

import pandas as pd

from .paths import data_dir

DIMENSIONES = ("completeness", "uniqueness", "validity", "consistency",
               "timeliness", "accuracy")
CRITICIDADES = ("alta", "media", "baja")
ESTADOS_CERT = ("borrador", "en_revision", "certificado", "deprecado")
#: Qué estado puede seguir a cuál. Deprecado es terminal: un dataset que se
#: retiró no vuelve a certificarse, se da de alta otro.
TRANSICIONES_CERT = {
    "borrador": ("en_revision", "deprecado"),
    "en_revision": ("borrador", "certificado", "deprecado"),
    "certificado": ("en_revision", "deprecado"),
    "deprecado": (),
}
SEVERIDADES = ("critica", "alta", "media", "baja")
#: SLA de resolución por severidad, en horas.
SLA_RESOLUCION_H = {"critica": 24, "alta": 72, "media": 168, "baja": 336}
ESTADOS_INC = ("abierto", "en_curso", "resuelto")
TRANSICIONES_INC = {
    "abierto": ("en_curso", "resuelto"),
    "en_curso": ("abierto", "resuelto"),
    "resuelto": ("abierto",),          # reabrir
}
TIPOS_CAMBIO = ("regla_calidad", "glosario", "definicion", "contrato",
                "ficha", "certificacion")
#: Umbral de calidad por defecto cuando el dataset no tiene reglas en esa
#: dimensión (con reglas, se hereda el umbral más exigente de ellas).
SLA_CALIDAD_DEFAULT = 95.0
SISTEMA = "sistema"

#: Campos editables de la ficha (la certificación va por su propio flujo).
CAMPOS_FICHA = ("dueno_negocio", "data_steward", "custodio_tecnico", "dominio",
                "criticidad", "sla_frescura_h", "sla_calidad", "pii",
                "confidencial")

_F_FICHAS = "steward_fichas.json"
_F_INCIDENTES = "steward_incidentes.json"
_F_CAMBIOS = "steward_cambios.json"


class StewardError(ValueError):
    """Error de validación del espacio del steward.

    ``clave`` identifica el motivo para que la pantalla lo muestre traducido
    (``stw_err_<clave>`` en i18n); el texto es el detalle para quien usa el
    motor directo. Hereda de ValueError: quien ya atrapaba ValueError sigue
    funcionando igual."""

    def __init__(self, clave: str, mensaje: str):
        super().__init__(mensaje)
        self.clave = clave


# ---------------------------------------------------------------------------
# Persistencia append-only
# ---------------------------------------------------------------------------

def _ruta(nombre: str) -> str:
    return os.path.join(data_dir(), nombre)


def leer_registros(nombre: str) -> list[dict]:
    """Los registros de un libro (lista vacía si no existe o está roto)."""
    ruta = _ruta(nombre)
    if not os.path.exists(ruta):
        return []
    try:
        with open(ruta, encoding="utf-8") as fh:
            datos = json.load(fh)
    except (json.JSONDecodeError, OSError):
        return []
    return datos if isinstance(datos, list) else []


def agregar_registro(nombre: str, registro: dict) -> dict:
    """Agrega AL FINAL. Nunca reescribe ni borra un registro anterior."""
    registros = leer_registros(nombre)
    registros.append(registro)
    ruta = _ruta(nombre)
    tmp = ruta + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(registros, fh, ensure_ascii=False, indent=2, default=str)
    os.replace(tmp, ruta)
    return registro


def _dt(valor=None) -> datetime:
    """Normaliza a datetime con zona UTC (``None`` = ahora)."""
    if valor is None:
        return datetime.now(timezone.utc)
    if isinstance(valor, str):
        valor = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    elif isinstance(valor, pd.Timestamp):
        valor = valor.to_pydatetime()
    elif not isinstance(valor, datetime):          # date
        valor = datetime(valor.year, valor.month, valor.day)
    return valor if valor.tzinfo else valor.replace(tzinfo=timezone.utc)


def _iso(valor=None) -> str:
    return _dt(valor).isoformat(timespec="seconds")


def _quien(quien: str) -> str:
    quien = (quien or "").strip()
    if not quien:
        raise StewardError("sin_quien", "Falta quién hace el cambio (nombre del responsable).")
    return quien


# ---------------------------------------------------------------------------
# Registro de cambios de criterio de negocio (auditoría)
# ---------------------------------------------------------------------------

def registrar_cambio(tipo: str, objeto: str, antes, despues, quien: str,
                     motivo: str = "", dataset: str = "",
                     ahora=None) -> dict | None:
    """Deja constancia de un cambio de criterio. Si antes == después no hay
    cambio y no se registra nada (devuelve ``None``)."""
    if tipo not in TIPOS_CAMBIO:
        raise StewardError("tipo_cambio", f"Tipo de cambio inválido: {tipo}")
    antes_s = _texto(antes)
    despues_s = _texto(despues)
    if antes_s == despues_s:
        return None
    return agregar_registro(_F_CAMBIOS, {
        "fecha": _iso(ahora), "tipo": tipo, "dataset": dataset or "",
        "objeto": objeto, "antes": antes_s, "despues": despues_s,
        "quien": _quien(quien), "motivo": (motivo or "").strip(),
    })


def _texto(valor) -> str:
    if valor is None:
        return ""
    if isinstance(valor, (dict, list)):
        return json.dumps(valor, ensure_ascii=False, sort_keys=True)
    return str(valor)


_COLS_CAMBIOS = ["fecha", "tipo", "dataset", "objeto", "antes", "despues",
                 "quien", "motivo"]


def cambios_df(datasets=None, incluir_generales: bool = True) -> pd.DataFrame:
    """El registro de cambios, del más nuevo al más viejo.

    ``datasets`` acota a esos datasets; ``incluir_generales`` decide si
    entran los cambios que no son de un dataset (p. ej. un término del
    glosario). Con datos propios cargados va en ``False``: los términos del
    glosario de la demo no son del cliente.
    """
    filas = leer_registros(_F_CAMBIOS)
    if datasets is not None:
        permitidos = set(datasets)
        filas = [f for f in filas if f.get("dataset") in permitidos
                 or (incluir_generales and not f.get("dataset"))]
    df = pd.DataFrame(filas, columns=_COLS_CAMBIOS)
    return df.iloc[::-1].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Ficha de steward
# ---------------------------------------------------------------------------

def horas_de_refresco(refresh: str) -> int:
    """Traduce el refresco del catálogo a horas. 0 = no se puede saber."""
    r = str(refresh or "").lower()
    for claves, horas in ((("hour", "hora"), 1),
                          (("daily", "diari", "dia", "día"), 24),
                          (("week", "seman"), 168),
                          (("month", "mensual", "mes"), 720)):
        if any(c in r for c in claves):
            return horas
    return 0


def _criticidad_de(clasificacion: str) -> str:
    c = str(clasificacion or "")
    if c in ("PII", "Confidencial"):
        return "alta"
    if c == "Interna":
        return "media"
    return "baja"


def _sla_calidad_base(dataset: str, results: pd.DataFrame | None) -> dict:
    sla = {d: SLA_CALIDAD_DEFAULT for d in DIMENSIONES}
    if results is not None and len(results):
        sub = results[results["dataset"] == dataset]
        for dim, umbral in sub.groupby("dimension")["threshold"].max().items():
            if dim in sla:
                sla[dim] = float(umbral)
    return sla


def ficha_base(fila_catalogo: dict, results: pd.DataFrame | None = None,
               dictionary: pd.DataFrame | None = None,
               asignacion: dict | None = None) -> dict:
    """La ficha que el programa PROPONE, desde el catálogo real.

    Dueño y steward: los del organigrama si alguien los asignó en
    Responsables; si no, los del catálogo. Nada de esto se inventa: con
    datos propios el catálogo no trae dueño, y la ficha queda sin dueño.
    """
    ds = str(fila_catalogo.get("dataset", ""))
    asignacion = asignacion or {}
    pii = False
    if dictionary is not None and len(dictionary) and "pii" in dictionary.columns:
        pii = bool(dictionary.loc[dictionary["dataset"] == ds, "pii"]
                   .fillna(False).astype(bool).any())
    clasif = str(fila_catalogo.get("classification", "") or "")
    pii = pii or clasif == "PII"
    return {
        "dataset": ds,
        "dueno_negocio": str(asignacion.get("owner_name") or fila_catalogo.get("owner") or ""),
        "data_steward": str(asignacion.get("steward_name")
                            or fila_catalogo.get("steward") or ""),
        "custodio_tecnico": "",
        "dominio": str(fila_catalogo.get("domain", "") or ""),
        "criticidad": _criticidad_de(clasif),
        "sla_frescura_h": horas_de_refresco(fila_catalogo.get("refresh", "")),
        "sla_calidad": _sla_calidad_base(ds, results),
        "pii": pii,
        "confidencial": clasif in ("Confidencial", "PII"),
        "estado_cert": "borrador",
        "cert_por": "", "cert_en": "",
        "version": 0, "guardado_por": "", "guardado_en": "", "motivo": "",
        "origen": "propuesta",
    }


def historial_ficha(dataset: str) -> list[dict]:
    """Todas las versiones guardadas de la ficha, de la primera a la última."""
    return [r for r in leer_registros(_F_FICHAS) if r.get("dataset") == dataset]


def ficha_vigente(dataset: str, base: dict | None = None) -> dict:
    """La última versión guardada; si nunca se guardó, la propuesta ``base``."""
    hist = historial_ficha(dataset)
    if hist:
        return {**hist[-1], "origen": "guardada"}
    if base is None:
        base = ficha_base({"dataset": dataset})
    return dict(base)


def _validar_ficha(f: dict) -> None:
    if f["criticidad"] not in CRITICIDADES:
        raise StewardError("criticidad", f"Criticidad inválida: {f['criticidad']}")
    horas = f["sla_frescura_h"]
    if not isinstance(horas, (int, float)) or horas < 0:
        raise StewardError("frescura", "El SLA de frescura son horas, un número >= 0.")
    sla = f["sla_calidad"]
    if not isinstance(sla, dict) or set(sla) - set(DIMENSIONES):
        raise StewardError("sla_calidad", f"SLA de calidad: dimensiones válidas {DIMENSIONES}")
    for dim, v in sla.items():
        if not isinstance(v, (int, float)) or not 0 <= v <= 100:
            raise StewardError("sla_calidad", f"SLA de calidad de {dim}: entre 0 y 100.")


def guardar_ficha(dataset: str, datos: dict, quien: str, motivo: str = "",
                  base: dict | None = None, ahora=None) -> dict:
    """Guarda una VERSIÓN nueva de la ficha (la anterior queda intacta).

    Cada campo que cambia deja su entrada en el registro de cambios; los
    umbrales de calidad cuentan como cambio de ``regla_calidad`` (son el
    criterio contra el que se abren incidentes).
    """
    quien = _quien(quien)
    extra = set(datos) - set(CAMPOS_FICHA)
    if extra:
        raise StewardError("no_editable", f"Campos no editables en la ficha: {sorted(extra)} "
                         "(la certificación va por cambiar_certificacion).")
    actual = ficha_vigente(dataset, base)
    nueva = {**actual, **datos}
    nueva["sla_calidad"] = {**actual.get("sla_calidad", {}),
                            **(datos.get("sla_calidad") or {})}
    nueva["sla_calidad"] = {k: float(v) for k, v in nueva["sla_calidad"].items()}
    _validar_ficha(nueva)
    for campo in CAMPOS_FICHA:
        if campo == "sla_calidad":
            for dim in DIMENSIONES:
                antes = actual.get("sla_calidad", {}).get(dim)
                despues = nueva["sla_calidad"].get(dim)
                if antes != despues:
                    registrar_cambio("regla_calidad", f"sla_calidad.{dim}", antes,
                                     despues, quien, motivo, dataset, ahora)
        elif actual.get(campo) != nueva.get(campo):
            registrar_cambio("ficha", campo, actual.get(campo), nueva.get(campo),
                             quien, motivo, dataset, ahora)
    return _apilar(dataset, nueva, quien, motivo, ahora)


def _apilar(dataset: str, ficha: dict, quien: str, motivo: str, ahora) -> dict:
    registro = {**ficha, "dataset": dataset,
                "version": len(historial_ficha(dataset)) + 1,
                "guardado_por": quien, "guardado_en": _iso(ahora),
                "motivo": (motivo or "").strip()}
    registro.pop("origen", None)
    return agregar_registro(_F_FICHAS, registro)


def cambiar_certificacion(dataset: str, nuevo: str, quien: str,
                          motivo: str = "", base: dict | None = None,
                          ahora=None) -> dict:
    """Mueve el dataset en el flujo de certificación.

    Certificar exige dueño de negocio y data steward asignados: un dataset
    "certificado" sin responsable es una contradicción que ningún auditor
    aceptaría.
    """
    quien = _quien(quien)
    if nuevo not in ESTADOS_CERT:
        raise StewardError("transicion", f"Estado de certificación inválido: {nuevo}")
    actual = ficha_vigente(dataset, base)
    previo = actual.get("estado_cert", "borrador")
    if nuevo not in TRANSICIONES_CERT[previo]:
        raise StewardError("transicion", f"No se puede pasar de «{previo}» a «{nuevo}». "
                         f"Permitidos: {TRANSICIONES_CERT[previo] or 'ninguno'}")
    if nuevo == "certificado" and not (actual.get("dueno_negocio", "").strip()
                                       and actual.get("data_steward", "").strip()):
        raise StewardError("cert_sin_dueno",
                           "Para certificar hacen falta dueño de negocio y data steward.")
    nueva = {**actual, "estado_cert": nuevo, "cert_por": quien, "cert_en": _iso(ahora)}
    registrar_cambio("certificacion", "estado_cert", previo, nuevo, quien, motivo,
                     dataset, ahora)
    return _apilar(dataset, nueva, quien, motivo, ahora)


def _asignaciones() -> dict:
    """Las asignaciones guardadas en Responsables (organigrama), por dataset."""
    from . import orgchart
    asg = orgchart.load_assignments()
    if asg is None or not len(asg) or "dataset" not in asg.columns:
        return {}
    return {str(r["dataset"]): r for r in asg.to_dict("records")}


def fichas(catalog: pd.DataFrame, results: pd.DataFrame | None = None,
           dictionary: pd.DataFrame | None = None) -> list[dict]:
    """La ficha vigente de cada dataset del catálogo que se pasa (y sólo de
    esos: con datos propios, sólo los propios)."""
    asg = _asignaciones()
    salida = []
    for fila in catalog.to_dict("records"):
        ds = str(fila["dataset"])
        base = ficha_base(fila, results, dictionary, asg.get(ds))
        f = ficha_vigente(ds, base)
        f["ultima_actualizacion"] = str(fila.get("last_updated", "") or "")
        salida.append(f)
    return salida


def fichas_df(lista: list[dict]) -> pd.DataFrame:
    """Las fichas aplanadas (una columna por umbral de dimensión)."""
    filas = []
    for f in lista:
        fila = {k: v for k, v in f.items() if k != "sla_calidad"}
        for dim in DIMENSIONES:
            fila[f"sla_{dim}"] = f.get("sla_calidad", {}).get(dim, SLA_CALIDAD_DEFAULT)
        filas.append(fila)
    columnas = ["dataset", "dominio", "dueno_negocio", "data_steward",
                "custodio_tecnico", "criticidad", "sla_frescura_h",
                *[f"sla_{d}" for d in DIMENSIONES], "pii", "confidencial",
                "estado_cert", "cert_por", "cert_en", "version", "guardado_por",
                "guardado_en", "origen", "ultima_actualizacion"]
    return pd.DataFrame(filas, columns=columnas)


# ---------------------------------------------------------------------------
# Cola de incidentes de calidad (event sourcing)
# ---------------------------------------------------------------------------

def _severidad(status: str, criticidad: str) -> str:
    if status == "fail":
        return "critica" if criticidad == "alta" else "alta"
    return "baja" if criticidad == "baja" else "media"


def hallazgos(results: pd.DataFrame, lista_fichas: list[dict]) -> list[dict]:
    """Lo que HOY merece incidente: reglas en warn/fail y dimensiones por
    debajo del SLA de calidad de la ficha. Clave estable: (dataset, regla)."""
    por_ds = {f["dataset"]: f for f in lista_fichas}
    salida = []
    if results is None or not len(results):
        return salida
    for r in results.to_dict("records"):
        ds = r["dataset"]
        if ds not in por_ds or r["status"] == "pass":
            continue
        salida.append({
            "dataset": ds, "rule_id": str(r["rule_id"]),
            "column": str(r.get("column", "")), "dimension": str(r["dimension"]),
            "detalle": f"{r.get('description', '')} · score {r['score']} "
                       f"< umbral {r['threshold']}",
            "severidad": _severidad(r["status"], por_ds[ds]["criticidad"]),
        })
    medias = results.groupby(["dataset", "dimension"])["score"].mean()
    for (ds, dim), score in medias.items():
        f = por_ds.get(ds)
        if f is None:
            continue
        sla = float(f.get("sla_calidad", {}).get(dim, SLA_CALIDAD_DEFAULT))
        if score < sla:
            salida.append({
                "dataset": ds, "rule_id": f"SLA-{dim}", "column": "",
                "dimension": dim,
                "detalle": f"SLA de calidad {dim}: {round(float(score), 2)} < {sla}",
                "severidad": "critica" if f["criticidad"] == "alta" else "alta",
            })
    return salida


def _estado_incidentes() -> dict[str, dict]:
    """Pliega los eventos en el estado vigente de cada incidente."""
    estado: dict[str, dict] = {}
    for ev in leer_registros(_F_INCIDENTES):
        iid = ev.get("id")
        if ev.get("evento") == "apertura":
            estado[iid] = {**{k: v for k, v in ev.items() if k != "evento"},
                           "estado": "abierto", "resuelto_en": "",
                           "resuelto_por": "", "ultima_nota": ""}
        elif iid in estado and ev.get("evento") == "estado":
            inc = estado[iid]
            inc["estado"] = ev["estado"]
            inc["ultima_nota"] = ev.get("nota", "")
            if ev["estado"] == "resuelto":
                inc["resuelto_en"], inc["resuelto_por"] = ev["fecha"], ev["quien"]
            else:
                inc["resuelto_en"], inc["resuelto_por"] = "", ""
    return estado


def _abiertos_por_clave(estado: dict) -> dict[tuple, dict]:
    return {(i["dataset"], i["rule_id"]): i for i in estado.values()
            if i["estado"] != "resuelto"}


def sincronizar_incidentes(results: pd.DataFrame, lista_fichas: list[dict],
                           ahora=None) -> dict:
    """Abre un incidente por cada hallazgo que no tenga uno abierto, y cierra
    solo los abiertos cuya regla volvió a pasar. Idempotente: correrlo dos
    veces seguidas no agrega nada. Sólo toca los datasets de ``lista_fichas``
    (con datos propios, los incidentes de la demo quedan como estaban)."""
    estado = _estado_incidentes()
    abiertos = _abiertos_por_clave(estado)
    por_ds = {f["dataset"]: f for f in lista_fichas}
    actuales = {(h["dataset"], h["rule_id"]): h
                for h in hallazgos(results, lista_fichas)}
    fecha = _dt(ahora)
    n_abiertos = n_cerrados = 0
    for clave, h in actuales.items():
        if clave in abiertos:
            continue
        f = por_ds[h["dataset"]]
        sla_h = SLA_RESOLUCION_H[h["severidad"]]
        agregar_registro(_F_INCIDENTES, {
            "evento": "apertura", "id": f"INC-{len(estado) + n_abiertos + 1:05d}",
            **h, "dominio": f.get("dominio", ""),
            "responsable": f.get("data_steward", "") or "",
            "fecha": fecha.isoformat(timespec="seconds"), "sla_h": sla_h,
            "vence": (fecha + timedelta(hours=sla_h)).isoformat(timespec="seconds"),
            "quien": SISTEMA,
        })
        n_abiertos += 1
    for clave, inc in abiertos.items():
        if clave[0] in por_ds and clave not in actuales:
            _evento_estado(inc["id"], "resuelto", SISTEMA,
                           "La regla volvió a cumplir su umbral.", ahora)
            n_cerrados += 1
    return {"abiertos": n_abiertos, "resueltos": n_cerrados}


def _evento_estado(iid: str, estado: str, quien: str, nota: str, ahora) -> dict:
    return agregar_registro(_F_INCIDENTES, {
        "evento": "estado", "id": iid, "estado": estado,
        "quien": quien, "nota": (nota or "").strip(), "fecha": _iso(ahora)})


def actualizar_incidente(iid: str, estado: str, quien: str, nota: str = "",
                         ahora=None) -> dict:
    """El steward mueve un incidente: abierto → en curso → resuelto (o lo
    reabre). Cada movimiento es un evento nuevo: el historial no se pisa."""
    quien = _quien(quien)
    inc = _estado_incidentes().get(iid)
    if inc is None:
        raise StewardError("incidente", f"No existe el incidente {iid}")
    if estado not in TRANSICIONES_INC[inc["estado"]]:
        raise StewardError("transicion",
                           f"No se puede pasar de «{inc['estado']}» a «{estado}».")
    return _evento_estado(iid, estado, quien, nota, ahora)


def historial_incidente(iid: str) -> list[dict]:
    return [e for e in leer_registros(_F_INCIDENTES) if e.get("id") == iid]


_COLS_INC = ["id", "dataset", "dominio", "rule_id", "column", "dimension",
             "severidad", "responsable", "estado", "fecha", "sla_h", "vence",
             "vencido", "resuelto_en", "resuelto_por", "detalle", "origen"]


def incidentes_df(results: pd.DataFrame | None, lista_fichas: list[dict],
                  ahora=None, incluir_detectados: bool = True) -> pd.DataFrame:
    """La cola: los incidentes guardados de estos datasets y, sin escribir
    nada en disco, los hallazgos de hoy que todavía no se abrieron
    (``origen = "detectado"``). Es la vista que usan la API y la exportación,
    que no deben tener efectos secundarios."""
    datasets = {f["dataset"] for f in lista_fichas}
    ref = _dt(ahora)
    estado = _estado_incidentes()
    filas = [dict(i, origen="registrado") for i in estado.values()
             if i["dataset"] in datasets]
    if incluir_detectados and results is not None:
        abiertos = _abiertos_por_clave(estado)
        por_ds = {f["dataset"]: f for f in lista_fichas}
        for h in hallazgos(results, lista_fichas):
            if (h["dataset"], h["rule_id"]) in abiertos:
                continue
            sla_h = SLA_RESOLUCION_H[h["severidad"]]
            filas.append({**h, "id": "", "dominio": por_ds[h["dataset"]]["dominio"],
                          "responsable": por_ds[h["dataset"]]["data_steward"],
                          "estado": "abierto", "fecha": ref.isoformat(timespec="seconds"),
                          "sla_h": sla_h,
                          "vence": (ref + timedelta(hours=sla_h)).isoformat(timespec="seconds"),
                          "resuelto_en": "", "resuelto_por": "", "origen": "detectado"})
    for f in filas:
        f["vencido"] = bool(f["estado"] != "resuelto" and _dt(f["vence"]) < ref)
    return pd.DataFrame(filas, columns=_COLS_INC)


# ---------------------------------------------------------------------------
# KPIs y tablero
# ---------------------------------------------------------------------------

def _con_dueno(f: dict) -> bool:
    return bool(str(f.get("dueno_negocio", "")).strip()
                and str(f.get("data_steward", "")).strip())


def kpis(lista_fichas: list[dict], incidentes: pd.DataFrame) -> dict:
    """Los números del steward. MTTR en horas, sobre incidentes resueltos."""
    n = len(lista_fichas)
    abiertos = incidentes[incidentes["estado"] != "resuelto"]
    resueltos = incidentes[(incidentes["estado"] == "resuelto")
                           & (incidentes["resuelto_en"].astype(str) != "")]
    horas = [(_dt(r["resuelto_en"]) - _dt(r["fecha"])).total_seconds() / 3600
             for r in resueltos.to_dict("records")]
    por_dominio = (abiertos.groupby("dominio").size().sort_values(ascending=False)
                   .to_dict() if len(abiertos) else {})
    return {
        "datasets": n,
        "pct_certificados": round(100.0 * sum(f.get("estado_cert") == "certificado"
                                              for f in lista_fichas) / n, 1) if n else 0.0,
        "pct_con_dueno": round(100.0 * sum(_con_dueno(f) for f in lista_fichas) / n,
                               1) if n else 0.0,
        "incidentes_abiertos": int(len(abiertos)),
        "incidentes_vencidos": int(abiertos["vencido"].sum()) if len(abiertos) else 0,
        "mttr_horas": round(sum(horas) / len(horas), 1) if horas else None,
        "abiertos_por_dominio": {str(k): int(v) for k, v in por_dominio.items()},
    }


def kpis_df(k: dict) -> pd.DataFrame:
    filas = [{"kpi": c, "value": k[c]} for c in
             ("datasets", "pct_certificados", "pct_con_dueno",
              "incidentes_abiertos", "incidentes_vencidos", "mttr_horas")]
    filas += [{"kpi": f"abiertos_dominio:{d}", "value": v}
              for d, v in k["abiertos_por_dominio"].items()]
    return pd.DataFrame(filas, columns=["kpi", "value"])


def vencimientos(lista_fichas: list[dict], incidentes: pd.DataFrame, ahora=None,
                 ultima_carga: dict | None = None) -> pd.DataFrame:
    """SLA vencidos: frescura (la última actualización es más vieja que el
    SLA) e incidentes abiertos pasados de su SLA de resolución.

    ``ultima_carga`` pisa la fecha del catálogo por dataset (p. ej. lo que el
    usuario cargó en esta sesión está fresco aunque el catálogo no lo sepa).
    """
    ref = _dt(ahora)
    ultima_carga = ultima_carga or {}
    filas = []
    for f in lista_fichas:
        horas = f.get("sla_frescura_h") or 0
        cuando = ultima_carga.get(f["dataset"]) or f.get("ultima_actualizacion")
        if not horas or not cuando:
            continue
        atraso = (ref - _dt(cuando)).total_seconds() / 3600 - horas
        if atraso > 0:
            filas.append({"tipo": "frescura", "dataset": f["dataset"], "id": "",
                          "responsable": f.get("data_steward", ""),
                          "limite": f"{horas} h", "atraso_h": round(atraso, 1)})
    if len(incidentes):
        for r in incidentes[incidentes["vencido"]].to_dict("records"):
            filas.append({"tipo": "incidente", "dataset": r["dataset"], "id": r["id"],
                          "responsable": r["responsable"], "limite": r["vence"],
                          "atraso_h": round((ref - _dt(r["vence"])).total_seconds()
                                            / 3600, 1)})
    return pd.DataFrame(filas, columns=["tipo", "dataset", "id", "responsable",
                                        "limite", "atraso_h"])


def tablero(lista_fichas: list[dict], incidentes: pd.DataFrame,
            steward: str | None = None, ahora=None,
            ultima_carga: dict | None = None) -> dict[str, pd.DataFrame]:
    """Lo que un steward mira al empezar el día. Con ``steward`` se acota a
    SUS datasets (y a los incidentes de los que es responsable)."""
    mias = [f for f in lista_fichas
            if not steward or f.get("data_steward", "") == steward]
    mios_ds = {f["dataset"] for f in mias}
    inc = incidentes[incidentes["dataset"].isin(mios_ds)] if steward else incidentes
    fdf = fichas_df(mias)
    return {
        "mis_datasets": fdf,
        "pendientes_certificacion": fdf[fdf["estado_cert"].isin(
            ["borrador", "en_revision"])].reset_index(drop=True),
        "incidentes_abiertos": inc[inc["estado"] != "resuelto"].reset_index(drop=True),
        "sin_dueno": fichas_df([f for f in lista_fichas if not _con_dueno(f)]),
        "vencimientos": vencimientos(mias, inc, ahora, ultima_carga),
    }


def stewards(lista_fichas: list[dict]) -> list[str]:
    return sorted({f["data_steward"] for f in lista_fichas
                   if str(f.get("data_steward", "")).strip()})


# ---------------------------------------------------------------------------
# Exportación (paquete BI)
# ---------------------------------------------------------------------------

def tablas_steward(catalog: pd.DataFrame, results: pd.DataFrame,
                   dictionary: pd.DataFrame | None, tables: dict,
                   incluir_generales: bool = True,
                   ahora=None) -> dict[str, pd.DataFrame]:
    """Las cuatro hojas del steward para el paquete BI, SOLO de los datasets
    del catálogo que se pasa. Sin efectos en disco: no abre incidentes."""
    from . import contrato_esquema
    lista = fichas(catalog, results, dictionary)
    datasets = [f["dataset"] for f in lista]
    return {
        "steward": fichas_df(lista),
        "contratos": contrato_esquema.contratos_df(
            {k: v for k, v in tables.items() if k in datasets}),
        "incidentes": incidentes_df(results, lista, ahora),
        "cambios_criterio": cambios_df(datasets, incluir_generales),
    }
