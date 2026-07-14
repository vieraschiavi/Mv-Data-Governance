"""
MV Data Governance · Auto-diagnóstico (health check).

Verifica en segundos que la instalación esté 100% operativa: dependencias,
motor de reglas, i18n trilingüe, catálogo, linaje, exportadores y API. Pensado
para que el usuario (o TI del cliente) confirme que todo funciona antes de
mostrar la demo.

Uso:
    python -m mvdg.selfcheck
Devuelve código de salida 0 si todo pasa, 1 si algo falla.
"""
from __future__ import annotations

import importlib
import sys


def run_checks() -> list[tuple[str, bool, str]]:
    """Ejecuta todos los chequeos y devuelve (nombre, ok, detalle)."""
    results: list[tuple[str, bool, str]] = []

    def check(name):
        def deco(fn):
            try:
                detail = fn()
                results.append((name, True, detail))
            except Exception as exc:  # noqa: BLE001 - reportamos cualquier fallo
                results.append((name, False, f"{type(exc).__name__}: {exc}"))
        return deco

    @check("Dependencias (pandas, plotly, streamlit, fastapi)")
    def _():
        for mod in ("pandas", "numpy", "plotly", "streamlit", "fastapi"):
            importlib.import_module(mod)
        return "todas presentes"

    @check("i18n trilingüe (paridad ES/EN/PT)")
    def _():
        from .i18n import LANGS, _T
        faltan = [(k, lang) for k, e in _T.items()
                  for lang in LANGS if not e.get(lang)]
        if faltan:
            raise AssertionError(f"faltan {len(faltan)} traducciones")
        return f"{len(_T)} claves × {len(LANGS)} idiomas"

    @check("Datos de demo (deterministas)")
    def _():
        from .demo_data import load_demo_tables
        t = load_demo_tables()
        assert set(t) == {"dim_customers", "dim_products", "fct_sales", "fct_payments"}
        return f"{len(t)} datasets, {sum(len(v) for v in t.values())} filas"

    @check("Motor de calidad (17 reglas, 6 dimensiones)")
    def _():
        from .quality import DIMENSIONS, RULES, overall_index, run_rules
        res = run_rules()
        assert {r.dimension for r in RULES} == set(DIMENSIONS)
        idx = overall_index(res)
        assert 0 < idx <= 100
        return f"{len(RULES)} reglas, índice {idx}"

    @check("Catálogo y PII")
    def _():
        from .catalog import catalog_df, pii_columns
        assert len(catalog_df("es")) == 4
        return f"{len(pii_columns())} columnas PII marcadas"

    @check("Linaje (grafo consistente)")
    def _():
        from .lineage import EDGES, NODES, downstream
        ids = {n["id"] for n in NODES}
        assert all(a in ids and b in ids for a, b in EDGES)
        assert "bi_dashboard" in downstream("crm")
        return f"{len(NODES)} nodos, {len(EDGES)} aristas"

    @check("Glosario y políticas")
    def _():
        from .glossary import term_count
        from .policies import policies_df
        assert len(policies_df("es")) == 6
        return f"{term_count()} términos, 6 políticas"

    @check("Exportadores (CSV/Excel/JSON/Parquet)")
    def _():
        from .exporters import (bi_bundle_xlsx, governance_tables,
                                to_csv_bytes, to_parquet_bytes)
        tabs = governance_tables("es")
        assert len(tabs) == 9
        assert to_csv_bytes(tabs["catalog"]).startswith(b"dataset".decode().encode("utf-8-sig"))
        assert bi_bundle_xlsx("es")[:2] == b"PK"
        pq = "sí" if to_parquet_bytes(tabs["kpis"]) else "no disponible"
        return f"{len(tabs)} tablas · Parquet: {pq}"

    @check("Fichas de empresas (persistencia)")
    def _():
        from .clients import recommended_pack
        assert recommended_pack("exe_ok") == "A"
        return "CRM de clientes operativo"

    @check("Conectores a base de datos (SQL + cloud DW/lake)")
    def _():
        from .connectors import CLOUD_ENGINES, ENGINES, build_url, test_connection
        assert {"postgresql", "mysql", "sqlserver", "oracle", "sqlite",
               "synapse", "snowflake", "bigquery", "databricks"} <= set(ENGINES)
        ok, _msg = test_connection({"engine": "sqlite", "database": ":memory:"})
        assert ok
        # build_url() de los 3 motores cloud: lógica pura, sin conexión real
        # (no probado contra una cuenta real de Snowflake/BigQuery/Databricks
        # en este entorno — ver docs/CLOUD_CONNECTORS.md)
        for eng in CLOUD_ENGINES:
            url = str(build_url({"engine": eng, "extra": {
                "account": "acc", "warehouse": "wh", "role": "r", "schema": "s",
                "project": "p", "dataset": "d", "server_hostname": "h", "http_path": "/x",
                "catalog": "c",
            }, "database": "db", "user": "u"}, password="pw"))
            assert url.startswith(eng if eng != "bigquery" else "bigquery")
        return f"{len(ENGINES)} motores ({len(CLOUD_ENGINES)} cloud DW/lake), SQLite verificado"

    @check("Centro de ayuda (speeches IA)")
    def _():
        from .help_center import SPEECHES, automation_rows
        assert len(SPEECHES) == 5 and len(automation_rows("es")) >= 6
        return f"{len(SPEECHES)} speeches, matriz de automatización"

    @check("Tutorial DAMA-DMBOK (11 áreas + teoría)")
    def _():
        from . import dmbok
        assert len(dmbok.areas("es")) == 11
        assert len(dmbok.principles("es")) == 6
        assert len(dmbok.concepts("es")) >= 12
        assert len(dmbok.maturity("es")) == 5 and len(dmbok.lifecycle("es")) == 6
        cov = dmbok.coverage_summary()
        assert cov["covered"] + cov["partial"] + cov["out"] == 11
        return (f"11 áreas, {len(dmbok.concepts('es'))} conceptos, "
                f"{cov['covered']} cubiertas / {cov['partial']} parciales")

    @check("Referencia COBIT 2019 + ISO/IEC 38505")
    def _():
        from . import cobit_iso as ci
        for lang in ("es", "en", "pt"):
            assert len(ci.cobit_objectives(lang)) == 8
            assert len(ci.iso_principles(lang)) == 6
            assert len(ci.iso_vrc(lang)) == 3
        ccov = ci.cobit_coverage_summary()
        icov = ci.iso_coverage_summary()
        assert ccov["covered"] + ccov["partial"] + ccov["out"] == 8
        assert icov["covered"] + icov["partial"] + icov["out"] == 6
        return (f"COBIT: 8 objetivos ({ccov['covered']} cubiertos) · "
               f"ISO 38505: 6 principios ({icov['covered']} cubiertos) + modelo VRC")

    @check("MDM: duplicados + golden record (probado contra la demo real)")
    def _():
        from . import mdm
        from .demo_data import load_demo_tables
        df = load_demo_tables()["dim_customers"]
        rules = mdm.suggest_rules(df, ["document_id", "email", "full_name", "birth_date"])
        clusters = mdm.find_duplicate_clusters(df, rules, min_confidence=0.5, block_column="country")
        assert len(clusters) == 8, "la demo trae 8 colisiones reales de document_id/email"
        assert all(c.confidence == 1.0 for c in clusters)
        # anti falso-positivo: "Ana Costa" x4 personas distintas no debe aparecer
        ana_ids = set(df.loc[df["full_name"] == "Ana Costa", "customer_id"])
        flagged = {df.loc[i, "customer_id"] for c in clusters for i in c.row_indices}
        assert not (ana_ids & flagged), "nombre común sin ID/email coincidente no debe marcarse"
        golden = mdm.build_golden_record(df, clusters[0])
        assert all(golden.values())
        return f"{len(clusters)} clusters reales detectados, 0 falsos positivos por nombre común"

    @check("API REST importable")
    def _():
        from bi_api.main import SAMPLE_TABLES, TABLES, app  # noqa: F401
        assert len(TABLES) == 9
        assert len(SAMPLE_TABLES) == 4
        return f"FastAPI OK, {len(TABLES)} tablas + {len(SAMPLE_TABLES)} tablas por dataset de ejemplo"

    @check("Modo servidor web (hosts autorizados)")
    def _():
        from .server import (authorization_status, parse_authorized,
                             run_server)
        assert authorization_status([])["mode"] == "open"
        assert authorization_status(["*"])["mode"] == "authorized"
        assert authorization_status(["nope"], identities={"x"})["mode"] == "denied"
        assert parse_authorized("a, b\n# comentario, con coma\nd") == ["a", "b", "d"]
        argv: list = []
        run_server(argv_out=argv)  # dry-run: no lanza el servidor
        assert "--server.address" in argv and "--server.port" in argv
        return "autorización por host + arranque server OK"

    @check("Dataset de ejemplo real (rotulado de alimentos)")
    def _():
        import os
        import pandas as pd
        from .profiler import profile_table, summary
        root = getattr(sys, "_MEIPASS", None) or os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(root, "assets", "samples",
                            "rotulado_de_alimentos_2026.csv")
        assert os.path.exists(path), "falta el CSV de ejemplo"
        df = pd.read_csv(path)
        info = summary(df)
        assert info["rows"] == 284 and info["columns"] == 12
        assert len(profile_table(df)) == 12
        return f"{info['rows']} filas × {info['columns']} columnas perfiladas"

    @check("IA externa opcional (apagada por defecto, con fallback local)")
    def _():
        import os
        from . import ai_provider
        # verificamos el comportamiento por defecto (sin keys) sin alterar
        # una configuracion real del usuario mas alla de la duracion del check
        saved = {v: os.environ.pop(v, None) for v in
                ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "MVDG_AI_PROVIDER")}
        try:
            assert ai_provider.configured_provider() is None
            assert ai_provider.ai_suggest_fix("ds", "col", "completeness", "desc", 1, "es") is None
        finally:
            for k, v in saved.items():
                if v is not None:
                    os.environ[k] = v
        return "sin API key configurada -> asistencia local (comportamiento por defecto verificado)"

    @check("Sugerencias de correccion (IA) para cada falla detectada")
    def _():
        from . import quality, samples
        from .remediation import suggest_fix
        n_checked = 0
        for r in quality.RULES:
            for lang in ("es", "en", "pt"):
                fix = suggest_fix(r.rule_id, r.dimension, r.column, 12, lang)
                assert all(fix.values()), r.rule_id
                n_checked += 1
        for key in samples.sample_keys():
            for r in samples.SAMPLES[key]["rules"]:
                for lang in ("es", "en", "pt"):
                    fix = suggest_fix(r.rule_id, r.dimension, r.column, 5, lang)
                    assert all(fix.values()), r.rule_id
                    n_checked += 1
        # regla desconocida -> repuesto generico, no debe romper
        generic = suggest_fix("ZZZ-99", "completeness", "col_x", 3, "es")
        assert all(generic.values())
        return f"{n_checked} combinaciones regla×idioma con sugerencia completa"

    @check("Datasets de ejemplo gobernados de punta a punta (catálogo+reglas+glosario+BI)")
    def _():
        from . import samples
        keys = samples.sample_keys()
        assert len(keys) >= 2
        total_rows = 0
        for key in keys:
            for lang in ("es", "en", "pt"):
                meta = samples.sample_meta(key, lang)
                assert meta["name"] and meta["owner"] and meta["steward"]
                results = samples.sample_quality_results(key, lang)
                assert len(results) >= 5
                gloss = samples.sample_glossary_df(key, lang)
                assert len(gloss) >= 3
            gov = samples.sample_governance_tables(key, "es")
            assert set(gov) == {"data", "dictionary", "quality_results", "glossary"}
            total_rows += len(gov["data"])
        return f"{len(keys)} datasets, {total_rows:,} filas gobernadas (catálogo, reglas, glosario, BI)"

    @check("Conector de metadata Power BI (.pbip -> catálogo+linaje SQL->reporte+DAX)")
    def _():
        import os
        import tempfile
        from . import powerbi_meta as pbi

        root = os.path.join(tempfile.mkdtemp(prefix="mvdg_selfcheck_pbip_"), "Demo.SemanticModel")
        dfn = os.path.join(root, "definition")
        os.makedirs(os.path.join(dfn, "tables"))
        with open(os.path.join(dfn, "tables", "Ventas.tmdl"), "w", encoding="utf-8") as fh:
            fh.write(
                "table Ventas\n"
                "\tmeasure Total = SUM ( Ventas[Monto] )\n"
                "\tcolumn Monto\n"
                "\t\tdataType: double\n"
                "\tpartition Ventas = m\n"
                "\t\tsource =\n"
                "\t\t\tlet\n"
                "\t\t\t\tSource = Sql.Database(\"Srv\", \"Db\")\n"
                "\t\t\tin\n"
                "\t\t\t\tSource\n"
            )
        out = pbi.ingest_pbip(root)
        model = out["_model"]
        assert model.table_sources.get("Ventas") == "SQL Server · Srv/Db"
        chain = out["lineage"]
        assert (chain["source_layer"] == "source").any(), "falta el tramo SQL -> tabla"
        assert (chain["target_layer"] == "bi").any(), "falta el tramo dataset -> reporte"
        assert set(out) >= {"catalog", "dictionary", "glossary", "lineage", "quality", "sources"}
        return "SQL Server -> tabla -> dataset -> reporte, cableado end-to-end (offline, sin filas)"

    @check("Power BI tenant-wide (Scanner API, apagado por defecto, con mock del transporte)")
    def _():
        import os
        from unittest import mock

        from . import powerbi_meta as pbi

        saved = {v: os.environ.pop(v, None) for v in
                ("POWERBI_TENANT_ID", "POWERBI_CLIENT_ID", "POWERBI_CLIENT_SECRET")}
        try:
            assert pbi.tenant_configured() is False
            try:
                pbi.read_scanner()
                raise AssertionError("read_scanner() debería fallar sin credenciales")
            except RuntimeError:
                pass

            def fake_form(url, form):
                return {"access_token": "tok"}

            def fake_json(url, headers, method="GET", body=None):
                if "admin/groups" in url:
                    return {"value": [{"id": "ws-1", "name": "Demo"}]}
                if "getInfo" in url:
                    return {"id": "scan-1"}
                if "scanStatus" in url:
                    return {"status": "Succeeded"}
                if "scanResult" in url:
                    return {"workspaces": [{"name": "Demo", "datasets": [{
                        "id": "ds-1", "name": "VentasDemo",
                        "tables": [{"name": "Ventas",
                                   "columns": [{"name": "Monto", "dataType": "double"}],
                                   "measures": [{"name": "Total", "expression": "SUM(Ventas[Monto])"}],
                                   "source": [{"expression": 'Sql.Database("Srv","Db")'}]}]}],
                        "reports": [{"name": "Rep", "datasetId": "ds-1"}]}]}
                raise AssertionError(url)

            with mock.patch.object(pbi, "_http_form", fake_form), \
                mock.patch.object(pbi, "_http_json", fake_json):
                out = pbi.ingest_tenant(tenant_id="t", client_id="c", client_secret="s")
            assert len(out["_models"]) == 1
            assert out["_models"][0].table_sources.get("Ventas") == "SQL Server · Srv/Db"
        finally:
            for k, v in saved.items():
                if v is not None:
                    os.environ[k] = v
        return "sin credenciales -> RuntimeError; con credenciales (mock) -> tenant escaneado end-to-end"

    @check("Tableau Metadata API (apagado por defecto, con mock del transporte)")
    def _():
        import os
        from unittest import mock

        from . import tableau_meta as tabl

        saved = {v: os.environ.pop(v, None) for v in
                ("TABLEAU_SERVER_URL", "TABLEAU_TOKEN_NAME", "TABLEAU_TOKEN_SECRET")}
        try:
            assert tabl.configured() is False
            try:
                tabl.read_site()
                raise AssertionError("read_site() debería fallar sin credenciales")
            except RuntimeError:
                pass

            def fake_json(url, headers, method="GET", body=None):
                if url.endswith("/auth/signin"):
                    return {"credentials": {"token": "sess", "site": {"id": "s1"}}}
                if url.endswith("/auth/signout"):
                    return {}
                if url.endswith("/api/metadata/graphql"):
                    return {"data": {"workbooks": [{"name": "WB", "projectName": "P",
                        "upstreamDatasources": [{"name": "DS",
                            "fields": [{"name": "Margen", "description": "",
                                       "formula": "SUM([X])/SUM([Y])"}],
                            "upstreamTables": [{"name": "ventas", "schema": "dbo",
                                               "database": {"connectionType": "sqlserver"}}]}]}]}}
                raise AssertionError(url)

            with mock.patch.object(tabl, "_http_json", fake_json):
                out = tabl.ingest_site(server="https://t.example.com",
                                       token_name="n", token_secret="s")
            assert out["_model"].workbooks == ["WB"]
            assert len(out["glossary"]) == 1
        finally:
            for k, v in saved.items():
                if v is not None:
                    os.environ[k] = v
        return "sin credenciales -> RuntimeError; con credenciales (mock) -> sitio escaneado end-to-end"

    @check("Ejemplos incluidos de Power BI (real, GitHub MIT) y Tableau (original)")
    def _():
        from . import powerbi_meta as pbi
        from . import tableau_meta as tabl

        pbi_out = pbi.ingest_example()
        pbi_model = pbi_out["_model"]
        assert len(pbi_model.tables) == 10 and len(pbi_model.measures) == 17
        assert all(m.description for m in pbi_model.measures), "descripciones /// no se capturaron"

        tenant_out = pbi.ingest_example_tenant()
        assert len(tenant_out["_models"]) == 4
        assert all("ilustrativo" in m.source.lower() for m in tenant_out["_models"])

        tab_out = tabl.ingest_example()
        tab_model = tab_out["_model"]
        assert tab_model.workbooks == ["VentasGlobalDemo"]
        assert sum(1 for f in tab_model.fields if f.is_calculated) == 3

        return (f"Power BI: {len(pbi_model.tables)} tablas reales (MIT) + 4 workspaces "
               f"ilustrativos · Tableau: {len(tab_model.workbooks)} workbook original, "
               f"{len(tab_model.datasources)} datasources")

    @check("Lanzadores de las 3 versiones (.exe / .bat / web)")
    def _():
        import os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        launchers = ["MV_DataGovernance.bat", "MV_DataGovernance_Server.bat",
                     "run.sh", "run_server.sh",
                     os.path.join("packaging", "mvdg_launcher.py"),
                     os.path.join("packaging", "mvdg.spec")]
        missing = [f for f in launchers if not os.path.exists(os.path.join(root, f))]
        assert not missing, f"faltan lanzadores: {missing}"
        return ".exe (PyInstaller) · .bat portable · web servidor — presentes"

    @check("Dashboard importable (sin errores)")
    def _():
        import importlib
        importlib.import_module("app.app")
        return "app/app.py carga sin errores"

    return results


def main() -> int:
    print("\n  MV Data Governance · Auto-diagnóstico\n" + "  " + "─" * 44)
    results = run_checks()
    ok_all = True
    for name, ok, detail in results:
        mark = "✓" if ok else "✗"
        print(f"  {mark} {name}")
        print(f"      {detail}")
        ok_all &= ok
    print("  " + "─" * 44)
    passed = sum(1 for _, ok, _ in results if ok)
    if ok_all:
        print(f"  ✅ 100% operativo — {passed}/{len(results)} chequeos OK.\n")
        return 0
    print(f"  ⚠️  {passed}/{len(results)} OK — revisá los ítems con ✗ arriba.\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
