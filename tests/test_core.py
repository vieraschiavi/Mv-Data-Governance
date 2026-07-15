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
    # las 3 versiones de arranque viajan en el paquete
    assert "MVDataGovernance/MV_DataGovernance_Server.bat" in names
    assert "MVDataGovernance/run_server.sh" in names
    assert "MVDataGovernance/server_authorized.txt" in names
    assert "MVDataGovernance/bi_api/main.py" in names
    assert not any(".venv" in n or "__pycache__" in n for n in names)
    assert br.build_option_a() is None  # sin Setup.exe construido


# ----------------------------------------------------- modo servidor (web)
def test_server_authorization_modes():
    from mvdg.server import authorization_status, parse_authorized

    # sin lista -> modo abierto
    assert authorization_status([])["mode"] == "open"
    # comodín -> autorizado
    assert authorization_status(["*"])["mode"] == "authorized"
    # host no listado -> denegado
    assert authorization_status(["srv-datos"], identities={"otro"})["mode"] == "denied"
    # host listado -> autorizado (case-insensitive)
    st = authorization_status(["SRV-Datos", "10.0.5.20"], identities={"srv-datos"})
    assert st["mode"] == "authorized" and st["matched"] == "srv-datos"


def test_server_parse_authorized_ignores_comments_and_commas():
    from mvdg.server import parse_authorized
    raw = ("# Lista de servidores, con comas en el comentario\n"
           "srv-datos.empresa.local, 10.0.5.20\n"
           "  \n"
           "# otra nota\n"
           "backup.empresa.local\n")
    assert parse_authorized(raw) == [
        "srv-datos.empresa.local", "10.0.5.20", "backup.empresa.local"]
    # env var en una sola línea
    assert parse_authorized("a, B ,c") == ["a", "b", "c"]


def test_server_run_dry_run_builds_streamlit_argv(monkeypatch):
    from mvdg import server
    monkeypatch.setenv("MVDG_SERVER_HOST", "0.0.0.0")
    monkeypatch.setenv("MVDG_SERVER_PORT", "8555")
    monkeypatch.setenv("MVDG_AUTHORIZED_HOSTS", "*")  # autoriza para el dry-run
    argv: list = []
    rc = server.run_server(argv_out=argv)
    assert rc == 0
    assert argv[:3] == ["streamlit", "run", argv[2]]
    assert argv[argv.index("--server.address") + 1] == "0.0.0.0"
    assert argv[argv.index("--server.port") + 1] == "8555"


def test_server_denied_when_host_not_authorized(monkeypatch):
    from mvdg import server
    monkeypatch.setenv("MVDG_AUTHORIZED_HOSTS", "un-host-que-no-soy-yo.local")
    argv: list = []
    rc = server.run_server(argv_out=argv)
    assert rc == 2  # no autorizado: no arranca
    assert argv == []


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


# ------------------------------------------------- conectores Cloud DW/Lake
def test_connectors_cloud_engines_registered():
    from mvdg import connectors as C
    assert {"synapse", "snowflake", "bigquery", "databricks"} <= set(C.ENGINES)
    assert set(C.CLOUD_ENGINES) == {"snowflake", "bigquery", "databricks"}
    for eng in C.CLOUD_ENGINES:
        assert eng in C.EXTRA_EXAMPLE and C.ENGINES[eng]["pip"]


def test_connectors_snowflake_url():
    from mvdg import connectors as C
    profile = {"engine": "snowflake", "user": "u", "database": "DB",
              "extra": {"account": "xy123.us-east-1", "warehouse": "WH",
                       "role": "SYSADMIN", "schema": "PUBLIC"}}
    url = str(C.build_url(profile, password="pw"))
    assert url.startswith("snowflake://u:")
    assert "xy123.us-east-1" in url and "DB/PUBLIC" in url
    assert "warehouse=WH" in url and "role=SYSADMIN" in url


def test_connectors_bigquery_url():
    from mvdg import connectors as C
    profile = {"engine": "bigquery",
              "extra": {"project": "my-proj", "dataset": "my_ds",
                       "credentials_path": "/tmp/creds.json"}}
    url = str(C.build_url(profile))
    assert url == "bigquery://my-proj/my_ds"
    # sin dataset -> solo project
    url2 = str(C.build_url({"engine": "bigquery", "extra": {"project": "my-proj"}}))
    assert url2 == "bigquery://my-proj"


def test_connectors_databricks_url():
    from mvdg import connectors as C
    profile = {"engine": "databricks",
              "extra": {"server_hostname": "adb-1.azuredatabricks.net",
                       "http_path": "/sql/1.0/warehouses/abc", "catalog": "main",
                       "schema": "default"}}
    url = str(C.build_url(profile, password="dapiTOKEN"))
    assert url.startswith("databricks://token:")
    assert "adb-1.azuredatabricks.net" in url
    assert "catalog=main" in url and "schema=default" in url


def test_connectors_synapse_reuses_mssql_driver():
    from mvdg import connectors as C
    assert C.ENGINES["synapse"]["driver"] == C.ENGINES["sqlserver"]["driver"]
    profile = {"engine": "synapse", "host": "myws.sql.azuresynapse.net",
              "port": 1433, "database": "mydb", "user": "admin"}
    url = str(C.build_url(profile, password="pw"))
    assert url.startswith("mssql+pyodbc://admin:")
    assert "myws.sql.azuresynapse.net:1433/mydb" in url


def test_connectors_save_connection_persists_extra(tmp_path, monkeypatch):
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    from mvdg import connectors as C
    profile = {"name": "sf-demo", "engine": "snowflake", "user": "u",
              "database": "DB", "password": "pw",
              "extra": {"account": "xy123", "warehouse": "WH"}}
    saved = C.save_connection(profile, save_password=True)
    reloaded = C.load_connections()[0]
    assert reloaded["extra"] == {"account": "xy123", "warehouse": "WH"}


# --------------------------------------------------------- proyecto por cliente
def test_workspace_save_load_stage_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    from mvdg import workspace as ws
    cid = "cli0001"
    df = pd.DataFrame({"id": [1, 2, 3], "name": ["a", "b", "c"]})
    m = ws.save_stage(cid, "Catálogo inicial", {"dataset": df},
                      kind="dataset", notes="primera carga")
    assert m["stage_id"] and m["name"] == "Catálogo inicial"
    assert m["tables"][0]["rows"] == 3 and m["tables"][0]["cols"] == 2
    # relectura fría (nueva llamada, disco)
    loaded = ws.load_stage(cid, m["stage_id"])
    assert list(loaded["loaded_tables"].keys()) == ["dataset"]
    pd.testing.assert_frame_equal(loaded["loaded_tables"]["dataset"], df)


def test_workspace_list_summary_and_delete(tmp_path, monkeypatch):
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    from mvdg import workspace as ws
    cid = "cli0002"
    df1 = pd.DataFrame({"a": [1, 2]})
    df2 = pd.DataFrame({"b": [1, 2, 3]})
    s1 = ws.save_stage(cid, "Etapa 1", {"t1": df1})
    s2 = ws.save_stage(cid, "Etapa 2", {"t2": df2, "t1": df1})
    stages = ws.list_stages(cid)
    assert [s["name"] for s in stages] == ["Etapa 2", "Etapa 1"]  # más nueva primero
    summ = ws.project_summary(cid)
    assert summ["stages"] == 2 and summ["tables"] == 3 and summ["rows"] == 2 + 3 + 2
    assert ws.delete_stage(cid, s1["stage_id"]) is True
    assert ws.delete_stage(cid, "nope") is False
    assert ws.project_summary(cid)["stages"] == 1


def test_workspace_rejects_empty(tmp_path, monkeypatch):
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    from mvdg import workspace as ws
    with pytest.raises(ValueError):
        ws.save_stage("c", "", {"t": pd.DataFrame({"a": [1]})})  # sin nombre
    with pytest.raises(ValueError):
        ws.save_stage("c", "Etapa", {})  # sin tablas
    with pytest.raises(ValueError):
        ws.save_stage("c", "Etapa", {"t": pd.DataFrame()})  # tabla vacía


