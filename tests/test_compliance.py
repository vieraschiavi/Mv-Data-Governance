# © 2026 Martín Viera. Todos los derechos reservados.
"""Registros de Compliance gobernados por ficha: la declaración de conflictos
de interés y el registro de vínculo con licenciantes.
"""
from __future__ import annotations

import io
import json
import os
import sys

import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from mvdg import compliance, steward  # noqa: E402
from mvdg.i18n import LANGS  # noqa: E402

CORTE = "2026-09-30"


@pytest.fixture(autouse=True)
def _carpeta_aislada(tmp_path, monkeypatch):
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    monkeypatch.delenv(compliance.ENV_PERFIL, raising=False)
    return tmp_path


def _por_regla(res) -> dict[str, set[str]]:
    h = res["hallazgos"]
    return {r: set(h.loc[h["regla"] == r, "colaborador"]) for r in h["regla"].unique()}


# ------------------------------------------------------------------ perfil
def test_sin_perfil_se_usa_el_generico_y_lo_dice():
    p = compliance.perfil_activo()
    assert p["generico"] is True
    f = compliance.ficha("licenciantes", p)
    assert "genérico" in f.iloc[-1, 1]


def test_el_perfil_propio_se_guarda_local_y_manda(tmp_path):
    ruta = compliance.guardar_perfil({
        "organizacion": "Org X", "sistema_fuente": "Sistema RRHH",
        "licenciantes": {"areas_obligadas": [{"area": "Calidad",
                                              "posiciones": ["Head"]}]}})
    assert ruta.startswith(str(tmp_path))
    p = compliance.perfil_activo()
    assert p["generico"] is False and p["organizacion"] == "Org X"
    # Lo que el perfil no trae se completa con el genérico.
    assert p["coi"]["periodicidad_meses"] == 12
    assert compliance.es_obligado("Calidad", "Head de Calidad", p)
    assert not compliance.es_obligado("Calidad", "Analista", p)
    f = compliance.ficha("licenciantes", p)
    assert "Sistema RRHH" in set(f.iloc[:, 1]) and "Calidad: Head" in set(f.iloc[:, 1])


def test_un_perfil_roto_no_rompe_y_avisa(tmp_path):
    (tmp_path / compliance.ARCHIVO_PERFIL).write_text("{ esto no es json", "utf-8")
    p = compliance.perfil_activo()
    assert p["generico"] is True and p["aviso"]
    with pytest.raises(ValueError):
        compliance.guardar_perfil({"licenciantes": {"areas_obligadas": [{"x": 1}]}})


def test_el_perfil_puede_venir_de_una_variable_de_entorno(tmp_path, monkeypatch):
    ruta = tmp_path / "otro.json"
    ruta.write_text(json.dumps({"organizacion": "Por env"}), "utf-8")
    monkeypatch.setenv(compliance.ENV_PERFIL, str(ruta))
    assert compliance.perfil_activo()["organizacion"] == "Por env"


# ------------------------------------------------------------------ fichas
@pytest.mark.parametrize("lang", LANGS)
@pytest.mark.parametrize("tipo", compliance.TIPOS)
def test_la_ficha_esta_completa_en_los_tres_idiomas(tipo, lang):
    f = compliance.ficha(tipo, lang=lang)
    assert len(f) >= 10
    assert all(str(v).strip() and "{" not in str(v) for v in f.iloc[:, 1])
    r = compliance.reglas_df(tipo, lang)
    assert len(r) == len(compliance.REGLAS[tipo])
    assert r["accion"].str.len().min() > 10


def test_la_ficha_dice_que_no_se_modifica():
    f = compliance.ficha("coi")
    texto = " ".join(f.iloc[:, 1])
    assert "¿Cuándo deben entrar en vigor estos cambios?" in texto
    assert "NO se modifica" in texto


