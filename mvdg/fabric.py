# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Microsoft Fabric (notebook + Lakehouse).

El puente para la empresa que tiene sus datos EN Fabric y quiere el gobierno
adentro de Fabric, no al lado.

────────────────────────────────────────────────────────────────────────────
Por qué hace falta un módulo y no alcanza con el conector
────────────────────────────────────────────────────────────────────────────
``mvdg.connectors`` (motor ``fabric``) resuelve la mitad: traer las tablas
desde afuera, por el SQL analytics endpoint, a la app de escritorio o al
servidor. Sirve para el consultor que analiza desde su PC.

Lo que NO resuelve es el caso de la empresa que ya vive adentro de Fabric:
ahí el dato no debería salir del tenant, y el resultado del gobierno tiene
que quedar donde el resto de la organización ya mira — o sea, como tablas
del Lakehouse, que Power BI lee nativo (DirectLake) sin exportar nada.

Este módulo corre DENTRO de un notebook de Fabric:

    from mvdg import fabric
    r = fabric.gobernar_lakehouse()          # lee, gobierna y escribe
    r["escritas"]                            # las tablas que quedaron

y deja las 9 tablas de gobierno (catálogo, diccionario, calidad por regla /
dataset / dimensión, linaje, glosario, políticas y KPIs) como tablas del
Lakehouse, con prefijo, listas para un tablero.

────────────────────────────────────────────────────────────────────────────
Tres decisiones que valen la pena explicar
────────────────────────────────────────────────────────────────────────────
1. NADA DE LA DEMO. Se gobierna con ``solo_usuario=True``: las tablas que
   se escriben en el Lakehouse del cliente contienen SUS datasets y nada
   más. Mezclar los datasets sintéticos de la demo en un tablero de
   producción no es una molestia estética — un índice de calidad calculado
   sobre defectos inyectados a propósito es un número falso.

2. SPARK SE INYECTA, NO SE IMPORTA. Ninguna función importa ``pyspark``:
   la sesión llega por parámetro o se toma del notebook. Así el motor
   sigue cumpliendo la regla de la casa (``mvdg/`` se importa y se testea
   sin levantar nada), este módulo se puede probar con una sesión falsa, y
   el programa no se cae al importarlo en una PC donde Spark no existe.

3. SI SE MUESTREA, SE DICE. Traer una tabla de Fabric entera a pandas
   puede no entrar en memoria, así que hay un tope de filas. Pero el
   resultado informa qué tablas se muestrearon y con cuántas filas: un
   perfil sobre una parte presentado como el total es un dato equivocado
   con cara de dato bueno.