def test_workspace_export_import_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    from mvdg import workspace as ws
    cid = "cli0003"
    df = pd.DataFrame({"id": [1, 2, 3, 4]})
    ws.save_stage(cid, "E1", {"d": df})
    ws.save_stage(cid, "E2", {"d": df})
    blob = ws.export_project(cid)
    assert isinstance(blob, bytes) and len(blob) > 0
    # borrar todo y restaurar desde el ZIP
    assert ws.delete_project(cid) is True
    assert ws.project_summary(cid)["stages"] == 0
    n = ws.import_project(cid, blob, replace=True)
    assert n == 2
    names = sorted(s["name"] for s in ws.list_stages(cid))
    assert names == ["E1", "E2"]


# ------------------------------------------------------------- tutorial DMBOK
@pytest.mark.parametrize("lang", LANGS)
def test_dmbok_content_complete(lang):
    from mvdg import dmbok
    assert len(dmbok.areas(lang)) == 11
    assert len(dmbok.principles(lang)) == 6
    assert len(dmbok.concepts(lang)) == 14
    assert len(dmbok.roles(lang)) == 3
    assert len(dmbok.maturity(lang)) == 5
    assert len(dmbok.lifecycle(lang)) == 6
    for a in dmbok.areas(lang):
        assert a["area"] and a["plain"] and a["tech"] and a["deliverables"]
        assert a["coverage"] in ("covered", "partial", "out")
        assert 0 <= a["score"] <= 100
    for c in dmbok.concepts(lang):
        assert c["term"] and c["def"] and c["cat"]


def test_dmbok_coverage_and_radar():
    from mvdg import dmbok
    cov = dmbok.coverage_summary()
    assert cov["covered"] + cov["partial"] + cov["out"] == 11
    radar = dmbok.coverage_scores("es")
    assert len(radar) == 11 and all(0 <= s <= 100 for _, s in radar)


def test_dmbok_translations_differ():
    from mvdg import dmbok
    es = [a["area"] for a in dmbok.areas("es")]
    en = [a["area"] for a in dmbok.areas("en")]
    assert es != en  # están realmente traducidas


# ------------------------------------------------- referencia COBIT 2019 + ISO 38505
@pytest.mark.parametrize("lang", LANGS)
def test_cobit_iso_content_complete(lang):
    from mvdg import cobit_iso as ci
    obs = ci.cobit_objectives(lang)
    assert len(obs) == 8
    for o in obs:
        assert o["code"] and o["name"] and o["plain"] and o["tech"] and o["deliverables"]
        assert o["coverage"] in ("covered", "partial", "out")
        assert 0 <= o["score"] <= 100

    princ = ci.iso_principles(lang)
    assert len(princ) == 6
    for p in princ:
        assert p["name"] and p["text"] and p["note"]
        assert p["coverage"] in ("covered", "partial", "out")

    vrc = ci.iso_vrc(lang)
    assert len(vrc) == 3
    for v in vrc:
        assert v["dim"] and v["text"] and v["mapped"]


def test_cobit_iso_coverage_and_radar():
    from mvdg import cobit_iso as ci
    ccov = ci.cobit_coverage_summary()
    assert ccov["covered"] + ccov["partial"] + ccov["out"] == 8
    icov = ci.iso_coverage_summary()
    assert icov["covered"] + icov["partial"] + icov["out"] == 6
    cradar = ci.cobit_coverage_scores("es")
    assert len(cradar) == 8 and all(0 <= s <= 100 for _, s in cradar)
    iradar = ci.iso_coverage_scores("es")
    assert len(iradar) == 6 and all(0 <= s <= 100 for _, s in iradar)


def test_cobit_iso_translations_differ():
    from mvdg import cobit_iso as ci
    es = [o["name"] for o in ci.cobit_objectives("es")]
    en = [o["name"] for o in ci.cobit_objectives("en")]
    assert es != en
    es_p = [p["name"] for p in ci.iso_principles("es")]
    en_p = [p["name"] for p in ci.iso_principles("en")]
    assert es_p != en_p


# ------------------------------------------------------- MDM (duplicados + golden record)
def test_mdm_finds_real_duplicates_in_demo_customers():
    # el dataset de demo trae 8 colisiones reales de document_id/email, sin
    # inyectar nada a propósito para este test — validación end-to-end real.
    from mvdg import mdm
    from mvdg.demo_data import load_demo_tables
    df = load_demo_tables()["dim_customers"]
    rules = mdm.suggest_rules(df, ["document_id", "email", "full_name", "birth_date"])
    report = mdm.dedup_report(df, rules, min_confidence=0.5, block_column="country")
    assert len(report) == 8
    assert (report["confidence"] == 100.0).all()
    assert (report["rows"] == 2).all()


def test_mdm_avoids_false_positives_on_common_names():
    # 'Ana Costa' aparece 4 veces en la demo: personas distintas, mismo
    # nombre común. El nombre solo (sin ID/email coincidente) no debe
    # alcanzar el umbral de confianza.
    from mvdg import mdm
    from mvdg.demo_data import load_demo_tables
    df = load_demo_tables()["dim_customers"]
    ana = df[df["full_name"] == "Ana Costa"]
    assert len(ana) >= 3   # confirma que el caso de prueba existe en la demo
    rules = mdm.suggest_rules(df, ["document_id", "email", "full_name", "birth_date"])
    clusters = mdm.find_duplicate_clusters(df, rules, min_confidence=0.5, block_column="country")
    flagged_ids = {df.loc[i, "customer_id"] for c in clusters for i in c.row_indices}
    assert not (set(ana["customer_id"]) & flagged_ids)


def test_mdm_golden_record_fills_gaps_from_best_row():
    import pandas as pd
    from mvdg import mdm
    df = pd.DataFrame([
        {"id": 1, "name": "Juan Perez", "email": "juan@x.com", "phone": None},
        {"id": 1, "name": "Juan Perez", "email": None, "phone": "099123456"},
    ])
    cluster = mdm.DuplicateCluster(row_indices=[0, 1], confidence=1.0, matched_on=["id"])
    golden = mdm.build_golden_record(df, cluster)
    assert golden["email"] == "juan@x.com" and golden["phone"] == "099123456"


def test_mdm_blocking_required_for_large_unblocked_comparisons():
    import pandas as pd
    from mvdg import mdm
    df = pd.DataFrame({"name": [f"Person {i}" for i in range(200)]})
    rules = [mdm.MatchRule("name", weight=1.0, kind="fuzzy")]
    with pytest.raises(ValueError):
        mdm.find_duplicate_clusters(df, rules)   # sin block_column, 200 filas -> demasiados pares


def test_mdm_suggest_rules_classifies_by_column_name():
    import pandas as pd
    from mvdg import mdm
    df = pd.DataFrame({"document_id": ["1"], "full_name": ["x"], "amount": [1.0]})
    rules = {r.column: r for r in mdm.suggest_rules(df, ["document_id", "full_name", "amount"])}
    assert rules["document_id"].kind == "exact" and rules["document_id"].weight == 3.0
    assert rules["full_name"].kind == "fuzzy"
    assert rules["amount"].kind == "exact"   # numérico -> exacto, no fuzzy


# ------------------------------------------------- dataset de ejemplo real
def test_sample_dataset_profiles():
    from mvdg.profiler import profile_table, suggest_rules, summary
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "assets", "samples", "rotulado_de_alimentos_2026.csv")
    assert os.path.exists(path), "el dataset de ejemplo debe estar versionado"
    df = pd.read_csv(path)
    info = summary(df)
    assert info["rows"] == 284 and info["columns"] == 12
    assert info["duplicate_rows"] == 0
    prof = profile_table(df)
    assert len(prof) == 12
    # 'muestra' es clave (única) y 'articulos' tiene muchos nulos
    assert set(prof["column"]) >= {"producto", "marca", "muestra", "articulos"}
    # las sugerencias corren sin error en los 3 idiomas
    for lang in LANGS:
        assert isinstance(suggest_rules(df, lang), list)


