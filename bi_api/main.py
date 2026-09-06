# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
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
import sys
import threading
import time
from collections import deque

import uvicorn
from fastapi import Body, FastAPI, File, HTTPException, Query, Request, UploadFile
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


@app.get("/api/instalacion", tags=["meta"])
def instalacion(lang: str = "es"):
    """Cómo está instalado esto y DÓNDE queda guardado lo que hace el usuario.

    No es un dato de diagnóstico: es lo único que cambia entre las dos formas
    de instalar (tu equipo / la VM del cliente), y el usuario tiene que poder
    verlo sin abrir una consola. En una VM no persistente, guardar en el
    perfil del usuario significa perder el trabajo al cerrar sesión — si eso
    está pasando, la pantalla lo dice.
    """
    from mvdg import install_mode
    return install_mode.descripcion(lang if lang in LANGS else "es")


# ---------------------------------------------------------------------------
# Licencia
#
# La version .exe (Electron + React) no tenia NINGUNA nocion de licencia: sus
# seis vistas son funciones gratuitas, no habia donde pegar la clave, y demo,
# paga y owner se veian exactamente igual. O sea que quien pagaba y usaba el
# .exe recibia la demo — el mismo bug que ya se cerro en la capa de licencias,
# un nivel mas arriba.
#
# Estos dos endpoints son lo minimo para que la compra sirva en el .exe:
# consultar que plan hay, y activar una clave.
#
# Que esto sea escritura sobre una API no la abre a nadie: escucha en
# 127.0.0.1 por defecto (fuera de loopback exige MVDG_API_TOKEN, ver main()),
# y sobre todo licensing.save() REVALIDA la firma Ed25519 antes de guardar
# nada. Mandar un token inventado no habilita nada: se rechaza igual que si se
# pegara en la otra interfaz.
# ---------------------------------------------------------------------------
@app.get("/api/licencia", tags=["meta"])
def licencia_estado():
    """Plan vigente y que funciones habilita."""
    from mvdg import licensing
    return licensing.status()


# Body(...)/File(...) en el default los marca ruff (B008): se sacan a
# constantes de modulo.
_CUERPO = Body(...)
_ARCHIVO = File(...)


@app.post("/api/licencia", tags=["meta"])
def licencia_activar(cuerpo: dict = _CUERPO):
    """Activa una clave MVDG2. Devuelve el estado nuevo, o 400 si no valida.

    No se guarda nada que no verifique: `save()` devuelve None y ahi se
    responde 400. Una clave rota tiene que fallar RUIDOSO — el sintoma de no
    hacerlo es un cliente que pego su clave, no vio ningun error, y sigue en
    demo sin entender por que.
    """
    from mvdg import licensing
    token = str((cuerpo or {}).get("token") or "").strip()
    if not token:
        raise HTTPException(400, "Falta la clave de licencia.")
    if licensing.save(token) is None:
        raise HTTPException(400, "La clave no es valida para este programa.")
    return licensing.status()


@app.post("/api/licencia/renovar", tags=["meta"])
def licencia_renovar():
    """Renueva la licencia si viene de una suscripcion que sigue paga.

    Es la unica llamada del programa que sale a internet, y solo hace algo si
    la licencia actual trae `sub`. Quien tiene Licencia PC (pago unico) recibe
    "sin_suscripcion" y no se toca nada.

    Nunca borra la licencia vigente: si la suscripcion figura impaga puede ser
    que el cobro se acredite mañana, y dejar al cliente afuera al instante por
    eso seria peor que esperar al vencimiento.
    """
    from mvdg import licensing
    r = licensing.renovar()
    return {**r, **licensing.status()}


@app.delete("/api/licencia", tags=["meta"])
def licencia_borrar():
    """Saca la licencia guardada y vuelve a plan demo."""
    from mvdg import licensing
    licensing.clear()
    return licensing.status()


