"""
MV Data Governance · API REST para herramientas de BI.

Sirve todas las tablas de gobierno en JSON (default) o CSV (``?format=csv``)
para que Power BI, Tableau, Looker, MicroStrategy, Qlik o Excel las consuman
como origen de datos web. Documentación interactiva en ``/docs``.

Levantar:
    python -m bi_api.main            # http://127.0.0.1:8600
    MVDG_API_PORT=9000 python -m bi_api.main
"""
from __future__ import annotations

import hmac
import json
import os
import socket
import sys
import threading
import time
from collections import deque

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

from mvdg import APP_NAME, __version__
from mvdg.exporters import governance_tables
from mvdg.i18n import LANGS
from mvdg.samples import sample_governance_tables, sample_keys, sample_meta

DEFAULT_PORT = 8600

# --------------------------------------------------------------- seguridad
# Esta API sirve metadatos de gobierno (catálogo, calidad, glosario). Por
# defecto escucha SOLO en 127.0.0.1, así que no queda expuesta a internet a
# menos que alguien la publique a propósito. Aun así, tres controles:
#
#   1) Rate limiting SIEMPRE activo (defensa contra un cliente BI en loop o
#      una pestaña del navegador martillando el puerto local).
#   2) Token opcional en localhost, OBLIGATORIO si se publica fuera de
#      loopback — mismo criterio de "falla cerrado" que mvdg/server.py.
#   3) CORS sin comodín por defecto: un `allow_origins=["*"]` en un puerto
#      local significa que CUALQUIER web que visites puede leer tus tablas
#      de gobierno desde el navegador. Se puede ampliar por variable de
#      entorno para el Power BI service, pero no viene abierto de fábrica.
#
# Nada de esto necesita una dependencia nueva ni cambia las URLs que
# docs/BI_INTEGRATION.md ya documenta para Power BI / Tableau / Excel.

# Ventana de rate limit: 240 req/min por IP. Un refresh de Power BI baja 9
# tablas; Tableau y Excel son parecidos. 240 deja margen de sobra para un
# refresh manual repetido y aun así corta un loop descontrolado.
RATE_LIMIT_REQUESTS = int(os.environ.get("MVDG_API_RATE_LIMIT", "240"))
RATE_LIMIT_WINDOW_S = 60.0
# Rutas que no consumen cuota: son las que un BI usa para "ping".
RATE_LIMIT_EXEMPT = frozenset({"/health"})

_rate_lock = threading.Lock()
_rate_hits: dict[str, deque] = {}


def _api_token() -> str:
    """Token compartido. Vacío = sin login (solo aceptable en loopback)."""
    return os.environ.get("MVDG_API_TOKEN", "").strip()


def _is_loopback(host: str) -> bool:
    return host in ("127.0.0.1", "::1", "localhost")


def _rate_limited(client_ip: str) -> bool:
    """Ventana deslizante por IP, en memoria del proceso.

    Sin dependencia externa a propósito: un solo proceso uvicorn sirve esta
    API, así que un contador en memoria es exacto para este despliegue."""
    if RATE_LIMIT_REQUESTS <= 0:          # 0 = desactivado explícitamente
        return False
    ahora = time.monotonic()
    with _rate_lock:
        hits = _rate_hits.setdefault(client_ip, deque())
        while hits and ahora - hits[0] > RATE_LIMIT_WINDOW_S:
            hits.popleft()
        if len(hits) >= RATE_LIMIT_REQUESTS:
            return True
        hits.append(ahora)
        # Higiene: no acumular IPs muertas para siempre.
        if len(_rate_hits) > 1024:
            for ip in [k for k, v in _rate_hits.items() if not v]:
                del _rate_hits[ip]
    return False


def _reset_rate_limit() -> None:
    """Limpia el estado del limitador (lo usan los tests)."""
    with _rate_lock:
        _rate_hits.clear()

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
# Las herramientas BI de escritorio (Power BI Desktop, Tableau Desktop, Excel)
# NO son navegadores y no mandan preflight CORS: no necesitan nada de esto.
# CORS solo importa para clientes en el browser, y ahí un comodín sería un
# agujero (cualquier web abierta podría leer el puerto local). Por eso el
# default es la propia app local, y se amplía a mano si alguien necesita el
# Power BI service:  MVDG_API_CORS_ORIGINS="https://app.powerbi.com"
_cors_env = os.environ.get("MVDG_API_CORS_ORIGINS", "").strip()
CORS_ORIGINS = ([o.strip() for o in _cors_env.split(",") if o.strip()]
                if _cors_env else
                ["http://127.0.0.1:8501", "http://localhost:8501"])
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS,
                   allow_methods=["GET"], allow_headers=["*"])