# ------------------------------------- datasets de ejemplo, gobernados end-to-end
def test_samples_file_second_dataset_versioned():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "assets", "samples", "dirty_cafe_sales.csv")
    assert os.path.exists(path), "el segundo dataset de ejemplo debe estar versionado"
    df = pd.read_csv(path)
    assert len(df) == 10000 and len(df.columns) == 8


@pytest.mark.parametrize("lang", LANGS)
def test_samples_meta_complete(lang):
    from mvdg import samples
    for key in samples.sample_keys():
        m = samples.sample_meta(key, lang)
        for field in ("name", "domain", "description", "owner", "steward",
                     "classification", "refresh", "source", "license"):
            assert m[field], f"{key}.{field} vacío en {lang}"


@pytest.mark.parametrize("lang", LANGS)
def test_samples_quality_results_have_real_spread(lang):
    from mvdg import samples
    ral = samples.sample_quality_results("rotulado_alimentos", lang)
    assert len(ral) == 6
    assert set(ral["status"]) <= {"pass", "warn", "fail"}
    assert (ral["status"] == "warn").sum() >= 1  # marca "-" y vencimiento detectados

    caf = samples.sample_quality_results("cafe_sales_kaggle", lang)
    assert len(caf) == 7
    assert (caf["status"] == "fail").sum() >= 3  # Item/Payment Method/Location muy incompletos

    bnk = samples.sample_quality_results("bank_marketing_uci", lang)
    assert len(bnk) == 6
    assert (bnk["status"] == "fail").sum() == 1  # contact muy incompleto (29%)
    assert (bnk["status"] == "pass").sum() >= 3

    from mvdg.quality import overall_index
    assert overall_index(caf) < overall_index(bnk) < overall_index(ral)  # cafe_sales es la más sucia a propósito


def test_samples_bank_conditional_rule_is_not_a_false_positive():
    """poutcome='unknown' cuando previous=0 es un caso de negocio válido (el
    cliente nunca fue contactado antes), no un hueco de calidad — BNK-05 debe
    salir en pass, no marcarlo como falla."""
    from mvdg import samples
    res = samples.sample_quality_results("bank_marketing_uci", "es")
    bnk05 = res[res["rule_id"] == "BNK-05"].iloc[0]
    assert bnk05["status"] == "pass"
    assert bnk05["affected_rows"] == 0


def test_samples_bank_classification_note_present():
    from mvdg import samples
    for lang in LANGS:
        m = samples.sample_meta("bank_marketing_uci", lang)
        assert m["classification"] == "Confidencial"
        assert m["classification_note"]
    # los otros dos datasets no llevan nota (no hace falta aclarar nada)
    for key in ("rotulado_alimentos", "cafe_sales_kaggle"):
        assert samples.sample_meta(key, "es")["classification_note"] is None


def test_samples_openfda_file_versioned():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "assets", "samples", "medicamentos_openfda.csv")
    assert os.path.exists(path), "el dataset openFDA debe estar versionado"
    df = pd.read_csv(path)
    assert len(df) == 1546 and len(df.columns) == 15
    # 6 grupos multinacionales, muchas razones sociales (caso MDM real)
    assert df["labeler_name"].nunique() > 20


@pytest.mark.parametrize("lang", LANGS)
def test_samples_openfda_quality_real_defects(lang):
    """Los defectos del NDC Directory son reales (no inyectados): 4 NDC
    duplicados, huecos de marca/principio activo/clase farmacológica en
    productos de uso humano, y listados FDA sin fecha."""
    from mvdg import samples
    med = samples.sample_quality_results("medicamentos_openfda", lang)
    assert len(med) == 8
    by_id = med.set_index("rule_id")
    assert by_id.loc["MED-01", "affected_rows"] == 4       # NDC duplicados reales
    assert by_id.loc["MED-01", "status"] in ("warn", "fail")
    assert by_id.loc["MED-02", "status"] == "pass"          # formato NDC impecable
    assert by_id.loc["MED-07", "status"] == "pass"          # fechas YYYYMMDD válidas
    assert (med["status"] == "fail").sum() >= 3             # huecos reales del registro


def test_samples_openfda_conditional_rules_scope():
    """Las reglas condicionales solo evalúan medicamentos de uso humano:
    los graneles/semielaborados sin marca NO son falsos positivos."""
    from mvdg import samples
    med = samples.sample_quality_results("medicamentos_openfda", "es")
    by_id = med.set_index("rule_id")
    df = samples.load_sample_table("medicamentos_openfda")
    total_sin_marca = int(df["brand_name"].isna().sum())
    humanos_sin_marca = int(df[df["product_type"].isin(
        {"HUMAN PRESCRIPTION DRUG", "HUMAN OTC DRUG"})]["brand_name"].isna().sum())
    assert by_id.loc["MED-04", "affected_rows"] == humanos_sin_marca
    assert humanos_sin_marca < total_sin_marca  # la condición recorta de verdad


def test_curation_inventory_covers_all_definitions():
    """Toda definición del programa (glosario demo + samples, catálogo,
    diccionario) aparece en el inventario de curaduría, pre-establecida y en
    estado 'sugerido_ia' hasta que un responsable la revise."""
    from mvdg import curation
    for lang in LANGS:
        df = curation.list_items(lang)
        assert len(df) > 100
        assert set(df["kind"]) == {"glossary", "catalog", "column"}
        assert (df["proposed"].str.len() > 0).all()  # nada arranca en blanco


def test_curation_validate_modify_reset(tmp_path, monkeypatch):
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    from mvdg import curation
    item = "glossary:medicamentos_openfda:ndc"
    # validar tal cual
    rec = curation.save_validation(item, "es", "validado", "",
                                   "María Viera", "Data Owner Regulatorio")
    assert rec["status"] == "validado" and rec["date"]
    df = curation.list_items("es").set_index("item_id")
    assert df.loc[item, "status"] == "validado"
    assert df.loc[item, "responsible_name"] == "María Viera"
    assert df.loc[item, "text"] == df.loc[item, "proposed"]  # validar no cambia el texto
    # modificar con texto oficial
    curation.save_validation(item, "es", "modificado", "Definición oficial corregida.",
                             "J. Pérez", "Data Steward")
    df = curation.list_items("es").set_index("item_id")
    assert df.loc[item, "status"] == "modificado"
    assert df.loc[item, "text"] == "Definición oficial corregida."
    assert curation.effective_text(item, "es", "fallback") == "Definición oficial corregida."
    # el veredicto es por idioma: en inglés sigue sugerido_ia
    assert curation.list_items("en").set_index("item_id").loc[item, "status"] == "sugerido_ia"
    # resumen y reset
    s = curation.summary("es")
    assert s["modificado"] == 1 and s["reviewed_pct"] > 0
    assert curation.reset_item(item, "es")
    assert curation.get_record(item, "es") is None


def test_curation_requires_responsible_name(tmp_path, monkeypatch):
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    from mvdg import curation
    with pytest.raises(ValueError):
        curation.save_validation("glossary:demo:customer", "es", "validado",
                                 "", "", "Data Owner")
    with pytest.raises(ValueError):
        curation.save_validation("glossary:demo:customer", "es", "sugerido_ia",
                                 "", "Nombre", "Cargo")


def _org_fixture():
    return pd.DataFrame({
        "Departamento": ["Dirección General", "Gerencia Comercial", "Gerencia Comercial",
                         "Finanzas", "Calidad y Regulatorio", "Calidad y Regulatorio",
                         "Marketing", "TI / Datos"],
        "Nombre completo": ["Ana Torres", "Bruno Díaz", "Carla Gómez", "Diego Ruiz",
                            "Elena Sosa", "Fabián López", "Gina Méndez", "Hugo Pereira"],
        "Puesto": ["CEO", "Gerente Comercial", "Analista de Ventas", "Director de Finanzas",
                   "Directora de Calidad", "Analista Regulatorio", "Jefa de Marketing",
                   "Coordinador de BI"],
        "Jefe directo": ["", "Ana Torres", "Bruno Díaz", "Ana Torres", "Ana Torres",
                         "Elena Sosa", "Ana Torres", "Diego Ruiz"],
    })