# ───────────────────────────────────────────────────────────────────────────
# LAS TRES FUNCIONES QUE SE COBRAN
# ───────────────────────────────────────────────────────────────────────────
# El .exe que baja el cliente habla SOLO con esta API. Y acá no existía ni un
# endpoint para migrar a Purview, migrar a Collibra ni escanear el tenant de
# BI — las tres únicas funciones que se pagan.
#
# O sea: el cliente pagaba, pegaba su clave, y la pantalla de licencia le
# decía "estas 3 funciones están desbloqueadas"… sin ninguna forma de
# usarlas. Vivían solo en app/app.py (Streamlit), que el .exe no levanta.
# Pagar y no recibir es el mismo problema que cobrar un mes y entregar para
# siempre, mirado desde el otro lado.
#
# Se replica el criterio que ya tenía Streamlit, que es el correcto
# comercialmente: LA VISTA PREVIA ES GRATIS —es lo que hace lucir el
# producto— y lo que se licencia es el push REAL contra el sistema de la
# empresa. Un plan demo puede ver exactamente qué se enviaría; no puede
# enviarlo.
#
# Y se respeta lo que manda el proyecto: los conectores externos están
# apagados por defecto. `dry_run` es True salvo pedido explícito, y sin
# credenciales configuradas el push real ni se intenta.

_DESTINOS_MIGRACION = {
    "purview": ("migracion_purview", "purview_export"),
    "collibra": ("migracion_collibra", "collibra_export"),
}


def _exigir_licencia(funcion: str) -> None:
    """Corta con 402 si el plan actual no incluye esa función.

    402 y no 403: 403 es "no tenés permiso" y suena a error del cliente. Acá
    la respuesta es "esto se paga", que es exactamente lo que significa
    Payment Required — y le deja a la interfaz un código sin ambigüedad para
    mostrar el aviso de licencia en vez de un error genérico.
    """
    from mvdg import licensing
    if not licensing.has_feature(funcion):
        raise HTTPException(402, {
            "error": "requiere_licencia",
            "funcion": funcion,
            "plan": licensing.plan(),
            "es": "Esta función necesita una licencia activa. La vista previa "
                  "no requiere ninguna.",
            "en": "This feature needs an active license. The preview needs "
                  "none.",
            "pt": "Esta função precisa de uma licença ativa. A pré-visualização "
                  "não precisa de nenhuma.",
        })


@app.get("/api/conectores", tags=["governance"])
def conectores_estado():
    """Qué conectores externos están configurados y cuáles habilita el plan.

    La interfaz lo necesita para decir la verdad ANTES de que el cliente
    apriete: sin credenciales el push real no puede correr por más licencia
    que tenga, y con licencia pero sin credenciales el problema no es la
    licencia. Sin esto los dos casos se ven igual — un botón que falla.
    """
    from mvdg import collibra_export, licensing, purview_export
    return {
        "plan": licensing.plan(),
        "purview": {
            "configurado": bool(purview_export.configured()),
            "licenciado": licensing.has_feature("migracion_purview"),
        },
        "collibra": {
            "configurado": bool(collibra_export.configured()),
            "licenciado": licensing.has_feature("migracion_collibra"),
        },
        "tenant_bi": {
            "licenciado": licensing.has_feature("escaneo_tenant_bi"),
        },
    }


@app.post("/api/migracion/{destino}", tags=["governance"])
def migrar(destino: str, cuerpo: dict = _CUERPO,
           lang: str = Query("es", pattern="^(es|en|pt)$")):
    """Migra el catálogo a Purview o Collibra.

    `aplicar: false` (el default) es la vista previa: no toca nada afuera y no
    pide licencia. `aplicar: true` es el push real contra el sistema de la
    empresa, y ese sí se licencia.

    El default es la vista previa a propósito: si mandar de verdad fuera lo
    que pasa cuando no se aclara nada, alcanzaría un cuerpo mal armado para
    escribirle al Purview de producción de un cliente.
    """
    import importlib

    if destino not in _DESTINOS_MIGRACION:
        raise HTTPException(404, f"Destino desconocido: {destino}. "
                                 f"Disponibles: {sorted(_DESTINOS_MIGRACION)}")
    funcion, modulo = _DESTINOS_MIGRACION[destino]
    aplicar = bool((cuerpo or {}).get("aplicar"))
    if aplicar:
        _exigir_licencia(funcion)

    exporter = importlib.import_module(f"mvdg.{modulo}")
    if aplicar and not exporter.configured():
        raise HTTPException(409, {
            "error": "conector_sin_configurar",
            "destino": destino,
            "es": f"Faltan las credenciales de {destino}. La vista previa "
                  f"funciona igual.",
            "en": f"{destino} credentials are missing. The preview still works.",
            "pt": f"Faltam as credenciais do {destino}. A pré-visualização "
                  f"funciona mesmo assim.",
        })

    t = governance_tables(lang)
    try:
        resultado = exporter.push_all(t["catalog"], t["dictionary"],
                                      t["glossary"], dry_run=not aplicar)
    except Exception as exc:  # noqa: BLE001 — cualquier fallo del conector
        # El detalle del error del sistema remoto no se filtra al cliente: el
        # tipo alcanza para diagnosticar sin exponer URLs internas ni tokens
        # que a veces vienen en el mensaje de la excepción.
        raise HTTPException(502, {
            "error": "conector_fallo", "destino": destino,
            "tipo": type(exc).__name__,
        }) from exc
    return {"destino": destino, "aplicado": aplicar, "resultado": resultado}


