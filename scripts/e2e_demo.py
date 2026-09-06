# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · verificación end-to-end con los casos demo.

Qué problema cierra
───────────────────
`pytest` prueba el motor importándolo: llama funciones de Python y compara
lo que devuelven. Eso no dice nada sobre lo que ve un cliente. Entre el
motor y el cliente hay tres capas que pytest NO atraviesa:

  1. La API sirviéndose de verdad por HTTP (uvicorn, no TestClient).
  2. El dashboard Streamlit RENDERIZADO en un navegador: una excepción de
     Python en una pestaña no rompe ningún test — se dibuja prolija dentro
     de la página y el proceso sigue vivo.
  3. La landing en el navegador: un error de JavaScript no tiene forma de
     aparecer en pytest, y sin embargo deja el selector de idioma o el
     video muertos para el que entra a comprar.

Esto levanta los tres servicios de verdad, los recorre con Chromium y
falla si aparece cualquier excepción renderizada, error de consola,
petición fallida o respuesta que no sea la esperada.

Uso
───
    python scripts/e2e_demo.py            # todo
    python scripts/e2e_demo.py --api      # solo la capa HTTP (sin navegador)

Sale con código 0 solo si TODOS los chequeos pasan. Cualquier fallo se
imprime con el detalle exacto y devuelve 1.

No corre dentro de `pytest`: necesita puertos, procesos y un Chromium
instalado. Es la verificación que se corre a mano (o en un job aparte)
antes de declarar una versión lista para producción.
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

LANGS = ("es", "en", "pt")

# Se importan tarde y con sys.path ya armado: este script se puede correr
# desde cualquier carpeta.
from bi_api.main import SAMPLE_TABLES, TABLES  # noqa: E402
from mvdg.samples import sample_keys  # noqa: E402

# ── acumulador de resultados ────────────────────────────────────────────
# Un fallo no corta el recorrido: interesa el parte completo, no el primer
# error. Frenar en el primero obliga a correr todo de nuevo por cada
# problema, y eso es exactamente lo que hace que nadie corra la
# verificación.
OK: list[str] = []
FALLAS: list[str] = []


def chequeo(nombre: str, condicion: bool, detalle: str = "") -> bool:
    if condicion:
        OK.append(nombre)
        print(f"  ✓ {nombre}")
    else:
        FALLAS.append(f"{nombre}{' — ' + detalle if detalle else ''}")
        print(f"  ✗ {nombre}{' — ' + detalle if detalle else ''}")
    return condicion


def seccion(titulo: str) -> None:
    print(f"\n── {titulo} " + "─" * max(0, 62 - len(titulo)))


# ── infraestructura de procesos ─────────────────────────────────────────
def puerto_libre() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def esperar(url: str, intentos: int = 80, espera: float = 0.5) -> bool:
    for _ in range(intentos):
        try:
            urllib.request.urlopen(url, timeout=2)
            return True
        except urllib.error.HTTPError:
            return True  # contestó: está vivo aunque el código no sea 200
        except Exception:
            time.sleep(espera)
    return False