def test_orgchart_header_detection_any_language_and_order():
    from mvdg import orgchart as oc
    org = oc.parse_org_table(_org_fixture())
    assert list(org.columns) == ["nombre", "cargo", "area", "reporta_a", "email"]
    assert len(org) == 8
    # encabezados en inglés también
    en = _org_fixture().rename(columns={"Departamento": "Department",
                                        "Nombre completo": "Name",
                                        "Puesto": "Job Title",
                                        "Jefe directo": "Reports To"})
    assert len(oc.parse_org_table(en)) == 8
    # sin columnas mínimas -> error claro, no un KeyError críptico
    with pytest.raises(ValueError):
        oc.parse_org_table(pd.DataFrame({"x": [1], "y": [2]}))


def test_orgchart_assignments_match_domain_and_seniority():
    """El owner sugerido es la persona de mayor jerarquía del área que
    matchea el dominio — y el orden de keywords es prioridad (para
    bank_marketing gana Marketing, no Comercial)."""
    from mvdg import orgchart as oc
    org = oc.parse_org_table(_org_fixture())
    asg = oc.suggest_assignments(org).set_index("dataset")
    assert asg.loc["fct_payments", "owner_name"] == "Diego Ruiz"        # Finanzas
    assert asg.loc["medicamentos_openfda", "owner_name"] == "Elena Sosa"  # Calidad/Regulatorio
    assert asg.loc["medicamentos_openfda", "steward_name"] == "Fabián López"
    assert asg.loc["bank_marketing_uci", "owner_name"] == "Gina Méndez"  # Marketing > Comercial
    assert (asg["estado"] == "sugerido").all()
    # todos los datasets del programa reciben responsable con nombre y cargo
    assert (asg["owner_name"].str.len() > 0).all()
    assert (asg["owner_role"].str.len() > 0).all()


def test_orgchart_persistence_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    from mvdg import orgchart as oc
    org = oc.parse_org_table(_org_fixture())
    oc.save_org(org)
    assert oc.load_org().equals(org)
    asg = oc.suggest_assignments(org)
    oc.save_assignments(asg)
    assert oc.load_assignments().equals(asg)


def test_orgchart_photo_ai_off_by_default(monkeypatch):
    for var in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY",
                "MVDG_AI_PROVIDER"):
        monkeypatch.delenv(var, raising=False)
    from mvdg.ai_provider import ai_parse_orgchart_image
    assert ai_parse_orgchart_image(b"fake-image-bytes") is None


def test_orgchart_photo_ai_parses_mocked_response(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    from mvdg import ai_provider as ap

    def fake_post(url, headers, body):
        assert "anthropic" in url
        # la imagen viaja en base64 dentro del body
        assert body["messages"][0]["content"][0]["type"] == "image"
        return {"content": [{"text": '{"personas": [{"nombre": "Ana Torres", '
                                     '"cargo": "CEO", "area": "Dirección", '
                                     '"reporta_a": ""}]}'}]}

    monkeypatch.setattr(ap, "_post_json", fake_post)
    people = ap.ai_parse_orgchart_image(b"png-bytes", "image/png", "es", "claude")
    assert people == [{"nombre": "Ana Torres", "cargo": "CEO",
                       "area": "Dirección", "reporta_a": "", "email": ""}]


def test_insights_governance_coverage(tmp_path, monkeypatch):
    """El índice de gobierno cubre los 8 datasets y sube cuando se asignan
    responsables con nombre (👥) y se curan definiciones (🖊️)."""
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    from mvdg import curation, insights, orgchart
    base = insights.governance_summary("es")
    assert base["datasets"] == 8
    assert base["classified_pct"] == 100.0 and base["rules_pct"] == 100.0
    assert 0 < base["governance_index"] < 100  # honesto: no arranca en 10/10
    # asignar responsables con nombre a todo -> owner/steward suben
    org = orgchart.parse_org_table(_org_fixture())
    orgchart.save_assignments(orgchart.suggest_assignments(org))
    # curar una definición -> curaduría sube
    curation.save_validation("glossary:medicamentos_openfda:ndc", "es",
                             "validado", "", "María Viera", "Data Owner")
    after = insights.governance_summary("es")
    assert after["owner_pct"] == 100.0 and after["steward_pct"] == 100.0
    assert after["curation_pct"] > base["curation_pct"]
    assert after["governance_index"] > base["governance_index"]


def test_insights_named_heuristic():
    from mvdg.insights import _named
    assert _named("María Viera") and _named("J. Pérez")
    assert not _named("Gerencia Comercial")
    assert not _named("Equipo de Datos de Ventas")
    assert not _named("")


def test_samples_openfda_bi_bundle_complete():
    """End-to-end hasta el BI: el paquete de gobierno del dataset openFDA trae
    datos + diccionario + calidad + glosario listos para exportar/servir."""
    from mvdg import samples
    gt = samples.sample_governance_tables("medicamentos_openfda", "es")
    for table in ("data", "dictionary", "quality_results", "glossary"):
        assert table in gt and len(gt[table]) > 0
    assert len(gt["dictionary"]) == 15   # las 15 columnas documentadas
    assert len(gt["glossary"]) == 9      # los 9 términos de negocio


# --------------------------------------- IA externa opcional (con fallback local)
def test_ai_provider_off_by_default(monkeypatch):
    from mvdg import ai_provider as ap
    for var in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "MVDG_AI_PROVIDER"):
        monkeypatch.delenv(var, raising=False)
    assert ap.configured_provider() is None
    assert ap.ai_suggest_fix("ds", "col", "completeness", "desc", 5, "es") is None


def test_ai_provider_priority_and_override(monkeypatch):
    from mvdg import ai_provider as ap
    for var in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "MVDG_AI_PROVIDER"):
        monkeypatch.delenv(var, raising=False)

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    assert ap.configured_provider() == "openai"

    # claude tiene prioridad si ambas keys estan presentes
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    assert ap.configured_provider() == "claude"

    # MVDG_AI_PROVIDER fuerza uno especifico, si tiene su key
    monkeypatch.setenv("MVDG_AI_PROVIDER", "openai")
    assert ap.configured_provider() == "openai"

    # forzar un proveedor sin key cargada no debe romper: cae al de prioridad
    monkeypatch.setenv("MVDG_AI_PROVIDER", "gemini")
    assert ap.configured_provider() == "claude"


def test_ai_provider_network_errors_fall_back_to_none(monkeypatch):
    """Cualquier falla de red/timeout/HTTP nunca debe romper la app: siempre
    devuelve None y el llamador cae a la sugerencia local."""
    import urllib.error
    from mvdg import ai_provider as ap
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")

    monkeypatch.setitem(ap._CALLERS, "claude",
                        lambda prompt, key, model: (_ for _ in ()).throw(urllib.error.URLError("offline")))
    assert ap.ai_suggest_fix("ds", "col", "completeness", "desc", 5, "es") is None

    monkeypatch.setitem(ap._CALLERS, "claude",
                        lambda prompt, key, model: (_ for _ in ()).throw(
                            urllib.error.HTTPError("url", 401, "unauthorized", {}, None)))
    assert ap.ai_suggest_fix("ds", "col", "completeness", "desc", 5, "es") is None


def test_ai_provider_malformed_responses_fall_back_to_none(monkeypatch):
    from mvdg import ai_provider as ap
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")

    monkeypatch.setitem(ap._CALLERS, "claude", lambda prompt, key, model: "not json at all")
    assert ap.ai_suggest_fix("ds", "col", "completeness", "desc", 5, "es") is None

    import json
    monkeypatch.setitem(ap._CALLERS, "claude",
                        lambda prompt, key, model: json.dumps({"root_cause": "x"}))  # faltan claves
    assert ap.ai_suggest_fix("ds", "col", "completeness", "desc", 5, "es") is None