# ------------------------------------------------------------- validación
def test_coi_encuentra_cada_defecto_inyectado():
    d = compliance.demo()
    res = compliance.validar_coi(d["coi"], d["maestro"], corte=CORTE)
    por = _por_regla(res)
    assert por["COI-01"] == {"C005", "C038", "C039"}   # vencida + sin declarar
    assert por["COI-02"] == {"C011"}
    assert por["COI-03"] == {"C007"}                    # Sí sin detalle; C009 sí trae
    assert por["COI-04"] == {"C013"}
    assert por["COI-05"] == {"C005"}
    assert por["COI-06"] == {"C003"}
    # El inactivo (C040) no se exige.
    assert "C040" not in set(res["hallazgos"]["colaborador"])
    r = res["resultados"].set_index("rule_id")
    assert set(r["dimension"]) <= set(steward.DIMENSIONES)
    assert (r["status"] != "pass").all()


def test_licenciantes_encuentra_cada_defecto_inyectado():
    d = compliance.demo()
    res = compliance.validar_licenciantes(d["licenciantes"], d["maestro"], corte=CORTE)
    por = _por_regla(res)
    assert por["LIC-01"] == {"C002", "C010"}           # Legales sin registro
    assert por["LIC-04"] == {"C003"}                    # licenciante vacío
    assert por["LIC-05"] == {"C009"}                    # TODOS + otro
    assert por["LIC-07"] == {"C001"}                    # fecha fin tocada
    # Los gerentes de Finanzas son obligados y declararon no tener vínculo.
    assert por["LIC-02"] and all(c in {"C011", "C019", "C027", "C035"}
                                 for c in por["LIC-02"])
    # El personal operativo de planta está exento: nadie lo reclama.
    operativos = set(d["maestro"].query("Posición == 'Operativo'")["Colaborador"])
    assert not operativos & set(res["hallazgos"]["colaborador"])
    assert any("exentos" in n for n in res["notas"])


def test_sin_maestro_la_cobertura_no_se_inventa():
    d = compliance.demo()
    res = compliance.validar_coi(d["coi"], None, corte=CORTE)
    r = res["resultados"].set_index("rule_id")
    assert r.loc["COI-01", "medible"] == False  # noqa: E712
    assert r.loc["COI-01", "status"] == "warn" and r.loc["COI-01", "score"] == 0
    assert any("maestro" in n for n in res["notas"])
    k = compliance.resumen(res)
    assert k["no_medibles"] == 1


def test_un_export_limpio_no_tiene_hallazgos():
    maestro = pd.DataFrame({"Legajo": ["A1", "A2"], "Área": ["IT", "IT"],
                            "Puesto": ["Analista", "Analista"]})
    coi = pd.DataFrame({"Legajo": ["A1", "A2"],
                        "Fecha de registro": ["15/09/2026", "20/09/2026"],
                        "Fecha de vigencia": ["15/09/2026", "20/09/2026"],
                        "¿Pregunta 1?": ["No", "Sí"], "Detalle": ["", "Explicado"]})
    res = compliance.validar_coi(coi, maestro, corte=CORTE)
    assert res["hallazgos"].empty
    assert (res["resultados"]["status"] == "pass").all()
    lic = pd.DataFrame({"Legajo": ["A1", "A2"],
                        "Licenciante": ["Ninguno", "Ninguno"],
                        "Fecha de inicio": ["", ""], "Fecha de fin": ["", ""]})
    res = compliance.validar_licenciantes(lic, maestro, corte=CORTE)
    assert res["hallazgos"].empty, res["hallazgos"]


def test_sin_columna_de_colaborador_no_valida_y_lo_dice():
    res = compliance.validar_coi(pd.DataFrame({"x": [1]}), corte=CORTE)
    assert res["resultados"].empty and res["notas"]


def test_las_fechas_se_leen_en_iso_y_en_dia_mes():
    s = compliance._fecha(pd.Series(["2026-09-10", "10/09/2026", "", None]))
    assert s[0] == s[1] == pd.Timestamp("2026-09-10")
    assert s[2:].isna().all()


@pytest.mark.parametrize("lang", LANGS)
def test_hallazgos_y_notas_en_los_tres_idiomas(lang):
    d = compliance.demo()
    for tipo, fn in (("coi", compliance.validar_coi),
                     ("licenciantes", compliance.validar_licenciantes)):
        res = fn(d[tipo], d["maestro"], corte=CORTE, lang=lang)
        textos = list(res["hallazgos"]["detalle"]) + list(res["hallazgos"]["accion"]) \
            + list(res["notas"]) + list(res["resultados"]["description"])
        assert textos and all(t and "{" not in t for t in textos)


