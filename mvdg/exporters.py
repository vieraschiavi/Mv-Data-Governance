# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Exportadores compatibles con cualquier BI.

Formatos: CSV, Excel (una tabla o paquete multi-hoja), JSON y Parquet
(si pyarrow está disponible). Los mismos DataFrames que sirve la API REST.
"""
from __future__ import annotations

import io
import json

import pandas as pd

from .catalog import catalog_df, dictionary_df
from .glossary import glossary_df
from .lineage import NODES as _LINEAGE_NODES
from .lineage import lineage_df
from .policies import policies_df
from .quality import (overall_index, quality_by_dataset,
                      quality_by_dimension, run_rules)


def scope_lineage_df(grafo) -> pd.DataFrame:
    """Aplana un grafo ``(nodos, aristas)`` a la tabla de linaje."""
    from . import scope
    return scope.lineage_to_df(*grafo)


def governance_tables(lang: str = "es",
                      include_samples: bool = False,
                      user_datasets: dict | None = None,
                      solo_usuario: bool = False) -> dict[str, pd.DataFrame]:
    """Todas las tablas de gobierno, listas para exportar o servir por API.

    Con ``include_samples=True`` el universo es el combinado demo + casos de
    ejemplo de Mis datos (ver ``mvdg.scope``) — mismo esquema de tablas,
    más filas. El default sigue siendo solo la demo (compatibilidad con la
    API y los tests existentes).

    ``user_datasets`` (``{nombre: DataFrame}``) suma lo que cargó el propio
    usuario. Es lo que hace que el Excel que subió termine en el bundle de
    Power BI y en la API, y no solo en la pestaña donde lo cargó — que era
    justamente el agujero: el cliente exportaba a BI y se llevaba la demo.

    ``solo_usuario=True`` cambia el universo entero: SOLO ``user_datasets``,
    cero filas de la demo. Existe para el gobierno que se deja corriendo
    dentro de la casa del cliente (p. ej. escrito de vuelta a un Lakehouse
    de Fabric, ver ``mvdg.fabric``). Ahí la demo no es una ayuda, es un
    error: nadie quiere ver "ventas_demo" al lado de sus tablas reales en
    un tablero de Power BI de producción, y un índice de calidad calculado
    sobre defectos sintéticos inyectados a propósito no es su índice de
    calidad. Mismo esquema de columnas en las 9 tablas — lo que cambia son
    las filas.

    El glosario queda VACÍO (con sus columnas) en ese modo: el glosario de
    la demo son términos inventados para mostrar el producto, y un glosario
    de negocio solo lo puede escribir la organización. Devolver el de la
    demo sería meterle definiciones falsas a un activo de gobierno.
    """
    # El grafo de linaje se lleva aparte del DataFrame porque sumarle los
    # datasets del usuario se hace sobre NODOS y ARISTAS, no sobre la tabla
    # ya aplanada. Aplanarlo antes de tiempo hacía que el linaje del usuario
    # reemplazara al de los casos de ejemplo en vez de sumarse.
    grafo = None
    if solo_usuario:
        from . import scope
        if not scope._items(user_datasets):
            raise ValueError(
                "solo_usuario=True necesita al menos un dataset con filas en "
                "user_datasets: sin datos del cliente no hay nada que gobernar "
                "y devolver la demo sería justamente lo que este modo evita.")
        results = scope.user_results(user_datasets, lang)
        catalog = scope.user_catalog(user_datasets, lang)
        dictionary = scope.user_dictionary(user_datasets, lang)
        # El grafo arranca sin los nodos de la demo, con UNA excepción: el
        # nodo de BI, al que todo dataset del usuario apunta. No es de la
        # demo (es genérico: "Dashboard BI (Power BI / Tableau / Looker…)")
        # y sin él el linaje del cliente queda con aristas que apuntan a un
        # nodo inexistente.
        lineage = scope.lineage_to_df(
            *scope.user_lineage(user_datasets, lang,
                                nodes=[n for n in _LINEAGE_NODES
                                       if n["id"] == "bi_dashboard"],
                                edges=[]))
        glossary = glossary_df(lang).iloc[0:0]
        policies = policies_df(lang, results, catalog=catalog, dictionary=dictionary)
        return _con_kpis(catalog, dictionary, results, lineage, glossary, policies)

    if include_samples:
        from . import scope
        results = scope.combined_results(lang)
        catalog = scope.combined_catalog(lang)
        dictionary = scope.combined_dictionary(lang)
        grafo = scope.combined_lineage(lang)
        glossary = scope.combined_glossary(lang)
    else:
        results = run_rules(lang=lang)
        catalog = catalog_df(lang)
        dictionary = dictionary_df(lang)
        glossary = glossary_df(lang)
    lineage = scope_lineage_df(grafo) if grafo else lineage_df()

    if user_datasets:
        from . import scope
        nodos, aristas = scope.user_lineage(
            user_datasets, lang,
            nodes=grafo[0] if grafo else None, edges=grafo[1] if grafo else None)
        results = pd.concat([results, scope.user_results(user_datasets, lang)],
                            ignore_index=True)
        catalog = pd.concat(
            [catalog, scope.user_catalog(user_datasets, lang, columnas=catalog.columns)],
            ignore_index=True)
        dictionary = pd.concat([dictionary, scope.user_dictionary(user_datasets, lang)],
                               ignore_index=True)
        lineage = scope.lineage_to_df(nodos, aristas)

    # Las políticas se derivan del catálogo y del diccionario finales: si se
    # calcularan antes de sumar lo del usuario, sus columnas con PII no
    # dispararían ninguna política.
    policies = (policies_df(lang, results, catalog=catalog, dictionary=dictionary)
                if (include_samples or user_datasets) else policies_df(lang, results))
    return _con_kpis(catalog, dictionary, results, lineage, glossary, policies)


def _con_kpis(catalog, dictionary, results, lineage, glossary, policies) -> dict:
    """Las 9 tablas con los KPIs derivados. En una sola función para que los
    dos universos (demo/combinado y solo-cliente) no puedan divergir en el
    esquema: lo que cambia entre modos son las FILAS, nunca las columnas."""
    kpis = pd.DataFrame([{
        "kpi": "quality_index", "value": overall_index(results)},
        {"kpi": "rules_total", "value": len(results)},
        {"kpi": "rules_pass", "value": int((results["status"] == "pass").sum())},
        {"kpi": "rules_warn", "value": int((results["status"] == "warn").sum())},
        {"kpi": "rules_fail", "value": int((results["status"] == "fail").sum())},
    ])
    return {
        "catalog": catalog,
        "dictionary": dictionary,
        "quality_results": results,
        "quality_by_dataset": quality_by_dataset(results),
        "quality_by_dimension": quality_by_dimension(results),
        "lineage": lineage,
        "glossary": glossary,
        "policies": policies,
        "kpis": kpis,
    }


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def to_json_bytes(df: pd.DataFrame) -> bytes:
    return json.dumps(df.to_dict(orient="records"),
                      ensure_ascii=False, indent=2, default=str).encode("utf-8")


def to_excel_bytes(df: pd.DataFrame, sheet: str = "data") -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter",
                       engine_kwargs={"options": {"in_memory": True}}) as xw:
        df.to_excel(xw, sheet_name=sheet[:31], index=False)
    return buf.getvalue()


def to_parquet_bytes(df: pd.DataFrame) -> bytes | None:
    """Parquet si hay motor disponible; ``None`` si no lo hay."""
    try:
        buf = io.BytesIO()
        df.to_parquet(buf, index=False)
        return buf.getvalue()
    except ImportError:
        return None


def bi_bundle_xlsx(lang: str = "es", user_datasets: dict | None = None,
                   solo_usuario: bool = False) -> bytes:
    """Excel multi-hoja con todo el paquete de gobierno (para cualquier BI).

    Con ``solo_usuario=True`` y datasets cargados, el paquete es SÓLO de
    esos datasets. Sin esto, quien exportaba con sus datos a la vista se
    llevaba el paquete de la demo: el mismo botón, otra información.
    """
    buf = io.BytesIO()
    tablas = governance_tables(lang, user_datasets=user_datasets,
                               solo_usuario=solo_usuario)
    tablas = {**tablas, **steward_sheets(tablas, user_datasets, solo_usuario)}
    with pd.ExcelWriter(buf, engine="xlsxwriter",
                       engine_kwargs={"options": {"in_memory": True}}) as xw:
        for name, df in tablas.items():
            df.to_excel(xw, sheet_name=name[:31], index=False)
    return buf.getvalue()


def steward_sheets(tablas: dict, user_datasets: dict | None = None,
                   solo_usuario: bool = False) -> dict[str, pd.DataFrame]:
    """Las hojas del Data Steward (ficha, contratos de esquema, incidentes y
    cambios de criterio) del MISMO universo que ``tablas``.

    Se acotan al catálogo de ``tablas``: con ``solo_usuario`` son sólo los
    datasets del cliente, y un cambio general (un término del glosario de la
    demo) tampoco entra. Sin efectos en disco: exportar no abre incidentes.
    """
    from . import scope, steward
    from .demo_data import load_demo_tables
    propias = dict(scope._items(user_datasets))
    fuentes = propias if solo_usuario else {**load_demo_tables(), **propias}
    return steward.tablas_steward(tablas["catalog"], tablas["quality_results"],
                                  tablas["dictionary"], fuentes,
                                  incluir_generales=not solo_usuario)
