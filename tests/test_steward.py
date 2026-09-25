# © 2026 Martín Viera. Todos los derechos reservados.
"""El espacio del Data Steward: ficha, certificación, incidentes, contrato de
esquema, auditoría de cambios de criterio y exportación sin fuga de la demo.
"""
from __future__ import annotations

import io
import os
import sys
from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from mvdg import catalog, contrato_esquema, fuente, samples, steward  # noqa: E402
from mvdg.demo_data import load_demo_tables  # noqa: E402
from mvdg.quality import run_rules  # noqa: E402

AJENOS = set(catalog.dataset_names()) | set(samples.sample_keys())
T0 = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def _carpeta_aislada(tmp_path, monkeypatch):
    """Todo lo persistente va a una carpeta temporal: los tests no tocan la
    carpeta de datos real de quien los corre."""
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    return tmp_path


def _demo():
    res = run_rules()
    return res, steward.fichas(catalog.catalog_df(), res, catalog.dictionary_df())


def _mis_datos() -> dict:
    return {"mis_ventas": pd.DataFrame({
        "venta_id": [1, 2, 3, 4, 5],
        "cliente_id": [1, 2, 3, 3, None],
        "email": ["a@x.com", "b@x.com", "c@x.com", "c@x.com", None],
        "canal": ["web", "web", "tienda", "tienda", "web"],
        "monto": [100.0, 250.5, -3.0, 80.0, 40.0],
    })}


# --------------------------------------------------------------- la ficha
def test_la_ficha_propuesta_sale_del_catalogo_real():
    res, fichas = _demo()
    f = next(x for x in fichas if x["dataset"] == "dim_customers")
    assert f["dueno_negocio"] == "Gerencia Comercial"
    assert f["data_steward"] == "M. Viera"
    assert f["custodio_tecnico"] == ""            # no se inventa
    assert f["criticidad"] == "alta" and f["pii"] and f["confidencial"]
    assert f["sla_frescura_h"] == 24               # refresh "daily"
    assert set(f["sla_calidad"]) == set(steward.DIMENSIONES)
    # Hereda el umbral real de la regla (CUS-02 completeness = 98.0).
    assert f["sla_calidad"]["completeness"] == 98.0
    assert f["estado_cert"] == "borrador" and f["origen"] == "propuesta"


def test_guardar_ficha_es_append_only_y_audita_cada_campo():
    _, fichas = _demo()
    base = next(x for x in fichas if x["dataset"] == "fct_sales")
    steward.guardar_ficha("fct_sales", {"custodio_tecnico": "Equipo DBA",
                                        "sla_calidad": {"accuracy": 99.0}},
                          "Ana Steward", "alta del custodio", base=base, ahora=T0)
    steward.guardar_ficha("fct_sales", {"criticidad": "media"}, "Ana Steward",
                          "revisión trimestral", base=base, ahora=T0)
    hist = steward.historial_ficha("fct_sales")
    assert [h["version"] for h in hist] == [1, 2]
    assert hist[0]["criticidad"] == "alta"            # la v1 no se pisó
    vig = steward.ficha_vigente("fct_sales")
    assert vig["criticidad"] == "media" and vig["custodio_tecnico"] == "Equipo DBA"
    assert vig["sla_calidad"]["accuracy"] == 99.0
    cambios = steward.cambios_df(["fct_sales"])
    tipos = set(cambios["tipo"])
    assert {"regla_calidad", "ficha"} <= tipos
    fila = cambios[cambios["objeto"] == "sla_calidad.accuracy"].iloc[0]
    assert (fila["antes"], fila["despues"], fila["quien"]) == ("98.0", "99.0", "Ana Steward")
    assert fila["motivo"] == "alta del custodio"


@pytest.mark.parametrize("datos, quien", [
    ({"criticidad": "urgentísima"}, "Ana"),
    ({"sla_calidad": {"validity": 120}}, "Ana"),
    ({"sla_calidad": {"belleza": 90}}, "Ana"),
    ({"sla_frescura_h": -1}, "Ana"),
    ({"estado_cert": "certificado"}, "Ana"),       # la certificación va aparte
    ({"criticidad": "baja"}, "   "),                 # sin responsable
])
def test_guardar_ficha_rechaza_datos_invalidos(datos, quien):
    with pytest.raises(ValueError):
        steward.guardar_ficha("fct_sales", datos, quien)
    assert steward.historial_ficha("fct_sales") == []