def test_ai_provider_successful_response_parsed(monkeypatch):
    import json
    from mvdg import ai_provider as ap
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")

    fake = {"root_cause": "causa", "short_term": "corto", "long_term": "largo", "owner": "equipo"}
    monkeypatch.setitem(ap._CALLERS, "claude",
                        lambda prompt, key, model: "aquí tenés:\n```json\n" + json.dumps(fake) + "\n```")
    result = ap.ai_suggest_fix("cafe_sales_kaggle", "Payment Method", "completeness",
                               "Payment Method completo", 3178, "es")
    assert result == fake


def test_ai_provider_prompt_never_includes_raw_data():
    """El prompt manda solo metadato de la falla (nombres/numeros), nunca
    puede referenciar una fila de datos real porque la funcion no la recibe."""
    from mvdg import ai_provider as ap
    prompt = ap._build_prompt("cafe_sales_kaggle", "Payment Method", "completeness",
                              "Payment Method completo", 3178, "es")
    assert "cafe_sales_kaggle" in prompt and "Payment Method" in prompt and "3178" in prompt
    assert "root_cause" in prompt  # pide el JSON con esas claves


def test_ai_provider_label_and_copilot_not_offered():
    from mvdg import ai_provider as ap
    assert ap.provider_label("claude") == "Claude (Anthropic)"
    assert ap.provider_label("openai") == "ChatGPT (OpenAI)"
    assert ap.provider_label("gemini") == "Gemini (Google)"
    assert "copilot" not in ap._PROVIDERS


def test_samples_accuracy_rule_is_meaningful():
    """La regla de exactitud (total = cantidad × precio) no es un no-op: si
    se corrompe Total Spent, el score debe bajar."""
    from mvdg import samples
    df = samples.load_sample_table("cafe_sales_kaggle").copy()
    rule = next(r for r in samples.SAMPLES["cafe_sales_kaggle"]["rules"] if r.rule_id == "CAF-07")
    score_before, _ = rule.check(df)
    df.loc[df.index[:500], "Total Spent"] = "999999.0"
    score_after, affected_after = rule.check(df)
    assert score_after < score_before
    assert affected_after > 0


def test_samples_dictionary_and_glossary_link_columns():
    from mvdg import samples
    for key in samples.sample_keys():
        dic = samples.sample_dictionary_df(key, "es")
        df = samples.load_sample_table(key)
        assert set(dic["column"]) == set(df.columns)
        gloss = samples.sample_glossary_df(key, "es")
        assert len(gloss) >= 3
        assert all(key in ds for ds in gloss["linked_datasets"])


def test_samples_governance_tables_bundle():
    from mvdg import samples
    for key in samples.sample_keys():
        gov = samples.sample_governance_tables(key, "es")
        assert set(gov) == {"data", "dictionary", "quality_results", "glossary"}
        assert len(gov["data"]) > 0


def test_samples_exportable_with_generic_exporters():
    """Los datasets de ejemplo deben poder exportarse con los mismos
    exportadores genéricos que usa el resto de la plataforma (BI real)."""
    from mvdg import samples
    from mvdg.exporters import to_csv_bytes, to_excel_bytes, to_json_bytes
    df = samples.load_sample_table("rotulado_alimentos")
    assert to_csv_bytes(df).startswith(b"\xef\xbb\xbf") or len(to_csv_bytes(df)) > 0
    assert to_excel_bytes(df)[:2] == b"PK"
    assert len(to_json_bytes(df)) > 0


def test_bi_api_serves_sample_datasets():
    from fastapi.testclient import TestClient
    from bi_api.main import app
    client = TestClient(app)

    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert set(body["samples"]) == {"rotulado_alimentos", "cafe_sales_kaggle",
                                    "bank_marketing_uci", "medicamentos_openfda"}

    r = client.get("/api/samples/cafe_sales_kaggle?lang=en")
    assert r.status_code == 200
    assert r.json()["owner"] == "Operations / Point of Sale"

    r = client.get("/api/samples/cafe_sales_kaggle/quality_results?lang=es&format=csv")
    assert r.status_code == 200
    assert "rule_id" in r.text

    r = client.get("/api/samples/rotulado_alimentos/data?format=json")
    assert r.status_code == 200 and r.json()["rows"] == 284

    assert client.get("/api/samples/no-existe/data").status_code == 404
    assert client.get("/api/samples/cafe_sales_kaggle/no-existe").status_code == 404


# ------------------------------------------- sugerencias de correccion (IA)
@pytest.mark.parametrize("lang", LANGS)
def test_remediation_covers_all_demo_rules(lang):
    from mvdg.quality import RULES
    from mvdg.remediation import REMEDIATIONS, suggest_fix
    # las 17 reglas de demo tienen contenido especifico, no generico
    assert {r.rule_id for r in RULES} <= set(REMEDIATIONS)
    for r in RULES:
        fix = suggest_fix(r.rule_id, r.dimension, r.column, 123, lang)
        for field in ("root_cause", "short_term", "long_term", "owner"):
            assert fix[field], f"{r.rule_id}.{field} vacio en {lang}"
        # el numero de filas afectadas aparece formateado en el texto
        assert "123" in fix["short_term"] or "123" in fix["root_cause"]


@pytest.mark.parametrize("lang", LANGS)
def test_remediation_covers_all_sample_rules(lang):
    from mvdg import samples
    from mvdg.remediation import REMEDIATIONS, suggest_fix
    for key in samples.sample_keys():
        for r in samples.SAMPLES[key]["rules"]:
            assert r.rule_id in REMEDIATIONS
            fix = suggest_fix(r.rule_id, r.dimension, r.column, 9, lang)
            assert all(fix.values())


def test_remediation_generic_fallback_for_unknown_rule():
    from mvdg.quality import DIMENSIONS
    from mvdg.remediation import suggest_fix
    for dim in DIMENSIONS:
        for lang in LANGS:
            fix = suggest_fix("NEW-01", dim, "alguna_columna", 4, lang)
            assert all(fix.values())
            assert "alguna_columna" in fix["short_term"] or "alguna_columna" in fix["root_cause"]


def test_remediation_thousands_separator():
    from mvdg.remediation import suggest_fix
    fix = suggest_fix("CAF-03", "completeness", "Payment Method", 3178, "es")
    assert "3,178" in fix["short_term"]


def test_render_fixes_shown_next_to_failures_in_app(monkeypatch):
    """Las reglas en warn/fail del dataset de ejemplo mas sucio deben tener
    una sugerencia de la IA disponible; las que pasan, no hace falta."""
    from mvdg import samples
    from mvdg.remediation import suggest_fix
    res = samples.sample_quality_results("cafe_sales_kaggle", "es")
    broken = res[res["status"] != "pass"]
    assert len(broken) == 5  # 3 fail + 2 warn, ver test_samples_quality_results_have_real_spread
    for _, row in broken.iterrows():
        fix = suggest_fix(row["rule_id"], row["dimension"], row["column"],
                          int(row["affected_rows"]), "es")
        assert all(fix.values())


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
    from bi_api.main import TABLES, app
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