# ───────────────────────────────────────────────────────────────────────────
# PERFILAR TUS PROPIOS DATOS
# ───────────────────────────────────────────────────────────────────────────
# La landing lo vende con estas palabras: «Subí un CSV o Excel y obtené al
# instante esquema, nulos, duplicados, PII detectada y reglas sugeridas». Y el
# plan de US$ 149 dice «Todo el programa sin límite de tiempo».
#
# El .exe no tenía NADA de eso. Ni endpoint, ni pantalla, ni forma de cargar un
# archivo. El perfilador vivía solo en app/app.py (Streamlit), que el .exe no
# levanta — así que el cliente bajaba el programa, buscaba la función principal
# que vio anunciada, y no existía.
#
# Es gratis a propósito: no está en FUNCIONES_PAGAS, igual que en Streamlit.
# Es lo que hace que alguien entienda el producto con SUS datos, que es lo que
# después se compra.
#
# EL ARCHIVO NO SALE DE LA MÁQUINA y no toca el disco: la API escucha en
# 127.0.0.1, se lee en memoria y se descarta. No hay ningún lugar donde
# quede — que es exactamente lo que la landing promete cuando dice que tus
# datos nunca salen de tu PC.

# ───────────────────────── Cuánto se acepta ─────────────────────────────
# Los topes viejos (40 MB, 200.000 filas) estaban puestos para el peor caso
# —la API expuesta a varios usuarios— y se los comía también el caso normal:
# alguien perfilando SU archivo en SU PC. Y el de filas era peor que el de
# bytes, porque no rechazaba: LEÍA LAS PRIMERAS 200.000 Y SEGUÍA. El cliente
# recibía el perfil de un pedazo de su archivo con cara de perfil completo.
#
# Ahora los dos se configuran, y por defecto no estorban:
#
#   MVDG_MAX_UPLOAD_MB    tope de tamaño en MB   (default 2048; 0 = sin tope)
#   MVDG_MAX_FILAS        tope de filas          (default 0 = sin tope)
#
# El tope de bytes sigue existiendo por defecto porque esta API PUEDE
# publicarse fuera de 127.0.0.1: sin ningún límite, una sola petición basta
# para voltear el proceso. En una instalación de escritorio se puede poner
# MVDG_MAX_UPLOAD_MB=0 y el único límite pasa a ser la RAM de la máquina,
# que es el límite honesto.
def _limite(env: str, defecto: int) -> int:
    """Lee un tope numérico del entorno. 0 (o negativo) = sin tope."""
    try:
        valor = int(os.environ.get(env, "").strip() or defecto)
    except ValueError:
        return defecto
    return max(0, valor)


_MAX_BYTES = _limite("MVDG_MAX_UPLOAD_MB", 2048) * 1024 * 1024
# 0 = leer el archivo entero. Es el default: truncar en silencio es la peor
# de las tres opciones (rechazar, truncar avisando, leer todo).
_MAX_FILAS = _limite("MVDG_MAX_FILAS", 0)
_EXT_OK = (".csv", ".tsv", ".txt", ".xlsx", ".xlsm", ".xls")


