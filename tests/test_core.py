"""
MV Data Governance · Suite de pruebas del motor, i18n, exportadores y API.

Ejecutar:  pytest tests/ -v
"""
from __future__ import annotations

import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mvdg.catalog import catalog_df, dictionary_df, dataset_names, pii_columns
from mvdg.demo_data import load_demo_tables
from mvdg.exporters import (bi_bundle_xlsx, governance_tables, to_csv_bytes,
                            to_excel_bytes, to_json_bytes)
from mvdg.glossary import glossary_df, term_count
from mvdg.i18n import LANGS, _T, all_keys, t
from mvdg.lineage import EDGES, NODES, downstream, lineage_df, lineage_figure, upstream
from mvdg.policies import policies_df
from mvdg.profiler import profile_table, suggest_rules, summary
from mvdg.quality import (DIMENSIONS, RULES, open_issues, overall_index,
                          quality_by_dataset, quality_by_dimension,
                          quality_matrix, quality_trend, run_rules)


# ------------------------------------------------------------------- i18n
def test_i18n_parity_all_languages():
    """Cada clave existe en los 3 idiomas y no está vacía."""
    for key, entry in _T.items():
        for lang in LANGS:
            assert entry.get(lang), f"Falta traducción {lang} para {key}"


def test_i18n_fallback():
    assert t("clave_inexistente", "en") == "clave_inexistente"
    assert t("app_title", "xx") == t("app_title", "es")
    assert len(all_keys()) > 80


# -------------------------------------------------------------- demo data
def test_demo_tables_deterministic():
    a, b = load_demo_tables(), load_demo_tables()
    for name in a:
        pd.testing.assert_frame_equal(a[name], b[name])


def test_demo_tables_have_injected_issues():
    tables = load_demo_tables()
    assert tables["dim_customers"]["email"].isna().sum() > 0
    assert (tables["dim_products"]["unit_price"] <= 0).sum() > 0
    assert tables["dim_customers"].duplicated(subset=["customer_id"]).sum() > 0


# ---------------------------------------------------------------- catálogo
@pytest.mark.parametrize("lang", LANGS)
def test_catalog_and_dictionary(lang):
    cat = catalog_df(lang)
    dic = dictionary_df(lang)
    assert set(cat["dataset"]) == set(dataset_names())
    assert (cat["rows"] > 0).all()
    assert dic["description"].str.len().gt(0).all()
    for ds, col in pii_columns():
        row = dic[(dic["dataset"] == ds) & (dic["column"] == col)]
        assert bool(row["pii"].iloc[0])


def test_catalog_translations_differ():
    es = catalog_df("es")["description"].iloc[0]
    en = catalog_df("en")["description"].iloc[0]
    assert es != en


# ----------------------------------------------------------------- calidad
def test_rules_cover_all_dimensions():
    assert {r.dimension for r in RULES} == set(DIMENSIONS)


@pytest.mark.parametrize("lang", LANGS)
def test_run_rules(lang):
    res = run_rules(lang=lang)
    assert len(res) == len(RULES)
    assert res["score"].between(0, 100).all()
    assert set(res["status"]) <= {"pass", "warn", "fail"}
    assert (res.loc[res["status"] == "pass", "score"]
            >= res.loc[res["status"] == "pass", "threshold"]).all()


def test_quality_aggregations():
    res = run_rules()
    assert 0 < overall_index(res) <= 100
    assert len(quality_by_dataset(res)) == len(dataset_names())
    assert quality_matrix(res).shape[0] == len(dataset_names())
    assert len(quality_by_dimension(res)) <= len(DIMENSIONS)
    trend = quality_trend(res)
    assert len(trend) == 12
    assert trend["quality_index"].iloc[-1] == overall_index(res)
    issues = open_issues(res)
    assert (issues["severity"].isin(["media", "alta"])).all()


# ------------------------------------------------------------------ linaje
def test_lineage_graph_consistency():
    ids = {n["id"] for n in NODES}
    for a, b in EDGES:
        assert a in ids and b in ids
    assert "crm" in upstream("bi_dashboard")
    assert "bi_dashboard" in downstream("crm")
    assert upstream("crm") == set()
    assert len(lineage_df()) == len(EDGES)
    fig = lineage_figure("fct_sales", {"source": "Fuentes"})
    assert len(fig.data) == len(EDGES) + 1  # aristas + capa de nodos


# ---------------------------------------------------------------- glosario
@pytest.mark.parametrize("lang", LANGS)
def test_glossary(lang):
    g = glossary_df(lang)
    assert len(g) == term_count()
    assert g["definition"].str.len().gt(10).all()
    known = set(dataset_names())
    for linked in g["linked_datasets"]:
        assert set(linked.split(", ")) <= known


