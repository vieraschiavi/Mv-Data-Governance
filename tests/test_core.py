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
    assert set(body["samples"]) == {"rotulado_alimentos", "cafe_sales_kaggle", "bank_marketing_uci"}

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


def test_powerbi_source_label_heuristics():
    from mvdg.powerbi_meta import _source_label_from_mquery
    assert _source_label_from_mquery('Source = Sql.Database("Srv", "Db")') == "SQL Server · Srv/Db"
    assert _source_label_from_mquery('Source = Sql.Databases("Srv")') == "SQL Server · Srv"
    assert _source_label_from_mquery('Value.NativeQuery(Source, "SELECT 1")') == \
        "SQL (consulta nativa · Value.NativeQuery)"
    assert _source_label_from_mquery('Source = Excel.Workbook(File.Contents("x.xlsx"))') == "Power Query · Excel.Workbook"
    assert _source_label_from_mquery('no hay ninguna funcion m aca') is None


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