# --------------------------------------------------------- certificación
def test_flujo_de_certificacion_con_quien_y_cuando():
    _, fichas = _demo()
    base = next(x for x in fichas if x["dataset"] == "dim_products")
    with pytest.raises(ValueError):             # no se saltea la revisión
        steward.cambiar_certificacion("dim_products", "certificado", "Ana", base=base)
    steward.cambiar_certificacion("dim_products", "en_revision", "Ana", "pedido", base=base,
                                  ahora=T0)
    steward.cambiar_certificacion("dim_products", "certificado", "Owner Ops", "ok", ahora=T0)
    vig = steward.ficha_vigente("dim_products")
    assert vig["estado_cert"] == "certificado"
    assert vig["cert_por"] == "Owner Ops" and vig["cert_en"].startswith("2026-09-01")
    steward.cambiar_certificacion("dim_products", "deprecado", "Owner Ops")
    with pytest.raises(ValueError):             # deprecado es terminal
        steward.cambiar_certificacion("dim_products", "borrador", "Owner Ops")
    audit = steward.cambios_df(["dim_products"])
    assert (audit["tipo"] == "certificacion").sum() == 3
    assert len(steward.historial_ficha("dim_products")) == 3


def test_no_se_certifica_un_dataset_sin_duenio():
    uni = fuente.universo("es", _mis_datos())
    f = steward.fichas(uni["catalog"], uni["quality_results"], uni["dictionary"])[0]
    assert f["dueno_negocio"] == "" and f["data_steward"] == ""
    steward.cambiar_certificacion("mis_ventas", "en_revision", "Ana", base=f)
    with pytest.raises(ValueError, match="dueño"):
        steward.cambiar_certificacion("mis_ventas", "certificado", "Ana")


# -------------------------------------------------------------- incidentes
def test_cada_regla_que_falla_abre_un_incidente_y_es_idempotente():
    res, fichas = _demo()
    fallan = res[res["status"] != "pass"]
    n = steward.sincronizar_incidentes(res, fichas, ahora=T0)
    assert n["abiertos"] >= len(fallan) > 0
    assert steward.sincronizar_incidentes(res, fichas, ahora=T0) == {"abiertos": 0,
                                                                      "resueltos": 0}
    inc = steward.incidentes_df(res, fichas, ahora=T0)
    assert set(fallan["rule_id"]) <= set(inc["rule_id"])
    assert (inc["origen"] == "registrado").all()
    fila = inc[inc["rule_id"] == fallan.iloc[0]["rule_id"]].iloc[0]
    esperado = next(f["data_steward"] for f in fichas if f["dataset"] == fila["dataset"])
    assert fila["responsable"] == esperado
    assert fila["severidad"] in steward.SEVERIDADES
    assert fila["sla_h"] == steward.SLA_RESOLUCION_H[fila["severidad"]]


def test_el_steward_mueve_el_incidente_y_el_mttr_se_calcula():
    res, fichas = _demo()
    steward.sincronizar_incidentes(res, fichas, ahora=T0)
    iid = steward.incidentes_df(res, fichas, ahora=T0)["id"].iloc[0]
    with pytest.raises(ValueError):
        steward.actualizar_incidente(iid, "abierto", "Ana")       # ya está abierto
    steward.actualizar_incidente(iid, "en_curso", "Ana", "mirando", ahora=T0)
    steward.actualizar_incidente(iid, "resuelto", "Ana", "corregido en origen",
                                 ahora=T0 + timedelta(hours=10))
    inc = steward.incidentes_df(res, fichas, ahora=T0 + timedelta(hours=10))
    k = steward.kpis(fichas, inc)
    assert k["mttr_horas"] == 10.0
    assert inc.set_index("id").loc[iid, "resuelto_por"] == "Ana"
    assert len(steward.historial_incidente(iid)) == 3      # apertura + 2 eventos
    assert k["abiertos_por_dominio"] and k["incidentes_abiertos"] == \
        int((inc["estado"] != "resuelto").sum())