# --------------------------------------------------------------- políticas
@pytest.mark.parametrize("lang", LANGS)
def test_policies(lang):
    p = policies_df(lang)
    assert len(p) == 6
    assert set(p["status"]) <= {"compliant", "partial", "noncompliant"}
    assert p["evidence"].str.len().gt(5).all()


# --------------------------------------------------------------- perfilador
def test_profiler_detects_issues_and_pii():
    df = load_demo_tables()["dim_customers"]
    prof = profile_table(df)
    assert "email" in prof.loc[prof["possible_pii"], "column"].tolist()
    info = summary(df)
    assert info["duplicate_rows"] > 0 and info["pii_columns"] >= 2
    for lang in LANGS:
        sugs = suggest_rules(df, lang)
        assert len(sugs) > 0


def test_profiler_empty_frame():
    empty = pd.DataFrame({"a": []})
    assert summary(empty)["rows"] == 0
    assert len(profile_table(empty)) == 1


# ------------------------------------------------------------- exportadores
@pytest.mark.parametrize("lang", LANGS)
def test_governance_tables_complete(lang):
    tabs = governance_tables(lang)
    assert set(tabs) == {"catalog", "dictionary", "quality_results",
                         "quality_by_dataset", "quality_by_dimension",
                         "lineage", "glossary", "policies", "kpis"}
    for name, df in tabs.items():
        assert len(df) > 0, name


def test_export_formats():
    df = catalog_df("es")
    assert to_csv_bytes(df).startswith("dataset".encode("utf-8-sig"))
    assert to_excel_bytes(df)[:2] == b"PK"      # zip/xlsx
    assert b"dim_customers" in to_json_bytes(df)
    assert bi_bundle_xlsx("pt")[:2] == b"PK"


# ------------------------------------------------------------ fichas clientes
def test_clients_crud_persistence(tmp_path, monkeypatch):
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    from mvdg import clients
    assert clients.load_clients() == []
    rec = clients.save_client({"company": "ACME", "country": "UY",
                               "it_restriction": "no_exe_python_ok",
                               "recommended_pack": clients.recommended_pack("no_exe_python_ok"),
                               "maturity": 3, "status": "demo"})
    assert rec["client_id"] and rec["created_at"]
    assert rec["recommended_pack"] == "B"
    # actualizar conserva id y created_at
    rec2 = clients.save_client({**rec, "status": "piloto"})
    assert rec2["client_id"] == rec["client_id"]
    assert rec2["created_at"] == rec["created_at"]
    assert len(clients.load_clients()) == 1
    # persiste en disco (relectura fría)
    df = clients.clients_df()
    assert df.iloc[0]["company"] == "ACME" and df.iloc[0]["status"] == "piloto"
    # borrar
    assert clients.delete_client(rec["client_id"]) is True
    assert clients.delete_client("nope") is False
    assert clients.clients_df().empty


def test_clients_recommended_pack():
    from mvdg.clients import recommended_pack
    assert recommended_pack("exe_ok") == "A"
    assert recommended_pack("no_exe_python_ok") == "B"
    assert recommended_pack("solo_web") == "Web"
    assert recommended_pack("???") == "B"


def test_clients_corrupt_file_is_safe(tmp_path, monkeypatch):
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    from mvdg import clients
    with open(tmp_path / "clientes.json", "w") as fh:
        fh.write("{esto no es json valido")
    assert clients.load_clients() == []


# ------------------------------------------------------------- centro de ayuda
@pytest.mark.parametrize("lang", LANGS)
def test_help_center(lang):
    from mvdg.help_center import AUTOMATION, SPEECHES, automation_rows, speeches
    rows = automation_rows(lang)
    assert len(rows) == len(AUTOMATION) >= 6
    assert {r["level"] for r in rows} == {"auto", "partial", "human"}
    sps = speeches(lang)
    assert len(sps) == len(SPEECHES) == 5
    for sp in sps:
        assert len(sp["text"]) > 200 and sp["title"] and sp["audience"]
    # cada área no automática apunta a un speech existente (círculo cerrado)
    ids = {s["speech_id"] for s in sps}
    for r in rows:
        if r["level"] != "auto":
            assert r["speech_id"] in ids


def test_help_center_translations_differ():
    from mvdg.help_center import speeches
    assert speeches("es")[0]["text"] != speeches("en")[0]["text"]
    assert speeches("pt")[0]["text"] != speeches("en")[0]["text"]


