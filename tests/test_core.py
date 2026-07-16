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


def test_vercel_deploy_does_not_ignore_api_functions():
    """Regresión: .vercelignore excluía la carpeta api/ (arrastrado de antes
    de que existieran las funciones serverless de MercadoPago ahí adentro),
    lo que hacía que Vercel nunca subiera checkout.js/verify-payment.js y el
    checkout devolviera 404 en producción. api/ tiene que seguir publicada."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    vercelignore = os.path.join(root, ".vercelignore")
    assert os.path.exists(vercelignore)
    with open(vercelignore, encoding="utf-8") as fh:
        lines = {ln.strip() for ln in fh if ln.strip()}
    assert "api" not in lines, (
        "api/ no puede estar en .vercelignore: ahí viven las funciones "
        "serverless de MercadoPago (checkout.js, verify-payment.js) que "
        "sirven /api/checkout y /api/verify-payment en producción.")
    for fname in ("checkout.js", "verify-payment.js", "_license.js"):
        assert os.path.exists(os.path.join(root, "api", fname)), fname


def _repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_vercel_rewrites_serve_all_landing_files():
    """Regresión: vercel.json solo re-escribía /, /mv_icon.png y /video/* hacia
    landing/ — todo lo demás que la página referencia con rutas relativas
    (descargas.html, img/*.jpg, payments-config.js, guia/pago/reviews, el ZIP
    de la demo) devolvía 404 en producción: botones de compra sin config,
    capturas rotas y 'Descargar demo' muerto. Tiene que existir el rewrite
    catch-all hacia /landing/."""
    import json as _json
    with open(os.path.join(_repo_root(), "vercel.json"), encoding="utf-8") as fh:
        cfg = _json.load(fh)
    sources = {r["source"]: r["destination"] for r in cfg.get("rewrites", [])}
    assert sources.get("/") == "/landing/index.html"
    assert sources.get("/:path*") == "/landing/:path*", (
        "falta el rewrite catch-all /:path* -> /landing/:path* — sin él, "
        "descargas.html, img/, payments-config.js y reviews-data.js dan 404")


def test_checkout_has_no_serverside_only_botid():
    """Regresión: checkout.js corría checkBotId (Vercel BotID) sin que la
    landing integrara el cliente de BotID — TODOS los clics reales en
    'Comprar'/'Suscribirme' recibían 403 {"error":"bot"}. La verificación
    server-side sola no puede volver sin la instrumentación del navegador."""
    root = _repo_root()
    with open(os.path.join(root, "api", "checkout.js"), encoding="utf-8") as fh:
        src = fh.read()
    assert 'require("botid' not in src and "checkBotId(" not in src
    import json as _json
    with open(os.path.join(root, "package.json"), encoding="utf-8") as fh:
        pkg = _json.load(fh)
    assert "botid" not in pkg.get("dependencies", {}), (
        "botid en dependencies reactivaría el checkBotId server-side")


def test_landing_pages_declare_lang_and_notranslate():
    """Regresión: sin <html lang> el traductor automático del navegador
    'traducía' la página — la marca quedaba 'MV Gobernanza de Datos',
    'US$ 390' quedaba '390 dólares estadounidenses' y tocaba Purview/
    Collibra. La página ya es trilingüe nativa (ES/EN/PT): se declara el
    idioma y se marca notranslate."""
    root = _repo_root()
    for page in ("index.html", "descargas.html", "guia.html", "pago.html", "reviews.html"):
        with open(os.path.join(root, "landing", page), encoding="utf-8") as fh:
            src = fh.read()
        assert '<html lang="es" translate="no">' in src, page
        assert '<meta name="google" content="notranslate">' in src, page
        assert src.lstrip().startswith("<!doctype html>"), page


def test_landing_prices_use_usd_not_us_dollar_sign():
    """El usuario pidió USD en vez de 'US$' (que el traductor del navegador
    convertía en 'dólares estadounidenses'). Ningún precio visible puede
    volver a usar 'US$'."""
    with open(os.path.join(_repo_root(), "landing", "index.html"), encoding="utf-8") as fh:
        src = fh.read()
    visible = [ln for ln in src.splitlines()
               if "US$" in ln and not ln.strip().startswith(('"', "'", "<!--", "*"))
               and 'US$ 390" en' not in ln]  # el comentario que documenta el bug
    assert visible == [], f"precios con US$ visibles: {visible}"


def test_landing_credit_buy_buttons_are_not_white_on_white():
    """Regresión: los botones 'Comprar' de créditos usaban btn-o (texto
    blanco, fondo transparente) sobre tarjetas blancas — invisibles. Tienen
    que usar btn-od (fondo blanco, texto oscuro)."""
    with open(os.path.join(_repo_root(), "landing", "index.html"), encoding="utf-8") as fh:
        src = fh.read()
    for key in ("cred100", "cred2500"):
        line = next(ln for ln in src.splitlines() if f'data-mp="{key}"' in ln)
        assert "btn-od" in line, f"{key}: {line.strip()}"
        assert "btn-o " not in line and 'btn-o"' not in line


def test_landing_contact_form_has_visible_mail_fallback():
    """Regresión: el formulario de contacto usaba solo location.href=mailto:,
    que falla EN SILENCIO sin app de correo configurada. Tiene que existir el
    respaldo visible (dirección directa + aviso de copiado al portapapeles)."""
    with open(os.path.join(_repo_root(), "landing", "index.html"), encoding="utf-8") as fh:
        src = fh.read()
    assert 'id="mailFallback"' in src
    assert "navigator.clipboard" in src
    assert 'href="mailto:vieraschiavi@gmail.com"' in src  # link directo siempre visible


# ------------------------------------------------- migración a Purview/Collibra
def _sample_gov_tables():
    from mvdg.exporters import governance_tables
    gov = governance_tables("es")
    return gov["catalog"], gov["dictionary"], gov["glossary"]


def test_purview_off_by_default(monkeypatch):
    for var in ("PURVIEW_TENANT_ID", "PURVIEW_CLIENT_ID", "PURVIEW_CLIENT_SECRET",
               "PURVIEW_ACCOUNT_NAME"):
        monkeypatch.delenv(var, raising=False)
    from mvdg import purview_export as pv
    assert pv.configured() is False
    cat, dic, glo = _sample_gov_tables()
    with pytest.raises(RuntimeError):
        pv.push_catalog(cat, dic, dry_run=False)


def test_purview_dry_run_never_touches_network(monkeypatch):
    """dry_run=True (el default) tiene que funcionar SIN credenciales y sin
    pegarle a la red — es el modo de previsualización."""
    for var in ("PURVIEW_TENANT_ID", "PURVIEW_CLIENT_ID", "PURVIEW_CLIENT_SECRET",
               "PURVIEW_ACCOUNT_NAME"):
        monkeypatch.delenv(var, raising=False)
    from mvdg import purview_export as pv
    cat, dic, glo = _sample_gov_tables()
    r = pv.push_all(cat, dic, glo, dry_run=True)
    assert r["dry_run"] is True
    assert r["catalog"]["entity_count"] == len(cat) + len(dic)
    assert r["glossary"]["term_count"] == len(glo)
    assert r["pii"]["classification_count"] > 0  # dim_customers tiene PII real


def test_purview_glossary_status_reflects_curation(tmp_path, monkeypatch):
    """El estado Draft/Approved en Purview tiene que salir de la curaduría
    real: sin revisar -> Draft, validado/modificado -> Approved."""
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    from mvdg import curation, purview_export as pv
    cat, dic, glo = _sample_gov_tables()

    def lookup(term_id):
        rec = curation.get_record(f"glossary:demo:{term_id}", "es")
        return (rec["status"], rec.get("text") or "") if rec else ("sugerido_ia", "")

    before = pv.push_glossary(glo, curation_lookup=lookup, dry_run=True)
    assert all(t["status"] == "Draft" for t in before["terms"])

    first_term_id = glo.iloc[0]["term_id"]
    curation.save_validation(f"glossary:demo:{first_term_id}", "es", "validado",
                             "", "María Viera", "Data Owner")
    after = pv.push_glossary(glo, curation_lookup=lookup, dry_run=True)
    statuses = {t["name"]: t["status"] for t in after["terms"]}
    approved_name = glo.iloc[0]["term"]
    assert statuses[approved_name] == "Approved"
    assert sum(1 for s in statuses.values() if s == "Approved") == 1


def test_purview_classification_heuristic():
    from mvdg.purview_export import _pii_classification
    assert _pii_classification("email") == "MICROSOFT.PERSONAL.EMAIL"
    assert _pii_classification("correo_electronico") == "MICROSOFT.PERSONAL.EMAIL"
    assert _pii_classification("full_name") == "MICROSOFT.PERSONAL.NAME"


def test_purview_push_mocked_end_to_end(monkeypatch):
    monkeypatch.setenv("PURVIEW_TENANT_ID", "tid")
    monkeypatch.setenv("PURVIEW_CLIENT_ID", "cid")
    monkeypatch.setenv("PURVIEW_CLIENT_SECRET", "sec")
    monkeypatch.setenv("PURVIEW_ACCOUNT_NAME", "acct")
    from mvdg import purview_export as pv
    cat, dic, glo = _sample_gov_tables()

    calls = {"token": 0, "bulk": 0, "glossary_list": 0, "glossary_create": 0, "term": 0}

    def fake_http_form(url, form):
        calls["token"] += 1
        assert "login.microsoftonline.com/tid" in url
        assert form["resource"] == "https://purview.azure.net"
        return {"access_token": "ptok"}

    def fake_http_json(url, headers, method="GET", body=None):
        assert headers["Authorization"] == "Bearer ptok"
        if url.endswith("/entity/bulk"):
            calls["bulk"] += 1
            mutated = [{"guid": f"g-{i}", "attributes": {"qualifiedName": e["attributes"]["qualifiedName"]}}
                      for i, e in enumerate(body["entities"])]
            return {"mutatedEntities": {"CREATE": mutated, "UPDATE": []}}
        if url.endswith("/glossary") and method == "GET":
            calls["glossary_list"] += 1
            return []
        if url.endswith("/glossary") and method == "POST":
            calls["glossary_create"] += 1
            return {"guid": "gloss-1", "name": "MV Data Governance"}
        if url.endswith("/glossary/term"):
            calls["term"] += 1
            return {"guid": f"term-{calls['term']}"}
        if url.endswith("/entity/bulk/classification"):
            return {}
        raise AssertionError(f"unexpected URL: {url}")

    monkeypatch.setattr(pv, "_http_form", fake_http_form)
    monkeypatch.setattr(pv, "_http_json", fake_http_json)

    r = pv.push_all(cat, dic, glo, dry_run=False)
    assert calls["token"] == 1
    assert calls["bulk"] == 1
    assert calls["glossary_create"] == 1  # no existía -> se crea
    assert calls["term"] == len(glo)
    assert r["catalog"]["entity_count"] == len(cat) + len(dic)
    assert len(r["catalog"]["guid_by_qualified_name"]) == len(cat) + len(dic)
    assert r["pii"]["classification_count"] > 0


def test_collibra_off_by_default(monkeypatch):
    for var in ("COLLIBRA_BASE_URL", "COLLIBRA_USERNAME", "COLLIBRA_PASSWORD",
               "COLLIBRA_DOMAIN_ID"):
        monkeypatch.delenv(var, raising=False)
    from mvdg import collibra_export as cb
    assert cb.configured() is False
    cat, dic, glo = _sample_gov_tables()
    with pytest.raises(RuntimeError):
        cb.push_glossary(glo, dry_run=False)


def test_collibra_dry_run_never_touches_network(monkeypatch):
    for var in ("COLLIBRA_BASE_URL", "COLLIBRA_USERNAME", "COLLIBRA_PASSWORD",
               "COLLIBRA_DOMAIN_ID"):
        monkeypatch.delenv(var, raising=False)
    from mvdg import collibra_export as cb
    cat, dic, glo = _sample_gov_tables()
    r = cb.push_all(cat, dic, glo, dry_run=True)
    assert r["dry_run"] is True
    assert r["catalog"]["asset_count"] == len(cat) + len(dic)
    assert r["glossary"]["term_count"] == len(glo)
    # sin COLLIBRA_TABLE_TYPE_ID configurado, el payload usa un placeholder
    # visible en vez de fallar en silencio
    assert r["catalog"]["payloads"][0]["asset"]["typeId"] == "<COLLIBRA_TABLE_TYPE_ID>"


def test_collibra_term_type_id_has_documented_default(monkeypatch):
    for var in ("COLLIBRA_BASE_URL", "COLLIBRA_USERNAME", "COLLIBRA_PASSWORD",
               "COLLIBRA_DOMAIN_ID", "COLLIBRA_TERM_TYPE_ID"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("COLLIBRA_DOMAIN_ID", "dom-1")
    from mvdg import collibra_export as cb
    cat, dic, glo = _sample_gov_tables()
    r = cb.push_glossary(glo, dry_run=True)
    assert r["terms"][0]["asset"]["typeId"] == cb._DEFAULT_TERM_TYPE_ID


def test_collibra_push_mocked_end_to_end(monkeypatch):
    monkeypatch.setenv("COLLIBRA_BASE_URL", "https://acme.collibra.com")
    monkeypatch.setenv("COLLIBRA_USERNAME", "svc")
    monkeypatch.setenv("COLLIBRA_PASSWORD", "pw")
    monkeypatch.setenv("COLLIBRA_DOMAIN_ID", "dom-1")
    monkeypatch.setenv("COLLIBRA_TABLE_TYPE_ID", "type-table")
    monkeypatch.setenv("COLLIBRA_COLUMN_TYPE_ID", "type-column")
    from mvdg import collibra_export as cb
    cat, dic, glo = _sample_gov_tables()

    calls = {"login": 0, "assets": 0, "attributes": 0, "logout": 0}
    asset_ids = iter(range(10_000))

    def fake_http_json(url, headers, method="GET", body=None):
        if url.endswith("/auth/sessions") and method == "POST":
            calls["login"] += 1
            return {}, ["JSESSIONID=abc123; Path=/; HttpOnly"]
        if url.endswith("/auth/sessions/current") and method == "DELETE":
            calls["logout"] += 1
            return {}, []
        assert headers["Cookie"] == "JSESSIONID=abc123"
        if url.endswith("/assets"):
            calls["assets"] += 1
            return {"id": f"asset-{next(asset_ids)}"}, []
        if url.endswith("/attributes"):
            calls["attributes"] += 1
            assert body["typeId"] == cb.DEFINITION_ATTRIBUTE_TYPE_ID
            return {"id": "attr-1"}, []
        raise AssertionError(f"unexpected URL: {url}")

    monkeypatch.setattr(cb, "_http_json", fake_http_json)

    r = cb.push_catalog(cat, dic, dry_run=False)
    assert calls["login"] == 1 and calls["logout"] == 1
    assert calls["assets"] == len(cat) + len(dic)
    assert calls["attributes"] == len(cat) + len(dic)  # todas tienen descripción
    assert r["asset_count"] == len(cat) + len(dic)


def test_collibra_logout_failure_does_not_break_push(monkeypatch):
    """Best-effort sign-out: si el logout falla, el push ya hecho no se
    pierde (mismo criterio que Tableau)."""
    monkeypatch.setenv("COLLIBRA_BASE_URL", "https://acme.collibra.com")
    monkeypatch.setenv("COLLIBRA_USERNAME", "svc")
    monkeypatch.setenv("COLLIBRA_PASSWORD", "pw")
    monkeypatch.setenv("COLLIBRA_DOMAIN_ID", "dom-1")
    monkeypatch.setenv("COLLIBRA_TERM_TYPE_ID", "type-term")
    from mvdg import collibra_export as cb
    cat, dic, glo = _sample_gov_tables()

    def fake_http_json(url, headers, method="GET", body=None):
        if url.endswith("/auth/sessions") and method == "POST":
            return {}, ["JSESSIONID=abc123; Path=/"]
        if url.endswith("/auth/sessions/current"):
            raise OSError("network blip")
        if url.endswith("/assets"):
            return {"id": "asset-x"}, []
        if url.endswith("/attributes"):
            return {"id": "attr-x"}, []
        raise AssertionError(url)

    monkeypatch.setattr(cb, "_http_json", fake_http_json)
    r = cb.push_glossary(glo, dry_run=False)  # no debe levantar
    assert r["term_count"] == len(glo)


# ------------------- integración real (sockets HTTP de verdad, sin mockear
# _http_json): levanta un servidor local que imita Purview/Collibra y corre
# el conector real contra él, para probar el protocolo/JSON/auth de punta a
# punta y no solo que se llamó a la función esperada con los args esperados.
def _free_port():
    import socket
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def test_purview_integration_real_http_roundtrip(tmp_path, monkeypatch):
    import json
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    calls = {"token": 0, "bulk": 0, "glossary_post": 0, "term": 0, "classification": 0}
    received = {"entities": None, "terms": []}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _body(self):
            length = int(self.headers.get("Content-Length", 0))
            return json.loads(self.rfile.read(length)) if length else None

        def _send(self, code, payload):
            data = json.dumps(payload).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            body = self._body()
            if "/oauth2/token" in self.path:
                calls["token"] += 1
                self._send(200, {"access_token": "sim-token"})
            elif self.path.endswith("/entity/bulk"):
                calls["bulk"] += 1
                received["entities"] = body["entities"]
                mutated = [{"guid": f"guid-{i}", "attributes": {"qualifiedName": e["attributes"]["qualifiedName"]}}
                          for i, e in enumerate(body["entities"])]
                self._send(200, {"mutatedEntities": {"CREATE": mutated, "UPDATE": []}})
            elif self.path.endswith("/glossary"):
                calls["glossary_post"] += 1
                self._send(200, {"guid": "gloss-1", "name": body["name"]})
            elif self.path.endswith("/glossary/term"):
                calls["term"] += 1
                received["terms"].append(body)
                self._send(200, {"guid": f"term-{calls['term']}"})
            elif self.path.endswith("/entity/bulk/classification"):
                calls["classification"] += 1
                self._send(200, {})
            else:
                self._send(404, {"error": self.path})

        def do_GET(self):
            if self.path.endswith("/glossary"):
                self._send(200, [])
            else:
                self._send(404, {"error": self.path})

    port = _free_port()
    server = HTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
        monkeypatch.setenv("PURVIEW_TENANT_ID", "tid")
        monkeypatch.setenv("PURVIEW_CLIENT_ID", "cid")
        monkeypatch.setenv("PURVIEW_CLIENT_SECRET", "sec")
        monkeypatch.setenv("PURVIEW_ACCOUNT_NAME", "acct")
        monkeypatch.setenv("PURVIEW_API_BASE", f"http://127.0.0.1:{port}")
        from mvdg import curation, purview_export as pv

        def fake_get_token():
            import urllib.request
            req = urllib.request.Request(f"http://127.0.0.1:{port}/oauth2/token",
                                         data=b"{}", method="POST")
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read())["access_token"]

        monkeypatch.setattr(pv, "_get_token", fake_get_token)

        cat, dic, glo = _sample_gov_tables()
        first_term_id = glo.iloc[0]["term_id"]
        curation.save_validation(f"glossary:demo:{first_term_id}", "es", "modificado",
                                 "Definición oficial revisada por el Data Owner.",
                                 "María Viera", "Data Owner Comercial")

        def lookup(term_id):
            rec = curation.get_record(f"glossary:demo:{term_id}", "es")
            return (rec["status"], rec.get("text") or "") if rec else ("sugerido_ia", "")

        result = pv.push_all(cat, dic, glo, curation_lookup=lookup, dry_run=False)
    finally:
        server.shutdown()

    # tráfico HTTP real recibido por un servidor de verdad, no una función mockeada
    assert calls == {"token": 1, "bulk": 1, "glossary_post": 1, "term": len(glo), "classification": 2}
    assert len(received["entities"]) == len(cat) + len(dic)
    statuses = {t["name"]: t["status"] for t in received["terms"]}
    approved_name = glo.iloc[0]["term"]
    assert statuses[approved_name] == "Approved"
    assert sum(1 for s in statuses.values() if s == "Draft") == len(glo) - 1
    curated_term = next(t for t in received["terms"] if t["name"] == approved_name)
    assert "Definición oficial revisada" in curated_term["longDescription"]
    n_pii_cols = int((dic["pii"] == True).sum())  # noqa: E712
    assert result["pii"]["classification_count"] == n_pii_cols


def test_collibra_integration_real_http_roundtrip(tmp_path, monkeypatch):
    import json
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    calls = {"login": 0, "logout": 0, "assets": 0, "attributes": 0}
    received = {"assets": []}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _body(self):
            length = int(self.headers.get("Content-Length", 0))
            return json.loads(self.rfile.read(length)) if length else None

        def _send(self, code, payload, cookie=None):
            data = json.dumps(payload).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            if cookie:
                self.send_header("Set-Cookie", cookie)
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            body = self._body()
            if self.path.endswith("/auth/sessions"):
                calls["login"] += 1
                self._send(200, {"userId": "u-1"},
                          cookie="JSESSIONID=sim-session; Path=/; HttpOnly")
            elif self.path.endswith("/assets"):
                calls["assets"] += 1
                assert self.headers.get("Cookie") == "JSESSIONID=sim-session"
                received["assets"].append(body)
                self._send(200, {"id": f"asset-{calls['assets']}", "name": body["name"]})
            elif self.path.endswith("/attributes"):
                calls["attributes"] += 1
                assert self.headers.get("Cookie") == "JSESSIONID=sim-session"
                self._send(200, {"id": f"attr-{calls['attributes']}"})
            else:
                self._send(404, {"error": self.path})

        def do_DELETE(self):
            if self.path.endswith("/auth/sessions/current"):
                calls["logout"] += 1
                self._send(200, {})
            else:
                self._send(404, {"error": self.path})

    port = _free_port()
    server = HTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
        monkeypatch.setenv("COLLIBRA_BASE_URL", f"http://127.0.0.1:{port}")
        monkeypatch.setenv("COLLIBRA_USERNAME", "svc")
        monkeypatch.setenv("COLLIBRA_PASSWORD", "pw")
        monkeypatch.setenv("COLLIBRA_DOMAIN_ID", "dom-1")
        monkeypatch.setenv("COLLIBRA_TABLE_TYPE_ID", "table-type")
        monkeypatch.setenv("COLLIBRA_COLUMN_TYPE_ID", "column-type")
        from mvdg import collibra_export as cb
        cat, dic, glo = _sample_gov_tables()
        result = cb.push_all(cat, dic, glo, dry_run=False)
    finally:
        server.shutdown()

    assert calls["login"] == 1 and calls["logout"] == 1  # sesión única reusada
    assert calls["assets"] == len(cat) + len(dic) + len(glo)
    assert calls["attributes"] == calls["assets"]  # todas tienen descripción
    table_types = {a["typeId"] for a in received["assets"][:len(cat)]}
    assert table_types == {"table-type"}
    assert result["catalog"]["asset_count"] == len(cat) + len(dic)


# ------------------------------------------------ enforcement (DDL, no ejecuta)
def test_enforcement_grant_revoke_by_classification():
    from mvdg import enforcement as en
    cat, dic, glo = _sample_gov_tables()
    roles = {"PII": ["rol_rrhh"], "Confidencial": ["rol_finanzas"], "Interna": ["rol_ops"]}
    ddl = en.build_grant_revoke_ddl(cat, roles, engine="postgresql")
    text = "\n".join(ddl)
    assert "REVOKE ALL ON \"dim_customers\" FROM PUBLIC;" in text
    assert "GRANT SELECT ON \"dim_customers\" TO \"rol_rrhh\";" in text  # dim_customers es PII
    # cada dataset tiene su REVOKE + (0 o más) GRANT -> al menos 1 REVOKE por dataset
    assert text.count("REVOKE ALL ON") == len(cat)


def test_enforcement_masking_postgresql_uses_view_not_native():
    """PostgreSQL no tiene masking nativo de columna -> el DDL usa una
    vista con las columnas PII ofuscadas, no ALTER COLUMN (que no existe
    para esto en PG)."""
    from mvdg import enforcement as en
    cat, dic, glo = _sample_gov_tables()
    ddl = en.build_column_masking_ddl(dic, engine="postgresql")
    text = "\n".join(ddl)
    assert "CREATE OR REPLACE VIEW \"dim_customers_masked\"" in text
    assert "'***' AS \"email\"" in text
    assert "customer_id" in text  # columnas no-PII se ven igual, sin ofuscar


def test_enforcement_masking_sqlserver_uses_native_masked_with():
    from mvdg import enforcement as en
    cat, dic, glo = _sample_gov_tables()
    ddl = en.build_column_masking_ddl(dic, engine="sqlserver")
    text = "\n".join(ddl)
    assert "ADD MASKED WITH (FUNCTION = 'email()')" in text  # detecta email por nombre
    assert "ADD MASKED WITH (FUNCTION = 'default()')" in text  # resto de PII, genérico


def test_enforcement_unsupported_engine_raises_not_silently_wrong():
    from mvdg import enforcement as en
    cat, dic, glo = _sample_gov_tables()
    with pytest.raises(ValueError):
        en.build_column_masking_ddl(dic, engine="oracle")
    with pytest.raises(ValueError):
        en.build_row_level_security_ddl("dim_customers", "steward", "rol_x", engine="mysql")


def test_enforcement_plan_never_executes_anything():
    """El módulo entero es generación de texto -- no hay ningún camino que
    abra una conexión de base de datos."""
    import mvdg.enforcement as en_mod
    src = open(en_mod.__file__, encoding="utf-8").read()
    for forbidden in ("sqlalchemy", "psycopg2", "pyodbc", "create_engine", ".execute(", "urllib"):
        assert forbidden not in src, f"enforcement.py no debería importar/usar '{forbidden}'"

    from mvdg import enforcement as en
    cat, dic, glo = _sample_gov_tables()
    plan = en.enforcement_plan(cat, dic, {"PII": ["rol_rrhh"]}, engine="postgresql")
    assert plan["grant_statements"] > 0 and plan["masking_statements"] > 0
    assert "NO ejecutado" in plan["script"]


def test_enforcement_row_level_security_both_engines():
    from mvdg import enforcement as en
    pg = en.build_row_level_security_ddl("dim_customers", "steward", "rol_comercial", "postgresql")
    assert any("ENABLE ROW LEVEL SECURITY" in s for s in pg)
    assert any("CREATE POLICY" in s for s in pg)
    ss = en.build_row_level_security_ddl("dim_customers", "steward", "rol_comercial", "sqlserver")
    assert any("CREATE SECURITY POLICY" in s for s in ss)


# --------------------------------------------- etiquetas MIP (Graph API real)
def test_mip_off_by_default(monkeypatch):
    for var in ("MIP_TENANT_ID", "MIP_CLIENT_ID", "MIP_CLIENT_SECRET"):
        monkeypatch.delenv(var, raising=False)
    from mvdg import mip_labels as mip
    assert mip.configured() is False
    assert mip.list_labels() == []  # sin credenciales, no intenta pegarle a la red
    with pytest.raises(RuntimeError):
        mip.assign_label("d1", "i1", "lbl-1", dry_run=False)


def test_mip_share_url_encoding_matches_documented_algorithm():
    """Base64 -> base64url sin padding, '/'->'_', '+'->'-', prefijo 'u!'
    (documentado por Microsoft Learn, "Access shared items")."""
    from mvdg import mip_labels as mip
    import base64
    url = "https://contoso.sharepoint.com/:x:/s/team/EXAMPLE?e=abc"
    encoded = mip.encode_share_url(url)
    assert encoded.startswith("u!")
    # decodificable de vuelta
    b64 = encoded[2:].replace("_", "/").replace("-", "+")
    b64 += "=" * (-len(b64) % 4)
    assert base64.b64decode(b64).decode("utf-8") == url


def test_mip_dry_run_never_touches_network(monkeypatch):
    for var in ("MIP_TENANT_ID", "MIP_CLIENT_ID", "MIP_CLIENT_SECRET"):
        monkeypatch.delenv(var, raising=False)
    from mvdg import mip_labels as mip
    r = mip.assign_label("d1", "i1", "lbl-1", dry_run=True)
    assert r["dry_run"] is True and "assignSensitivityLabel" in r["url"]


def test_mip_suggest_label_never_invents_an_id():
    """La sugerencia SIEMPRE sale de la lista real de etiquetas del tenant
    -- nunca de un id inventado por el programa."""
    from mvdg import mip_labels as mip
    labels = [{"id": "real-id-1", "name": "Confidencial - Solo interno"},
             {"id": "real-id-2", "name": "Publico"}]
    picked = mip.suggest_label("PII", labels)
    assert picked["id"] == "real-id-1"  # matchea por nombre, id real de la lista
    assert mip.suggest_label("PII", []) is None  # sin etiquetas en el tenant, no inventa nada


def test_mip_plan_skips_datasets_without_mapped_file():
    """Un dataset gobernado que no tiene archivo mapeado en OneDrive/
    SharePoint no puede tener etiqueta MIP (la etiqueta vive en el
    archivo) -- se lista aparte, explícitamente, no se saltea en
    silencio."""
    from mvdg import mip_labels as mip
    cat, dic, glo = _sample_gov_tables()
    file_map = {"dim_customers": {"driveId": "d1", "itemId": "i1"}}
    labels = [{"id": "l1", "name": "Confidencial"}]
    r = mip.push_labels(cat, file_map, dry_run=True)
    assert len(r["plan"]) == 1 and r["plan"][0]["dataset"] == "dim_customers"
    assert set(r["skipped_no_file"]) == set(cat["dataset"]) - {"dim_customers"}


def test_mip_integration_real_http_roundtrip(monkeypatch):
    """Mismo patrón que la simulación de Purview/Collibra: servidor HTTP
    local real (sin mockear _http_json) para probar el protocolo/JSON/auth
    de punta a punta contra la Graph API tal como la documenta Microsoft."""
    import json
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    calls = {"token": 0, "labels": 0, "assign": 0}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _body(self):
            length = int(self.headers.get("Content-Length", 0))
            return json.loads(self.rfile.read(length)) if length else None

        def do_GET(self):
            if "sensitivityLabels" in self.path:
                calls["labels"] += 1
                payload = json.dumps({"value": [{"id": "lbl-conf", "name": "Confidencial"}]}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            body = self._body()
            if "assignSensitivityLabel" in self.path:
                calls["assign"] += 1
                assert body["sensitivityLabelId"] == "lbl-conf"
                self.send_response(202)
                self.send_header("Location", "http://example/monitor/1")
                self.send_header("Content-Length", "0")
                self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()

    port = _free_port()
    server = HTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        monkeypatch.setenv("MIP_TENANT_ID", "tid")
        monkeypatch.setenv("MIP_CLIENT_ID", "cid")
        monkeypatch.setenv("MIP_CLIENT_SECRET", "sec")
        from mvdg import mip_labels as mip
        monkeypatch.setattr(mip, "_GRAPH_V1", f"http://127.0.0.1:{port}")
        monkeypatch.setattr(mip, "_GRAPH_BETA", f"http://127.0.0.1:{port}")
        monkeypatch.setattr(mip, "_get_token", lambda: "fake-graph-token")

        cat, dic, glo = _sample_gov_tables()
        file_map = {"dim_customers": {"driveId": "drv-1", "itemId": "itm-1"}}
        result = mip.push_labels(cat, file_map, dry_run=False)
    finally:
        server.shutdown()

    assert calls == {"token": 0, "labels": 1, "assign": 1}  # token mockeado aparte, no cuenta
    assert result["assigned"][0]["dataset"] == "dim_customers"
    assert result["assigned"][0]["result"]["status"] == 202


# --------------------------------------------------- escaneo de todas las conexiones
def test_connectors_scan_all_partial_failure_does_not_stop_the_rest(tmp_path, monkeypatch):
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    import sqlite3
    from mvdg import connectors as C

    good_db = str(tmp_path / "ok.db")
    con = sqlite3.connect(good_db)
    pd.DataFrame({"id": [1, 2]}).to_sql("clientes", con, index=False)
    con.close()

    C.save_connection({"name": "OK", "engine": "sqlite", "database": good_db,
                       "user": "", "password": ""}, save_password=False)
    C.save_connection({"name": "Rota", "engine": "sqlite", "database": "/no/existe.db",
                       "user": "", "password": ""}, save_password=False)

    df = C.scan_all_connections()
    assert set(df["name"]) == {"OK", "Rota"}
    ok_rows = df[df["name"] == "OK"]
    assert "clientes" in ok_rows["table"].tolist()
    assert ok_rows["error"].isna().all()
    broken_rows = df[df["name"] == "Rota"]
    assert broken_rows["table"].isna().all()
    assert broken_rows["error"].notna().all()


# ------------------------------------------- Azure Resource Graph (discovery)
def test_azure_discovery_off_by_default(monkeypatch):
    for var in ("AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET",
               "AZURE_SUBSCRIPTION_ID"):
        monkeypatch.delenv(var, raising=False)
    from mvdg import azure_discovery as az
    assert az.configured() is False
    with pytest.raises(RuntimeError):
        az.discover_data_resources()


def test_azure_discovery_query_covers_all_data_types():
    from mvdg import azure_discovery as az
    q = az.build_query()
    assert q.startswith("Resources | where type in~ (")
    for t in az.DATA_RESOURCE_TYPES:
        assert f"'{t}'" in q


def test_azure_discovery_suggest_connection_profile_maps_known_types():
    from mvdg import azure_discovery as az
    sql = az.suggest_connection_profile({"type": "microsoft.sql/servers/databases", "name": "srv1/db1"})
    assert sql["engine"] == "sqlserver" and "database.windows.net" in sql["host"]
    pg = az.suggest_connection_profile({"type": "microsoft.dbforpostgresql/flexibleservers", "name": "pg1"})
    assert pg["engine"] == "postgresql"
    # un tipo no relacionado con conexión (ej. Storage) no sugiere perfil -- no inventa un motor que no existe
    assert az.suggest_connection_profile({"type": "microsoft.storage/storageaccounts", "name": "s1"}) is None


def test_azure_discovery_mocked_end_to_end(monkeypatch):
    monkeypatch.setenv("AZURE_TENANT_ID", "tid")
    monkeypatch.setenv("AZURE_CLIENT_ID", "cid")
    monkeypatch.setenv("AZURE_CLIENT_SECRET", "sec")
    monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", "sub-1")
    from mvdg import azure_discovery as az

    calls = {"query": 0}

    def fake_http_json(url, headers, body):
        assert headers["Authorization"] == "Bearer tok-123"
        assert body["subscriptions"] == ["sub-1"]
        calls["query"] += 1
        return {"data": [
            {"name": "srv1/db1", "type": "microsoft.sql/servers/databases",
             "resourceGroup": "rg1", "location": "eastus", "subscriptionId": "sub-1", "id": "/x/1"},
            {"name": "stg1", "type": "microsoft.storage/storageaccounts",
             "resourceGroup": "rg1", "location": "eastus", "subscriptionId": "sub-1", "id": "/x/2"},
        ]}  # sin $skipToken -> una sola página

    monkeypatch.setattr(az, "_get_token", lambda: "tok-123")
    monkeypatch.setattr(az, "_http_json", fake_http_json)

    df = az.discover_data_resources()
    assert calls["query"] == 1
    assert len(df) == 2
    assert set(df["category"]) == {"Azure SQL Database", "Storage Account"}
    assert "resourceGroup" in df.columns and "location" in df.columns


def test_azure_discovery_paginates_with_skiptoken(monkeypatch):
    monkeypatch.setenv("AZURE_TENANT_ID", "tid")
    monkeypatch.setenv("AZURE_CLIENT_ID", "cid")
    monkeypatch.setenv("AZURE_CLIENT_SECRET", "sec")
    monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", "sub-1")
    from mvdg import azure_discovery as az

    pages = [
        {"data": [{"name": f"db{i}", "type": "microsoft.sql/servers/databases",
                  "resourceGroup": "rg", "location": "eastus", "subscriptionId": "sub-1", "id": f"/x/{i}"}
                 for i in range(3)], "$skipToken": "page2"},
        {"data": [{"name": "db3", "type": "microsoft.sql/servers/databases",
                  "resourceGroup": "rg", "location": "eastus", "subscriptionId": "sub-1", "id": "/x/3"}]},
    ]
    calls = {"n": 0}

    def fake_http_json(url, headers, body):
        page = pages[calls["n"]]
        calls["n"] += 1
        return page

    monkeypatch.setattr(az, "_get_token", lambda: "tok-123")
    monkeypatch.setattr(az, "_http_json", fake_http_json)
    df = az.discover_data_resources()
    assert calls["n"] == 2
    assert len(df) == 4


# --------------------------------------------- Collibra pull (conector inverso)
def test_collibra_pull_off_by_default(monkeypatch):
    for var in ("COLLIBRA_BASE_URL", "COLLIBRA_USERNAME", "COLLIBRA_PASSWORD",
               "COLLIBRA_DOMAIN_ID"):
        monkeypatch.delenv(var, raising=False)
    from mvdg import collibra_pull as cbp
    with pytest.raises(RuntimeError):
        cbp.pull_glossary()
    with pytest.raises(RuntimeError):
        cbp.pull_catalog()


def test_collibra_pull_catalog_requires_table_type_id(monkeypatch):
    monkeypatch.setenv("COLLIBRA_BASE_URL", "https://acme.collibra.com")
    monkeypatch.setenv("COLLIBRA_USERNAME", "svc")
    monkeypatch.setenv("COLLIBRA_PASSWORD", "pw")
    monkeypatch.setenv("COLLIBRA_DOMAIN_ID", "dom-1")
    monkeypatch.delenv("COLLIBRA_TABLE_TYPE_ID", raising=False)
    from mvdg import collibra_pull as cbp
    assert cbp.table_pull_configured() is False
    with pytest.raises(RuntimeError):
        cbp.pull_catalog()
    # pull_all no debe explotar -- reporta el catálogo salteado explícitamente
    import mvdg.collibra_export as cb

    def fake_http_json(url, headers, method="GET", body=None):
        if url.endswith("/auth/sessions"):
            return {}, ["JSESSIONID=sess1; Path=/"]
        if url.endswith("/auth/sessions/current"):
            return {}, []
        if "/assets" in url:
            return {"total": 0, "offset": 0, "limit": 200, "results": []}, []
        raise AssertionError(url)

    monkeypatch.setattr(cb, "_http_json", fake_http_json)
    r = cbp.pull_all()
    assert r["catalog"]["table_count"] == 0
    assert "skipped_reason" in r["catalog"]


def test_collibra_pull_integration_real_http_roundtrip(monkeypatch):
    import json
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    calls = {"login": 0, "logout": 0, "assets": 0, "attributes": 0}
    term_asset = {"id": "asset-term-1", "name": "Cliente"}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code, payload, cookie=None):
            data = json.dumps(payload).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            if cookie:
                self.send_header("Set-Cookie", cookie)
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            if self.path.endswith("/auth/sessions"):
                calls["login"] += 1
                self._send(200, {"userId": "u-1"}, cookie="JSESSIONID=pull-sess; Path=/; HttpOnly")
            else:
                self._send(404, {"error": self.path})

        def do_GET(self):
            assert self.headers.get("Cookie") == "JSESSIONID=pull-sess"
            if self.path.startswith("/rest/2.0/assets"):
                calls["assets"] += 1
                self._send(200, {"total": 1, "offset": 0, "limit": 200, "results": [term_asset]})
            elif self.path.startswith("/rest/2.0/attributes"):
                calls["attributes"] += 1
                assert f"assetId={term_asset['id']}" in self.path
                self._send(200, {"total": 1, "offset": 0, "limit": 200,
                                 "results": [{"value": "Definición real traída de Collibra."}]})
            else:
                self._send(404, {"error": self.path})

        def do_DELETE(self):
            calls["logout"] += 1
            self._send(200, {})

    port = _free_port()
    server = HTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        monkeypatch.setenv("COLLIBRA_BASE_URL", f"http://127.0.0.1:{port}")
        monkeypatch.setenv("COLLIBRA_USERNAME", "svc")
        monkeypatch.setenv("COLLIBRA_PASSWORD", "pw")
        monkeypatch.setenv("COLLIBRA_DOMAIN_ID", "dom-1")
        from mvdg import collibra_pull as cbp
        result = cbp.pull_glossary()
    finally:
        server.shutdown()

    assert calls == {"login": 1, "logout": 1, "assets": 1, "attributes": 1}
    assert result["term_count"] == 1
    assert result["terms"][0]["name"] == "Cliente"
    assert result["terms"][0]["definition"] == "Definición real traída de Collibra."


# ================================================== fixes 2026-07-16 (round 2)
# Purview pull (conector inverso), persistencia de lo importado, qualifiedNames
# reales, keyring, login del modo servidor, robustez de red y simetría de
# estados Collibra — ver docs/PURVIEW_COLLIBRA.md para el detalle de cada uno.

def test_purview_pull_off_by_default(monkeypatch):
    for var in ("PURVIEW_TENANT_ID", "PURVIEW_CLIENT_ID", "PURVIEW_CLIENT_SECRET",
               "PURVIEW_ACCOUNT_NAME"):
        monkeypatch.delenv(var, raising=False)
    from mvdg import purview_pull as pvp
    assert pvp.configured() is False
    with pytest.raises(RuntimeError):
        pvp.pull_glossary()
    with pytest.raises(RuntimeError):
        pvp.pull_catalog()


def test_purview_pull_mocked_glossary_and_catalog(monkeypatch):
    monkeypatch.setenv("PURVIEW_TENANT_ID", "tid")
    monkeypatch.setenv("PURVIEW_CLIENT_ID", "cid")
    monkeypatch.setenv("PURVIEW_CLIENT_SECRET", "sec")
    monkeypatch.setenv("PURVIEW_ACCOUNT_NAME", "acct")
    from mvdg import purview_export as pv
    from mvdg import purview_pull as pvp

    calls = {"token": 0, "glossary_list": 0, "terms_list": 0, "search": 0}

    def fake_http_form(url, form):
        calls["token"] += 1
        return {"access_token": "ptok"}

    def fake_http_json(url, headers, method="GET", body=None):
        assert headers["Authorization"] == "Bearer ptok"
        if url.endswith("/glossary") and method == "GET":
            calls["glossary_list"] += 1
            return [{"guid": "gloss-1", "name": "MV Data Governance"}]
        if url.endswith("/glossary/gloss-1/terms"):
            calls["terms_list"] += 1
            return [{"guid": "term-1", "name": "Cliente", "longDescription": "Definición larga."},
                    {"guid": "term-2", "name": "Venta", "shortDescription": "Corta."},
                    {"name": "sin guid, se descarta"}]
        if "/datamap/api/search/query" in url:
            calls["search"] += 1
            return {"value": [{"id": "tbl-1", "name": "dim_customers", "description": "Tabla real."}],
                    "continuationToken": None}
        raise AssertionError(f"unexpected URL: {method} {url}")

    monkeypatch.setattr(pv, "_http_form", fake_http_form)
    monkeypatch.setattr(pv, "_http_json", fake_http_json)

    r = pvp.pull_all()
    assert calls["token"] == 2  # un token por función (glosario y catálogo piden el suyo)
    assert r["glossary"]["term_count"] == 2
    names = {t["name"] for t in r["glossary"]["terms"]}
    assert names == {"Cliente", "Venta"}
    assert r["catalog"]["table_count"] == 1
    assert r["catalog"]["tables"][0]["name"] == "dim_customers"


def test_purview_pull_glossary_missing_returns_empty(monkeypatch):
    monkeypatch.setenv("PURVIEW_TENANT_ID", "tid")
    monkeypatch.setenv("PURVIEW_CLIENT_ID", "cid")
    monkeypatch.setenv("PURVIEW_CLIENT_SECRET", "sec")
    monkeypatch.setenv("PURVIEW_ACCOUNT_NAME", "acct")
    from mvdg import purview_export as pv
    from mvdg import purview_pull as pvp
    monkeypatch.setattr(pv, "_http_form", lambda url, form: {"access_token": "t"})
    monkeypatch.setattr(pv, "_http_json", lambda url, headers, method="GET", body=None: [])
    r = pvp.pull_glossary()
    assert r["term_count"] == 0 and r["terms"] == []


def test_purview_pull_catalog_paginates_with_continuation_token(monkeypatch):
    monkeypatch.setenv("PURVIEW_TENANT_ID", "tid")
    monkeypatch.setenv("PURVIEW_CLIENT_ID", "cid")
    monkeypatch.setenv("PURVIEW_CLIENT_SECRET", "sec")
    monkeypatch.setenv("PURVIEW_ACCOUNT_NAME", "acct")
    from mvdg import purview_export as pv
    from mvdg import purview_pull as pvp

    pages = [
        {"value": [{"id": "t1", "name": "a"}], "continuationToken": "cont-2"},
        {"value": [{"id": "t2", "name": "b"}], "continuationToken": None},
    ]
    calls = {"n": 0}

    def fake_http_json(url, headers, method="GET", body=None):
        page = pages[calls["n"]]
        calls["n"] += 1
        return page

    monkeypatch.setattr(pv, "_http_form", lambda url, form: {"access_token": "t"})
    monkeypatch.setattr(pv, "_http_json", fake_http_json)
    r = pvp.pull_catalog()
    assert calls["n"] == 2
    assert r["table_count"] == 2
    assert {t["name"] for t in r["tables"]} == {"a", "b"}


def test_purview_pull_integration_real_http_roundtrip(monkeypatch):
    """Servidor HTTP local real: prueba el protocolo de punta a punta (auth
    header, JSON, paginación por continuationToken) sin mockear _http_json."""
    import json
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    calls = {"token": 0, "glossary": 0, "terms": 0, "search": 0}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code, payload):
            data = json.dumps(payload).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            if "/oauth2/token" in self.path:
                calls["token"] += 1
                self._send(200, {"access_token": "sim-token"})
            elif "/datamap/api/search/query" in self.path:
                calls["search"] += 1
                self._send(200, {"value": [{"id": "tbl-1", "name": "dim_customers",
                                            "description": "real"}], "continuationToken": None})
            else:
                self._send(404, {"error": self.path})

        def do_GET(self):
            assert self.headers.get("Authorization") == "Bearer sim-token"
            if self.path.endswith("/glossary"):
                calls["glossary"] += 1
                self._send(200, [{"guid": "gloss-1", "name": "MV Data Governance"}])
            elif self.path.endswith("/glossary/gloss-1/terms"):
                calls["terms"] += 1
                self._send(200, [{"guid": "term-1", "name": "Cliente",
                                  "longDescription": "Definición real."}])
            else:
                self._send(404, {"error": self.path})

    port = _free_port()
    server = HTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        monkeypatch.setenv("PURVIEW_TENANT_ID", "tid")
        monkeypatch.setenv("PURVIEW_CLIENT_ID", "cid")
        monkeypatch.setenv("PURVIEW_CLIENT_SECRET", "sec")
        monkeypatch.setenv("PURVIEW_ACCOUNT_NAME", "acct")
        monkeypatch.setenv("PURVIEW_API_BASE", f"http://127.0.0.1:{port}")
        from mvdg import purview_export as pv
        from mvdg import purview_pull as pvp

        def fake_get_token():
            import urllib.request
            req = urllib.request.Request(f"http://127.0.0.1:{port}/oauth2/token",
                                         data=b"{}", method="POST")
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read())["access_token"]

        monkeypatch.setattr(pv, "_get_token", fake_get_token)
        result = pvp.pull_all()
    finally:
        server.shutdown()

    assert calls["token"] == 2 and calls["glossary"] == 1 and calls["terms"] == 1
    assert calls["search"] == 1
    assert result["glossary"]["terms"][0]["name"] == "Cliente"
    assert result["catalog"]["tables"][0]["name"] == "dim_customers"


# --------------------------------------------------- persistencia de lo importado
def test_imported_save_list_delete_terms_and_tables(tmp_path, monkeypatch):
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    from mvdg import imported
    n = imported.save_terms("collibra", [{"collibra_id": "a1", "name": "Cliente",
                                          "definition": "Def traída."}])
    assert n == 1
    n2 = imported.save_tables("purview", [{"purview_id": "t1", "name": "dim_x",
                                           "description": "Tabla traída."}])
    assert n2 == 1
    terms = imported.list_terms()
    tables = imported.list_tables()
    assert len(terms) == 1 and terms.iloc[0]["name"] == "Cliente"
    assert len(tables) == 1 and tables.iloc[0]["source"] == "purview"
    assert imported.delete_term("collibra", "a1") is True
    assert imported.delete_term("collibra", "a1") is False  # ya no está
    assert imported.delete_table("purview", "t1") is True
    assert imported.list_terms().empty and imported.list_tables().empty


def test_imported_save_rejects_unknown_source(tmp_path, monkeypatch):
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    from mvdg import imported
    with pytest.raises(ValueError):
        imported.save_terms("atlan", [{"collibra_id": "a1", "name": "X"}])


def test_imported_save_skips_items_without_id_or_name(tmp_path, monkeypatch):
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    from mvdg import imported
    n = imported.save_terms("collibra", [{"collibra_id": "", "name": "Sin id"},
                                         {"collibra_id": "ok1", "name": ""}])
    assert n == 0
    assert imported.list_terms().empty


def test_imported_items_enter_curation_flow(tmp_path, monkeypatch):
    """Lo importado no queda aislado: entra al mismo inventario de
    curaduría que el catálogo/glosario de demo y los samples."""
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    from mvdg import curation, imported
    imported.save_terms("collibra", [{"collibra_id": "a1", "name": "Cliente Importado",
                                      "definition": "Definición traída de Collibra."}])
    df = curation.list_items("es")
    row = df[df["item_id"] == "glossary:imported:collibra:a1"]
    assert len(row) == 1
    assert row.iloc[0]["status"] == "sugerido_ia"
    assert row.iloc[0]["text"] == "Definición traída de Collibra."
    # y se puede validar como cualquier otra definición
    curation.save_validation("glossary:imported:collibra:a1", "es", "validado",
                             "", "M. Viera", "Data Owner")
    df2 = curation.list_items("es")
    row2 = df2[df2["item_id"] == "glossary:imported:collibra:a1"]
    assert row2.iloc[0]["status"] == "validado"


# ------------------------------------------------------- keyring / connectors
def test_connectors_keyring_probe_never_raises(monkeypatch):
    """Sea cual sea el estado del keyring del SO en esta máquina, la sonda
    nunca puede tirar una excepción — ni siquiera un PanicException de
    pyo3 (que no hereda de Exception) si el backend está roto."""
    from mvdg import connectors as c
    c._keyring_ok_cache = None  # forzar una sonda real, no la cacheada
    result = c._keyring_usable()
    assert isinstance(result, bool)


def test_connectors_password_falls_back_to_obfuscation_without_keyring(tmp_path, monkeypatch):
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    from mvdg import connectors as c
    monkeypatch.setattr(c, "_keyring_usable", lambda: False)
    prof = c.save_connection({"name": "t", "engine": "postgresql", "host": "h",
                              "port": 5432, "database": "d", "user": "u",
                              "password": "s3cr3t"}, save_password=True)
    assert prof["secret_backend"] == "obfuscated"
    assert prof["password_enc"]  # algo quedó guardado, ofuscado
    assert c.stored_password(prof) == "s3cr3t"
    assert c.secret_backend_label(prof) == "obfuscated"


def test_connectors_password_uses_keyring_when_available(tmp_path, monkeypatch):
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    from mvdg import connectors as c
    store: dict[tuple, str] = {}
    monkeypatch.setattr(c, "_keyring_usable", lambda: True)

    def fake_set(conn_id, secret):
        store[conn_id] = secret
        return True

    def fake_get(conn_id):
        return store.get(conn_id, "")

    def fake_delete(conn_id):
        store.pop(conn_id, None)

    monkeypatch.setattr(c, "_keyring_set", fake_set)
    monkeypatch.setattr(c, "_keyring_get", fake_get)
    monkeypatch.setattr(c, "_keyring_delete", fake_delete)

    prof = c.save_connection({"name": "t", "engine": "postgresql", "host": "h",
                              "port": 5432, "database": "d", "user": "u",
                              "password": "s3cr3t"}, save_password=True)
    assert prof["secret_backend"] == "keyring"
    assert prof["password_enc"] == ""  # nada en el JSON, quedó en el keyring
    assert c.stored_password(prof) == "s3cr3t"
    c.delete_connection(prof["conn_id"])
    assert prof["conn_id"] not in store  # se limpió del keyring también


def test_connectors_no_password_clears_keyring_entry(tmp_path, monkeypatch):
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    from mvdg import connectors as c
    deleted = []
    monkeypatch.setattr(c, "_keyring_delete", lambda cid: deleted.append(cid))
    prof = c.save_connection({"name": "t", "engine": "postgresql", "host": "h",
                              "port": 5432, "database": "d", "user": "u",
                              "password": "x"}, save_password=False)
    assert prof["secret_backend"] == ""
    assert c.secret_backend_label(prof) == "none"
    assert deleted == [prof["conn_id"]]


def test_connectors_purview_qualified_name_azure_sql_confirmed_format():
    from mvdg.connectors import purview_qualified_name
    profile = {"engine": "sqlserver", "host": "myserver.database.windows.net",
              "database": "SalesDB"}
    assert (purview_qualified_name(profile, "dbo.dim_customers")
           == "mssql://myserver.database.windows.net/SalesDB/dbo/dim_customers")
    # sin schema explícito, se asume dbo (default de Azure SQL/SQL Server)
    assert (purview_qualified_name(profile, "dim_customers")
           == "mssql://myserver.database.windows.net/SalesDB/dbo/dim_customers")


def test_connectors_purview_qualified_name_none_when_not_azure_sql():
    """Para lo que Microsoft NO documenta el formato exacto (on-prem, otros
    motores/hosts) se devuelve None a propósito — no se inventa un
    qualifiedName que después no matchea con lo que Purview escaneó de
    verdad. Lo que decide es el HOST (el único patrón confirmado es
    *.database.windows.net), no una lista de motores permitidos."""
    from mvdg.connectors import purview_qualified_name
    on_prem = {"engine": "sqlserver", "host": "srv-datos.miempresa.local", "database": "d"}
    assert purview_qualified_name(on_prem, "t") is None
    postgres_local = {"engine": "postgresql", "host": "pg.miempresa.local", "database": "d"}
    assert purview_qualified_name(postgres_local, "t") is None
    assert purview_qualified_name({"engine": "postgresql", "host": "", "database": "d"}, "t") is None
    assert purview_qualified_name({"engine": "sqlserver",
                                   "host": "x.database.windows.net", "database": ""}, "t") is None


# --------------------------------------------------------- login modo servidor
def test_server_auth_not_required_in_desktop_mode(monkeypatch):
    from mvdg import server
    monkeypatch.delenv("MVDG_SERVER_MODE", raising=False)
    monkeypatch.setenv("MVDG_SERVER_PASSWORD", "secreto")
    assert server.server_mode_active() is False
    assert server.auth_required() is False  # modo escritorio: no se pide login


def test_server_auth_required_only_with_password_set(monkeypatch):
    from mvdg import server
    monkeypatch.setenv("MVDG_SERVER_MODE", "1")
    monkeypatch.delenv("MVDG_SERVER_PASSWORD", raising=False)
    assert server.auth_required() is False  # servidor pero sin contraseña configurada
    monkeypatch.setenv("MVDG_SERVER_PASSWORD", "secreto")
    assert server.auth_required() is True


def test_server_check_password_correct_and_constant_time(monkeypatch):
    from mvdg import server
    monkeypatch.setenv("MVDG_SERVER_PASSWORD", "correcta123")
    assert server.check_password("correcta123") is True
    assert server.check_password("incorrecta") is False
    assert server.check_password("") is False
    monkeypatch.delenv("MVDG_SERVER_PASSWORD", raising=False)
    assert server.check_password("cualquiera") is False  # sin var seteada, nunca entra


def test_server_run_server_sets_server_mode_flag(monkeypatch, tmp_path):
    """run_server() marca MVDG_SERVER_MODE escribiendo os.environ
    directamente (a propósito: tiene que sobrevivir mientras el proceso de
    Streamlit está arriba) — por eso este test la limpia a mano en un
    finally en vez de confiar en monkeypatch, que solo deshace lo que él
    mismo seteó."""
    from mvdg import server
    monkeypatch.delenv("MVDG_SERVER_MODE", raising=False)
    monkeypatch.setenv("MVDG_AUTHORIZED_HOSTS", "*")
    try:
        argv_out = []
        server.run_server(argv_out=argv_out)
        assert os.environ.get("MVDG_SERVER_MODE") == "1"
        assert argv_out  # se armaron los argumentos de streamlit
    finally:
        os.environ.pop("MVDG_SERVER_MODE", None)


# --------------------------------------------------- Purview: relación, qualifiedName real
def test_purview_classification_phone_is_phone_not_ip():
    """Regresión: 'telefono' mapeaba por error a MICROSOFT.PERSONAL.IPADDRESS."""
    from mvdg.purview_export import _pii_classification
    assert _pii_classification("telefono") == "MICROSOFT.PERSONAL.US.PHONE_NUMBER"
    assert _pii_classification("phone_number") == "MICROSOFT.PERSONAL.US.PHONE_NUMBER"
    assert _pii_classification("ip_address") == "MICROSOFT.PERSONAL.IPADDRESS"
    assert _pii_classification("full_name") == "MICROSOFT.PERSONAL.NAME"


def test_purview_columns_link_to_their_table():
    """Cada rdbms_column debe referenciar a su rdbms_table por qualifiedName
    (relationshipAttributes.table) — sin esto, la pestaña Schema de la
    tabla queda vacía en Purview."""
    from mvdg.purview_export import build_entity_payload
    cat, dic, _ = _sample_gov_tables()
    entities = build_entity_payload(cat, dic)
    columns = [e for e in entities if e["typeName"] == "rdbms_column"]
    assert columns
    for c in columns:
        rel = c["relationshipAttributes"]["table"]
        assert rel["typeName"] == "rdbms_table"
        table_qn = c["attributes"]["qualifiedName"].rsplit("#", 1)[0]
        assert rel["uniqueAttributes"]["qualifiedName"] == table_qn


def test_purview_qualified_name_map_used_when_provided():
    """Con un qualifiedName real (de una conexión SQL), la entidad se
    fusiona con lo que Purview ya escaneó en vez de usar mvdg://."""
    from mvdg.purview_export import build_entity_payload
    cat, dic, _ = _sample_gov_tables()
    ds = cat.iloc[0]["dataset"]
    qn_map = {ds: f"mssql://srv.database.windows.net/db/dbo/{ds}"}
    entities = build_entity_payload(cat, dic, qualified_name_map=qn_map)
    table_entity = next(e for e in entities if e["typeName"] == "rdbms_table"
                        and e["attributes"]["name"] == ds)
    assert table_entity["attributes"]["qualifiedName"] == qn_map[ds]
    col_entity = next(e for e in entities if e["typeName"] == "rdbms_column"
                      and e["attributes"]["qualifiedName"].startswith(qn_map[ds]))
    assert col_entity["relationshipAttributes"]["table"]["uniqueAttributes"]["qualifiedName"] == qn_map[ds]
    # el resto de los datasets, sin entrada en el mapa, siguen usando mvdg://
    other_ds = cat.iloc[1]["dataset"]
    other_entity = next(e for e in entities if e["typeName"] == "rdbms_table"
                        and e["attributes"]["name"] == other_ds)
    assert other_entity["attributes"]["qualifiedName"] == f"mvdg://{other_ds}"


def test_purview_glossary_repush_updates_existing_terms_not_recreates(monkeypatch):
    """Un segundo push del glosario NO debe fallar con 409: los términos que
    ya existen (por nombre) se actualizan con PUT; los nuevos se crean."""
    monkeypatch.setenv("PURVIEW_TENANT_ID", "tid")
    monkeypatch.setenv("PURVIEW_CLIENT_ID", "cid")
    monkeypatch.setenv("PURVIEW_CLIENT_SECRET", "sec")
    monkeypatch.setenv("PURVIEW_ACCOUNT_NAME", "acct")
    from mvdg import purview_export as pv
    _cat, _dic, glo = _sample_gov_tables()
    existing_name = glo.iloc[0]["term"]

    calls = {"term_post": 0, "term_put": 0, "terms_list": 0}

    def fake_http_form(url, form):
        return {"access_token": "ptok"}

    def fake_http_json(url, headers, method="GET", body=None):
        if url.endswith("/glossary") and method == "GET":
            return [{"guid": "gloss-1", "name": "MV Data Governance"}]
        if url.endswith("/glossary/gloss-1/terms") and method == "GET":
            calls["terms_list"] += 1
            return [{"guid": "term-old-1", "name": existing_name}]
        if url.endswith("/glossary/term") and method == "POST":
            calls["term_post"] += 1
            return {"guid": f"term-new-{calls['term_post']}"}
        if "/glossary/term/term-old-1" in url and method == "PUT":
            calls["term_put"] += 1
            assert body["guid"] == "term-old-1"
            assert body["anchor"]["glossaryGuid"] == "gloss-1"
            return {"guid": "term-old-1"}
        raise AssertionError(f"unexpected URL: {method} {url}")

    monkeypatch.setattr(pv, "_http_form", fake_http_form)
    monkeypatch.setattr(pv, "_http_json", fake_http_json)

    r = pv.push_glossary(glo, dry_run=False)
    assert calls["terms_list"] == 1
    assert calls["term_put"] == 1                  # el que ya existía
    assert calls["term_post"] == len(glo) - 1       # el resto se crea
    assert r["term_count"] == len(glo)
    assert r["failed"] == []


def test_purview_glossary_failed_term_does_not_abort_the_rest(monkeypatch):
    monkeypatch.setenv("PURVIEW_TENANT_ID", "tid")
    monkeypatch.setenv("PURVIEW_CLIENT_ID", "cid")
    monkeypatch.setenv("PURVIEW_CLIENT_SECRET", "sec")
    monkeypatch.setenv("PURVIEW_ACCOUNT_NAME", "acct")
    import urllib.error
    from mvdg import purview_export as pv
    _cat, _dic, glo = _sample_gov_tables()
    bad_name = glo.iloc[0]["term"]

    def fake_http_json(url, headers, method="GET", body=None):
        if url.endswith("/glossary") and method == "GET":
            return [{"guid": "gloss-1", "name": "MV Data Governance"}]
        if url.endswith("/glossary/gloss-1/terms") and method == "GET":
            return []  # ningún término existente: todo se crea por POST
        if url.endswith("/glossary/term") and method == "POST":
            if body["name"] == bad_name:
                raise urllib.error.HTTPError(url, 500, "boom", None, None)
            return {"guid": "term-ok"}
        raise AssertionError(f"unexpected URL: {method} {url}")

    monkeypatch.setattr(pv, "_http_form", lambda url, form: {"access_token": "t"})
    monkeypatch.setattr(pv, "_http_json", fake_http_json)
    r = pv.push_glossary(glo, dry_run=False)
    assert len(r["failed"]) == 1 and r["failed"][0]["name"] == bad_name
    assert r["term_count"] == len(glo) - 1  # el resto se creó igual


def test_purview_push_catalog_batches_large_entity_lists(monkeypatch):
    monkeypatch.setenv("PURVIEW_TENANT_ID", "tid")
    monkeypatch.setenv("PURVIEW_CLIENT_ID", "cid")
    monkeypatch.setenv("PURVIEW_CLIENT_SECRET", "sec")
    monkeypatch.setenv("PURVIEW_ACCOUNT_NAME", "acct")
    from mvdg import purview_export as pv
    monkeypatch.setattr(pv, "_BULK_BATCH_SIZE", 2)  # fuerza varios lotes con pocos datos
    cat, dic, _glo = _sample_gov_tables()

    calls = {"bulk": 0}

    def fake_http_json(url, headers, method="GET", body=None):
        if url.endswith("/entity/bulk"):
            calls["bulk"] += 1
            assert len(body["entities"]) <= 2
            mutated = [{"guid": f"g-{calls['bulk']}-{i}",
                       "attributes": {"qualifiedName": e["attributes"]["qualifiedName"]}}
                      for i, e in enumerate(body["entities"])]
            return {"mutatedEntities": {"CREATE": mutated, "UPDATE": []}}
        raise AssertionError(f"unexpected URL: {method} {url}")

    monkeypatch.setattr(pv, "_http_form", lambda url, form: {"access_token": "t"})
    monkeypatch.setattr(pv, "_http_json", fake_http_json)
    r = pv.push_catalog(cat, dic, dry_run=False)
    total_entities = len(cat) + len(dic)
    import math
    assert calls["bulk"] == math.ceil(total_entities / 2)
    assert r["entity_count"] == total_entities
    assert len(r["guid_by_qualified_name"]) == total_entities
    assert r["failed_batches"] == []


def test_purview_push_catalog_partial_batch_failure_does_not_abort_others(monkeypatch):
    monkeypatch.setenv("PURVIEW_TENANT_ID", "tid")
    monkeypatch.setenv("PURVIEW_CLIENT_ID", "cid")
    monkeypatch.setenv("PURVIEW_CLIENT_SECRET", "sec")
    monkeypatch.setenv("PURVIEW_ACCOUNT_NAME", "acct")
    import urllib.error
    from mvdg import purview_export as pv
    monkeypatch.setattr(pv, "_BULK_BATCH_SIZE", 2)
    cat, dic, _glo = _sample_gov_tables()

    calls = {"bulk": 0}

    def fake_http_json(url, headers, method="GET", body=None):
        calls["bulk"] += 1
        if calls["bulk"] == 1:
            raise urllib.error.HTTPError(url, 500, "boom", None, None)
        mutated = [{"guid": f"g-{i}", "attributes": {"qualifiedName": e["attributes"]["qualifiedName"]}}
                  for i, e in enumerate(body["entities"])]
        return {"mutatedEntities": {"CREATE": mutated, "UPDATE": []}}

    monkeypatch.setattr(pv, "_http_form", lambda url, form: {"access_token": "t"})
    monkeypatch.setattr(pv, "_http_json", fake_http_json)
    r = pv.push_catalog(cat, dic, dry_run=False)
    assert len(r["failed_batches"]) == 1
    assert calls["bulk"] > 1  # los lotes siguientes se mandaron igual
    assert len(r["guid_by_qualified_name"]) < r["entity_count"]  # el lote fallido no aportó guids


def test_purview_retries_429_with_backoff_then_succeeds(monkeypatch):
    from mvdg import purview_export as pv
    import urllib.error

    sleeps = []
    monkeypatch.setattr(pv.time, "sleep", lambda s: sleeps.append(s))

    attempts = {"n": 0}
    real_urlopen = pv.urllib.request.urlopen

    class FakeResp:
        def __init__(self, payload):
            self._payload = payload

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            import json as _json
            return _json.dumps(self._payload).encode()

    def fake_urlopen(req, timeout=None):
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise urllib.error.HTTPError(req.full_url, 429, "slow down",
                                         {"Retry-After": "0"}, None)
        return FakeResp({"ok": True})

    monkeypatch.setattr(pv.urllib.request, "urlopen", fake_urlopen)
    result = pv._http_json("http://x/y", {})
    assert result == {"ok": True}
    assert attempts["n"] == 2
    assert sleeps == [0.0]


def test_purview_429_gives_up_after_max_retries(monkeypatch):
    from mvdg import purview_export as pv
    import urllib.error
    monkeypatch.setattr(pv.time, "sleep", lambda s: None)
    attempts = {"n": 0}

    def always_429(req, timeout=None):
        attempts["n"] += 1
        raise urllib.error.HTTPError(req.full_url, 429, "slow down", {}, None)

    monkeypatch.setattr(pv.urllib.request, "urlopen", always_429)
    with pytest.raises(urllib.error.HTTPError):
        pv._http_json("http://x/y", {})
    assert attempts["n"] == pv._MAX_RETRIES_429 + 1  # intento original + reintentos


# ------------------------------------------------------------- Collibra: robustez
def test_collibra_column_table_relation_created_when_configured(monkeypatch):
    monkeypatch.setenv("COLLIBRA_BASE_URL", "https://acme.collibra.com")
    monkeypatch.setenv("COLLIBRA_USERNAME", "svc")
    monkeypatch.setenv("COLLIBRA_PASSWORD", "pw")
    monkeypatch.setenv("COLLIBRA_DOMAIN_ID", "dom-1")
    monkeypatch.setenv("COLLIBRA_TABLE_TYPE_ID", "type-table")
    monkeypatch.setenv("COLLIBRA_COLUMN_TYPE_ID", "type-column")
    monkeypatch.setenv("COLLIBRA_COLUMN_TABLE_RELATION_TYPE_ID", "rel-col-table")
    from mvdg import collibra_export as cb
    cat, dic, _glo = _sample_gov_tables()

    relations = []
    asset_ids = iter(range(10_000))

    def fake_http_json(url, headers, method="GET", body=None):
        if url.endswith("/auth/sessions") and method == "POST":
            return {}, ["JSESSIONID=abc123; Path=/"]
        if url.endswith("/auth/sessions/current"):
            return {}, []
        if url.endswith("/assets"):
            return {"id": f"asset-{next(asset_ids)}"}, []
        if url.endswith("/attributes"):
            return {"id": "attr-1"}, []
        if url.endswith("/relations") and method == "POST":
            relations.append(body)
            return {"id": "rel-1"}, []
        raise AssertionError(f"unexpected URL: {url}")

    monkeypatch.setattr(cb, "_http_json", fake_http_json)
    r = cb.push_catalog(cat, dic, dry_run=False)
    assert r["asset_count"] == len(cat) + len(dic)
    assert len(relations) == len(dic)               # una relación por columna
    assert all(rel["typeId"] == "rel-col-table" for rel in relations)
    assert r["failed"] == []

    # sin la env var: mismo push, cero llamadas a /relations (no regresión)
    monkeypatch.delenv("COLLIBRA_COLUMN_TABLE_RELATION_TYPE_ID")
    relations.clear()
    cb.push_catalog(cat, dic, dry_run=False)
    assert relations == []


def test_collibra_push_partial_failure_isolated_per_item(monkeypatch):
    monkeypatch.setenv("COLLIBRA_BASE_URL", "https://acme.collibra.com")
    monkeypatch.setenv("COLLIBRA_USERNAME", "svc")
    monkeypatch.setenv("COLLIBRA_PASSWORD", "pw")
    monkeypatch.setenv("COLLIBRA_DOMAIN_ID", "dom-1")
    monkeypatch.setenv("COLLIBRA_TABLE_TYPE_ID", "type-table")
    monkeypatch.setenv("COLLIBRA_COLUMN_TYPE_ID", "type-column")
    import urllib.error
    from mvdg import collibra_export as cb
    cat, dic, _glo = _sample_gov_tables()
    bad_dataset = cat.iloc[0]["dataset"]

    def fake_http_json(url, headers, method="GET", body=None):
        if url.endswith("/auth/sessions") and method == "POST":
            return {}, ["JSESSIONID=abc123; Path=/"]
        if url.endswith("/auth/sessions/current"):
            return {}, []
        if url.endswith("/assets"):
            if body.get("name") == bad_dataset:
                raise urllib.error.HTTPError(url, 500, "boom", None, None)
            return {"id": "asset-ok"}, []
        if url.endswith("/attributes"):
            return {"id": "attr-1"}, []
        raise AssertionError(f"unexpected URL: {url}")

    monkeypatch.setattr(cb, "_http_json", fake_http_json)
    r = cb.push_catalog(cat, dic, dry_run=False)
    assert len(r["failed"]) == 1
    assert r["failed"][0]["name"] == bad_dataset
    # el resto de los assets (otras tablas + todas las columnas) sí se crearon
    assert r["asset_count"] == len(cat) + len(dic) - 1


def test_collibra_term_status_reflects_curation(tmp_path, monkeypatch):
    """statusId Candidate/Accepted en Collibra tiene que salir de la
    curaduría real, igual que Draft/Approved en Purview."""
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    from mvdg import collibra_export as cb, curation
    _cat, _dic, glo = _sample_gov_tables()

    def lookup(term_id):
        rec = curation.get_record(f"glossary:demo:{term_id}", "es")
        return (rec["status"], rec.get("text") or "") if rec else ("sugerido_ia", "")

    before = cb.build_term_payloads(glo, "term-type", "dom-1", curation_lookup=lookup)
    assert all(t["asset"]["statusId"] == cb._DEFAULT_CANDIDATE_STATUS_ID for t in before)

    first_term_id = glo.iloc[0]["term_id"]
    curation.save_validation(f"glossary:demo:{first_term_id}", "es", "validado",
                             "", "María Viera", "Data Owner")
    after = cb.build_term_payloads(glo, "term-type", "dom-1", curation_lookup=lookup)
    statuses = {t["asset"]["name"]: t["asset"]["statusId"] for t in after}
    approved_name = glo.iloc[0]["term"]
    assert statuses[approved_name] == cb._DEFAULT_ACCEPTED_STATUS_ID
    assert sum(1 for s in statuses.values() if s == cb._DEFAULT_ACCEPTED_STATUS_ID) == 1


def test_collibra_status_ids_are_documented_and_overridable(monkeypatch):
    from mvdg import collibra_export as cb
    assert cb._DEFAULT_CANDIDATE_STATUS_ID == "00000000-0000-0000-0000-000000005008"
    assert cb._DEFAULT_ACCEPTED_STATUS_ID == "00000000-0000-0000-0000-000000005009"
    monkeypatch.setenv("COLLIBRA_CANDIDATE_STATUS_ID", "custom-candidate")
    _cat, _dic, glo = _sample_gov_tables()
    terms = cb.build_term_payloads(glo, "term-type", "dom-1")
    assert terms[0]["asset"]["statusId"] == "custom-candidate"


# ------------------------------------ glosario automático desde la base de datos
def test_glossary_auto_expands_common_abbreviations():
    from mvdg.glossary_auto import expand_identifier
    assert expand_identifier("fec_pag", "es") == ("fecha pago", True)
    assert expand_identifier("cli_id", "es") == ("cliente identificador", True)
    assert expand_identifier("imp_tot", "es") == ("importe total", True)
    assert expand_identifier("cust_addr", "en") == ("customer address", True)
    # camelCase también se parte y expande
    assert expand_identifier("fecPago", "es")[0].startswith("fecha")


def test_glossary_auto_never_invents_unknown_tokens():
    """Un token que no está en el diccionario queda tal cual (en minúsculas)
    — la corrección es del humano en la tabla editable, no una invención."""
    from mvdg.glossary_auto import expand_identifier
    phrase, expanded = expand_identifier("xyzzy_frobnicate", "es")
    assert phrase == "xyzzy frobnicate"
    assert expanded is False


def test_glossary_auto_terms_have_stable_upsert_ids():
    from mvdg.glossary_auto import build_terms_from_schema
    schema = {"cli_fac": ["fec_pag", "imp_tot"]}
    terms = build_terms_from_schema(schema, "es", conn_id="abc123")
    ids = {t["database_id"] for t in terms}
    assert ids == {"abc123:cli_fac.fec_pag", "abc123:cli_fac.imp_tot"}
    # re-generar produce los mismos ids -> save_terms hace upsert, no duplica
    again = {t["database_id"] for t in build_terms_from_schema(schema, "es", conn_id="abc123")}
    assert again == ids


def test_glossary_auto_end_to_end_with_real_sqlite(tmp_path, monkeypatch):
    """Flujo completo contra una base REAL (SQLite): esquema con nombres
    abreviados -> borrador con palabras completas -> guardado local ->
    aparece en 🖊️ Curaduría con su origen, editable/validable a mano."""
    import sqlite3
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    db = tmp_path / "ventas.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE cli_fac (fec_pag TEXT, imp_tot REAL, tel_cli TEXT)")
    con.commit(); con.close()

    from mvdg import curation, glossary_auto, imported
    profile = {"conn_id": "sqlt1", "engine": "sqlite", "database": str(db)}
    draft = glossary_auto.build_from_connection(profile, "es")
    by_col = {t["column"]: t for t in draft}
    assert by_col["fec_pag"]["name"] == "fecha pago"
    assert by_col["imp_tot"]["name"] == "importe total"
    assert by_col["tel_cli"]["name"] == "teléfono cliente"
    assert all(t["definition"] for t in draft)

    # el usuario corrige uno a mano antes de guardar (editable de verdad)
    by_col["tel_cli"]["name"] = "teléfono del cliente"
    n = imported.save_terms("database", draft)
    assert n == 3
    df = curation.list_items("es")
    row = df[df["item_id"] == "glossary:imported:database:sqlt1:cli_fac.tel_cli"]
    assert len(row) == 1
    assert row.iloc[0]["label"] == "teléfono del cliente"
    assert row.iloc[0]["dataset"] == "🗄️ base de datos"
    assert row.iloc[0]["status"] == "sugerido_ia"
    # y se valida/modifica como cualquier otra definición del programa
    curation.save_validation("glossary:imported:database:sqlt1:cli_fac.tel_cli",
                             "es", "modificado", "Teléfono de contacto del cliente.",
                             "M. Viera", "Data Steward")
    df2 = curation.list_items("es")
    row2 = df2[df2["item_id"] == "glossary:imported:database:sqlt1:cli_fac.tel_cli"]
    assert row2.iloc[0]["status"] == "modificado"
    assert row2.iloc[0]["text"] == "Teléfono de contacto del cliente."


def test_glossary_auto_broken_table_does_not_stop_the_rest(tmp_path, monkeypatch):
    from mvdg import connectors, glossary_auto
    import sqlite3
    db = tmp_path / "x.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE ok_tbl (cod_prod TEXT)")
    con.commit(); con.close()
    profile = {"conn_id": "c1", "engine": "sqlite", "database": str(db)}

    real_list_columns = connectors.list_columns

    def flaky(prof, table, password=None):
        if table == "ok_tbl":
            return real_list_columns(prof, table, password=password)
        raise RuntimeError("boom")

    monkeypatch.setattr(connectors, "list_tables", lambda p, password=None: ["rota", "ok_tbl"])
    monkeypatch.setattr(connectors, "list_columns", flaky)
    terms = glossary_auto.build_from_connection(profile, "es")
    assert [t["column"] for t in terms] == ["cod_prod"]
    assert terms[0]["name"] == "código producto"