def test_si_la_regla_vuelve_a_pasar_el_incidente_se_cierra_solo():
    res, fichas = _demo()
    steward.sincronizar_incidentes(res, fichas, ahora=T0)
    arreglado = res.assign(status="pass", score=100.0)
    n = steward.sincronizar_incidentes(arreglado, fichas, ahora=T0 + timedelta(hours=1))
    assert n["resueltos"] > 0
    inc = steward.incidentes_df(arreglado, fichas)
    assert (inc["estado"] == "resuelto").all()
    assert set(inc["resuelto_por"]) == {steward.SISTEMA}


def test_vencimientos_de_sla_y_tablero_del_steward():
    res, fichas = _demo()
    steward.sincronizar_incidentes(res, fichas, ahora=T0)
    luego = T0 + timedelta(days=30)
    inc = steward.incidentes_df(res, fichas, ahora=luego)
    assert inc["vencido"].all()
    tab = steward.tablero(fichas, inc, steward="M. Viera", ahora=luego)
    assert set(tab["mis_datasets"]["dataset"]) == {"dim_customers"}
    assert set(tab["incidentes_abiertos"]["dataset"]) == {"dim_customers"}
    assert len(tab["pendientes_certificacion"]) == 1
    venc = tab["vencimientos"]
    assert {"frescura", "incidente"} <= set(venc["tipo"])
    assert (venc["atraso_h"] > 0).all()
    # Lo recién cargado está fresco aunque el catálogo tenga otra fecha.
    fresco = steward.vencimientos(fichas, inc.iloc[0:0], ahora=luego,
                                  ultima_carga={f["dataset"]: luego.isoformat()
                                                for f in fichas})
    assert fresco.empty


def test_datasets_sin_duenio_aparecen_en_el_tablero():
    uni = fuente.universo("es", _mis_datos())
    fichas = steward.fichas(uni["catalog"], uni["quality_results"], uni["dictionary"])
    inc = steward.incidentes_df(uni["quality_results"], fichas)
    tab = steward.tablero(fichas, inc)
    assert list(tab["sin_dueno"]["dataset"]) == ["mis_ventas"]
    assert steward.kpis(fichas, inc)["pct_con_dueno"] == 0.0


# ------------------------------------------------------ contrato de esquema
def test_el_contrato_inicial_sale_del_perfilado():
    df = _mis_datos()["mis_ventas"]
    con = contrato_esquema.generar_contrato(df, "mis_ventas")
    cols = {c["name"]: c for c in con["columns"]}
    assert cols["venta_id"]["key"] and not cols["venta_id"]["nullable"]
    assert cols["cliente_id"]["type"] == "integer" and cols["cliente_id"]["nullable"]
    assert cols["monto"]["type"] == "number"
    assert cols["canal"]["accepted_values"] == ["tienda", "web"]
    assert cols["email"]["accepted_values"] is None        # PII: no se enumera
    assert contrato_esquema.validar_contrato(df, con) == []


def test_validar_contrato_detecta_cada_tipo_de_violacion():
    df = _mis_datos()["mis_ventas"]
    con = contrato_esquema.generar_contrato(df, "mis_ventas")
    malo = df.drop(columns=["monto"]).assign(
        extra=1, canal=["web", "fax", "web", "tienda", "web"],
        venta_id=[1, 1, 2, None, 3], email=[1, 2, 3, 4, 5])
    checks = {v["check"] for v in contrato_esquema.validar_contrato(malo, con)}
    assert {"columna_faltante", "columna_no_declarada", "valor_no_aceptado",
            "clave_duplicada", "clave_nula", "tipo"} <= checks
    no_nulo = {**con, "columns": [dict(c, nullable=False) if c["name"] == "cliente_id"
                                  else c for c in con["columns"]]}
    assert any(v["check"] == "nulos" for v in contrato_esquema.validar_contrato(df, no_nulo))