# ------------------------------------------------------------- Power BI meta
def _make_pbip(root):
    """Escribe un proyecto .pbip mínimo (TMDL, sin cache.abf) bajo ``root``."""
    sm = root / "VentasDemo.SemanticModel"
    dfn = sm / "definition"
    (dfn / "tables").mkdir(parents=True)
    (dfn / "roles").mkdir(parents=True)
    (root / "VentasDemo.Report").mkdir(parents=True)
    (sm / ".platform").write_text(
        '{ "metadata": { "type": "SemanticModel", "displayName": "VentasDemo" } }',
        encoding="utf-8")
    # DAX multi-línea + medidas simples + columna calculada + PII
    ventas = (
        "table Ventas\n"
        "\tmeasure 'Total Ventas' =\n"
        "\t\t\tSUMX (\n"
        "\t\t\t\tVentas,\n"
        "\t\t\t\tVentas[Cantidad] * Ventas[PrecioUnitario]\n"
        "\t\t\t)\n"
        "\t\tdisplayFolder: Metricas\n"
        "\t\tdescription: Suma de cantidad por precio\n"
        "\tmeasure Margen = [Total Ventas] - [Total Costo]\n"
        "\tcolumn Cantidad\n"
        "\t\tdataType: int64\n"
        "\t\tsourceColumn: Cantidad\n"
        "\tcolumn Email\n"
        "\t\tdataType: string\n"
        "\t\tsourceColumn: email\n"
        "\tcolumn MargenPct\n"
        "\t\tdataType: double\n"
        "\t\texpression = DIVIDE ( [Margen], [Total Ventas] )\n"
        "\tpartition Ventas = m\n"
        "\t\tmode: import\n"
        "\t\tsource =\n"
        "\t\t\t\tlet\n"
        "\t\t\t\t\tSource = Sql.Database(\"MyServer\", \"MyDB\"),\n"
        "\t\t\t\t\tVentas1 = Source{[Schema=\"dbo\",Item=\"Ventas\"]}[Data]\n"
        "\t\t\t\tin\n"
        "\t\t\t\t\tVentas1\n"
    )
    (dfn / "tables" / "Ventas.tmdl").write_text(ventas, encoding="utf-8")
    rels = (
        "relationship aaaa-1111\n"
        "\tfromColumn: Ventas.ClienteKey\n"
        "\ttoColumn: Cliente.ClienteKey\n\n"
        "relationship bbbb-2222\n"
        "\tcrossFilteringBehavior: bothDirections\n"
        "\tfromColumn: Ventas.FechaKey\n"
        "\ttoColumn: Calendario.FechaKey\n"
    )
    (dfn / "relationships.tmdl").write_text(rels, encoding="utf-8")
    (dfn / "roles" / "Vendedor.tmdl").write_text(
        'role Vendedor\n\ttablePermission Ventas = Ventas[Region] = "Sur"\n',
        encoding="utf-8")
    return str(sm)


def test_powerbi_pbip_parse(tmp_path):
    from mvdg import powerbi_meta as pbi
    model = pbi.read_pbip(_make_pbip(tmp_path))
    assert model.name == "VentasDemo"
    assert "Ventas" in model.tables
    names = {m.name for m in model.measures}
    assert {"Total Ventas", "Margen"} <= names
    total = next(m for m in model.measures if m.name == "Total Ventas")
    assert "\n" not in total.dax and "SUMX" in total.dax   # DAX multi-línea colapsado
    assert total.description and total.display_folder == "Metricas"
    assert any(r.both_directions for r in model.relationships)   # relación bidireccional
    assert model.roles == ["Vendedor"]                            # RLS detectado
    assert "VentasDemo" in model.reports
    calc = next(c for c in model.columns if c.name == "MargenPct")
    assert calc.is_calculated and "DIVIDE" in calc.dax
    dic = pbi.to_dictionary(model)
    assert bool(dic.loc[dic["column"] == "Email", "pii"].iloc[0])  # PII


def test_powerbi_sql_source_wired_into_lineage(tmp_path):
    # cadena completa: SQL Server -> tabla -> dataset (modelo) -> reporte
    from mvdg import powerbi_meta as pbi
    out = pbi.ingest_pbip(_make_pbip(tmp_path))
    model = out["_model"]
    assert model.table_sources.get("Ventas") == "SQL Server · MyServer/MyDB"

    srcs = out["sources"]
    assert set(srcs.columns) == {"table", "source"}
    assert srcs.loc[srcs["table"] == "Ventas", "source"].iloc[0] == "SQL Server · MyServer/MyDB"

    lin = out["lineage"]
    sql_row = lin[(lin["source"] == "SQL Server · MyServer/MyDB") & (lin["source_layer"] == "source")]
    assert len(sql_row) == 1
    assert sql_row.iloc[0]["target"] == "Ventas" and sql_row.iloc[0]["target_layer"] == "curated"
    # la cadena sigue: tabla -> modelo -> reporte, sin cortarse
    assert ((lin["source"] == "Ventas") & (lin["target"] == model.name)).any()
    assert ((lin["source"] == model.name) & (lin["source_layer"] == "mart")).any()


def test_powerbi_tmdl_doc_comment_and_metadata_traits():
    # regresión: encontrado escaneando un proyecto .pbip real de GitHub —
    # sourceLineageTag/dataCategory se colaban en el texto del DAX, y las
    # descripciones nativas "/// ..." de TMDL no se capturaban.
    from mvdg.powerbi_meta import _parse_table_tmdl
    tmdl = (
        "table Targets\n"
        "\tlineageTag: 5c67d908-0588-43c0-9dbc-1c64794f92c8\n"
        "\tsourceLineageTag: fc05aa02-32da-45a3-a497-78e97999d244\n"
        "\n"
        "\t/// Total sales goal for the current filter context.\n"
        "\tmeasure Target = SUM(Targets[TargetAmount])\n"
        "\t\tformatString: \\$#,0;(\\$#,0);\\$#,0\n"
        "\t\tlineageTag: 35b9a71b-304f-4f4f-9f7f-cc49da4a2c84\n"
        "\t\tsourceLineageTag: ffc79c2c-8c37-499d-919a-2a3511102514\n"
        "\t\tdataCategory: Uncategorized\n"
        "\n"
        "\tmeasure Undocumented = SUM(Targets[X])\n"
    )
    _, _, measures, _ = _parse_table_tmdl(tmdl)
    target = next(m for m in measures if m.name == "Target")
    assert target.dax == "SUM(Targets[TargetAmount])"   # sin metadatos colados
    assert target.description == "Total sales goal for the current filter context."
    other = next(m for m in measures if m.name == "Undocumented")
    assert other.description == ""   # sin "///" antes -> sin descripción, no arrastra la anterior


def test_powerbi_source_label_heuristics():
    from mvdg.powerbi_meta import _source_label_from_mquery
    assert _source_label_from_mquery('Source = Sql.Database("Srv", "Db")') == "SQL Server · Srv/Db"
    assert _source_label_from_mquery('Source = Sql.Databases("Srv")') == "SQL Server · Srv"
    assert _source_label_from_mquery('Value.NativeQuery(Source, "SELECT 1")') == \
        "SQL (consulta nativa · Value.NativeQuery)"
    assert _source_label_from_mquery('Source = Excel.Workbook(File.Contents("x.xlsx"))') == "Power Query · Excel.Workbook"
    assert _source_label_from_mquery('no hay ninguna funcion m aca') is None


# --------------------------------------------------- Power BI tenant (Scanner API)
def test_powerbi_tenant_off_by_default(monkeypatch):
    from mvdg import powerbi_meta as pbi
    for var in ("POWERBI_TENANT_ID", "POWERBI_CLIENT_ID", "POWERBI_CLIENT_SECRET"):
        monkeypatch.delenv(var, raising=False)
    assert pbi.tenant_configured() is False
    with pytest.raises(RuntimeError):
        pbi.read_scanner()


def _scanner_result_json():
    return {
        "workspaces": [{
            "name": "Ventas LATAM",
            "datasets": [{
                "id": "ds-1", "name": "VentasDemo",
                "tables": [{
                    "name": "Ventas",
                    "columns": [{"name": "Monto", "dataType": "double"}],
                    "measures": [{"name": "Total", "expression": "SUM ( Ventas[Monto] )",
                                 "description": "Suma de ventas"}],
                    "source": [{"expression": 'Source = Sql.Database("Srv", "Db")'}],
                }],
                "relationships": [{"fromTable": "Ventas", "fromColumn": "ClienteKey",
                                   "toTable": "Cliente", "toColumn": "ClienteKey",
                                   "crossFilteringBehavior": "BothDirections"}],
                "roles": [{"name": "Vendedor"}],
            }],
            "reports": [{"name": "Dashboard Ventas", "datasetId": "ds-1"}],
        }],
    }