Verificado contra Microsoft Learn el 2026-09-15. El camino principal de
escritura usa ``saveAsTable`` —la API documentada que no depende de ninguna
ruta de montaje— así que no hay rutas adivinadas en el medio. NO se probó
en vivo contra un tenant real de Fabric (no hay uno en este entorno): el
mismo criterio de honestidad que el resto de los conectores del programa.
"""
from __future__ import annotations

import os

import pandas as pd

# Tope por defecto al traer una tabla del Lakehouse a pandas: 0 = SIN TOPE,
# cada tabla entera. Mismo criterio que ``connectors.MAX_ROWS`` (antes era
# 100.000). Se puede pedir un tope con ``muestra=N``; si recorta, el
# resultado lo dice en ``muestreadas`` y da el total real en
# ``filas_totales`` — nunca un recorte mudo.
MAX_FILAS = 0

# Prefijo de las tablas que se escriben. Con prefijo, el gobierno queda
# junto y ordenado en la lista del Lakehouse, y se distingue de un vistazo
# de las tablas de negocio del cliente.
PREFIJO = "gobierno_"

# Señales de que el proceso corre dentro de un notebook de Fabric/Synapse.
# Ninguna decisión de corrección depende de acertar esto: solo cambia
# mensajes y valores por defecto (ver ``en_fabric``).
_RUTA_LAKEHOUSE = "/lakehouse/default"
_ENV_ARCADIA = "Microsoft.ProjectArcadia"


def en_fabric() -> bool:
    """¿Esto corre dentro de un notebook de Fabric?

    Es una PISTA, no un permiso: el módulo funciona igual si esto devuelve
    False (por ejemplo con una sesión de Spark inyectada a mano desde
    otro lado). Se usa para los mensajes y para saber si tiene sentido
    ofrecer el camino de archivos del Lakehouse montado.
    """
    if os.environ.get("AZURE_SERVICE") == _ENV_ARCADIA:
        return True
    return os.path.isdir(_RUTA_LAKEHOUSE)


def sesion_spark(spark=None):
    """La sesión de Spark a usar: la inyectada, o la del notebook.

    En un notebook de Fabric, ``spark`` ya existe como variable global del
    intérprete. Se la busca ahí en vez de crear una nueva: crear una sesión
    propia en un notebook que ya tiene la suya es la forma más rápida de
    quedarse sin ejecutores.

    Devuelve None si no hay ninguna — no es un error: hay un camino sin
    Spark (ver ``escribir_tablas``).
    """
    if spark is not None:
        return spark
    try:                                    # la global del notebook
        import builtins
        candidata = getattr(builtins, "spark", None)
        if candidata is not None:
            return candidata
    except Exception:                       # pragma: no cover - defensivo
        pass
    try:
        from pyspark.sql import SparkSession
    except ImportError:
        return None
    # getActiveSession: la que ya está andando. NUNCA .getOrCreate() acá,
    # que levantaría una sesión nueva sin que nadie la pidiera.
    try:
        return SparkSession.getActiveSession()
    except Exception:                       # pragma: no cover - defensivo
        return None


def _exigir_spark(spark=None):
    ses = sesion_spark(spark)
    if ses is None:
        raise RuntimeError(
            "No hay una sesión de Spark. Esto se corre dentro de un notebook "
            "de Fabric (donde `spark` ya existe), o se le pasa la sesión: "
            "fabric.gobernar_lakehouse(spark=spark).")
    return ses


def listar_tablas(spark=None) -> list[str]:
    """Los nombres de las tablas del Lakehouse por defecto del notebook."""
    ses = _exigir_spark(spark)
    return [t.name for t in ses.catalog.listTables()]


def leer_tablas(nombres=None, spark=None,
                muestra: int | None = MAX_FILAS) -> tuple[dict, dict]:
    """Trae tablas del Lakehouse a pandas.

    ``nombres=None`` trae todas las del Lakehouse por defecto. Por defecto
    (``muestra`` 0 o ``None``) trae cada tabla entera.

    Devuelve ``(tablas, muestreadas)``: el segundo dict dice qué tablas se
    cortaron y en cuántas filas, para que el resultado nunca presente un
    perfil parcial como si fuera el total.
    """
    ses = _exigir_spark(spark)
    if nombres is None:
        nombres = listar_tablas(ses)
    muestra = max(0, int(muestra or 0))

    tablas: dict[str, pd.DataFrame] = {}
    muestreadas: dict[str, int] = {}
    for nombre in nombres:
        sdf = ses.read.table(nombre)
        if muestra:
            # Se pide una fila MÁS que el tope: si vuelve, la tabla tenía
            # más y hay que avisar. Contar con .count() sería una pasada
            # completa sobre el dato para saber algo que el propio corte
            # ya responde.
            pdf = sdf.limit(muestra + 1).toPandas()
            if len(pdf) > muestra:
                pdf = pdf.head(muestra)
                muestreadas[nombre] = muestra
        else:
            pdf = sdf.toPandas()
        tablas[nombre] = pdf
    return tablas, muestreadas


def gobernar(tablas: dict, lang: str = "es") -> dict:
    """Las 9 tablas de gobierno sobre las tablas del cliente, sin la demo.

    Es una línea sola a propósito: el motor de gobierno es el mismo que usa
    el dashboard y la API. Si esto tuviera lógica propia, el gobierno que
    ve el cliente en Fabric podría diferir del que ve en el programa.
    """
    from .exporters import governance_tables
    return governance_tables(lang, user_datasets=tablas, solo_usuario=True)


def _a_spark(df: pd.DataFrame, ses):
    """pandas -> Spark, esquivando el caso que rompe la inferencia.

    Una columna de objetos enteramente nula (p. ej. ``owner`` cuando
    todavía nadie asignó dueños) no le da a Spark ningún valor del cual
    inferir el tipo, y la creación falla con un error que no menciona la
    columna. Se convierten a texto: son campos de texto vacíos, que es lo
    que representan.
    """
    limpio = df.copy()
    for col in limpio.columns:
        if limpio[col].dtype == object and limpio[col].isna().all():
            limpio[col] = limpio[col].astype(str).where(limpio[col].notna(), None)
    limpio.columns = [str(c) for c in limpio.columns]
    return ses.createDataFrame(limpio)


def escribir_tablas(gobierno: dict, spark=None, prefijo: str = PREFIJO,
                    modo: str = "overwrite", ruta: str | None = None) -> dict:
    """Deja las tablas de gobierno en el Lakehouse.

    Con Spark (el caso normal en un notebook) las escribe como TABLAS del
    Lakehouse vía ``saveAsTable`` — o sea Delta, que es lo que hace que
    Power BI las lea nativo sin exportar nada y sin ninguna ruta de por
    medio.

    Sin Spark (notebook de Python puro) las escribe como Parquet en
    ``ruta``. El default apunta al Lakehouse montado, pero la ruta es un
    parámetro: si no existe, se dice cuál se intentó en vez de fallar con
    un error de sistema de archivos.

    Devuelve ``{"escritas": [...], "formato": "delta"|"parquet", "destino": ...}``.
    """
    ses = sesion_spark(spark)
    if ses is not None:
        escritas = []
        for nombre, df in gobierno.items():
            destino = f"{prefijo}{nombre}"
            _a_spark(df, ses).write.mode(modo).saveAsTable(destino)
            escritas.append(destino)
        return {"escritas": escritas, "formato": "delta", "destino": "Tables/"}

    destino = ruta or f"{_RUTA_LAKEHOUSE}/Files/{prefijo.rstrip('_')}"
    if not os.path.isdir(os.path.dirname(destino.rstrip("/")) or "/"):
        raise RuntimeError(
            f"Sin Spark y sin poder escribir en {destino!r}: ese Lakehouse no "
            "está montado en este proceso. Corré esto dentro de un notebook "
            "de Fabric con un Lakehouse por defecto, o pasá una ruta que "
            "exista: fabric.escribir_tablas(g, ruta='/ruta/que/existe').")
    os.makedirs(destino, exist_ok=True)
    escritas = []
    for nombre, df in gobierno.items():
        archivo = os.path.join(destino, f"{prefijo}{nombre}.parquet")
        df.to_parquet(archivo, index=False)
        escritas.append(archivo)
    return {"escritas": escritas, "formato": "parquet", "destino": destino}


def _contar_recortadas(ses, muestreadas: dict) -> dict:
    """Total real de filas de cada tabla que el tope recortó. Si el conteo
    falla, queda ``None``: el recorte se sigue avisando en ``muestreadas``."""
    totales: dict[str, int | None] = {}
    for nombre in muestreadas:
        try:
            totales[nombre] = int(ses.read.table(nombre).count())
        except Exception:  # noqa: BLE001 - el aviso de recorte no depende del conteo
            totales[nombre] = None
    return totales


def gobernar_lakehouse(nombres=None, lang: str = "es", spark=None,
                       prefijo: str = PREFIJO, muestra: int | None = MAX_FILAS,
                       escribir: bool = True, modo: str = "overwrite",
                       ruta: str | None = None) -> dict:
    """Lee el Lakehouse, lo gobierna y escribe el resultado. Una celda.

    Con ``escribir=False`` devuelve las tablas sin tocar el Lakehouse —
    para mirar el resultado antes de dejarlo publicado.

    El diccionario que devuelve incluye ``muestreadas``: si está vacío, el
    gobierno se calculó sobre las tablas COMPLETAS. Si no, ``filas_totales``
    dice cuántas filas tenía de verdad cada tabla recortada (un ``count()``
    de Spark, que se paga SOLO cuando hubo recorte).
    """
    ses = _exigir_spark(spark)
    tablas, muestreadas = leer_tablas(nombres, ses, muestra=muestra)
    if not any(len(df) for df in tablas.values()):
        raise RuntimeError(
            "No se leyó ninguna fila del Lakehouse: no hay tablas, están "
            "vacías, o el notebook no tiene un Lakehouse por defecto "
            "asignado (el panel de la izquierda, con el ícono de pin).")
    gobierno = gobernar(tablas, lang)
    salida = {
        "tablas_leidas": {n: len(df) for n, df in tablas.items()},
        "muestreadas": muestreadas,
        "filas_totales": _contar_recortadas(ses, muestreadas),
        "gobierno": gobierno,
        "escritas": [],
    }
    if escribir:
        salida.update(escribir_tablas(gobierno, ses, prefijo=prefijo,
                                      modo=modo, ruta=ruta))
    return salida