def test_el_contrato_se_exporta_a_yaml_valido():
    yaml = pytest.importorskip("yaml")
    con = contrato_esquema.generar_contrato(load_demo_tables()["fct_sales"], "fct_sales")
    doc = yaml.safe_load(contrato_esquema.a_yaml(con))
    modelo = doc["models"][0]
    assert modelo["name"] == "fct_sales"
    cols = {c["name"]: c for c in modelo["columns"]}
    assert set(cols) == set(load_demo_tables()["fct_sales"].columns)
    assert "unique" in cols["sale_id"]["data_tests"]
    valores = next(t for t in cols["channel"]["data_tests"] if isinstance(t, dict))
    assert "web" in valores["accepted_values"]["values"]


def test_guardar_contrato_versiona_y_audita():
    df = _mis_datos()["mis_ventas"]
    con = contrato_esquema.generar_contrato(df, "mis_ventas")
    contrato_esquema.guardar_contrato(con, "Ana", "primer contrato", ahora=T0)
    con2 = {**con, "columns": [dict(c, accepted_values=["web", "tienda", "app"])
                               if c["name"] == "canal" else c for c in con["columns"]]}
    contrato_esquema.guardar_contrato(con2, "Ana", "se suma el canal app", ahora=T0)
    hist = contrato_esquema.historial("mis_ventas")
    assert [h["version"] for h in hist] == [1, 2]
    assert contrato_esquema.contrato_para("mis_ventas", df)["version"] == 2
    audit = steward.cambios_df(["mis_ventas"])
    assert list(audit["tipo"]) == ["contrato", "contrato"]
    assert "app" in audit.iloc[0]["despues"] and "app" not in audit.iloc[0]["antes"]
    with pytest.raises(ValueError):
        contrato_esquema.guardar_contrato({**con, "columns": []}, "Ana")
    tabla = contrato_esquema.contratos_df({"mis_ventas": df})
    assert set(tabla["version"]) == {2} and len(tabla) == len(df.columns)


# --------------------------------------------------------------- auditoría
def test_un_cambio_de_glosario_queda_auditado():
    from mvdg import curation
    item = curation.list_items("es").query("kind == 'glossary'").iloc[0]["item_id"]
    curation.save_validation(item, "es", "modificado", "Definición nueva",
                             "Laura Owner", "Data Owner", "alineado con finanzas")
    audit = steward.cambios_df()
    fila = audit[audit["objeto"] == item].iloc[0]
    assert fila["tipo"] == "glosario" and fila["antes"] == "sugerido_ia"
    assert "Definición nueva" in fila["despues"] and fila["quien"] == "Laura Owner"
    assert fila["motivo"] == "alineado con finanzas"


def test_un_cambio_sin_diferencia_no_se_registra():
    assert steward.registrar_cambio("ficha", "x", "a", "a", "Ana") is None
    with pytest.raises(ValueError):
        steward.registrar_cambio("inventado", "x", "a", "b", "Ana")
    assert steward.cambios_df().empty


# -------------------------------------------------------------- exportación
def test_el_paquete_bi_trae_las_hojas_del_steward():
    from mvdg.exporters import bi_bundle_xlsx
    libro = pd.read_excel(io.BytesIO(bi_bundle_xlsx("es")), sheet_name=None)
    for hoja in ("steward", "contratos", "incidentes", "cambios_criterio"):
        assert hoja in libro, hoja
    assert set(catalog.dataset_names()) <= set(libro["steward"]["dataset"])
    assert set(libro["contratos"]["dataset"]) == set(catalog.dataset_names())
    assert len(libro["incidentes"]) > 0