@app.post("/api/perfilar", tags=["governance"])
async def perfilar(archivo: UploadFile = _ARCHIVO,
                   lang: str = Query("es", pattern="^(es|en|pt)$")):
    """Perfila un CSV o Excel: esquema, nulos, duplicados, PII y reglas.

    No requiere licencia. No guarda nada.
    """
    import io

    import pandas as pd

    from mvdg import profiler

    nombre = (archivo.filename or "").strip()
    if not nombre.lower().endswith(_EXT_OK):
        raise HTTPException(400, {
            "error": "formato_no_soportado",
            "es": f"Se aceptan {', '.join(_EXT_OK)}.",
            "en": f"Accepted formats: {', '.join(_EXT_OK)}.",
            "pt": f"Formatos aceitos: {', '.join(_EXT_OK)}.",
        })

    crudo = await archivo.read(_MAX_BYTES + 1) if _MAX_BYTES else await archivo.read()
    if _MAX_BYTES and len(crudo) > _MAX_BYTES:
        raise HTTPException(413, {
            "error": "archivo_muy_grande",
            "max_mb": _MAX_BYTES // (1024 * 1024),
            "es": f"El archivo pasa de {_MAX_BYTES // (1024 * 1024)} MB.",
            "en": f"The file is over {_MAX_BYTES // (1024 * 1024)} MB.",
            "pt": f"O arquivo passa de {_MAX_BYTES // (1024 * 1024)} MB.",
        })
    if not crudo:
        raise HTTPException(400, {"error": "archivo_vacio"})

    try:
        # nrows=None es "todas": con _MAX_FILAS en 0 se lee el archivo entero.
        _filas = _MAX_FILAS or None
        if nombre.lower().endswith((".xlsx", ".xlsm", ".xls")):
            df = pd.read_excel(io.BytesIO(crudo), nrows=_filas)
        else:
            # sep=None + engine="python" deja que pandas descubra si es coma,
            # punto y coma o tabulador. En Uruguay el Excel exporta con punto y
            # coma por el separador decimal, asi que asumir la coma daria una
            # sola columna con todo adentro y un perfil que no dice nada.
            df = pd.read_csv(io.BytesIO(crudo), sep=None, engine="python",
                             nrows=_filas)
    except Exception as exc:  # noqa: BLE001 — cualquier archivo roto
        raise HTTPException(400, {
            "error": "no_se_pudo_leer", "tipo": type(exc).__name__,
            "es": "No se pudo leer el archivo. ¿Está completo y bien formado?",
            "en": "The file could not be read. Is it complete and well formed?",
            "pt": "Não foi possível ler o arquivo. Está completo e bem formado?",
        }) from exc

    if df.empty or not len(df.columns):
        raise HTTPException(400, {"error": "sin_datos"})

    perfil = profiler.profile_table(df)
    return {
        "archivo": nombre,
        # Los conteos se convierten uno por uno y NO metiendolos en una Series:
        # pandas unifica el tipo de la Series entera, asi que un solo decimal
        # (null_cells_pct) convertia "4 filas" en "4.0 filas". Un conteo con
        # decimales en pantalla se lee como un error del programa.
        "resumen": {k: (int(v) if float(v).is_integer() and k != "null_cells_pct"
                        else round(float(v), 2))
                    for k, v in profiler.summary(df).items()},
        "perfil": json.loads(perfil.to_json(orient="records",
                                            date_format="iso")),
        "reglas": profiler.suggest_rules(df, lang),
        # Que el cliente sepa que vio TODO su archivo, o que se corto. Un
        # perfil sobre la mitad de las filas presentado como si fuera el total
        # es un dato equivocado con cara de dato bueno.
        "filas_leidas": int(len(df)),
        "truncado": bool(_MAX_FILAS and len(df) >= _MAX_FILAS),
    }


# ───────────────────────────────────────────────────────────────────────────
# INGENIERÍA DE DATOS AUTOMÁTICA (mvdg/dataeng.py)
# ───────────────────────────────────────────────────────────────────────────
# La pestaña completa: perfil avanzado, calidad por 6 dimensiones, claves y
# joins entre tablas, análisis temporal, fuga de información (leakage) contra
# un target y feature engineering anti-leakage — sobre un archivo o una base
# de datos SQL. Gratis, igual que /api/perfilar: no está en FUNCIONES_PAGAS.
#
# El motor (mvdg/dataeng.py) es language-neutral a propósito: cada issue,
# cada motivo de fuga y cada feature llevan un CÓDIGO estable, no una
# oración armada. La traducción pasa ACÁ, en la API — mismo lugar donde ya
# se resuelve el idioma para el resto de /api/perfilar y de las tablas de
# gobierno — así que ni Streamlit ni React tienen que reimplementar la
# lógica de "qué texto le corresponde a este código".
#
# La fuente SQL reusa mvdg/connectors.py (9 motores, credenciales protegidas
# con el keyring del SO) en vez de duplicar un conector acá: es el mismo
# motor que ya usa la pestaña Perfilador de Streamlit, con las conexiones
# guardadas compartidas entre las dos interfaces (~/.mv_data_governance).
#
# La traducción de los códigos language-neutral vive en `mvdg.dataeng`
# (`traducir_resultado` y compañía), no acá: Streamlit también la necesita
# para su propia integración de este motor, y duplicarla en bi_api hubiera
# significado dos lugares que traducen "qi_nulos_masivos" y que pueden
# desalinearse — el mismo tipo de bug que ya le costó caro a este proyecto
# (ver api/checkout.js, precio y vencimiento separados en dos archivos).