def test_powerbi_list_workspace_ids_paginates_past_5000(monkeypatch):
    # un tenant multinacional puede tener más workspaces que el tope de una
    # sola página ($top) — hay que seguir pidiendo con $skip hasta agotarlos.
    from mvdg import powerbi_meta as pbi

    pages = {
        0: [{"id": f"ws-{i}", "name": f"W{i}"} for i in range(3)],   # top=3, página llena
        3: [{"id": "ws-3", "name": "W3"}],                            # última página, incompleta
    }

    def fake_http_json(url, headers, method="GET", body=None):
        assert "admin/groups" in url
        skip = int(url.split("$skip=")[1].split("&")[0])
        return {"value": pages.get(skip, [])}

    monkeypatch.setattr(pbi, "_http_json", fake_http_json)
    result = pbi.list_workspace_ids("tok", top=3)
    assert [w["id"] for w in result] == ["ws-0", "ws-1", "ws-2", "ws-3"]


def test_powerbi_tenant_scan_mocked_end_to_end(monkeypatch):
    from mvdg import powerbi_meta as pbi

    calls = {"token": 0, "groups": 0, "getinfo": 0, "status": 0, "result": 0}

    def fake_http_form(url, form):
        calls["token"] += 1
        assert "login.microsoftonline.com" in url
        assert form["client_id"] == "cid"
        return {"access_token": "tok-123"}

    def fake_http_json(url, headers, method="GET", body=None):
        assert headers["Authorization"] == "Bearer tok-123" or "Authorization" not in headers
        if "admin/groups" in url:
            calls["groups"] += 1
            return {"value": [{"id": "ws-1", "name": "Ventas LATAM"}]}
        if url.endswith("/getInfo") or "getInfo?" in url:
            calls["getinfo"] += 1
            assert body == {"workspaces": ["ws-1"]}
            return {"id": "scan-1"}
        if "/scanStatus/" in url:
            calls["status"] += 1
            return {"status": "Succeeded"}
        if "/scanResult/" in url:
            calls["result"] += 1
            return _scanner_result_json()
        raise AssertionError(f"unexpected URL: {url}")

    monkeypatch.setattr(pbi, "_http_form", fake_http_form)
    monkeypatch.setattr(pbi, "_http_json", fake_http_json)

    models = pbi.read_scanner(tenant_id="tid", client_id="cid", client_secret="sec")
    assert calls == {"token": 1, "groups": 1, "getinfo": 1, "status": 1, "result": 1}
    assert len(models) == 1
    m = models[0]
    assert m.name == "VentasDemo" and m.workspace == "Ventas LATAM"
    assert m.table_sources.get("Ventas") == "SQL Server · Srv/Db"
    assert any(r.both_directions for r in m.relationships)
    assert m.roles == ["Vendedor"]
    assert m.reports == ["Dashboard Ventas"]   # linkeado por datasetId

    out = pbi.ingest_tenant(tenant_id="tid", client_id="cid", client_secret="sec")
    assert len(out["catalog"]) == 1
    assert "Ventas LATAM" in out["catalog"].iloc[0]["domain"]
    lin = out["lineage"]
    assert (lin["source_layer"] == "source").any() and (lin["target_layer"] == "bi").any()


def test_powerbi_tenant_missing_credentials_raises(monkeypatch):
    from mvdg import powerbi_meta as pbi
    for var in ("POWERBI_TENANT_ID", "POWERBI_CLIENT_ID", "POWERBI_CLIENT_SECRET"):
        monkeypatch.delenv(var, raising=False)
    with pytest.raises(RuntimeError):
        pbi.read_scanner(tenant_id="only-this-one")


def test_powerbi_bundled_example_is_real_and_parses(tmp_path):
    # el .pbip real incluido con el programa (GitHub, MIT) debe seguir
    # parseando limpio — este mismo archivo encontró 2 bugs reales del
    # parser (ver test_powerbi_tmdl_doc_comment_and_metadata_traits).
    from mvdg import powerbi_meta as pbi
    out = pbi.ingest_example()
    model = out["_model"]
    assert model.name == "Adventure Works Demo"
    assert len(model.tables) == 10 and len(model.measures) == 17
    assert all(m.description for m in model.measures)   # /// se capturan bien
    assert "Sales" in model.tables and "Targets" in model.tables


def test_powerbi_example_tenant_is_illustrative_not_a_real_scan():
    from mvdg import powerbi_meta as pbi
    out = pbi.ingest_example_tenant()
    models = out["_models"]
    assert len(models) == 4   # 4 workspaces simulados
    workspaces = {m.workspace for m in models}
    assert len(workspaces) == 4   # cada uno con nombre distinto
    # todos comparten el contenido real (mismas tablas/medidas), solo cambia
    # el workspace/reporte simulado
    assert {m.name for m in models} == {"Adventure Works Demo"}
    assert all(len(m.tables) == 10 for m in models)
    # tiene que quedar explícitamente marcado como ilustrativo, no un scan real
    assert all("ilustrativo" in m.source.lower() for m in models)
    assert (out["catalog"]["source"].str.contains("ilustrativo", case=False)).all()


# ---------------------------------------------------------- Tableau (Metadata API)
def test_tableau_off_by_default(monkeypatch):
    from mvdg import tableau_meta as tab
    for var in ("TABLEAU_SERVER_URL", "TABLEAU_TOKEN_NAME", "TABLEAU_TOKEN_SECRET"):
        monkeypatch.delenv(var, raising=False)
    assert tab.configured() is False
    with pytest.raises(RuntimeError):
        tab.read_site()


def _tableau_graphql_response():
    return {"data": {"workbooks": [{
        "name": "Ventas Regional", "projectName": "Comercial",
        "upstreamDatasources": [{
            "name": "DS Ventas",
            "fields": [
                {"name": "Monto", "description": "", "formula": None},
                {"name": "Margen %", "description": "Margen sobre ventas",
                 "formula": "SUM([Margen]) / SUM([Monto])"},
                {"name": "Margen % dup", "description": "",
                 "formula": "SUM([Margen]) / SUM([Monto])"},
            ],
            "upstreamTables": [{"name": "ventas", "schema": "dbo",
                               "database": {"name": "Db", "connectionType": "sqlserver"}}],
        }],
    }]}}


def test_tableau_site_scan_mocked_end_to_end(monkeypatch):
    from mvdg import tableau_meta as tab

    calls = {"signin": 0, "graphql": 0, "signout": 0}

    def fake_http_json(url, headers, method="GET", body=None):
        if url.endswith("/auth/signin"):
            calls["signin"] += 1
            assert body["credentials"]["personalAccessTokenName"] == "mv-token"
            return {"credentials": {"token": "sess-abc", "site": {"id": "site-1"}}}
        if url.endswith("/auth/signout"):
            calls["signout"] += 1
            return {}
        if url.endswith("/api/metadata/graphql"):
            calls["graphql"] += 1
            assert headers["X-Tableau-Auth"] == "sess-abc"
            return _tableau_graphql_response()
        raise AssertionError(f"unexpected URL: {url}")

    monkeypatch.setattr(tab, "_http_json", fake_http_json)

    model = tab.read_site(server="https://tableau.example.com",
                          token_name="mv-token", token_secret="secret")
    assert calls == {"signin": 1, "graphql": 1, "signout": 1}
    assert model.workbooks == ["Ventas Regional"]
    assert [d.name for d in model.datasources] == ["DS Ventas"]
    assert model.datasources[0].upstream_tables == ["dbo.ventas (sqlserver)"]
    calc_names = {fl.name for fl in model.fields if fl.is_calculated}
    assert calc_names == {"Margen %", "Margen % dup"}   # duplicated formula, detected by TAB-02

    out = tab.ingest_site(server="https://tableau.example.com",
                          token_name="mv-token", token_secret="secret")
    assert len(out["catalog"]) == 1
    assert len(out["glossary"]) == 2   # 2 calculated fields = 2 glossary terms
    q = out["quality"]
    dupe_rule = q[q["rule_id"] == "TAB-02"].iloc[0]
    assert dupe_rule["affected_rows"] == 1 and dupe_rule["status"] != "pass"
    lin = out["lineage"]
    assert (lin["source_layer"] == "source").any() and (lin["target_layer"] == "bi").any()