def test_con_datos_propios_el_paquete_no_trae_nada_de_la_demo():
    """Aunque la carpeta ya tenga fichas, incidentes, contratos y cambios de
    la demo guardados, el paquete del cliente es SOLO del cliente."""
    from mvdg import curation
    from mvdg.exporters import bi_bundle_xlsx
    res, fichas = _demo()
    steward.sincronizar_incidentes(res, fichas)
    steward.guardar_ficha("dim_customers", {"custodio_tecnico": "DBA"}, "Ana")
    contrato_esquema.guardar_contrato(contrato_esquema.generar_contrato(
        load_demo_tables()["fct_sales"], "fct_sales"), "Ana")
    item = curation.list_items("es").query("kind == 'glossary'").iloc[0]["item_id"]
    curation.save_validation(item, "es", "validado", "", "Ana", "Steward")

    libro = pd.read_excel(io.BytesIO(bi_bundle_xlsx(
        "es", user_datasets=_mis_datos(), solo_usuario=True)), sheet_name=None)
    for hoja in ("steward", "contratos", "incidentes", "cambios_criterio"):
        df = libro[hoja]
        if "dataset" in df.columns:
            assert set(df["dataset"].dropna().astype(str)) <= {"mis_ventas"}, hoja
        texto = df.astype(str).to_string()
        fugas = sorted(a for a in AJENOS if a in texto)
        assert not fugas, (hoja, fugas)
    assert list(libro["steward"]["dataset"]) == ["mis_ventas"]
    assert set(libro["contratos"]["dataset"]) == {"mis_ventas"}
    assert libro["cambios_criterio"].empty       # el glosario de la demo no entra


# ---------------------------------------------------------------------- API
def test_la_api_sirve_las_vistas_del_steward():
    from fastapi.testclient import TestClient

    from bi_api.main import app
    c = TestClient(app)
    r = c.get("/api/steward/steward", params={"lang": "en"})
    assert r.status_code == 200 and r.json()["rows"] >= len(catalog.dataset_names())
    assert c.get("/api/steward/incidentes", params={"format": "csv"}).text.startswith("id")
    kpis = {x["kpi"] for x in c.get("/api/steward/kpis").json()["data"]}
    assert {"pct_certificados", "pct_con_dueno", "mttr_horas"} <= kpis
    y = c.get("/api/steward/contrato/fct_sales", params={"format": "yaml"})
    assert y.status_code == 200 and "models:" in y.text
    j = c.get("/api/steward/contrato/fct_sales").json()
    assert j["contract"]["dataset"] == "fct_sales" and isinstance(j["violations"], list)
    assert c.get("/api/steward/nada").status_code == 404
    assert c.get("/api/steward/contrato/nada").status_code == 404
    # Consultar la API no escribe incidentes en disco.
    assert steward.leer_registros("steward_incidentes.json") == []


# ----------------------------------------------------------------------- UI
def _app(monkeypatch, datos=None):
    from streamlit.testing.v1 import AppTest
    for v in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY",
              "XAI_API_KEY", "MVDG_AI_API_KEY", "MVDG_AI_PROVIDER"):
        monkeypatch.delenv(v, raising=False)
    at = AppTest.from_file(os.path.join(RAIZ, "app", "app.py"), default_timeout=300)
    if datos:
        at.session_state["mvdg_user_datasets"] = datos
    at.run()
    assert not at.exception, [str(e.value)[:300] for e in at.exception]
    return at


def test_la_pestania_del_steward_guarda_una_ficha_desde_la_ui(monkeypatch):
    at = _app(monkeypatch)
    # Al abrir, cada regla que falla ya tiene su incidente en la cola.
    assert steward.leer_registros("steward_incidentes.json")
    ds = at.selectbox(key="stw_ds").value
    at.text_input(key=f"stw_cus_{ds}").input("Equipo DBA")
    at.text_input(key=f"stw_who_{ds}").input("Ana Steward")
    at.text_input(key=f"stw_why_{ds}").input("alta del custodio")
    at.button(key="stw_save_sheet").click().run()
    assert not at.exception, [str(e.value)[:300] for e in at.exception]
    hist = steward.historial_ficha(ds)
    assert len(hist) == 1 and hist[0]["custodio_tecnico"] == "Equipo DBA"
    assert hist[0]["guardado_por"] == "Ana Steward"
    assert "custodio_tecnico" in set(steward.cambios_df([ds])["objeto"])


def test_la_pestania_del_steward_con_datos_propios_no_muestra_la_demo(monkeypatch):
    at = _app(monkeypatch, _mis_datos())
    assert at.selectbox(key="stw_ds").options == ["mis_ventas"]
    assert at.selectbox(key="stw_con_ds").options == ["mis_ventas"]
    incs = steward.leer_registros("steward_incidentes.json")
    assert incs and {e["dataset"] for e in incs if "dataset" in e} == {"mis_ventas"}