def _de_error(clave: str, status: int, **extra) -> HTTPException:
    """Arma un HTTPException trilingüe a partir de una clave de mvdg/i18n.py."""
    from mvdg.i18n import t
    return HTTPException(status, {
        "error": clave,
        "es": t(clave, "es"), "en": t(clave, "en"), "pt": t(clave, "pt"),
        **extra,
    })


# Acá entran VARIOS archivos a la vez (o un .sqlite con varias tablas), así
# que el tope es el del conjunto. Configurable con MVDG_MAX_UPLOAD_DE_MB;
# 0 = sin tope, igual que en /api/perfilar.
_MAX_BYTES_DE = _limite("MVDG_MAX_UPLOAD_DE_MB", 4096) * 1024 * 1024
_ARCHIVOS = File(...)


@app.post("/api/ingenieria/archivo", tags=["governance"])
async def ingenieria_archivo(
    archivos: list[UploadFile] = _ARCHIVOS,
    lang: str = Query("es", pattern="^(es|en|pt)$"),
    target: str = Query(""),
    columna_tiempo: str = Query(""),
):
    """Analiza uno o varios archivos (CSV/TSV/Excel/Parquet/JSON/JSONL/SQLite)
    con el motor completo de ingeniería de datos. No requiere licencia. No
    guarda nada — igual que /api/perfilar.
    """
    from mvdg import dataeng

    if not archivos:
        raise _de_error("de_err_vacio", 400)

    tablas: dict = {}
    restante = _MAX_BYTES_DE
    for arch in archivos:
        nombre = (arch.filename or "").strip()
        ext = os.path.splitext(nombre.lower())[1]
        if ext not in dataeng.EXT_SOPORTADAS:
            raise _de_error("de_err_formato", 400)
        # Con el tope apagado (_MAX_BYTES_DE = 0) se lee el archivo entero y
        # no se lleva presupuesto: `restante` deja de tener sentido.
        if _MAX_BYTES_DE:
            crudo = await arch.read(restante + 1)
            if len(crudo) > restante:
                raise _de_error("de_grande", 413)
        else:
            crudo = await arch.read()
        if not crudo:
            continue
        restante -= len(crudo)
        try:
            leidas = dataeng.leer_archivo_bytes(nombre, crudo)
        except Exception as exc:  # noqa: BLE001 — cualquier archivo roto
            raise _de_error("de_malo", 400, tipo=type(exc).__name__) from exc
        stem = dataeng.slug(os.path.splitext(nombre)[0], 30)
        for tname, tdf in leidas.items():
            clave = tname if len(archivos) == 1 else f"{stem}__{tname}"
            base, i = clave, 2
            while clave in tablas:
                clave = f"{base}_{i}"
                i += 1
            tablas[clave] = tdf

    if not tablas:
        raise _de_error("de_err_vacio", 400)

    truncado_tablas = len(tablas) > dataeng.MAX_TABLAS_MULTIPLES
    if truncado_tablas:
        tablas = dict(list(tablas.items())[:dataeng.MAX_TABLAS_MULTIPLES])

    tgt = target.strip() or None
    tcol = columna_tiempo.strip() or None
    resultados = {
        nombre: dataeng.traducir_resultado(
            dataeng.analizar_tabla(nombre, df, target=tgt, columna_tiempo=tcol), lang)
        for nombre, df in tablas.items()
    }
    joins = dataeng.joins_sugeridos(tablas) if len(tablas) > 1 else []
    return {
        "tablas": resultados,
        "joins": dataeng.traducir_joins(joins, lang),
        "truncado_tablas": truncado_tablas,
    }