@app.middleware("http")
async def _guard(request: Request, call_next):
    """Rate limit + autenticación opcional, en el punto de ejecución.

    Va como middleware y no dentro de cada handler a propósito: así una ruta
    nueva queda protegida por omisión en vez de depender de que alguien se
    acuerde de agregarle el chequeo."""
    ruta = request.url.path
    ip = request.client.host if request.client else "desconocido"

    if ruta not in RATE_LIMIT_EXEMPT and _rate_limited(ip):
        return JSONResponse(
            status_code=429,
            headers={"Retry-After": str(int(RATE_LIMIT_WINDOW_S))},
            content={"error": "rate_limit",
                     "detail": (
                         f"ES: Demasiadas consultas (máx. {RATE_LIMIT_REQUESTS}/min). "
                         f"Esperá un minuto o subí el límite con MVDG_API_RATE_LIMIT. · "
                         f"EN: Too many requests (max {RATE_LIMIT_REQUESTS}/min). "
                         f"Wait a minute or raise MVDG_API_RATE_LIMIT. · "
                         f"PT: Muitas consultas (máx. {RATE_LIMIT_REQUESTS}/min). "
                         f"Aguarde um minuto ou aumente MVDG_API_RATE_LIMIT.")})

    token = _api_token()
    if token and ruta not in ("/health",):
        enviado = request.headers.get("authorization", "")
        prefijo = "bearer "
        enviado = (enviado[len(prefijo):]
                   if enviado[:len(prefijo)].lower() == prefijo else "")
        # compare_digest: comparación de tiempo constante, no filtra el token
        # carácter a carácter por diferencia de tiempo de respuesta.
        if not hmac.compare_digest(enviado, token):
            return JSONResponse(
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
                content={"error": "unauthorized",
                         "detail": (
                             "ES: Falta el token. Mandá el header "
                             "'Authorization: Bearer <MVDG_API_TOKEN>'. · "
                             "EN: Missing token. Send the header "
                             "'Authorization: Bearer <MVDG_API_TOKEN>'. · "
                             "PT: Falta o token. Envie o cabeçalho "
                             "'Authorization: Bearer <MVDG_API_TOKEN>'.")})

    return await call_next(request)

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


def _port_free(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def main():
    port = int(os.environ.get("MVDG_API_PORT", DEFAULT_PORT))
    host = os.environ.get("MVDG_API_HOST", "127.0.0.1").strip() or "127.0.0.1"

    # Publicar esta API fuera de loopback expone catálogo, calidad y glosario
    # a la red. Sin token eso sería un dataset de gobierno abierto a cualquiera
    # que llegue al puerto: se corta acá (falla cerrado), no se sirve igual.
    if not _is_loopback(host) and not _api_token():
        sys.stderr.write(
            f"\n  [MV Data Governance] Te pidieron publicar la API en {host} "
            f"(fuera de 127.0.0.1) SIN token de acceso.\n"
            f"  ES: Definí MVDG_API_TOKEN=<token secreto> antes de exponerla, o "
            f"dejá MVDG_API_HOST en 127.0.0.1 para uso local.\n"
            f"  EN: Set MVDG_API_TOKEN=<secret> before exposing it, or keep "
            f"MVDG_API_HOST at 127.0.0.1 for local use.\n"
            f"  PT: Defina MVDG_API_TOKEN=<segredo> antes de expor, ou mantenha "
            f"MVDG_API_HOST em 127.0.0.1 para uso local.\n\n")
        sys.exit(1)

    # Este puerto es un punto de integración FIJO: Power BI/Tableau/Excel lo
    # tienen configurado como origen de datos, y docs/BI_INTEGRATION.md lo
    # documenta como http://127.0.0.1:8600. Si otro programa ya lo está
    # usando, NO lo "resolvemos" saltando en silencio a otro puerto (eso
    # rompería esas conexiones ya armadas sin avisar) — se corta acá con un
    # mensaje claro y accionable en vez del traceback crudo de uvicorn.
    if not _port_free(host, port):
        sys.stderr.write(
            f"\n  [MV Data Governance] El puerto {port} ya está en uso por otro "
            f"programa / port {port} is already in use by another program / a "
            f"porta {port} ja esta em uso por outro programa.\n"
            f"  ES: Cerrá ese programa, o corré con MVDG_API_PORT=<otro puerto> "
            f"para usar otro (recordá actualizar la URL en tu BI).\n"
            f"  EN: Close that program, or run with MVDG_API_PORT=<port> to use "
            f"a different one (remember to update the URL in your BI tool).\n"
            f"  PT: Feche esse programa, ou rode com MVDG_API_PORT=<porta> para "
            f"usar outra (lembre de atualizar a URL na sua ferramenta de BI).\n\n")
        sys.exit(1)

    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
