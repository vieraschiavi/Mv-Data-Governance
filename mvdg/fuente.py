# © 2026 Martín Viera. Todos los derechos reservados.
"""MV Data Governance · La fuente activa: la demo, o SOLO los datos del usuario.

El pedido, textual: «al elegir dataset por archivo o sql debería aplicarse a
todas las pestañas y desaparezca los datos demos».

Antes lo que el usuario cargaba se SUMABA a la demo: el catálogo mostraba
sus tablas al lado de ``ventas_demo``, el índice de calidad promediaba sus
reglas con los defectos sintéticos inyectados a propósito, y varias pestañas
(Calidad, Linaje, Glosario, MDM, Contratos, el resumen de Panorama) seguían
leyendo la demo directo, como si el archivo no existiera. Quien probaba el
producto con su propio Excel veía un tablero que mezclaba sus datos con datos
inventados — y un número de calidad que no era el suyo.

Ahora hay dos universos y ninguno se mezcla con el otro:

* **Sin datos propios** → la demo, como siempre (con o sin los casos de
  ejemplo, según el interruptor de la barra lateral).
* **Con al menos un dataset cargado** (archivo, SQLite o conexión SQL) →
  SOLO lo cargado, en TODAS las pestañas. Es el mismo universo que
  ``governance_tables(..., solo_usuario=True)`` ya armaba para el gobierno
  que se deja corriendo en la casa del cliente; acá lo usa la pantalla.

Lo que la demo trae y el cliente todavía no tiene NO se inventa: el glosario
queda vacío (un glosario de negocio sólo lo escribe la organización), la
serie de evolución de calidad no se dibuja (es sintética: con datos reales
se construye corrida a corrida) y los dueños quedan sin asignar hasta que
Curaduría o el organigrama los completen.

Este módulo no importa Streamlit: la app lo consume, y se prueba solo.
"""
from __future__ import annotations

import pandas as pd

from . import scope
from .exporters import _LINEAGE_NODES, governance_tables


def solo_propios(user_datasets) -> bool:
    """True si hay al menos un dataset del usuario CON filas.

    Un archivo vacío o una consulta que no devolvió nada no apagan la demo:
    dejarían al usuario mirando pestañas en blanco sin saber por qué.
    """
    return bool(scope._items(user_datasets))


def universo(lang: str, user_datasets) -> dict:
    """Todo lo que las pestañas necesitan, calculado SOLO sobre lo cargado.

    Devuelve las nueve tablas de ``governance_tables`` más:

    * ``tables`` — los DataFrames del usuario (lo que MDM, el perfilador y
      las exportaciones recorren), sin ninguna tabla de la demo;
    * ``lineage_graph`` — nodos y aristas (origen → dataset → BI) para
      dibujar el grafo, el mismo que aplana la tabla ``lineage``;
    * ``pii`` — pares (dataset, columna) detectados como personales;
    * ``coverage`` / ``summary`` — la cobertura de gobierno por dataset y su
      resumen, sobre los datasets del usuario y no sobre los de la demo.
    """
    if not solo_propios(user_datasets):
        raise ValueError("universo() necesita al menos un dataset con filas: "
                         "sin datos propios, la fuente activa es la demo.")
    from . import insights

    gov = governance_tables(lang, user_datasets=user_datasets, solo_usuario=True)
    nodos, aristas = scope.user_lineage(
        user_datasets, lang,
        nodes=[n for n in _LINEAGE_NODES if n["id"] == "bi_dashboard"],
        edges=[])
    dic = gov["dictionary"]
    pii = [(str(r.dataset), str(r.column)) for r in dic.itertuples()
           if bool(r.pii)]
    cobertura = insights.coverage_for(gov["catalog"], gov["quality_results"], lang)
    return {
        **gov,
        "tables": dict(scope._items(user_datasets)),
        "lineage_graph": (nodos, aristas),
        "pii": pii,
        "coverage": cobertura,
        "summary": insights.summary_of(cobertura),
    }


def nombres(user_datasets) -> list[str]:
    """Los nombres de lo cargado, en el orden en que se cargó."""
    return [n for n, _df in scope._items(user_datasets)]


def vacio_como(df: pd.DataFrame) -> pd.DataFrame:
    """Un DataFrame sin filas con las mismas columnas: lo que muestra una
    pestaña cuando el universo del usuario todavía no tiene eso (glosario)."""
    return df.iloc[0:0]