def pedir(url: str, timeout: int = 30) -> tuple[int, bytes, str]:
    """GET que nunca tira: devuelve (código, cuerpo, content-type)."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status, r.read(), r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        return e.code, e.read(), e.headers.get("Content-Type", "")
    except Exception as e:  # noqa: BLE001
        return 0, str(e).encode(), ""


def subir(url: str, campo: str, archivos: list[str], timeout: int = 180) -> tuple[int, bytes]:
    """POST multipart sin dependencias: `requests` no está en runtime."""
    import uuid
    borde = uuid.uuid4().hex
    partes = []
    for ruta in archivos:
        with open(ruta, "rb") as fh:
            crudo = fh.read()
        partes.append(
            f"--{borde}\r\nContent-Disposition: form-data; name=\"{campo}\"; "
            f"filename=\"{os.path.basename(ruta)}\"\r\n"
            "Content-Type: application/octet-stream\r\n\r\n".encode() + crudo + b"\r\n")
    cuerpo = b"".join(partes) + f"--{borde}--\r\n".encode()
    req = urllib.request.Request(
        url, data=cuerpo, method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={borde}"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:  # noqa: BLE001
        return 0, str(e).encode()


class Servicio:
    """Proceso hijo que se apaga sí o sí, aunque el recorrido explote."""

    def __init__(self, nombre: str, cmd: list[str], url_salud: str, env: dict | None = None):
        self.nombre, self.cmd, self.url_salud, self.env = nombre, cmd, url_salud, env
        self.proc: subprocess.Popen | None = None
        self.log = ""

    def __enter__(self) -> Servicio:
        entorno = dict(os.environ)
        if self.env:
            entorno.update(self.env)
        self.proc = subprocess.Popen(
            self.cmd, cwd=REPO_ROOT, env=entorno,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if not esperar(self.url_salud):
            self.__exit__(None, None, None)
            raise SystemExit(f"{self.nombre} no levantó en {self.url_salud}\n{self.log}")
        print(f"  · {self.nombre} arriba en {self.url_salud}")
        return self

    def __exit__(self, *_exc) -> None:
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()


# ── 1. capa HTTP: la API tal como la consume un BI ──────────────────────
def verificar_api(base: str) -> None:
    seccion("API REST (uvicorn real, como la ve Power BI / Tableau)")

    cod, cuerpo, _ = pedir(f"{base}/health")
    chequeo("/health responde 200", cod == 200, f"código {cod}")
    try:
        salud = json.loads(cuerpo)
    except Exception:  # noqa: BLE001
        salud = {}
    chequeo("/health se dice sano", str(salud.get("status", "")).lower() in ("ok", "healthy"),
            f"status={salud.get('status')!r}")

    # Las 9 tablas de gobierno × 3 idiomas × 2 formatos: 54 respuestas.
    # Una tabla vacía es un fallo: significa que el motor corrió pero no
    # gobernó nada, que es peor que un error (no se nota).
    fallos_tablas: list[str] = []
    vacias: list[str] = []
    for tabla in TABLES:
        for lang in LANGS:
            cod, cuerpo, ctype = pedir(f"{base}/api/{tabla}?lang={lang}")
            if cod != 200:
                fallos_tablas.append(f"{tabla}/{lang} -> {cod}")
                continue
            try:
                filas = _filas(json.loads(cuerpo))
            except Exception:  # noqa: BLE001
                fallos_tablas.append(f"{tabla}/{lang} -> JSON inválido")
                continue
            if not filas:
                vacias.append(f"{tabla}/{lang}")
            cod_csv, cuerpo_csv, _ = pedir(f"{base}/api/{tabla}?lang={lang}&format=csv")
            if cod_csv != 200 or not cuerpo_csv.strip():
                fallos_tablas.append(f"{tabla}/{lang} CSV -> {cod_csv}")
    chequeo(f"{len(TABLES)} tablas × {len(LANGS)} idiomas × JSON+CSV responden 200",
            not fallos_tablas, "; ".join(fallos_tablas[:5]))
    chequeo("ninguna tabla de gobierno vuelve vacía", not vacias, "; ".join(vacias[:5]))

    # Los 4 datasets demo, gobernados de punta a punta.
    datasets = sample_keys()
    fallos_ds: list[str] = []
    resumen_calidad: dict[str, tuple[int, int]] = {}
    for ds in datasets:
        cod, cuerpo, _ = pedir(f"{base}/api/samples/{ds}")
        if cod != 200:
            fallos_ds.append(f"{ds} ficha -> {cod}")
            continue
        for tabla in SAMPLE_TABLES:
            for lang in LANGS:
                cod, cuerpo, _ = pedir(f"{base}/api/samples/{ds}/{tabla}?lang={lang}")
                if cod != 200:
                    fallos_ds.append(f"{ds}/{tabla}/{lang} -> {cod}")
                    continue
                try:
                    filas = _filas(json.loads(cuerpo))
                except Exception:  # noqa: BLE001
                    fallos_ds.append(f"{ds}/{tabla}/{lang} -> JSON inválido")
                    continue
                if not filas:
                    fallos_ds.append(f"{ds}/{tabla}/{lang} -> vacío")
                if tabla == "quality_results" and lang == "es":
                    resumen_calidad[ds] = (
                        sum(1 for f in filas if str(f.get("status", "")).lower() != "pass"),
                        len(filas))
    chequeo(f"los {len(datasets)} datasets demo se sirven completos "
            f"({len(SAMPLE_TABLES)} tablas × {len(LANGS)} idiomas)",
            not fallos_ds, "; ".join(fallos_ds[:5]))

    # El caso demo tiene defectos inyectados a propósito: si NINGUNA regla
    # falla, el motor no está evaluando nada y la demo no demuestra nada.
    con_fallas = [d for d, (f, _) in resumen_calidad.items() if f > 0]
    chequeo("los datasets demo detectan fallas de calidad reales",
            len(con_fallas) >= 1,
            f"reglas que fallan por dataset: {resumen_calidad}")
    for ds, (f, tot) in sorted(resumen_calidad.items()):
        print(f"      · {ds}: {f}/{tot} reglas NO pasan (falla o alerta)")

    # Errores: tienen que fallar limpio, no con un 500.
    cod, _, _ = pedir(f"{base}/api/no_existe")
    chequeo("una tabla inexistente da 404 (no 500)", cod == 404, f"código {cod}")
    cod, _, _ = pedir(f"{base}/api/samples/no_existe")
    chequeo("un dataset inexistente da 404 (no 500)", cod == 404, f"código {cod}")
    cod, _, _ = pedir(f"{base}/api/catalog?lang=zz")
    chequeo("un idioma inválido se rechaza (422)", cod == 422, f"código {cod}")

    # Perfilado e ingeniería de datos sobre un CSV demo REAL subido por HTTP.
    csv_demo = os.path.join(REPO_ROOT, "assets", "samples", "dirty_cafe_sales.csv")
    cod, cuerpo = subir(f"{base}/api/perfilar?lang=es", "archivo", [csv_demo])
    perfil = json.loads(cuerpo) if cod == 200 else {}
    chequeo("/api/perfilar acepta un CSV demo real", cod == 200, f"código {cod}")
    columnas = perfil.get("perfil") or []
    chequeo("el perfilado devuelve una fila por columna", len(columnas) > 0,
            f"claves: {sorted(perfil)}")
    resumen = perfil.get("resumen") or {}
    chequeo("el perfilado cuenta filas y columnas del archivo real",
            resumen.get("rows", 0) > 0 and resumen.get("columns", 0) == len(columnas),
            f"resumen={resumen}, columnas perfiladas={len(columnas)}")
    # El CSV demo tiene nulos inyectados a propósito: si el perfilado
    # reporta 0%, no está midiendo — está devolviendo una plantilla.
    chequeo("el perfilado detecta los nulos inyectados en el CSV demo",
            float(resumen.get("null_cells_pct", 0)) > 0,
            f"null_cells_pct={resumen.get('null_cells_pct')}")
    chequeo("el perfilado propone reglas de calidad", len(perfil.get("reglas") or []) > 0)
    print(f"      · {resumen.get('rows')} filas × {resumen.get('columns')} columnas, "
          f"{resumen.get('null_cells_pct')}% de celdas nulas, "
          f"{len(perfil.get('reglas') or [])} reglas propuestas")

    cod, cuerpo = subir(f"{base}/api/ingenieria/archivo?lang=es", "archivos", [csv_demo])
    ing = json.loads(cuerpo) if cod == 200 else {}
    chequeo("/api/ingenieria/archivo acepta el mismo CSV", cod == 200, f"código {cod}")

    # Lo que se le muestra al usuario tiene que estar traducido y sin
    # placeholders sin rellenar: un "{ventana}" en pantalla es un bug visible.
    etiquetas = _etiquetas_de(ing)
    chequeo("la ingeniería de datos devuelve features con etiqueta",
            len(etiquetas) > 0, f"{len(etiquetas)} etiquetas")
    crudas = [e for e in etiquetas if "{" in e or "}" in e]
    chequeo("ninguna etiqueta queda con un placeholder sin rellenar",
            not crudas, "; ".join(crudas[:3]))

    # La misma llamada en los 3 idiomas tiene que dar textos DISTINTOS: si
    # coinciden, la traducción no se está aplicando (cae al código crudo).
    por_idioma = {}
    for lang in LANGS:
        cod, cuerpo = subir(f"{base}/api/ingenieria/archivo?lang={lang}", "archivos", [csv_demo])
        por_idioma[lang] = _etiquetas_de(json.loads(cuerpo)) if cod == 200 else []
    chequeo("la ingeniería de datos responde en los 3 idiomas",
            all(por_idioma[x] for x in LANGS),
            {k: len(v) for k, v in por_idioma.items()})
    chequeo("los 3 idiomas devuelven textos distintos (la traducción se aplica)",
            por_idioma["es"] != por_idioma["en"] and por_idioma["es"] != por_idioma["pt"])

    # Un conector externo sin credenciales NO puede prender solo.
    cod, cuerpo, _ = pedir(f"{base}/api/conectores")
    conectores = json.loads(cuerpo) if cod == 200 else {}
    chequeo("/api/conectores responde 200", cod == 200, f"código {cod}")
    prendidos = _conectores_prendidos(conectores)
    chequeo("ningún conector externo aparece activo sin credenciales",
            not prendidos, f"activos: {prendidos}")


def _filas(payload) -> list:
    """Las filas de una respuesta de tabla.

    La API no devuelve la lista pelada: la envuelve en
    ``{table, lang, rows, data}`` para que un BI sepa qué está leyendo sin
    mirar la URL. Acá interesan las filas.
    """
    if isinstance(payload, dict):
        return payload.get("data") or []
    return payload if isinstance(payload, list) else []


def _etiquetas_de(respuesta: dict) -> list[str]:
    """Junta las etiquetas de features de la respuesta de ingeniería.

    La forma exacta del payload es un detalle del endpoint; acá interesa
    solo el texto que termina viendo el usuario, venga de donde venga.
    """
    out: list[str] = []

    def caminar(nodo) -> None:
        if isinstance(nodo, dict):
            if isinstance(nodo.get("etiqueta"), str):
                out.append(nodo["etiqueta"])
            for v in nodo.values():
                caminar(v)
        elif isinstance(nodo, list):
            for v in nodo:
                caminar(v)

    caminar(respuesta)
    return out


def _conectores_prendidos(respuesta) -> list[str]:
    """Conectores que se declaran configurados sin que haya credenciales.

    La respuesta es ``{plan, <conector>: {configurado, licenciado}, ...}``.
    Sin variables de entorno cargadas, `configurado` tiene que ser False en
    todos: es la garantía de que el motor no sale a la red por su cuenta.
    """
    return [nombre for nombre, estado in respuesta.items()
            if isinstance(estado, dict) and estado.get("configurado") is True]


# ── 2 y 3. navegador ────────────────────────────────────────────────────
def _chromium_kwargs() -> dict:
    """Este sandbox trae un Chromium completo en PLAYWRIGHT_BROWSERS_PATH
    pero no la variante `chrome-headless-shell` que Playwright busca por
    defecto. Misma lógica que assets/video/record_screencast.py."""
    base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if base:
        candidato = os.path.join(base, "chromium")
        if os.path.exists(candidato):
            return {"executable_path": candidato}
    return {}


def _pestañas_declaradas() -> int:
    """Cuántas pestañas de primer nivel declara app.py.

    Se lee del texto, no importando app.py: importarlo levanta Streamlit
    entero dentro del proceso del E2E. La llamada es una sola en el archivo
    (``st.tabs([...])`` de primer nivel) y cada pestaña es un ``t("tab_...")``.
    """
    import re

    fuente = open(os.path.join(REPO_ROOT, "app", "app.py"), encoding="utf-8").read()
    # La primera st.tabs del archivo es la de primer nivel; las otras son
    # sub-pestañas dentro de un panel.
    inicio = fuente.index("st.tabs([")
    fin = fuente.index("])", inicio)
    return len(re.findall(r't\("tab_\w+",\s*lang\)', fuente[inicio:fin]))


class Vigilante:
    """Junta todo lo que el navegador considera un problema.

    Los errores de consola de terceros (extensiones, favicon) no existen
    acá: todo se sirve desde 127.0.0.1, así que cualquier ruido es nuestro.
    """

    def __init__(self, page, ignorar: tuple[str, ...] = ()):
        self.errores: list[str] = []
        self.ignorar = ignorar
        page.on("console", self._consola)
        page.on("pageerror", lambda e: self._sumar(f"pageerror: {e}"))
        page.on("requestfailed", lambda r: self._sumar(
            f"request falló: {r.url} ({r.failure})"))
        page.on("response", lambda r: r.status >= 500 and self._sumar(
            f"HTTP {r.status}: {r.url}"))

    def _consola(self, msg) -> None:
        if msg.type == "error":
            self._sumar(f"console.error: {msg.text}")

    def _sumar(self, texto: str) -> None:
        if any(p in texto for p in self.ignorar):
            return
        self.errores.append(texto)


def verificar_streamlit(base: str, pw) -> None:
    seccion("Dashboard Streamlit renderizado en Chromium")
    from mvdg.i18n import t

    nav = pw.chromium.launch(**_chromium_kwargs())
    ctx = nav.new_context(viewport={"width": 1440, "height": 950})
    page = ctx.new_page()
    vig = Vigilante(page)
    try:
        page.goto(base, wait_until="load", timeout=90_000)
        page.wait_for_selector('[data-testid="stTab"]', timeout=90_000)
        page.wait_for_timeout(6000)  # que Panorama termine de calcular

        # Solo las pestañas de PRIMER nivel: alguna pestaña (Estándares)
        # tiene sub-pestañas propias, que también son stTab. Sin acotar al
        # tablist de arriba, el recorrido intenta clickear sub-pestañas que
        # están ocultas dentro de un panel cerrado.
        pestañas = page.locator('[role="tablist"]').first.locator('[data-testid="stTab"]')
        # Cuántas tienen que ser NO se escribe acá: se cuenta en app.py. Este
        # número estaba clavado en 20 y al agregar tres pestañas el E2E se puso
        # rojo por estar desactualizado, no por un defecto — un rojo que no
        # significa nada enseña a ignorar el rojo. Leyéndolo del código, la
        # comprobación sigue siendo real (que Streamlit las DIBUJE todas) y deja
        # de envejecer sola.
        esperadas = _pestañas_declaradas()
        chequeo(f"el dashboard carga y dibuja sus {esperadas} pestañas",
                pestañas.count() == esperadas, f"encontradas {pestañas.count()}")

        # Recorrer TODAS. Una excepción de Python en una pestaña se dibuja
        # dentro de la página y no rompe nada: solo se ve entrando.
        con_excepcion: list[str] = []
        vacias: list[str] = []
        for i in range(pestañas.count()):
            nombre = pestañas.nth(i).inner_text().strip()
            pestañas.nth(i).click()
            page.wait_for_timeout(2200)
            if page.locator('[data-testid="stException"]').count():
                detalle = page.locator('[data-testid="stException"]').first.inner_text()
                con_excepcion.append(f"{nombre}: {detalle.splitlines()[0][:90]}")
            cuerpo = page.locator('[data-testid="stMain"]').inner_text().strip()
            if len(cuerpo) < 120:
                vacias.append(nombre)
            print(f"      · {nombre}: {len(cuerpo)} caracteres renderizados")
        chequeo("ninguna pestaña levanta una excepción de Python",
                not con_excepcion, "; ".join(con_excepcion))
        chequeo("ninguna pestaña queda en blanco", not vacias, "; ".join(vacias))

        # El idioma tiene que cambiar de verdad la pantalla, no solo el menú.
        titulos = {}
        for lang in LANGS:
            page.locator('[data-testid="stSidebar"] label',
                         has_text={"es": "Español", "en": "English",
                                   "pt": "Português"}[lang]).first.click()
            page.wait_for_timeout(4000)
            page.locator('[data-testid="stTab"]').first.click()
            page.wait_for_timeout(2500)
            titulos[lang] = page.locator('[data-testid="stMain"]').inner_text()[:2000]
            esperado = t("tab_quality", lang)
            chequeo(f"idioma {lang}: la pestaña Calidad se llama «{esperado}»",
                    page.locator(f'[data-testid="stTab"]:has-text("{esperado}")').count() > 0)
        chequeo("cambiar de idioma cambia el contenido, no solo el menú",
                titulos["es"] != titulos["en"] and titulos["es"] != titulos["pt"])

        chequeo("el dashboard no deja errores en la consola del navegador",
                not vig.errores, "; ".join(vig.errores[:4]))
    finally:
        ctx.close()
        nav.close()


def verificar_landing(base: str, pw) -> None:
    seccion("Landing en Chromium (lo que ve el que va a comprar)")

    nav = pw.chromium.launch(**_chromium_kwargs())
    ctx = nav.new_context(viewport={"width": 1440, "height": 950})
    page = ctx.new_page()
    # El CDN de jsDelivr no se resuelve desde el sandbox: ese fallo es del
    # entorno, no del sitio (por eso hay una fuente local antes).
    vig = Vigilante(page, ignorar=("cdn.jsdelivr.net",))
    try:
        page.goto(f"{base}/index.html", wait_until="load", timeout=60_000)
        page.wait_for_timeout(2500)

        chequeo("la landing carga con su título", bool(page.title().strip()), page.title())
        # Los dos videos: el de antes/después (el argumento para quien decide)
        # y la demo narrada. Los dos tienen que existir, cambiar de idioma y
        # servirse de verdad — un <source> que apunta a un 404 se ve igual de
        # bien en el HTML y deja un recuadro negro en la pantalla del cliente.
        videos = page.locator("video[data-vbase]")
        bases = [videos.nth(i).get_attribute("data-vbase") for i in range(videos.count())]
        chequeo("los dos videos (antes/después y demo) están en la página",
                len(bases) == 2, f"encontrados: {bases}")
        chequeo("el antes/después aparece antes que la demo narrada",
                bases[:1] == ["MVDataGovernance_AntesDespues"], f"orden: {bases}")

        # El selector de idioma tiene que cambiar el texto Y los dos videos.
        for lang in LANGS:
            page.locator(f'.lang button[data-lang="{lang}"]').click()
            page.wait_for_timeout(900)
            for i, base_video in enumerate(bases):
                src = videos.nth(i).locator("source").first.get_attribute("src") or ""
                chequeo(f"idioma {lang}: {base_video} apunta al archivo de ese idioma",
                        src.endswith(f"_{lang}.mp4"), f"src={src}")
                cod, _, _ = pedir(f"{base}/{src}")
                chequeo(f"idioma {lang}: {base_video} existe y se sirve", cod == 200,
                        f"código {cod} en {src}")
            texto = page.locator("body").inner_text()
            chequeo(f"idioma {lang}: la página tiene contenido", len(texto) > 800,
                    f"{len(texto)} caracteres")

        # Cada botón que apunta a un ancla tiene que llegar a algún lado.
        rotas = page.evaluate("""() => Array.from(document.querySelectorAll('a[href^="#"]'))
            .map(a => a.getAttribute('href'))
            .filter(h => h.length > 1 && !document.querySelector(h))""")
        chequeo("ningún enlace interno apunta a una sección que no existe",
                not rotas, "; ".join(sorted(set(rotas))[:5]))

        # Ninguna imagen rota ni escalada a la fuerza: el pedido explícito
        # era que no quede texto solapado ni recortado.
        rotas = page.evaluate("""() => Array.from(document.images)
            .filter(i => i.complete && i.naturalWidth === 0)
            .map(i => i.currentSrc || i.src)""")
        chequeo("ninguna imagen de la landing está rota", not rotas, "; ".join(rotas[:3]))

        deformadas = page.evaluate("""() => Array.from(document.images)
            .filter(i => i.naturalWidth > 0 && i.clientWidth > 0)
            .map(i => ({src: i.currentSrc || i.src,
                        r1: i.naturalWidth / i.naturalHeight,
                        r2: i.clientWidth / i.clientHeight}))
            .filter(o => Math.abs(o.r1 - o.r2) / o.r1 > 0.06)
            .map(o => o.src)""")
        chequeo("ninguna imagen se muestra deformada (proporción alterada)",
                not deformadas, "; ".join(deformadas[:3]))

        chequeo("la landing no deja errores en la consola del navegador",
                not vig.errores, "; ".join(vig.errores[:4]))
    finally:
        ctx.close()
        nav.close()

    verificar_encuadre(base, pw)


# Del monitor de 27" al teléfono más angosto que se sigue usando. Un ancho
# suelto no alcanza: los defectos de encuadre viven en los extremos y en los
# bordes de cada media query, no en el ancho en el que uno diseña.
ANCHOS = (2560, 1920, 1720, 1600, 1440, 1366, 1280, 1180, 1024, 900, 820, 768, 430, 390, 360, 320)


def verificar_encuadre(base: str, pw) -> None:
    """Ninguna página se sale del marco en ningún ancho.

    Barra horizontal en el navegador = hay contenido afuera de la pantalla.
    En un teléfono eso es texto cortado o un botón inalcanzable; el que entra
    a comprar no lo reporta, se va.
    """
    seccion("Encuadre: ninguna página desborda a lo ancho")
    import glob

    paginas = sorted(os.path.basename(f)
                     for f in glob.glob(os.path.join(REPO_ROOT, "landing", "*.html")))
    nav = pw.chromium.launch(**_chromium_kwargs())
    try:
        for pagina in paginas:
            malos: list[str] = []
            for ancho in ANCHOS:
                ctx = nav.new_context(viewport={"width": ancho, "height": 900})
                page = ctx.new_page()
                page.goto(f"{base}/{pagina}", wait_until="load", timeout=60_000)
                page.wait_for_timeout(800)
                desborde = page.evaluate(
                    "() => document.documentElement.scrollWidth"
                    " - document.documentElement.clientWidth")
                if desborde > 1:
                    malos.append(f"{ancho}px:+{desborde}")
                ctx.close()
            chequeo(f"{pagina} entra en el marco en los {len(ANCHOS)} anchos "
                    f"({ANCHOS[-1]}–{ANCHOS[0]}px)", not malos, " ".join(malos))
    finally:
        nav.close()


# ── recorrido ───────────────────────────────────────────────────────────
def main() -> int:
    solo_api = "--api" in sys.argv
    print("MV Data Governance · verificación end-to-end (casos demo)")

    seccion("Levantando servicios de verdad")
    puerto_api = puerto_libre()
    api = Servicio("bi_api (uvicorn)",
                   [sys.executable, "-m", "uvicorn", "bi_api.main:app",
                    "--host", "127.0.0.1", "--port", str(puerto_api), "--log-level", "warning"],
                   f"http://127.0.0.1:{puerto_api}/health")

    with api:
        verificar_api(f"http://127.0.0.1:{puerto_api}")

        if not solo_api:
            try:
                from playwright.sync_api import sync_playwright
            except ImportError:
                print("\n⚠️  playwright no está instalado: se saltea el navegador.")
                print("    pip install playwright && playwright install chromium")
                return _parte()

            puerto_st = puerto_libre()
            puerto_web = puerto_libre()
            st = Servicio("Streamlit",
                          [sys.executable, "-m", "streamlit", "run", "app/app.py",
                           "--server.headless", "true", "--server.port", str(puerto_st),
                           "--server.address", "127.0.0.1", "--browser.gatherUsageStats", "false"],
                          f"http://127.0.0.1:{puerto_st}/")
            web = Servicio("landing (http.server)",
                           [sys.executable, "-m", "http.server", str(puerto_web),
                            "--bind", "127.0.0.1", "--directory", "landing"],
                           f"http://127.0.0.1:{puerto_web}/index.html")
            with st, web, sync_playwright() as pw:
                verificar_streamlit(f"http://127.0.0.1:{puerto_st}/", pw)
                verificar_landing(f"http://127.0.0.1:{puerto_web}", pw)

    return _parte()


def _parte() -> int:
    print("\n" + "═" * 70)
    if FALLAS:
        print(f"E2E CON FALLAS — {len(OK)} OK, {len(FALLAS)} fallas:")
        for f in FALLAS:
            print(f"  ✗ {f}")
        return 1
    print(f"E2E OK — {len(OK)}/{len(OK)} chequeos pasaron contra los servicios reales.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