def test_tableau_signout_failure_does_not_break_scan(monkeypatch):
    from mvdg import tableau_meta as tab

    def fake_http_json(url, headers, method="GET", body=None):
        if url.endswith("/auth/signin"):
            return {"credentials": {"token": "sess-abc", "site": {"id": "site-1"}}}
        if url.endswith("/auth/signout"):
            raise OSError("network blip on signout")
        if url.endswith("/api/metadata/graphql"):
            return _tableau_graphql_response()
        raise AssertionError(f"unexpected URL: {url}")

    monkeypatch.setattr(tab, "_http_json", fake_http_json)
    model = tab.read_site(server="https://tableau.example.com",
                          token_name="mv-token", token_secret="secret")
    assert model.workbooks == ["Ventas Regional"]   # el fallo del sign-out no rompe el escaneo


def _make_twb(root, name="Demo.twb"):
    xml = (
        "<?xml version='1.0' encoding='utf-8' ?>\n"
        "<workbook version='18.1'>\n"
        "  <datasources>\n"
        "    <datasource caption='Ventas' name='sqlserver.x'>\n"
        "      <connection class='sqlserver' server='Srv' dbname='Db'>\n"
        "        <relation name='Ventas' table='[dbo].[Ventas]' type='table' />\n"
        "      </connection>\n"
        "      <column caption='Monto' datatype='real' name='[Monto]' role='measure' />\n"
        "      <column caption='Margen %' datatype='real' name='[Calc1]' role='measure'>\n"
        "        <calculation class='tableau' formula='SUM([Margen])/SUM([Monto])' />\n"
        "      </column>\n"
        "    </datasource>\n"
        "  </datasources>\n"
        "  <dashboards><dashboard name='Panel'><zones/></dashboard></dashboards>\n"
        "</workbook>\n"
    )
    p = root / name
    p.write_text(xml, encoding="utf-8")
    return str(p)


def test_tableau_read_twb_offline(tmp_path):
    from mvdg import tableau_meta as tabl
    path = _make_twb(tmp_path)
    model = tabl.read_twb(path)
    assert model.workbooks == ["Demo"]
    assert [d.name for d in model.datasources] == ["Ventas"]
    assert model.datasources[0].upstream_tables == ["sqlserver · Srv/Db"]
    calc = next(f for f in model.fields if f.is_calculated)
    assert calc.name == "Margen %" and calc.formula == "SUM([Margen])/SUM([Monto])"

    out = tabl.ingest_twb(path)
    assert len(out["catalog"]) == 1
    lin = out["lineage"]
    assert (lin["source_layer"] == "source").any() and (lin["target_layer"] == "bi").any()


def test_tableau_read_twbx_zip_wrapper(tmp_path):
    import zipfile
    from mvdg import tableau_meta as tabl
    twb_path = _make_twb(tmp_path, "Inner.twb")
    twbx_path = str(tmp_path / "Demo.twbx")
    with zipfile.ZipFile(twbx_path, "w") as zf:
        zf.write(twb_path, "Inner.twb")
    model = tabl.read_twb(twbx_path)
    assert [d.name for d in model.datasources] == ["Ventas"]   # se desempaqueta el .twb interno


def test_tableau_read_twb_missing_file_raises(tmp_path):
    from mvdg import tableau_meta as tabl
    with pytest.raises(FileNotFoundError):
        tabl.read_twb(str(tmp_path / "no_existe.twb"))


def test_tableau_bundled_example_parses():
    from mvdg import tableau_meta as tabl
    out = tabl.ingest_example()
    model = out["_model"]
    assert model.workbooks == ["VentasGlobalDemo"]
    assert {d.name for d in model.datasources} == {"Ventas Global", "Metas Regionales"}
    calc_names = {f.name for f in model.fields if f.is_calculated}
    assert calc_names == {"Margen %", "Ticket Promedio", "Segmento de Cuenta"}
    assert len(out["glossary"]) == 3
    lin = out["lineage"]
    assert (lin["source_layer"] == "source").any() and (lin["target_layer"] == "bi").any()


def test_powerbi_normalizers_match_mvdg_schema(tmp_path):
    from mvdg import powerbi_meta as pbi
    from mvdg.glossary import glossary_df
    from mvdg.lineage import lineage_df
    from mvdg.quality import DIMENSIONS, run_rules
    out = pbi.ingest_pbip(_make_pbip(tmp_path))
    # columnas idénticas a las tablas nativas del motor de gobierno
    assert set(out["glossary"].columns) == set(glossary_df().columns)
    assert set(out["lineage"].columns) == set(lineage_df().columns)
    assert set(out["quality"].columns) == set(run_rules().columns)
    # las dimensiones de salud de modelo caen dentro de las 6 DAMA
    assert set(out["quality"]["dimension"]) <= set(DIMENSIONS)
    # el catálogo reporta 0 filas: es metadata, no datos
    assert (out["catalog"]["rows"] == 0).all()


def test_powerbi_lineage_dynamic_figure(tmp_path):
    from mvdg import powerbi_meta as pbi
    from mvdg.lineage import downstream, graph_from_lineage, lineage_figure, upstream
    out = pbi.ingest_pbip(_make_pbip(tmp_path))
    nodes, edges = graph_from_lineage(out["lineage"])
    assert nodes and edges
    fig = lineage_figure(nodes=nodes, edges=edges)     # no debe romper con grafo dinámico
    assert fig is not None and len(fig.data) > 0
    model_id = f"model_{out['_model'].name}"
    assert downstream(f"tbl_Ventas", edges) & {model_id}   # tabla → modelo
    assert upstream(model_id, edges)                        # el modelo tiene ancestros


def test_lineage_demo_still_works():
    # el grafo de demo (sin args) sigue funcionando igual que antes
    from mvdg.lineage import EDGES, lineage_figure, upstream
    fig = lineage_figure()
    assert fig is not None and len(fig.data) > 0
    assert upstream("mart_sales")  # ancestros del mart de demo


def test_ai_dax_refactor_offline(monkeypatch):
    from mvdg.ai_provider import _build_dax_prompt, ai_refactor_dax
    for var in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "MVDG_AI_PROVIDER"):
        monkeypatch.delenv(var, raising=False)
    # sin key configurada, nunca llama afuera: devuelve None
    assert ai_refactor_dax("Total Ventas", "SUMX ( Ventas, 1 )", "Ventas", "es") is None
    # DAX vacío también da None
    assert ai_refactor_dax("X", "", "T", "es") is None
    # el prompt se arma en los 3 idiomas e incluye la medida y el DAX
    for lg in LANGS:
        p = _build_dax_prompt("Total Ventas", "SUMX ( Ventas, 1 )", "Ventas", lg)
        assert "Total Ventas" in p and "SUMX" in p


def test_ai_tableau_calc_refactor_offline(monkeypatch):
    from mvdg.ai_provider import _build_calc_prompt, ai_refactor_calc
    for var in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "MVDG_AI_PROVIDER"):
        monkeypatch.delenv(var, raising=False)
    # sin key configurada, nunca llama afuera: devuelve None
    assert ai_refactor_calc("Margen %", "SUM([Margen])/SUM([Monto])", "DS Ventas", "es") is None
    # fórmula vacía también da None
    assert ai_refactor_calc("X", "", "DS", "es") is None
    # el prompt se arma en los 3 idiomas e incluye el campo y la fórmula
    for lg in LANGS:
        p = _build_calc_prompt("Margen %", "SUM([Margen])/SUM([Monto])", "DS Ventas", lg)
        assert "Margen %" in p and "SUM([Margen])" in p
