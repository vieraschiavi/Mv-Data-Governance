"""
MV Data Governance · API REST para herramientas de BI.

Sirve todas las tablas de gobierno en JSON (default) o CSV (``?format=csv``)
para que Power BI, Tableau, Looker, MicroStrategy, Qlik o Excel las consuman
como origen de datos web. Documentación interactiva en ``/docs``.

Levantar:
    python -m api.main            # http://127.0.0.1:8600
    MVDG_API_PORT=9000 python -m api.main
"""
from __future__ import annotations

import json
import os

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from mvdg import APP_NAME, __version__
from mvdg.exporters import governance_tables
from mvdg.i18n import LANGS
from mvdg.samples import sample_governance_tables, sample_keys, sample_meta

DEFAULT_PORT = 8600

app = FastAPI(
    title=f"{APP_NAME} API",
    version=__version__,
    description=(
        "API de gobierno de datos para BI · Data governance API for BI · "
        "API de governança de dados para BI. "
        "Tablas: catalog, dictionary, quality_results, quality_by_dataset, "
        "quality_by_dimension, lineage, glossary, policies, kpis. "
        "Datasets de ejemplo externos (reales), gobernados de punta a punta, "
        "en /api/samples/{dataset}/{table}."
    ),
)
# BI tools (Power BI service, Tableau, browsers) llaman desde otros orígenes.
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["GET"], allow_headers=["*"])

TABLES = ["catalog", "dictionary", "quality_results", "quality_by_dataset",
          "quality_by_dimension", "lineage", "glossary", "policies", "kpis"]
SAMPLE_TABLES = ["data", "dictionary", "quality_results", "glossary"]


@app.get("/", tags=["meta"])
def root():
    return {
        "app": APP_NAME,
        "version": __version__,
        "languages": LANGS,
        "tables": TABLES,
        "samples": sample_keys(),
        "sample_tables": SAMPLE_TABLES,
        "how_to": {
            "json": "/api/{table}?lang=es|en|pt",
            "csv": "/api/{table}?lang=es&format=csv",
            "samples_json": "/api/samples/{dataset}/{table}?lang=es|en|pt",
            "samples_csv": "/api/samples/{dataset}/{table}?lang=es&format=csv",
            "docs": "/docs",
        },
    }


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


def _serve(df, table: str, lang: str, format: str):
    if format == "csv":
        return PlainTextResponse(df.to_csv(index=False),
                                 media_type="text/csv; charset=utf-8")
    # to_json→loads normaliza tipos numpy y convierte NaN/NaT en null,
    # garantizando JSON estricto para cualquier cliente BI.
    records = json.loads(df.to_json(orient="records", date_format="iso"))
    return {"table": table, "lang": lang, "rows": len(df), "data": records}


@app.get("/api/{table}", tags=["governance"])
def get_table(
    table: str,
    lang: str = Query("es", pattern="^(es|en|pt)$"),
    format: str = Query("json", pattern="^(json|csv)$"),
):
    """Devuelve una tabla de gobierno en el idioma pedido, en JSON o CSV."""
    if table not in TABLES:
        raise HTTPException(404, f"Tabla desconocida: {table}. Disponibles: {TABLES}")
    df = governance_tables(lang)[table]
    return _serve(df, table, lang, format)


@app.get("/api/samples/{dataset}/{table}", tags=["samples"])
def get_sample_table(
    dataset: str,
    table: str,
    lang: str = Query("es", pattern="^(es|en|pt)$"),
    format: str = Query("json", pattern="^(json|csv)$"),
):
    """Un dataset de ejemplo externo (real), gobernado de punta a punta:
    datos crudos, diccionario, resultados de calidad (reglas con umbral y
    estado) y glosario — pensado para conectar Power BI, Tableau o cualquier
    BI directamente a un caso real, no solo a la demo sintética."""
    if dataset not in sample_keys():
        raise HTTPException(404, f"Dataset desconocido: {dataset}. Disponibles: {sample_keys()}")
    if table not in SAMPLE_TABLES:
        raise HTTPException(404, f"Tabla desconocida: {table}. Disponibles: {SAMPLE_TABLES}")
    df = sample_governance_tables(dataset, lang)[table]
    return _serve(df, table, lang, format)


@app.get("/api/samples/{dataset}", tags=["samples"])
def get_sample_meta(dataset: str, lang: str = Query("es", pattern="^(es|en|pt)$")):
    """Ficha del dataset de ejemplo: nombre, dominio, dueño, steward,
    clasificación, fuente/licencia y las tablas disponibles."""
    if dataset not in sample_keys():
        raise HTTPException(404, f"Dataset desconocido: {dataset}. Disponibles: {sample_keys()}")
    meta = sample_meta(dataset, lang)
    meta["tables"] = SAMPLE_TABLES
    return meta


def main():
    port = int(os.environ.get("MVDG_API_PORT", DEFAULT_PORT))
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")


if __name__ == "__main__":
    main()