# ------------------------------------------------------ incidentes y export
def test_las_reglas_que_fallan_abren_incidentes_en_la_cola_del_steward():
    d = compliance.demo()
    res = compliance.validar_coi(d["coi"], d["maestro"], corte=CORTE)
    ficha = compliance.ficha_steward("coi")
    assert ficha["pii"] and ficha["criticidad"] == "alta"
    out = steward.sincronizar_incidentes(res["resultados"], [ficha])
    assert out["abiertos"] >= 6
    # Idempotente.
    assert steward.sincronizar_incidentes(res["resultados"], [ficha])["abiertos"] == 0


def test_el_excel_trae_ficha_reglas_resultados_y_hallazgos():
    d = compliance.demo()
    res = compliance.validar_licenciantes(d["licenciantes"], d["maestro"], corte=CORTE)
    libro = pd.read_excel(io.BytesIO(compliance.a_excel("licenciantes", res)),
                          sheet_name=None)
    assert {"Ficha", "Reglas", "Resultados", "Hallazgos", "Notas"} <= set(libro)
    assert len(libro["Hallazgos"]) == len(res["hallazgos"])
    # Sin datos: igual sale la ficha para mandar.
    solo = pd.read_excel(io.BytesIO(compliance.a_excel("coi", None)), sheet_name=None)
    assert set(solo) == {"Ficha", "Reglas"}


# ----------------------------------------------------------------------- UI
def test_la_subpestania_de_compliance_se_dibuja_con_la_demo(monkeypatch):
    from streamlit.testing.v1 import AppTest
    for v in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY",
              "XAI_API_KEY", "MVDG_AI_API_KEY", "MVDG_AI_PROVIDER"):
        monkeypatch.delenv(v, raising=False)
    at = AppTest.from_file(os.path.join(RAIZ, "app", "app.py"), default_timeout=300)
    at.run()
    assert not at.exception, [str(e.value)[:300] for e in at.exception]
    assert at.radio(key="cmp_tipo").value == "coi"
    at.radio(key="cmp_tipo").set_value("licenciantes").run()
    assert not at.exception, [str(e.value)[:300] for e in at.exception]
    # La demo sintética no abre incidentes en la cola real.
    incs = steward.leer_registros("steward_incidentes.json")
    assert not {e.get("dataset") for e in incs} & set(compliance.DATASET.values())


def test_el_boton_sugerir_llena_los_umbrales_de_la_ficha(tmp_path, monkeypatch):
    """«No entiendo qué umbrales poner»: un clic y quedan cargados."""
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(os.path.join(RAIZ, "app", "app.py"), default_timeout=300)
    at.run()
    ds = at.selectbox(key="stw_ds").value
    for d in steward.DIMENSIONES:
        at.number_input(key=f"stw_q_{d}_{ds}").set_value(1.0)
    at.button(key=f"stw_sug_{ds}").click().run()
    assert not at.exception, [str(e.value)[:300] for e in at.exception]
    valores = {d: at.number_input(key=f"stw_q_{d}_{ds}").value for d in steward.DIMENSIONES}
    assert all(v >= min(steward.PISO_POR_CRITICIDAD.values()) for v in valores.values()), valores


def test_sin_fecha_de_fin_9999_se_entiende_en_pandas_2_y_3():
    """9999-12-31 desbordaba el Timestamp de pandas 2 y la regla LIC-07
    no se medía (CI en Python 3.10 lo agarró)."""
    f = compliance._fecha(pd.Series(["9999-12-31", "31/12/9999", "2026-06-30", None]))
    assert f.iloc[0] == f.iloc[1] == pd.Timestamp(compliance.FECHA_SIN_FIN)
    assert f.iloc[2] == pd.Timestamp("2026-06-30") and pd.isna(f.iloc[3])
    d = compliance.demo()
    import copy
    perfil = copy.deepcopy(compliance.PERFIL_GENERICO)
    perfil["licenciantes"]["fecha_fin_default"] = "9999-12-31"
    res = compliance.validar_licenciantes(d["licenciantes"], d["maestro"], perfil=perfil,
                                          corte=CORTE)
    assert _por_regla(res)["LIC-07"] == {"C001"}