# ---------------------------------------------------------------- release zip
def test_build_release_option_b(tmp_path, monkeypatch):
    # la carpeta packaging/ del repo queda tapada por la librería 'packaging'
    # de PyPI, asi que se carga el modulo directamente por ruta
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "mvdg_build_release",
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "packaging", "build_release.py"))
    br = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(br)
    monkeypatch.setattr(br, "DIST", str(tmp_path))
    out = br.build_option_b()
    assert os.path.exists(out)
    import zipfile
    names = zipfile.ZipFile(out).namelist()
    assert "MVDataGovernance/MV_DataGovernance.bat" in names
    assert "MVDataGovernance/app/app.py" in names
    assert "MVDataGovernance/requirements.txt" in names
    assert not any(".venv" in n or "__pycache__" in n for n in names)
    assert br.build_option_a() is None  # sin Setup.exe construido


# ---------------------------------------------------- conectores a base de datos
def test_connectors_sqlite_end_to_end(tmp_path, monkeypatch):
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    pytest.importorskip("sqlalchemy")
    import sqlite3
    from mvdg import connectors as C

    db = str(tmp_path / "empresa.db")
    con = sqlite3.connect(db)
    pd.DataFrame({"id": [1, 2, 3], "email": ["a@x.com", None, "mal"],
                 "monto": [10, -5, 20]}).to_sql("ventas", con, index=False)
    con.close()

    prof = {"name": "demo", "engine": "sqlite", "database": db,
            "user": "", "password": "clave"}
    saved = C.save_connection(prof, save_password=True)
    assert saved["conn_id"]
    # contraseña no queda en texto plano pero es recuperable
    assert "clave" not in open(C._file(), encoding="utf-8").read()
    assert C.stored_password(C.load_connections()[0]) == "clave"

    ok, msg = C.test_connection(saved)
    assert ok, msg
    assert "ventas" in C.list_tables(saved)
    df = C.load_table(saved, "ventas", limit=100)
    assert len(df) == 3 and "email" in df.columns
    q = C.run_query(saved, "SELECT id FROM ventas WHERE monto > 0")
    assert len(q) == 2
    assert C.delete_connection(saved["conn_id"]) is True
    assert C.load_connections() == []


def test_connectors_guards():
    from mvdg import connectors as C
    # motor desconocido
    with pytest.raises(ValueError):
        C.build_url({"engine": "no-existe"})
    # solo lectura en run_query
    with pytest.raises(ValueError):
        C.run_query({"engine": "sqlite", "database": ":memory:"},
                    "DELETE FROM x")
    # driver ausente -> mensaje legible, no excepción
    ok, msg = C.test_connection({"engine": "postgresql", "host": "localhost",
                                 "port": 5432, "database": "x",
                                 "user": "u", "password": "p"})
    assert ok is False and "driver" in msg.lower()


# ------------------------------------------------------------- auto-diagnostico
def test_selfcheck_all_pass():
    from mvdg.selfcheck import run_checks
    results = run_checks()
    assert len(results) >= 12
    failed = [(n, d) for n, ok, d in results if not ok]
    assert not failed, f"selfcheck fallo: {failed}"


# --------------------------------------------------- caso de ejemplo (impacto)
def test_medir_impacto_reproducible():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "mvdg_medir_impacto",
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "docs", "caso_ejemplo", "medir_impacto.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    r = mod.medir()
    # el "despues" debe ser mejor que el "antes" en indice y filas afectadas
    assert r["despues"]["indice"] > r["antes"]["indice"]
    assert r["despues"]["filas_afectadas"] < r["antes"]["filas_afectadas"]
    assert r["mejora_indice"] > 0 and r["reduccion_filas_pct"] > 0
    # determinista: dos corridas dan el mismo resultado
    assert mod.medir()["antes"]["indice"] == r["antes"]["indice"]


# --------------------------------------------------------------------- API
def test_api_all_tables_and_formats():
    pytest.importorskip("fastapi")
    try:
        from fastapi.testclient import TestClient
    except RuntimeError:
        pytest.skip("httpx2 no disponible para TestClient")
    from api.main import TABLES, app
    c = TestClient(app)
    assert c.get("/health").json() == {"status": "ok"}
    for tbl in TABLES:
        r = c.get(f"/api/{tbl}", params={"lang": "pt"})
        assert r.status_code == 200
        body = r.json()
        assert body["rows"] == len(body["data"]) > 0
    assert c.get("/api/catalog", params={"format": "csv"}).text.startswith("dataset")
    assert c.get("/api/nope").status_code == 404
    assert c.get("/api/catalog", params={"lang": "xx"}).status_code == 422
