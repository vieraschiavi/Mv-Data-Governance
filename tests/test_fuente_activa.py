"""La fuente activa: con datos propios cargados, la demo desaparece de TODO
el programa; sin ellos, vuelve.

Pedido textual: «al elegir dataset por archivo o sql debería aplicarse a
todas las pestañas y desaparezca los datos demos».
"""
from __future__ import annotations

import os
import sys

import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from mvdg import contracts, fuente, insights, samples  # noqa: E402
from mvdg.catalog import dataset_names  # noqa: E402

#: Todo lo que la demo y los casos de ejemplo traen. Ninguno de estos
#: nombres puede aparecer con datos propios cargados.
AJENOS = set(dataset_names()) | set(samples.sample_keys())


def _mis_datos() -> dict:
    return {"mis_ventas": pd.DataFrame({
        "cliente_id": [1, 2, 3, 3, None],
        "email": ["a@x.com", "b@x.com", "c@x.com", "c@x.com", None],
        "monto": [100.0, 250.5, -3.0, 80.0, 40.0],
        "fecha": pd.to_datetime(["2026-01-01", "2026-02-01", "2026-03-01",
                                 "2026-03-01", "2026-04-01"]),
    })}


# ------------------------------------------------------------------ motor
def test_sin_datos_propios_la_fuente_es_la_demo():
    assert not fuente.solo_propios({})
    assert not fuente.solo_propios(None)
    # Un archivo vacío no apaga la demo: dejaría las pestañas en blanco.
    assert not fuente.solo_propios({"vacio": pd.DataFrame()})
    with pytest.raises(ValueError):
        fuente.universo("es", {})


def test_con_datos_propios_ninguna_tabla_trae_la_demo():
    uni = fuente.universo("es", _mis_datos())
    for clave in ("catalog", "dictionary", "quality_results",
                  "quality_by_dataset", "policies"):
        df = uni[clave]
        if "dataset" in df.columns and len(df):
            assert set(df["dataset"]) <= {"mis_ventas"}, clave
    assert set(uni["tables"]) == {"mis_ventas"}
    nodos, aristas = uni["lineage_graph"]
    assert not {n["id"] for n in nodos} & AJENOS
    assert ("mis_ventas", "bi_dashboard") in aristas
    # Lo que la demo trae y el cliente no, no se inventa.
    assert uni["glossary"].empty and list(uni["glossary"].columns)
    assert len(uni["quality_results"]) > 0


def test_la_pii_y_la_cobertura_son_de_tus_datos():
    uni = fuente.universo("es", _mis_datos())
    assert ("mis_ventas", "email") in uni["pii"]
    assert list(uni["coverage"]["dataset"]) == ["mis_ventas"]
    assert uni["summary"]["datasets"] == 1
    # Sin dueño asignado todavía: 0 %, no el 50 % de la demo.
    assert uni["summary"]["owner_pct"] == 0.0


def test_el_resumen_de_una_cobertura_vacia_no_divide_por_cero():
    vacia = insights.coverage_for(pd.DataFrame(columns=["dataset"]),
                                  pd.DataFrame(columns=["dataset"]))
    assert insights.summary_of(vacia)["governance_index"] == 0.0


def test_el_resumen_de_la_demo_no_cambio():
    """`governance_summary` pasó a usar `summary_of`: los números de la
    demo tienen que ser los mismos que antes."""
    r = insights.governance_summary("es")
    assert r == insights.summary_of(insights.governance_coverage("es"))
    assert r["datasets"] == len(dataset_names()) + len(samples.sample_keys())


def test_los_contratos_con_tus_datos_son_de_tus_productos():
    uni = fuente.universo("es", _mis_datos())
    con = contracts.contracts_df("es", uni["quality_results"], uni["catalog"],
                                 uni["lineage_graph"])
    assert list(con["dataset"]) == ["mis_ventas"]
    ale = contracts.alerts_df("es", uni["quality_results"], uni["catalog"],
                              uni["lineage_graph"])
    assert set(ale["dataset"]) <= {"mis_ventas"}
    assert contracts.kpis("es", uni["quality_results"], uni["catalog"],
                          uni["lineage_graph"])["products"] == 1


def test_los_contratos_sin_catalogo_siguen_siendo_los_de_la_demo():
    con = contracts.contracts_df("es")
    assert set(dataset_names()) <= set(con["dataset"])


# ------------------------------------------------------------- la app entera
def _correr(monkeypatch, tmp_path, datos: dict | None):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    for v in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY",
              "XAI_API_KEY", "MVDG_AI_API_KEY", "MVDG_AI_PROVIDER"):
        monkeypatch.delenv(v, raising=False)
    at = AppTest.from_file(os.path.join(RAIZ, "app", "app.py"),
                           default_timeout=300)
    if datos:
        at.session_state["mvdg_user_datasets"] = datos
    at.run()
    return at


def _nombres_en_tablas(at) -> set[str]:
    """Todos los textos de todas las tablas que dibujó la app."""
    vistos: set[str] = set()
    for df in at.dataframe:
        valor = df.value
        if isinstance(valor, pd.DataFrame):
            for col in valor.columns:
                # Texto puede venir como `object` o como `string` según la
                # versión de pandas: los números no nombran datasets.
                if not pd.api.types.is_numeric_dtype(valor[col]):
                    vistos |= {str(x) for x in valor[col].dropna().unique()}
    return vistos


def test_la_app_con_tus_datos_no_muestra_la_demo_en_ninguna_pestana(
        tmp_path, monkeypatch):
    at = _correr(monkeypatch, tmp_path, _mis_datos())
    assert not at.exception, [str(e.value)[:300] for e in at.exception]
    textos = _nombres_en_tablas(at)
    assert "mis_ventas" in textos
    fugas = textos & AJENOS
    assert not fugas, f"la demo se filtró en: {sorted(fugas)}"
    # Tampoco en las listas para elegir: ningún selector ofrece un dataset
    # de la demo o de los casos.
    for w in list(at.selectbox) + list(at.multiselect) + list(at.radio):
        ofrece = {str(x) for x in (w.options or [])} & AJENOS
        assert not ofrece, (w.key, sorted(ofrece))
    # El interruptor de los casos de ejemplo no tiene nada que decidir.
    toggle = next(t for t in at.toggle if t.key == "scope_samples")
    assert toggle.disabled


def test_la_app_sin_datos_propios_muestra_la_demo(tmp_path, monkeypatch):
    at = _correr(monkeypatch, tmp_path, None)
    assert not at.exception, [str(e.value)[:300] for e in at.exception]
    assert set(dataset_names()) & _nombres_en_tablas(at)