def _de_resolver_conexion(cuerpo: dict) -> tuple[dict, str | None]:
    """Arma (profile, password) a partir del cuerpo del pedido.

    Si trae `conn_id`, parte de la conexión ya guardada (no hace falta
    reescribir host/usuario cada vez) y el cuerpo puede pisar cualquier
    campo puntual — incluida la contraseña, sin que eso la guarde.
    """
    from mvdg import connectors
    cuerpo = cuerpo or {}
    conn_id = cuerpo.get("conn_id")
    base = {}
    if conn_id:
        for c in connectors.load_connections():
            if c.get("conn_id") == conn_id:
                base = dict(c)
                break
    profile = {**base, **{k: v for k, v in cuerpo.items() if v not in (None, "")}}
    password = cuerpo.get("password") or (connectors.stored_password(base) if base else "")
    return profile, (password or None)


@app.get("/api/ingenieria/sql/conexiones", tags=["governance"])
def ingenieria_sql_conexiones():
    """Conexiones guardadas — nunca la contraseña, ni cifrada ni ofuscada."""
    from mvdg import connectors
    return [{k: v for k, v in c.items() if k != "password_enc"}
            for c in connectors.load_connections()]


@app.post("/api/ingenieria/sql/conexiones", tags=["governance"])
def ingenieria_sql_guardar(cuerpo: dict = _CUERPO):
    """Guarda (o actualiza, por `conn_id`) una conexión a base de datos."""
    from mvdg import connectors
    cuerpo = cuerpo or {}
    if not str(cuerpo.get("name", "")).strip():
        raise HTTPException(400, "Falta el nombre de la conexión.")
    stored = connectors.save_connection(cuerpo, save_password=bool(cuerpo.get("save_password", True)))
    return {k: v for k, v in stored.items() if k != "password_enc"}


@app.delete("/api/ingenieria/sql/conexiones/{conn_id}", tags=["governance"])
def ingenieria_sql_borrar(conn_id: str):
    from mvdg import connectors
    connectors.delete_connection(conn_id)
    return {"ok": True}


@app.post("/api/ingenieria/sql/probar", tags=["governance"])
def ingenieria_sql_probar(cuerpo: dict = _CUERPO):
    """Prueba una conexión SQL (ad hoc o guardada por `conn_id`)."""
    profile, password = _de_resolver_conexion(cuerpo)
    from mvdg import connectors
    ok, msg = connectors.test_connection(profile, password=password)
    return {"ok": ok, "mensaje": msg}


@app.post("/api/ingenieria/sql/tablas", tags=["governance"])
def ingenieria_sql_tablas(cuerpo: dict = _CUERPO):
    """Tablas visibles en la conexión."""
    profile, password = _de_resolver_conexion(cuerpo)
    from mvdg import connectors
    try:
        tablas = connectors.list_tables(profile, password=password)
    except Exception as exc:  # noqa: BLE001 — el error real de conexión importa acá
        raise HTTPException(502, {"error": "conexion_fallo", "tipo": type(exc).__name__,
                                  "detalle": str(exc)}) from exc
    return {"tablas": tablas}


@app.post("/api/ingenieria/sql/analizar", tags=["governance"])
def ingenieria_sql_analizar(cuerpo: dict = _CUERPO,
                            lang: str = Query("es", pattern="^(es|en|pt)$")):
    """Trae una o varias tablas (o el resultado de una consulta SELECT/WITH)
    y corre el motor completo de ingeniería de datos. Gratis, sin licencia —
    igual que /api/ingenieria/archivo, solo cambia de dónde sale el
    DataFrame.
    """
    from mvdg import connectors, dataeng

    profile, password = _de_resolver_conexion(cuerpo)
    if not profile.get("engine"):
        raise HTTPException(400, "Falta el motor de la conexión.")

    try:
        # Sin techo: `limite=0` trae la tabla entera. Antes se recortaba a
        # connectors.MAX_ROWS, así que pedir más filas de las permitidas
        # devolvía menos sin decir nada.
        crudo_lim = cuerpo.get("limite")
        limite = (max(0, int(crudo_lim)) if crudo_lim is not None
                  else dataeng.MUESTRA_SQL_DEFECTO)
    except (TypeError, ValueError):
        limite = dataeng.MUESTRA_SQL_DEFECTO

    query = str(cuerpo.get("query") or "").strip()
    nombres_tablas = [str(x) for x in (cuerpo.get("tablas") or [])][:dataeng.MAX_TABLAS_MULTIPLES]

    tablas: dict = {}
    try:
        if query:
            tablas["consulta"] = connectors.run_query(profile, query, limite, password=password)
        for nombre in nombres_tablas:
            tablas[nombre] = connectors.load_table(profile, nombre, limite, password=password)
    except ValueError as exc:  # consulta que no es SELECT/WITH
        raise HTTPException(400, {"error": "consulta_no_permitida", "detalle": str(exc)}) from exc
    except Exception as exc:  # noqa: BLE001 — el error real de conexión importa acá
        raise HTTPException(502, {"error": "conexion_fallo", "tipo": type(exc).__name__,
                                  "detalle": str(exc)}) from exc

    if not tablas:
        raise HTTPException(400, "Indicá al menos una tabla o una consulta.")

    tgt = str(cuerpo.get("target") or "").strip() or None
    tcol = str(cuerpo.get("columna_tiempo") or "").strip() or None
    resultados = {
        nombre: dataeng.traducir_resultado(
            dataeng.analizar_tabla(nombre, df, target=tgt, columna_tiempo=tcol,
                                   muestra=dataeng.TOPE_FILAS), lang)
        for nombre, df in tablas.items()
    }
    joins = dataeng.joins_sugeridos(tablas) if len(tablas) > 1 else []
    return {"tablas": resultados, "joins": dataeng.traducir_joins(joins, lang)}


