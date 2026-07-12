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

    @check("Conectores a base de datos")
    def _():
        from .connectors import ENGINES, test_connection
        assert {"postgresql", "mysql", "sqlserver", "oracle", "sqlite"} <= set(ENGINES)
        ok, _msg = test_connection({"engine": "sqlite", "database": ":memory:"})
        assert ok
        return f"{len(ENGINES)} motores (SQLite verificado)"

    @check("Centro de ayuda (speeches IA)")
    def _():
        from .help_center import SPEECHES, automation_rows
        assert len(SPEECHES) == 5 and len(automation_rows("es")) >= 6
        return f"{len(SPEECHES)} speeches, matriz de automatización"

    @check("API REST importable")
    def _():
        from api.main import TABLES, app  # noqa: F401
        assert len(TABLES) == 9
        return f"FastAPI OK, {len(TABLES)} endpoints"

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