@app.post("/api/bi/escanear-tenant", tags=["governance"])
def escanear_tenant(cuerpo: dict = _CUERPO,
                    lang: str = Query("es", pattern="^(es|en|pt)$")):
    """Escanea el tenant de Power BI y cataloga lo que encuentre.

    Acá no hay vista previa que valga: leer el tenant de la empresa ES la
    función. Por eso pide licencia siempre, a diferencia de las migraciones.
    """
    _exigir_licencia("escaneo_tenant_bi")
    from mvdg import powerbi_meta

    try:
        maximo = int((cuerpo or {}).get("max_workspaces") or 25)
    except (TypeError, ValueError):
        raise HTTPException(400, "max_workspaces tiene que ser un numero") from None
    maximo = max(1, min(maximo, 1000))

    try:
        salida = powerbi_meta.ingest_tenant(lang, max_workspaces=maximo)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, {
            "error": "tenant_fallo", "tipo": type(exc).__name__,
        }) from exc

    # Las tablas vuelven como DataFrame; se serializan igual que el resto de
    # la API para que la interfaz no tenga que tratarlas distinto.
    tablas = {}
    for nombre, valor in (salida or {}).items():
        if hasattr(valor, "to_json"):
            tablas[nombre] = json.loads(valor.to_json(orient="records",
                                                      date_format="iso"))
        else:
            tablas[nombre] = valor
    return {"max_workspaces": maximo, "tablas": tablas}


def _serve(df, table: str, lang: str, format: str):
    if format == "csv":
        return PlainTextResponse(df.to_csv(index=False),
                                 media_type="text/csv; charset=utf-8")
    # to_json→loads normaliza tipos numpy y convierte NaN/NaT en null,
    # garantizando JSON estricto para cualquier cliente BI.
    records = json.loads(df.to_json(orient="records", date_format="iso"))
    return {"table": table, "lang": lang, "rows": len(df), "data": records}


# ---------------------------------------------------------------------------
# Relevamiento y reuniones
#
# El motor de los dos modulos ya existe (mvdg/interview.py, mvdg/meetings.py) y
# la interfaz completa esta en el panel Streamlit. Estos endpoints lo dejan
# alcanzable desde la API, que es por donde lo consume la version .exe: sin
# ellos, el motor solo se podria usar desde una de las dos interfaces.
#
# Van ANTES de /api/{table}: esa ruta es un comodin y se come cualquier cosa
# que se declare despues. Hay un test que fija el orden, porque el sintoma de
# equivocarse no es un error sino un 200 con el contenido de otra ruta.
# ---------------------------------------------------------------------------
@app.get("/api/relevamiento/preguntas", tags=["governance"])
def relevamiento_preguntas(lang: str = Query("es", pattern="^(es|en|pt)$")):
    """El banco entero: areas del pipeline y sus preguntas."""
    from mvdg import interview
    return {"lang": lang, "areas": interview.areas(lang),
            "preguntas": interview.questions(lang)}


@app.post("/api/relevamiento/repreguntas", tags=["governance"])
def relevamiento_repreguntas(cuerpo: dict = _CUERPO):
    """Que repreguntar sobre una respuesta. Local: no sale nada de la maquina."""
    from mvdg import interview
    datos = cuerpo or {}
    lang = str(datos.get("lang") or "es")
    lang = lang if lang in LANGS else "es"
    qid = str(datos.get("id") or "").strip()
    if not interview.question(qid, lang):
        raise HTTPException(404, f"No existe la pregunta {qid!r}.")
    return {"id": qid,
            "repreguntas": interview.follow_ups(
                qid, str(datos.get("respuesta") or ""), lang)}


@app.get("/api/relevamiento/{client_id}", tags=["governance"])
def relevamiento_estado(client_id: str,
                        lang: str = Query("es", pattern="^(es|en|pt)$")):
    """Lo respondido para un cliente, con la cobertura por area."""
    from mvdg import interview
    return {
        "client_id": client_id, "lang": lang,
        "cobertura": interview.overall_coverage(client_id),
        "por_area": json.loads(
            interview.progress(client_id, lang).to_json(orient="records")),
        "respuestas": json.loads(
            interview.answers_df(client_id, lang).to_json(orient="records")),
    }


@app.post("/api/relevamiento/{client_id}", tags=["governance"])
def relevamiento_guardar(client_id: str, cuerpo: dict = _CUERPO):
    """Anota quien respondio que. El estado se deduce si no viene."""
    from mvdg import interview
    datos = cuerpo or {}
    qid = str(datos.get("id") or "").strip()
    if not interview.question(qid):
        raise HTTPException(404, f"No existe la pregunta {qid!r}.")
    return interview.save_answer(
        client_id, qid,
        respuesta=str(datos.get("respuesta") or ""),
        responsable=str(datos.get("responsable") or ""),
        area_responsable=str(datos.get("area_responsable") or ""),
        estado=str(datos.get("estado") or ""))


@app.post("/api/reuniones/minuta", tags=["governance"])
def reuniones_minuta(cuerpo: dict = _CUERPO):
    """Transcripcion -> minuta: quien hablo, hallazgos y cruce con el pipeline.

    Recibe TEXTO, no audio: transcribir manda el audio a un tercero y esa
    decision se toma en la interfaz, con el aviso delante, no por una llamada
    de API que alguien podria encadenar sin darse cuenta.
    """
    from mvdg import meetings
    datos = cuerpo or {}
    lang = str(datos.get("lang") or "es")
    lang = lang if lang in LANGS else "es"
    inter = meetings.parse_transcript(str(datos.get("texto") or ""))
    minuta = meetings.minutes(
        inter, lang, titulo=str(datos.get("titulo") or ""),
        fecha=str(datos.get("fecha") or ""),
        participantes=str(datos.get("participantes") or ""))
    tablas = ("oradores", "hallazgos", "pipeline", "transcripcion")
    salida = {k: v for k, v in minuta.items() if k not in tablas}
    salida.update({k: json.loads(minuta[k].to_json(orient="records"))
                   for k in tablas})
    return salida


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
    """.Esta el puerto libre de verdad?

    Delegado a mvdg.netports: la version anterior ponia SO_REUSEADDR, que en
    Windows permite hacer bind sobre un puerto que otra app ya ocupa. O sea
    que este chequeo — el que existe justamente para NO pisar a nadie —
    devolvia "libre" en el sistema operativo donde mas importa."""
    from mvdg.netports import puerto_libre
    return puerto_libre(host, port)


def _dir_ui() -> str | None:
    """Carpeta con la interfaz de escritorio (React) ya empaquetada.

    La sirve ESTE servidor, en /app, a propósito: así la UI y la API quedan
    en el mismo origen y no hace falta CORS ni abrirla por file://, que son
    las dos formas habituales de que un empaquetado de escritorio termine
    con un agujero de seguridad o con un "no carga y no se sabe por qué".

    Orden: MVDG_UI_DIR (para armados a medida o para el bundle de
    electron-builder, que mueve las carpetas) y si no, la ruta del repo.
    Si no existe, no se monta nada — la API sigue funcionando igual para
    Power BI/Tableau, que es su trabajo principal.
    """
    from pathlib import Path
    candidatas = []
    env = os.environ.get("MVDG_UI_DIR", "").strip()
    if env:
        candidatas.append(Path(env))
    candidatas.append(Path(__file__).resolve().parent.parent / "electron" / "ui" / "dist")
    for c in candidatas:
        if (c / "index.html").is_file():
            return str(c)
    return None


_UI = _dir_ui()
if _UI:
    from fastapi.staticfiles import StaticFiles
    # html=True hace que /app sirva index.html en la raíz de la carpeta.
    app.mount("/app", StaticFiles(directory=_UI, html=True), name="ui")


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
